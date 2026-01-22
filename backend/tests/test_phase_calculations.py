"""Tests for league phase calculations - dates, rounds, etc."""

from datetime import datetime, timedelta

import pytest
from app.league.models import Group, League, LeaguePlayer
from app.league.service import (
    calculate_group_phase_rounds,
    calculate_phase_dates,
    get_league_player_count,
    get_qualifying_info,
    round_up_to_hour,
)
from sqlmodel import Session


class TestRoundUpToHour:
    """Test datetime rounding to next hour."""

    def test_already_on_hour(self):
        """Already on the hour returns same time."""
        dt = datetime(2024, 1, 15, 14, 0, 0, 0)
        result = round_up_to_hour(dt)
        assert result == dt

    def test_rounds_up_from_minutes(self):
        """Rounds up when minutes are present."""
        dt = datetime(2024, 1, 15, 14, 30, 0, 0)
        result = round_up_to_hour(dt)
        assert result == datetime(2024, 1, 15, 15, 0, 0, 0)

    def test_rounds_up_from_seconds(self):
        """Rounds up when only seconds are present."""
        dt = datetime(2024, 1, 15, 14, 0, 30, 0)
        result = round_up_to_hour(dt)
        assert result == datetime(2024, 1, 15, 15, 0, 0, 0)

    def test_rounds_up_from_microseconds(self):
        """Rounds up when only microseconds are present."""
        dt = datetime(2024, 1, 15, 14, 0, 0, 500)
        result = round_up_to_hour(dt)
        assert result == datetime(2024, 1, 15, 15, 0, 0, 0)

    def test_handles_day_rollover(self):
        """Correctly handles rollover to next day."""
        dt = datetime(2024, 1, 15, 23, 30, 0, 0)
        result = round_up_to_hour(dt)
        assert result == datetime(2024, 1, 16, 0, 0, 0, 0)

    def test_handles_month_rollover(self):
        """Correctly handles rollover to next month."""
        dt = datetime(2024, 1, 31, 23, 30, 0, 0)
        result = round_up_to_hour(dt)
        assert result == datetime(2024, 2, 1, 0, 0, 0, 0)


class TestGetLeaguePlayerCount:
    """Test player count retrieval."""

    def test_counts_zero_players(self, session: Session):
        """Returns 0 for empty league."""
        league = League(
            name="Empty League",
            organizer_id=1,
            registration_end=datetime.utcnow() + timedelta(days=7),
        )
        session.add(league)
        session.commit()

        count = get_league_player_count(session, league.id)
        assert count == 0

    def test_counts_all_players(self, session: Session):
        """Returns correct count of all players."""
        league = League(
            name="Test League",
            organizer_id=1,
            registration_end=datetime.utcnow() + timedelta(days=7),
        )
        session.add(league)
        session.commit()

        for i in range(5):
            player = LeaguePlayer(league_id=league.id, user_id=100 + i)
            session.add(player)
        session.commit()

        count = get_league_player_count(session, league.id)
        assert count == 5


class TestCalculateGroupPhaseRounds:
    """Test group phase round calculations."""

    def test_four_player_group_needs_3_rounds(self, session: Session):
        """4 players need 3 rounds (n-1)."""
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
                league_id=league.id, group_id=group.id, user_id=100 + i
            )
            session.add(player)
        session.commit()

        rounds = calculate_group_phase_rounds(session, league)
        assert rounds == 3

    def test_six_player_group_needs_5_rounds(self, session: Session):
        """6 players need 5 rounds."""
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

        for i in range(6):
            player = LeaguePlayer(
                league_id=league.id, group_id=group.id, user_id=100 + i
            )
            session.add(player)
        session.commit()

        rounds = calculate_group_phase_rounds(session, league)
        assert rounds == 5

    def test_uses_largest_group_size(self, session: Session):
        """Uses the largest group to determine rounds."""
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

        # Group A: 4 players
        for i in range(4):
            player = LeaguePlayer(
                league_id=league.id, group_id=group_a.id, user_id=100 + i
            )
            session.add(player)

        # Group B: 5 players (larger)
        for i in range(5):
            player = LeaguePlayer(
                league_id=league.id, group_id=group_b.id, user_id=200 + i
            )
            session.add(player)
        session.commit()

        rounds = calculate_group_phase_rounds(session, league)
        assert rounds == 4  # 5 - 1 = 4 (based on larger group)

    def test_returns_zero_for_no_groups(self, session: Session):
        """Returns 0 when no groups exist."""
        league = League(
            name="Test League",
            organizer_id=1,
            registration_end=datetime.utcnow() + timedelta(days=7),
        )
        session.add(league)
        session.commit()

        rounds = calculate_group_phase_rounds(session, league)
        assert rounds == 0


