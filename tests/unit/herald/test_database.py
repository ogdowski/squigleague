"""
Unit tests for herald/database.py - Database operations

Tests all CRUD operations, cleanup functions, and monitoring.
Uses real PostgreSQL database with table truncation for isolation.
"""

from datetime import datetime, timedelta

import pytest
from sqlalchemy import text

from herald import database


class TestCreateExchange:
    """Tests for create_exchange() function"""

    def test_create_exchange__success(self, test_engine):
        """Test successful exchange creation"""
        exchange_id = "test-exchange-001"
        list_content = "Test Army List\n1000 points"
        hash_value = "abc123def456"
        timestamp = datetime.now()

        success = database.create_exchange(
            exchange_id=exchange_id,
            list_a=list_content,
            hash_a=hash_value,
            timestamp_a=timestamp,
        )

        assert success is True

        # Verify in database
        with test_engine.connect() as conn:
            result = conn.execute(
                text("SELECT id, list_a, hash_a FROM herald_exchanges WHERE id = :id"),
                {"id": exchange_id},
            ).fetchone()

        assert result is not None
        assert result.id == exchange_id
        assert result.list_a == list_content
        assert result.hash_a == hash_value

    def test_create_exchange__saves_all_fields(self, test_engine):
        """Test that all fields are saved correctly"""
        exchange_id = "test-exchange-002"
        list_content = "Complete Army List"
        hash_value = "full_hash_value"
        timestamp = datetime(2025, 11, 20, 10, 30, 0)

        database.create_exchange(
            exchange_id=exchange_id,
            list_a=list_content,
            hash_a=hash_value,
            timestamp_a=timestamp,
        )

        with test_engine.connect() as conn:
            result = conn.execute(
                text("SELECT * FROM herald_exchanges WHERE id = :id"),
                {"id": exchange_id},
            ).fetchone()

        assert result.id == exchange_id
        assert result.list_a == list_content
        assert result.hash_a == hash_value
        # Compare timestamps (database returns timezone-aware, convert to UTC)
        assert result.timestamp_a.replace(tzinfo=None) == timestamp
        assert result.list_b is None
        assert result.hash_b is None
        assert result.timestamp_b is None

    def test_create_exchange__duplicate_id_fails(self):
        """Test that creating exchange with duplicate ID fails"""
        exchange_id = "duplicate-id"

        # Create first exchange
        database.create_exchange(
            exchange_id=exchange_id,
            list_a="First List",
            hash_a="hash1",
            timestamp_a=datetime.now(),
        )

        # Attempt to create duplicate
        success = database.create_exchange(
            exchange_id=exchange_id,
            list_a="Second List",
            hash_a="hash2",
            timestamp_a=datetime.now(),
        )

        assert success is False


class TestExchangeExists:
    """Tests for exchange_exists() function"""

    def test_exchange_exists__returns_true_when_exists(self, create_test_exchange):
        """Test that exchange_exists returns True for existing exchange"""
        exchange_id = create_test_exchange(exchange_id="existing-exchange")

        exists = database.exchange_exists(exchange_id)

        assert exists is True

    def test_exchange_exists__returns_false_when_not_exists(self):
        """Test that exchange_exists returns False for non-existent exchange"""
        exists = database.exchange_exists("nonexistent-id")

        assert exists is False


class TestGetExchange:
    """Tests for get_exchange() function"""

    def test_get_exchange__returns_exchange_data(self, create_test_exchange):
        """Test retrieving exchange data"""
        exchange_id = create_test_exchange(
            exchange_id="test-get-001", list_a="Player A List", hash_a="hash_a_value"
        )

        result = database.get_exchange(exchange_id)

        assert result is not None
        assert result["id"] == exchange_id
        assert result["list_a"] == "Player A List"
        assert result["hash_a"] == "hash_a_value"

    def test_get_exchange__returns_none_when_not_found(self):
        """Test that get_exchange returns None for non-existent ID"""
        result = database.get_exchange("nonexistent-id")

        assert result is None

    def test_get_exchange__includes_list_b_when_complete(self, create_test_exchange):
        """Test that complete exchange includes list_b"""
        exchange_id = create_test_exchange(
            exchange_id="complete-exchange",
            list_a="Player A",
            list_b="Player B",
            hash_a="hash_a",
            hash_b="hash_b",
        )

        result = database.get_exchange(exchange_id)

        assert result["list_b"] == "Player B"
        assert result["hash_b"] == "hash_b"


