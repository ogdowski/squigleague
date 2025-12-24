"""
ELO Models

Database models for ELO rating system.
"""

from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel, Column, Integer, String, DateTime
from sqlalchemy.sql import func


class ELOConfig(SQLModel, table=True):
    """
    ELO Configuration for different rating types.
    
    Allows admins to configure K-factor for each rating context.
    """
    __tablename__ = "elo_configs"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)  # "league", "tournament", "global"
    k_factor: int = Field(default=50)
    is_active: bool = Field(default=True)
    description: Optional[str] = None
    
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    )


class ELORating(SQLModel, table=True):
    """
    Current ELO rating for a user in a specific context.
    
    Tracks overall stats and peak performance.
    """
    __tablename__ = "elo_ratings"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    rating_type: str = Field(index=True)  # "league", "tournament", "global"
    
    # Current rating
    rating: int = Field(default=1000)
    
    # Match statistics
    games_played: int = Field(default=0)
    wins: int = Field(default=0)
    losses: int = Field(default=0)
    draws: int = Field(default=0)
    
    # Peak performance
    peak_rating: int = Field(default=1000)
    peak_date: Optional[datetime] = None
    
    # Win streak tracking
    current_streak: int = Field(default=0)  # Positive = win streak, negative = loss streak
    best_win_streak: int = Field(default=0)
    worst_loss_streak: int = Field(default=0)
    
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    )
    
    def win_rate(self) -> float:
        """Calculate win percentage"""
        if self.games_played == 0:
            return 0.0
        return (self.wins / self.games_played) * 100
    
    def is_provisional(self) -> bool:
        """Check if rating is still provisional (< 5 games)"""
        return self.games_played < 5


class ELOHistory(SQLModel, table=True):
    """
    Historical record of ELO changes.
    
    Tracks every rating change for transparency and analysis.
    """
    __tablename__ = "elo_history"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    opponent_id: int = Field(foreign_key="users.id", index=True)
    
    rating_type: str = Field(index=True)  # "league", "tournament", "global"
    
    # Rating change details
    old_rating: int
    new_rating: int
    rating_change: int  # Can be positive or negative
    
    # Match result
    result: str  # "win", "draw", "loss"
    
    # ELO calculation details
    k_factor: int
    expected_score: float  # 0.0 to 1.0
    actual_score: float    # 0.0 (loss), 0.5 (draw), 1.0 (win)
    
    # Optional match reference
    match_id: Optional[int] = None  # FK to League Match
    match_type: Optional[str] = None  # "league", "tournament", "friendly"
    
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        # Use Column index flag to avoid Field/sa_column incompatibility
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), index=True)
    )
