"""
Dependency Injection Functions

Common dependencies for FastAPI routes.
"""

from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from sqlmodel import Session
from app.db import get_session


# Database session dependency (re-exported for convenience)
def get_db() -> Generator[Session, None, None]:
    """Get database session dependency"""
    return get_session()


# User authentication dependencies will be added when FastAPI Users is integrated
# For now, placeholder functions:

async def get_current_user(session: Session = Depends(get_db)):
    """
    Get current authenticated user.
    
    TODO: Implement with FastAPI Users
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Authentication not yet implemented"
    )


async def get_current_active_user(
    current_user = Depends(get_current_user)
):
    """
    Get current active user.
    
    TODO: Implement with FastAPI Users
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user
