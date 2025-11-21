"""
Integration tests for Herald exchange workflows

Tests complete end-to-end exchange flows with real database and API.
"""

import pytest
from datetime import datetime
import hashlib


class TestFullExchangeWorkflow:
    """Test complete exchange creation and response flow"""

    def test_full_exchange_workflow__create_respond_view(self, test_client):
        """Test complete workflow: create → respond → view

        Workflow:
        1. Player A creates exchange with list
        2. Player B responds with their list
        3. Both lists are revealed
        4. Both players can view complete exchange
        """
        # Step 1: Player A creates exchange
        create_response = test_client.post(
            "/api/herald/exchange/create",
            json={"list_content": "Player A Army List\n1000 points\nSpace Marines"},
        )

        assert create_response.status_code == 200
        create_data = create_response.json()
        exchange_id = create_data["exchange_id"]
        hash_a = create_data["hash_a"]

        # Verify exchange ID format
        assert len(exchange_id.split("-")) == 4

        # Step 2: Check status (should be waiting)
        status_response = test_client.get(f"/api/herald/exchange/{exchange_id}/status")
        assert status_response.json()["ready"] is False

        # Step 3: Player B responds
        respond_response = test_client.post(
            f"/api/herald/exchange/{exchange_id}/respond",
            json={"list_content": "Player B Army List\n1000 points\nOrks"},
        )

        assert respond_response.status_code == 200

        # Step 4: Check status (should be ready)
        status_response = test_client.get(f"/api/herald/exchange/{exchange_id}/status")
        assert status_response.json()["ready"] is True

        # Step 5: View complete exchange
        view_response = test_client.get(f"/api/herald/exchange/{exchange_id}")

        assert view_response.status_code == 200
        view_data = view_response.json()

        assert view_data["id"] == exchange_id
        assert view_data["status"] == "complete"
        assert view_data["list_a"] == "Player A Army List\n1000 points\nSpace Marines"
        assert view_data["list_b"] == "Player B Army List\n1000 points\nOrks"
        assert view_data["hash_a"] == hash_a
        assert "hash_b" in view_data
        assert "timestamp_a" in view_data
        assert "timestamp_b" in view_data

    def test_exchange_creation__generates_valid_id(self, test_client):
        """Test that exchange creation generates valid memorable ID"""
        response = test_client.post(
            "/api/herald/exchange/create", json={"list_content": "Test List"}
        )

        exchange_id = response.json()["exchange_id"]

        # Verify format: word-word-word-XXXX
        parts = exchange_id.split("-")
        assert len(parts) == 4
        assert len(parts[3]) == 4  # Hash part
        assert all(c in "0123456789abcdef" for c in parts[3])

    def test_exchange_hash_verification__matches_content(self, test_client):
        """Test that returned hash matches list content"""
        list_content = "Verification Test Army List\n500 points"

        response = test_client.post(
            "/api/herald/exchange/create", json={"list_content": list_content}
        )

        returned_hash = response.json()["hash_a"]
        expected_hash = hashlib.sha256(list_content.encode()).hexdigest()

        assert returned_hash == expected_hash

    def test_exchange_not_found__returns_404(self, test_client):
        """Test that requesting non-existent exchange returns 404"""
        response = test_client.get("/api/herald/exchange/nonexistent-id-9999")

        assert response.status_code == 404
        assert (
            "not found" in response.json()["detail"].lower()
            or "invalid" in response.json()["detail"].lower()
        )

    def test_exchange_already_complete__rejects_second_response(self, test_client):
        """Test that responding to complete exchange is rejected"""
        # Create and complete exchange
        create_response = test_client.post(
            "/api/herald/exchange/create", json={"list_content": "Player A"}
        )
        exchange_id = create_response.json()["exchange_id"]

        # First response
        test_client.post(
            f"/api/herald/exchange/{exchange_id}/respond",
            json={"list_content": "Player B First"},
        )

        # Second response (should fail)
        second_response = test_client.post(
            f"/api/herald/exchange/{exchange_id}/respond",
            json={"list_content": "Player B Second"},
        )

        assert second_response.status_code == 400
        assert "complete" in second_response.json()["detail"].lower()

    def test_multiple_exchanges__independent(self, test_client):
        """Test that multiple exchanges are independent"""
        # Create two exchanges
        response1 = test_client.post(
            "/api/herald/exchange/create", json={"list_content": "Exchange 1 List A"}
        )
        exchange_id_1 = response1.json()["exchange_id"]

        response2 = test_client.post(
            "/api/herald/exchange/create", json={"list_content": "Exchange 2 List A"}
        )
        exchange_id_2 = response2.json()["exchange_id"]

        # Complete only exchange 1
        test_client.post(
            f"/api/herald/exchange/{exchange_id_1}/respond",
            json={"list_content": "Exchange 1 List B"},
        )

        # Check exchange 1 is complete
        view1 = test_client.get(f"/api/herald/exchange/{exchange_id_1}")
        assert view1.json()["status"] == "complete"

        # Check exchange 2 is still waiting
        view2 = test_client.get(f"/api/herald/exchange/{exchange_id_2}")
        assert view2.json()["status"] == "waiting"

    def test_pending_exchange__hides_list_content(self, test_client):
        """Test that pending exchange doesn't reveal list content"""
        response = test_client.post(
            "/api/herald/exchange/create", json={"list_content": "Secret Army List"}
        )
        exchange_id = response.json()["exchange_id"]

        # View pending exchange
        view = test_client.get(f"/api/herald/exchange/{exchange_id}")
        data = view.json()

        assert data["status"] == "waiting"
        assert "list_a" not in data
        assert "list_b" not in data
