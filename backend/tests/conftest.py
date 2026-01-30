"""Test configuration for SquigLeague backend tests"""

import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

# Add app directory to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

# Set test environment variables before importing app modules
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"
os.environ["ENVIRONMENT"] = "testing"
os.environ["DEBUG"] = "False"

# Import all models to ensure they're registered with SQLModel metadata
from app.bsdata.models import (
    BattleFormation,
    BattleTacticCard,
    BattleTrait,
    BSDataSyncStatus,
    CoreAbility,
    Faction,
    GrandAlliance,
    HeroicTrait,
    Manifestation,
    ManifestationLore,
    Prayer,
    PrayerLore,
    RegimentOfRenown,
    Spell,
    SpellLore,
    Unit,
    UnitAbility,
    UnitFaction,
    Weapon,
)
from app.league.models import (
    AppSettings,
    ArmyMatchupStats,
    ArmyStats,
    Group,
    League,
    LeaguePlayer,
    Match,
    PlayerElo,
    Vote,
    VoteCategory,
)
from app.matchup.models import Matchup
from app.users.models import OAuthAccount, User


@pytest.fixture(name="session")
def session_fixture():
    """Create an in-memory SQLite database for testing"""
    from datetime import datetime, timedelta

    from app.core.security import get_password_hash

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        # Seed test user: alakhaine@dundrafts.com / Alakhaine / FinFan11
        test_user = User(
            email="alakhaine@dundrafts.com",
            username="Alakhaine",
            hashed_password=get_password_hash("FinFan11"),
            role="player",
            is_active=True,
            is_verified=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        session.add(test_user)
        session.commit()
        session.refresh(test_user)

        # Seed test matchup
        test_matchup = Matchup(
            name="test-matchup",
            player1_id=test_user.id,
            player1_submitted=True,
            player2_submitted=False,
            player1_list="Cities of Sigmar",
            player2_list=None,
            map_name="Age of Sigmar Mission 1",
            created_at=datetime.utcnow(),
        )
        session.add(test_matchup)
        session.commit()

        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create a test client with database session override"""
    from app.db import get_session
    from app.main import app

    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="test_user")
def test_user_fixture(session: Session):
    """Get the seeded test user from the database"""
    from sqlmodel import select

    statement = select(User).where(User.username == "Alakhaine")
    user = session.scalars(statement).first()
    return user


@pytest.fixture(name="auth_headers")
def auth_headers_fixture(client: TestClient):
    """Get authentication headers for the test user"""
    response = client.post(
        "/auth/login",
        json={"email": "alakhaine@dundrafts.com", "password": "FinFan11"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
