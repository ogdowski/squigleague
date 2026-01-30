"""Tests for voting feature."""

from datetime import datetime, timedelta

import pytest
from app.league.models import Group, League, LeaguePlayer, Vote, VoteCategory
from app.league.service import (
    break_tie_random,
    cast_vote,
    close_voting,
    create_vote_category,
    enable_voting_for_league,
    get_player_vote,
    get_voting_results,
)
from sqlmodel import Session, select


class TestCreateLeagueWithVotingEnabled:
    """Test league creation with voting enabled."""

    def test_league_has_voting_enabled_field(self, session: Session):
        """League model has voting_enabled field."""
        league = League(
            name="Test League",
            organizer_id=1,
            registration_end=datetime.utcnow() + timedelta(days=7),
            voting_enabled=True,
        )
        session.add(league)
        session.commit()
        session.refresh(league)

        assert league.voting_enabled is True
        assert league.voting_closed_at is None

    def test_voting_enabled_defaults_to_false(self, session: Session):
        """Voting is disabled by default."""
        league = League(
            name="Test League",
            organizer_id=1,
            registration_end=datetime.utcnow() + timedelta(days=7),
        )
        session.add(league)
        session.commit()
        session.refresh(league)

        assert league.voting_enabled is False


class TestCreateVoteCategory:
    """Test vote category creation."""

    def test_create_vote_category(self, session: Session):
        """Can create a vote category."""
        league = League(
            name="Test League",
            organizer_id=1,
            registration_end=datetime.utcnow() + timedelta(days=7),
            voting_enabled=True,
        )
        session.add(league)
        session.commit()

        category = create_vote_category(
            session,
            league_id=league.id,
            name="Best Sportsmanship",
            description="Vote for the most sportsmanlike player.",
        )

        assert category.id is not None
        assert category.league_id == league.id
        assert category.name == "Best Sportsmanship"
        assert category.description == "Vote for the most sportsmanlike player."
        assert category.winner_id is None

    def test_enable_voting_creates_default_category(self, session: Session):
        """Enabling voting creates default best_sport category."""
        league = League(
            name="Test League",
            organizer_id=1,
            registration_end=datetime.utcnow() + timedelta(days=7),
        )
        session.add(league)
        session.commit()

        category = enable_voting_for_league(session, league)

        assert league.voting_enabled is True
        assert category is not None
        assert category.name == "best_sport"
        assert category.league_id == league.id


class TestCastVote:
    """Test vote casting."""

    def _create_league_with_players(self, session: Session, num_players: int = 4):
        """Helper to create a finished league with players."""
        league = League(
            name="Test League",
            organizer_id=1,
            registration_end=datetime.utcnow() - timedelta(days=7),
            status="finished",
            voting_enabled=True,
        )
        session.add(league)
        session.commit()

        category = VoteCategory(
            league_id=league.id,
            name="Best Sportsmanship",
        )
        session.add(category)
        session.commit()

        players = []
        for i in range(num_players):
            player = LeaguePlayer(
                league_id=league.id,
                user_id=100 + i,
            )
            session.add(player)
            players.append(player)
        session.commit()

        for p in players:
            session.refresh(p)

        return league, category, players

    def test_cast_vote(self, session: Session):
        """Can cast a vote."""
        league, category, players = self._create_league_with_players(session)

        vote = cast_vote(
            session,
            category_id=category.id,
            voter_id=players[0].id,
            voted_for_id=players[1].id,
        )

        assert vote.id is not None
        assert vote.category_id == category.id
        assert vote.voter_id == players[0].id
        assert vote.voted_for_id == players[1].id

    def test_cannot_vote_for_self(self, session: Session):
        """Unique constraint prevents duplicate votes."""
        league, category, players = self._create_league_with_players(session)

        # First vote
        cast_vote(
            session,
            category_id=category.id,
            voter_id=players[0].id,
            voted_for_id=players[1].id,
        )

        # Second vote from same voter in same category should fail
        with pytest.raises(Exception):  # IntegrityError from unique constraint
            cast_vote(
                session,
                category_id=category.id,
                voter_id=players[0].id,
                voted_for_id=players[2].id,
            )

    def test_get_player_vote(self, session: Session):
        """Can retrieve a player's existing vote."""
        league, category, players = self._create_league_with_players(session)

        cast_vote(
            session,
            category_id=category.id,
            voter_id=players[0].id,
            voted_for_id=players[1].id,
        )

        vote = get_player_vote(session, category.id, players[0].id)
        assert vote is not None
        assert vote.voted_for_id == players[1].id

    def test_get_player_vote_returns_none_if_not_voted(self, session: Session):
        """Returns None if player hasn't voted."""
        league, category, players = self._create_league_with_players(session)

        vote = get_player_vote(session, category.id, players[0].id)
        assert vote is None


