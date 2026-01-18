#!/usr/bin/env python3
"""Test complete matchup flow including player names feature."""
import requests
import sys
import time

BASE_URL = "http://localhost"

def test_full_flow():
    """Test creating and viewing matchup with player names."""
    timestamp = int(time.time())
    
    # Create player 1
    print("\n1. Creating Player 1...")
    p1_email = f"player1_{timestamp}@test.com"
    p1_username = f"player1_{timestamp}"
    response = requests.post(f"{BASE_URL}/api/auth/register", json={
        "email": p1_email,
        "username": p1_username,
        "password": "password123"
    })
    if response.status_code not in (200, 201):
        print(f"   ✗ FAILED: {response.status_code} {response.text}")
        return False
    p1_token = response.json()["access_token"]
    print(f"   ✓ Player 1 registered: {p1_username}")
    
    # Create player 2
    print("\n2. Creating Player 2...")
    p2_email = f"player2_{timestamp}@test.com"
    p2_username = f"player2_{timestamp}"
    response = requests.post(f"{BASE_URL}/api/auth/register", json={
        "email": p2_email,
        "username": p2_username,
        "password": "password123"
    })
    if response.status_code not in (200, 201):
        print(f"   ✗ FAILED: {response.status_code} {response.text}")
        return False
    p2_token = response.json()["access_token"]
    print(f"   ✓ Player 2 registered: {p2_username}")
    
    # Player 1 creates matchup
    print("\n3. Player 1 creating matchup...")
    list_data = "Test Army List\n- 10 Liberators"
    response = requests.post(
        f"{BASE_URL}/api/matchup",
        headers={"Authorization": f"Bearer {p1_token}"},
        json={"army_list": list_data}
    )
    if response.status_code != 201:
        print(f"   ✗ FAILED: {response.status_code} {response.text}")
        return False
    matchup_data = response.json()
    print(f"   Response: {matchup_data}")
    matchup_name = matchup_data["name"]
    print(f"   ✓ Matchup created: {matchup_name}")
    
    # Player 2 submits list
    print("\n4. Player 2 submitting list with matchup name...")
    p2_list = "Player 2 Army\n- 20 Stormcast"
    response = requests.post(
        f"{BASE_URL}/api/matchup/{matchup_name}/submit",
        headers={"Authorization": f"Bearer {p2_token}"},
        json={"army_list": p2_list}
    )
    if response.status_code != 200:
        print(f"   ✗ FAILED: {response.status_code} {response.text}")
        return False
    print(f"   ✓ Player 2 submitted list")
    
    # Try to view the matchup
    print(f"\n5. Viewing matchup {matchup_name}...")
    response = requests.get(f"{BASE_URL}/api/matchup/{matchup_name}")
    if response.status_code != 200:
        print(f"   ✗ FAILED: {response.status_code} {response.text}")
        return False
    status = response.json()
    print(f"   ✓ Matchup retrieved")
    
    # Check for player names
    print("\n6. Verifying player names display...")
    p1_name = status.get("player1_username")
    p2_name = status.get("player2_username")
    
    if not p1_name:
        print(f"   ✗ FAILED: player1_username is missing or null")
        print(f"   Response: {status}")
        return False
    if not p2_name:
        print(f"   ✗ FAILED: player2_username is missing or null")
        print(f"   Response: {status}")
        return False
    
    print(f"   ✓ Player 1 name: {p1_name}")
    print(f"   ✓ Player 2 name: {p2_name}")
    
    if p1_name != p1_username:
        print(f"   ✗ FAILED: Expected {p1_username}, got {p1_name}")
        return False
    if p2_name != p2_username:
        print(f"   ✗ FAILED: Expected {p2_username}, got {p2_name}")
        return False
    
    print(f"\n✓✓✓ ALL TESTS PASSED ✓✓✓")
    print(f"Player names feature works correctly!")
    return True

if __name__ == "__main__":
    try:
        success = test_full_flow()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗✗✗ TEST ERROR ✗✗✗")
        print(f"Exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
