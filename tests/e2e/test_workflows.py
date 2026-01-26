"""
End-to-end tests for complete user workflows.

Tests realistic user scenarios through the entire application stack.
"""
import pytest
import requests
import time

BASE_URL = "http://localhost"


class TestCompleteMatchupWorkflow:
    """Test complete matchup creation and reveal workflow."""

    def test_two_users_create_and_reveal_matchup(self):
        """
        Complete workflow:
        1. Two users register
        2. User 1 creates matchup
        3. User 2 finds and submits to matchup
        4. Both users can view revealed matchup with names
        """
        timestamp = int(time.time())
        
        # Step 1: Register two users
        p1_response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "email": f"player1_{timestamp}@test.com",
                "username": f"Alice_{timestamp}",
                "password": "password123"
            }
        )
        p1_token = p1_response.json()["access_token"]
        p1_username = f"Alice_{timestamp}"
        
        p2_response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "email": f"player2_{timestamp}@test.com",
                "username": f"Bob_{timestamp}",
                "password": "password123"
            }
        )
        p2_token = p2_response.json()["access_token"]
        p2_username = f"Bob_{timestamp}"
        
        # Step 2: Player 1 creates matchup
        create_response = requests.post(
            f"{BASE_URL}/api/matchup",
            headers={"Authorization": f"Bearer {p1_token}"},
            json={
                "army_list": "Stormcast Eternals\n- Lord-Imperatant\n- 10 Liberators\n- 5 Vindictors"
            }
        )
        matchup_name = create_response.json()["name"]
        
        # Step 3: Player 1 checks their matchups
        my_matchups_response = requests.get(
            f"{BASE_URL}/api/matchup/my-matchups",
            headers={"Authorization": f"Bearer {p1_token}"}
        )
        matchups = my_matchups_response.json()
        assert len(matchups) >= 1
        assert matchups[0]["player1_username"] == p1_username
        
        # Step 4: Player 2 views the matchup
        status_response = requests.get(f"{BASE_URL}/api/matchup/{matchup_name}")
        status = status_response.json()
        assert status["player1_submitted"] == True
        assert status["player2_submitted"] == False
        assert status["is_revealed"] == False
        assert status["player1_username"] == p1_username
        
        # Step 5: Player 2 submits their list
        submit_response = requests.post(
            f"{BASE_URL}/api/matchup/{matchup_name}/submit",
            headers={"Authorization": f"Bearer {p2_token}"},
            json={
                "army_list": "Orruk Warclans\n- Megaboss\n- 10 Ardboyz\n- 5 Brutes"
            }
        )
        assert submit_response.json()["is_revealed"] == True
        
        # Step 6: Player 2 checks their matchups
        p2_matchups = requests.get(
            f"{BASE_URL}/api/matchup/my-matchups",
            headers={"Authorization": f"Bearer {p2_token}"}
        ).json()
        assert any(m["name"] == matchup_name for m in p2_matchups)
        
        # Step 7: Both players can see the reveal
        reveal_response = requests.get(f"{BASE_URL}/api/matchup/{matchup_name}/reveal")
        reveal = reveal_response.json()
        
        assert reveal["player1_username"] == p1_username
        assert reveal["player2_username"] == p2_username
        assert "Stormcast" in reveal["player1_list"]
        assert "Orruk" in reveal["player2_list"]
        assert reveal["map_name"] is not None
        assert reveal["revealed_at"] is not None
        
        # Step 8: Verify both users see names in their matchup lists
        p1_list = requests.get(
            f"{BASE_URL}/api/matchup/my-matchups",
            headers={"Authorization": f"Bearer {p1_token}"}
        ).json()
        p1_matchup = next(m for m in p1_list if m["name"] == matchup_name)
        assert p1_matchup["player1_username"] == p1_username
        assert p1_matchup["player2_username"] == p2_username
        
        p2_list = requests.get(
            f"{BASE_URL}/api/matchup/my-matchups",
            headers={"Authorization": f"Bearer {p2_token}"}
        ).json()
        p2_matchup = next(m for m in p2_list if m["name"] == matchup_name)
        assert p2_matchup["player1_username"] == p1_username
        assert p2_matchup["player2_username"] == p2_username


