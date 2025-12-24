"""
Security Utilities

Password hashing and JWT token management.
Reused from original squire/auth.py with minimal changes.
"""

from datetime import datetime, timedelta
from typing import Optional
import bcrypt
from jose import JWTError, jwt
from app.config import settings


# ═══════════════════════════════════════════════
# PASSWORD HASHING
# ═══════════════════════════════════════════════


def hash_password(password: str) -> str:
    """
    Hash password with bcrypt.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password as string
    """
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verify password against hash.
    
    Args:
        password: Plain text password
        password_hash: Stored password hash
        
    Returns:
        True if password matches, False otherwise
    """
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except Exception:
        return False


# ═══════════════════════════════════════════════
# JWT TOKEN MANAGEMENT
# ═══════════════════════════════════════════════


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token.
    
    Args:
        data: Data to encode in token (usually {"sub": user_id})
        expires_delta: Optional custom expiration time
        
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and verify JWT token.
    
    Args:
        token: JWT token to decode
        
    Returns:
        Decoded token payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None
