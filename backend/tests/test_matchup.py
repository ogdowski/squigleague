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


class TestMatchupFactionHiding:
    """Test that army factions are hidden before reveal"""

    def test_faction_hidden_before_reveal(self, client: TestClient, session: Session):
        """Test that faction is not returned before both players submit"""
        # Create matchup with faction
        response = client.post(
            "/matchup",
            json={
                "army_list": "Stormcast Eternals army list here",
                "army_faction": "Stormcast Eternals",
            },
        )
        assert response.status_code == 201
        matchup_name = response.json()["name"]

        # Get status - faction should be hidden
        status_response = client.get(f"/matchup/{matchup_name}")
        assert status_response.status_code == 200
        data = status_response.json()
        assert data["player1_army_faction"] is None
        assert data["player2_army_faction"] is None
        assert data["is_revealed"] is False

    def test_faction_shown_after_reveal(self, client: TestClient, session: Session):
        """Test that faction is shown after both players submit"""
        # Create matchup
        response = client.post(
            "/matchup",
            json={
                "army_list": "Stormcast Eternals army list here",
                "army_faction": "Stormcast Eternals",
            },
        )
        matchup_name = response.json()["name"]

        # Submit player 2's list
        client.post(
            f"/matchup/{matchup_name}/submit",
            json={
                "army_list": "Gloomspite Gitz army list here",
                "army_faction": "Gloomspite Gitz",
            },
        )

        # Get status - factions should be visible
        status_response = client.get(f"/matchup/{matchup_name}")
        data = status_response.json()
        assert data["is_revealed"] is True
        assert data["player1_army_faction"] == "Stormcast Eternals"
        assert data["player2_army_faction"] == "Gloomspite Gitz"


class TestMatchupTitleUpdate:
    """Test matchup title update endpoint"""

    def test_update_title_as_participant(
        self, client: TestClient, session: Session, test_user, auth_headers
    ):
        """Test that participant can update title"""
        # Create matchup as authenticated user
        response = client.post(
            "/matchup",
            json={"army_list": "Test army list here"},
            headers=auth_headers,
        )
        matchup_name = response.json()["name"]

        # Update title
        update_response = client.patch(
            f"/matchup/{matchup_name}/title",
            json={"title": "Epic Battle"},
            headers=auth_headers,
        )
        assert update_response.status_code == 200
        assert update_response.json()["title"] == "Epic Battle"

        # Verify in status
        status_response = client.get(f"/matchup/{matchup_name}")
        assert status_response.json()["title"] == "Epic Battle"

    def test_update_title_clear(
        self, client: TestClient, session: Session, test_user, auth_headers
    ):
        """Test that title can be cleared"""
        response = client.post(
            "/matchup",
            json={"army_list": "Test army list here", "title": "Original Title"},
            headers=auth_headers,
        )
        matchup_name = response.json()["name"]

        # Clear title
        update_response = client.patch(
            f"/matchup/{matchup_name}/title",
            json={"title": None},
            headers=auth_headers,
        )
        assert update_response.status_code == 200
        assert update_response.json()["title"] is None

    def test_update_title_not_participant(
        self, client: TestClient, session: Session, test_user, auth_headers
    ):
        """Test that non-participant cannot update title"""
        # Create matchup anonymously
        response = client.post(
            "/matchup",
            json={"army_list": "Test army list here"},
        )
        matchup_name = response.json()["name"]

        # Try to update as different user
        update_response = client.patch(
            f"/matchup/{matchup_name}/title",
            json={"title": "Hacked Title"},
            headers=auth_headers,
        )
        assert update_response.status_code == 403

    def test_update_title_after_confirmed_fails(
        self, client: TestClient, session: Session, test_user, auth_headers
    ):
        """Test that title cannot be updated after result confirmed"""
        # Create revealed matchup with confirmed result
        matchup = Matchup(
            name="test-title-confirmed",
            player1_id=test_user.id,
            player1_submitted=True,
            player2_submitted=True,
            player1_list="List 1",
            player2_list="List 2",
            map_name="Test Map",
            result_status="confirmed",
            player1_score=70,
            player2_score=60,
        )
        session.add(matchup)
        session.commit()

        update_response = client.patch(
            "/matchup/test-title-confirmed/title",
            json={"title": "New Title"},
            headers=auth_headers,
        )
        assert update_response.status_code == 400
        assert "confirmed" in update_response.json()["detail"].lower()


