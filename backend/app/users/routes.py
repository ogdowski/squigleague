from datetime import datetime

from app.config import settings
from app.core.deps import get_current_user
from app.core.security import create_access_token, get_password_hash, verify_password
from app.db import get_session
from app.users.auth import get_discord_oauth_client, get_google_oauth_client
from app.users.models import OAuthAccount, User
from app.users.schemas import (
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
    UserUpdate,
)
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select

router = APIRouter()


@router.post(
    "/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED
)
async def register(user_data: UserCreate, session: Session = Depends(get_session)):
    """Register a new user."""
    statement = select(User).where(
        (User.email == user_data.email) | (User.username == user_data.username)
    )
    existing_user = session.exec(statement).first()

    if existing_user:
        if existing_user.email == user_data.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken",
            )

    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=get_password_hash(user_data.password),
        role="player",
        is_active=True,
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    access_token = create_access_token(data={"sub": str(user.id)})

    return TokenResponse(
        access_token=access_token,
        user=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, session: Session = Depends(get_session)):
    """Login with email and password."""
    statement = select(User).where(User.email == credentials.email)
    user = session.exec(statement).first()

    if not user or not user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )

    access_token = create_access_token(data={"sub": str(user.id)})

    return TokenResponse(
        access_token=access_token,
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current authenticated user info."""
    return UserResponse.model_validate(current_user)


@router.patch("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Update current user profile."""
    if user_update.username:
        statement = select(User).where(
            User.username == user_update.username,
            User.id != current_user.id,
        )
        existing_user = session.exec(statement).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken",
            )
        current_user.username = user_update.username

    if user_update.email:
        statement = select(User).where(
            User.email == user_update.email,
            User.id != current_user.id,
        )
        existing_user = session.exec(statement).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
        current_user.email = user_update.email

    session.add(current_user)
    session.commit()
    session.refresh(current_user)

    return UserResponse.model_validate(current_user)


# ═══════════════════════════════════════════════
# OAuth Routes
# ═══════════════════════════════════════════════


@router.get("/oauth/google")
async def oauth_google():
    """Redirect to Google OAuth login."""
    client = get_google_oauth_client()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google OAuth not configured",
        )

    redirect_uri = f"{settings.BASE_URL}/api/auth/oauth/google/callback"
    authorization_url = await client.get_authorization_url(
        redirect_uri,
        scope=["openid", "email", "profile"],
    )
    return {"authorization_url": authorization_url}


@router.get("/oauth/google/callback")
async def oauth_google_callback(
    code: str,
    session: Session = Depends(get_session),
):
    """Handle Google OAuth callback."""
    client = get_google_oauth_client()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google OAuth not configured",
        )

    redirect_uri = f"{settings.BASE_URL}/api/auth/oauth/google/callback"

    try:
        token = await client.get_access_token(code, redirect_uri)
        user_info = await client.get_id_email(token["access_token"])

        provider_user_id = user_info[0]  # Google user ID
        email = user_info[1]  # Email

        # Check if OAuth account exists
        statement = select(OAuthAccount).where(
            OAuthAccount.provider == "google",
            OAuthAccount.provider_user_id == provider_user_id,
        )
        oauth_account = session.exec(statement).first()

        if oauth_account:
            # Get existing user
            user = session.get(User, oauth_account.user_id)
        else:
            # Check if user exists with this email
            statement = select(User).where(User.email == email)
            user = session.exec(statement).first()

            if not user:
                # Create new user
                username = email.split("@")[0]
                # Make username unique if needed
                counter = 1
                base_username = username
                while session.exec(
                    select(User).where(User.username == username)
                ).first():
                    username = f"{base_username}{counter}"
                    counter += 1

                user = User(
                    email=email,
                    username=username,
                    role="player",
                    is_active=True,
                    is_verified=True,  # OAuth users are pre-verified
                )
                session.add(user)
                session.commit()
                session.refresh(user)

            # Create OAuth account link
            oauth_account = OAuthAccount(
                user_id=user.id,
                provider="google",
                provider_user_id=provider_user_id,
                access_token=token.get("access_token"),
                refresh_token=token.get("refresh_token"),
                expires_at=datetime.utcnow(),
            )
            session.add(oauth_account)
            session.commit()

        # Create JWT token
        access_token = create_access_token(data={"sub": str(user.id)})

        # Redirect to frontend with token
        frontend_url = (
            settings.BASE_URL if settings.CORS_ORIGINS else "http://localhost"
        )
        return RedirectResponse(
            url=f"{frontend_url}/oauth/callback?token={access_token}&provider=google"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth authentication failed: {str(e)}",
        )


@router.get("/oauth/discord")
async def oauth_discord():
    """Redirect to Discord OAuth login."""
    client = get_discord_oauth_client()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Discord OAuth not configured",
        )

    redirect_uri = f"{settings.BASE_URL}/api/auth/oauth/discord/callback"
    authorization_url = await client.get_authorization_url(
        redirect_uri,
        scope=["identify", "email"],
    )
    return {"authorization_url": authorization_url}


@router.get("/oauth/discord/callback")
async def oauth_discord_callback(
    code: str,
    session: Session = Depends(get_session),
):
    """Handle Discord OAuth callback."""
    client = get_discord_oauth_client()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Discord OAuth not configured",
        )

    redirect_uri = f"{settings.BASE_URL}/api/auth/oauth/discord/callback"

    try:
        token = await client.get_access_token(code, redirect_uri)
        user_info = await client.get_id_email(token["access_token"])

        provider_user_id = user_info[0]  # Discord user ID
        email = user_info[1]  # Email

        # Check if OAuth account exists
        statement = select(OAuthAccount).where(
            OAuthAccount.provider == "discord",
            OAuthAccount.provider_user_id == provider_user_id,
        )
        oauth_account = session.exec(statement).first()

        if oauth_account:
            # Get existing user
            user = session.get(User, oauth_account.user_id)
        else:
            # Check if user exists with this email
            statement = select(User).where(User.email == email)
            user = session.exec(statement).first()

            if not user:
                # Create new user
                username = (
                    email.split("@")[0] if email else f"discord_{provider_user_id[:8]}"
                )
                # Make username unique if needed
                counter = 1
                base_username = username
                while session.exec(
                    select(User).where(User.username == username)
                ).first():
                    username = f"{base_username}{counter}"
                    counter += 1

                user = User(
                    email=email or f"discord_{provider_user_id}@placeholder.com",
                    username=username,
                    role="player",
                    is_active=True,
                    is_verified=True,  # OAuth users are pre-verified
                )
                session.add(user)
                session.commit()
                session.refresh(user)

            # Create OAuth account link
            oauth_account = OAuthAccount(
                user_id=user.id,
                provider="discord",
                provider_user_id=provider_user_id,
                access_token=token.get("access_token"),
                refresh_token=token.get("refresh_token"),
                expires_at=datetime.utcnow(),
            )
            session.add(oauth_account)
            session.commit()

        # Create JWT token
        access_token = create_access_token(data={"sub": str(user.id)})

        # Redirect to frontend with token
        frontend_url = (
            settings.BASE_URL if settings.CORS_ORIGINS else "http://localhost"
        )
        return RedirectResponse(
            url=f"{frontend_url}/oauth/callback?token={access_token}&provider=discord"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth authentication failed: {str(e)}",
        )
