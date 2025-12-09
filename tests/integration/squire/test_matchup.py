"""
Tests for Squire matchup system
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestMatchupCreation:
    """Test matchup creation endpoint"""

    def test_create_matchup_age_of_sigmar(self):
        """Test creating a matchup for Age of Sigmar"""
        response = client.post(
            "/api/squire/matchup/create",
            json={"game_system": "age_of_sigmar"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "matchup_id" in data
        assert len(data["matchup_id"]) > 0

    def test_create_matchup_40k(self):
        """Test creating a matchup for Warhammer 40k"""
        response = client.post(
            "/api/squire/matchup/create",
            json={"game_system": "warhammer_40k"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "matchup_id" in data

    def test_create_matchup_old_world(self):
        """Test creating a matchup for The Old World"""
        response = client.post(
            "/api/squire/matchup/create",
            json={"game_system": "the_old_world"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "matchup_id" in data

    def test_create_matchup_invalid_system(self):
        """Test creating a matchup with invalid game system"""
        response = client.post(
            "/api/squire/matchup/create",
            json={"game_system": "invalid_system"}
        )
        assert response.status_code == 422  # Validation error


class TestMatchupSubmission:
    """Test matchup list submission"""

    def setup_method(self):
        """Create a matchup before each test"""
        response = client.post(
            "/api/squire/matchup/create",
            json={"game_system": "age_of_sigmar"}
        )
        self.matchup_id = response.json()["matchup_id"]

    def test_first_player_submission(self):
        """Test first player submitting their list"""
        response = client.post(
            f"/api/squire/matchup/{self.matchup_id}/submit",
            json={
                "player_name": "Alice",
                "army_list": "Test Army List\nUnit 1\nUnit 2"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_complete"] is False
        assert data["player1"]["name"] == "Alice"
        assert data["player2"] is None
        assert data["battle_plan"] is None  # Not revealed yet

    def test_second_player_submission_generates_battle_plan(self):
        """Test that battle plan is generated when second player submits"""
        # First player submits
        client.post(
            f"/api/squire/matchup/{self.matchup_id}/submit",
            json={
                "player_name": "Alice",
                "army_list": "Alice's Army"
            }
        )

        # Second player submits
        response = client.post(
            f"/api/squire/matchup/{self.matchup_id}/submit",
            json={
                "player_name": "Bob",
                "army_list": "Bob's Army"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_complete"] is True
        assert data["player1"]["name"] == "Alice"
        assert data["player2"]["name"] == "Bob"
        assert data["battle_plan"] is not None
        assert "name" in data["battle_plan"]
        assert data["battle_plan"]["game_system"] == "age_of_sigmar"

    def test_third_player_cannot_join(self):
        """Test that a third player cannot join a full matchup"""
        # First two players submit
        client.post(
            f"/api/squire/matchup/{self.matchup_id}/submit",
            json={"player_name": "Alice", "army_list": "Alice's Army"}
        )
        client.post(
            f"/api/squire/matchup/{self.matchup_id}/submit",
            json={"player_name": "Bob", "army_list": "Bob's Army"}
        )

        # Third player tries to join
        response = client.post(
            f"/api/squire/matchup/{self.matchup_id}/submit",
            json={"player_name": "Charlie", "army_list": "Charlie's Army"}
        )
        assert response.status_code == 400
        assert "full" in response.json()["detail"].lower()

    def test_submit_to_nonexistent_matchup(self):
        """Test submitting to a matchup that doesn't exist"""
        response = client.post(
            "/api/squire/matchup/invalid_id/submit",
            json={"player_name": "Alice", "army_list": "Test"}
        )
        assert response.status_code == 404


