from app.config import settings
from sqlmodel import Session, create_engine

# Create database engine with appropriate settings for the database type
if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite doesn't support pool_size and max_overflow
    engine = create_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        connect_args=(
            {"check_same_thread": False} if "memory" in settings.DATABASE_URL else {}
        ),
    )
else:
    # PostgreSQL and other databases support connection pooling
    engine = create_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
    )


def get_session():
    """Dependency for getting database sessions."""
    with Session(engine) as session:
        yield session


def create_db_and_tables():
    """Create database tables. Called on startup."""
    # Import all models here to ensure they're registered
    from app.league.models import (  # noqa: F401
        AppSettings,
        ArmyMatchupStats,
        ArmyStats,
        Group,
        League,
        LeaguePlayer,
        Match,
        PlayerElo,
    )
    from app.matchup.models import Matchup  # noqa: F401
    from app.users.models import OAuthAccount, User  # noqa: F401
    from sqlmodel import SQLModel

    SQLModel.metadata.create_all(engine)
