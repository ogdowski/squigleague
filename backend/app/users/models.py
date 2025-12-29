from typing import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship


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

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
