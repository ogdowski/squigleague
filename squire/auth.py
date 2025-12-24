"""
Authentication Module for SquigLeague

User registration, login, email verification, and JWT token management
"""

import os
from datetime import datetime, timedelta
from typing import Optional
import uuid
import bcrypt
from jose import JWTError, jwt
from fastapi import HTTPException, Header, Depends
from pydantic import BaseModel, EmailStr, Field, validator
import re

from squire.database import User, EmailVerificationToken, get_session
from squire.email_service import send_verification_email


# ═══════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════


JWT_SECRET = os.getenv("JWT_SECRET", "dev_secret_key_change_in_production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = 24


# ═══════════════════════════════════════════════
# REQUEST/RESPONSE MODELS
# ═══════════════════════════════════════════════


class RegisterRequest(BaseModel):
    """User registration request"""
    username: str = Field(..., min_length=3, max_length=20)
    email: EmailStr
    password: str = Field(..., min_length=8)
    
    @validator("username")
    def validate_username(cls, v):
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError("Username can only contain letters, numbers, and underscores")
        return v.lower()
    
    @validator("password")
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        # Optional: Add number requirement for stronger passwords
        # if not re.search(r"\d", v):
        #     raise ValueError("Password must contain at least one number")
        return v


class RegisterResponse(BaseModel):
    """User registration response"""
    user_id: str
    username: str
    email: str
    message: str


class LoginRequest(BaseModel):
    """User login request"""
    username_or_email: str
    password: str


class LoginResponse(BaseModel):
    """User login response"""
    user_id: str
    username: str
    email: str
    token: str
    expires_at: str


class UserResponse(BaseModel):
    """Current user info response"""
    user_id: str
    username: str
    email: str
    email_verified: bool
    is_admin: bool
    created_at: str


class UserProfileStats(BaseModel):
    """User profile statistics"""
    total_matchups: int
    favorite_system: Optional[str] = None
    matchups_this_month: int
    systems_played: dict[str, int]


class UserProfileResponse(BaseModel):
    """User profile with stats"""
    user_id: str
    username: str
    email: str
    email_verified: bool
    is_admin: bool
    country: Optional[str] = None
    city: Optional[str] = None
    profile_image_url: Optional[str] = None
    created_at: str
    stats: UserProfileStats


class ResendVerificationRequest(BaseModel):
    """Resend verification email request"""
    email: EmailStr


# ═══════════════════════════════════════════════
# PASSWORD HASHING
# ═══════════════════════════════════════════════


def hash_password(password: str) -> str:
    """Hash password with bcrypt"""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


# ═══════════════════════════════════════════════
# JWT TOKEN MANAGEMENT
# ═══════════════════════════════════════════════


def create_jwt_token(user_id: str, username: str, email: str) -> tuple[str, datetime]:
    """
    Create JWT token for authenticated user
    
    Returns:
        Tuple of (token, expiry_datetime)
    """
    expires_at = datetime.utcnow() + timedelta(hours=JWT_EXPIRY_HOURS)
    
    # Get user object to include all profile fields in token
    from squire.database import get_session, User
    db = next(get_session())
    try:
        user_obj = db.query(User).filter(User.id == user_id).first()
        
        payload = {
            "user_id": user_id,
            "username": username,
            "email": email,
            "is_admin": user_obj.is_admin if user_obj else False,
            "email_verified": user_obj.email_verified if user_obj else False,
            "exp": expires_at,
        }
    finally:
        db.close()
    
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token, expires_at


def decode_jwt_token(token: str) -> Optional[dict]:
    """
    Decode and validate JWT token
    
    Returns:
        Payload dict if valid, None if invalid/expired
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        return None


# ═══════════════════════════════════════════════
# AUTHENTICATION MIDDLEWARE
# ═══════════════════════════════════════════════


async def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    """
    Dependency to get current authenticated user from JWT token
    
    Usage: user = Depends(get_current_user)
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Extract token from "Bearer {token}"
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = parts[1]
    payload = decode_jwt_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return payload


async def require_admin(user: dict = Depends(get_current_user)) -> dict:
    """
    Dependency to require admin privileges
    
    Usage: admin_user = Depends(require_admin)
    """
    db = get_session()
    try:
        db_user = db.query(User).filter(User.id == user["user_id"]).first()
        if not db_user or not db_user.is_admin:
            raise HTTPException(status_code=403, detail="Admin privileges required")
        return user
    finally:
        db.close()


# ═══════════════════════════════════════════════
# REGISTRATION & VERIFICATION
# ═══════════════════════════════════════════════


async def register_user(request: RegisterRequest) -> RegisterResponse:
    """
    Register new user and send verification email
    
    Raises:
        HTTPException: If username or email already exists
    """
    db = get_session()
    
    try:
        # Check if username exists
        existing_user = db.query(User).filter(User.username == request.username.lower()).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already taken")
        
        # Check if email exists
        existing_email = db.query(User).filter(User.email == request.email.lower()).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create user
        user = User(
            id=uuid.uuid4(),
            username=request.username.lower(),
            email=request.email.lower(),
            password_hash=hash_password(request.password),
            email_verified=False,
        )
        db.add(user)
        db.flush()
        
        # Create verification token
        verification_token = EmailVerificationToken(
            user_id=user.id,
            token=uuid.uuid4(),
            expires_at=datetime.utcnow() + timedelta(hours=24),
        )
        db.add(verification_token)
        db.commit()
        
        # Send verification email
        await send_verification_email(
            username=user.username,
            email=user.email,
            verification_token=str(verification_token.token),
        )
        
        return RegisterResponse(
            user_id=str(user.id),
            username=user.username,
            email=user.email,
            message="Registration successful. Please check your email to verify your account.",
        )
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")
    finally:
        db.close()


async def verify_email(token: str) -> dict:
    """
    Verify user email with token
    
    Returns:
        Success message dict
        
    Raises:
        HTTPException: If token invalid or expired
    """
    db = get_session()
    
    try:
        # Find verification token
        verification = db.query(EmailVerificationToken).filter(
            EmailVerificationToken.token == uuid.UUID(token)
        ).first()
        
        if not verification:
            raise HTTPException(status_code=400, detail="Invalid verification token")
        
        if verification.is_expired:
            raise HTTPException(status_code=400, detail="Verification token expired. Please request a new one.")
        
        # Get user
        user = db.query(User).filter(User.id == verification.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if user.email_verified:
            return {
                "verified": True,
                "message": "Email already verified. You can log in.",
                "redirect_url": "/squire/login"
            }
        
        # Verify email
        user.email_verified = True
        db.delete(verification)
        db.commit()
        
        return {
            "verified": True,
            "message": "Email verified! You can now log in.",
            "redirect_url": "/squire/login"
        }
        
    except HTTPException:
        db.rollback()
        raise
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid token format")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")
    finally:
        db.close()


async def resend_verification_email(email: str) -> dict:
    """
    Resend verification email to unverified user
    
    Returns:
        Generic success message (security: don't leak user existence)
    """
    db = get_session()
    
    try:
        # Find user
        user = db.query(User).filter(User.email == email.lower()).first()
        
        # Generic response regardless of user existence
        generic_response = {
            "message": "If that email is registered and unverified, a verification email has been sent."
        }
        
        if not user:
            return generic_response
        
        if user.email_verified:
            return generic_response
        
        # Delete old tokens
        db.query(EmailVerificationToken).filter(
            EmailVerificationToken.user_id == user.id
        ).delete()
        
        # Create new token
        verification_token = EmailVerificationToken(
            user_id=user.id,
            token=uuid.uuid4(),
            expires_at=datetime.utcnow() + timedelta(hours=24),
        )
        db.add(verification_token)
        db.commit()
        
        # Send email
        await send_verification_email(
            username=user.username,
            email=user.email,
            verification_token=str(verification_token.token),
        )
        
        return generic_response
        
    except Exception as e:
        db.rollback()
        print(f"ERROR: Failed to resend verification: {e}")
        return generic_response
    finally:
        db.close()


async def login_user(username_or_email: str, password: str) -> LoginResponse:
    """
    Authenticate user and return JWT token
    
    Raises:
        HTTPException: If credentials invalid or email not verified
    """
    db = get_session()
    
    try:
        # Find user by username or email
        user = db.query(User).filter(
            (User.username == username_or_email.lower()) | (User.email == username_or_email.lower())
        ).first()
        
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Verify password
        if not verify_password(password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Check email verified
        if not user.email_verified:
            raise HTTPException(
                status_code=403,
                detail="Email not verified. Please check your email for the verification link."
            )
        
        # Generate JWT token
        token, expires_at = create_jwt_token(
            user_id=str(user.id),
            username=user.username,
            email=user.email,
        )
        
        return LoginResponse(
            user_id=str(user.id),
            username=user.username,
            email=user.email,
            token=token,
            expires_at=expires_at.isoformat(),
        )
        
    finally:
        db.close()


async def get_user_info(user_payload: dict) -> UserResponse:
    """
    Get current user information
    
    Args:
        user_payload: JWT payload from get_current_user dependency
        
    Returns:
        User information
    """
    db = get_session()
    
    try:
        user = db.query(User).filter(User.id == user_payload["user_id"]).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserResponse(
            user_id=str(user.id),
            username=user.username,
            email=user.email,
            email_verified=user.email_verified,
            is_admin=user.is_admin,
            created_at=user.created_at.isoformat(),
        )
        
    finally:
        db.close()


async def get_user_profile(user_payload: dict) -> UserProfileResponse:
    """
    Get user profile with statistics
    
    Args:
        user_payload: JWT payload from get_current_user dependency
        
    Returns:
        User profile with stats
    """
    from squire.matchup import get_matchups_for_user
    from datetime import datetime
    from collections import Counter
    
    db = get_session()
    
    try:
        user = db.query(User).filter(User.id == user_payload["user_id"]).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get user's matchups for stats
        all_matchups = get_matchups_for_user(str(user.id))
        
        # Calculate stats
        total_matchups = len(all_matchups)
        
        # Count matchups by system
        systems_counter = Counter()
        for matchup in all_matchups:
            systems_counter[matchup.game_system.value] += 1
        
        # Determine favorite system
        favorite_system = None
        if systems_counter:
            fav_sys = systems_counter.most_common(1)[0][0]
            system_names = {
                'age_of_sigmar': 'Age of Sigmar',
                'warhammer_40k': 'Warhammer 40,000',
                'the_old_world': 'The Old World'
            }
            favorite_system = system_names.get(fav_sys, fav_sys)
        
        # Count matchups this month
        now = datetime.utcnow()
        matchups_this_month = sum(
            1 for m in all_matchups 
            if m.created_at.month == now.month and m.created_at.year == now.year
        )
        
        stats = UserProfileStats(
            total_matchups=total_matchups,
            favorite_system=favorite_system,
            matchups_this_month=matchups_this_month,
            systems_played=dict(systems_counter)
        )
        
        return UserProfileResponse(
            user_id=str(user.id),
            username=user.username,
            email=user.email,
            email_verified=user.email_verified,
            is_admin=user.is_admin,
            country=user.country,
            city=user.city,
            profile_image_url=user.profile_image_url,
            created_at=user.created_at.isoformat(),
            stats=stats
        )
        
    finally:
        db.close()
