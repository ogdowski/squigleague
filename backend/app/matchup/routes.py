from datetime import datetime

from app.core.deps import get_current_user, get_current_user_optional
from app.data import BATTLE_PLAN_DATA, MAP_IMAGES, MISSION_MAPS, detect_army_faction
from app.db import get_session
from app.league.models import League
from app.matchup.models import Matchup
from app.matchup.schemas import (
    MatchupCreate,
    MatchupCreateResponse,
    MatchupPublicToggle,
    MatchupReveal,
    MatchupStatus,
    MatchupSubmit,
    ResultResponse,
    ResultSubmit,
)
from app.matchup.service import (
    confirm_result,
    edit_result,
    get_army_factions,
    get_battle_plan_data,
    get_map_image,
    get_result_info_message,
    submit_list,
    submit_result,
)
from app.users.models import User
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlmodel import Session, func, select

router = APIRouter()


@router.get("/armies")
async def get_armies():
    """Get list of available army factions."""
    return {"armies": get_army_factions()}


@router.post(
    "", response_model=MatchupCreateResponse, status_code=status.HTTP_201_CREATED
)
async def create_matchup(
    data: MatchupCreate,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user_optional),
):
    """Create a new matchup with Player 1's army list and return the UUID link."""
    # Detect army faction if not provided
    army_faction = data.army_faction
    if not army_faction:
        army_faction = detect_army_faction(data.army_list)

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
        title=data.title,
        player1_list=data.army_list,
        player1_army_faction=army_faction,
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


def _build_matchup_list(
    session: Session, matchups: list, current_user_id: int | None
) -> list[MatchupStatus]:
    """Helper to build matchup status list with bulk user fetching."""
    if not matchups:
        return []

    # Collect all user IDs
    user_ids = set()
    for matchup in matchups:
        if matchup.player1_id:
            user_ids.add(matchup.player1_id)
        if matchup.player2_id:
            user_ids.add(matchup.player2_id)

    # Bulk fetch users (1 query instead of 2N)
    users = (
        session.scalars(select(User).where(User.id.in_(user_ids))).all()
        if user_ids
        else []
    )
    user_map = {u.id: u for u in users}

    matchup_list = []
    for matchup in matchups:
        player1 = user_map.get(matchup.player1_id)
        player2 = user_map.get(matchup.player2_id)

        matchup_list.append(
            MatchupStatus(
                name=matchup.name,
                title=matchup.title,
                player1_submitted=matchup.player1_submitted,
                player2_submitted=matchup.player2_submitted,
                is_revealed=matchup.is_revealed,
                is_public=matchup.is_public,
                created_at=matchup.created_at,
                expires_at=matchup.expires_at,
                player1_id=matchup.player1_id,
                player2_id=matchup.player2_id,
                player1_username=player1.username if player1 else None,
                player2_username=player2.username if player2 else None,
                player1_avatar=player1.avatar_url if player1 else None,
                player2_avatar=player2.avatar_url if player2 else None,
                player1_army_faction=matchup.player1_army_faction,
                player2_army_faction=matchup.player2_army_faction,
                player1_score=matchup.player1_score,
                player2_score=matchup.player2_score,
                result_status=matchup.result_status,
                result_submitted_by_id=matchup.result_submitted_by_id,
                result_auto_confirm_at=matchup.result_auto_confirm_at,
                can_submit_result=matchup.can_submit_result(current_user_id),
                can_confirm_result=matchup.can_confirm_result(current_user_id),
                result_info_message=get_result_info_message(matchup, current_user_id),
            )
        )

    return matchup_list


@router.get("/my-matchups", response_model=list[MatchupStatus])
async def get_my_matchups(
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """Get all matchups for the current user."""
    results = list(
        session.scalars(
            select(Matchup)
            .where(
                or_(
                    Matchup.player1_id == current_user.id,
                    Matchup.player2_id == current_user.id,
                )
            )
            .order_by(Matchup.created_at.desc())
        ).all()
    )

    return _build_matchup_list(session, results, current_user.id)


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

    results = list(session.scalars(statement).all())
    current_user_id = current_user.id if current_user else None

    return _build_matchup_list(session, results, current_user_id)


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
        "version": "0.4.15",
    }


@router.get("/{matchup_name}", response_model=MatchupStatus)
async def get_matchup_status(
    matchup_name: str,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user_optional),
):
    """Get matchup status (without revealing lists)."""
    matchup = session.scalars(
        select(Matchup).where(Matchup.name == matchup_name)
    ).first()

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

    current_user_id = current_user.id if current_user else None

    return MatchupStatus(
        name=matchup.name,
        title=matchup.title,
        player1_submitted=matchup.player1_submitted,
        player2_submitted=matchup.player2_submitted,
        is_revealed=matchup.is_revealed,
        is_public=matchup.is_public,
        created_at=matchup.created_at,
        expires_at=matchup.expires_at,
        player1_id=matchup.player1_id,
        player2_id=matchup.player2_id,
        player1_username=player1.username if player1 else None,
        player2_username=player2.username if player2 else None,
        player1_avatar=player1.avatar_url if player1 else None,
        player2_avatar=player2.avatar_url if player2 else None,
        player1_army_faction=matchup.player1_army_faction,
        player2_army_faction=matchup.player2_army_faction,
        player1_score=matchup.player1_score,
        player2_score=matchup.player2_score,
        result_status=matchup.result_status,
        result_submitted_by_id=matchup.result_submitted_by_id,
        result_auto_confirm_at=matchup.result_auto_confirm_at,
        can_submit_result=matchup.can_submit_result(current_user_id),
        can_confirm_result=matchup.can_confirm_result(current_user_id),
        result_info_message=get_result_info_message(matchup, current_user_id),
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
    matchup = session.scalars(
        select(Matchup).where(Matchup.name == matchup_name)
    ).first()

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
            army_faction=submission.army_faction,
        )
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err),
        )

    return {
        "message": "List submitted successfully",
        "is_revealed": matchup.is_revealed,
        "army_faction": (
            matchup.player1_army_faction if is_player1 else matchup.player2_army_faction
        ),
    }


