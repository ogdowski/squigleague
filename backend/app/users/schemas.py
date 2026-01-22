from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    """Schema for user registration."""

    email: EmailStr
    username: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=8)


class UserLogin(BaseModel):
    """Schema for user login."""

    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """Schema for updating user profile."""

    username: Optional[str] = Field(None, min_length=3, max_length=100)
    email: Optional[EmailStr] = None
    discord_username: Optional[str] = Field(None, max_length=100)
    show_email: Optional[bool] = None
    avatar_url: Optional[str] = Field(None, max_length=500)
    wants_organizer: Optional[bool] = None  # Toggle between player/organizer role
    preferred_language: Optional[str] = Field(None, max_length=5)  # ISO 639-1 code
    city: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)


class UserResponse(BaseModel):
    """Schema for user response."""

    id: int
    email: str
    username: str
    role: str
    is_active: bool
    is_verified: bool
    discord_username: Optional[str] = None
    show_email: bool = False
    avatar_url: Optional[str] = None
    has_discord_oauth: bool = False  # True if discord linked via OAuth
    preferred_language: str = "en"  # ISO 639-1 code
    city: Optional[str] = None
    country: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    """Schema for authentication token response."""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse
