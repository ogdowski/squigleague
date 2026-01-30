"""Tests for feature toggles and rules access guard."""

from datetime import datetime

import pytest
from app.core.security import create_access_token, get_password_hash
from app.league.models import AppSettings
from app.users.models import User
from sqlmodel import Session, select


def _create_admin(session: Session) -> User:
    """Create an admin user for testing."""
    admin = User(
        email="admin@test.com",
        username="TestAdmin",
        hashed_password=get_password_hash("AdminPass123"),
        role="admin",
        is_active=True,
        is_verified=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    session.add(admin)
    session.commit()
    session.refresh(admin)
    return admin


def _get_auth_headers(user: User) -> dict:
    """Generate JWT auth headers for a user."""
    token = create_access_token(data={"sub": str(user.id)})
    return {"Authorization": f"Bearer {token}"}


def _set_rules_enabled(session: Session, enabled: bool) -> None:
    """Set rules_enabled in AppSettings."""
    statement = select(AppSettings).where(AppSettings.key == "rules_enabled")
    setting = session.scalars(statement).first()
    if setting:
        setting.value = str(enabled).lower()
        setting.updated_at = datetime.utcnow()
    else:
        setting = AppSettings(key="rules_enabled", value=str(enabled).lower())
    session.add(setting)
    session.commit()


class TestGetFeatureToggles:
    """GET /admin/settings/features - public endpoint."""

    def test_returns_false_by_default(self, client):
        """When no setting exists, rules_enabled defaults to false."""
        response = client.get("/admin/settings/features")
        assert response.status_code == 200
        assert response.json() == {"rules_enabled": False}

    def test_returns_true_when_enabled(self, client, session):
        """When rules_enabled is set to true, returns true."""
        _set_rules_enabled(session, True)
        response = client.get("/admin/settings/features")
        assert response.status_code == 200
        assert response.json() == {"rules_enabled": True}

    def test_returns_false_when_disabled(self, client, session):
        """When rules_enabled is explicitly set to false, returns false."""
        _set_rules_enabled(session, False)
        response = client.get("/admin/settings/features")
        assert response.status_code == 200
        assert response.json() == {"rules_enabled": False}


class TestUpdateFeatureToggles:
    """PATCH /admin/settings/features - admin only."""

    def test_admin_can_enable_rules(self, client, session):
        """Admin can set rules_enabled to true."""
        admin = _create_admin(session)
        headers = _get_auth_headers(admin)

        response = client.patch(
            "/admin/settings/features",
            json={"rules_enabled": True},
            headers=headers,
        )
        assert response.status_code == 200
        assert response.json() == {"rules_enabled": True}

        # Verify persisted
        setting = session.scalars(
            select(AppSettings).where(AppSettings.key == "rules_enabled")
        ).first()
        assert setting is not None
        assert setting.value == "true"

    def test_admin_can_disable_rules(self, client, session):
        """Admin can set rules_enabled to false."""
        admin = _create_admin(session)
        headers = _get_auth_headers(admin)
        _set_rules_enabled(session, True)

        response = client.patch(
            "/admin/settings/features",
            json={"rules_enabled": False},
            headers=headers,
        )
        assert response.status_code == 200
        assert response.json() == {"rules_enabled": False}

    def test_player_cannot_update(self, client, session, test_user):
        """Regular player gets 403 when trying to update feature toggles."""
        headers = _get_auth_headers(test_user)

        response = client.patch(
            "/admin/settings/features",
            json={"rules_enabled": True},
            headers=headers,
        )
        assert response.status_code == 403

    def test_unauthenticated_cannot_update(self, client):
        """Unauthenticated request gets 401."""
        response = client.patch(
            "/admin/settings/features",
            json={"rules_enabled": True},
        )
        assert response.status_code == 401


class TestBsdataRulesGuard:
    """BSData endpoints blocked when rules disabled, admin always passes."""

    def test_player_blocked_when_rules_disabled(self, client, session, test_user):
        """Player gets 403 on bsdata endpoints when rules are disabled."""
        headers = _get_auth_headers(test_user)
        # rules_enabled not set = disabled by default

        response = client.get("/bsdata/grand-alliances", headers=headers)
        assert response.status_code == 403
        assert response.json()["detail"] == "Rules feature is disabled"

    def test_player_allowed_when_rules_enabled(self, client, session, test_user):
        """Player can access bsdata endpoints when rules are enabled."""
        headers = _get_auth_headers(test_user)
        _set_rules_enabled(session, True)

        response = client.get("/bsdata/grand-alliances", headers=headers)
        assert response.status_code == 200

    def test_admin_always_allowed_when_disabled(self, client, session):
        """Admin can access bsdata endpoints even when rules are disabled."""
        admin = _create_admin(session)
        headers = _get_auth_headers(admin)
        # rules_enabled not set = disabled

        response = client.get("/bsdata/grand-alliances", headers=headers)
        assert response.status_code == 200

    def test_admin_always_allowed_when_enabled(self, client, session):
        """Admin can access bsdata endpoints when rules are enabled."""
        admin = _create_admin(session)
        headers = _get_auth_headers(admin)
        _set_rules_enabled(session, True)

        response = client.get("/bsdata/grand-alliances", headers=headers)
        assert response.status_code == 200

    def test_unauthenticated_blocked(self, client):
        """Unauthenticated request gets 401 on bsdata endpoints."""
        response = client.get("/bsdata/grand-alliances")
        assert response.status_code == 401

    def test_multiple_endpoints_blocked(self, client, session, test_user):
        """Multiple bsdata endpoints are all blocked when rules disabled."""
        headers = _get_auth_headers(test_user)

        endpoints = [
            "/bsdata/grand-alliances",
            "/bsdata/factions",
            "/bsdata/battle-tactics",
            "/bsdata/core-abilities",
            "/bsdata/regiments-of-renown",
            "/bsdata/spell-lores",
            "/bsdata/status",
        ]
        for endpoint in endpoints:
            response = client.get(endpoint, headers=headers)
            assert response.status_code == 403, f"{endpoint} should be blocked"

    def test_multiple_endpoints_allowed(self, client, session, test_user):
        """Multiple bsdata endpoints are all accessible when rules enabled."""
        headers = _get_auth_headers(test_user)
        _set_rules_enabled(session, True)

        endpoints = [
            "/bsdata/grand-alliances",
            "/bsdata/factions",
            "/bsdata/battle-tactics",
            "/bsdata/core-abilities",
            "/bsdata/regiments-of-renown",
            "/bsdata/spell-lores",
            "/bsdata/status",
        ]
        for endpoint in endpoints:
            response = client.get(endpoint, headers=headers)
            assert response.status_code == 200, f"{endpoint} should be accessible"
