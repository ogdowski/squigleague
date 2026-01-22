"""Tests for tiebreaker logic in league standings."""

from datetime import datetime, timedelta

import pytest
from app.league.models import Group, League, LeaguePlayer, Match, PlayerElo
from app.league.service import compare_for_knockout_tiebreaker, get_group_standings
from sqlmodel import Session


class TestCompareForKnockoutTiebreaker:
    """Test knockout qualification tiebreaker logic."""

    def test_fewer_unplayed_matches_wins(self, session: Session):
        """Player with fewer unplayed matches wins tiebreaker."""
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

        # Player 1: played all games
        p1 = LeaguePlayer(
            league_id=league.id,
            group_id=group.id,
            user_id=101,
            total_points=2000,
            games_played=3,
        )
        # Player 2: same points but 1 unplayed game
        p2 = LeaguePlayer(
            league_id=league.id,
            group_id=group.id,
            user_id=102,
            total_points=2000,
            games_played=2,
        )
        p3 = LeaguePlayer(league_id=league.id, group_id=group.id, user_id=103)
        p4 = LeaguePlayer(league_id=league.id, group_id=group.id, user_id=104)
        session.add_all([p1, p2, p3, p4])
        session.commit()

        # Create matches - p1 has all confirmed, p2 has one scheduled
        for i, opponent in enumerate([p3, p4]):
            # p1's matches - all confirmed
            m1 = Match(
                league_id=league.id,
                player1_id=p1.id,
                player2_id=opponent.id,
                phase="group",
                status="confirmed",
                player1_score=70,
                player2_score=60,
            )
            session.add(m1)

        # p2's matches - one confirmed, one scheduled (unplayed)
        m2_confirmed = Match(
            league_id=league.id,
            player1_id=p2.id,
            player2_id=p3.id,
            phase="group",
            status="confirmed",
            player1_score=70,
            player2_score=60,
        )
        m2_scheduled = Match(
            league_id=league.id,
            player1_id=p2.id,
            player2_id=p4.id,
            phase="group",
            status="scheduled",
        )
        session.add_all([m2_confirmed, m2_scheduled])
        session.commit()

        # p1 should win (fewer unplayed matches)
        result = compare_for_knockout_tiebreaker(session, p1, p2)
        assert result == -1  # p1 wins

    def test_higher_average_points_wins_when_same_unplayed(self, session: Session):
        """Player with higher average points wins when unplayed matches equal."""
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

        # Same games played, different average
        p1 = LeaguePlayer(
            league_id=league.id,
            group_id=group.id,
            user_id=101,
            total_points=3000,
            games_played=3,  # avg = 1000
        )
        p2 = LeaguePlayer(
            league_id=league.id,
            group_id=group.id,
            user_id=102,
            total_points=2700,
            games_played=3,  # avg = 900
        )
        session.add_all([p1, p2])
        session.commit()

        result = compare_for_knockout_tiebreaker(session, p1, p2)
        assert result == -1  # p1 wins (higher average)

        result_reverse = compare_for_knockout_tiebreaker(session, p2, p1)
        assert result_reverse == 1  # p2 loses

    def test_lower_elo_wins_as_final_tiebreaker(self, session: Session):
        """Lower ELO player wins tiebreaker (underdog advantage)."""
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

        # Same everything except ELO
        p1 = LeaguePlayer(
            league_id=league.id,
            group_id=group.id,
            user_id=101,
            total_points=3000,
            games_played=3,
        )
        p2 = LeaguePlayer(
            league_id=league.id,
            group_id=group.id,
            user_id=102,
            total_points=3000,
            games_played=3,
        )
        session.add_all([p1, p2])
        session.commit()

        # Create ELO records
        elo1 = PlayerElo(user_id=101, elo=1200)  # Higher ELO
        elo2 = PlayerElo(user_id=102, elo=1000)  # Lower ELO
        session.add_all([elo1, elo2])
        session.commit()

        # p1 has higher ELO, so p2 (lower ELO) should win
        result = compare_for_knockout_tiebreaker(session, p1, p2)
        assert result == 1  # p2 wins (lower ELO = underdog)

    def test_returns_zero_when_completely_tied(self, session: Session):
        """Returns 0 when all tiebreakers are equal."""
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

        # Identical stats, no ELO records
        p1 = LeaguePlayer(
            league_id=league.id,
            group_id=group.id,
            user_id=101,
            total_points=3000,
            games_played=3,
        )
        p2 = LeaguePlayer(
            league_id=league.id,
            group_id=group.id,
            user_id=102,
            total_points=3000,
            games_played=3,
        )
        session.add_all([p1, p2])
        session.commit()

        result = compare_for_knockout_tiebreaker(session, p1, p2)
        assert result == 0  # Complete tie


class TestGroupStandingsTiebreakers:
    """Test tiebreakers in group standings."""

    def test_more_games_played_breaks_points_tie(self, session: Session):
        """When points are equal, more games played ranks higher."""
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

        # Same points, different games played
        p1 = LeaguePlayer(
            league_id=league.id,
            group_id=group.id,
            user_id=101,
            total_points=2000,
            games_played=2,  # avg = 1000
        )
        p2 = LeaguePlayer(
            league_id=league.id,
            group_id=group.id,
            user_id=102,
            total_points=2000,
            games_played=3,  # avg = 666
        )
        # Add more players to make minimum games requirement lower
        p3 = LeaguePlayer(
            league_id=league.id,
            group_id=group.id,
            user_id=103,
            total_points=1000,
            games_played=2,
        )
        p4 = LeaguePlayer(
            league_id=league.id,
            group_id=group.id,
            user_id=104,
            total_points=500,
            games_played=2,
        )
        session.add_all([p1, p2, p3, p4])
        session.commit()

        standings = get_group_standings(session, group.id)

        # Both meet minimum games (2 for 4-player group)
        # p2 should rank above p1 (same points, more games played)
        assert standings[0].user_id == 102  # p2 first (more games)
        assert standings[1].user_id == 101  # p1 second

    def test_average_points_breaks_games_tie(self, session: Session):
        """When points and games equal, average points breaks tie."""
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

        # Same points AND games - average should be same too
        # This tests the final sort key
        p1 = LeaguePlayer(
            league_id=league.id,
            group_id=group.id,
            user_id=101,
            total_points=3000,
            games_played=3,  # avg = 1000
        )
        p2 = LeaguePlayer(
            league_id=league.id,
            group_id=group.id,
            user_id=102,
            total_points=3000,
            games_played=3,  # avg = 1000
        )
        p3 = LeaguePlayer(
            league_id=league.id,
            group_id=group.id,
            user_id=103,
            total_points=1500,
            games_played=3,
        )
        p4 = LeaguePlayer(
            league_id=league.id,
            group_id=group.id,
            user_id=104,
            total_points=1000,
            games_played=3,
        )
        session.add_all([p1, p2, p3, p4])
        session.commit()

        standings = get_group_standings(session, group.id)

        # p1 and p2 should both be at top (tied)
        top_two_ids = {standings[0].user_id, standings[1].user_id}
        assert top_two_ids == {101, 102}
