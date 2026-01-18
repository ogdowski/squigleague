#!/usr/bin/env python3
"""Test authentication through Docker nginx proxy."""
import requests
import sys
import time

BASE_URL = "http://localhost"

def test_auth_flow():
    """Test complete auth flow through nginx proxy."""
    print("Testing authentication through Docker environment...")
    
    # Generate unique username
    timestamp = int(time.time())
    email = f"test_{timestamp}@example.com"
    username = f"testuser_{timestamp}"
    password = "testpass123"
    
    # Test 1: Register
    print(f"\n1. Registering user: {username}")
    response = requests.post(
        f"{BASE_URL}/api/auth/register",
        json={"email": email, "username": username, "password": password}
    )
    print(f"   Status: {response.status_code}")
    if response.status_code not in (200, 201):
        print(f"   ERROR: {response.text}")
        return False
    
    data = response.json()
    token = data.get("access_token")
    if not token:
        print("   ERROR: No access_token in response")
        return False
    print(f"   ✓ Got token: {token[:20]}...")
    
    # Test 2: Access protected endpoint with token
    print("\n2. Accessing /api/matchup/my-matchups with Authorization header")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/matchup/my-matchups", headers=headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 401:
        print("   ✗ FAILED: Got 401 Unauthorized - nginx not passing Authorization header!")
        return False
    elif response.status_code == 200:
        print(f"   ✓ SUCCESS: Got authenticated response")
        print(f"   Data: {response.json()}")
        return True
    else:
        print(f"   ERROR: Unexpected status {response.status_code}: {response.text}")
        return False

if __name__ == "__main__":
    try:
        success = test_auth_flow()
        if success:
            print("\n✓✓✓ ALL TESTS PASSED ✓✓✓")
            print("Authentication works correctly through Docker nginx proxy!")
            sys.exit(0)
        else:
            print("\n✗✗✗ TEST FAILED ✗✗✗")
            sys.exit(1)
    except Exception as e:
        print(f"\n✗✗✗ TEST ERROR ✗✗✗")
        print(f"Exception: {e}")
        sys.exit(1)
