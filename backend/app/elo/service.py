"""
ELO Service

Business logic for ELO rating management.
"""

from datetime import datetime, timezone
from typing import Optional, Tuple
from sqlmodel import Session, select, and_
from fastapi import HTTPException, status

from app.elo.models import ELOConfig, ELORating, ELOHistory
from app.elo.calculator import calculate_elo_change, rating_to_rank


# ═══════════════════════════════════════════════
# CONFIG MANAGEMENT
# ═══════════════════════════════════════════════


def get_config(session: Session, rating_type: str) -> ELOConfig:
    """Get ELO config for a rating type"""
    config = session.exec(
        select(ELOConfig).where(ELOConfig.name == rating_type)
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ELO config not found for rating type: {rating_type}"
        )
    
    return config


def update_config(
    session: Session,
    rating_type: str,
    k_factor: Optional[int] = None,
    is_active: Optional[bool] = None,
    description: Optional[str] = None
) -> ELOConfig:
    """Update ELO config (admin only)"""
    config = get_config(session, rating_type)
    
    if k_factor is not None:
        config.k_factor = k_factor
    if is_active is not None:
        config.is_active = is_active
    if description is not None:
        config.description = description
    
    session.add(config)
    session.commit()
    session.refresh(config)
    
    return config


# ═══════════════════════════════════════════════
# RATING MANAGEMENT
# ═══════════════════════════════════════════════


def get_or_create_rating(
    session: Session,
    user_id: int,
    rating_type: str
) -> ELORating:
    """Get existing rating or create new one at 1000"""
    rating = session.exec(
        select(ELORating).where(
            and_(
                ELORating.user_id == user_id,
                ELORating.rating_type == rating_type
            )
        )
    ).first()
    
    if not rating:
        rating = ELORating(
            user_id=user_id,
            rating_type=rating_type,
            rating=1000,
            peak_rating=1000
        )
        session.add(rating)
        session.commit()
        session.refresh(rating)
    
    return rating


def get_user_ratings(session: Session, user_id: int) -> dict[str, ELORating]:
    """Get all ratings for a user"""
    ratings = session.exec(
        select(ELORating).where(ELORating.user_id == user_id)
    ).all()
    
    return {r.rating_type: r for r in ratings}


def get_leaderboard(
    session: Session,
    rating_type: str,
    limit: int = 100,
    min_games: int = 0
) -> list[ELORating]:
    """
    Get leaderboard for a rating type.
    
    Args:
        session: Database session
        rating_type: "league", "tournament", or "global"
        limit: Maximum number of entries
        min_games: Minimum games played to appear on leaderboard
    
    Returns:
        List of ELORating entries, ordered by rating descending
    """
    query = select(ELORating).where(
        and_(
            ELORating.rating_type == rating_type,
            ELORating.games_played >= min_games
        )
    ).order_by(ELORating.rating.desc()).limit(limit)
    
    return list(session.exec(query).all())


# ═══════════════════════════════════════════════
# MATCH RESULT PROCESSING
# ═══════════════════════════════════════════════


def update_elo_after_match(
    session: Session,
    player1_id: int,
    player2_id: int,
    result: str,
    rating_type: str,
    match_id: Optional[int] = None,
    match_type: Optional[str] = None
) -> Tuple[ELOHistory, ELOHistory]:
    """
    Update ELO ratings after a match.
    
    Args:
        session: Database session
        player1_id: ID of player 1
        player2_id: ID of player 2
        result: "player1_win", "player2_win", or "draw"
        rating_type: "league", "tournament", or "global"
        match_id: Optional FK to match record
        match_type: Optional match type for reference
    
    Returns:
        Tuple of (player1_history, player2_history)
    """
    # Validate config exists and is active
    config = get_config(session, rating_type)
    if not config.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"ELO rating type '{rating_type}' is not active"
        )
    
    # Get or create ratings
    player1_rating = get_or_create_rating(session, player1_id, rating_type)
    player2_rating = get_or_create_rating(session, player2_id, rating_type)
    
    # Calculate new ratings
    new_p1_rating, new_p2_rating, details = calculate_elo_change(
        player1_rating.rating,
        player2_rating.rating,
        player1_rating.games_played,
        player2_rating.games_played,
        result,
        config.k_factor
    )
    
    # Update player 1 rating
    player1_history = _update_player_rating(
        session,
        player1_rating,
        new_p1_rating,
        details["player1_change"],
        details["player1_expected"],
        details["player1_actual"],
        details["player1_k"],
        player2_id,
        _result_for_player(result, 1),
        rating_type,
        match_id,
        match_type
    )
    
    # Update player 2 rating
    player2_history = _update_player_rating(
        session,
        player2_rating,
        new_p2_rating,
        details["player2_change"],
        details["player2_expected"],
        details["player2_actual"],
        details["player2_k"],
        player1_id,
        _result_for_player(result, 2),
        rating_type,
        match_id,
        match_type
    )
    
    session.commit()
    
    return player1_history, player2_history


