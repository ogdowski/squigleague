# Testing Policy - Squig League

**Version**: 1.0  
**Effective Date**: November 20, 2025  
**Owner**: QA Team  
**Status**: MANDATORY

---

## Core Principles

### 1. Zero Tolerance Policy

**All code MUST have 100% test coverage. No exceptions.**

- Every function must have unit tests
- Every API endpoint must have integration tests
- Every user flow must have end-to-end tests
- Coverage reports are generated on every commit
- PRs are blocked if coverage drops below 100%

### 2. Truthfulness Policy (No Mocking)

**Tests must interact with real systems. Mocking is forbidden in critical paths.**

**Allowed:**
- ✅ Real PostgreSQL database (Docker test containers)
- ✅ Real FastAPI TestClient
- ✅ Real HTTP requests within test environment
- ✅ Test fixtures and factories for data generation
- ✅ Database transaction rollback for cleanup

**Forbidden:**
- ❌ Mocking database calls
- ❌ Mocking internal application logic
- ❌ Mocking API responses
- ❌ Using in-memory databases as substitutes
- ❌ Stubbing critical business logic

**Exception - External Services Only:**
- Email services (SendGrid, etc.)
- Payment gateways (Stripe, etc.)
- Third-party APIs (BSData, etc.)
- Cloud storage (S3, etc.)

**Rationale**: Mocks hide integration bugs. Real systems catch real problems.

### 3. Test-Driven Development (Encouraged)

**Write tests before or alongside implementation.**

Preferred workflow:
1. Write failing test that defines expected behavior
2. Implement minimum code to pass test
3. Refactor with confidence (tests protect you)
4. Repeat

### 4. Fast Feedback Loop

**Tests must run quickly to encourage frequent execution.**

- Unit tests: <5 seconds total
- Integration tests: <30 seconds total
- Full suite: <60 seconds total
- Use database transactions (rollback is fast)
- Parallelize independent tests
- Optimize slow tests or mark as `@pytest.mark.slow`

---

## Test Categories

### Unit Tests

**Purpose**: Test individual functions/classes in isolation

**Scope**: Single function or method  
**Dependencies**: Minimal (test fixtures only)  
**Speed**: Very fast (<100ms per test)  
**Location**: `tests/unit/{module}/test_{file}.py`

**Example:**
```python
# tests/unit/herald/test_words.py
def test_generate_exchange_id_format():
    """Test exchange ID follows format: adjective-noun-verb-XXXX"""
    exchange_id = generate_exchange_id(check_exists_callback=lambda x: False)
    
    parts = exchange_id.split('-')
    assert len(parts) == 4
    assert len(parts[3]) == 4  # 4-char hash
    assert all(c in '0123456789abcdef' for c in parts[3])
```

**Coverage Target**: 100% of all functions

### Integration Tests

**Purpose**: Test multiple components working together

**Scope**: Full workflows (database + API + business logic)  
**Dependencies**: Real PostgreSQL, FastAPI TestClient  
**Speed**: Fast (<1s per test)  
**Location**: `tests/integration/{module}/test_{feature}.py`

**Example:**
```python
# tests/integration/herald/test_exchange_flow.py
def test_full_exchange_workflow(test_client, test_db):
    """Test complete exchange creation and response flow"""
    # Create exchange (Player A)
    response = test_client.post("/api/herald/exchange/create", json={
        "list_content": "Army List A"
    })
    assert response.status_code == 200
    exchange_id = response.json()["exchange_id"]
    
    # Submit response (Player B)
    response = test_client.post(f"/api/herald/exchange/{exchange_id}/respond", json={
        "list_content": "Army List B"
    })
    assert response.status_code == 200
    
    # Verify both lists visible
    response = test_client.get(f"/api/herald/exchange/{exchange_id}")
    data = response.json()
    assert data["list_a"] == "Army List A"
    assert data["list_b"] == "Army List B"
```

**Coverage Target**: 100% of all API endpoints and workflows

### End-to-End Tests (Future - Phase 3+)

**Purpose**: Test complete user journeys through UI

**Scope**: Browser automation (Playwright/Selenium)  
**Dependencies**: Full application stack  
**Speed**: Slow (5-30s per test)  
**Location**: `tests/e2e/{feature}/test_{flow}.py`

**When to implement**: After frontend becomes complex (Phase 3+)

---

## Test Organization

### Directory Structure

