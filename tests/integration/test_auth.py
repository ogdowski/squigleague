"""
Integration tests for authentication endpoints.

Tests user registration, login, token validation, and session management
through the Docker nginx proxy.
"""
import pytest
import requests
import time

BASE_URL = "http://localhost"


class TestAuthentication:
    """Test suite for authentication functionality."""

    def test_user_registration(self):
        """Test user can register with valid credentials."""
        timestamp = int(time.time())
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "email": f"test_{timestamp}@example.com",
                "username": f"testuser_{timestamp}",
                "password": "password123"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["username"] == f"testuser_{timestamp}"
    
    def test_registration_duplicate_email(self):
        """Test registration fails with duplicate email."""
        timestamp = int(time.time())
        email = f"duplicate_{timestamp}@example.com"
        
        # First registration succeeds
        requests.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "email": email,
                "username": f"user1_{timestamp}",
                "password": "password123"
            }
        )
        
        # Second registration with same email fails
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "email": email,
                "username": f"user2_{timestamp}",
                "password": "password123"
            }
        )
        
        assert response.status_code == 400
    
    def test_registration_short_password(self):
        """Test registration fails with password < 8 characters."""
        timestamp = int(time.time())
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "email": f"test_{timestamp}@example.com",
                "username": f"testuser_{timestamp}",
                "password": "short"
            }
        )
        
        assert response.status_code == 422
    
    def test_user_login(self):
        """Test user can login with valid credentials."""
        timestamp = int(time.time())
        email = f"login_{timestamp}@example.com"
        password = "password123"
        
        # Register user
        requests.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "email": email,
                "username": f"loginuser_{timestamp}",
                "password": password
            }
        )
        
        # Login
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": email, "password": password}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "user" in data
    
    def test_login_wrong_password(self):
        """Test login fails with incorrect password."""
        timestamp = int(time.time())
        email = f"wrongpass_{timestamp}@example.com"
        
        # Register user
        requests.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "email": email,
                "username": f"user_{timestamp}",
                "password": "correctpassword"
            }
        )
        
        # Login with wrong password
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": email, "password": "wrongpassword"}
        )
        
        assert response.status_code == 401
    
    def test_login_nonexistent_user(self):
        """Test login fails for non-existent user."""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "password123"
            }
        )
        
        assert response.status_code == 401
    
    def test_token_authentication(self):
        """Test protected endpoint accepts valid token."""
        timestamp = int(time.time())
        
        # Register and get token
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "email": f"token_{timestamp}@example.com",
                "username": f"tokenuser_{timestamp}",
                "password": "password123"
            }
        )
        token = response.json()["access_token"]
        
        # Access protected endpoint
        response = requests.get(
            f"{BASE_URL}/api/matchup/my-matchups",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
    
    def test_protected_endpoint_no_token(self):
        """Test protected endpoint rejects request without token."""
        response = requests.get(f"{BASE_URL}/api/matchup/my-matchups")
        assert response.status_code == 401
    
    def test_protected_endpoint_invalid_token(self):
        """Test protected endpoint rejects invalid token."""
        response = requests.get(
            f"{BASE_URL}/api/matchup/my-matchups",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401
    
    def test_get_current_user(self):
        """Test /auth/me endpoint returns current user info."""
        timestamp = int(time.time())
        username = f"meuser_{timestamp}"
        
        # Register and get token
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "email": f"me_{timestamp}@example.com",
                "username": username,
                "password": "password123"
            }
        )
        token = response.json()["access_token"]
        
        # Get current user
        response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == username
