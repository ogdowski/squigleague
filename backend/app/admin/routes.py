"""Admin endpoints for user and role management."""

from typing import Optional

from app.admin.schemas import (
    AdminMatchupResponse,
    ClaimApproval,
    EloSettingsResponse,
    EloSettingsUpdate,
    FeatureTogglesResponse,
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
    get_setting,
    set_setting,
)
from app.league.models import LeaguePlayer, PlayerElo
from app.league.service import recalculate_all_army_stats
from app.matchup.models import Matchup
from app.users.models import OAuthAccount, User
from fastapi import APIRouter, Depends, HTTPException, Query, status
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
            last_login=user.last_login,
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
        last_login=user.last_login,
    )


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_admin),
):
    """Usuwa uzytkownika (tylko admin)."""
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
            detail="Cannot delete your own account",
        )

    # Unlink league players (keep history, just remove user reference)
    league_players = session.scalars(
        select(LeaguePlayer).where(LeaguePlayer.user_id == user_id)
    ).all()
    for player in league_players:
        player.user_id = None
        player.is_claimed = False
        session.add(player)

    # Delete OAuth accounts
    oauth_accounts = session.scalars(
        select(OAuthAccount).where(OAuthAccount.user_id == user_id)
    ).all()
    for oauth in oauth_accounts:
        session.delete(oauth)

    # Delete ELO record
    elo_record = session.scalars(
        select(PlayerElo).where(PlayerElo.user_id == user_id)
    ).first()
    if elo_record:
        session.delete(elo_record)

    # Delete user
    session.delete(user)
    session.commit()

    return {"message": "User deleted successfully"}


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


@router.get("/settings/features", response_model=FeatureTogglesResponse)
async def get_feature_toggles(
    session: Session = Depends(get_session),
):
    """Get feature toggles (public, no auth required)."""
    rules_enabled = get_setting(session, "rules_enabled", "false") == "true"
    return FeatureTogglesResponse(rules_enabled=rules_enabled)


@router.patch("/settings/features", response_model=FeatureTogglesResponse)
async def update_feature_toggles(
    data: FeatureTogglesResponse,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_admin),
):
    """Update feature toggles (admin only)."""
    set_setting(session, "rules_enabled", str(data.rules_enabled).lower())
    return FeatureTogglesResponse(rules_enabled=data.rules_enabled)


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


# ============ Matchups ============


@router.get("/matchups", response_model=list[AdminMatchupResponse])
async def list_matchups(
    status_filter: Optional[str] = Query(
        None, description="Filter: pending, revealed, all"
    ),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_admin),
):
    """Lista matchupow dla admina. Listy widoczne tylko gdy ujawnione."""
    statement = select(Matchup).order_by(Matchup.created_at.desc())

    if status_filter == "pending":
        # Not yet revealed (at least one player hasn't submitted)
        statement = statement.where(
            (Matchup.player1_submitted == False) | (Matchup.player2_submitted == False)
        )
    elif status_filter == "revealed":
        # Both submitted
        statement = statement.where(
            Matchup.player1_submitted == True, Matchup.player2_submitted == True
        )

    matchups = session.scalars(statement).all()

    # Get usernames for players
    user_ids = set()
    for matchup in matchups:
        if matchup.player1_id:
            user_ids.add(matchup.player1_id)
        if matchup.player2_id:
            user_ids.add(matchup.player2_id)

    users_map = {}
    if user_ids:
        users = session.scalars(select(User).where(User.id.in_(user_ids))).all()
        users_map = {user.id: user.username for user in users}

    result = []
    for matchup in matchups:
        is_revealed = matchup.player1_submitted and matchup.player2_submitted
        result.append(
            AdminMatchupResponse(
                id=matchup.id,
                name=matchup.name,
                title=matchup.title,
                player1_id=matchup.player1_id,
                player2_id=matchup.player2_id,
                player1_username=users_map.get(matchup.player1_id),
                player2_username=users_map.get(matchup.player2_id),
                player1_submitted=matchup.player1_submitted,
                player2_submitted=matchup.player2_submitted,
                is_revealed=is_revealed,
                is_public=matchup.is_public,
                created_at=matchup.created_at,
                # Only show lists if revealed
                player1_list=matchup.player1_list if is_revealed else None,
                player2_list=matchup.player2_list if is_revealed else None,
                player1_army_faction=(
                    matchup.player1_army_faction if is_revealed else None
                ),
                player2_army_faction=(
                    matchup.player2_army_faction if is_revealed else None
                ),
                map_name=matchup.map_name if is_revealed else None,
                player1_score=matchup.player1_score,
                player2_score=matchup.player2_score,
                result_status=matchup.result_status,
            )
        )

    return result
