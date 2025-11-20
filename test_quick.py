"""Quick test to debug the issue"""
import os
import sys
from pathlib import Path

# Setup paths
herald_path = Path(__file__).parent / "herald"
sys.path.insert(0, str(herald_path))

# Set test database
os.environ["DATABASE_URL"] = "postgresql://test_user:test_password@localhost:5433/test_squigleague"

# Now import
from herald import database

# Test log_request
print("Testing log_request...")
try:
    database.log_request("192.168.1.1", "/test", "test-agent")
    print("✓ log_request succeeded")
except Exception as e:
    print(f"✗ log_request failed: {e}")

# Test create_exchange
print("\nTesting create_exchange...")
try:
    exchange_id = database.create_exchange("test-id-123", "Test List", "hash123")
    print(f"✓ create_exchange succeeded: {exchange_id}")
except Exception as e:
    print(f"✗ create_exchange failed: {e}")