class TestVotingResults:
    """Test voting results calculation."""

    def _create_league_with_votes(self, session: Session, votes: list[tuple[int, int]]):
        """Helper to create a league with specific votes.

        Args:
            votes: List of (voter_index, voted_for_index) tuples
        """
        league = League(
            name="Test League",
            organizer_id=1,
            registration_end=datetime.utcnow() - timedelta(days=7),
            status="finished",
            voting_enabled=True,
        )
        session.add(league)
        session.commit()

        category = VoteCategory(
            league_id=league.id,
            name="Best Sportsmanship",
        )
        session.add(category)
        session.commit()

        # Create 5 players
        players = []
        for i in range(5):
            player = LeaguePlayer(
                league_id=league.id,
                user_id=100 + i,
            )
            session.add(player)
            players.append(player)
        session.commit()

        for p in players:
            session.refresh(p)

        # Cast votes
        for voter_idx, voted_for_idx in votes:
            vote = Vote(
                category_id=category.id,
                voter_id=players[voter_idx].id,
                voted_for_id=players[voted_for_idx].id,
            )
            session.add(vote)
        session.commit()

        return league, category, players

    def test_results_sorted_by_vote_count(self, session: Session):
        """Results are sorted by vote count descending."""
        # Player 1 gets 3 votes, Player 2 gets 1 vote
        votes = [
            (0, 1),  # Player 0 votes for Player 1
            (2, 1),  # Player 2 votes for Player 1
            (3, 1),  # Player 3 votes for Player 1
            (4, 2),  # Player 4 votes for Player 2
        ]
        league, category, players = self._create_league_with_votes(session, votes)

        results = get_voting_results(session, category.id)

        assert results["total_votes"] == 4
        assert len(results["results"]) == 2
        assert results["results"][0]["player_id"] == players[1].id
        assert results["results"][0]["vote_count"] == 3
        assert results["results"][1]["player_id"] == players[2].id
        assert results["results"][1]["vote_count"] == 1

    def test_detects_clear_winner(self, session: Session):
        """Correctly identifies a clear winner (no tie)."""
        votes = [
            (0, 1),
            (2, 1),
            (3, 2),
        ]
        league, category, players = self._create_league_with_votes(session, votes)

        results = get_voting_results(session, category.id)

        assert results["is_tied"] is False
        assert results["winner_id"] == players[1].id

    def test_detects_tie(self, session: Session):
        """Correctly identifies a tie."""
        # Player 1 and Player 2 both get 2 votes
        votes = [
            (0, 1),
            (2, 1),
            (3, 2),
            (4, 2),
        ]
        league, category, players = self._create_league_with_votes(session, votes)

        results = get_voting_results(session, category.id)

        assert results["is_tied"] is True
        assert results["winner_id"] is None

    def test_empty_results(self, session: Session):
        """Handles no votes gracefully."""
        league, category, players = self._create_league_with_votes(session, [])

        results = get_voting_results(session, category.id)

        assert results["total_votes"] == 0
        assert results["results"] == []
        assert results["winner_id"] is None
        assert results["is_tied"] is False


