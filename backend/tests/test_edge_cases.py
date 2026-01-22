"""Tests for edge cases and boundary conditions."""

from datetime import datetime, timedelta

import pytest
from app.league.models import Group, League, LeaguePlayer, Match
from app.league.service import (
    calculate_knockout_size,
    calculate_num_groups,
    draw_groups,
    generate_group_matches,
    generate_knockout_matches,
    get_group_standings,
    get_qualified_players,
)
from app.matchup.models import Matchup
from app.matchup.service import submit_list, submit_result
from sqlmodel import Session


class TestSmallLeagueEdgeCases:
    """Test edge cases with small number of players."""

    def test_single_player_league(self, session: Session):
        """Single player league - cannot have matches."""
        league = League(
            name="Solo League",
            organizer_id=1,
            registration_end=datetime.utcnow() + timedelta(days=7),
            min_group_size=4,
            max_group_size=6,
        )
        session.add(league)
        session.commit()

        player = LeaguePlayer(league_id=league.id, user_id=101)
        session.add(player)
        session.commit()

        # Drawing groups with 1 player
        num_groups = calculate_num_groups(1, min_group_size=4, max_group_size=6)
        assert num_groups == 1

    def test_two_player_league_generates_one_match(self, session: Session):
        """Two players generate exactly one match."""
        league = League(
            name="Tiny League",
            organizer_id=1,
            registration_end=datetime.utcnow() + timedelta(days=7),
            min_group_size=2,
            max_group_size=6,
        )
        session.add(league)
        session.commit()

        group = Group(league_id=league.id, name="Group A")
        session.add(group)
        session.commit()

        p1 = LeaguePlayer(league_id=league.id, group_id=group.id, user_id=101)
        p2 = LeaguePlayer(league_id=league.id, group_id=group.id, user_id=102)
        session.add_all([p1, p2])
        session.commit()

        matches = generate_group_matches(session, league)
        assert len(matches) == 1
        assert {matches[0].player1_id, matches[0].player2_id} == {p1.id, p2.id}

    def test_minimum_knockout_is_top2(self, session: Session):
        """Minimum knockout size is always 2."""
        # Even with 3 players, knockout is top 2
        assert calculate_knockout_size(3) == 2
        assert calculate_knockout_size(4) == 2
        assert calculate_knockout_size(5) == 2


class TestLargeLeagueEdgeCases:
    """Test edge cases with large number of players."""

    def test_fifty_players_group_distribution(self):
        """50 players distributed evenly into groups."""
        num_groups = calculate_num_groups(50, min_group_size=4, max_group_size=6)
        # 50 / 4 = 12.5 -> 12 groups of ~4 players
        assert num_groups >= 8  # At least 8 groups
        assert num_groups <= 12  # At most 12 groups

    def test_exactly_max_group_size_players(self):
        """Players equal to max_group_size creates 1 group."""
        num_groups = calculate_num_groups(6, min_group_size=4, max_group_size=6)
        assert num_groups == 1


class TestGroupStandingsEdgeCases:
    """Test edge cases in group standings."""

    def test_standings_with_no_games_played(self, session: Session):
        """Standings work when no one has played yet."""
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

        for i in range(4):
            player = LeaguePlayer(
                league_id=league.id,
                group_id=group.id,
                user_id=100 + i,
                games_played=0,
                total_points=0,
            )
            session.add(player)
        session.commit()

        standings = get_group_standings(session, group.id)
        assert len(standings) == 4
        # All should have 0 points
        assert all(p.total_points == 0 for p in standings)

    def test_standings_empty_group(self, session: Session):
        """Empty group returns empty standings."""
        league = League(
            name="Test League",
            organizer_id=1,
            registration_end=datetime.utcnow() + timedelta(days=7),
        )
        session.add(league)
        session.commit()

        group = Group(league_id=league.id, name="Empty Group")
        session.add(group)
        session.commit()

        standings = get_group_standings(session, group.id)
        assert len(standings) == 0


class TestMatchEdgeCases:
    """Test edge cases in match handling."""

    def test_zero_score_match(self, session: Session):
        """Match with 0-0 score is valid draw."""
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

        p1 = LeaguePlayer(league_id=league.id, group_id=group.id, user_id=101)
        p2 = LeaguePlayer(league_id=league.id, group_id=group.id, user_id=102)
        session.add_all([p1, p2])
        session.commit()

        match = Match(
            league_id=league.id,
            player1_id=p1.id,
            player2_id=p2.id,
            phase="group",
            status="confirmed",
            player1_score=0,
            player2_score=0,
        )
        session.add(match)
        session.commit()

        assert match.winner_id is None  # Draw
        assert match.is_completed is True

    def test_very_high_scores(self, session: Session):
        """Very high scores are handled correctly."""
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

        p1 = LeaguePlayer(league_id=league.id, group_id=group.id, user_id=101)
        p2 = LeaguePlayer(league_id=league.id, group_id=group.id, user_id=102)
        session.add_all([p1, p2])
        session.commit()

        match = Match(
            league_id=league.id,
            player1_id=p1.id,
            player2_id=p2.id,
            phase="group",
            status="confirmed",
            player1_score=150,  # Very high
            player2_score=30,  # Low
        )
        session.add(match)
        session.commit()

        assert match.winner_id == p1.id