class TestAnonymousMatchupWorkflow:
    """Test workflow with anonymous users."""

    def test_anonymous_users_complete_matchup(self):
        """
        Workflow:
        1. Anonymous user creates matchup
        2. Another anonymous user submits
        3. Both can view reveal (no usernames)
        """
        # Step 1: Anonymous user creates matchup
        create_response = requests.post(
            f"{BASE_URL}/api/matchup",
            json={"army_list": "Test Army\n- 10 Warriors\n- Hero"}
        )
        matchup_name = create_response.json()["name"]
        
        # Step 2: Check status shows null usernames
        status = requests.get(f"{BASE_URL}/api/matchup/{matchup_name}").json()
        assert status["player1_username"] is None
        assert status["player2_username"] is None
        
        # Step 3: Another anonymous user submits
        requests.post(
            f"{BASE_URL}/api/matchup/{matchup_name}/submit",
            json={"army_list": "Enemy Army\n- 20 Troops\n- Leader"}
        )
        
        # Step 4: Reveal shows no usernames
        reveal = requests.get(f"{BASE_URL}/api/matchup/{matchup_name}/reveal").json()
        assert reveal["player1_username"] is None
        assert reveal["player2_username"] is None


class TestMixedAuthWorkflow:
    """Test workflow with mix of authenticated and anonymous users."""

    def test_authenticated_vs_anonymous(self):
        """
        Workflow:
        1. Authenticated user creates matchup
        2. Anonymous user submits
        3. Reveal shows only player 1 username
        """
        timestamp = int(time.time())
        
        # Register authenticated user
        auth_response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "email": f"auth_{timestamp}@test.com",
                "username": f"AuthUser_{timestamp}",
                "password": "password123"
            }
        )
        token = auth_response.json()["access_token"]
        username = f"AuthUser_{timestamp}"
        
        # Authenticated user creates matchup
        create_response = requests.post(
            f"{BASE_URL}/api/matchup",
            headers={"Authorization": f"Bearer {token}"},
            json={"army_list": "Auth Army\n- 10 Units\n- Hero"}
        )
        matchup_name = create_response.json()["name"]
        
        # Anonymous user submits
        requests.post(
            f"{BASE_URL}/api/matchup/{matchup_name}/submit",
            json={"army_list": "Anon Army\n- 20 Troops\n- Leader"}
        )
        
        # Reveal shows mixed usernames
        reveal = requests.get(f"{BASE_URL}/api/matchup/{matchup_name}/reveal").json()
        assert reveal["player1_username"] == username
        assert reveal["player2_username"] is None


class TestErrorRecoveryWorkflow:
    """Test error handling and recovery scenarios."""

    def test_duplicate_submission_handling(self):
        """Test that player 2 cannot submit twice."""
        timestamp = int(time.time())
        
        p1_response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "email": f"p1_{timestamp}@test.com",
                "username": f"p1_{timestamp}",
                "password": "password123"
            }
        )
        p1_token = p1_response.json()["access_token"]
        
        p2_response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "email": f"p2_{timestamp}@test.com",
                "username": f"p2_{timestamp}",
                "password": "password123"
            }
        )
        p2_token = p2_response.json()["access_token"]
        
        # Create matchup
        create_response = requests.post(
            f"{BASE_URL}/api/matchup",
            headers={"Authorization": f"Bearer {p1_token}"},
            json={"army_list": "Army\n- 10 Units\n- Hero"}
        )
        matchup_name = create_response.json()["name"]
        
        # First submission succeeds
        first_submit = requests.post(
            f"{BASE_URL}/api/matchup/{matchup_name}/submit",
            headers={"Authorization": f"Bearer {p2_token}"},
            json={"army_list": "Army2\n- 20 Troops\n- Leader"}
        )
        assert first_submit.status_code == 200
        
        # Second submission should fail (already revealed)
        second_submit = requests.post(
            f"{BASE_URL}/api/matchup/{matchup_name}/submit",
            headers={"Authorization": f"Bearer {p2_token}"},
            json={"army_list": "Army3\n- 30 Soldiers\n- Commander"}
        )
        assert second_submit.status_code != 200
