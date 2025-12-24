"""
Matchup Service

Business logic for matchup management with database persistence.
Migrated and enhanced from squire/matchup.py
"""

import secrets
from datetime import datetime
from typing import Optional
from sqlmodel import Session, select
from fastapi import HTTPException, status

from app.matchup.models import Matchup
from app.matchup.battle_plans import BattlePlan, GameSystem, generate_battle_plan


def create_matchup(
    session: Session,
    game_system: str,
    creator_user_id: Optional[int] = None,
) -> Matchup:
    """
    Create a new matchup for the given game system.
    
    Args:
        session: Database session
        game_system: Game system identifier
        creator_user_id: Optional user ID of the matchup creator
        
    Returns:
        New Matchup instance saved to database
    """
    # Validate game system
    try:
        GameSystem(game_system)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid game system. Must be one of: {[gs.value for gs in GameSystem]}"
        )
    
    # Generate unique UUID
    uuid = secrets.token_urlsafe(12)
    
    # Create matchup
    matchup = Matchup(
        uuid=uuid,
        game_system=game_system,
        player1_user_id=creator_user_id,
    )
    
    session.add(matchup)
    session.commit()
    session.refresh(matchup)
    
    return matchup


def get_matchup(session: Session, uuid: str) -> Matchup:
    """
    Get matchup by UUID.
    
    Args:
        session: Database session
        uuid: Matchup UUID
        
    Returns:
        Matchup instance
        
    Raises:
        HTTPException: If matchup not found or expired
    """
    statement = select(Matchup).where(Matchup.uuid == uuid)
    matchup = session.exec(statement).first()
    
    if not matchup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Matchup not found"
        )
    
    if matchup.is_expired():
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Matchup has expired (older than 7 days)"
        )
    
    return matchup


def submit_list(
    session: Session,
    uuid: str,
    player_name: str,
    army_list: str,
    user_id: Optional[int] = None,
) -> tuple[Matchup, int, bool]:
    """
    Submit an army list to a matchup.
    
    Args:
        session: Database session
        uuid: Matchup UUID
        player_name: Player's display name
        army_list: Army list text
        user_id: Optional authenticated user ID
        
    Returns:
        Tuple of (matchup, player_number, both_submitted)
        player_number: 1 or 2
        both_submitted: True if this was the second submission
        
    Raises:
        HTTPException: If matchup not found, expired, or already complete
    """
    matchup = get_matchup(session, uuid)
    
    if matchup.is_complete():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Matchup already has two players"
        )
    
    # Determine which player slot to fill
    if not matchup.player1_submitted:
        # First player
        matchup.player1_name = player_name
        matchup.player1_list = army_list
        matchup.player1_submitted = True
        if user_id and not matchup.player1_user_id:
            matchup.player1_user_id = user_id
        player_number = 1
        
    elif not matchup.player2_submitted:
        # Second player
        matchup.player2_name = player_name
        matchup.player2_list = army_list
        matchup.player2_submitted = True
        if user_id:
            matchup.player2_user_id = user_id
        player_number = 2
        
        # Generate battle plan when second player submits
        _generate_and_save_battle_plan(matchup)
        matchup.revealed_at = datetime.utcnow()
        
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Matchup already complete"
        )
    
    session.add(matchup)
    session.commit()
    session.refresh(matchup)
    
    return matchup, player_number, matchup.is_complete()


def _generate_and_save_battle_plan(matchup: Matchup) -> None:
    """
    Generate battle plan and save to matchup.
    
    Args:
        matchup: Matchup instance to update
    """
    game_system = GameSystem(matchup.game_system)
    battle_plan: BattlePlan = generate_battle_plan(game_system)
    
    # Convert BattlePlan dataclass to dict for JSON storage
    matchup.battle_plan = {
        "name": battle_plan.name,
        "game_system": battle_plan.game_system.value,
        "deployment": battle_plan.deployment.value,
        "deployment_description": battle_plan.deployment_description,
        "primary_objective": battle_plan.primary_objective,
        "secondary_objectives": battle_plan.secondary_objectives,
        "victory_conditions": battle_plan.victory_conditions,
        "turn_limit": battle_plan.turn_limit,
        "special_rules": battle_plan.special_rules,
        "battle_tactics": battle_plan.battle_tactics,
    }
    
    matchup.map_name = battle_plan.name


def get_matchup_history(
    session: Session,
    user_id: int,
    limit: int = 50,
) -> list[Matchup]:
    """
    Get matchup history for a user.
    
    Args:
        session: Database session
        user_id: User ID
        limit: Maximum number of results
        
    Returns:
        List of matchups where user participated
    """
    statement = (
        select(Matchup)
        .where(
            (Matchup.player1_user_id == user_id) | (Matchup.player2_user_id == user_id)
        )
        .order_by(Matchup.created_at.desc())
        .limit(limit)
    )
    
    matchups = session.exec(statement).all()
    return list(matchups)
