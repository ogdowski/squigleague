"""
Shared test fixtures and configuration for Herald module tests

Sets DATABASE_URL environment variable to redirect production code to test database.
Uses table truncation for cleanup instead of transaction rollback.
"""

import os
import sys
from datetime import datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text

# Add herald directory to path so 'import database' works
herald_path = Path(__file__).parent.parent / "herald"
sys.path.insert(0, str(herald_path))

# Test database configuration
TEST_DB_URL = "postgresql://test_user:test_password@localhost:5433/test_squigleague"

# CRITICAL: Set environment variables BEFORE importing any herald modules
os.environ["DATABASE_URL"] = TEST_DB_URL
os.environ["TESTING"] = "true"  # Disable scheduler and other background tasks
os.environ["TESTING"] = "true"  # Disable scheduler in tests


@pytest.fixture(scope="session")
def test_engine():
    """Create test database engine (session scope)"""
    engine = create_engine(TEST_DB_URL, echo=False)
    yield engine
    engine.dispose()


@pytest.fixture(
    autouse=False
)  # DISABLED - causes deadlocks when running multiple test files
def cleanup_database(test_engine):
    """Clean database after each test"""
    yield

    # Truncate tables after each test with autocommit to avoid locks
    with test_engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
        conn.execute(text("TRUNCATE TABLE herald_exchanges RESTART IDENTITY CASCADE"))
        conn.execute(text("TRUNCATE TABLE herald_request_log RESTART IDENTITY CASCADE"))


@pytest.fixture
def test_client(test_engine):
    """Provide FastAPI TestClient"""
    # Import AFTER DATABASE_URL is set
    from herald import main as herald_main

    client = TestClient(herald_main.app)
    yield client


@pytest.fixture
def create_test_exchange(test_engine):
    """Factory for creating test exchanges directly in database"""

    def _create_exchange(
        exchange_id: str = "test-exchange-001",
        list_a: str = "Test List A",
        list_b: str = None,
        hash_a: str = "abc123",
        hash_b: str = None,
        timestamp_a: datetime = None,
        timestamp_b: datetime = None,
    ) -> str:
        if timestamp_a is None:
            timestamp_a = datetime.now()
        if timestamp_b is None and list_b is not None:
            timestamp_b = datetime.now()

        query = text(
            """
            INSERT INTO herald_exchanges 
            (id, list_a, hash_a, timestamp_a, list_b, hash_b, timestamp_b)
            VALUES (:id, :list_a, :hash_a, :timestamp_a, :list_b, :hash_b, :timestamp_b)
        """
        )

        with test_engine.connect().execution_options(
            isolation_level="AUTOCOMMIT"
        ) as conn:
            conn.execute(
                query,
                {
                    "id": exchange_id,
                    "list_a": list_a,
                    "hash_a": hash_a,
                    "timestamp_a": timestamp_a,
                    "list_b": list_b,
                    "hash_b": hash_b,
                    "timestamp_b": timestamp_b,
                },
            )

        return exchange_id

    return _create_exchange


@pytest.fixture
def get_db_exchange(test_engine):
    """Fixture for retrieving exchange from database"""

    def _get_exchange(exchange_id: str):
        query = text("SELECT * FROM herald_exchanges WHERE id = :id")

        with test_engine.connect() as conn:
            result = conn.execute(query, {"id": exchange_id}).fetchone()

        return result

    return _get_exchange


@pytest.fixture
def count_db_records(test_engine):
    """Fixture for counting records in tables"""

    def _count(table: str, where: str = None):
        if where:
            query = text(f"SELECT COUNT(*) as count FROM {table} WHERE {where}")
        else:
            query = text(f"SELECT COUNT(*) as count FROM {table}")

        with test_engine.connect() as conn:
            result = conn.execute(query).fetchone()

        return result.count

    return _count


# Pytest configuration hooks
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "slow: Slow-running tests")
    config.addinivalue_line("markers", "asyncio: Async tests")


def pytest_collection_modifyitems(config, items):
    """Automatically mark tests based on their path"""
    for item in items:
        # Add 'unit' marker to tests in tests/unit/
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)

        # Add 'integration' marker to tests in tests/integration/
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
