import io
import uuid
from datetime import datetime
from pathlib import Path

import httpx
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
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import RedirectResponse
from PIL import Image
from sqlmodel import Session, select

AVATAR_SIZE = (256, 256)
AVATAR_DIR = Path("/app/uploads/avatars")

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
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get current authenticated user info."""
    has_discord_oauth = (
        session.exec(
            select(OAuthAccount).where(
                OAuthAccount.user_id == current_user.id,
                OAuthAccount.provider == "discord",
            )
        ).first()
        is not None
    )
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        role=current_user.role,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        discord_username=current_user.discord_username,
        show_email=current_user.show_email,
        avatar_url=current_user.avatar_url,
        has_discord_oauth=has_discord_oauth,
        created_at=current_user.created_at,
    )


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

    # Discord username - only editable if not logged in via Discord
    if user_update.discord_username is not None:
        has_discord_oauth = session.exec(
            select(OAuthAccount).where(
                OAuthAccount.user_id == current_user.id,
                OAuthAccount.provider == "discord",
            )
        ).first()
        if has_discord_oauth:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Discord username is managed by Discord OAuth",
            )
        current_user.discord_username = user_update.discord_username or None

    if user_update.show_email is not None:
        current_user.show_email = user_update.show_email

    # Avatar can always be changed (even with Discord OAuth - user override)
    if user_update.avatar_url is not None:
        current_user.avatar_url = user_update.avatar_url or None

    # Toggle organizer role (only if not admin)
    if user_update.wants_organizer is not None and current_user.role != "admin":
        if user_update.wants_organizer:
            current_user.role = "organizer"
        else:
            current_user.role = "player"

    session.add(current_user)
    session.commit()
    session.refresh(current_user)

    has_discord_oauth = (
        session.exec(
            select(OAuthAccount).where(
                OAuthAccount.user_id == current_user.id,
                OAuthAccount.provider == "discord",
            )
        ).first()
        is not None
    )
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        role=current_user.role,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        discord_username=current_user.discord_username,
        show_email=current_user.show_email,
        avatar_url=current_user.avatar_url,
        has_discord_oauth=has_discord_oauth,
        created_at=current_user.created_at,
    )


@router.post("/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Upload and set user avatar image."""
    # Validate file type
    if file.content_type not in ["image/jpeg", "image/png", "image/gif", "image/webp"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only JPEG, PNG, GIF, and WebP are allowed.",
        )

    # Read and process image
    try:
        contents = await file.read()
        if len(contents) > 5 * 1024 * 1024:  # 5MB limit
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File too large. Maximum size is 5MB.",
            )

        # Open and resize image
        img = Image.open(io.BytesIO(contents))

        # Convert to RGB if necessary (for PNG with transparency)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        # Resize to standard size, maintaining aspect ratio and cropping to square
        width, height = img.size
        min_dim = min(width, height)
        left = (width - min_dim) // 2
        top = (height - min_dim) // 2
        img = img.crop((left, top, left + min_dim, top + min_dim))
        img = img.resize(AVATAR_SIZE, Image.Resampling.LANCZOS)

        # Generate unique filename
        filename = f"{current_user.id}_{uuid.uuid4().hex[:8]}.jpg"
        filepath = AVATAR_DIR / filename

        # Ensure directory exists
        AVATAR_DIR.mkdir(parents=True, exist_ok=True)

        # Save image
        img.save(filepath, "JPEG", quality=85)

        # Delete old avatar file if it was an uploaded one
        if current_user.avatar_url and "/uploads/avatars/" in current_user.avatar_url:
            old_filename = current_user.avatar_url.split("/")[-1]
            old_filepath = AVATAR_DIR / old_filename
            if old_filepath.exists() and old_filepath != filepath:
                old_filepath.unlink()

        # Update user avatar URL (include /api prefix for nginx routing)
        avatar_url = f"/api/uploads/avatars/{filename}"
        current_user.avatar_url = avatar_url
        session.add(current_user)
        session.commit()

        return {"avatar_url": avatar_url}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process image: {str(e)}",
        )


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

        # Fetch Discord username and avatar from Discord API
        discord_username = None
        discord_avatar_url = None
        async with httpx.AsyncClient() as http_client:
            resp = await http_client.get(
                "https://discord.com/api/users/@me",
                headers={"Authorization": f"Bearer {token['access_token']}"},
            )
            if resp.status_code == 200:
                discord_data = resp.json()
                discord_username = discord_data.get("username")
                # Build avatar URL
                avatar_hash = discord_data.get("avatar")
                if avatar_hash:
                    discord_avatar_url = f"https://cdn.discordapp.com/avatars/{provider_user_id}/{avatar_hash}.png?size=256"

        # Check if OAuth account exists
        statement = select(OAuthAccount).where(
            OAuthAccount.provider == "discord",
            OAuthAccount.provider_user_id == provider_user_id,
        )
        oauth_account = session.exec(statement).first()

        if oauth_account:
            # Get existing user and update discord_username/avatar
            user = session.get(User, oauth_account.user_id)
            updated = False
            if discord_username and user.discord_username != discord_username:
                user.discord_username = discord_username
                updated = True
            if discord_avatar_url and user.avatar_url != discord_avatar_url:
                user.avatar_url = discord_avatar_url
                updated = True
            if updated:
                session.add(user)
                session.commit()
                session.refresh(user)
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
                    discord_username=discord_username,  # Set from Discord API
                    avatar_url=discord_avatar_url,  # Set from Discord API
                )
                session.add(user)
                session.commit()
                session.refresh(user)
            elif discord_username or discord_avatar_url:
                # Update discord info for existing user linking Discord
                if discord_username:
                    user.discord_username = discord_username
                if discord_avatar_url:
                    user.avatar_url = discord_avatar_url
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
