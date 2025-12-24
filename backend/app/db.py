"""
Database Configuration and Session Management

Using SQLModel (SQLAlchemy + Pydantic) for ORM.
"""

from typing import Generator
from sqlmodel import Session, create_engine
from app.config import settings

# Create engine
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # Log SQL queries in debug mode
    pool_pre_ping=True,   # Verify connections before using
)


def get_session() -> Generator[Session, None, None]:
    """
    Dependency that provides a database session.
    
    Usage:
        @app.get("/users")
        def get_users(session: Session = Depends(get_session)):
            ...
    """
    with Session(engine) as session:
        yield session


def init_db() -> None:
    """
    Initialize database - create all tables.
    Called on application startup.
    """
    from sqlmodel import SQLModel
    
    # Import all models here to ensure they're registered
    from app.users.models import User  # noqa: F401
    # Import other models as they're created
    
    SQLModel.metadata.create_all(engine)
