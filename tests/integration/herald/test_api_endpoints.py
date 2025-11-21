"""
Integration tests for Herald API endpoints

Tests all API endpoints with real HTTP requests and database.
"""

import pytest


class TestHealthEndpoints:
    """Tests for health check endpoints"""

    def test_GET_health__returns_200(self, test_client):
        """Test GET /health returns 200"""
        response = test_client.get("/health")

        assert response.status_code == 200

    def test_GET_health__returns_health_data(self, test_client):
        """Test GET /health returns correct structure"""
        response = test_client.get("/health")
        data = response.json()

        assert data["status"] in ["healthy", "unhealthy"]
        assert data["module"] == "herald"
        assert data["database"] in ["connected", "disconnected"]

    def test_GET_api_herald_health__returns_200(self, test_client):
        """Test GET /api/herald/health returns 200"""
        response = test_client.get("/api/herald/health")

        assert response.status_code == 200
        assert response.json()["module"] == "herald"


class TestCreateExchangeEndpoint:
    """Tests for POST /api/herald/exchange/create"""

    def test_POST_create_exchange__returns_200(self, test_client):
        """Test POST /api/herald/exchange/create returns 200"""
        response = test_client.post(
            "/api/herald/exchange/create",
            json={"list_content": "Test Army List\n1000 points"},
        )

        assert response.status_code == 200

    def test_POST_create_exchange__returns_exchange_id(self, test_client):
        """Test POST /api/herald/exchange/create returns exchange_id"""
        response = test_client.post(
            "/api/herald/exchange/create", json={"list_content": "Test Army List"}
        )

        data = response.json()
        assert "exchange_id" in data
        assert isinstance(data["exchange_id"], str)

    def test_POST_create_exchange__returns_hash(self, test_client):
        """Test POST /api/herald/exchange/create returns hash"""
        response = test_client.post(
            "/api/herald/exchange/create", json={"list_content": "Test List"}
        )

        data = response.json()
        assert "hash_a" in data
        assert len(data["hash_a"]) == 64  # SHA-256 hex length

    def test_POST_create_exchange__422_for_empty_content(self, test_client):
        """Test POST /api/herald/exchange/create returns 422 for empty content"""
        response = test_client.post(
            "/api/herald/exchange/create", json={"list_content": ""}
        )

        assert response.status_code == 422

    def test_POST_create_exchange__422_for_missing_content(self, test_client):
        """Test POST /api/herald/exchange/create returns 422 for missing content"""
        response = test_client.post("/api/herald/exchange/create", json={})

        assert response.status_code == 422


class TestGetExchangeEndpoint:
    """Tests for GET /api/herald/exchange/{id}"""

    def test_GET_exchange__returns_200_for_pending(
        self, test_client, create_test_exchange
    ):
        """Test GET /api/herald/exchange/{id} returns 200 for pending exchange"""
        exchange_id = create_test_exchange(list_a="Test", list_b=None)
        print(f"\nDEBUG: Created exchange_id: {exchange_id}")

        response = test_client.get(f"/api/herald/exchange/{exchange_id}")
        print(f"DEBUG: Response status: {response.status_code}")
        print(f"DEBUG: Response body: {response.json()}")

        assert response.status_code == 200

    def test_GET_exchange__pending_status(self, test_client, create_test_exchange):
        """Test GET /api/herald/exchange/{id} shows waiting status"""
        exchange_id = create_test_exchange(list_a="Test", list_b=None)

        response = test_client.get(f"/api/herald/exchange/{exchange_id}")
        data = response.json()

        assert data["status"] == "waiting"
        assert "list_a" not in data

    def test_GET_exchange__complete_status(self, test_client, create_test_exchange):
        """Test GET /api/herald/exchange/{id} shows complete status"""
        exchange_id = create_test_exchange(list_a="List A", list_b="List B")

        response = test_client.get(f"/api/herald/exchange/{exchange_id}")
        data = response.json()

        assert data["status"] == "complete"
        assert data["list_a"] == "List A"
        assert data["list_b"] == "List B"

    def test_GET_exchange__404_for_invalid_id(self, test_client):
        """Test GET /api/herald/exchange/{id} returns 404 for invalid ID"""
        response = test_client.get("/api/herald/exchange/invalid-format")

        assert response.status_code == 404

    def test_GET_exchange__404_for_nonexistent_id(self, test_client):
        """Test GET /api/herald/exchange/{id} returns 404 for non-existent ID"""
        response = test_client.get("/api/herald/exchange/crimson-marine-charges-9999")

        assert response.status_code == 404


class TestRespondExchangeEndpoint:
    """Tests for POST /api/herald/exchange/{id}/respond"""

    def test_POST_respond__returns_200(self, test_client, create_test_exchange):
        """Test POST /api/herald/exchange/{id}/respond returns 200"""
        exchange_id = create_test_exchange(list_a="A", list_b=None)

        response = test_client.post(
            f"/api/herald/exchange/{exchange_id}/respond",
            json={"list_content": "Player B List"},
        )

        assert response.status_code == 200

    def test_POST_respond__completes_exchange(self, test_client, create_test_exchange):
        """Test POST /api/herald/exchange/{id}/respond completes exchange"""
        exchange_id = create_test_exchange(list_a="A", list_b=None)

        test_client.post(
            f"/api/herald/exchange/{exchange_id}/respond",
            json={"list_content": "Player B List"},
        )

        # Verify complete
        view = test_client.get(f"/api/herald/exchange/{exchange_id}")
        assert view.json()["status"] == "complete"

    def test_POST_respond__404_for_invalid_id(self, test_client):
        """Test POST /api/herald/exchange/{id}/respond returns 404 for invalid ID"""
        response = test_client.post(
            "/api/herald/exchange/invalid/respond", json={"list_content": "B"}
        )

        assert response.status_code == 404

    def test_POST_respond__400_for_already_complete(
        self, test_client, create_test_exchange
    ):
        """Test POST /api/herald/exchange/{id}/respond returns 400 if already complete"""
        exchange_id = create_test_exchange(list_a="A", list_b="B")

        response = test_client.post(
            f"/api/herald/exchange/{exchange_id}/respond",
            json={"list_content": "B Again"},
        )

        assert response.status_code == 400


class TestStatusEndpoint:
    """Tests for GET /api/herald/exchange/{id}/status"""

    def test_GET_status__returns_ready_bool(self, test_client, create_test_exchange):
        """Test GET /api/herald/exchange/{id}/status returns ready boolean"""
        exchange_id = create_test_exchange(list_a="A", list_b=None)

        response = test_client.get(f"/api/herald/exchange/{exchange_id}/status")

        assert response.status_code == 200
        assert "ready" in response.json()
        assert isinstance(response.json()["ready"], bool)


class TestStatsEndpoint:
    """Tests for GET /api/herald/stats"""

    def test_GET_stats__returns_200(self, test_client):
        """Test GET /api/herald/stats returns 200"""
        response = test_client.get("/api/herald/stats")

        assert response.status_code == 200

    def test_GET_stats__returns_statistics(self, test_client):
        """Test GET /api/herald/stats returns statistics"""
        response = test_client.get("/api/herald/stats")
        data = response.json()

        assert "completed_exchanges" in data
        assert isinstance(data["completed_exchanges"], int)