class TestUpdateExchangeWithListB:
    """Tests for update_exchange_with_list_b() function"""

    def test_update_exchange_with_list_b__success(
        self, create_test_exchange, test_engine
    ):
        """Test successful update with list_b"""
        exchange_id = create_test_exchange(
            exchange_id="update-test", list_a="Player A", list_b=None
        )

        list_b = "Player B List"
        hash_b = "hash_b_value"
        timestamp_b = datetime.now()

        success = database.update_exchange_with_list_b(
            exchange_id=exchange_id,
            list_b=list_b,
            hash_b=hash_b,
            timestamp_b=timestamp_b,
        )

        assert success is True

        with test_engine.connect() as conn:
            result = conn.execute(
                text("SELECT list_b, hash_b FROM herald_exchanges WHERE id = :id"),
                {"id": exchange_id},
            ).fetchone()

        assert result.list_b == list_b
        assert result.hash_b == hash_b

    def test_update_exchange_with_list_b__only_updates_when_null(
        self, create_test_exchange
    ):
        """Test that update only works when list_b is NULL"""
        exchange_id = create_test_exchange(
            exchange_id="already-complete",
            list_a="Player A",
            list_b="Original Player B",
        )

        success = database.update_exchange_with_list_b(
            exchange_id=exchange_id,
            list_b="New Player B",
            hash_b="new_hash",
            timestamp_b=datetime.now(),
        )

        assert success is False

    def test_update_exchange_with_list_b__fails_for_nonexistent(self):
        """Test that update fails for non-existent exchange"""
        success = database.update_exchange_with_list_b(
            exchange_id="nonexistent",
            list_b="Player B",
            hash_b="hash",
            timestamp_b=datetime.now(),
        )

        assert success is False


class TestExchangeIsComplete:
    """Tests for exchange_is_complete() function"""

    def test_exchange_is_complete__returns_true_when_complete(
        self, create_test_exchange
    ):
        """Test returns True for complete exchange"""
        exchange_id = create_test_exchange(
            exchange_id="complete", list_a="A", list_b="B"
        )

        is_complete = database.exchange_is_complete(exchange_id)

        assert is_complete is True

    def test_exchange_is_complete__returns_false_when_pending(
        self, create_test_exchange
    ):
        """Test returns False for pending exchange"""
        exchange_id = create_test_exchange(
            exchange_id="pending", list_a="A", list_b=None
        )

        is_complete = database.exchange_is_complete(exchange_id)

        assert is_complete is False

    def test_exchange_is_complete__returns_false_for_nonexistent(self):
        """Test returns False for non-existent exchange"""
        is_complete = database.exchange_is_complete("nonexistent")

        assert is_complete is False


class TestLogRequest:
    """Tests for log_request() function"""

    def test_log_request__saves_to_database(self, test_engine):
        """Test that request logging saves to database"""
        database.log_request(
            ip="192.168.1.100", endpoint="/api/test", user_agent="TestAgent/1.0"
        )

        with test_engine.connect() as conn:
            result = conn.execute(
                text("SELECT * FROM herald_request_log WHERE ip = :ip"),
                {"ip": "192.168.1.100"},
            ).fetchone()

        assert result is not None
        assert result.endpoint == "/api/test"
        assert result.user_agent == "TestAgent/1.0"

    def test_log_request__handles_error_gracefully(self):
        """Test that logging errors don't crash"""
        # This should not raise an exception
        database.log_request(ip=None, endpoint="/test", user_agent="Test")


class TestGetAbusiveIPs:
    """Tests for get_abusive_ips() function"""

    def test_get_abusive_ips__returns_ips_over_threshold(self, test_engine):
        """Test finding IPs exceeding request threshold"""
        # Create 150 requests from one IP
        abusive_ip = "10.0.0.50"
        with test_engine.connect() as conn:
            for i in range(150):
                conn.execute(
                    text(
                        "INSERT INTO herald_request_log (ip, endpoint, user_agent) VALUES (:ip, :ep, :ua)"
                    ),
                    {"ip": abusive_ip, "ep": f"/test/{i}", "ua": "bot"},
                )
            conn.commit()

        result = database.get_abusive_ips(min_requests=100, hours=1)

        assert len(result) > 0
        assert any(r["ip"] == abusive_ip for r in result)

    def test_get_abusive_ips__filters_by_time_window(self, test_engine):
        """Test that time window filtering works"""
        # Create old requests (should be excluded)
        old_time = datetime.now() - timedelta(hours=25)

        with test_engine.connect() as conn:
            for i in range(200):
                conn.execute(
                    text(
                        "INSERT INTO herald_request_log (ip, endpoint, user_agent, timestamp) VALUES (:ip, :ep, :ua, :ts)"
                    ),
                    {"ip": "10.0.0.99", "ep": "/old", "ua": "bot", "ts": old_time},
                )
            conn.commit()

        result = database.get_abusive_ips(min_requests=100, hours=24)

        # Should not find old requests
        assert not any(r["ip"] == "10.0.0.99" for r in result)

    def test_get_abusive_ips__empty_when_no_abuse(self):
        """Test returns empty list when no abuse detected"""
        result = database.get_abusive_ips(min_requests=1000, hours=1)

        assert result == []