@router.get("/{matchup_name}/reveal", response_model=MatchupReveal)
async def reveal_matchup_endpoint(
    matchup_name: str,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user_optional),
):
    """Reveal both army lists and the assigned map."""
    matchup = session.scalars(
        select(Matchup).where(Matchup.name == matchup_name)
    ).first()

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

    current_user_id = current_user.id if current_user else None

    return MatchupReveal(
        name=matchup.name,
        title=matchup.title,
        player1_list=matchup.player1_list,
        player2_list=matchup.player2_list,
        player1_army_faction=matchup.player1_army_faction,
        player2_army_faction=matchup.player2_army_faction,
        map_name=matchup.map_name,
        map_image=get_map_image(matchup.map_name) if matchup.map_name else None,
        deployment=battle_plan.get("deployment") if battle_plan else None,
        objectives=battle_plan.get("objectives") if battle_plan else None,
        scoring=battle_plan.get("scoring") if battle_plan else None,
        underdog_ability=battle_plan.get("underdog_ability") if battle_plan else None,
        objective_types=battle_plan.get("objective_types") if battle_plan else None,
        revealed_at=matchup.revealed_at,
        player1_id=matchup.player1_id,
        player2_id=matchup.player2_id,
        player1_username=player1.username if player1 else None,
        player2_username=player2.username if player2 else None,
        player1_avatar=player1.avatar_url if player1 else None,
        player2_avatar=player2.avatar_url if player2 else None,
        player1_score=matchup.player1_score,
        player2_score=matchup.player2_score,
        result_status=matchup.result_status,
        result_submitted_by_id=matchup.result_submitted_by_id,
        result_confirmed_at=matchup.result_confirmed_at,
        result_auto_confirm_at=matchup.result_auto_confirm_at,
        can_submit_result=matchup.can_submit_result(current_user_id),
        can_confirm_result=matchup.can_confirm_result(current_user_id),
        result_info_message=get_result_info_message(matchup, current_user_id),
    )


@router.post("/{matchup_name}/result", response_model=ResultResponse)
async def submit_matchup_result(
    matchup_name: str,
    result_data: ResultSubmit,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """Submit a match result. Requires authentication."""
    matchup = session.scalars(
        select(Matchup).where(Matchup.name == matchup_name)
    ).first()

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

    try:
        matchup = submit_result(
            matchup,
            result_data.player1_score,
            result_data.player2_score,
            current_user.id,
            session,
        )
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err),
        )

    if matchup.result_status == "confirmed":
        message = "Result submitted and confirmed (opponent not registered)."
    else:
        message = "Result submitted. Waiting for opponent confirmation."

    return ResultResponse(
        message=message,
        result_status=matchup.result_status,
        player1_score=matchup.player1_score,
        player2_score=matchup.player2_score,
        auto_confirm_at=matchup.result_auto_confirm_at,
    )


@router.post("/{matchup_name}/result/confirm", response_model=ResultResponse)
async def confirm_matchup_result(
    matchup_name: str,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """Confirm a pending match result. Requires authentication."""
    matchup = session.scalars(
        select(Matchup).where(Matchup.name == matchup_name)
    ).first()

    if not matchup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Matchup not found",
        )

    try:
        matchup = confirm_result(matchup, current_user.id, session)
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err),
        )

    return ResultResponse(
        message="Result confirmed.",
        result_status=matchup.result_status,
        player1_score=matchup.player1_score,
        player2_score=matchup.player2_score,
        auto_confirm_at=None,
    )


@router.post("/{matchup_name}/result/edit", response_model=ResultResponse)
async def edit_matchup_result(
    matchup_name: str,
    result_data: ResultSubmit,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """Edit a pending match result. The original submitter will need to confirm."""
    matchup = session.scalars(
        select(Matchup).where(Matchup.name == matchup_name)
    ).first()

    if not matchup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Matchup not found",
        )

    try:
        matchup = edit_result(
            matchup,
            result_data.player1_score,
            result_data.player2_score,
            current_user.id,
            session,
        )
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err),
        )

    return ResultResponse(
        message="Result edited. Waiting for opponent to confirm.",
        result_status=matchup.result_status,
        player1_score=matchup.player1_score,
        player2_score=matchup.player2_score,
        auto_confirm_at=matchup.result_auto_confirm_at,
    )