class TestMatchupEdgeCases:
    """Test edge cases in matchup handling."""

    def test_matchup_with_empty_list(self, session: Session):
        """Matchup allows empty army list."""
        matchup = Matchup(
            name="test-empty",
            player1_id=1,
            player2_id=2,
            player1_submitted=False,
            player2_submitted=False,
        )
        session.add(matchup)
        session.commit()

        result = submit_list(
            matchup=matchup,
            army_list="",  # Empty list
            is_player1=True,
            session=session,
            user_id=1,
        )

        assert result.player1_submitted is True
        assert result.player1_list == ""

    def test_matchup_with_very_long_list(self, session: Session):
        """Matchup handles very long army lists."""
        matchup = Matchup(
            name="test-long",
            player1_id=1,
            player2_id=2,
            player1_submitted=False,
            player2_submitted=False,
        )
        session.add(matchup)
        session.commit()

        long_list = "Unit Name\n" * 1000  # 1000 lines

        result = submit_list(
            matchup=matchup,
            army_list=long_list,
            is_player1=True,
            session=session,
            user_id=1,
        )

        assert result.player1_submitted is True
        assert len(result.player1_list) >= 10000

    def test_matchup_both_anonymous(self, session: Session):
        """Both players anonymous - result can't be submitted."""
        matchup = Matchup(
            name="test-anon-both",
            player1_id=None,
            player2_id=None,
            player1_submitted=True,
            player2_submitted=True,
            player1_list="List 1",
            player2_list="List 2",
            map_name="Test Map",
            revealed_at=datetime.utcnow(),
        )
        session.add(matchup)
        session.commit()

        assert matchup.can_submit_result(user_id=1) is False
        assert matchup.can_submit_result(user_id=None) is False

    def test_matchup_one_anonymous(self, session: Session):
        """One player anonymous - registered player can submit."""
        matchup = Matchup(
            name="test-anon-one",
            player1_id=1,
            player2_id=None,  # Anonymous
            player1_submitted=True,
            player2_submitted=True,
            player1_list="List 1",
            player2_list="List 2",
            map_name="Test Map",
            revealed_at=datetime.utcnow(),
        )
        session.add(matchup)
        session.commit()

        assert matchup.can_submit_result(user_id=1) is True
        assert matchup.can_submit_result(user_id=2) is False  # Not a player


class TestKnockoutEdgeCases:
    """Test edge cases in knockout phase."""

    def test_qualified_players_fewer_than_knockout_size(self, session: Session):
        """Handles case where fewer qualify than knockout size."""
        league = League(
            name="Test League",
            organizer_id=1,
            registration_end=datetime.utcnow() + timedelta(days=7),
            knockout_size=8,
            has_knockout_phase=True,
        )
        session.add(league)
        session.commit()

        group = Group(league_id=league.id, name="Group A")
        session.add(group)
        session.commit()

        # Only 4 players but knockout_size=8
        for i in range(4):
            player = LeaguePlayer(
                league_id=league.id,
                group_id=group.id,
                user_id=100 + i,
                total_points=1000 * (4 - i),
                games_played=3,
            )
            session.add(player)
        session.commit()

        qualified = get_qualified_players(session, league)
        # Should return all 4, not try to return 8
        assert len(qualified) == 4

    def test_knockout_with_exactly_2_players(self, session: Session):
        """Knockout with exactly 2 players goes straight to final."""
        league = League(
            name="Test League",
            organizer_id=1,
            registration_end=datetime.utcnow() + timedelta(days=7),
            knockout_size=2,
            has_knockout_phase=True,
        )
        session.add(league)
        session.commit()

        group = Group(league_id=league.id, name="Group A")
        session.add(group)
        session.commit()

        p1 = LeaguePlayer(
            league_id=league.id,
            group_id=group.id,
            user_id=101,
            total_points=3000,
            games_played=1,
        )
        p2 = LeaguePlayer(
            league_id=league.id,
            group_id=group.id,
            user_id=102,
            total_points=2000,
            games_played=1,
        )
        session.add_all([p1, p2])
        session.commit()

        matches = generate_knockout_matches(session, league)
        assert len(matches) == 1
        assert matches[0].knockout_round == "final"
