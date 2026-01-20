import random
from datetime import datetime, timedelta
from typing import Optional

from app.league.constants import BATTLE_PLAN_DATA, MAP_IMAGES, MISSION_MAPS
from app.matchup.constants import ARMY_FACTIONS, detect_army_faction
from app.matchup.models import Matchup
from sqlmodel import Session, select

# Auto-confirm result after 24 hours
AUTO_CONFIRM_HOURS = 24


def get_map_image(map_name: str) -> str | None:
    """Get battle plan image filename for a map name."""
    return MAP_IMAGES.get(map_name)


def get_battle_plan_data(map_name: str) -> dict | None:
    """Get full battle plan data for a map name."""
    return BATTLE_PLAN_DATA.get(map_name)


def draw_random_map() -> str:
    """Draw a random map from the available maps."""
    return random.choice(MISSION_MAPS)


def get_army_factions() -> list[str]:
    """Return list of available army factions."""
    return ARMY_FACTIONS


def reveal_matchup(matchup: Matchup, session: Session) -> Matchup:
    """Reveal matchup by assigning a random map."""
    if not matchup.is_revealed:
        raise ValueError("Both players must submit their lists before revealing")

    if matchup.map_name:
        return matchup  # Already revealed

    matchup.map_name = draw_random_map()
    matchup.revealed_at = datetime.utcnow()

    session.add(matchup)
    session.commit()
    session.refresh(matchup)

    return matchup


def submit_list(
    matchup: Matchup,
    army_list: str,
    is_player1: bool,
    session: Session,
    user_id: int = None,
    army_faction: str = None,
) -> Matchup:
    """Submit an army list for a matchup."""
    # If no army faction provided, try to detect from list
    if not army_faction:
        army_faction = detect_army_faction(army_list)

    if is_player1:
        if matchup.player1_submitted:
            raise ValueError("Player 1 has already submitted their list")
        matchup.player1_list = army_list
        matchup.player1_army_faction = army_faction
        matchup.player1_submitted = True
        if user_id and not matchup.player1_id:
            matchup.player1_id = user_id
    else:
        if matchup.player2_submitted:
            raise ValueError("Player 2 has already submitted their list")
        matchup.player2_list = army_list
        matchup.player2_army_faction = army_faction
        matchup.player2_submitted = True
        if user_id:
            matchup.player2_id = user_id

    session.add(matchup)
    session.commit()
    session.refresh(matchup)

    # Auto-reveal if both lists are submitted
    if matchup.is_revealed and not matchup.map_name:
        matchup = reveal_matchup(matchup, session)

    return matchup


def submit_result(
    matchup: Matchup,
    player1_score: int,
    player2_score: int,
    submitted_by_user_id: int,
    session: Session,
) -> Matchup:
    """
    Submit a match result.

    The result goes into pending_confirmation state and waits for the opponent
    to confirm, or auto-confirms after 24 hours.
    """
    if not matchup.is_revealed:
        raise ValueError("Matchup must be revealed before submitting result")

    if matchup.result_status == "confirmed":
        raise ValueError("Result has already been confirmed")

    # Verify user is one of the players
    if submitted_by_user_id not in (matchup.player1_id, matchup.player2_id):
        raise ValueError("Only players in this matchup can submit results")

    # Check if at least one player is registered
    if matchup.player1_id is None and matchup.player2_id is None:
        raise ValueError("At least one player must be registered to submit results")

    # Determine if opponent is registered
    opponent_is_registered = False
    if submitted_by_user_id == matchup.player1_id:
        opponent_is_registered = matchup.player2_id is not None
    else:
        opponent_is_registered = matchup.player1_id is not None

    matchup.player1_score = player1_score
    matchup.player2_score = player2_score
    matchup.result_submitted_by_id = submitted_by_user_id
    matchup.result_submitted_at = datetime.utcnow()

    # If opponent is not registered, auto-confirm immediately
    if not opponent_is_registered:
        matchup.result_status = "confirmed"
        matchup.result_confirmed_at = datetime.utcnow()
        matchup.result_auto_confirm_at = None
    else:
        # Set to pending_confirmation with 24h auto-confirm
        matchup.result_status = "pending_confirmation"
        matchup.result_auto_confirm_at = datetime.utcnow() + timedelta(
            hours=AUTO_CONFIRM_HOURS
        )

    session.add(matchup)
    session.commit()
    session.refresh(matchup)

    return matchup


