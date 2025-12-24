"""
Matchup Routes

API endpoints for matchup functionality (list exchange and battle plan generation).
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.db import get_session
from app.config import settings
from app.matchup import service
from app.matchup.schemas import (
    MatchupCreate,
    MatchupCreateResponse,
    ListSubmit,
    ListSubmitResponse,
    MatchupStatus,
    MatchupReveal,
    BattlePlanData,
    MatchupHistoryItem,
)


router = APIRouter(prefix="/api/matchup", tags=["matchup"])


# ═══════════════════════════════════════════════
# PUBLIC ENDPOINTS (Anonymous + Authenticated)
# ═══════════════════════════════════════════════


@router.post("", response_model=MatchupCreateResponse)
async def create_matchup(
    request: MatchupCreate,
    session: Session = Depends(get_session),
):
    """
    Create a new matchup.
    
    Works for both anonymous and authenticated users.
    Returns a unique UUID link to share with opponent.
    """
    # TODO: Get current user if authenticated (when auth is ready)
    creator_user_id = None
    
    matchup = service.create_matchup(
        session=session,
        game_system=request.game_system,
        creator_user_id=creator_user_id,
    )
    
    # Build share URL
    share_url = f"{settings.FRONTEND_URL}/matchup/{matchup.uuid}"
    
    return MatchupCreateResponse(
        uuid=matchup.uuid,
        game_system=matchup.game_system,
        share_url=share_url,
        created_at=matchup.created_at,
        expires_at=matchup.expires_at,
    )


@router.get("/{uuid}", response_model=MatchupStatus)
async def get_matchup_status(
    uuid: str,
    session: Session = Depends(get_session),
):
    """
    Get matchup status (before both lists submitted).
    
    Shows submission status but not the lists themselves.
    Public endpoint - no authentication required.
    """
    matchup = service.get_matchup(session, uuid)
    
    return MatchupStatus(
        uuid=matchup.uuid,
        game_system=matchup.game_system,
        player1_submitted=matchup.player1_submitted,
        player2_submitted=matchup.player2_submitted,
        waiting_count=matchup.get_waiting_count(),
        is_complete=matchup.is_complete(),
        is_expired=matchup.is_expired(),
        created_at=matchup.created_at,
        expires_at=matchup.expires_at,
    )


@router.post("/{uuid}/submit", response_model=ListSubmitResponse)
async def submit_army_list(
    uuid: str,
    request: ListSubmit,
    session: Session = Depends(get_session),
):
    """
    Submit an army list to a matchup.
    
    First submission: Player 1's list
    Second submission: Player 2's list (triggers battle plan generation)
    
    Public endpoint - works for anonymous and authenticated users.
    """
    # TODO: Get current user if authenticated
    user_id = None
    
    matchup, player_number, both_submitted = service.submit_list(
        session=session,
        uuid=uuid,
        player_name=request.player_name,
        army_list=request.army_list,
        user_id=user_id,
    )
    
    if both_submitted:
        message = "List submitted! Battle plan generated. You can now view the reveal."
    else:
        message = f"List submitted as Player {player_number}. Waiting for opponent."
    
    return ListSubmitResponse(
        message=message,
        player_number=player_number,
        waiting_for_opponent=not both_submitted,
        both_submitted=both_submitted,
    )


@router.get("/{uuid}/reveal", response_model=MatchupReveal)
async def reveal_matchup(
    uuid: str,
    session: Session = Depends(get_session),
):
    """
    Reveal both lists and battle plan.
    
    Only works after both players have submitted their lists.
    Public endpoint - no authentication required.
    """
    matchup = service.get_matchup(session, uuid)
    
    if not matchup.is_complete():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot reveal: waiting for {2 - matchup.get_waiting_count()} more player(s)"
        )
    
    # Build battle plan data
    bp = matchup.battle_plan
    battle_plan = BattlePlanData(
        name=bp["name"],
        deployment=bp["deployment"],
        deployment_description=bp["deployment_description"],
        primary_objective=bp["primary_objective"],
        secondary_objectives=bp["secondary_objectives"],
        victory_conditions=bp["victory_conditions"],
        turn_limit=bp["turn_limit"],
        special_rules=bp.get("special_rules"),
        battle_tactics=bp.get("battle_tactics"),
    )
    
    return MatchupReveal(
        uuid=matchup.uuid,
        game_system=matchup.game_system,
        player1_name=matchup.player1_name,
        player1_list=matchup.player1_list,
        player1_submitted_at=matchup.created_at,  # Approximation
        player2_name=matchup.player2_name,
        player2_list=matchup.player2_list,
        player2_submitted_at=matchup.revealed_at or matchup.created_at,
        battle_plan=battle_plan,
        map_name=matchup.map_name,
        created_at=matchup.created_at,
        revealed_at=matchup.revealed_at or matchup.created_at,
    )


# ═══════════════════════════════════════════════
# AUTHENTICATED ENDPOINTS
# ═══════════════════════════════════════════════


@router.get("/history/me", response_model=list[MatchupHistoryItem])
async def get_my_matchup_history(
    session: Session = Depends(get_session),
    limit: int = 50,
):
    """
    Get matchup history for authenticated user.
    
    TODO: Add authentication when ready
    """
    # TODO: Get current user
    # current_user: User = Depends(current_active_user)
    
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Authentication not yet implemented. Use public matchup endpoints."
    )
    
    # matchups = service.get_matchup_history(session, current_user.id, limit)
    # return [MatchupHistoryItem.model_validate(m) for m in matchups]
