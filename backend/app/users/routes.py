"""
User Routes

Authentication and user management endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.db import get_session
from app.users.auth import (
    auth_backend,
    fastapi_users,
    google_oauth_client,
    discord_oauth_client,
    current_active_user,
)
from app.users.models import User
from app.users.schemas import UserRead, UserUpdate, UserProfileResponse, UserProfileStats
from app.core.permissions import require_role


# ═══════════════════════════════════════════════
# ROUTER SETUP
# ═══════════════════════════════════════════════


router = APIRouter(prefix="/api", tags=["users"])


# ═══════════════════════════════════════════════
# FASTAPI USERS ROUTES
# ═══════════════════════════════════════════════


# Auth routes (login, logout, etc.)
router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

# User management routes (me, update profile)
router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)

# Google OAuth
router.include_router(
    fastapi_users.get_oauth_router(
        google_oauth_client,
        auth_backend,
        settings.SECRET_KEY,
        redirect_url=f"{settings.FRONTEND_URL}/auth/callback/google",
        associate_by_email=True,
    ),
    prefix="/auth/google",
    tags=["auth"],
)

# Discord OAuth
router.include_router(
    fastapi_users.get_oauth_router(
        discord_oauth_client,
        auth_backend,
        settings.SECRET_KEY,
        redirect_url=f"{settings.FRONTEND_URL}/auth/callback/discord",
        associate_by_email=True,
    ),
    prefix="/auth/discord",
    tags=["auth"],
)


# ═══════════════════════════════════════════════
# CUSTOM USER ROUTES
# ═══════════════════════════════════════════════


@router.get("/users/me/profile", response_model=UserProfileResponse)
async def get_my_profile(
    current_user: User = Depends(current_active_user),
    session: Session = Depends(get_session),
):
    """
    Get current user's profile with statistics.
    
    TODO: Add ELO stats once ELO module is implemented.
    """
    # Basic stats (placeholder until modules are implemented)
    stats = UserProfileStats(
        total_matchups=0,
        league_elo=1000,
        tournament_elo=1000,
        global_elo=1000,
        total_games=0,
        wins=0,
        losses=0,
        draws=0,
    )
    
    return UserProfileResponse(
        user=UserRead.model_validate(current_user),
        stats=stats,
    )


@router.get("/users/{user_id}/profile", response_model=UserProfileResponse)
async def get_user_profile(
    user_id: int,
    session: Session = Depends(get_session),
):
    """
    Get any user's public profile with statistics.
    Public endpoint - no authentication required.
    """
    # Get user
    statement = select(User).where(User.id == user_id)
    user = session.exec(statement).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Basic stats (placeholder)
    stats = UserProfileStats(
        total_matchups=0,
        league_elo=1000,
        tournament_elo=1000,
        global_elo=1000,
        total_games=0,
        wins=0,
        losses=0,
        draws=0,
    )
    
    return UserProfileResponse(
        user=UserRead.model_validate(user),
        stats=stats,
    )


# ═══════════════════════════════════════════════
# ADMIN ROUTES
# ═══════════════════════════════════════════════


@router.get("/admin/users", tags=["admin"])
async def list_users(
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role("admin")),
    skip: int = 0,
    limit: int = 100,
):
    """
    List all users (admin only).
    """
    statement = select(User).offset(skip).limit(limit)
    users = session.exec(statement).all()
    
    return {
        "users": [UserRead.model_validate(user) for user in users],
        "total": len(users),
        "skip": skip,
        "limit": limit,
    }


@router.patch("/admin/users/{user_id}/role", tags=["admin"])
async def update_user_role(
    user_id: int,
    new_role: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role("admin")),
):
    """
    Update user role (admin only).
    
    Allowed roles: player, organizer, admin
    """
    if new_role not in ["player", "organizer", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role. Must be: player, organizer, or admin"
        )
    
    # Get user
    statement = select(User).where(User.id == user_id)
    user = session.exec(statement).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update role
    user.role = new_role
    session.add(user)
    session.commit()
    session.refresh(user)
    
    return {
        "message": f"User role updated to {new_role}",
        "user": UserRead.model_validate(user),
    }


# Import settings for OAuth redirect URLs
from app.config import settings