def confirm_result(
    matchup: Matchup,
    confirmed_by_user_id: int,
    session: Session,
) -> Matchup:
    """Confirm a pending match result."""
    if matchup.result_status != "pending_confirmation":
        raise ValueError("No pending result to confirm")

    # Verify user is the opponent (not the one who submitted)
    if confirmed_by_user_id == matchup.result_submitted_by_id:
        raise ValueError("You cannot confirm your own result submission")

    if confirmed_by_user_id not in (matchup.player1_id, matchup.player2_id):
        raise ValueError("Only players in this matchup can confirm results")

    matchup.result_status = "confirmed"
    matchup.result_confirmed_by_id = confirmed_by_user_id
    matchup.result_confirmed_at = datetime.utcnow()
    matchup.result_auto_confirm_at = None  # Clear auto-confirm

    session.add(matchup)
    session.commit()
    session.refresh(matchup)

    return matchup


def edit_result(
    matchup: Matchup,
    player1_score: int,
    player2_score: int,
    edited_by_user_id: int,
    session: Session,
) -> Matchup:
    """
    Edit a pending match result.

    When opponent edits the result, they become the new submitter
    and the original submitter needs to confirm.
    """
    if matchup.result_status != "pending_confirmation":
        raise ValueError("No pending result to edit")

    if edited_by_user_id == matchup.result_submitted_by_id:
        raise ValueError("You cannot edit your own result submission")

    if edited_by_user_id not in (matchup.player1_id, matchup.player2_id):
        raise ValueError("Only players in this matchup can edit results")

    # Update scores
    matchup.player1_score = player1_score
    matchup.player2_score = player2_score

    # Swap submitter - now the editor becomes the submitter
    matchup.result_submitted_by_id = edited_by_user_id
    matchup.result_submitted_at = datetime.utcnow()

    # Reset auto-confirm timer
    matchup.result_auto_confirm_at = datetime.utcnow() + timedelta(
        hours=AUTO_CONFIRM_HOURS
    )

    session.add(matchup)
    session.commit()
    session.refresh(matchup)

    return matchup


def auto_confirm_expired_results(session: Session) -> int:
    """
    Auto-confirm results that have passed their auto_confirm_at time.
    Returns the number of results confirmed.
    """
    now = datetime.utcnow()
    statement = select(Matchup).where(
        Matchup.result_status == "pending_confirmation",
        Matchup.result_auto_confirm_at <= now,
    )
    matchups = session.scalars(statement).all()

    count = 0
    for matchup in matchups:
        matchup.result_status = "confirmed"
        matchup.result_confirmed_at = now
        matchup.result_auto_confirm_at = None
        session.add(matchup)
        count += 1

    if count > 0:
        session.commit()

    return count


def get_result_info_message(
    matchup: Matchup, current_user_id: Optional[int]
) -> Optional[str]:
    """
    Get info message about result submission for the current user.
    """
    if not matchup.is_revealed:
        return None

    # If result is already confirmed, no message needed
    if matchup.result_status == "confirmed":
        return None

    # Both players anonymous - can't submit results
    if matchup.player1_id is None and matchup.player2_id is None:
        return "Create an account to submit match results."

    # Current user is not logged in
    if current_user_id is None:
        # Check if they could be one of the players
        if matchup.player1_id is None or matchup.player2_id is None:
            return "Log in or create an account to submit match results."
        return "Log in to submit or confirm match results."

    # User is logged in but not a player in this matchup
    if current_user_id not in (matchup.player1_id, matchup.player2_id):
        return None

    # Pending confirmation - message for the opponent
    if matchup.result_status == "pending_confirmation":
        if current_user_id != matchup.result_submitted_by_id:
            return "Your opponent submitted a result. Please confirm or dispute it."

    return None
