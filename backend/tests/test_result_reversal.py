"""Tests for result editing and statistics reversal."""

from datetime import datetime, timedelta

import pytest
from app.league.models import Group, League, LeaguePlayer, Match
from app.league.service import submit_match_result
from sqlmodel import Session


class TestResultResubmission:
    """Test re-submitting results and stats reversal."""

    def test_resubmit_reverses_previous_stats(self, session: Session):
        """Re-submitting result reverses previous stats before applying new."""
        league = League(
            name="Test League",
            organizer_id=1,
            registration_end=datetime.utcnow() + timedelta(days=7),
            points_per_win=1000,
            points_per_draw=600,
            points_per_loss=200,
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
            games_played=0,
            games_won=0,
            games_lost=0,
            games_drawn=0,
            total_points=0,
        )
        p2 = LeaguePlayer(
            league_id=league.id,
            group_id=group.id,
            user_id=102,
            games_played=0,
            games_won=0,
            games_lost=0,
            games_drawn=0,
            total_points=0,
        )
        session.add_all([p1, p2])
        session.commit()

        match = Match(
            league_id=league.id,
            player1_id=p1.id,
            player2_id=p2.id,
            phase="group",
            status="scheduled",
        )
        session.add(match)
        session.commit()

        # First submission: p1 wins 72-65
        submit_match_result(session, match, 72, 65, submitted_by_id=101)
        session.refresh(p1)
        session.refresh(p2)

        assert p1.games_won == 1
        assert p2.games_lost == 1
        old_p1_points = p1.total_points
        old_p2_points = p2.total_points

        # Re-submission: p2 wins 70-68 (opposite result!)
        submit_match_result(session, match, 68, 70, submitted_by_id=102)
        session.refresh(p1)
        session.refresh(p2)

        # Stats should be reversed and new result applied
        assert p1.games_won == 0
        assert p1.games_lost == 1
        assert p2.games_won == 1
        assert p2.games_lost == 0

        # Points should change
        assert p1.total_points != old_p1_points
        assert p2.total_points != old_p2_points

    def test_resubmit_from_win_to_draw(self, session: Session):
        """Re-submitting from win to draw updates stats correctly."""
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

        p1 = LeaguePlayer(
            league_id=league.id,
            group_id=group.id,
            user_id=101,
            games_played=0,
            games_won=0,
            games_lost=0,
            games_drawn=0,
            total_points=0,
        )
        p2 = LeaguePlayer(
            league_id=league.id,
            group_id=group.id,
            user_id=102,
            games_played=0,
            games_won=0,
            games_lost=0,
            games_drawn=0,
            total_points=0,
        )
        session.add_all([p1, p2])
        session.commit()

        match = Match(
            league_id=league.id,
            player1_id=p1.id,
            player2_id=p2.id,
            phase="group",
            status="scheduled",
        )
        session.add(match)
        session.commit()

        # First: p1 wins
        submit_match_result(session, match, 72, 65, submitted_by_id=101)

        # Re-submit: draw
        submit_match_result(session, match, 70, 70, submitted_by_id=102)
        session.refresh(p1)
        session.refresh(p2)

        assert p1.games_won == 0
        assert p1.games_drawn == 1
        assert p2.games_lost == 0
        assert p2.games_drawn == 1

    def test_games_played_stays_at_one_after_resubmit(self, session: Session):
        """Games played should stay at 1 after re-submission (not increment)."""
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

        p1 = LeaguePlayer(
            league_id=league.id,
            group_id=group.id,
            user_id=101,
            games_played=0,
            total_points=0,
        )
        p2 = LeaguePlayer(
            league_id=league.id,
            group_id=group.id,
            user_id=102,
            games_played=0,
            total_points=0,
        )
        session.add_all([p1, p2])
        session.commit()

        match = Match(
            league_id=league.id,
            player1_id=p1.id,
            player2_id=p2.id,
            phase="group",
            status="scheduled",
        )
        session.add(match)
        session.commit()

        # Submit multiple times
        submit_match_result(session, match, 72, 65, submitted_by_id=101)
        submit_match_result(session, match, 65, 72, submitted_by_id=102)
        submit_match_result(session, match, 70, 70, submitted_by_id=101)

        session.refresh(p1)
        session.refresh(p2)

        # Games played should still be 1, not 3
        assert p1.games_played == 1
        assert p2.games_played == 1


