from datetime import datetime

from app.core.deps import get_current_user, get_current_user_optional
from app.db import get_session
from app.league.constants import BATTLE_PLAN_DATA, MAP_IMAGES, MISSION_MAPS
from app.league.models import League
from app.matchup.models import Matchup
from app.matchup.schemas import (
    MatchupCreate,
    MatchupCreateResponse,
    MatchupPublicToggle,
    MatchupReveal,
    MatchupStatus,
    MatchupSubmit,
)
from app.matchup.service import get_battle_plan_data, get_map_image, submit_list
from app.users.models import User
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlmodel import Session, func, select

router = APIRouter()


@router.post(
    "", response_model=MatchupCreateResponse, status_code=status.HTTP_201_CREATED
)
async def create_matchup(
    data: MatchupCreate,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user_optional),
):
    """Create a new matchup with Player 1's army list and return the UUID link."""
    # Look up player2 by username if provided
    player2_id = None
    if data.player2_username:
        statement = select(User).where(User.username == data.player2_username)
        player2 = session.scalars(statement).first()
        if player2:
            player2_id = player2.id

    matchup = Matchup(
        player1_id=current_user.id if current_user else None,
        player2_id=player2_id,
        player1_list=data.army_list,
        player1_submitted=True,
        is_public=data.is_public,
    )

    session.add(matchup)
    session.commit()
    session.refresh(matchup)

    return MatchupCreateResponse(
        name=matchup.name,
        link=f"/matchup/{matchup.name}",
        expires_at=matchup.expires_at,
    )


@router.get("/my-matchups", response_model=list[MatchupStatus])
async def get_my_matchups(
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """Get all matchups for the current user."""
    statement = (
        select(Matchup, User)
        .outerjoin(User, Matchup.player1_id == User.id)
        .where(
            or_(
                Matchup.player1_id == current_user.id,
                Matchup.player2_id == current_user.id,
            )
        )
        .order_by(Matchup.created_at.desc())
    )

    results = session.scalars(
        select(Matchup)
        .where(
            or_(
                Matchup.player1_id == current_user.id,
                Matchup.player2_id == current_user.id,
            )
        )
        .order_by(Matchup.created_at.desc())
    ).all()

    # Fetch player info separately
    matchup_list = []
    for matchup in results:
        player1 = session.get(User, matchup.player1_id) if matchup.player1_id else None
        player2 = session.get(User, matchup.player2_id) if matchup.player2_id else None

        matchup_list.append(
            MatchupStatus(
                name=matchup.name,
                player1_submitted=matchup.player1_submitted,
                player2_submitted=matchup.player2_submitted,
                is_revealed=matchup.is_revealed,
                is_public=matchup.is_public,
                created_at=matchup.created_at,
                expires_at=matchup.expires_at,
                player1_username=player1.username if player1 else None,
                player2_username=player2.username if player2 else None,
                player1_avatar=player1.avatar_url if player1 else None,
                player2_avatar=player2.avatar_url if player2 else None,
            )
        )

    return matchup_list


@router.get("/public", response_model=list[MatchupStatus])
async def get_public_matchups(
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user_optional),
    limit: int = Query(default=50, le=100),
):
    """Get public completed matchups from other users."""
    now = datetime.utcnow()

    # Base query: public, revealed, not expired
    statement = (
        select(Matchup)
        .where(
            Matchup.is_public.is_(True),
            Matchup.player1_submitted.is_(True),
            Matchup.player2_submitted.is_(True),
            Matchup.expires_at > now,
        )
        .order_by(Matchup.revealed_at.desc())
        .limit(limit)
    )

    results = session.scalars(statement).all()

    matchup_list = []
    for matchup in results:
        player1 = session.get(User, matchup.player1_id) if matchup.player1_id else None
        player2 = session.get(User, matchup.player2_id) if matchup.player2_id else None

        matchup_list.append(
            MatchupStatus(
                name=matchup.name,
                player1_submitted=matchup.player1_submitted,
                player2_submitted=matchup.player2_submitted,
                is_revealed=matchup.is_revealed,
                is_public=matchup.is_public,
                created_at=matchup.created_at,
                expires_at=matchup.expires_at,
                player1_username=player1.username if player1 else None,
                player2_username=player2.username if player2 else None,
                player1_avatar=player1.avatar_url if player1 else None,
                player2_avatar=player2.avatar_url if player2 else None,
            )
        )

    return matchup_list


@router.get("/search-users")
async def search_users(
    q: str = Query(min_length=2),
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """Search for users by username for matchup assignment."""
    statement = (
        select(User)
        .where(
            User.username.ilike(f"%{q}%"),
            User.id != current_user.id,  # Exclude self
        )
        .limit(10)
    )

    users = session.scalars(statement).all()

    return [
        {
            "id": user.id,
            "username": user.username,
            "avatar_url": user.avatar_url,
        }
        for user in users
    ]


@router.get("/maps")
async def get_maps():
    """Get available mission maps with their battle plan data."""
    return {
        "maps": MISSION_MAPS,
        "battle_plans": BATTLE_PLAN_DATA,
        "images": MAP_IMAGES,
    }


@router.get("/maps/{map_name}")
async def get_map_details(map_name: str):
    """Get battle plan details for a specific map."""
    if map_name not in MISSION_MAPS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Map not found",
        )
    return {
        "name": map_name,
        "image": MAP_IMAGES.get(map_name),
        "battle_plan": BATTLE_PLAN_DATA.get(map_name),
    }


