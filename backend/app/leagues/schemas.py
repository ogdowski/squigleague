"""
Leagues Schemas

Request and response models for league endpoints.
"""

from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field


# Request Schemas

class LeagueCreate(BaseModel):
    """Create new league"""
    name: str = Field(..., min_length=3, max_length=100)
    season: str = Field(..., min_length=3, max_length=50)
    format_type: str = Field(default="group_playoff")
    config: dict = Field(default={})
    start_date: date
    registration_deadline: date


class LeagueUpdate(BaseModel):
    """Update league (organizer only)"""
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    season: Optional[str] = Field(None, min_length=3, max_length=50)
    registration_deadline: Optional[date] = None
    config: Optional[dict] = None


class MatchResultSubmit(BaseModel):
    """Submit match result"""
    player1_score: int = Field(..., ge=0, le=100)
    player2_score: int = Field(..., ge=0, le=100)


# Response Schemas

class LeagueRead(BaseModel):
    """League details"""
    id: int
    name: str
    season: str
    organizer_id: int
    format_type: str
    config: dict
    status: str
    start_date: date
    registration_deadline: date
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class LeagueListItem(BaseModel):
    """League list item (condensed)"""
    id: int
    name: str
    season: str
    status: str
    registration_deadline: date
    
    class Config:
        from_attributes = True


class ParticipantRead(BaseModel):
    """League participant"""
    id: int
    league_id: int
    user_id: int
    group_number: Optional[int] = None
    registered_at: datetime
    
    class Config:
        from_attributes = True


class MatchRead(BaseModel):
    """League match"""
    id: int
    league_id: int
    player1_id: int
    player2_id: int
    phase: str
    round_number: int
    player1_score: Optional[int] = None
    player2_score: Optional[int] = None
    player1_points: Optional[int] = None
    player2_points: Optional[int] = None
    played: bool
    deadline: datetime
    
    class Config:
        from_attributes = True


class StandingRead(BaseModel):
    """League standing"""
    id: int
    league_id: int
    user_id: int
    phase: str
    total_points: int
    matches_played: int
    matches_total: int
    wins: int
    draws: int
    losses: int
    position: int
    
    class Config:
        from_attributes = True
