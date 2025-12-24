"""
Dependency Injection Functions

Common dependencies for FastAPI routes.
"""

from typing import Generator
from fastapi import Depends
from sqlmodel import Session
from app.db import get_session


# Database session dependency (re-exported for convenience)
def get_db() -> Generator[Session, None, None]:
    """Get database session dependency"""
    return get_session()


# User authentication dependencies - imported from users.auth
# These will be properly set up when users module is imported
def get_current_user():
    """
    Get current authenticated user.
    Import from app.users.auth for actual implementation.
    """
    from app.users.auth import current_active_user
    return current_active_user


def get_current_active_user():
    """
    Get current active user.
    Import from app.users.auth for actual implementation.
    """
    from app.users.auth import current_active_user
    return current_active_user
