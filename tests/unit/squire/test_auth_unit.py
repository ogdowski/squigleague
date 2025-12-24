"""
Comprehensive Unit Tests for Authentication System

Tests password validation, JWT token generation, and business logic.
Mocks database and email sending.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import uuid
import bcrypt
from jose import jwt

from squire.auth import (
    hash_password,
    verify_password,
    create_jwt_token,
    decode_jwt_token,
    RegisterRequest,
    LoginRequest
)


class TestPasswordHashing:
    """Test password hashing and verification"""
    
    def test_hash_password_creates_valid_hash(self):
        """Test that password hashing produces valid bcrypt hash"""
        password = "testpassword123"
        hashed = hash_password(password)
        
        assert hashed is not None
        assert isinstance(hashed, str)
        assert len(hashed) > 0
        assert hashed != password  # Hash should not equal plaintext
        assert hashed.startswith("$2b$")  # bcrypt format
    
    def test_hash_password_different_each_time(self):
        """Test that same password produces different hashes (salt)"""
        password = "testpassword123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        assert hash1 != hash2  # Different salts
    
    def test_verify_password_correct(self):
        """Test password verification with correct password"""
        password = "testpassword123"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password"""
        password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed = hash_password(password)
        
        assert verify_password(wrong_password, hashed) is False
    
    def test_verify_password_empty(self):
        """Test password verification with empty password"""
        password = "testpassword123"
        hashed = hash_password(password)
        
        assert verify_password("", hashed) is False


class TestJWTTokens:
    """Test JWT token creation and verification"""
    
    def test_create_jwt_token(self):
        """Test JWT token creation"""
        user_id = str(uuid.uuid4())
        username = "testuser"
        email = "test@example.com"
        
        token, expires_at = create_jwt_token(user_id, username, email)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
        assert isinstance(expires_at, datetime)
    
    def test_decode_jwt_token_valid(self):
        """Test decoding of valid JWT token"""
        user_id = str(uuid.uuid4())
        username = "testuser"
        email = "test@example.com"
        
        token, _ = create_jwt_token(user_id, username, email)
        payload = decode_jwt_token(token)
        
        assert payload is not None
        assert payload["user_id"] == user_id
        assert payload["username"] == username
        assert payload["email"] == email
        assert "exp" in payload
    
    def test_decode_jwt_token_invalid(self):
        """Test decoding of malformed JWT token"""
        invalid_token = "invalid.token.here"
        payload = decode_jwt_token(invalid_token)
        
        assert payload is None


class TestPasswordValidation:
    """Test password validation rules"""
    
    def test_valid_password_simple(self):
        """Test that simple passwords are accepted (no special char required)"""
        request = RegisterRequest(
            username="testuser",
            email="test@example.com",
            password="password123"  # No special characters
        )
        assert request.password == "password123"
    
    def test_valid_password_with_special_chars(self):
        """Test that passwords with special chars are accepted"""
        request = RegisterRequest(
            username="testuser",
            email="test@example.com",
            password="password123!"
        )
        assert request.password == "password123!"
    
    def test_invalid_password_too_short(self):
        """Test that short passwords are rejected"""
        with pytest.raises(ValueError, match="at least 8 characters"):
            RegisterRequest(
                username="testuser",
                email="test@example.com",
                password="short"
            )
    
    def test_invalid_password_empty(self):
        """Test that empty passwords are rejected"""
        with pytest.raises(ValueError):
            RegisterRequest(
                username="testuser",
                email="test@example.com",
                password=""
            )


class TestUsernameValidation:
    """Test username validation rules"""
    
    def test_valid_username_alphanumeric(self):
        """Test that alphanumeric usernames are accepted"""
        request = RegisterRequest(
            username="testuser123",
            email="test@example.com",
            password="password123"
        )
        assert request.username == "testuser123"
    
    def test_valid_username_with_underscore(self):
        """Test that usernames with underscores are accepted"""
        request = RegisterRequest(
            username="test_user",
            email="test@example.com",
            password="password123"
        )
        assert request.username == "test_user"
    
    def test_invalid_username_special_chars(self):
        """Test that usernames with special characters are rejected"""
        with pytest.raises(ValueError, match="letters, numbers, and underscores"):
            RegisterRequest(
                username="test@user",
                email="test@example.com",
                password="password123"
            )
    
    def test_invalid_username_too_short(self):
        """Test that usernames under 3 chars are rejected"""
        with pytest.raises(ValueError):
            RegisterRequest(
                username="ab",
                email="test@example.com",
                password="password123"
            )
    
    def test_invalid_username_too_long(self):
        """Test that usernames over 20 chars are rejected"""
        with pytest.raises(ValueError):
            RegisterRequest(
                username="a" * 21,
                email="test@example.com",
                password="password123"
            )
    
    def test_username_lowercase_conversion(self):
        """Test that usernames are converted to lowercase"""
        request = RegisterRequest(
            username="TestUser",
            email="test@example.com",
            password="password123"
        )
        assert request.username == "testuser"


class TestEmailValidation:
    """Test email validation"""
    
    def test_valid_email(self):
        """Test that valid emails are accepted"""
        request = RegisterRequest(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        assert request.email == "test@example.com"
    
    def test_invalid_email_no_at(self):
        """Test that emails without @ are rejected"""
        with pytest.raises(ValueError):
            RegisterRequest(
                username="testuser",
                email="testexample.com",
                password="password123"
            )
    
    def test_invalid_email_no_domain(self):
        """Test that emails without domain are rejected"""
        with pytest.raises(ValueError):
            RegisterRequest(
                username="testuser",
                email="test@",
                password="password123"
            )
