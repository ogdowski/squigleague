# Testing Guide - Squig League

Quick reference for writing and running tests in the Squig League project.

---

## Quick Start

### Running Tests

```bash
# All tests
pytest

# Specific module
pytest tests/unit/herald/

# Specific test
pytest tests/unit/herald/test_words.py::test_generate_exchange_id

# With coverage
pytest --cov=herald --cov=squire --cov-report=html

# Parallel execution
pytest -n auto

# Watch mode (re-run on file changes)
ptw -- tests/
```

### Writing Your First Test

```python
# tests/unit/herald/test_my_feature.py
def test_my_feature__expected_behavior():
    """Test that my feature behaves as expected"""
    # Arrange
    input_data = {"key": "value"}
    
    # Act
    result = my_function(input_data)
    
    # Assert
    assert result["key"] == "value"
    assert result["processed"] is True
```

---

## Test Structure (AAA Pattern)

**Arrange → Act → Assert**

```python
def test_exchange_creation__returns_exchange_id():
    """Test exchange creation returns valid exchange ID"""
    
    # Arrange - Set up test data
    list_content = "Test Army List\n1000 points"
    
    # Act - Execute the function under test
    result = create_exchange(list_content)
    
    # Assert - Verify the outcome
    assert result["exchange_id"] is not None
    assert "-" in result["exchange_id"]
```

---

## Common Test Patterns

### Testing API Endpoints

```python
def test_create_exchange_endpoint(test_client):
    """Test POST /api/herald/exchange/create"""
    response = test_client.post("/api/herald/exchange/create", json={
        "list_content": "Test Army List"
    })
    
    assert response.status_code == 200
    assert "exchange_id" in response.json()
```

### Testing Database Operations

```python
def test_save_exchange__persists_to_database(test_db):
    """Test exchange is saved to database"""
    # Create exchange
    exchange_id = create_exchange_in_db(test_db, {
        "id": "test-exchange-abc1",
        "list_a": "Test List",
        "hash_a": "abc123..."
    })
    
    # Verify in database
    result = test_db.execute(
        text("SELECT * FROM herald_exchanges WHERE id = :id"),
        {"id": exchange_id}
    ).fetchone()
    
    assert result is not None
    assert result.list_a == "Test List"
```

### Testing Validation

```python
def test_exchange_creation__rejects_empty_list():
    """Test that empty list content is rejected"""
    with pytest.raises(ValidationError) as exc_info:
        ExchangeCreate(list_content="")
    
    assert "list_content" in str(exc_info.value)
```

### Testing Error Cases

```python
def test_get_exchange__returns_404_for_nonexistent_id(test_client):
    """Test GET /api/herald/exchange/{id} returns 404 for invalid ID"""
    response = test_client.get("/api/herald/exchange/nonexistent-id")
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
```

---

## Fixtures

### Using Fixtures

```python
# tests/conftest.py defines fixtures
@pytest.fixture
def test_client():
    return TestClient(app)

# Use in tests
def test_something(test_client):
    response = test_client.get("/health")
    assert response.status_code == 200
```

### Common Fixtures

**test_client** - FastAPI TestClient
```python
def test_api(test_client):
    response = test_client.get("/api/endpoint")
```

**test_db** - Clean database connection (auto-rollback)
```python
def test_database(test_db):
    result = test_db.execute(text("SELECT 1"))
```

**sample_exchange_data** - Pre-populated test data
```python
def test_with_data(sample_exchange_data):
    exchange = sample_exchange_data["exchange"]
    assert exchange["id"] is not None
```

### Creating Custom Fixtures

```python
# tests/conftest.py
@pytest.fixture
def sample_battle():
    """Provide sample battle data for tests"""
    return {
        "id": "battle-001",
        "player1": "Alice",
        "player2": "Bob",
        "result": "player1_win"
    }

# Use in test
def test_battle(sample_battle):
    assert sample_battle["result"] == "player1_win"
```

---

## Parametrized Tests

**Test multiple inputs without code duplication:**

```python
@pytest.mark.parametrize("input_value,expected", [
    ("", False),
    ("valid-exchange-id-abc1", True),
    ("invalid", False),
    ("too-short", False),
])
def test_exchange_id_validation(input_value, expected):
    """Test exchange ID validation with multiple inputs"""
    result = is_valid_exchange_id(input_value)
    assert result == expected
```

**Multiple parameters:**

