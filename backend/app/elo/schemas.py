"""
ELO Schemas

Pydantic models for ELO API requests and responses.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# ═══════════════════════════════════════════════
# CONFIG SCHEMAS
# ═══════════════════════════════════════════════


class ELOConfigRead(BaseModel):
    """ELO config response"""
    id: int
    name: str
    k_factor: int
    is_active: bool
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ELOConfigUpdate(BaseModel):
    """Update ELO config (admin only)"""
    k_factor: Optional[int] = Field(None, ge=10, le=100)
    is_active: Optional[bool] = None
    description: Optional[str] = None


# ═══════════════════════════════════════════════
# RATING SCHEMAS
# ═══════════════════════════════════════════════


class ELORatingRead(BaseModel):
    """Current ELO rating response"""
    id: int
    user_id: int
    rating_type: str
    rating: int
    games_played: int
    wins: int
    losses: int
    draws: int
    win_rate: float
    peak_rating: int
    peak_date: Optional[datetime] = None
    current_streak: int
    best_win_streak: int
    worst_loss_streak: int
    is_provisional: bool
    rank: str  # "Grandmaster", "Master", etc.
    created_at: datetime
    updated_at: datetime


class ELORatingWithUser(BaseModel):
    """ELO rating with user details (for leaderboards)"""
    id: int
    user_id: int
    username: str  # Joined from User
    rating_type: str
    rating: int
    games_played: int
    wins: int
    losses: int
    draws: int
    win_rate: float
    peak_rating: int
    current_streak: int
    is_provisional: bool
    rank: str


# ═══════════════════════════════════════════════
# HISTORY SCHEMAS
# ═══════════════════════════════════════════════


class ELOHistoryRead(BaseModel):
    """ELO history entry response"""
    id: int
    user_id: int
    opponent_id: int
    opponent_username: str  # Joined from User
    rating_type: str
    old_rating: int
    new_rating: int
    rating_change: int
    result: str
    k_factor: int
    expected_score: float
    actual_score: float
    match_id: Optional[int] = None
    match_type: Optional[str] = None
    created_at: datetime


# ═══════════════════════════════════════════════
# LEADERBOARD SCHEMAS
# ═══════════════════════════════════════════════


class LeaderboardEntry(BaseModel):
    """Single entry in leaderboard"""
    rank: int  # Position in leaderboard (1, 2, 3, ...)
    user_id: int
    username: str
    rating: int
    games_played: int
    wins: int
    losses: int
    draws: int
    win_rate: float
    current_streak: int
    is_provisional: bool
    tier: str  # "Grandmaster", "Master", etc.


class LeaderboardResponse(BaseModel):
    """Leaderboard response"""
    rating_type: str
    total_players: int
    entries: list[LeaderboardEntry]


# ═══════════════════════════════════════════════
# MATCH RESULT SCHEMAS
# ═══════════════════════════════════════════════


class MatchResultSubmit(BaseModel):
    """Submit a match result to update ELO"""
    player1_id: int
    player2_id: int
    result: str = Field(..., pattern="^(player1_win|player2_win|draw)$")
    rating_type: str = Field(..., pattern="^(league|tournament|global)$")
    match_id: Optional[int] = None
    match_type: Optional[str] = None


class MatchResultResponse(BaseModel):
    """Response after submitting match result"""
    player1_id: int
    player2_id: int
    result: str
    rating_type: str
    
    # Player 1 changes
    player1_old_rating: int
    player1_new_rating: int
    player1_change: int
    player1_expected_score: float
    
    # Player 2 changes
    player2_old_rating: int
    player2_new_rating: int
    player2_change: int
    player2_expected_score: float
    
    # History IDs
    player1_history_id: int
    player2_history_id: int


# ═══════════════════════════════════════════════
# STATS SCHEMAS
# ═══════════════════════════════════════════════


class UserELOStats(BaseModel):
    """All ELO ratings for a user"""
    user_id: int
    username: str
    league_rating: Optional[ELORatingRead] = None
    tournament_rating: Optional[ELORatingRead] = None
    global_rating: Optional[ELORatingRead] = None


class ELOProgressChart(BaseModel):
    """Data for rating progress chart"""
    user_id: int
    rating_type: str
    data_points: list[dict]  # [{date, rating}, ...]