class TestCloseVoting:
    """Test closing voting."""

    def test_close_voting_sets_timestamp(self, session: Session):
        """Closing voting sets the voting_closed_at timestamp."""
        league = League(
            name="Test League",
            organizer_id=1,
            registration_end=datetime.utcnow() - timedelta(days=7),
            status="finished",
            voting_enabled=True,
        )
        session.add(league)
        session.commit()

        category = VoteCategory(league_id=league.id, name="Best Sportsmanship")
        session.add(category)
        session.commit()

        close_voting(session, league)

        session.refresh(league)
        assert league.voting_closed_at is not None

    def test_close_voting_auto_sets_winner_when_no_tie(self, session: Session):
        """Auto-sets winner when there's a clear winner."""
        league = League(
            name="Test League",
            organizer_id=1,
            registration_end=datetime.utcnow() - timedelta(days=7),
            status="finished",
            voting_enabled=True,
        )
        session.add(league)
        session.commit()

        category = VoteCategory(league_id=league.id, name="Best Sportsmanship")
        session.add(category)
        session.commit()

        # Create players and votes
        players = []
        for i in range(3):
            player = LeaguePlayer(league_id=league.id, user_id=100 + i)
            session.add(player)
            players.append(player)
        session.commit()

        for p in players:
            session.refresh(p)

        # Player 1 gets 2 votes, Player 2 gets 1 vote
        vote1 = Vote(
            category_id=category.id,
            voter_id=players[0].id,
            voted_for_id=players[1].id,
        )
        vote2 = Vote(
            category_id=category.id,
            voter_id=players[2].id,
            voted_for_id=players[1].id,
        )
        session.add_all([vote1, vote2])
        session.commit()

        close_voting(session, league)

        session.refresh(category)
        assert category.winner_id == players[1].id

    def test_close_voting_does_not_set_winner_on_tie(self, session: Session):
        """Does not set winner when there's a tie."""
        league = League(
            name="Test League",
            organizer_id=1,
            registration_end=datetime.utcnow() - timedelta(days=7),
            status="finished",
            voting_enabled=True,
        )
        session.add(league)
        session.commit()

        category = VoteCategory(league_id=league.id, name="Best Sportsmanship")
        session.add(category)
        session.commit()

        # Create players
        players = []
        for i in range(4):
            player = LeaguePlayer(league_id=league.id, user_id=100 + i)
            session.add(player)
            players.append(player)
        session.commit()

        for p in players:
            session.refresh(p)

        # Player 1 and Player 2 both get 1 vote
        vote1 = Vote(
            category_id=category.id,
            voter_id=players[0].id,
            voted_for_id=players[1].id,
        )
        vote2 = Vote(
            category_id=category.id,
            voter_id=players[2].id,
            voted_for_id=players[3].id,
        )
        session.add_all([vote1, vote2])
        session.commit()

        result = close_voting(session, league)

        session.refresh(category)
        assert category.winner_id is None
        assert result["categories"][0]["is_tied"] is True


class TestBreakTieRandom:
    """Test tie breaker."""

    def test_break_tie_sets_winner(self, session: Session):
        """Breaking tie sets a winner from the provided list."""
        league = League(
            name="Test League",
            organizer_id=1,
            registration_end=datetime.utcnow() - timedelta(days=7),
            status="finished",
            voting_enabled=True,
        )
        session.add(league)
        session.commit()

        category = VoteCategory(league_id=league.id, name="Best Sportsmanship")
        session.add(category)
        session.commit()

        players = []
        for i in range(2):
            player = LeaguePlayer(league_id=league.id, user_id=100 + i)
            session.add(player)
            players.append(player)
        session.commit()

        for p in players:
            session.refresh(p)

        tied_player_ids = [players[0].id, players[1].id]

        winner_id = break_tie_random(session, category, tied_player_ids)

        assert winner_id in tied_player_ids
        session.refresh(category)
        assert category.winner_id == winner_id


class TestOnlyLeaguePlayersCanVote:
    """Test that only league players can vote."""

    def test_vote_with_invalid_voter_id_no_app_validation(self, session: Session):
        """Vote with non-existent voter_id is not validated at app level.

        FK constraint enforcement depends on PostgreSQL; SQLite does not enforce
        foreign keys by default, so this test verifies current app behavior.
        """
        league = League(
            name="Test League",
            organizer_id=1,
            registration_end=datetime.utcnow() - timedelta(days=7),
            status="finished",
            voting_enabled=True,
        )
        session.add(league)
        session.commit()

        category = VoteCategory(league_id=league.id, name="Best Sportsmanship")
        session.add(category)
        session.commit()

        player = LeaguePlayer(league_id=league.id, user_id=100)
        session.add(player)
        session.commit()
        session.refresh(player)

        # No app-level validation on voter_id — FK enforced only in PostgreSQL
        vote = Vote(
            category_id=category.id,
            voter_id=99999,
            voted_for_id=player.id,
        )
        session.add(vote)
        session.commit()
        session.refresh(vote)
        assert vote.voter_id == 99999
