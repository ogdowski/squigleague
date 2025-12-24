"""
FastAPI Users Configuration

OAuth setup and user management configuration.
"""

from typing import Optional
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, IntegerIDMixin
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users.db import SQLAlchemyUserDatabase
from httpx_oauth.clients.google import GoogleOAuth2
from httpx_oauth.clients.discord import DiscordOAuth2
from sqlmodel import Session

from app.config import settings
from app.db import get_session
from app.users.models import User, OAuthAccount


# ═══════════════════════════════════════════════
# OAUTH CLIENTS
# ═══════════════════════════════════════════════


google_oauth_client = GoogleOAuth2(
    client_id=settings.GOOGLE_CLIENT_ID or "",
    client_secret=settings.GOOGLE_CLIENT_SECRET or "",
)

discord_oauth_client = DiscordOAuth2(
    client_id=settings.DISCORD_CLIENT_ID or "",
    client_secret=settings.DISCORD_CLIENT_SECRET or "",
    scopes=["identify", "email"],
)


# ═══════════════════════════════════════════════
# USER DATABASE ADAPTER
# ═══════════════════════════════════════════════


async def get_user_db(session: Session = Depends(get_session)):
    """Get user database adapter"""
    yield SQLAlchemyUserDatabase(session, User, OAuthAccount)


# ═══════════════════════════════════════════════
# USER MANAGER
# ═══════════════════════════════════════════════


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    """User manager with custom logic"""
    
    reset_password_token_secret = settings.SECRET_KEY
    verification_token_secret = settings.SECRET_KEY
    
    async def on_after_register(self, user: User, request: Optional[Request] = None):
        """Called after user registration"""
        print(f"User {user.id} has registered via OAuth")
    
    async def on_after_login(
        self,
        user: User,
        request: Optional[Request] = None,
        response = None,
    ):
        """Called after successful login"""
        print(f"User {user.id} ({user.username}) logged in")
    
    async def create(self, user_create, safe: bool = False, request: Optional[Request] = None):
        """
        Override create to auto-generate username from email if not provided.
        For OAuth users, username will be extracted from OAuth data.
        """
        # If username not provided, generate from email
        if not hasattr(user_create, 'username') or not user_create.username:
            email_prefix = user_create.email.split('@')[0]
            # Sanitize username (remove special chars)
            username = ''.join(c for c in email_prefix if c.isalnum() or c == '_')
            user_create.username = username[:100]  # Limit to 100 chars
        
        return await super().create(user_create, safe=safe, request=request)
    
    async def oauth_callback(
        self,
        oauth_name: str,
        access_token: str,
        account_id: str,
        account_email: str,
        expires_at: Optional[int] = None,
        refresh_token: Optional[str] = None,
        request: Optional[Request] = None,
        *,
        associate_by_email: bool = False,
        is_verified_by_default: bool = True,
    ):
        """
        Handle OAuth callback.
        Override to set username from OAuth provider data.
        """
        # For new users, extract username from email or OAuth data
        user_create_dict = {
            "email": account_email,
            "username": account_email.split('@')[0],  # Default username from email
            "password": "oauth_user_no_password",  # Dummy password (not used)
            "is_verified": is_verified_by_default,
            "role": "player",  # Default role
        }
        
        return await super().oauth_callback(
            oauth_name=oauth_name,
            access_token=access_token,
            account_id=account_id,
            account_email=account_email,
            expires_at=expires_at,
            refresh_token=refresh_token,
            request=request,
            associate_by_email=associate_by_email,
            is_verified_by_default=is_verified_by_default,
        )


async def get_user_manager(user_db=Depends(get_user_db)):
    """Get user manager dependency"""
    yield UserManager(user_db)


# ═══════════════════════════════════════════════
# AUTHENTICATION BACKEND
# ═══════════════════════════════════════════════


bearer_transport = BearerTransport(tokenUrl="api/auth/jwt/login")


def get_jwt_strategy() -> JWTStrategy:
    """Get JWT strategy for authentication"""
    return JWTStrategy(
        secret=settings.SECRET_KEY,
        lifetime_seconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)


# ═══════════════════════════════════════════════
# FASTAPI USERS INSTANCE
# ═══════════════════════════════════════════════


fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

# Dependency to get current active user
current_active_user = fastapi_users.current_user(active=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)
