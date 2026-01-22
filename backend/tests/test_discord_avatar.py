"""Tests for Discord avatar sync endpoint"""

from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest
from app.core.security import create_access_token, get_password_hash
from app.db import get_session
from app.main import app
from app.users.models import OAuthAccount, User
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool


@pytest.fixture(name="db_session")
def db_session_fixture():
    """Create an in-memory SQLite database for testing"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="test_user")
def test_user_fixture(db_session: Session):
    """Create a test user"""
    user = User(
        email="testuser@example.com",
        username="testuser",
        hashed_password=get_password_hash("password123"),
        role="player",
        is_active=True,
        is_verified=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(name="user_with_discord")
def user_with_discord_fixture(db_session: Session, test_user: User):
    """Create a user with Discord OAuth linked"""
    oauth_account = OAuthAccount(
        user_id=test_user.id,
        provider="discord",
        provider_user_id="123456789012345678",
        access_token="discord_test_token",
        refresh_token="discord_refresh_token",
        expires_at=datetime.utcnow(),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db_session.add(oauth_account)
    db_session.commit()
    return test_user


@pytest.fixture(name="client")
def client_fixture(db_session: Session):
    """Create a test client with database session override"""

    def get_session_override():
        return db_session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="auth_headers")
def auth_headers_fixture(test_user: User):
    """Create auth headers for test user"""
    token = create_access_token(data={"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}


class TestSyncDiscordAvatar:
    """Tests for POST /auth/me/sync-discord-avatar endpoint"""

    def test_sync_without_auth_returns_401(self, client: TestClient):
        """Test that unauthenticated request returns 401"""
        response = client.post("/auth/me/sync-discord-avatar")
        assert response.status_code == 401

    def test_sync_without_discord_oauth_returns_400(
        self, client: TestClient, auth_headers: dict
    ):
        """Test that user without Discord OAuth gets 400"""
        response = client.post("/auth/me/sync-discord-avatar", headers=auth_headers)
        assert response.status_code == 400
        assert "No Discord account linked" in response.json()["detail"]

    def test_sync_with_expired_token_returns_401(
        self, client: TestClient, user_with_discord: User, db_session: Session
    ):
        """Test that expired Discord token returns 401"""
        token = create_access_token(data={"sub": str(user_with_discord.id)})
        headers = {"Authorization": f"Bearer {token}"}

        with patch("app.users.routes.httpx.AsyncClient") as mock_client:
            mock_response = AsyncMock()
            mock_response.status_code = 401
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )

            response = client.post("/auth/me/sync-discord-avatar", headers=headers)

        assert response.status_code == 401
        assert "Discord token expired" in response.json()["detail"]

    def test_sync_with_discord_api_error_returns_502(
        self, client: TestClient, user_with_discord: User, db_session: Session
    ):
        """Test that Discord API error returns 502"""
        token = create_access_token(data={"sub": str(user_with_discord.id)})
        headers = {"Authorization": f"Bearer {token}"}

        with patch("app.users.routes.httpx.AsyncClient") as mock_client:
            mock_response = AsyncMock()
            mock_response.status_code = 500
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )

            response = client.post("/auth/me/sync-discord-avatar", headers=headers)

        assert response.status_code == 502
        assert "Failed to fetch Discord profile" in response.json()["detail"]

    def test_sync_with_no_avatar_on_discord_returns_404(
        self, client: TestClient, user_with_discord: User, db_session: Session
    ):
        """Test that user without Discord avatar gets 404"""
        token = create_access_token(data={"sub": str(user_with_discord.id)})
        headers = {"Authorization": f"Bearer {token}"}

        with patch("app.users.routes.httpx.AsyncClient") as mock_client:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json = lambda: {
                "id": "123456789012345678",
                "username": "testuser",
                "avatar": None,
            }
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )

            response = client.post("/auth/me/sync-discord-avatar", headers=headers)

        assert response.status_code == 404
        assert "No avatar set on Discord" in response.json()["detail"]

    def test_sync_success_updates_avatar(
        self, client: TestClient, user_with_discord: User, db_session: Session
    ):
        """Test successful Discord avatar sync"""
        token = create_access_token(data={"sub": str(user_with_discord.id)})
        headers = {"Authorization": f"Bearer {token}"}

        with patch("app.users.routes.httpx.AsyncClient") as mock_client:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json = lambda: {
                "id": "123456789012345678",
                "username": "testuser",
                "avatar": "abc123def456",
            }
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )

            response = client.post("/auth/me/sync-discord-avatar", headers=headers)

        assert response.status_code == 200
        expected_url = "https://cdn.discordapp.com/avatars/123456789012345678/abc123def456.png?size=256"
        assert response.json()["avatar_url"] == expected_url

        # Verify user avatar was updated in database
        db_session.expire_all()
        updated_user = db_session.get(User, user_with_discord.id)
        assert updated_user.avatar_url == expected_url

    def test_sync_replaces_old_avatar_url(
        self, client: TestClient, user_with_discord: User, db_session: Session
    ):
        """Test that syncing replaces existing avatar URL"""
        # Set an existing avatar URL
        user_with_discord.avatar_url = "https://example.com/old-avatar.png"
        db_session.add(user_with_discord)
        db_session.commit()

        token = create_access_token(data={"sub": str(user_with_discord.id)})
        headers = {"Authorization": f"Bearer {token}"}

        with patch("app.users.routes.httpx.AsyncClient") as mock_client:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json = lambda: {
                "id": "123456789012345678",
                "username": "testuser",
                "avatar": "newhash789",
            }
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )

            response = client.post("/auth/me/sync-discord-avatar", headers=headers)

        assert response.status_code == 200
        expected_url = "https://cdn.discordapp.com/avatars/123456789012345678/newhash789.png?size=256"
        assert response.json()["avatar_url"] == expected_url

        db_session.expire_all()
        updated_user = db_session.get(User, user_with_discord.id)
        assert updated_user.avatar_url == expected_url