@router.get("/stats")
async def get_stats(session: Session = Depends(get_session)):
    """Get platform statistics."""
    # Count completed matchups (both lists submitted)
    completed_statement = select(func.count(Matchup.id)).where(
        Matchup.player1_submitted.is_(True),
        Matchup.player2_submitted.is_(True),
    )
    completed_count = session.execute(completed_statement).scalar_one()

    # Count expired matchups
    now = datetime.utcnow()
    expired_statement = select(func.count(Matchup.id)).where(Matchup.expires_at < now)
    expired_count = session.execute(expired_statement).scalar_one()

    # Count leagues created
    leagues_statement = select(func.count(League.id))
    leagues_count = session.execute(leagues_statement).scalar_one()

    return {
        "exchanges_completed": completed_count,
        "exchanges_expired": expired_count,
        "leagues_created": leagues_count,
        "version": "0.3.2",
    }


@router.get("/{matchup_name}", response_model=MatchupStatus)
async def get_matchup_status(
    matchup_name: str,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user_optional),
):
    """Get matchup status (without revealing lists)."""
    statement = select(Matchup).where(Matchup.name == matchup_name)
    matchup = session.scalars(statement).first()

    if not matchup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Matchup not found",
        )

    if matchup.is_expired:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Matchup has expired",
        )

    # Fetch player info if they exist
    player1 = session.get(User, matchup.player1_id) if matchup.player1_id else None
    player2 = session.get(User, matchup.player2_id) if matchup.player2_id else None

    # Check if current user is a participant
    is_participant = False
    if current_user:
        is_participant = (
            matchup.player1_id == current_user.id
            or matchup.player2_id == current_user.id
        )

    return MatchupStatus(
        name=matchup.name,
        player1_submitted=matchup.player1_submitted,
        player2_submitted=matchup.player2_submitted,
        is_revealed=matchup.is_revealed,
        is_public=matchup.is_public,
        created_at=matchup.created_at,
        expires_at=matchup.expires_at,
        player1_username=player1.username if player1 else None,
        player2_username=player2.username if player2 else None,
        player1_avatar=player1.avatar_url if player1 else None,
        player2_avatar=player2.avatar_url if player2 else None,
    )


@router.patch("/{matchup_name}/public")
async def toggle_matchup_public(
    matchup_name: str,
    data: MatchupPublicToggle,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """Toggle matchup public visibility. Only participants can do this."""
    statement = select(Matchup).where(Matchup.name == matchup_name)
    matchup = session.scalars(statement).first()

    if not matchup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Matchup not found",
        )

    # Check if user is a participant
    if matchup.player1_id != current_user.id and matchup.player2_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only participants can change matchup visibility",
        )

    matchup.is_public = data.is_public
    session.add(matchup)
    session.commit()

    return {"message": "Visibility updated", "is_public": matchup.is_public}


@router.post("/{matchup_name}/submit")
async def submit_army_list(
    matchup_name: str,
    submission: MatchupSubmit,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user_optional),
):
    """Submit an army list to a matchup."""
    statement = select(Matchup).where(Matchup.name == matchup_name)
    matchup = session.scalars(statement).first()

    if not matchup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Matchup not found",
        )

    if matchup.is_expired:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Matchup has expired",
        )

    # Determine if this is player1 or player2
    is_player1 = False
    if current_user and matchup.player1_id == current_user.id:
        is_player1 = True
    elif not matchup.player1_submitted:
        is_player1 = True

    try:
        matchup = submit_list(
            matchup,
            submission.army_list,
            is_player1,
            session,
            user_id=current_user.id if current_user else None,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    return {
        "message": "List submitted successfully",
        "is_revealed": matchup.is_revealed,
    }


@router.get("/{matchup_name}/reveal", response_model=MatchupReveal)
async def reveal_matchup(
    matchup_name: str,
    session: Session = Depends(get_session),
):
    """Reveal both army lists and the assigned map."""
    statement = select(Matchup).where(Matchup.name == matchup_name)
    matchup = session.scalars(statement).first()

    if not matchup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Matchup not found",
        )

    if not matchup.is_revealed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Both players must submit their lists before revealing",
        )

    # Fetch player info if they exist
    player1 = session.get(User, matchup.player1_id) if matchup.player1_id else None
    player2 = session.get(User, matchup.player2_id) if matchup.player2_id else None

    # Get battle plan data
    battle_plan = get_battle_plan_data(matchup.map_name) if matchup.map_name else None

    return MatchupReveal(
        name=matchup.name,
        player1_list=matchup.player1_list,
        player2_list=matchup.player2_list,
        map_name=matchup.map_name,
        map_image=get_map_image(matchup.map_name) if matchup.map_name else None,
        deployment=battle_plan.get("deployment") if battle_plan else None,
        objectives=battle_plan.get("objectives") if battle_plan else None,
        scoring=battle_plan.get("scoring") if battle_plan else None,
        underdog_ability=battle_plan.get("underdog_ability") if battle_plan else None,
        objective_types=battle_plan.get("objective_types") if battle_plan else None,
        revealed_at=matchup.revealed_at,
        player1_username=player1.username if player1 else None,
        player2_username=player2.username if player2 else None,
        player1_avatar=player1.avatar_url if player1 else None,
        player2_avatar=player2.avatar_url if player2 else None,
    )