```
squigleague/
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Shared fixtures and configuration
│   ├── pytest.ini               # Pytest configuration (symlink from root)
│   │
│   ├── unit/                    # Unit tests (fast, isolated)
│   │   ├── __init__.py
│   │   ├── herald/
│   │   │   ├── __init__.py
│   │   │   ├── test_database.py     # Database operations
│   │   │   ├── test_main.py         # API route handlers
│   │   │   ├── test_models.py       # Pydantic models
│   │   │   └── test_words.py        # Helper functions
│   │   └── squire/              # Future
│   │
│   ├── integration/             # Integration tests (real systems)
│   │   ├── __init__.py
│   │   ├── herald/
│   │   │   ├── __init__.py
│   │   │   ├── test_exchange_flow.py    # Full exchange workflow
│   │   │   ├── test_api_endpoints.py    # All API endpoints
│   │   │   ├── test_rate_limiting.py    # Rate limiting enforcement
│   │   │   └── test_admin_endpoints.py  # Admin endpoints
│   │   └── squire/              # Future
│   │
│   ├── fixtures/                # Test data and factories
│   │   ├── __init__.py
│   │   ├── factories.py         # Factory Boy factories
│   │   ├── herald_data.py       # Sample Herald data
│   │   └── squire_data.py       # Sample Squire data (future)
│   │
│   └── performance/             # Performance/load tests (optional)
│       ├── __init__.py
│       └── test_load.py         # k6 or Locust tests
│
├── pytest.ini                   # Root pytest configuration
├── requirements-dev.txt         # Test dependencies
└── .coveragerc                  # Coverage configuration
```

### File Naming Convention

**Test Files**: `test_{module}.py`  
**Test Functions**: `test_{behavior}__{context}`  
**Test Classes**: `Test{Feature}` (only for grouping related tests)

**Examples:**
```python
# Good
test_exchange_creation__valid_input()
test_exchange_creation__empty_list_rejected()
test_exchange_creation__exceeds_character_limit()

# Bad
test_1()
test_exchange()
my_test()
```

---

## Fixtures and Factories

### Fixture Guidelines

**Scope Levels:**
- `session`: Created once for entire test session (database engine)
- `module`: Created once per test module
- `class`: Created once per test class
- `function`: Created for each test (default, safest)

**Example:**
```python
# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from fastapi.testclient import TestClient

@pytest.fixture(scope="session")
def test_engine():
    """PostgreSQL test database engine (created once)"""
    engine = create_engine(TEST_DATABASE_URL)
    # Run schema migrations
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()

@pytest.fixture(scope="function")
def test_db(test_engine):
    """Clean database for each test (transaction rollback)"""
    connection = test_engine.connect()
    transaction = connection.begin()
    
    yield connection
    
    # Rollback ensures clean state for next test
    transaction.rollback()
    connection.close()

@pytest.fixture
def test_client():
    """FastAPI test client"""
    return TestClient(app)
```

### Factory Pattern (Factory Boy)

**Purpose**: Generate realistic test data

**Example:**
```python
# tests/fixtures/factories.py
import factory
from faker import Faker

fake = Faker()

class ExchangeFactory(factory.Factory):
    class Meta:
        model = dict
    
    exchange_id = factory.LazyFunction(
        lambda: f"{fake.word()}-{fake.word()}-{fake.word()}-{fake.hex_chars(4)}"
    )
    list_content = factory.LazyFunction(
        lambda: f"Test Army List\n{fake.text(200)}"
    )
    hash_value = factory.LazyFunction(lambda: fake.sha256())
    
# Usage in tests:
def test_something():
    exchange_data = ExchangeFactory()
    assert exchange_data["exchange_id"] is not None
```

---

## Running Tests

### Local Development

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/herald/test_words.py

# Run specific test function
pytest tests/unit/herald/test_words.py::test_generate_exchange_id

# Run with coverage
pytest --cov=herald --cov=squire --cov-report=html

# Run only unit tests (fast)
pytest -m unit

# Run only integration tests
pytest -m integration

# Run tests in parallel (faster)
pytest -n auto

# Run with verbose output
pytest -v

# Stop on first failure
pytest -x
```

### Just Commands

```bash
# Run all tests
just test

# Run with coverage report
just test-coverage

# Run only fast tests
just test-fast

# Run integration tests
just test-integration

# Watch mode (re-run on file changes)
just test-watch
```

### CI/CD Pipeline

Tests run automatically on:
- Every commit to `main` branch
- Every pull request
- Every push to `develop` branch

**Pipeline Steps:**
1. Start PostgreSQL test container
2. Install dependencies
3. Run linting (Black, isort, flake8)
4. Run tests with coverage
5. Upload coverage report
6. Block merge if:
   - Any test fails
   - Coverage < 100%
   - Linting errors exist

---

## Coverage Requirements

### Metrics

**Minimum Coverage**: 100% (enforced)  
**Coverage Types**:
- Line coverage: 100%
- Branch coverage: 100%
- Function coverage: 100%

### Exclusions (Rare)

Only these patterns may be excluded:

```python
# Explicit pragma
def debug_only_function():  # pragma: no cover
    """Only used in development"""
    pass

