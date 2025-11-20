"""
Unit tests for herald/models.py - Pydantic validation models

Tests input validation for API request/response models.
"""

import pytest
from pydantic import ValidationError
from herald.models import (
    CreateExchangeRequest,
    RespondExchangeRequest,
    CreateExchangeResponse,
    ExchangeStatusResponse,
    HealthCheckResponse,
    ResourcesResponse
)


class TestCreateExchangeRequest:
    """Tests for CreateExchangeRequest model"""
    
    def test_valid_request__accepts_normal_list(self):
        """Test that valid army list is accepted"""
        request = CreateExchangeRequest(
            list_content="Test Army List\n1000 points\nSpace Marines"
        )
        
        assert request.list_content == "Test Army List\n1000 points\nSpace Marines"
    
    def test_valid_request__strips_whitespace(self):
        """Test that leading/trailing whitespace is stripped"""
        request = CreateExchangeRequest(
            list_content="  Test Army List  \n\n"
        )
        
        assert request.list_content == "Test Army List"
    
    def test_invalid_request__empty_string_rejected(self):
        """Test that empty string is rejected"""
        with pytest.raises(ValidationError) as exc_info:
            CreateExchangeRequest(list_content="")
        
        errors = exc_info.value.errors()
        assert len(errors) > 0
        assert any("empty" in str(err).lower() for err in errors)
    
    def test_invalid_request__whitespace_only_rejected(self):
        """Test that whitespace-only string is rejected"""
        with pytest.raises(ValidationError) as exc_info:
            CreateExchangeRequest(list_content="   \n\n\t  ")
        
        errors = exc_info.value.errors()
        assert len(errors) > 0
    
    def test_invalid_request__missing_field_rejected(self):
        """Test that missing list_content field is rejected"""
        with pytest.raises(ValidationError) as exc_info:
            CreateExchangeRequest()
        
        errors = exc_info.value.errors()
        assert len(errors) > 0
        assert any(err['loc'] == ('list_content',) for err in errors)
    
    def test_invalid_request__exceeds_max_length_rejected(self):
        """Test that content over 50k characters is rejected"""
        huge_list = "X" * 50001  # 50,001 characters
        
        with pytest.raises(ValidationError) as exc_info:
            CreateExchangeRequest(list_content=huge_list)
        
        errors = exc_info.value.errors()
        assert len(errors) > 0
        assert any("max_length" in str(err).lower() for err in errors)
    
    def test_valid_request__accepts_max_length(self):
        """Test that exactly 50k characters is accepted"""
        max_list = "X" * 50000  # Exactly 50,000 characters
        
        request = CreateExchangeRequest(list_content=max_list)
        assert len(request.list_content) == 50000
    
    def test_valid_request__accepts_multiline(self):
        """Test that multiline content is accepted"""
        multiline_list = """
        Space Marines - Ultramarines
        1000 points
        
        HQ:
        - Captain
        
        Troops:
        - 10x Intercessors
        """
        
        request = CreateExchangeRequest(list_content=multiline_list)
        assert "\n" in request.list_content


class TestRespondExchangeRequest:
    """Tests for RespondExchangeRequest model (same validation as Create)"""
    
    def test_valid_request__accepts_normal_list(self):
        """Test that valid army list is accepted"""
        request = RespondExchangeRequest(
            list_content="Player B Army List\n1000 points\nOrks"
        )
        
        assert request.list_content == "Player B Army List\n1000 points\nOrks"
    
    def test_invalid_request__empty_string_rejected(self):
        """Test that empty string is rejected"""
        with pytest.raises(ValidationError):
            RespondExchangeRequest(list_content="")
    
    def test_invalid_request__whitespace_only_rejected(self):
        """Test that whitespace-only string is rejected"""
        with pytest.raises(ValidationError):
            RespondExchangeRequest(list_content="   \n  ")
    
    def test_valid_request__strips_whitespace(self):
        """Test that whitespace is stripped"""
        request = RespondExchangeRequest(
            list_content="  Test List  "
        )
        
        assert request.list_content == "Test List"


class TestCreateExchangeResponse:
    """Tests for CreateExchangeResponse model"""
    
    def test_valid_response__all_fields(self):
        """Test that response with all fields is valid"""
        response = CreateExchangeResponse(
            exchange_id="crimson-marine-charges-7a2f",
            url="/exchange/crimson-marine-charges-7a2f",
            full_url="https://squigleague.com/exchange/crimson-marine-charges-7a2f"
        )
        
        assert response.exchange_id == "crimson-marine-charges-7a2f"
        assert response.url == "/exchange/crimson-marine-charges-7a2f"
        assert response.full_url == "https://squigleague.com/exchange/crimson-marine-charges-7a2f"
    
    def test_invalid_response__missing_exchange_id(self):
        """Test that missing exchange_id is rejected"""
        with pytest.raises(ValidationError) as exc_info:
            CreateExchangeResponse(
                url="/test",
                full_url="https://test.com"
            )
        
        errors = exc_info.value.errors()
        assert any(err['loc'] == ('exchange_id',) for err in errors)


