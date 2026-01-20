"""Admin endpoints for user and role management."""

from app.admin.schemas import (
    ClaimApproval,
    EloSettingsResponse,
    EloSettingsUpdate,
    RoleUpdate,
    UserResponse,
)
from app.core.deps import require_role
from app.db import get_session
from app.league.elo import (
    DEFAULT_K_FACTOR,
    DEFAULT_NEW_PLAYER_GAMES,
    DEFAULT_NEW_PLAYER_K,
    get_global_k_factor,
    get_new_player_games_threshold,
    get_new_player_k_factor,
    set_setting,
)
from app.league.models import LeaguePlayer
from app.league.service import recalculate_all_army_stats
from app.users.models import User
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

router = APIRouter()

get_admin = require_role("admin")


@router.get("/users", response_model=list[UserResponse])
async def list_users(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_admin),
):
    """Lista wszystkich uzytkownikow (tylko admin)."""
    statement = select(User).order_by(User.created_at.desc())
    users = session.scalars(statement).all()

    return [
        UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            role=user.role,
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at,
        )
        for user in users
    ]


@router.patch("/users/{user_id}/role", response_model=UserResponse)
async def update_user_role(
    user_id: int,
    data: RoleUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_admin),
):
    """Zmienia role uzytkownika (tylko admin)."""
    statement = select(User).where(User.id == user_id)
    user = session.scalars(statement).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change your own role",
        )

    user.role = data.role
    session.add(user)
    session.commit()
    session.refresh(user)

    return UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        role=user.role,
        is_active=user.is_active,
        is_verified=user.is_verified,
        created_at=user.created_at,
    )


@router.post("/claim/approve")
async def approve_claim(
    data: ClaimApproval,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_admin),
):
    """Zatwierdza przejecie konta (admin)."""
    statement = select(LeaguePlayer).where(LeaguePlayer.id == data.league_player_id)
    player = session.scalars(statement).first()

    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="League player not found",
        )

    statement = select(User).where(User.id == data.user_id)
    user = session.scalars(statement).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    player.user_id = user.id
    player.is_claimed = True
    session.add(player)
    session.commit()

    return {"message": "Claim approved"}


@router.get("/stats")
async def get_admin_stats(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_admin),
):
    """Statystyki dla admina."""
    users_count = len(session.scalars(select(User)).all())
    players_count = session.scalars(select(User).where(User.role == "player")).all()
    organizers_count = session.scalars(
        select(User).where(User.role == "organizer")
    ).all()
    admins_count = session.scalars(select(User).where(User.role == "admin")).all()

    return {
        "total_users": users_count,
        "players": len(players_count),
        "organizers": len(organizers_count),
        "admins": len(admins_count),
    }


# ============ Settings ============


@router.get("/settings/elo", response_model=EloSettingsResponse)
async def get_elo_settings(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_admin),
):
    """Get ELO system settings."""
    return EloSettingsResponse(
        k_factor=get_global_k_factor(session),
        new_player_k=get_new_player_k_factor(session),
        new_player_games=get_new_player_games_threshold(session),
    )


@router.patch("/settings/elo", response_model=EloSettingsResponse)
async def update_elo_settings(
    data: EloSettingsUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_admin),
):
    """Update ELO system settings."""
    if data.k_factor is not None:
        set_setting(session, "elo_k_factor", str(data.k_factor))

    if data.new_player_k is not None:
        set_setting(session, "elo_new_player_k", str(data.new_player_k))

    if data.new_player_games is not None:
        set_setting(session, "elo_new_player_games", str(data.new_player_games))

    return EloSettingsResponse(
        k_factor=get_global_k_factor(session),
        new_player_k=get_new_player_k_factor(session),
        new_player_games=get_new_player_games_threshold(session),
    )


@router.post("/recalculate-army-stats")
async def recalculate_army_stats(
    session: Session = Depends(get_session),
    _: User = Depends(get_admin),
):
    """Recalculates all army statistics from confirmed matches. Admin only."""
    result = recalculate_all_army_stats(session)
    return {
        "message": "Army stats recalculated successfully",
        **result,
    }