# Type checking blocks
if TYPE_CHECKING:  # pragma: no cover
    from typing import Protocol
```

**Approval Required**: All coverage exclusions require QA approval in PR review.

### Coverage Reports

**Generated Automatically:**
- `htmlcov/index.html` - Interactive HTML report
- `coverage.xml` - Machine-readable report
- Terminal summary on test run

**Review Process:**
1. Check coverage report after every test run
2. Identify uncovered lines (highlighted in red)
3. Write tests for uncovered code
4. Re-run until 100% coverage

---

## Assertions and Test Quality

### Good Assertions

**Specific and Clear:**
```python
# Good
assert exchange_id == "crimson-ork-charges-7a2f"
assert response.status_code == 200
assert "exchange_id" in response.json()
assert len(battles) == 5

# Bad
assert exchange_id  # Too vague
assert response  # What are we checking?
assert True  # Meaningless
```

### Multiple Assertions (When Appropriate)

**Related checks in one test:**
```python
def test_exchange_response_structure():
    """Test API response has correct structure"""
    response = create_exchange(test_data)
    
    # All assertions test the same concept (response structure)
    assert response.status_code == 200
    assert "exchange_id" in response.json()
    assert "hash_a" in response.json()
    assert isinstance(response.json()["exchange_id"], str)
```

**Separate tests for separate behaviors:**
```python
# Good - separate concerns
def test_exchange_creation__returns_200():
    assert response.status_code == 200

def test_exchange_creation__generates_unique_id():
    assert response.json()["exchange_id"] is not None

# Bad - testing everything in one test
def test_exchange_creation():
    # Too many unrelated assertions
    assert response.status_code == 200
    assert database_has_exchange()
    assert rate_limit_decremented()
    assert email_sent()
```

### Error Testing

**Always test error cases:**
```python
def test_exchange_creation__empty_list_rejected():
    """Test that empty list content is rejected"""
    response = test_client.post("/api/herald/exchange/create", json={
        "list_content": ""
    })
    
    assert response.status_code == 422  # Validation error
    assert "List content cannot be empty" in response.json()["detail"]

def test_exchange_creation__exceeds_character_limit():
    """Test that lists over 50k characters are rejected"""
    huge_list = "X" * 50001
    response = test_client.post("/api/herald/exchange/create", json={
        "list_content": huge_list
    })
    
    assert response.status_code == 422
```

---

## Database Testing

### Test Database Setup

**Use Docker PostgreSQL container:**
```yaml
# docker-compose.test.yml
services:
  postgres-test:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: test_user
      POSTGRES_PASSWORD: test_password
      POSTGRES_DB: test_squigleague
    ports:
      - "5433:5432"
    tmpfs:
      - /var/lib/postgresql/data  # In-memory for speed
```

**Connection:**
```python
TEST_DATABASE_URL = "postgresql://test_user:test_password@localhost:5433/test_squigleague"
```

### Transaction Rollback Pattern

**Every test gets clean database:**
```python
@pytest.fixture(scope="function")
def test_db(test_engine):
    """Provide clean database for each test"""
    connection = test_engine.connect()
    transaction = connection.begin()
    
    yield connection
    
    # Rollback transaction - faster than truncating tables
    transaction.rollback()
    connection.close()
```

**Why this works:**
- Each test runs in a transaction
- Transaction rolls back after test completes
- Database returns to clean state
- Much faster than `DELETE FROM` or `TRUNCATE`
- Tests can run in parallel

### Testing Database Operations

```python
def test_create_exchange__saves_to_database(test_db):
    """Test exchange is persisted to database"""
    # Create exchange
    exchange_id = create_exchange(
        exchange_id="test-exchange-id-abc1",
        list_a="Test List",
        hash_a="abc123...",
        timestamp_a=datetime.now()
    )
    
    # Verify in database (real query, no mocking)
    result = test_db.execute(
        text("SELECT id, list_a FROM herald_exchanges WHERE id = :id"),
        {"id": exchange_id}
    ).fetchone()
    
    assert result is not None
    assert result.id == "test-exchange-id-abc1"
    assert result.list_a == "Test List"
```

---

## API Testing

### FastAPI TestClient

**Use TestClient for all API tests:**
```python
from fastapi.testclient import TestClient
from herald.main import app

client = TestClient(app)

def test_health_endpoint():
    """Test health check returns 200"""
    response = client.get("/health")
    
    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "module": "herald",
        "database": "connected"
    }
```

### Testing All HTTP Methods

```python
# GET
def test_get_exchange(test_client):
    response = test_client.get("/api/herald/exchange/test-id")
    assert response.status_code == 200

# POST
def test_create_exchange(test_client):
    response = test_client.post("/api/herald/exchange/create", json={
        "list_content": "Test"
    })
    assert response.status_code == 200

