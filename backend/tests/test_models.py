"""Tests for model methods and properties."""

from datetime import datetime, timedelta

import pytest
from app.league.models import Group, League, LeaguePlayer, Match
from app.matchup.models import Matchup


class TestMatchupModel:
    """Test Matchup model methods and properties."""

    class TestIsRevealed:
        """Test is_revealed property."""

        def test_not_revealed_when_no_submissions(self):
            matchup = Matchup(
                name="test",
                player1_submitted=False,
                player2_submitted=False,
            )
            assert matchup.is_revealed is False

        def test_not_revealed_when_only_player1_submitted(self):
            matchup = Matchup(
                name="test",
                player1_submitted=True,
                player2_submitted=False,
            )
            assert matchup.is_revealed is False

        def test_not_revealed_when_only_player2_submitted(self):
            matchup = Matchup(
                name="test",
                player1_submitted=False,
                player2_submitted=True,
            )
            assert matchup.is_revealed is False

        def test_revealed_when_both_submitted(self):
            matchup = Matchup(
                name="test",
                player1_submitted=True,
                player2_submitted=True,
            )
            assert matchup.is_revealed is True

    class TestHasResult:
        """Test has_result property."""

        def test_no_result_when_status_none(self):
            matchup = Matchup(name="test", result_status=None)
            assert matchup.has_result is False

        def test_has_result_when_pending(self):
            matchup = Matchup(name="test", result_status="pending_confirmation")
            assert matchup.has_result is True

        def test_has_result_when_confirmed(self):
            matchup = Matchup(name="test", result_status="confirmed")
            assert matchup.has_result is True

    class TestIsResultConfirmed:
        """Test is_result_confirmed property."""

        def test_not_confirmed_when_pending(self):
            matchup = Matchup(name="test", result_status="pending_confirmation")
            assert matchup.is_result_confirmed is False

        def test_confirmed_when_confirmed(self):
            matchup = Matchup(name="test", result_status="confirmed")
            assert matchup.is_result_confirmed is True

        def test_not_confirmed_when_none(self):
            matchup = Matchup(name="test", result_status=None)
            assert matchup.is_result_confirmed is False

    class TestWinnerId:
        """Test winner_id property."""

        def test_none_when_not_confirmed(self):
            matchup = Matchup(
                name="test",
                player1_id=1,
                player2_id=2,
                player1_score=72,
                player2_score=65,
                result_status="pending_confirmation",
            )
            assert matchup.winner_id is None

        def test_player1_wins(self):
            matchup = Matchup(
                name="test",
                player1_id=1,
                player2_id=2,
                player1_score=72,
                player2_score=65,
                result_status="confirmed",
            )
            assert matchup.winner_id == 1

        def test_player2_wins(self):
            matchup = Matchup(
                name="test",
                player1_id=1,
                player2_id=2,
                player1_score=65,
                player2_score=72,
                result_status="confirmed",
            )
            assert matchup.winner_id == 2

        def test_draw_returns_none(self):
            matchup = Matchup(
                name="test",
                player1_id=1,
                player2_id=2,
                player1_score=70,
                player2_score=70,
                result_status="confirmed",
            )
            assert matchup.winner_id is None

    class TestCanSubmitResult:
        """Test can_submit_result method."""

        def test_cannot_submit_before_reveal(self):
            matchup = Matchup(
                name="test",
                player1_id=1,
                player2_id=2,
                player1_submitted=True,
                player2_submitted=False,
            )
            assert matchup.can_submit_result(user_id=1) is False

        def test_cannot_submit_when_confirmed(self):
            matchup = Matchup(
                name="test",
                player1_id=1,
                player2_id=2,
                player1_submitted=True,
                player2_submitted=True,
                result_status="confirmed",
            )
            assert matchup.can_submit_result(user_id=1) is False

        def test_cannot_submit_when_both_anonymous(self):
            matchup = Matchup(
                name="test",
                player1_id=None,
                player2_id=None,
                player1_submitted=True,
                player2_submitted=True,
            )
            assert matchup.can_submit_result(user_id=1) is False

        def test_cannot_submit_when_not_a_player(self):
            matchup = Matchup(
                name="test",
                player1_id=1,
                player2_id=2,
                player1_submitted=True,
                player2_submitted=True,
            )
            assert matchup.can_submit_result(user_id=999) is False

        def test_can_submit_when_revealed_and_is_player(self):
            matchup = Matchup(
                name="test",
                player1_id=1,
                player2_id=2,
                player1_submitted=True,
                player2_submitted=True,
            )
            assert matchup.can_submit_result(user_id=1) is True
            assert matchup.can_submit_result(user_id=2) is True

        def test_can_resubmit_when_pending(self):
            matchup = Matchup(
                name="test",
                player1_id=1,
                player2_id=2,
                player1_submitted=True,
                player2_submitted=True,
                result_status="pending_confirmation",
            )
            # Can resubmit while pending (for edits)
            assert matchup.can_submit_result(user_id=1) is True

    class TestCanConfirmResult:
        """Test can_confirm_result method."""

        def test_cannot_confirm_when_not_pending(self):
            matchup = Matchup(
                name="test",
                player1_id=1,
                player2_id=2,
                result_status=None,
            )
            assert matchup.can_confirm_result(user_id=2) is False

        def test_cannot_confirm_own_submission(self):
            matchup = Matchup(
                name="test",
                player1_id=1,
                player2_id=2,
                result_status="pending_confirmation",
                result_submitted_by_id=1,
            )
            assert matchup.can_confirm_result(user_id=1) is False

        def test_opponent_can_confirm(self):
            matchup = Matchup(
                name="test",
                player1_id=1,
                player2_id=2,
                result_status="pending_confirmation",
                result_submitted_by_id=1,
            )
            assert matchup.can_confirm_result(user_id=2) is True

        def test_player1_can_confirm_player2_submission(self):
            matchup = Matchup(
                name="test",
                player1_id=1,
                player2_id=2,
                result_status="pending_confirmation",
                result_submitted_by_id=2,
            )
            assert matchup.can_confirm_result(user_id=1) is True

        def test_anonymous_cannot_confirm(self):
            matchup = Matchup(
                name="test",
                player1_id=1,
                player2_id=2,
                result_status="pending_confirmation",
                result_submitted_by_id=1,
            )
            assert matchup.can_confirm_result(user_id=None) is False


