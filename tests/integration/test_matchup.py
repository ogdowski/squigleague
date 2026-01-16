"""
Integration tests for matchup endpoints.

Tests matchup creation, submission, retrieval, and reveal functionality.
"""
import pytest
import requests
import time
import random

BASE_URL = "http://localhost"


def create_test_user(suffix=""):
    """Helper: Create a test user and return token."""
    timestamp = int(time.time() * 1000) + random.randint(0, 9999)
    response = requests.post(
        f"{BASE_URL}/api/auth/register",
        json={
            "email": f"user{suffix}_{timestamp}@example.com",
            "username": f"user{suffix}_{timestamp}",
            "password": "password123"
        }
    )
    if response.status_code not in (200, 201):
        raise Exception(f"Registration failed: {response.status_code} {response.text}")
    return response.json()["access_token"], f"user{suffix}_{timestamp}"


class TestMatchupCreation:
    """Test suite for matchup creation."""

    def test_create_matchup_authenticated(self):
        """Test authenticated user can create matchup."""
        token, _ = create_test_user("1")
        
        response = requests.post(
            f"{BASE_URL}/api/matchup",
            headers={"Authorization": f"Bearer {token}"},
            json={"army_list": "Test Army\n- 10 Liberators\n- Hero"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "name" in data
        assert "link" in data
        assert "expires_at" in data
    
    def test_create_matchup_anonymous(self):
        """Test anonymous user can create matchup."""
        response = requests.post(
            f"{BASE_URL}/api/matchup",
            json={"army_list": "Anonymous Army\n- 10 Warriors\n- Hero"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "name" in data
    
    def test_create_matchup_short_list(self):
        """Test matchup creation fails with too short army list."""
        token, _ = create_test_user("1")
        
        response = requests.post(
            f"{BASE_URL}/api/matchup",
            headers={"Authorization": f"Bearer {token}"},
            json={"army_list": "Short"}
        )
        
        assert response.status_code == 422


class TestMatchupSubmission:
    """Test suite for army list submission."""

    def test_submit_list_authenticated(self):
        """Test player 2 can submit list when authenticated."""
        p1_token, _ = create_test_user("1")
        p2_token, _ = create_test_user("2")
        
        # Player 1 creates matchup
        response = requests.post(
            f"{BASE_URL}/api/matchup",
            headers={"Authorization": f"Bearer {p1_token}"},
            json={"army_list": "P1 Army\n- 10 Liberators"}
        )
        matchup_name = response.json()["name"]
        
        # Player 2 submits
        response = requests.post(
            f"{BASE_URL}/api/matchup/{matchup_name}/submit",
            headers={"Authorization": f"Bearer {p2_token}"},
            json={"army_list": "P2 Army\n- 20 Stormcast"}
        )
        
        assert response.status_code == 200
        assert response.json()["is_revealed"] == True
    
    def test_submit_list_anonymous(self):
        """Test anonymous player 2 can submit list."""
        p1_token, _ = create_test_user("1")
        
        # Player 1 creates matchup
        response = requests.post(
            f"{BASE_URL}/api/matchup",
            headers={"Authorization": f"Bearer {p1_token}"},
            json={"army_list": "P1 Army\n- 10 Liberators"}
        )
        matchup_name = response.json()["name"]
        
        # Anonymous player 2 submits
        response = requests.post(
            f"{BASE_URL}/api/matchup/{matchup_name}/submit",
            json={"army_list": "P2 Army\n- 20 Stormcast"}
        )
        
        assert response.status_code == 200
    
    def test_submit_to_nonexistent_matchup(self):
        """Test submission fails for non-existent matchup."""
        token, _ = create_test_user("1")
        
        response = requests.post(
            f"{BASE_URL}/api/matchup/nonexistent-matchup-xyz/submit",
            headers={"Authorization": f"Bearer {token}"},
            json={"army_list": "P2 Army\n- 20 Stormcast"}
        )
        
        assert response.status_code == 404


class TestMatchupRetrieval:
    """Test suite for matchup retrieval."""

    def test_get_matchup_status(self):
        """Test retrieving matchup status before reveal."""
        token, _ = create_test_user("1")
        
        # Create matchup
        response = requests.post(
            f"{BASE_URL}/api/matchup",
            headers={"Authorization": f"Bearer {token}"},
            json={"army_list": "P1 Army\n- 10 Liberators"}
        )
        matchup_name = response.json()["name"]
        
        # Get status
        response = requests.get(f"{BASE_URL}/api/matchup/{matchup_name}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == matchup_name
        assert data["player1_submitted"] == True
        assert data["player2_submitted"] == False
        assert data["is_revealed"] == False
    
    def test_get_nonexistent_matchup(self):
        """Test retrieving non-existent matchup returns 404."""
        response = requests.get(f"{BASE_URL}/api/matchup/nonexistent-xyz")
        assert response.status_code == 404
    
    def test_get_my_matchups(self):
        """Test authenticated user can retrieve their matchups."""
        token, _ = create_test_user("1")
        
        # Create matchup
        response = requests.post(
            f"{BASE_URL}/api/matchup",
            headers={"Authorization": f"Bearer {token}"},
            json={"army_list": "P1 Army\n- 10 Liberators"}
        )
        matchup_name = response.json()["name"]
        
        # Get my matchups
        response = requests.get(
            f"{BASE_URL}/api/matchup/my-matchups",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        matchups = response.json()
        assert len(matchups) >= 1
        assert any(m["name"] == matchup_name for m in matchups)
    
    def test_my_matchups_requires_auth(self):
        """Test /my-matchups requires authentication."""
        response = requests.get(f"{BASE_URL}/api/matchup/my-matchups")
        assert response.status_code == 401


class TestMatchupReveal:
    """Test suite for matchup reveal functionality."""

    def test_reveal_complete_matchup(self):
        """Test revealing matchup after both lists submitted."""
        p1_token, _ = create_test_user("1")
        p2_token, _ = create_test_user("2")
        
        # Player 1 creates
        response = requests.post(
            f"{BASE_URL}/api/matchup",
            headers={"Authorization": f"Bearer {p1_token}"},
            json={"army_list": "P1 Army\n- 10 Liberators"}
        )
        matchup_name = response.json()["name"]
        
        # Player 2 submits
        requests.post(
            f"{BASE_URL}/api/matchup/{matchup_name}/submit",
            headers={"Authorization": f"Bearer {p2_token}"},
            json={"army_list": "P2 Army\n- 20 Stormcast"}
        )
        
        # Reveal
        response = requests.get(f"{BASE_URL}/api/matchup/{matchup_name}/reveal")
        
        assert response.status_code == 200
        data = response.json()
        assert "player1_list" in data
        assert "player2_list" in data
        assert "map_name" in data
        assert "revealed_at" in data
    
    def test_reveal_incomplete_matchup(self):
        """Test revealing matchup before both lists submitted fails."""
        token, _ = create_test_user("1")
        
        # Player 1 creates (no player 2 yet)
        response = requests.post(
            f"{BASE_URL}/api/matchup",
            headers={"Authorization": f"Bearer {token}"},
            json={"army_list": "P1 Army\n- 10 Liberators"}
        )
        matchup_name = response.json()["name"]
        
        # Attempt reveal
        response = requests.get(f"{BASE_URL}/api/matchup/{matchup_name}/reveal")
        
        assert response.status_code == 400


class TestPlayerNames:
    """Test suite for player names feature."""

    def test_player_names_in_status(self):
        """Test player usernames appear in matchup status."""
        p1_token, p1_username = create_test_user("1")
        p2_token, p2_username = create_test_user("2")
        
        # Player 1 creates
        response = requests.post(
            f"{BASE_URL}/api/matchup",
            headers={"Authorization": f"Bearer {p1_token}"},
            json={"army_list": "P1 Army\n- 10 Liberators"}
        )
        matchup_name = response.json()["name"]
        
        # Player 2 submits
        requests.post(
            f"{BASE_URL}/api/matchup/{matchup_name}/submit",
            headers={"Authorization": f"Bearer {p2_token}"},
            json={"army_list": "P2 Army\n- 20 Stormcast"}
        )
        
        # Check status
        response = requests.get(f"{BASE_URL}/api/matchup/{matchup_name}")
        data = response.json()
        
        assert data["player1_username"] == p1_username
        assert data["player2_username"] == p2_username
    
    def test_player_names_in_reveal(self):
        """Test player usernames appear in reveal."""
        p1_token, p1_username = create_test_user("1")
        p2_token, p2_username = create_test_user("2")
        
        # Player 1 creates
        response = requests.post(
            f"{BASE_URL}/api/matchup",
            headers={"Authorization": f"Bearer {p1_token}"},
            json={"army_list": "P1 Army\n- 10 Liberators"}
        )
        matchup_name = response.json()["name"]
        
        # Player 2 submits
        requests.post(
            f"{BASE_URL}/api/matchup/{matchup_name}/submit",
            headers={"Authorization": f"Bearer {p2_token}"},
            json={"army_list": "P2 Army\n- 20 Stormcast"}
        )
        
        # Check reveal
        response = requests.get(f"{BASE_URL}/api/matchup/{matchup_name}/reveal")
        data = response.json()
        
        assert data["player1_username"] == p1_username
        assert data["player2_username"] == p2_username
    
    def test_anonymous_player_null_username(self):
        """Test anonymous players have null username."""
        # Anonymous player 1 creates
        response = requests.post(
            f"{BASE_URL}/api/matchup",
            json={"army_list": "P1 Army\n- 10 Liberators"}
        )
        matchup_name = response.json()["name"]
        
        # Check status
        response = requests.get(f"{BASE_URL}/api/matchup/{matchup_name}")
        data = response.json()
        
        assert data["player1_username"] is None