class TestPointsCalculationOnResubmit:
    """Test that points are calculated correctly on re-submission."""

    def test_points_reflect_latest_result(self, session: Session):
        """Total points should reflect the latest submitted result."""
        league = League(
            name="Test League",
            organizer_id=1,
            registration_end=datetime.utcnow() + timedelta(days=7),
            points_per_win=1000,
            points_per_draw=600,
            points_per_loss=200,
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
            games_played=0,
            total_points=0,
        )
        p2 = LeaguePlayer(
            league_id=league.id,
            group_id=group.id,
            user_id=102,
            games_played=0,
            total_points=0,
        )
        session.add_all([p1, p2])
        session.commit()

        match = Match(
            league_id=league.id,
            player1_id=p1.id,
            player2_id=p2.id,
            phase="group",
            status="scheduled",
        )
        session.add(match)
        session.commit()

        # Submit draw (70-70)
        submit_match_result(session, match, 70, 70, submitted_by_id=101)
        session.refresh(p1)
        session.refresh(p2)

        # Both should have draw points (~650)
        assert 600 <= p1.total_points <= 700
        assert p1.total_points == p2.total_points

        # Re-submit as win for p1
        submit_match_result(session, match, 80, 60, submitted_by_id=101)
        session.refresh(p1)
        session.refresh(p2)

        # p1 should now have win points, p2 loss points
        assert p1.total_points > 1000  # Win + bonus
        assert p2.total_points < 300  # Loss + small bonus

    def test_match_league_points_updated(self, session: Session):
        """Match's player_league_points fields are updated on resubmit."""
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
            status="scheduled",
        )
        session.add(match)
        session.commit()

        # First submission
        submit_match_result(session, match, 72, 65, submitted_by_id=101)
        session.refresh(match)
        old_p1_league_pts = match.player1_league_points
        old_p2_league_pts = match.player2_league_points

        # Re-submit with different scores
        submit_match_result(session, match, 65, 72, submitted_by_id=102)
        session.refresh(match)

        # Points on match should be updated
        assert match.player1_league_points != old_p1_league_pts
        assert match.player2_league_points != old_p2_league_pts
        # Now p2 has more points than p1
        assert match.player2_league_points > match.player1_league_points


class TestMultipleMatchesStats:
    """Test statistics with multiple matches."""

    def test_cumulative_stats_across_matches(self, session: Session):
        """Stats accumulate correctly across multiple matches."""
        league = League(
            name="Test League",
            organizer_id=1,
            registration_end=datetime.utcnow() + timedelta(days=7),
            points_per_win=1000,
            points_per_draw=600,
            points_per_loss=200,
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
            games_played=0,
            games_won=0,
            games_lost=0,
            games_drawn=0,
            total_points=0,
        )
        p2 = LeaguePlayer(
            league_id=league.id,
            group_id=group.id,
            user_id=102,
            games_played=0,
            games_won=0,
            games_lost=0,
            games_drawn=0,
            total_points=0,
        )
        p3 = LeaguePlayer(
            league_id=league.id,
            group_id=group.id,
            user_id=103,
            games_played=0,
            games_won=0,
            games_lost=0,
            games_drawn=0,
            total_points=0,
        )
        session.add_all([p1, p2, p3])
        session.commit()

        # Match 1: p1 vs p2 - p1 wins
        match1 = Match(
            league_id=league.id,
            player1_id=p1.id,
            player2_id=p2.id,
            phase="group",
            status="scheduled",
        )
        session.add(match1)
        session.commit()
        submit_match_result(session, match1, 72, 65, submitted_by_id=101)

        # Match 2: p1 vs p3 - p1 loses
        match2 = Match(
            league_id=league.id,
            player1_id=p1.id,
            player2_id=p3.id,
            phase="group",
            status="scheduled",
        )
        session.add(match2)
        session.commit()
        submit_match_result(session, match2, 60, 75, submitted_by_id=101)

        session.refresh(p1)

        assert p1.games_played == 2
        assert p1.games_won == 1
        assert p1.games_lost == 1
        assert p1.games_drawn == 0
        # Total points should be sum of both matches
        assert p1.total_points > 1000  # Win pts + loss pts