class TestMatchupRetrieval:
    """Test retrieving matchup data"""

    def setup_method(self):
        """Create a matchup before each test"""
        response = client.post(
            "/api/squire/matchup/create",
            json={"game_system": "warhammer_40k"}
        )
        self.matchup_id = response.json()["matchup_id"]

    def test_get_empty_matchup(self):
        """Test retrieving a matchup with no submissions"""
        response = client.get(f"/api/squire/matchup/{self.matchup_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["matchup_id"] == self.matchup_id
        assert data["game_system"] == "warhammer_40k"
        assert data["is_complete"] is False
        assert data["player1"] is None
        assert data["player2"] is None
        assert data["battle_plan"] is None

    def test_get_partial_matchup(self):
        """Test retrieving a matchup with one submission"""
        client.post(
            f"/api/squire/matchup/{self.matchup_id}/submit",
            json={"player_name": "Alice", "army_list": "Alice's Army"}
        )

        response = client.get(f"/api/squire/matchup/{self.matchup_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["is_complete"] is False
        assert data["player1"]["name"] == "Alice"
        # Army list should be hidden until complete
        assert "army_list" not in data["player1"] or data["player1"]["army_list"] is None

    def test_get_complete_matchup(self):
        """Test retrieving a complete matchup reveals all data"""
        client.post(
            f"/api/squire/matchup/{self.matchup_id}/submit",
            json={"player_name": "Alice", "army_list": "Alice's Army"}
        )
        client.post(
            f"/api/squire/matchup/{self.matchup_id}/submit",
            json={"player_name": "Bob", "army_list": "Bob's Army"}
        )

        response = client.get(f"/api/squire/matchup/{self.matchup_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["is_complete"] is True
        assert data["player1"]["name"] == "Alice"
        assert data["player1"]["army_list"] == "Alice's Army"
        assert data["player2"]["name"] == "Bob"
        assert data["player2"]["army_list"] == "Bob's Army"
        assert data["battle_plan"] is not None

    def test_get_nonexistent_matchup(self):
        """Test retrieving a matchup that doesn't exist"""
        response = client.get("/api/squire/matchup/invalid_id")
        assert response.status_code == 404


class TestBattlePlanGeneration:
    """Test battle plan generation for different systems"""

    def test_battle_plan_contains_required_fields(self):
        """Test that generated battle plans have all required fields"""
        # Create and complete a matchup
        response = client.post(
            "/api/squire/matchup/create",
            json={"game_system": "age_of_sigmar"}
        )
        matchup_id = response.json()["matchup_id"]

        client.post(
            f"/api/squire/matchup/{matchup_id}/submit",
            json={"player_name": "Alice", "army_list": "Test"}
        )
        response = client.post(
            f"/api/squire/matchup/{matchup_id}/submit",
            json={"player_name": "Bob", "army_list": "Test"}
        )

        battle_plan = response.json()["battle_plan"]
        assert "name" in battle_plan
        assert "game_system" in battle_plan
        assert "deployment" in battle_plan
        assert "primary_objective" in battle_plan
        assert "victory_conditions" in battle_plan
        assert "turn_limit" in battle_plan

    def test_battle_plan_matches_system(self):
        """Test that battle plan matches the selected game system"""
        for system in ["age_of_sigmar", "warhammer_40k", "the_old_world"]:
            response = client.post(
                "/api/squire/matchup/create",
                json={"game_system": system}
            )
            matchup_id = response.json()["matchup_id"]

            client.post(
                f"/api/squire/matchup/{matchup_id}/submit",
                json={"player_name": "P1", "army_list": "Test"}
            )
            response = client.post(
                f"/api/squire/matchup/{matchup_id}/submit",
                json={"player_name": "P2", "army_list": "Test"}
            )

            battle_plan = response.json()["battle_plan"]
            assert battle_plan["game_system"] == system


class TestMatchupValidation:
    """Test input validation for matchup endpoints"""

    def test_create_matchup_missing_system(self):
        """Test creating matchup without game_system"""
        response = client.post("/api/squire/matchup/create", json={})
        assert response.status_code == 422

    def test_submit_missing_name(self):
        """Test submitting without player name"""
        response = client.post(
            "/api/squire/matchup/create",
            json={"game_system": "age_of_sigmar"}
        )
        matchup_id = response.json()["matchup_id"]

        response = client.post(
            f"/api/squire/matchup/{matchup_id}/submit",
            json={"army_list": "Test"}
        )
        assert response.status_code == 422

    def test_submit_missing_army_list(self):
        """Test submitting without army list"""
        response = client.post(
            "/api/squire/matchup/create",
            json={"game_system": "age_of_sigmar"}
        )
        matchup_id = response.json()["matchup_id"]

        response = client.post(
            f"/api/squire/matchup/{matchup_id}/submit",
            json={"player_name": "Alice"}
        )
        assert response.status_code == 422

    def test_submit_empty_name(self):
        """Test submitting with empty player name"""
        response = client.post(
            "/api/squire/matchup/create",
            json={"game_system": "age_of_sigmar"}
        )
        matchup_id = response.json()["matchup_id"]

        response = client.post(
            f"/api/squire/matchup/{matchup_id}/submit",
            json={"player_name": "", "army_list": "Test"}
        )
        assert response.status_code == 422

    def test_submit_empty_army_list(self):
        """Test submitting with empty army list"""
        response = client.post(
            "/api/squire/matchup/create",
            json={"game_system": "age_of_sigmar"}
        )
        matchup_id = response.json()["matchup_id"]

        response = client.post(
            f"/api/squire/matchup/{matchup_id}/submit",
            json={"player_name": "Alice", "army_list": ""}
        )
        assert response.status_code == 422
