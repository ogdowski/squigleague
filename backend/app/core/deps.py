from typing import Optional

from app.core.security import decode_access_token
from app.db import get_session
from app.league.models import AppSettings
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session, select

security = HTTPBearer(auto_error=False)


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    session: Session = Depends(get_session),
):
    """Get current user from JWT token (optional - returns None if not authenticated)."""
    if not credentials:
        return None

    token = credentials.credentials
    payload = decode_access_token(token)

    if not payload:
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None

    from app.users.models import User

    statement = select(User).where(User.id == int(user_id))
    user = session.exec(statement).first()

    return user


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session),
):
    """Get current user from JWT token (required)."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    from app.users.models import User

    statement = select(User).where(User.id == int(user_id))
    user = session.exec(statement).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )

    return user


def require_role(*allowed_roles: str):
    """Dependency factory for role-based access control."""

    async def role_checker(current_user=Depends(get_current_user)):
        if current_user.role not in allowed_roles and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user

    return role_checker


get_current_organizer = require_role("organizer", "admin")
get_current_admin = require_role("admin")


async def require_rules_enabled(
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Block access to rules/bsdata when rules feature is disabled. Admin always passes."""
    if current_user.role == "admin":
        return current_user
    statement = select(AppSettings).where(AppSettings.key == "rules_enabled")
    setting = session.scalars(statement).first()
    if not setting or setting.value != "true":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Rules feature is disabled",
        )
    return current_user