class TestMatchupPublicToggle:
    """Test matchup public toggle restrictions"""

    def test_toggle_public_as_participant(
        self, client: TestClient, session: Session, test_user, auth_headers
    ):
        """Test that participant can toggle public visibility"""
        response = client.post(
            "/matchup",
            json={"army_list": "Test army list here", "is_public": True},
            headers=auth_headers,
        )
        matchup_name = response.json()["name"]

        # Toggle to private
        toggle_response = client.patch(
            f"/matchup/{matchup_name}/public",
            json={"is_public": False},
            headers=auth_headers,
        )
        assert toggle_response.status_code == 200
        assert toggle_response.json()["is_public"] is False

    def test_toggle_public_after_confirmed_works(
        self, client: TestClient, session: Session, test_user, auth_headers
    ):
        """Test that public can be toggled even after result confirmed"""
        matchup = Matchup(
            name="test-public-confirmed",
            player1_id=test_user.id,
            player1_submitted=True,
            player2_submitted=True,
            player1_list="List 1",
            player2_list="List 2",
            map_name="Test Map",
            result_status="confirmed",
            player1_score=70,
            player2_score=60,
            is_public=True,
        )
        session.add(matchup)
        session.commit()

        toggle_response = client.patch(
            "/matchup/test-public-confirmed/public",
            json={"is_public": False},
            headers=auth_headers,
        )
        assert toggle_response.status_code == 200
        assert toggle_response.json()["is_public"] is False


class TestMatchupSubmitRestrictions:
    """Test that assigned opponents block others from submitting"""

    def test_assigned_opponent_blocks_anonymous(
        self, client: TestClient, session: Session, test_user, auth_headers
    ):
        """Test that anonymous users cannot submit when player2 is assigned"""
        # Create matchup with assigned player2
        response = client.post(
            "/matchup",
            json={"army_list": "Test army list here"},
            headers=auth_headers,
        )
        matchup_name = response.json()["name"]

        # Manually assign player2 to a different user
        matchup = session.scalars(
            select(Matchup).where(Matchup.name == matchup_name)
        ).first()
        matchup.player2_id = 999  # Some other user ID
        session.add(matchup)
        session.commit()

        # Try to submit as anonymous - should fail
        submit_response = client.post(
            f"/matchup/{matchup_name}/submit",
            json={"army_list": "Anonymous list"},
        )
        assert submit_response.status_code == 403
        assert "assigned opponent" in submit_response.json()["detail"].lower()


class TestMatchupCancellation:
    """Test matchup cancellation"""

    def test_cancel_matchup_as_creator(
        self, client: TestClient, session: Session, test_user, auth_headers
    ):
        """Test that player1 can cancel before player2 submits"""
        response = client.post(
            "/matchup",
            json={"army_list": "Test army list here"},
            headers=auth_headers,
        )
        matchup_name = response.json()["name"]

        # Cancel the matchup
        cancel_response = client.post(
            f"/matchup/{matchup_name}/cancel",
            headers=auth_headers,
        )
        assert cancel_response.status_code == 200

        # Verify it's cancelled
        status_response = client.get(f"/matchup/{matchup_name}")
        assert status_response.json()["is_cancelled"] is True

    def test_cannot_cancel_after_player2_submits(
        self, client: TestClient, session: Session, test_user, auth_headers
    ):
        """Test that player1 cannot cancel after player2 has submitted"""
        response = client.post(
            "/matchup",
            json={"army_list": "Test army list here"},
            headers=auth_headers,
        )
        matchup_name = response.json()["name"]

        # Player2 submits
        client.post(
            f"/matchup/{matchup_name}/submit",
            json={"army_list": "Player 2 list"},
        )

        # Try to cancel - should fail
        cancel_response = client.post(
            f"/matchup/{matchup_name}/cancel",
            headers=auth_headers,
        )
        assert cancel_response.status_code == 400
        assert "opponent has submitted" in cancel_response.json()["detail"].lower()

    def test_cannot_submit_to_cancelled_matchup(
        self, client: TestClient, session: Session, test_user, auth_headers
    ):
        """Test that nobody can submit to a cancelled matchup"""
        response = client.post(
            "/matchup",
            json={"army_list": "Test army list here"},
            headers=auth_headers,
        )
        matchup_name = response.json()["name"]

        # Cancel it
        client.post(f"/matchup/{matchup_name}/cancel", headers=auth_headers)

        # Try to submit - should fail
        submit_response = client.post(
            f"/matchup/{matchup_name}/submit",
            json={"army_list": "Too late list"},
        )
        assert submit_response.status_code == 400
        assert "cancelled" in submit_response.json()["detail"].lower()


class TestStatsEndpoint:
    """Test statistics endpoint"""

    def test_get_stats(self, client: TestClient):
        """Test getting platform statistics"""
        response = client.get("/matchup/stats")
        assert response.status_code == 200
        data = response.json()
        assert "exchanges_completed" in data
        assert "version" in data
        # Version is dynamic, just check it's a string
        assert isinstance(data["version"], str)
        assert isinstance(data["exchanges_completed"], int)