class TestGetQualifyingInfo:
    """Test knockout qualifying info calculation."""

    def test_no_knockout_returns_zero(self, session: Session):
        """Returns (0, 0) when knockout phase disabled."""
        league = League(
            name="Test League",
            organizer_id=1,
            registration_end=datetime.utcnow() + timedelta(days=7),
            has_knockout_phase=False,
        )
        session.add(league)
        session.commit()

        spots_per_group, total = get_qualifying_info(session, league)
        assert spots_per_group == 0
        assert total == 0

    def test_two_groups_top4_gives_2_per_group(self, session: Session):
        """2 groups with top 4 = 2 spots per group."""
        league = League(
            name="Test League",
            organizer_id=1,
            registration_end=datetime.utcnow() + timedelta(days=7),
            has_knockout_phase=True,
            knockout_size=4,
        )
        session.add(league)
        session.commit()

        group_a = Group(league_id=league.id, name="Group A")
        group_b = Group(league_id=league.id, name="Group B")
        session.add_all([group_a, group_b])
        session.commit()

        # 4 players per group = 8 total
        for i in range(4):
            session.add(
                LeaguePlayer(league_id=league.id, group_id=group_a.id, user_id=100 + i)
            )
            session.add(
                LeaguePlayer(league_id=league.id, group_id=group_b.id, user_id=200 + i)
            )
        session.commit()

        spots_per_group, total = get_qualifying_info(session, league)
        assert spots_per_group == 2
        assert total == 4

    def test_no_groups_returns_zero(self, session: Session):
        """Returns (0, 0) when no groups exist."""
        league = League(
            name="Test League",
            organizer_id=1,
            registration_end=datetime.utcnow() + timedelta(days=7),
            has_knockout_phase=True,
        )
        session.add(league)
        session.commit()

        spots_per_group, total = get_qualifying_info(session, league)
        assert spots_per_group == 0
        assert total == 0


class TestCalculatePhaseDates:
    """Test phase start/end date calculations."""

    def test_calculates_group_phase_dates(self, session: Session):
        """Calculates correct group phase duration."""
        league = League(
            name="Test League",
            organizer_id=1,
            registration_end=datetime.utcnow() + timedelta(days=7),
            days_per_match=14,
            has_knockout_phase=False,
        )
        session.add(league)
        session.commit()

        group = Group(league_id=league.id, name="Group A")
        session.add(group)
        session.commit()

        # 4 players = 3 rounds, 14 days each = 42 days
        for i in range(4):
            player = LeaguePlayer(
                league_id=league.id, group_id=group.id, user_id=100 + i
            )
            session.add(player)
        session.commit()

        start_date = datetime(2024, 1, 1, 12, 0, 0)
        group_start, group_end, knockout_start, knockout_end = calculate_phase_dates(
            session, league, start_date
        )

        assert group_start == datetime(2024, 1, 1, 12, 0, 0)
        # 3 rounds * 14 days = 42 days
        expected_group_end = datetime(2024, 2, 12, 12, 0, 0)
        assert group_end == expected_group_end
        assert knockout_start is None
        assert knockout_end is None

    def test_calculates_knockout_phase_dates(self, session: Session):
        """Calculates knockout phase following group phase."""
        league = League(
            name="Test League",
            organizer_id=1,
            registration_end=datetime.utcnow() + timedelta(days=7),
            days_per_match=14,
            has_knockout_phase=True,
            knockout_size=4,
        )
        session.add(league)
        session.commit()

        group = Group(league_id=league.id, name="Group A")
        session.add(group)
        session.commit()

        # 4 players
        for i in range(4):
            player = LeaguePlayer(
                league_id=league.id, group_id=group.id, user_id=100 + i
            )
            session.add(player)
        session.commit()

        start_date = datetime(2024, 1, 1, 12, 0, 0)
        group_start, group_end, knockout_start, knockout_end = calculate_phase_dates(
            session, league, start_date
        )

        # Top 4 knockout = 2 rounds (semi + final) * 14 days = 28 days
        assert knockout_start == group_end
        assert knockout_end is not None
        assert knockout_end > knockout_start
