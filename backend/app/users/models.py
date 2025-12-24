"""
User Models

SQLModel User model compatible with FastAPI Users.
"""

from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel
from fastapi_users.db import SQLAlchemyBaseUserTable


class User(SQLAlchemyBaseUserTable[int], SQLModel, table=True):
    """
    User model with FastAPI Users integration.
    
    Supports OAuth authentication (Google + Discord).
    No email/password authentication in new version.
    """
    __tablename__ = "users"
    
    # Primary key
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # FastAPI Users required fields
    email: str = Field(unique=True, index=True, max_length=255, nullable=False)
    hashed_password: str = Field(max_length=1024, nullable=False)  # Required by FastAPI Users
    is_active: bool = Field(default=True, nullable=False)
    is_superuser: bool = Field(default=False, nullable=False)
    is_verified: bool = Field(default=True, nullable=False)  # OAuth users are auto-verified
    
    # Custom fields
    username: str = Field(unique=True, index=True, max_length=100, nullable=False)
    role: str = Field(default="player", max_length=20, nullable=False)  # player, organizer, admin
    
    # Profile fields (optional)
    country: Optional[str] = Field(default=None, max_length=100)
    city: Optional[str] = Field(default=None, max_length=100)
    profile_image_url: Optional[str] = Field(default=None, max_length=500)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"


class OAuthAccount(SQLModel, table=True):
    """
    OAuth account linked to a user.
    Managed by FastAPI Users.
    """
    __tablename__ = "oauth_accounts"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", nullable=False, index=True)
    oauth_name: str = Field(max_length=100, nullable=False, index=True)  # "google" or "discord"
    access_token: str = Field(max_length=1024, nullable=False)
    expires_at: Optional[int] = None
    refresh_token: Optional[str] = Field(default=None, max_length=1024)
    account_id: str = Field(max_length=320, nullable=False, index=True)  # OAuth provider's user ID
    account_email: str = Field(max_length=320, nullable=False)
    
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
