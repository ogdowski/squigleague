"""Tests for matchup service - result workflow and list submission."""

from datetime import datetime, timedelta
from unittest.mock import patch

import pytest
from app.matchup.models import Matchup
from app.matchup.service import (
    AUTO_CONFIRM_HOURS,
    auto_confirm_expired_results,
    confirm_result,
    draw_random_map,
    edit_result,
    reveal_matchup,
    submit_list,
    submit_result,
)
from sqlmodel import Session


class TestSubmitList:
    """Test list submission and auto-reveal."""

    def test_submit_list_player1(self, session: Session):
        """Test player 1 submitting their list."""
        matchup = Matchup(
            name="test-list-p1",
            player1_id=1,
            player1_submitted=False,
            player2_submitted=False,
        )
        session.add(matchup)
        session.commit()

        result = submit_list(
            matchup=matchup,
            army_list="Stormcast Eternals\n- 10 Liberators",
            is_player1=True,
            session=session,
            user_id=1,
            army_faction="Stormcast Eternals",
        )

        assert result.player1_submitted is True
        assert result.player1_list == "Stormcast Eternals\n- 10 Liberators"
        assert result.player1_army_faction == "Stormcast Eternals"
        assert result.player2_submitted is False
        assert result.map_name is None  # Not revealed yet

    def test_submit_list_player2(self, session: Session):
        """Test player 2 submitting their list."""
        matchup = Matchup(
            name="test-list-p2",
            player1_id=1,
            player2_id=2,
            player1_submitted=True,
            player1_list="Stormcast list",
            player2_submitted=False,
        )
        session.add(matchup)
        session.commit()

        result = submit_list(
            matchup=matchup,
            army_list="Gloomspite Gitz\n- 20 Stabbas",
            is_player1=False,
            session=session,
            user_id=2,
            army_faction="Gloomspite Gitz",
        )

        assert result.player2_submitted is True
        assert result.player2_list == "Gloomspite Gitz\n- 20 Stabbas"
        assert result.player2_army_faction == "Gloomspite Gitz"

    def test_submit_list_auto_reveal_when_both_submitted(self, session: Session):
        """Test that matchup is auto-revealed when both lists are submitted."""
        matchup = Matchup(
            name="test-auto-reveal",
            player1_id=1,
            player2_id=2,
            player1_submitted=True,
            player1_list="Player 1 list",
            player2_submitted=False,
        )
        session.add(matchup)
        session.commit()

        with patch("app.matchup.service.draw_random_map") as mock_draw:
            mock_draw.return_value = "Passing Seasons"
            result = submit_list(
                matchup=matchup,
                army_list="Player 2 list",
                is_player1=False,
                session=session,
                user_id=2,
            )

        assert result.is_revealed is True
        assert result.map_name == "Passing Seasons"
        assert result.revealed_at is not None

    def test_submit_list_detects_faction_automatically(self, session: Session):
        """Test that faction is auto-detected from army list text."""
        matchup = Matchup(
            name="test-faction-detect",
            player1_id=1,
            player1_submitted=False,
            player2_submitted=False,
        )
        session.add(matchup)
        session.commit()

        result = submit_list(
            matchup=matchup,
            army_list="Ironjawz\n- Megaboss on Maw-krusha\n- 10 Brutes",
            is_player1=True,
            session=session,
            user_id=1,
            army_faction=None,  # Not provided, should be detected
        )

        assert result.player1_army_faction == "Ironjawz"

    def test_submit_list_already_submitted_raises_error(self, session: Session):
        """Test that submitting twice raises an error."""
        matchup = Matchup(
            name="test-double-submit",
            player1_id=1,
            player1_submitted=True,
            player1_list="Already submitted",
            player2_submitted=False,
        )
        session.add(matchup)
        session.commit()

        with pytest.raises(ValueError, match="already submitted"):
            submit_list(
                matchup=matchup,
                army_list="New list",
                is_player1=True,
                session=session,
                user_id=1,
            )


