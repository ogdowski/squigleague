"""
Integration Tests for Authentication + Matchup System

Tests the complete flow:
1. User registration (with mocked email)
2. Email verification (MOCKED - one-time exception for test truthfulness)
3. Login and token retrieval
4. Matchup creation (requires auth)
5. Matchup submission and battle plan generation

EMAIL MOCKING EXCEPTION:
The email verification link is mocked because real email requires
external SMTP credentials. This is the ONE exception to test truthfulness.
All other functionality is tested against real backend code.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import uuid

from herald.main import app
from squire.database import get_session, User, EmailVerificationToken


@pytest.fixture
def client():
    """Create test client"""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def mock_email_service():
    """Mock email sending to avoid requiring SMTP credentials"""
    with patch('squire.auth.send_verification_email') as mock_send:
        mock_send.return_value = True
        yield mock_send


@pytest.fixture
def registered_user(client, mock_email_service):
    """Create and return a registered user with mocked verification"""
    # Register user
    username = f"testuser_{uuid.uuid4().hex[:8]}"
    email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    password = "testpass123"
    
    response = client.post(
        "/api/squire/auth/register",
        json={
            "username": username,
            "email": email,
            "password": password
        }
    )
    
    assert response.status_code == 200
    user_data = response.json()
    user_id = user_data["user_id"]
    
    # MOCKED: Manually verify email (simulating clicking verification link)
    # In production, user would click link from email
    db = get_session()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        user.email_verified = True
        db.commit()
    finally:
        db.close()
    
    return {
        "user_id": user_id,
        "username": username,
        "email": email,
        "password": password
    }


@pytest.fixture
def auth_token(registered_user):
    """Get authentication token for registered user"""
    response = client.post(
        "/api/squire/auth/login",
        json={
            "username_or_email": registered_user["username"],
            "password": registered_user["password"]
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    return data["token"]


class TestRegistrationFlow:
    """Test user registration"""
    
    def test_register_new_user_success(self, client, mock_email_service):
        """Test successful user registration"""
        response = client.post(
            "/api/squire/auth/register",
            json={
                "username": f"newuser_{uuid.uuid4().hex[:8]}",
                "email": f"new_{uuid.uuid4().hex[:8]}@example.com",
                "password": "password123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert "username" in data
        assert "email" in data
        assert "message" in data
        
        # Verify email was "sent" (mocked)
        mock_email_service.assert_called_once()
    
    def test_register_duplicate_username_fails(self, client, mock_email_service):
        """Test registration fails with duplicate username"""
        username = f"dupuser_{uuid.uuid4().hex[:8]}"
        
        # First registration
        client.post(
            "/api/squire/auth/register",
            json={
                "username": username,
                "email": f"user1_{uuid.uuid4().hex[:8]}@example.com",
                "password": "password123"
            }
        )
        
        # Duplicate username
        response = client.post(
            "/api/squire/auth/register",
            json={
                "username": username,
                "email": f"user2_{uuid.uuid4().hex[:8]}@example.com",
                "password": "password123"
            }
        )
        
        assert response.status_code == 400
        assert "username" in response.json()["detail"].lower()
    
    def test_register_password_too_short_fails(self, client, mock_email_service):
        """Test registration fails with short password"""
        response = client.post(
            "/api/squire/auth/register",
            json={
                "username": f"user_{uuid.uuid4().hex[:8]}",
                "email": f"test_{uuid.uuid4().hex[:8]}@example.com",
                "password": "short"
            }
        )
        
        assert response.status_code == 422  # Validation error


class TestLoginFlow:
    """Test user login"""
    
    def test_login_with_verified_email_success(self, client, registered_user):
        """Test login succeeds with verified email"""
        response = client.post(
            "/api/squire/auth/login",
            json={
                "username_or_email": registered_user["username"],
                "password": registered_user["password"]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user_id" in data
        assert "username" in data
        assert "expires_at" in data
        assert len(data["token"]) > 0
    
    def test_login_with_email_address(self, client, registered_user):
        """Test login with email address instead of username"""
        response = client.post(
            "/api/squire/auth/login",
            json={
                "username_or_email": registered_user["email"],
                "password": registered_user["password"]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
    
    def test_login_wrong_password_fails(self, client, registered_user):
        """Test login fails with wrong password"""
        response = client.post(
            "/api/squire/auth/login",
            json={
                "username_or_email": registered_user["username"],
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == 401
    
    def test_login_nonexistent_user_fails(self, client):
        """Test login fails for nonexistent user"""
        response = client.post(
            "/api/squire/auth/login",
            json={
                "username_or_email": "nonexistent_user",
                "password": "password123"
            }
        )
        
        assert response.status_code == 401


class TestAuthenticatedEndpoints:
    """Test endpoints that require authentication"""
    
    def test_get_current_user_with_valid_token(self, client, auth_token, registered_user):
        """Test /auth/me endpoint with valid token"""
        response = client.get(
            "/api/squire/auth/me",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == registered_user["username"]
        assert data["email"] == registered_user["email"]
        assert data["email_verified"] is True
    
    def test_get_current_user_without_token_fails(self, client):
        """Test /auth/me endpoint fails without token"""
        response = client.get("/api/squire/auth/me")
        
        assert response.status_code == 401
    
    def test_get_current_user_with_invalid_token_fails(self, client):
        """Test /auth/me endpoint fails with invalid token"""
        response = client.get(
            "/api/squire/auth/me",
            headers={"Authorization": "Bearer invalid_token_here"}
        )
        
        assert response.status_code == 401


class TestMatchupWithAuthentication:
    """Test matchup system with authentication requirements"""
    
    def test_create_matchup_with_auth_success(self, client, auth_token):
        """Test matchup creation succeeds with valid auth token"""
        response = client.post(
            "/api/squire/matchup/create",
            json={"game_system": "age_of_sigmar"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "matchup_id" in data
        assert data["game_system"] == "age_of_sigmar"
        assert "share_url" in data
    
    def test_create_matchup_without_auth_fails(self, client):
        """Test matchup creation fails without auth token"""
        response = client.post(
            "/api/squire/matchup/create",
            json={"game_system": "age_of_sigmar"}
        )
        
        assert response.status_code == 401
    
    def test_create_matchup_with_invalid_token_fails(self, client):
        """Test matchup creation fails with invalid token"""
        response = client.post(
            "/api/squire/matchup/create",
            json={"game_system": "age_of_sigmar"},
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == 401
    
    def test_complete_matchup_flow_with_auth(self, client, auth_token):
        """Test complete matchup flow: create, submit, reveal"""
        # Create matchup
        create_response = client.post(
            "/api/squire/matchup/create",
            json={"game_system": "warhammer_40k"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert create_response.status_code == 200
        matchup_id = create_response.json()["matchup_id"]
        
        # First player submits
        submit1_response = client.post(
            f"/api/squire/matchup/{matchup_id}/submit",
            json={
                "player_name": "Player 1",
                "army_list": "Army List 1\nUnit A\nUnit B"
            }
        )
        assert submit1_response.status_code == 200
        data1 = submit1_response.json()
        assert data1["is_complete"] is False
        assert data1["battle_plan"] is None
        
        # Second player submits
        submit2_response = client.post(
            f"/api/squire/matchup/{matchup_id}/submit",
            json={
                "player_name": "Player 2",
                "army_list": "Army List 2\nUnit X\nUnit Y"
            }
        )
        assert submit2_response.status_code == 200
        data2 = submit2_response.json()
        assert data2["is_complete"] is True
        assert data2["battle_plan"] is not None
        assert data2["battle_plan"]["game_system"] == "warhammer_40k"
        assert "deployment" in data2["battle_plan"]
        assert "primary_objective" in data2["battle_plan"]


class TestMatchupSubmission:
    """Test matchup list submission (no auth required for submission)"""
    
    def test_submit_to_nonexistent_matchup_fails(self, client):
        """Test submission to nonexistent matchup fails"""
        response = client.post(
            "/api/squire/matchup/nonexistent_id/submit",
            json={
                "player_name": "Player",
                "army_list": "Army"
            }
        )
        
        assert response.status_code == 404
    
    def test_submit_third_player_fails(self, client, auth_token):
        """Test that third player cannot submit to full matchup"""
        # Create matchup
        create_response = client.post(
            "/api/squire/matchup/create",
            json={"game_system": "age_of_sigmar"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        matchup_id = create_response.json()["matchup_id"]
        
        # Player 1 submits
        client.post(
            f"/api/squire/matchup/{matchup_id}/submit",
            json={"player_name": "Player 1", "army_list": "Army 1"}
        )
        
        # Player 2 submits
        client.post(
            f"/api/squire/matchup/{matchup_id}/submit",
            json={"player_name": "Player 2", "army_list": "Army 2"}
        )
        
        # Player 3 tries to submit
        response = client.post(
            f"/api/squire/matchup/{matchup_id}/submit",
            json={"player_name": "Player 3", "army_list": "Army 3"}
        )
        
        # Should fail - matchup already full
        assert response.status_code == 400 or response.status_code == 422


class TestBattlePlanGeneration:
    """Test battle plan generation logic"""
    
    def test_battle_plan_random_endpoint(self, client):
        """Test random battle plan generation endpoint"""
        response = client.get("/api/squire/battle-plan/random?system=age_of_sigmar")
        
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "deployment" in data
        assert "primary_objective" in data
        assert data["game_system"] == "age_of_sigmar"
    
    def test_battle_plan_different_systems(self, client):
        """Test battle plans for different game systems"""
        systems = ["age_of_sigmar", "warhammer_40k", "the_old_world"]
        
        for system in systems:
            response = client.get(f"/api/squire/battle-plan/random?system={system}")
            assert response.status_code == 200
            data = response.json()
            assert data["game_system"] == system


