"""Tests for league player management - removal, walkovers, group changes."""

from datetime import datetime, timedelta

import pytest
from app.league.models import Group, League, LeaguePlayer, Match
from app.league.service import change_player_group, remove_player_from_league
from sqlmodel import Session, select


class TestRemovePlayerFromLeague:
    """Test player removal with walkover handling."""

    def test_removes_player(self, session: Session):
        """Player is removed from the league."""
        league = League(
            name="Test League",
            organizer_id=1,
            registration_end=datetime.utcnow() + timedelta(days=7),
        )
        session.add(league)
        session.commit()

        group = Group(league_id=league.id, name="Group A")
        session.add(group)
        session.commit()

        player = LeaguePlayer(league_id=league.id, group_id=group.id, user_id=101)
        session.add(player)
        session.commit()

        player_id = player.id
        remove_player_from_league(session, player)

        # Player should be gone
        result = session.get(LeaguePlayer, player_id)
        assert result is None

    def test_awards_walkover_to_opponent_for_scheduled_matches(self, session: Session):
        """Opponent gets walkover (25:0, 1075 pts) for scheduled matches."""
        league = League(
            name="Test League",
            organizer_id=1,
            registration_end=datetime.utcnow() + timedelta(days=7),
        )
        session.add(league)
        session.commit()

        group = Group(league_id=league.id, name="Group A")
        session.add(group)
        session.commit()

        leaving_player = LeaguePlayer(
            league_id=league.id,
            group_id=group.id,
            user_id=101,
            games_played=0,
            games_won=0,
            total_points=0,
        )
        opponent = LeaguePlayer(
            league_id=league.id,
            group_id=group.id,
            user_id=102,
            games_played=0,
            games_won=0,
            total_points=0,
        )
        session.add_all([leaving_player, opponent])
        session.commit()

        # Scheduled match
        match = Match(
            league_id=league.id,
            player1_id=leaving_player.id,
            player2_id=opponent.id,
            phase="group",
            status="scheduled",
        )
        session.add(match)
        session.commit()

        result = remove_player_from_league(
            session, leaving_player, award_walkovers=True
        )

        session.refresh(match)
        session.refresh(opponent)

        # Match becomes confirmed walkover
        assert match.status == "confirmed"
        assert match.player1_score == 0  # Leaving player
        assert match.player2_score == 25  # Opponent wins 25:0
        assert match.player2_league_points == 1075

        # Opponent stats updated
        assert opponent.games_played == 1
        assert opponent.games_won == 1
        assert opponent.total_points == 1075

        assert result["walkover_matches"] == 1

    def test_keeps_confirmed_matches_unchanged(self, session: Session):
        """Confirmed matches are not modified when player leaves."""
        league = League(
            name="Test League",
            organizer_id=1,
            registration_end=datetime.utcnow() + timedelta(days=7),
        )
        session.add(league)
        session.commit()

        group = Group(league_id=league.id, name="Group A")
        session.add(group)
        session.commit()

        leaving_player = LeaguePlayer(
            league_id=league.id,
            group_id=group.id,
            user_id=101,
            games_played=1,
            games_won=0,
            games_lost=1,
            total_points=246,
        )
        opponent = LeaguePlayer(
            league_id=league.id,
            group_id=group.id,
            user_id=102,
            games_played=1,
            games_won=1,
            total_points=1054,
        )
        session.add_all([leaving_player, opponent])
        session.commit()

        # Already confirmed match
        match = Match(
            league_id=league.id,
            player1_id=leaving_player.id,
            player2_id=opponent.id,
            phase="group",
            status="confirmed",
            player1_score=68,
            player2_score=72,
            player1_league_points=246,
            player2_league_points=1054,
        )
        session.add(match)
        session.commit()

        match_id = match.id
        remove_player_from_league(session, leaving_player)

        # Match should still exist and be unchanged
        result_match = session.get(Match, match_id)
        assert result_match is not None
        assert result_match.status == "confirmed"
        assert result_match.player1_score == 68
        assert result_match.player2_score == 72

    def test_deletes_matches_when_no_walkover(self, session: Session):
        """Deletes scheduled matches when award_walkovers=False."""
        league = League(
            name="Test League",
            organizer_id=1,
            registration_end=datetime.utcnow() + timedelta(days=7),
        )
        session.add(league)
        session.commit()

        group = Group(league_id=league.id, name="Group A")
        session.add(group)
        session.commit()

        leaving_player = LeaguePlayer(
            league_id=league.id, group_id=group.id, user_id=101
        )
        opponent = LeaguePlayer(league_id=league.id, group_id=group.id, user_id=102)
        session.add_all([leaving_player, opponent])
        session.commit()

        match = Match(
            league_id=league.id,
            player1_id=leaving_player.id,
            player2_id=opponent.id,
            phase="group",
            status="scheduled",
        )
        session.add(match)
        session.commit()

        match_id = match.id
        result = remove_player_from_league(
            session, leaving_player, award_walkovers=False
        )

        # Match should be deleted
        assert session.get(Match, match_id) is None
        assert result["deleted_matches"] == 1
        assert result["walkover_matches"] == 0

    def test_walkover_reverses_pending_stats(self, session: Session):
        """Walkover correctly reverses previous pending stats before applying new ones."""
        league = League(
            name="Test League",
            organizer_id=1,
            registration_end=datetime.utcnow() + timedelta(days=7),
        )
        session.add(league)
        session.commit()

        group = Group(league_id=league.id, name="Group A")
        session.add(group)
        session.commit()

        leaving_player = LeaguePlayer(
            league_id=league.id,
            group_id=group.id,
            user_id=101,
            games_played=1,
            games_won=1,
            total_points=1054,
        )
        opponent = LeaguePlayer(
            league_id=league.id,
            group_id=group.id,
            user_id=102,
            games_played=1,
            games_lost=1,
            total_points=246,
        )
        session.add_all([leaving_player, opponent])
        session.commit()

        # Pending match where opponent was losing
        match = Match(
            league_id=league.id,
            player1_id=leaving_player.id,
            player2_id=opponent.id,
            phase="group",
            status="pending_confirmation",
            player1_score=72,
            player2_score=65,
            player1_league_points=1054,
            player2_league_points=246,
        )
        session.add(match)
        session.commit()

        remove_player_from_league(session, leaving_player, award_walkovers=True)

        session.refresh(opponent)
        session.refresh(match)

        # Opponent's old loss should be reversed, then walkover win applied
        # Old: 1 game, 1 loss, 246 pts -> reversed -> 0 games, 0 losses, 0 pts
        # Walkover: +1 game, +1 win, +1075 pts
        assert opponent.games_played == 1
        assert opponent.games_won == 1
        assert opponent.games_lost == 0
        assert opponent.total_points == 1075


