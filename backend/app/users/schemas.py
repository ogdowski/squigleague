"""
User Schemas

Pydantic schemas for user-related requests and responses.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserRead(BaseModel):
    """User response schema (public info)"""
    id: int
    username: str
    email: EmailStr
    role: str
    is_active: bool
    is_verified: bool
    country: Optional[str] = None
    city: Optional[str] = None
    profile_image_url: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """User update schema (for profile updates)"""
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    city: Optional[str] = Field(None, max_length=100)
    profile_image_url: Optional[str] = Field(None, max_length=500)


class UserCreate(BaseModel):
    """
    User creation schema.
    Not used for OAuth (users are created automatically),
    but required by FastAPI Users.
    """
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=8)  # Not used in OAuth flow
    role: str = Field(default="player")


class UserProfileStats(BaseModel):
    """User profile statistics"""
    total_matchups: int = 0
    league_elo: Optional[int] = None
    tournament_elo: Optional[int] = None
    global_elo: Optional[int] = None
    total_games: int = 0
    wins: int = 0
    losses: int = 0
    draws: int = 0
    
    
class UserProfileResponse(BaseModel):
    """Extended user profile with stats"""
    user: UserRead
    stats: UserProfileStats