class TestDeleteOldExchanges:
    """Tests for delete_old_exchanges() function"""

    def test_delete_old_exchanges__deletes_old_only(self, test_engine):
        """Test deletes only old exchanges"""
        old_time = datetime.now() - timedelta(days=35)
        recent_time = datetime.now() - timedelta(days=5)

        with test_engine.connect() as conn:
            conn.execute(
                text(
                    "INSERT INTO herald_exchanges (id, list_a, hash_a, timestamp_a, created_at) VALUES (:id, :la, :ha, :ta, :ca)"
                ),
                {
                    "id": "old-exchange",
                    "la": "old",
                    "ha": "hash",
                    "ta": old_time,
                    "ca": old_time,
                },
            )
            conn.execute(
                text(
                    "INSERT INTO herald_exchanges (id, list_a, hash_a, timestamp_a, created_at) VALUES (:id, :la, :ha, :ta, :ca)"
                ),
                {
                    "id": "recent-exchange",
                    "la": "recent",
                    "ha": "hash",
                    "ta": recent_time,
                    "ca": recent_time,
                },
            )
            conn.commit()

        deleted = database.delete_old_exchanges(days=30)

        assert deleted >= 1

        # Verify recent still exists
        with test_engine.connect() as conn:
            result = conn.execute(
                text("SELECT id FROM herald_exchanges WHERE id = 'recent-exchange'")
            ).fetchone()
        assert result is not None

    def test_delete_old_exchanges__preserves_recent(self, create_test_exchange):
        """Test that recent exchanges are preserved"""
        exchange_id = create_test_exchange(exchange_id="recent")

        database.delete_old_exchanges(days=30)

        # Should still exist
        assert database.exchange_exists(exchange_id)

    def test_delete_old_exchanges__returns_count(self, test_engine):
        """Test returns count of deleted exchanges"""
        old_time = datetime.now() - timedelta(days=40)

        with test_engine.connect() as conn:
            for i in range(5):
                conn.execute(
                    text(
                        "INSERT INTO herald_exchanges (id, list_a, hash_a, timestamp_a, created_at) VALUES (:id, :la, :ha, :ta, :ca)"
                    ),
                    {
                        "id": f"old-{i}",
                        "la": "old",
                        "ha": "hash",
                        "ta": old_time,
                        "ca": old_time,
                    },
                )
            conn.commit()

        deleted = database.delete_old_exchanges(days=30)

        assert deleted >= 5


class TestDeleteOldLogs:
    """Tests for delete_old_logs() function"""

    def test_delete_old_logs__deletes_old_only(self, test_engine):
        """Test deletes only old logs"""
        old_time = datetime.now() - timedelta(days=35)

        with test_engine.connect() as conn:
            for i in range(10):
                conn.execute(
                    text(
                        "INSERT INTO herald_request_log (ip, endpoint, user_agent, timestamp) VALUES (:ip, :ep, :ua, :ts)"
                    ),
                    {"ip": "10.0.0.1", "ep": "/old", "ua": "old", "ts": old_time},
                )
            conn.commit()

        deleted = database.delete_old_logs(days=30)

        assert deleted >= 10

    def test_delete_old_logs__returns_count(self, test_engine):
        """Test returns count of deleted logs"""
        old_time = datetime.now() - timedelta(days=40)

        with test_engine.connect() as conn:
            for i in range(15):
                conn.execute(
                    text(
                        "INSERT INTO herald_request_log (ip, endpoint, user_agent, timestamp) VALUES (:ip, :ep, :ua, :ts)"
                    ),
                    {"ip": f"10.0.0.{i}", "ep": "/test", "ua": "test", "ts": old_time},
                )
            conn.commit()

        deleted = database.delete_old_logs(days=30)

        assert deleted >= 15


class TestCheckDatabaseHealth:
    """Tests for check_database_health() function"""

    def test_check_database_health__returns_true_when_connected(self):
        """Test returns True when database is healthy"""
        healthy = database.check_database_health()

        assert healthy is True

    def test_check_database_health__handles_connection_error(self, monkeypatch):
        """Test handles database connection errors gracefully"""

        # Mock the database connection to fail
        def mock_get_db():
            raise Exception("Connection failed")

        monkeypatch.setattr(database, "get_db", mock_get_db)

        healthy = database.check_database_health()

        assert healthy is False


class TestGetStats:
    """Tests for get_stats() function"""

    def test_get_stats__returns_all_counts(self, create_test_exchange):
        """Test returns dictionary with all statistics"""
        # Create test data
        create_test_exchange(exchange_id="stat-1", list_a="A", list_b="B")
        create_test_exchange(exchange_id="stat-2", list_a="A", list_b=None)

        stats = database.get_stats()

        assert "total_exchanges" in stats
        assert "complete_exchanges" in stats
        assert "pending_exchanges" in stats

    def test_get_stats__counts_complete_exchanges(self, create_test_exchange):
        """Test correctly counts complete exchanges"""
        create_test_exchange(exchange_id="complete-1", list_a="A", list_b="B")
        create_test_exchange(exchange_id="complete-2", list_a="A", list_b="B")

        stats = database.get_stats()

        assert stats["complete_exchanges"] >= 2

    def test_get_stats__counts_pending_exchanges(self, create_test_exchange):
        """Test correctly counts pending exchanges"""
        create_test_exchange(exchange_id="pending-1", list_a="A", list_b=None)
        create_test_exchange(exchange_id="pending-2", list_a="A", list_b=None)

        stats = database.get_stats()

        assert stats["pending_exchanges"] >= 2