class TestChangePlayerGroup:
    """Test moving players between groups."""

    def test_moves_player_to_new_group(self, session: Session):
        """Player's group_id is updated."""
        league = League(
            name="Test League",
            organizer_id=1,
            registration_end=datetime.utcnow() + timedelta(days=7),
        )
        session.add(league)
        session.commit()

        group_a = Group(league_id=league.id, name="Group A")
        group_b = Group(league_id=league.id, name="Group B")
        session.add_all([group_a, group_b])
        session.commit()

        player = LeaguePlayer(league_id=league.id, group_id=group_a.id, user_id=101)
        session.add(player)
        session.commit()

        change_player_group(session, player, group_b, regenerate_matches=False)

        session.refresh(player)
        assert player.group_id == group_b.id

    def test_deletes_old_group_matches(self, session: Session):
        """Unconfirmed matches in old group are deleted."""
        league = League(
            name="Test League",
            organizer_id=1,
            registration_end=datetime.utcnow() + timedelta(days=7),
            days_per_match=14,
        )
        session.add(league)
        session.commit()

        group_a = Group(league_id=league.id, name="Group A")
        group_b = Group(league_id=league.id, name="Group B")
        session.add_all([group_a, group_b])
        session.commit()

        player = LeaguePlayer(league_id=league.id, group_id=group_a.id, user_id=101)
        old_groupmate = LeaguePlayer(
            league_id=league.id, group_id=group_a.id, user_id=102
        )
        session.add_all([player, old_groupmate])
        session.commit()

        # Match in old group (between player and old_groupmate)
        old_match = Match(
            league_id=league.id,
            player1_id=player.id,
            player2_id=old_groupmate.id,
            phase="group",
            status="scheduled",
        )
        session.add(old_match)
        session.commit()

        old_match_id = old_match.id

        # Count matches before move
        matches_before = session.scalars(
            select(Match).where(Match.league_id == league.id)
        ).all()
        assert len(matches_before) == 1

        result = change_player_group(session, player, group_b, regenerate_matches=True)

        # Match should be deleted
        assert result["deleted_matches"] == 1

        # Verify no old matches remain for this player with old groupmate
        matches_after = session.scalars(
            select(Match).where(
                Match.league_id == league.id,
                Match.phase == "group",
                (
                    (Match.player1_id == player.id)
                    & (Match.player2_id == old_groupmate.id)
                )
                | (
                    (Match.player1_id == old_groupmate.id)
                    & (Match.player2_id == player.id)
                ),
            )
        ).all()
        assert len(matches_after) == 0

    def test_creates_new_group_matches(self, session: Session):
        """Creates matches with players in new group."""
        league = League(
            name="Test League",
            organizer_id=1,
            registration_end=datetime.utcnow() + timedelta(days=7),
            days_per_match=14,
        )
        session.add(league)
        session.commit()

        group_a = Group(league_id=league.id, name="Group A")
        group_b = Group(league_id=league.id, name="Group B")
        session.add_all([group_a, group_b])
        session.commit()

        player = LeaguePlayer(league_id=league.id, group_id=group_a.id, user_id=101)
        new_groupmate1 = LeaguePlayer(
            league_id=league.id, group_id=group_b.id, user_id=201
        )
        new_groupmate2 = LeaguePlayer(
            league_id=league.id, group_id=group_b.id, user_id=202
        )
        session.add_all([player, new_groupmate1, new_groupmate2])
        session.commit()

        result = change_player_group(session, player, group_b, regenerate_matches=True)

        # Should create 2 new matches (vs new_groupmate1 and new_groupmate2)
        assert result["created_matches"] == 2

        # Verify matches exist
        matches = session.scalars(
            select(Match).where(
                Match.league_id == league.id,
                (Match.player1_id == player.id) | (Match.player2_id == player.id),
            )
        ).all()
        assert len(matches) == 2

    def test_keeps_confirmed_matches_when_moving(self, session: Session):
        """Confirmed matches are not deleted when moving groups."""
        league = League(
            name="Test League",
            organizer_id=1,
            registration_end=datetime.utcnow() + timedelta(days=7),
            days_per_match=14,
        )
        session.add(league)
        session.commit()

        group_a = Group(league_id=league.id, name="Group A")
        group_b = Group(league_id=league.id, name="Group B")
        session.add_all([group_a, group_b])
        session.commit()

        player = LeaguePlayer(league_id=league.id, group_id=group_a.id, user_id=101)
        old_groupmate = LeaguePlayer(
            league_id=league.id, group_id=group_a.id, user_id=102
        )
        session.add_all([player, old_groupmate])
        session.commit()

        # Confirmed match in old group
        confirmed_match = Match(
            league_id=league.id,
            player1_id=player.id,
            player2_id=old_groupmate.id,
            phase="group",
            status="confirmed",
            player1_score=72,
            player2_score=65,
        )
        session.add(confirmed_match)
        session.commit()

        confirmed_match_id = confirmed_match.id
        change_player_group(session, player, group_b, regenerate_matches=True)

        # Confirmed match should still exist
        assert session.get(Match, confirmed_match_id) is not None

    def test_no_change_if_same_group(self, session: Session):
        """Does nothing if player is moved to same group."""
        league = League(
            name="Test League",
            organizer_id=1,
            registration_end=datetime.utcnow() + timedelta(days=7),
        )
        session.add(league)
        session.commit()

        group_a = Group(league_id=league.id, name="Group A")
        session.add(group_a)
        session.commit()

        player = LeaguePlayer(league_id=league.id, group_id=group_a.id, user_id=101)
        session.add(player)
        session.commit()

        result = change_player_group(session, player, group_a, regenerate_matches=True)

        assert result["deleted_matches"] == 0
        assert result["created_matches"] == 0
