"""Test player names feature end-to-end"""
import requests
import json

BASE_URL = "http://localhost:8000"

print("=" * 60)
print("Testing Player Names Feature")
print("=" * 60)

# Step 1: Register a user
import time
timestamp = int(time.time())
print(f"\n1. Registering user 'player1_{timestamp}'...")
register_data = {
    "email": f"player1_{timestamp}@test.com",
    "username": f"player1_{timestamp}",
    "password": "testpass123"
}
response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
print(f"Status: {response.status_code}")
if response.status_code == 201:
    user_data = response.json()
    token = user_data['access_token']
    print(f"✓ User registered: {user_data['user']['username']}")
    print(f"✓ Token: {token[:20]}...")
else:
    print(f"✗ Error: {response.text}")
    exit(1)

# Step 2: Create matchup as authenticated user
print("\n2. Creating matchup as authenticated user...")
matchup_data = {
    "army_list": "Player1's Army\n- 20 Stabbas\n- 3 Fanatics\n- 10 Shootas"
}
headers = {"Authorization": f"Bearer {token}"}
response = requests.post(f"{BASE_URL}/matchup", json=matchup_data, headers=headers)
print(f"Status: {response.status_code}")
if response.status_code == 201:
    matchup_response = response.json()
    matchup_name = matchup_response['name']
    print(f"✓ Matchup created: {matchup_name}")
else:
    print(f"✗ Error: {response.text}")
    exit(1)

# Step 3: Get matchup status (should show player1 username)
print("\n3. Getting matchup status...")
response = requests.get(f"{BASE_URL}/matchup/{matchup_name}")
print(f"Status: {response.status_code}")
if response.status_code == 200:
    status_data = response.json()
    print(f"Matchup: {status_data['name']}")
    print(f"Player 1 submitted: {status_data['player1_submitted']}")
    print(f"Player 1 username: {status_data.get('player1_username', 'NOT FOUND')}")
    print(f"Player 2 username: {status_data.get('player2_username', 'NOT FOUND')}")
    
    if status_data.get('player1_username') == 'player1':
        print("✓ SUCCESS: Player1 username is displayed!")
    else:
        print("✗ FAIL: Player1 username not found in response")
        print(f"Full response: {json.dumps(status_data, indent=2)}")
else:
    print(f"✗ Error: {response.text}")
    exit(1)

# Step 4: Register second user
print(f"\n4. Registering user 'player2_{timestamp}'...")
register_data2 = {
    "email": f"player2_{timestamp}@test.com",
    "username": f"player2_{timestamp}",
    "password": "testpass456"
}
response = requests.post(f"{BASE_URL}/auth/register", json=register_data2)
print(f"Status: {response.status_code}")
if response.status_code == 201:
    user_data2 = response.json()
    token2 = user_data2['access_token']
    print(f"✓ User registered: {user_data2['user']['username']}")
else:
    print(f"✗ Error: {response.text}")
    exit(1)

# Step 5: Submit as player2
print("\n5. Player2 submitting list...")
submit_data = {
    "army_list": "Player2's Army\n- 30 Goblins\n- 5 Trolls"
}
headers2 = {"Authorization": f"Bearer {token2}"}
response = requests.post(f"{BASE_URL}/matchup/{matchup_name}/submit", json=submit_data, headers=headers2)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    print("✓ Player2 list submitted")
else:
    print(f"✗ Error: {response.text}")

# Step 6: Get revealed matchup
print("\n6. Getting revealed matchup...")
response = requests.get(f"{BASE_URL}/matchup/{matchup_name}/reveal")
print(f"Status: {response.status_code}")
if response.status_code == 200:
    reveal_data = response.json()
    print(f"Player 1 username: {reveal_data.get('player1_username', 'NOT FOUND')}")
    print(f"Player 2 username: {reveal_data.get('player2_username', 'NOT FOUND')}")
    
    expected_p1 = f"player1_{timestamp}"
    expected_p2 = f"player2_{timestamp}"
    if reveal_data.get('player1_username') == expected_p1 and reveal_data.get('player2_username') == expected_p2:
        print("\n" + "=" * 60)
        print("✓✓✓ ALL TESTS PASSED! ✓✓✓")
        print("Both player names are displayed correctly!")
        print("=" * 60)
    else:
        print("\n✗ FAIL: One or both usernames missing")
        print(f"Expected P1: {expected_p1}, Got: {reveal_data.get('player1_username')}")
        print(f"Expected P2: {expected_p2}, Got: {reveal_data.get('player2_username')}")
        print(f"Full response: {json.dumps(reveal_data, indent=2)}")
else:
    print(f"✗ Error: {response.text}")

print("\nTest complete.")
