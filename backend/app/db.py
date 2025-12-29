from sqlmodel import Session, create_engine
from app.config import settings

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # Log SQL queries in debug mode
    pool_pre_ping=True,    # Verify connections before using
    pool_size=5,           # Connection pool size
    max_overflow=10,       # Max overflow connections
)


def get_session():
    """Dependency for getting database sessions."""
    with Session(engine) as session:
        yield session


def create_db_and_tables():
    """Create database tables. Called on startup."""
    from sqlmodel import SQLModel

    # Import all models here to ensure they're registered
    from app.users.models import User, OAuthAccount  # noqa: F401
    from app.matchup.models import Matchup  # noqa: F401

    SQLModel.metadata.create_all(engine)
