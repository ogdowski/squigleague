"""Tests for matchup module"""

import pytest
from app.matchup.models import Matchup
from fastapi.testclient import TestClient
from sqlmodel import Session, select


class TestMatchupCreation:
    """Test matchup creation endpoint"""

    def test_create_matchup_anonymous(self, client: TestClient, session: Session):
        """Test creating a matchup without authentication"""
        response = client.post(
            "/matchup",
            json={
                "army_list": "My awesome Gloomspite Gitz army\n- 20 Stabbas\n- 3 Fanatics"
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert "name" in data
        assert "link" in data
        assert "expires_at" in data
        assert data["link"].startswith("/matchup/")

        # Verify in database
        matchup_name = data["name"]
        statement = select(Matchup).where(Matchup.name == matchup_name)
        matchup = session.exec(statement).first()
        assert matchup is not None
        assert matchup.player1_submitted is True
        assert matchup.player2_submitted is False
        assert (
            matchup.player1_list
            == "My awesome Gloomspite Gitz army\n- 20 Stabbas\n- 3 Fanatics"
        )
        assert matchup.map_name is None

    def test_matchup_name_format(self, client: TestClient):
        """Test that matchup names follow the expected format"""
        response = client.post(
            "/matchup",
            json={"army_list": "Test army list with at least 10 characters"},
        )

        assert response.status_code == 201
        name = response.json()["name"]
        parts = name.split("-")
        assert len(parts) == 3
        assert len(parts[2]) == 4


class TestMatchupStatus:
    """Test matchup status endpoint"""

    def test_get_matchup_status_one_submitted(self, client: TestClient):
        """Test getting status when only player 1 has submitted"""
        create_response = client.post(
            "/matchup",
            json={"army_list": "Player 1 list"},
        )
        matchup_name = create_response.json()["name"]

        response = client.get(f"/matchup/{matchup_name}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == matchup_name
        assert data["player1_submitted"] is True
        assert data["player2_submitted"] is False
        assert data["is_revealed"] is False

    def test_get_nonexistent_matchup(self, client: TestClient):
        """Test getting a matchup that doesn't exist"""
        response = client.get("/matchup/nonexistent-matchup-name")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestStatsEndpoint:
    """Test statistics endpoint"""

    def test_get_stats(self, client: TestClient):
        """Test getting platform statistics"""
        response = client.get("/matchup/stats")
        assert response.status_code == 200
        data = response.json()
        assert "exchanges_completed" in data
        assert "exchanges_expired" in data
        assert "version" in data
        assert data["version"] == "0.3.0"
        assert isinstance(data["exchanges_completed"], int)
        assert isinstance(data["exchanges_expired"], int)
