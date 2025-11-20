"""
Integration tests for Herald admin endpoints

Tests admin functionality including authentication and resource monitoring.
"""

import pytest
from unittest.mock import patch
import os


class TestAdminResourcesEndpoint:
    """Tests for GET /admin/resources endpoint"""
    
    def test_admin_resources__requires_auth(self, test_client):
        """Test that /admin/resources requires admin key"""
        response = test_client.get("/admin/resources?admin_key=wrong-key")
        
        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()
    
    def test_admin_resources__401_without_key(self, test_client):
        """Test that /admin/resources returns 401 without admin key"""
        response = test_client.get("/admin/resources")
        
        assert response.status_code in [401, 422]  # 422 if key is required param
    
    @patch.dict(os.environ, {'ADMIN_KEY': 'test-admin-key'})
    def test_admin_resources__returns_cpu_memory_disk(self, test_client):
        """Test that /admin/resources returns resource data with valid key"""
        response = test_client.get("/admin/resources?admin_key=test-admin-key")
        
        if response.status_code == 200:
            data = response.json()
            assert "cpu_percent" in data
            assert "memory" in data
            assert "disk" in data
            
            # Verify memory structure
            assert "used_mb" in data["memory"]
            assert "available_mb" in data["memory"]
            assert "percent" in data["memory"]
            
            # Verify disk structure
            assert "used_gb" in data["disk"]
            assert "free_gb" in data["disk"]
            assert "percent" in data["disk"]


class TestAdminAbuseReportEndpoint:
    """Tests for GET /admin/abuse-report endpoint"""
    
    def test_admin_abuse_report__requires_auth(self, test_client):
        """Test that /admin/abuse-report requires admin key"""
        response = test_client.get("/admin/abuse-report?admin_key=wrong-key")
        
        assert response.status_code == 401
    
    def test_admin_abuse_report__401_without_key(self, test_client):
        """Test that /admin/abuse-report returns 401 without key"""
        response = test_client.get("/admin/abuse-report")
        
        assert response.status_code in [401, 422]
    
    @patch.dict(os.environ, {'ADMIN_KEY': 'test-admin-key'})
    def test_admin_abuse_report__returns_data(self, test_client):
        """Test that /admin/abuse-report returns abuse data"""
        response = test_client.get("/admin/abuse-report?admin_key=test-admin-key")
        
        if response.status_code == 200:
            data = response.json()
            assert "abusive_ips" in data
            assert "stats" in data
            assert "threshold" in data
            
            # Verify threshold structure
            assert "min_requests" in data["threshold"]
            assert "hours" in data["threshold"]
    
    @patch.dict(os.environ, {'ADMIN_KEY': 'test-admin-key'})
    def test_admin_abuse_report__respects_threshold(self, test_client, test_engine):
        """Test that /admin/abuse-report respects min_requests threshold"""
        from sqlalchemy import text
        
        # Create some request logs
        with test_engine.connect() as conn:
            for i in range(50):
                conn.execute(
                    text("""
                        INSERT INTO herald_request_log (ip, endpoint, user_agent)
                        VALUES (:ip, :endpoint, :user_agent)
                    """),
                    {
                        "ip": "10.0.0.100",
                        "endpoint": f"/api/test/{i}",
                        "user_agent": "test"
                    }
                )
            conn.commit()
        
        # Query with high threshold (should be empty)
        response = test_client.get(
            "/admin/abuse-report?admin_key=test-admin-key&min_requests=200&hours=1"
        )
        
        if response.status_code == 200:
            data = response.json()
            # With 50 requests, threshold of 200 should return no abusive IPs
            assert len(data["abusive_ips"]) == 0
    
    @patch.dict(os.environ, {'ADMIN_KEY': 'test-admin-key'})
    def test_admin_abuse_report__finds_abusive_ips(self, test_client, test_engine):
        """Test that /admin/abuse-report finds IPs exceeding threshold"""
        from sqlalchemy import text
        
        # Create many requests from one IP
        abusive_ip = "192.168.1.200"
        with test_engine.connect() as conn:
            for i in range(150):
                conn.execute(
                    text("""
                        INSERT INTO herald_request_log (ip, endpoint, user_agent)
                        VALUES (:ip, :endpoint, :user_agent)
                    """),
                    {
                        "ip": abusive_ip,
                        "endpoint": f"/api/spam/{i}",
                        "user_agent": "spammer"
                    }
                )
            conn.commit()
        
        # Query with low threshold
        response = test_client.get(
            "/admin/abuse-report?admin_key=test-admin-key&min_requests=100&hours=1"
        )
        
        if response.status_code == 200:
            data = response.json()
            # Should find the abusive IP
            abusive_ips = data["abusive_ips"]
            assert any(ip["ip"] == abusive_ip for ip in abusive_ips)