class TestExchangeStatusResponse:
    """Tests for ExchangeStatusResponse model"""
    
    def test_valid_response__ready_true(self):
        """Test response with ready=True"""
        response = ExchangeStatusResponse(ready=True)
        assert response.ready is True
    
    def test_valid_response__ready_false(self):
        """Test response with ready=False"""
        response = ExchangeStatusResponse(ready=False)
        assert response.ready is False
    
    def test_invalid_response__missing_ready(self):
        """Test that missing ready field is rejected"""
        with pytest.raises(ValidationError) as exc_info:
            ExchangeStatusResponse()
        
        errors = exc_info.value.errors()
        assert any(err['loc'] == ('ready',) for err in errors)
    
    def test_invalid_response__wrong_type(self):
        """Test that non-boolean ready value is rejected"""
        with pytest.raises(ValidationError):
            ExchangeStatusResponse(ready="yes")


class TestHealthCheckResponse:
    """Tests for HealthCheckResponse model"""
    
    def test_valid_response__all_fields(self):
        """Test response with all fields"""
        response = HealthCheckResponse(
            status="healthy",
            module="herald",
            database="connected"
        )
        
        assert response.status == "healthy"
        assert response.module == "herald"
        assert response.database == "connected"
    
    def test_valid_response__unhealthy_status(self):
        """Test response with unhealthy status"""
        response = HealthCheckResponse(
            status="unhealthy",
            module="herald",
            database="disconnected"
        )
        
        assert response.status == "unhealthy"
        assert response.database == "disconnected"
    
    def test_invalid_response__missing_fields(self):
        """Test that missing fields are rejected"""
        with pytest.raises(ValidationError):
            HealthCheckResponse(status="healthy")


class TestResourcesResponse:
    """Tests for ResourcesResponse model"""
    
    def test_valid_response__all_fields(self):
        """Test response with all resource fields"""
        response = ResourcesResponse(
            cpu_percent=45.5,
            memory={
                "used_mb": 2048.5,
                "available_mb": 6144.2,
                "percent": 25.0
            },
            disk={
                "used_gb": 50.5,
                "free_gb": 200.8,
                "percent": 20.0
            }
        )
        
        assert response.cpu_percent == 45.5
        assert response.memory["used_mb"] == 2048.5
        assert response.disk["free_gb"] == 200.8
    
    def test_valid_response__zero_cpu(self):
        """Test response with 0% CPU usage"""
        response = ResourcesResponse(
            cpu_percent=0.0,
            memory={"used_mb": 1000, "available_mb": 7000, "percent": 12.5},
            disk={"used_gb": 10, "free_gb": 90, "percent": 10.0}
        )
        
        assert response.cpu_percent == 0.0
    
    def test_valid_response__high_cpu(self):
        """Test response with 100% CPU usage"""
        response = ResourcesResponse(
            cpu_percent=100.0,
            memory={"used_mb": 8000, "available_mb": 200, "percent": 97.5},
            disk={"used_gb": 95, "free_gb": 5, "percent": 95.0}
        )
        
        assert response.cpu_percent == 100.0
    
    def test_invalid_response__missing_cpu(self):
        """Test that missing cpu_percent is rejected"""
        with pytest.raises(ValidationError):
            ResourcesResponse(
                memory={"used_mb": 1000, "available_mb": 7000, "percent": 12.5},
                disk={"used_gb": 10, "free_gb": 90, "percent": 10.0}
            )
    
    def test_invalid_response__missing_memory(self):
        """Test that missing memory dict is rejected"""
        with pytest.raises(ValidationError):
            ResourcesResponse(
                cpu_percent=50.0,
                disk={"used_gb": 10, "free_gb": 90, "percent": 10.0}
            )
    
    def test_invalid_response__wrong_cpu_type(self):
        """Test that non-float CPU value is handled"""
        with pytest.raises(ValidationError):
            ResourcesResponse(
                cpu_percent="high",
                memory={"used_mb": 1000, "available_mb": 7000, "percent": 12.5},
                disk={"used_gb": 10, "free_gb": 90, "percent": 10.0}
            )