class TestRevealMatchup:
    """Test matchup reveal logic."""

    def test_reveal_matchup_assigns_random_map(self, session: Session):
        """Test that revealing assigns a random map."""
        matchup = Matchup(
            name="test-reveal",
            player1_id=1,
            player2_id=2,
            player1_submitted=True,
            player2_submitted=True,
            player1_list="List 1",
            player2_list="List 2",
            map_name=None,
        )
        session.add(matchup)
        session.commit()

        with patch("app.matchup.service.draw_random_map") as mock_draw:
            mock_draw.return_value = "Roiling Roots"
            result = reveal_matchup(matchup, session)

        assert result.map_name == "Roiling Roots"
        assert result.revealed_at is not None

    def test_reveal_matchup_not_ready_raises_error(self, session: Session):
        """Test that revealing before both submit raises error."""
        matchup = Matchup(
            name="test-reveal-early",
            player1_id=1,
            player1_submitted=True,
            player2_submitted=False,
            player1_list="List 1",
        )
        session.add(matchup)
        session.commit()

        with pytest.raises(ValueError, match="Both players must submit"):
            reveal_matchup(matchup, session)

    def test_reveal_matchup_already_revealed_returns_same(self, session: Session):
        """Test that revealing an already revealed matchup returns it unchanged."""
        matchup = Matchup(
            name="test-already-revealed",
            player1_id=1,
            player2_id=2,
            player1_submitted=True,
            player2_submitted=True,
            player1_list="List 1",
            player2_list="List 2",
            map_name="Already Set",
            revealed_at=datetime.utcnow(),
        )
        session.add(matchup)
        session.commit()

        result = reveal_matchup(matchup, session)

        assert result.map_name == "Already Set"


class TestSubmitResult:
    """Test result submission workflow."""

    def test_submit_result_sets_pending_confirmation(self, session: Session):
        """Test that submitting result sets pending_confirmation status."""
        matchup = Matchup(
            name="test-submit-result",
            player1_id=1,
            player2_id=2,
            player1_submitted=True,
            player2_submitted=True,
            player1_list="List 1",
            player2_list="List 2",
            map_name="Test Map",
            revealed_at=datetime.utcnow(),
        )
        session.add(matchup)
        session.commit()

        result = submit_result(
            matchup=matchup,
            player1_score=72,
            player2_score=65,
            submitted_by_user_id=1,
            session=session,
        )

        assert result.player1_score == 72
        assert result.player2_score == 65
        assert result.result_status == "pending_confirmation"
        assert result.result_submitted_by_id == 1
        assert result.result_submitted_at is not None
        assert result.result_auto_confirm_at is not None

    def test_submit_result_auto_confirms_when_opponent_anonymous(
        self, session: Session
    ):
        """Test that result is auto-confirmed when opponent is anonymous."""
        matchup = Matchup(
            name="test-anon-opponent",
            player1_id=1,
            player2_id=None,  # Anonymous opponent
            player1_submitted=True,
            player2_submitted=True,
            player1_list="List 1",
            player2_list="List 2",
            map_name="Test Map",
            revealed_at=datetime.utcnow(),
        )
        session.add(matchup)
        session.commit()

        result = submit_result(
            matchup=matchup,
            player1_score=80,
            player2_score=55,
            submitted_by_user_id=1,
            session=session,
        )

        assert result.result_status == "confirmed"
        assert result.result_confirmed_at is not None
        assert result.result_auto_confirm_at is None

    def test_submit_result_not_revealed_raises_error(self, session: Session):
        """Test that submitting result before reveal raises error."""
        matchup = Matchup(
            name="test-not-revealed",
            player1_id=1,
            player2_id=2,
            player1_submitted=True,
            player2_submitted=False,
            player1_list="List 1",
        )
        session.add(matchup)
        session.commit()

        with pytest.raises(ValueError, match="must be revealed"):
            submit_result(
                matchup=matchup,
                player1_score=70,
                player2_score=60,
                submitted_by_user_id=1,
                session=session,
            )

    def test_submit_result_already_confirmed_raises_error(self, session: Session):
        """Test that submitting to confirmed matchup raises error."""
        matchup = Matchup(
            name="test-already-confirmed",
            player1_id=1,
            player2_id=2,
            player1_submitted=True,
            player2_submitted=True,
            player1_list="List 1",
            player2_list="List 2",
            map_name="Test Map",
            revealed_at=datetime.utcnow(),
            result_status="confirmed",
            player1_score=70,
            player2_score=60,
        )
        session.add(matchup)
        session.commit()

        with pytest.raises(ValueError, match="already been confirmed"):
            submit_result(
                matchup=matchup,
                player1_score=75,
                player2_score=55,
                submitted_by_user_id=1,
                session=session,
            )

    def test_submit_result_non_player_raises_error(self, session: Session):
        """Test that non-player cannot submit result."""
        matchup = Matchup(
            name="test-non-player",
            player1_id=1,
            player2_id=2,
            player1_submitted=True,
            player2_submitted=True,
            player1_list="List 1",
            player2_list="List 2",
            map_name="Test Map",
            revealed_at=datetime.utcnow(),
        )
        session.add(matchup)
        session.commit()

        with pytest.raises(ValueError, match="Only players"):
            submit_result(
                matchup=matchup,
                player1_score=70,
                player2_score=60,
                submitted_by_user_id=999,  # Not a player
                session=session,
            )