# PUT (if used)
def test_update_exchange(test_client):
    response = test_client.put("/api/herald/exchange/test-id", json={...})
    assert response.status_code == 200

# DELETE (if used)
def test_delete_exchange(test_client):
    response = test_client.delete("/api/herald/exchange/test-id")
    assert response.status_code == 204
```

### Testing Rate Limiting

```python
def test_rate_limiting__blocks_after_limit(test_client):
    """Test rate limiting blocks requests after limit"""
    # Make requests up to limit (10/hour for create)
    for i in range(10):
        response = test_client.post("/api/herald/exchange/create", json={
            "list_content": f"Test {i}"
        })
        assert response.status_code == 200
    
    # 11th request should be blocked
    response = test_client.post("/api/herald/exchange/create", json={
        "list_content": "Test 11"
    })
    assert response.status_code == 429  # Too Many Requests
    assert "rate limit" in response.json()["detail"].lower()
```

---

## Performance Testing

### Response Time Assertions

```python
import time

def test_api_response_time__under_500ms(test_client):
    """Test API responds within 500ms"""
    start = time.time()
    response = test_client.get("/api/herald/stats")
    duration = time.time() - start
    
    assert response.status_code == 200
    assert duration < 0.5  # 500ms
```

### Load Testing (Optional)

**Use pytest-benchmark or k6:**
```python
def test_exchange_creation_throughput(benchmark):
    """Benchmark exchange creation performance"""
    result = benchmark(create_exchange, test_data)
    assert result is not None
```

---

## Continuous Integration

### GitHub Actions Workflow

**File**: `.github/workflows/test.yml`

**Key Requirements:**
- Run on every PR and push to main
- Block merge if tests fail
- Block merge if coverage < 100%
- Upload coverage reports
- Cache dependencies for speed

**Status Badge:**
```markdown
![Tests](https://github.com/ogdowski/squigleague/workflows/Tests/badge.svg)
![Coverage](https://codecov.io/gh/ogdowski/squigleague/branch/main/graph/badge.svg)
```

---

## Test Maintenance

### When to Update Tests

**Always update tests when:**
- Adding new feature (write tests first or alongside)
- Fixing bug (add test that would have caught it)
- Refactoring code (tests should still pass)
- Changing API contracts (update integration tests)
- Updating dependencies (ensure compatibility)

### Flaky Tests (Zero Tolerance)

**A flaky test that passes/fails randomly is a bug.**

**Common causes:**
- Timing/race conditions → Fix with proper synchronization
- Shared state between tests → Use transaction rollback
- External dependencies → Mock external services only
- Random data without seed → Use seeded Faker

**Resolution:**
1. Identify flaky test
2. Fix root cause (don't just re-run)
3. Add to CI with multiple runs to verify fix
4. Never merge code with flaky tests

---

## Documentation Requirements

### Test Docstrings

**Every test must have a docstring:**
```python
def test_exchange_creation__valid_input():
    """Test that valid exchange data creates exchange successfully
    
    Verifies:
    - Returns 200 status code
    - Returns exchange_id in response
    - Exchange is saved to database
    """
    # Test implementation
```

### Module Documentation

**Every test module should have module docstring:**
```python
# tests/integration/herald/test_exchange_flow.py
"""Integration tests for Herald exchange workflows

Tests the complete exchange creation and response flow,
including database persistence, hash generation, and
API responses.
"""
```

---

## Review Checklist

**Before submitting PR, verify:**

- [ ] All tests pass locally (`pytest`)
- [ ] Coverage is 100% (`pytest --cov`)
- [ ] No flaky tests (run multiple times)
- [ ] Tests are well-named and documented
- [ ] No mocking of internal logic
- [ ] Database tests use transaction rollback
- [ ] Error cases are tested
- [ ] Edge cases are covered
- [ ] Code is formatted (`black .`)
- [ ] Imports are sorted (`isort .`)
- [ ] No linting errors (`flake8`)

---

## Enforcement

### Automated Enforcement

**CI Pipeline Blocks Merge If:**
- Any test fails
- Coverage < 100%
- Linting errors exist
- Type checking fails (mypy)

### Manual Review

**Code reviewers check:**
- Test quality (meaningful assertions)
- Test coverage (no artificial 100%)
- No prohibited mocking
- Proper fixture usage
- Clear test documentation

### Consequences

**For violations:**
- PR rejected
- Coverage exclusions removed
- Mocked tests rewritten
- Flaky tests fixed before merge

---

## Questions?

**Slack**: #testing  
**Email**: qa-team@squigleague.com  
**Documentation**: [docs/TESTING.md](TESTING.md)

**Remember**: Tests are not a burden - they're your safety net. Write tests, sleep well.

---

**Last Updated**: November 20, 2025  
**Next Review**: January 20, 2026