```python
@pytest.mark.parametrize("list_content,expected_status", [
    ("Valid List", 200),
    ("", 422),  # Empty
    ("X" * 50001, 422),  # Too long
])
def test_create_exchange__various_inputs(test_client, list_content, expected_status):
    """Test exchange creation with various list contents"""
    response = test_client.post("/api/herald/exchange/create", json={
        "list_content": list_content
    })
    assert response.status_code == expected_status
```

---

## Testing Async Code

**Use pytest-asyncio:**

```python
import pytest

@pytest.mark.asyncio
async def test_async_database_operation():
    """Test asynchronous database query"""
    async with async_db_connection() as conn:
        result = await conn.execute("SELECT 1")
        assert result is not None
```

---

## Markers

**Categorize and filter tests:**

```python
# Mark as slow test
@pytest.mark.slow
def test_expensive_operation():
    """Test that takes a long time"""
    result = process_large_dataset()
    assert result is not None

# Mark as integration test
@pytest.mark.integration
def test_full_workflow():
    """Integration test for complete workflow"""
    pass

# Run only specific markers
# pytest -m "not slow"  # Skip slow tests
# pytest -m integration  # Run only integration tests
```

---

## Test Data Factories

**Generate realistic test data with Factory Boy:**

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
        lambda: f"Army List\n{fake.text(200)}"
    )

# Usage in tests
def test_with_factory_data():
    exchange = ExchangeFactory()
    assert exchange["exchange_id"] is not None
    assert len(exchange["list_content"]) > 10
```

---

## Coverage

### Viewing Coverage Reports

```bash
# Generate HTML coverage report
pytest --cov=herald --cov=squire --cov-report=html

# Open report
start htmlcov/index.html  # Windows
open htmlcov/index.html   # macOS
xdg-open htmlcov/index.html  # Linux
```

### Interpreting Coverage

**Green Lines** - Covered by tests  
**Red Lines** - Not covered (must add tests)  
**Yellow Lines** - Partially covered (add branch tests)

### Excluding Code (Rare)

```python
def debug_function():  # pragma: no cover
    """Only used in development, not tested"""
    print("Debug info")
```

**Requires approval** - Coverage exclusions need QA review.

---

## Debugging Tests

### Print Debugging

```python
def test_something():
    result = my_function()
    print(f"Result: {result}")  # Will show in pytest output with -s
    assert result is not None

# Run with output
pytest -s tests/unit/herald/test_file.py
```

### Using pdb (Python Debugger)

```python
def test_something():
    result = my_function()
    import pdb; pdb.set_trace()  # Breakpoint
    assert result is not None

# Run test - will drop into debugger
pytest tests/unit/herald/test_file.py
```

### Verbose Output

```bash
# Show test names
pytest -v

# Show print statements
pytest -s

# Show full diff on assertion failures
pytest -vv
```

---

## Common Issues

### Issue: Test Database Not Clean

**Problem**: Tests fail due to data from previous tests

**Solution**: Ensure `test_db` fixture uses transaction rollback
```python
@pytest.fixture(scope="function")
def test_db(test_engine):
    connection = test_engine.connect()
    transaction = connection.begin()
    yield connection
    transaction.rollback()  # Clean up
    connection.close()
```

### Issue: Flaky Tests

**Problem**: Test passes/fails randomly

**Solution**: Identify source of randomness
- Use seeded Faker: `fake = Faker(); Faker.seed(12345)`
- Avoid time-dependent tests without mocking time
- Use proper synchronization for async code
- Ensure no shared state between tests

### Issue: Import Errors

**Problem**: `ModuleNotFoundError: No module named 'herald'`

**Solution**: Ensure PYTHONPATH includes project root
```bash
# In pytest.ini
[pytest]
pythonpath = .
```

### Issue: Fixtures Not Found

**Problem**: `fixture 'test_client' not found`

**Solution**: Ensure `conftest.py` exists in tests/ directory
```
tests/
├── conftest.py  ← Must exist
└── unit/
    └── test_file.py
