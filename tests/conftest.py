"""
Pytest configuration and fixtures for test suite.
"""
import pytest


@pytest.fixture(scope="session")
def base_url():
    """Base URL for API requests."""
    return "http://localhost"


@pytest.fixture
def api_client(base_url):
    """Configured API client for tests."""
    import requests
    
    class APIClient:
        def __init__(self, base_url):
            self.base_url = base_url
            self.session = requests.Session()
        
        def get(self, path, **kwargs):
            return self.session.get(f"{self.base_url}{path}", **kwargs)
        
        def post(self, path, **kwargs):
            return self.session.post(f"{self.base_url}{path}", **kwargs)
    
    return APIClient(base_url)
