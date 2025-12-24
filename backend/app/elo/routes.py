"""
ELO Routes

API endpoints for ELO rating system.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select

from app.db import get_session
from app.elo import service
from app.elo.calculator import rating_to_rank
from app.elo.models import ELORating, ELOConfig
from app.elo.schemas import (
    ELOConfigRead,
    ELOConfigUpdate,
    ELORatingRead,
    ELORatingWithUser,
    ELOHistoryRead,
    LeaderboardEntry,
    LeaderboardResponse,
    MatchResultSubmit,
    MatchResultResponse,
    UserELOStats,
    ELOProgressChart,
)


router = APIRouter(prefix="/api/elo", tags=["elo"])


# ═══════════════════════════════════════════════
# PUBLIC ENDPOINTS
# ═══════════════════════════════════════════════


@router.get("/leaderboard/{rating_type}", response_model=LeaderboardResponse)
async def get_leaderboard(
    rating_type: str,
    session: Session = Depends(get_session),
    limit: int = Query(100, ge=1, le=500),
    min_games: int = Query(0, ge=0),
):
    """
    Get leaderboard for a rating type.
    
    - rating_type: "league", "tournament", or "global"
    - limit: Maximum number of entries (default 100)
    - min_games: Minimum games to appear (default 0)
    """
    if rating_type not in ["league", "tournament", "global"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="rating_type must be 'league', 'tournament', or 'global'"
        )
    
    ratings = service.get_leaderboard(session, rating_type, limit, min_games)
    
    # Build leaderboard entries with user data
    entries = []
    for idx, rating in enumerate(ratings, start=1):
        # Get username (TODO: optimize with join)
        from app.users.models import User
        user = session.get(User, rating.user_id)
        
        entries.append(LeaderboardEntry(
            rank=idx,
            user_id=rating.user_id,
            username=user.username if user else "Unknown",
            rating=rating.rating,
            games_played=rating.games_played,
            wins=rating.wins,
            losses=rating.losses,
            draws=rating.draws,
            win_rate=rating.win_rate(),
            current_streak=rating.current_streak,
            is_provisional=rating.is_provisional(),
            tier=rating_to_rank(rating.rating),
        ))
    
    return LeaderboardResponse(
        rating_type=rating_type,
        total_players=len(entries),
        entries=entries
    )


@router.get("/user/{user_id}", response_model=UserELOStats)
async def get_user_elo_stats(
    user_id: int,
    session: Session = Depends(get_session),
):
    """
    Get all ELO ratings for a specific user.
    """
    # Get username
    from app.users.models import User
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User not found: {user_id}"
        )
    
    # Get all ratings
    ratings_dict = service.get_user_ratings(session, user_id)
    
    def _to_rating_read(rating: Optional[ELORating]) -> Optional[ELORatingRead]:
        if not rating:
            return None
        return ELORatingRead(
            id=rating.id,
            user_id=rating.user_id,
            rating_type=rating.rating_type,
            rating=rating.rating,
            games_played=rating.games_played,
            wins=rating.wins,
            losses=rating.losses,
            draws=rating.draws,
            win_rate=rating.win_rate(),
            peak_rating=rating.peak_rating,
            peak_date=rating.peak_date,
            current_streak=rating.current_streak,
            best_win_streak=rating.best_win_streak,
            worst_loss_streak=rating.worst_loss_streak,
            is_provisional=rating.is_provisional(),
            rank=rating_to_rank(rating.rating),
            created_at=rating.created_at,
            updated_at=rating.updated_at,
        )
    
    return UserELOStats(
        user_id=user_id,
        username=user.username,
        league_rating=_to_rating_read(ratings_dict.get("league")),
        tournament_rating=_to_rating_read(ratings_dict.get("tournament")),
        global_rating=_to_rating_read(ratings_dict.get("global")),
    )


@router.get("/history/{user_id}", response_model=list[ELOHistoryRead])
async def get_user_elo_history(
    user_id: int,
    session: Session = Depends(get_session),
    rating_type: Optional[str] = None,
    limit: int = Query(50, ge=1, le=500),
):
    """
    Get ELO history for a user.
    
    - rating_type: Optional filter ("league", "tournament", "global")
    - limit: Maximum entries (default 50)
    """
    history = service.get_user_history(session, user_id, rating_type, limit)
    
    # Build response with opponent usernames
    from app.users.models import User
    
    result = []
    for entry in history:
        opponent = session.get(User, entry.opponent_id)
        result.append(ELOHistoryRead(
            id=entry.id,
            user_id=entry.user_id,
            opponent_id=entry.opponent_id,
            opponent_username=opponent.username if opponent else "Unknown",
            rating_type=entry.rating_type,
            old_rating=entry.old_rating,
            new_rating=entry.new_rating,
            rating_change=entry.rating_change,
            result=entry.result,
            k_factor=entry.k_factor,
            expected_score=entry.expected_score,
            actual_score=entry.actual_score,
            match_id=entry.match_id,
            match_type=entry.match_type,
            created_at=entry.created_at,
        ))
    
    return result


@router.get("/progress/{user_id}/{rating_type}", response_model=ELOProgressChart)
async def get_rating_progress(
    user_id: int,
    rating_type: str,
    session: Session = Depends(get_session),
    limit: int = Query(100, ge=1, le=500),
):
    """
    Get rating progress data for charting.
    
    Returns time-series data of rating changes.
    """
    if rating_type not in ["league", "tournament", "global"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="rating_type must be 'league', 'tournament', or 'global'"
        )
    
    data_points = service.get_rating_progress(session, user_id, rating_type, limit)
    
    return ELOProgressChart(
        user_id=user_id,
        rating_type=rating_type,
        data_points=data_points
    )


@router.get("/config/{rating_type}", response_model=ELOConfigRead)
async def get_elo_config(
    rating_type: str,
    session: Session = Depends(get_session),
):
    """Get ELO configuration for a rating type"""
    config = service.get_config(session, rating_type)
    return config


# ═══════════════════════════════════════════════
# PROTECTED ENDPOINTS (Organizer/Admin)
# ═══════════════════════════════════════════════


@router.post("/match/result", response_model=MatchResultResponse)
async def submit_match_result(
    request: MatchResultSubmit,
    session: Session = Depends(get_session),
    # TODO: Add authentication
    # current_user: User = Depends(current_active_user)
):
    """
    Submit a match result to update ELO ratings.
    
    TODO: Add role check (organizer or admin only)
    """
    # Validate users exist
    from app.users.models import User
    
    player1 = session.get(User, request.player1_id)
    player2 = session.get(User, request.player2_id)
    
    if not player1 or not player2:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or both players not found"
        )
    
    # Update ELO
    p1_history, p2_history = service.update_elo_after_match(
        session=session,
        player1_id=request.player1_id,
        player2_id=request.player2_id,
        result=request.result,
        rating_type=request.rating_type,
        match_id=request.match_id,
        match_type=request.match_type,
    )
    
    return MatchResultResponse(
        player1_id=request.player1_id,
        player2_id=request.player2_id,
        result=request.result,
        rating_type=request.rating_type,
        player1_old_rating=p1_history.old_rating,
        player1_new_rating=p1_history.new_rating,
        player1_change=p1_history.rating_change,
        player1_expected_score=p1_history.expected_score,
        player2_old_rating=p2_history.old_rating,
        player2_new_rating=p2_history.new_rating,
        player2_change=p2_history.rating_change,
        player2_expected_score=p2_history.expected_score,
        player1_history_id=p1_history.id,
        player2_history_id=p2_history.id,
    )


@router.patch("/config/{rating_type}", response_model=ELOConfigRead)
async def update_elo_config(
    rating_type: str,
    request: ELOConfigUpdate,
    session: Session = Depends(get_session),
    # TODO: Add authentication
    # current_user: User = Depends(require_role("admin"))
):
    """
    Update ELO configuration (admin only).
    
    TODO: Add admin role check
    """
    config = service.update_config(
        session=session,
        rating_type=rating_type,
        k_factor=request.k_factor,
        is_active=request.is_active,
        description=request.description,
    )
    
    return config