class TestConfirmResult:
    """Test result confirmation workflow."""

    def test_confirm_result_by_opponent(self, session: Session):
        """Test opponent confirming the result."""
        matchup = Matchup(
            name="test-confirm",
            player1_id=1,
            player2_id=2,
            player1_submitted=True,
            player2_submitted=True,
            player1_list="List 1",
            player2_list="List 2",
            map_name="Test Map",
            revealed_at=datetime.utcnow(),
            result_status="pending_confirmation",
            player1_score=72,
            player2_score=65,
            result_submitted_by_id=1,
            result_submitted_at=datetime.utcnow(),
            result_auto_confirm_at=datetime.utcnow() + timedelta(hours=24),
        )
        session.add(matchup)
        session.commit()

        result = confirm_result(
            matchup=matchup,
            confirmed_by_user_id=2,  # Opponent confirms
            session=session,
        )

        assert result.result_status == "confirmed"
        assert result.result_confirmed_by_id == 2
        assert result.result_confirmed_at is not None
        assert result.result_auto_confirm_at is None

    def test_confirm_own_result_raises_error(self, session: Session):
        """Test that submitter cannot confirm their own result."""
        matchup = Matchup(
            name="test-self-confirm",
            player1_id=1,
            player2_id=2,
            player1_submitted=True,
            player2_submitted=True,
            player1_list="List 1",
            player2_list="List 2",
            map_name="Test Map",
            revealed_at=datetime.utcnow(),
            result_status="pending_confirmation",
            player1_score=72,
            player2_score=65,
            result_submitted_by_id=1,
        )
        session.add(matchup)
        session.commit()

        with pytest.raises(ValueError, match="cannot confirm your own"):
            confirm_result(
                matchup=matchup,
                confirmed_by_user_id=1,  # Same as submitter
                session=session,
            )

    def test_confirm_no_pending_result_raises_error(self, session: Session):
        """Test confirming when no pending result raises error."""
        matchup = Matchup(
            name="test-no-pending",
            player1_id=1,
            player2_id=2,
            player1_submitted=True,
            player2_submitted=True,
            player1_list="List 1",
            player2_list="List 2",
            map_name="Test Map",
            revealed_at=datetime.utcnow(),
            result_status=None,  # No result submitted
        )
        session.add(matchup)
        session.commit()

        with pytest.raises(ValueError, match="No pending result"):
            confirm_result(
                matchup=matchup,
                confirmed_by_user_id=2,
                session=session,
            )


