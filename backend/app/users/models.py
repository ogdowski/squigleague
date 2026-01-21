from datetime import datetime
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class Location(SQLModel, table=True):
    """Cached unique cities and countries for autocomplete."""

    __tablename__ = "locations"

    id: Optional[int] = Field(default=None, primary_key=True)
    city: Optional[str] = Field(default=None, max_length=100, index=True)
    country: Optional[str] = Field(default=None, max_length=100, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class OAuthAccount(SQLModel, table=True):
    """OAuth account linked to a user."""

    __tablename__ = "oauth_accounts"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    provider: str = Field(max_length=50, index=True)  # "google" or "discord"
    provider_user_id: str = Field(max_length=255, index=True)
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class User(SQLModel, table=True):
    """User model."""

    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    username: str = Field(max_length=100, unique=True, index=True)
    hashed_password: Optional[str] = None  # Optional for OAuth-only users
    role: str = Field(default="player")  # player, organizer, admin
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)

    # Contact info
    discord_username: Optional[str] = Field(default=None, max_length=100)
    show_email: bool = Field(default=False)  # Whether to show email on profile

    # Location
    city: Optional[str] = Field(default=None, max_length=100)
    country: Optional[str] = Field(default=None, max_length=100)

    # Avatar
    avatar_url: Optional[str] = Field(default=None, max_length=500)

    # Language preference (ISO 639-1 code: en, pl, etc.)
    preferred_language: str = Field(default="en", max_length=5)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