def _result_for_player(result: str, player_number: int) -> str:
    """Convert match result to individual player result"""
    if result == "draw":
        return "draw"
    elif result == f"player{player_number}_win":
        return "win"
    else:
        return "loss"


def _update_player_rating(
    session: Session,
    rating: ELORating,
    new_rating: int,
    rating_change: int,
    expected_score: float,
    actual_score: float,
    k_factor: int,
    opponent_id: int,
    result: str,
    rating_type: str,
    match_id: Optional[int],
    match_type: Optional[str]
) -> ELOHistory:
    """Update a single player's rating and create history entry"""
    old_rating = rating.rating
    
    # Update rating
    rating.rating = new_rating
    rating.games_played += 1
    
    # Update win/loss/draw counts
    if result == "win":
        rating.wins += 1
        rating.current_streak = max(1, rating.current_streak + 1)
        rating.best_win_streak = max(rating.best_win_streak, rating.current_streak)
    elif result == "loss":
        rating.losses += 1
        rating.current_streak = min(-1, rating.current_streak - 1)
        rating.worst_loss_streak = min(rating.worst_loss_streak, rating.current_streak)
    else:  # draw
        rating.draws += 1
        rating.current_streak = 0
    
    # Update peak rating
    if new_rating > rating.peak_rating:
        rating.peak_rating = new_rating
        rating.peak_date = datetime.now(timezone.utc)
    
    session.add(rating)
    
    # Create history entry
    history = ELOHistory(
        user_id=rating.user_id,
        opponent_id=opponent_id,
        rating_type=rating_type,
        old_rating=old_rating,
        new_rating=new_rating,
        rating_change=rating_change,
        result=result,
        k_factor=k_factor,
        expected_score=expected_score,
        actual_score=actual_score,
        match_id=match_id,
        match_type=match_type
    )
    session.add(history)
    
    return history


# ═══════════════════════════════════════════════
# HISTORY QUERIES
# ═══════════════════════════════════════════════


def get_user_history(
    session: Session,
    user_id: int,
    rating_type: Optional[str] = None,
    limit: int = 50
) -> list[ELOHistory]:
    """Get ELO history for a user"""
    query = select(ELOHistory).where(ELOHistory.user_id == user_id)
    
    if rating_type:
        query = query.where(ELOHistory.rating_type == rating_type)
    
    query = query.order_by(ELOHistory.created_at.desc()).limit(limit)
    
    return list(session.exec(query).all())


def get_rating_progress(
    session: Session,
    user_id: int,
    rating_type: str,
    limit: int = 100
) -> list[dict]:
    """
    Get rating progress data points for charting.
    
    Returns list of {date, rating} dicts.
    """
    history = session.exec(
        select(ELOHistory)
        .where(
            and_(
                ELOHistory.user_id == user_id,
                ELOHistory.rating_type == rating_type
            )
        )
        .order_by(ELOHistory.created_at.asc())
        .limit(limit)
    ).all()
    
    return [
        {
            "date": entry.created_at.isoformat(),
            "rating": entry.new_rating
        }
        for entry in history
    ]


# ═══════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════


def seed_default_configs(session: Session) -> None:
    """Create default ELO configs if they don't exist"""
    default_configs = [
        {
            "name": "league",
            "k_factor": 50,
            "description": "League match ELO ratings"
        },
        {
            "name": "tournament",
            "k_factor": 50,
            "description": "Tournament match ELO ratings"
        },
        {
            "name": "global",
            "k_factor": 50,
            "description": "Global ELO rating across all matches"
        }
    ]
    
    for config_data in default_configs:
        existing = session.exec(
            select(ELOConfig).where(ELOConfig.name == config_data["name"])
        ).first()
        
        if not existing:
            config = ELOConfig(**config_data)
            session.add(config)
    
    session.commit()
