import random
from datetime import datetime

from app.league.constants import MISSION_MAPS
from app.matchup.models import Matchup
from sqlmodel import Session


def draw_random_map() -> str:
    """Draw a random map from the available maps."""
    return random.choice(MISSION_MAPS)


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
) -> Matchup:
    """Submit an army list for a matchup."""
    if is_player1:
        if matchup.player1_submitted:
            raise ValueError("Player 1 has already submitted their list")
        matchup.player1_list = army_list
        matchup.player1_submitted = True
        if user_id and not matchup.player1_id:
            matchup.player1_id = user_id
    else:
        if matchup.player2_submitted:
            raise ValueError("Player 2 has already submitted their list")
        matchup.player2_list = army_list
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