class TestMatchModel:
    """Test Match model methods and properties."""

    class TestIsCompleted:
        """Test is_completed property."""

        def test_not_completed_when_scheduled(self):
            match = Match(
                league_id=1,
                player1_id=1,
                player2_id=2,
                phase="group",
                status="scheduled",
            )
            assert match.is_completed is False

        def test_not_completed_when_pending(self):
            match = Match(
                league_id=1,
                player1_id=1,
                player2_id=2,
                phase="group",
                status="pending_confirmation",
            )
            assert match.is_completed is False

        def test_completed_when_confirmed(self):
            match = Match(
                league_id=1,
                player1_id=1,
                player2_id=2,
                phase="group",
                status="confirmed",
            )
            assert match.is_completed is True

    class TestWinnerId:
        """Test winner_id property."""

        def test_none_when_not_completed(self):
            match = Match(
                league_id=1,
                player1_id=1,
                player2_id=2,
                phase="group",
                status="pending_confirmation",
                player1_score=72,
                player2_score=65,
            )
            assert match.winner_id is None

        def test_player1_wins(self):
            match = Match(
                league_id=1,
                player1_id=1,
                player2_id=2,
                phase="group",
                status="confirmed",
                player1_score=72,
                player2_score=65,
            )
            assert match.winner_id == 1

        def test_player2_wins(self):
            match = Match(
                league_id=1,
                player1_id=1,
                player2_id=2,
                phase="group",
                status="confirmed",
                player1_score=65,
                player2_score=72,
            )
            assert match.winner_id == 2

        def test_draw_returns_none(self):
            match = Match(
                league_id=1,
                player1_id=1,
                player2_id=2,
                phase="group",
                status="confirmed",
                player1_score=70,
                player2_score=70,
            )
            assert match.winner_id is None

    class TestBothListsSubmitted:
        """Test both_lists_submitted property."""

        def test_false_when_no_lists(self):
            match = Match(
                league_id=1,
                player1_id=1,
                player2_id=2,
                phase="group",
                status="scheduled",
                player1_army_list=None,
                player2_army_list=None,
            )
            assert match.both_lists_submitted is False

        def test_false_when_only_player1_list(self):
            match = Match(
                league_id=1,
                player1_id=1,
                player2_id=2,
                phase="group",
                status="scheduled",
                player1_army_list="some list",
                player2_army_list=None,
            )
            assert match.both_lists_submitted is False

        def test_true_when_both_lists(self):
            match = Match(
                league_id=1,
                player1_id=1,
                player2_id=2,
                phase="group",
                status="scheduled",
                player1_army_list="list 1",
                player2_army_list="list 2",
            )
            assert match.both_lists_submitted is True

    class TestListsRevealed:
        """Test lists_revealed property."""

        def test_not_revealed_when_no_timestamp(self):
            match = Match(
                league_id=1,
                player1_id=1,
                player2_id=2,
                phase="group",
                status="scheduled",
                lists_revealed_at=None,
            )
            assert match.lists_revealed is False

        def test_revealed_when_timestamp_set(self):
            match = Match(
                league_id=1,
                player1_id=1,
                player2_id=2,
                phase="group",
                status="scheduled",
                lists_revealed_at=datetime.utcnow(),
            )
            assert match.lists_revealed is True


class TestLeaguePlayerModel:
    """Test LeaguePlayer model properties."""

    class TestAveragePoints:
        """Test average_points property."""

        def test_zero_when_no_games(self):
            player = LeaguePlayer(
                league_id=1, user_id=1, games_played=0, total_points=0
            )
            assert player.average_points == 0.0

        def test_calculates_average(self):
            player = LeaguePlayer(
                league_id=1, user_id=1, games_played=3, total_points=3000
            )
            assert player.average_points == 1000.0

        def test_handles_fractional_average(self):
            player = LeaguePlayer(
                league_id=1, user_id=1, games_played=3, total_points=3200
            )
            assert player.average_points == pytest.approx(1066.67, rel=0.01)


class TestLeagueModel:
    """Test League model properties."""

    class TestIsRegistrationOpen:
        """Test is_registration_open property."""

        def test_open_during_registration_period(self):
            league = League(
                name="Test",
                organizer_id=1,
                status="registration",
                registration_end=datetime.utcnow() + timedelta(days=7),
            )
            assert league.is_registration_open is True

        def test_closed_after_registration_end(self):
            league = League(
                name="Test",
                organizer_id=1,
                status="registration",
                registration_end=datetime.utcnow() - timedelta(days=1),
            )
            assert league.is_registration_open is False

        def test_closed_when_not_in_registration_status(self):
            league = League(
                name="Test",
                organizer_id=1,
                status="group_phase",
                registration_end=datetime.utcnow() + timedelta(days=7),
            )
            assert league.is_registration_open is False