class TestEditResult:
    """Test result editing workflow."""

    def test_edit_result_swaps_submitter(self, session: Session):
        """Test that editing result makes editor the new submitter."""
        matchup = Matchup(
            name="test-edit",
            player1_id=1,
            player2_id=2,
            player1_submitted=True,
            player2_submitted=True,
            player1_list="List 1",
            player2_list="List 2",
            map_name="Test Map",
            revealed_at=datetime.utcnow(),
            result_status="pending_confirmation",
            player1_score=72,
            player2_score=65,
            result_submitted_by_id=1,
            result_submitted_at=datetime.utcnow() - timedelta(hours=1),
            result_auto_confirm_at=datetime.utcnow() + timedelta(hours=23),
        )
        session.add(matchup)
        session.commit()

        result = edit_result(
            matchup=matchup,
            player1_score=65,  # Swapped scores
            player2_score=72,
            edited_by_user_id=2,  # Opponent edits
            session=session,
        )

        assert result.player1_score == 65
        assert result.player2_score == 72
        assert result.result_submitted_by_id == 2  # Now player 2 is submitter
        assert result.result_status == "pending_confirmation"

    def test_edit_own_result_raises_error(self, session: Session):
        """Test that submitter cannot edit their own result."""
        matchup = Matchup(
            name="test-self-edit",
            player1_id=1,
            player2_id=2,
            player1_submitted=True,
            player2_submitted=True,
            player1_list="List 1",
            player2_list="List 2",
            map_name="Test Map",
            revealed_at=datetime.utcnow(),
            result_status="pending_confirmation",
            player1_score=72,
            player2_score=65,
            result_submitted_by_id=1,
        )
        session.add(matchup)
        session.commit()

        with pytest.raises(ValueError, match="cannot edit your own"):
            edit_result(
                matchup=matchup,
                player1_score=75,
                player2_score=60,
                edited_by_user_id=1,  # Same as submitter
                session=session,
            )


class TestAutoConfirmExpiredResults:
    """Test auto-confirmation of expired results."""

    def test_auto_confirm_expired_results(self, session: Session):
        """Test that expired results are auto-confirmed."""
        # Create matchup with expired auto_confirm_at
        matchup = Matchup(
            name="test-auto-confirm",
            player1_id=1,
            player2_id=2,
            player1_submitted=True,
            player2_submitted=True,
            player1_list="List 1",
            player2_list="List 2",
            map_name="Test Map",
            revealed_at=datetime.utcnow(),
            result_status="pending_confirmation",
            player1_score=72,
            player2_score=65,
            result_submitted_by_id=1,
            result_submitted_at=datetime.utcnow() - timedelta(hours=25),
            result_auto_confirm_at=datetime.utcnow() - timedelta(hours=1),  # Expired
        )
        session.add(matchup)
        session.commit()

        count = auto_confirm_expired_results(session)

        assert count == 1
        session.refresh(matchup)
        assert matchup.result_status == "confirmed"
        assert matchup.result_confirmed_at is not None
        assert matchup.result_auto_confirm_at is None

    def test_auto_confirm_skips_not_expired(self, session: Session):
        """Test that non-expired results are not auto-confirmed."""
        matchup = Matchup(
            name="test-not-expired",
            player1_id=1,
            player2_id=2,
            player1_submitted=True,
            player2_submitted=True,
            player1_list="List 1",
            player2_list="List 2",
            map_name="Test Map",
            revealed_at=datetime.utcnow(),
            result_status="pending_confirmation",
            player1_score=72,
            player2_score=65,
            result_submitted_by_id=1,
            result_auto_confirm_at=datetime.utcnow()
            + timedelta(hours=23),  # Not expired
        )
        session.add(matchup)
        session.commit()

        count = auto_confirm_expired_results(session)

        assert count == 0
        session.refresh(matchup)
        assert matchup.result_status == "pending_confirmation"
