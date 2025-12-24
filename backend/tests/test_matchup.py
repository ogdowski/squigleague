"""
Test Matchup Module

Tests for matchup creation, list submission, and battle plan generation.
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool

from app.main import app
from app.db import get_session


# ═══════════════════════════════════════════════
# TEST DATABASE SETUP
# ═══════════════════════════════════════════════


@pytest.fixture(name="session")
def session_fixture():
    """Create test database session"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create test client with test database"""
    def get_session_override():
        return session
    
    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


# ═══════════════════════════════════════════════
# MATCHUP CREATION TESTS
# ═══════════════════════════════════════════════


def test_create_matchup_aos(client: TestClient):
    """Test creating AoS matchup"""
    response = client.post(
        "/api/matchup",
        json={"game_system": "aos"}
    )
    assert response.status_code == 200
    data = response.json()
    
    assert "uuid" in data
    assert data["game_system"] == "aos"
    assert "share_url" in data
    assert "created_at" in data
    assert "expires_at" in data


def test_create_matchup_40k(client: TestClient):
    """Test creating 40k matchup"""
    response = client.post(
        "/api/matchup",
        json={"game_system": "40k"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["game_system"] == "40k"


def test_create_matchup_tow(client: TestClient):
    """Test creating The Old World matchup"""
    response = client.post(
        "/api/matchup",
        json={"game_system": "tow"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["game_system"] == "tow"


def test_create_matchup_invalid_system(client: TestClient):
    """Test creating matchup with invalid game system"""
    response = client.post(
        "/api/matchup",
        json={"game_system": "invalid"}
    )
    assert response.status_code == 422  # Validation error


# ═══════════════════════════════════════════════
# MATCHUP STATUS TESTS
# ═══════════════════════════════════════════════


def test_get_matchup_status(client: TestClient):
    """Test getting matchup status"""
    # Create matchup
    create_response = client.post(
        "/api/matchup",
        json={"game_system": "aos"}
    )
    uuid = create_response.json()["uuid"]
    
    # Get status
    response = client.get(f"/api/matchup/{uuid}")
    assert response.status_code == 200
    data = response.json()
    
    assert data["uuid"] == uuid
    assert data["game_system"] == "aos"
    assert data["player1_submitted"] is False
    assert data["player2_submitted"] is False
    assert data["waiting_count"] == 2
    assert data["is_complete"] is False


def test_get_nonexistent_matchup(client: TestClient):
    """Test getting status of non-existent matchup"""
    response = client.get("/api/matchup/nonexistent-uuid")
    assert response.status_code == 404


# ═══════════════════════════════════════════════
# LIST SUBMISSION TESTS
# ═══════════════════════════════════════════════


def test_submit_first_list(client: TestClient):
    """Test submitting first player's list"""
    # Create matchup
    create_response = client.post(
        "/api/matchup",
        json={"game_system": "aos"}
    )
    uuid = create_response.json()["uuid"]
    
    # Submit first list
    response = client.post(
        f"/api/matchup/{uuid}/submit",
        json={
            "player_name": "Player One",
            "army_list": "Stormcast Eternals:\n- Lord-Imperatant\n- 5 Vindictors"
        }
    )
    assert response.status_code == 200
    data = response.json()
    
    assert data["player_number"] == 1
    assert data["waiting_for_opponent"] is True
    assert data["both_submitted"] is False
    assert "Waiting for opponent" in data["message"]


def test_submit_both_lists(client: TestClient):
    """Test submitting both lists triggers battle plan generation"""
    # Create matchup
    create_response = client.post(
        "/api/matchup",
        json={"game_system": "aos"}
    )
    uuid = create_response.json()["uuid"]
    
    # Submit first list
    client.post(
        f"/api/matchup/{uuid}/submit",
        json={
            "player_name": "Player One",
            "army_list": "Stormcast Eternals army"
        }
    )
    
    # Submit second list
    response = client.post(
        f"/api/matchup/{uuid}/submit",
        json={
            "player_name": "Player Two",
            "army_list": "Nighthaunt army"
        }
    )
    assert response.status_code == 200
    data = response.json()
    
    assert data["player_number"] == 2
    assert data["waiting_for_opponent"] is False
    assert data["both_submitted"] is True
    assert "Battle plan generated" in data["message"]


def test_submit_list_twice(client: TestClient):
    """Test submitting a third list is rejected"""
    # Create matchup
    create_response = client.post(
        "/api/matchup",
        json={"game_system": "aos"}
    )
    uuid = create_response.json()["uuid"]
    
    # Submit two lists
    client.post(
        f"/api/matchup/{uuid}/submit",
        json={"player_name": "P1", "army_list": "List 1"}
    )
    client.post(
        f"/api/matchup/{uuid}/submit",
        json={"player_name": "P2", "army_list": "List 2"}
    )
    
    # Try to submit third list
    response = client.post(
        f"/api/matchup/{uuid}/submit",
        json={"player_name": "P3", "army_list": "List 3"}
    )
    assert response.status_code == 400
    assert "already complete" in response.json()["detail"].lower()


# ═══════════════════════════════════════════════
# REVEAL TESTS
# ═══════════════════════════════════════════════


def test_reveal_before_both_submitted(client: TestClient):
    """Test revealing before both lists submitted is rejected"""
    # Create matchup
    create_response = client.post(
        "/api/matchup",
        json={"game_system": "aos"}
    )
    uuid = create_response.json()["uuid"]
    
    # Try to reveal
    response = client.get(f"/api/matchup/{uuid}/reveal")
    assert response.status_code == 400
    assert "waiting for" in response.json()["detail"].lower()


def test_reveal_after_both_submitted(client: TestClient):
    """Test revealing matchup after both lists submitted"""
    # Create matchup
    create_response = client.post(
        "/api/matchup",
        json={"game_system": "aos"}
    )
    uuid = create_response.json()["uuid"]
    
    # Submit both lists
    client.post(
        f"/api/matchup/{uuid}/submit",
        json={
            "player_name": "Alice",
            "army_list": "Stormcast army"
        }
    )
    client.post(
        f"/api/matchup/{uuid}/submit",
        json={
            "player_name": "Bob",
            "army_list": "Nighthaunt army"
        }
    )
    
    # Reveal
    response = client.get(f"/api/matchup/{uuid}/reveal")
    assert response.status_code == 200
    data = response.json()
    
    # Check player data
    assert data["uuid"] == uuid
    assert data["game_system"] == "aos"
    assert data["player1_name"] == "Alice"
    assert data["player1_list"] == "Stormcast army"
    assert data["player2_name"] == "Bob"
    assert data["player2_list"] == "Nighthaunt army"
    
    # Check battle plan
    assert "battle_plan" in data
    bp = data["battle_plan"]
    assert "name" in bp
    assert "deployment" in bp
    assert "primary_objective" in bp
    assert "secondary_objectives" in bp
    assert "victory_conditions" in bp
    assert "turn_limit" in bp
    
    # Check map
    assert "map_name" in data


# ═══════════════════════════════════════════════
# GAME SYSTEM SPECIFIC TESTS
# ═══════════════════════════════════════════════


def test_aos_battle_plan_format(client: TestClient):
    """Test AoS battle plan has correct structure"""
    # Create and complete matchup
    create_response = client.post(
        "/api/matchup",
        json={"game_system": "aos"}
    )
    uuid = create_response.json()["uuid"]
    
    client.post(
        f"/api/matchup/{uuid}/submit",
        json={"player_name": "P1", "army_list": "List 1"}
    )
    client.post(
        f"/api/matchup/{uuid}/submit",
        json={"player_name": "P2", "army_list": "List 2"}
    )
    
    # Reveal and check battle plan
    response = client.get(f"/api/matchup/{uuid}/reveal")
    bp = response.json()["battle_plan"]
    
    # AoS-specific fields
    assert bp["turn_limit"] == 5
    assert "battle_tactics" in bp
    assert isinstance(bp["battle_tactics"], list)


def test_40k_battle_plan_format(client: TestClient):
    """Test 40k battle plan has correct structure"""
    # Create and complete matchup
    create_response = client.post(
        "/api/matchup",
        json={"game_system": "40k"}
    )
    uuid = create_response.json()["uuid"]
    
    client.post(
        f"/api/matchup/{uuid}/submit",
        json={"player_name": "P1", "army_list": "List 1"}
    )
    client.post(
        f"/api/matchup/{uuid}/submit",
        json={"player_name": "P2", "army_list": "List 2"}
    )
    
    # Reveal and check battle plan
    response = client.get(f"/api/matchup/{uuid}/reveal")
    bp = response.json()["battle_plan"]
    
    # 40k-specific fields
    assert bp["turn_limit"] == 5
    assert len(bp["secondary_objectives"]) == 3  # 40k has 3 secondaries


def test_tow_battle_plan_format(client: TestClient):
    """Test TOW battle plan has correct structure"""
    # Create and complete matchup
    create_response = client.post(
        "/api/matchup",
        json={"game_system": "tow"}
    )
    uuid = create_response.json()["uuid"]
    
    client.post(
        f"/api/matchup/{uuid}/submit",
        json={"player_name": "P1", "army_list": "List 1"}
    )
    client.post(
        f"/api/matchup/{uuid}/submit",
        json={"player_name": "P2", "army_list": "List 2"}
    )
    
    # Reveal and check battle plan
    response = client.get(f"/api/matchup/{uuid}/reveal")
    bp = response.json()["battle_plan"]
    
    # TOW-specific fields
    assert bp["turn_limit"] == 6  # TOW typically has 6 turns