```

---

## Best Practices

### DO:
- ✅ Write descriptive test names (`test_feature__scenario`)
- ✅ Use AAA pattern (Arrange, Act, Assert)
- ✅ Test one behavior per test
- ✅ Use fixtures for shared setup
- ✅ Test error cases and edge cases
- ✅ Keep tests fast (< 1s each)
- ✅ Use real database with transaction rollback
- ✅ Write tests alongside implementation

### DON'T:
- ❌ Mock internal application logic
- ❌ Write vague test names (`test_1`, `test_exchange`)
- ❌ Test multiple unrelated behaviors in one test
- ❌ Share state between tests
- ❌ Skip error case testing
- ❌ Leave tests commented out
- ❌ Use production database for tests

---

## Test Examples

### Complete Unit Test Example

```python
# tests/unit/herald/test_words.py
"""Unit tests for Herald word generation and exchange ID creation"""

import pytest
from herald.words import generate_exchange_id, ADJECTIVES, NOUNS, VERBS


def test_generate_exchange_id__format():
    """Test exchange ID follows format: adjective-noun-verb-XXXX"""
    exchange_id = generate_exchange_id(check_exists_callback=lambda x: False)
    
    parts = exchange_id.split('-')
    assert len(parts) == 4
    assert len(parts[3]) == 4
    assert all(c in '0123456789abcdef' for c in parts[3])


def test_generate_exchange_id__uses_word_lists():
    """Test exchange ID uses words from defined lists"""
    exchange_id = generate_exchange_id(check_exists_callback=lambda x: False)
    
    adjective, noun, verb, hash_part = exchange_id.split('-')
    assert adjective in ADJECTIVES
    assert noun in NOUNS
    assert verb in VERBS


def test_generate_exchange_id__retries_on_collision():
    """Test exchange ID generation retries when ID already exists"""
    call_count = 0
    
    def check_exists(exchange_id):
        nonlocal call_count
        call_count += 1
        return call_count <= 2  # First 2 attempts "exist"
    
    exchange_id = generate_exchange_id(check_exists_callback=check_exists)
    
    assert call_count == 3  # Tried 3 times
    assert exchange_id is not None
```

### Complete Integration Test Example

```python
# tests/integration/herald/test_exchange_flow.py
"""Integration tests for Herald exchange workflows"""

import pytest
from fastapi.testclient import TestClient


def test_full_exchange_workflow(test_client, test_db):
    """Test complete exchange creation and response flow
    
    Workflow:
    1. Player A creates exchange with list
    2. Player B responds with their list
    3. Both lists are revealed
    4. Both players can view exchange
    """
    # Step 1: Player A creates exchange
    response = test_client.post("/api/herald/exchange/create", json={
        "list_content": "Player A Army List\n1000 points\n..."
    })
    assert response.status_code == 200
    
    data = response.json()
    exchange_id = data["exchange_id"]
    hash_a = data["hash_a"]
    
    # Verify exchange in database
    result = test_db.execute(
        text("SELECT id, list_a FROM herald_exchanges WHERE id = :id"),
        {"id": exchange_id}
    ).fetchone()
    assert result is not None
    assert result.list_a is not None
    
    # Step 2: Player B responds
    response = test_client.post(f"/api/herald/exchange/{exchange_id}/respond", json={
        "list_content": "Player B Army List\n1000 points\n..."
    })
    assert response.status_code == 200
    
    # Step 3: Verify both lists revealed
    response = test_client.get(f"/api/herald/exchange/{exchange_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["exchange_id"] == exchange_id
    assert data["list_a"] is not None
    assert data["list_b"] is not None
    assert data["hash_a"] == hash_a
    assert data["hash_b"] is not None
    assert data["timestamp_a"] is not None
    assert data["timestamp_b"] is not None
```

---

## Troubleshooting

### Tests Fail in CI but Pass Locally

**Possible causes:**
- Different Python version
- Missing environment variables
- Different timezone (use UTC in tests)
- Different database state

**Solution:**
- Check CI logs for specific errors
- Match Python version locally to CI
- Set TZ=UTC in both environments
- Ensure database migrations run in CI

### Coverage Stuck Below 100%

**Solution:**
1. Generate HTML coverage report: `pytest --cov --cov-report=html`
2. Open `htmlcov/index.html` in browser
3. Click on files with <100% coverage
4. Red lines = not covered - write tests for these lines
5. Yellow lines = partial coverage - add branch tests

---

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [FastAPI testing guide](https://fastapi.tiangolo.com/tutorial/testing/)
- [Factory Boy documentation](https://factoryboy.readthedocs.io/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)

---

**Questions?**
- See [TESTING_POLICY.md](TESTING_POLICY.md) for detailed policy
- Ask in #testing Slack channel
- Email qa-team@squigleague.com
