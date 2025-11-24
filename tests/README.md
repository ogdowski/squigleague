# Tests - Squig League

This directory contains the complete test suite for the Squig League platform.

---

## Quick Start

```bash
# Install dependencies
pip install -r requirements-dev.txt

# Start test database
docker-compose -f docker-compose.test.yml up -d

# Run all tests
pytest

# Run with coverage
pytest --cov=herald --cov=squire --cov-report=html

# Open coverage report
start htmlcov/index.html  # Windows
open htmlcov/index.html   # macOS
```

---

## Directory Structure

```
tests/
├── conftest.py                     # Shared fixtures and configuration
├── fixtures/
│   ├── factories.py                # Factory Boy test data generators
│   └── herald_data.py              # Sample test data for Herald
├── unit/                           # Unit tests (fast, isolated)
│   └── herald/
│       ├── test_words.py           # Exchange ID generation (29 tests) ✅
│       ├── test_models.py          # Pydantic models (28 tests) ✅
│       ├── test_database.py        # Database operations (TODO)
│       └── test_main.py            # API routes and middleware (TODO)
└── integration/                    # Integration tests (real systems)
    └── herald/
        ├── test_exchange_flow.py   # Full workflows (TODO)
        ├── test_api_endpoints.py   # API endpoints (TODO)
        ├── test_rate_limiting.py   # Rate limiting (TODO)
        └── test_admin_endpoints.py # Admin endpoints (TODO)
```

---

## Test Categories

### Unit Tests (`tests/unit/`)

**Fast, isolated tests** for individual functions and classes.

- **Speed**: < 100ms per test
- **Scope**: Single function or method
- **Dependencies**: Minimal (fixtures only)
- **Location**: `tests/unit/{module}/test_{file}.py`

**Run unit tests only:**
```bash
pytest -m unit
```

### Integration Tests (`tests/integration/`)

**Real system tests** with database and API.

- **Speed**: < 1s per test
- **Scope**: Full workflows (database + API + logic)
- **Dependencies**: Real PostgreSQL, FastAPI TestClient
- **Location**: `tests/integration/{module}/test_{feature}.py`

**Run integration tests only:**
```bash
pytest -m integration
```

---

## Current Status

### Test Coverage

| Module | Tests | Coverage | Status |
|--------|-------|----------|--------|
| `herald/words.py` | 29 | 100% | ✅ Complete |
| `herald/models.py` | 28 | 100% | ✅ Complete |
| `herald/database.py` | 0 | 0% | ❌ TODO |
| `herald/main.py` | 0 | 0% | ❌ TODO |
| **Total** | **57** | **~40%** | **In Progress** |

### Completed Tests

- ✅ **test_words.py** (29 tests)
  - Exchange ID generation and validation
  - Word list verification
  - Collision handling

- ✅ **test_models.py** (28 tests)
  - Pydantic model validation
  - Request/response models
  - Edge cases and error handling

### Remaining Tests

- ❌ **test_database.py** (~30 tests needed)
- ❌ **test_main.py** (~25 tests needed)
- ❌ **Integration tests** (~31 tests needed)

**Target**: ~143 total tests for 100% coverage

---

## Writing Tests

### Test File Template

```python
"""
Unit tests for herald/module.py - Description

Brief description of what's being tested.
"""

import pytest
from herald import module


class TestFeatureName:
    """Tests for feature_name() function"""
    
    def test_feature__expected_behavior(self):
        """Test that feature behaves as expected"""
        # Arrange
        input_data = "test input"
        
        # Act
        result = module.feature(input_data)
        
        # Assert
        assert result == "expected output"
    
    def test_feature__edge_case(self):
        """Test that feature handles edge case"""
        # Test implementation
        pass
```

### Using Fixtures

**Available Fixtures** (from `conftest.py`):
- `test_db` - Clean database connection (transaction rollback)
- `test_client` - FastAPI TestClient
- `sample_exchange_data` - Sample exchange data
- `create_test_exchange` - Factory to create exchanges
- `assert_db_has_exchange` - Database assertion helper

**Example:**
```python
def test_create_exchange(test_db):
    """Test exchange creation in database"""
    # Use test_db fixture
    result = test_db.execute(text("SELECT 1"))
    assert result is not None
```

### Test Naming Convention

**Format**: `test_{function}__{scenario}`

**Examples:**
- `test_create_exchange__success`
- `test_create_exchange__duplicate_id_fails`
- `test_validate_exchange_id__invalid_format_returns_false`

---

## Running Tests

### Basic Commands

```bash
# All tests
pytest

# Specific file
pytest tests/unit/herald/test_words.py

# Specific test
pytest tests/unit/herald/test_words.py::test_generate_exchange_id__correct_format

# Verbose output
pytest -v

# Show print statements
pytest -s

# Stop on first failure
pytest -x
```

### Coverage Commands

```bash
# Run with coverage
pytest --cov=herald --cov=squire

# Generate HTML report
pytest --cov --cov-report=html

# Fail if coverage < 100%
pytest --cov --cov-fail-under=100

# Terminal report with missing lines
pytest --cov --cov-report=term-missing
```

### Parallel Execution

```bash
# Run tests in parallel (faster)
pytest -n auto

# Specific number of workers
pytest -n 4
```

---

## Test Fixtures

### Database Fixtures

**test_db** - Clean database for each test
```python
def test_something(test_db):
    """Test with database"""
    # Database state is clean
    # Changes rollback after test
    pass
```

**create_test_exchange** - Factory to create exchanges
```python
def test_something(create_test_exchange):
    """Test with exchange data"""
    exchange_id = create_test_exchange(
        exchange_id="test-id",
        list_a="Test List"
    )
    # Exchange is in database
```

### API Fixtures

**test_client** - FastAPI TestClient
```python
def test_api(test_client):
    """Test API endpoint"""
    response = test_client.get("/api/herald/health")
    assert response.status_code == 200
```

### Data Fixtures

**sample_exchange_data** - Pre-built exchange data
```python
def test_with_data(sample_exchange_data):
    """Test with sample data"""
    assert sample_exchange_data["id"] is not None
```

---

## Test Data

### Sample Data

**Location**: `tests/fixtures/herald_data.py`

**Available Data:**
- `SAMPLE_LIST_SPACE_MARINES` - Example army list
- `SAMPLE_LIST_ORKS` - Example army list
- `VALID_EXCHANGE_IDS` - Valid exchange ID examples
- `INVALID_EXCHANGE_IDS` - Invalid exchange ID examples

**Usage:**
```python
from tests.fixtures.herald_data import SAMPLE_LIST_SPACE_MARINES

def test_with_sample_data():
    list_content = SAMPLE_LIST_SPACE_MARINES
    assert len(list_content) > 0
```

### Factories

**Location**: `tests/fixtures/factories.py`

**Available Factories:**
- `ExchangeFactory` - Generate exchange data
- `CompletedExchangeFactory` - Generate complete exchange
- `RequestLogFactory` - Generate request log data

**Usage:**
```python
from tests.fixtures.factories import generate_exchange

def test_with_factory():
    exchange = generate_exchange(list_a="Custom List")
    assert exchange["list_a"] == "Custom List"
```

---

## CI/CD Integration

Tests run automatically on:
- Every push to `main` or `develop`
- Every pull request

**Pipeline checks:**
- ✅ All tests pass
- ✅ Coverage is 100%
- ✅ Code is formatted (black, isort)
- ✅ No linting errors (flake8)

**Merge is blocked if:**
- ❌ Any test fails
- ❌ Coverage < 100%
- ❌ Linting errors exist

---

## Debugging Tests

### Print Debugging

```python
def test_something():
    result = my_function()
    print(f"Result: {result}")  # Shows with -s flag
    assert result is not None
```

Run with: `pytest -s`

### Using pdb

```python
def test_something():
    result = my_function()
    import pdb; pdb.set_trace()  # Breakpoint
    assert result is not None
```

### Verbose Failures

```bash
# Show full diff
pytest -vv

# Show local variables
pytest --showlocals
```

---

## Common Issues

### Database Not Clean

**Problem**: Tests fail due to data from previous tests

**Solution**: Use `test_db` fixture (auto-rollback)
```python
def test_something(test_db):  # ← Use fixture
    # Test runs in transaction
    # Auto-rollback after test
```

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'herald'`

**Solution**: Ensure `pytest.ini` has:
```ini
[pytest]
pythonpath = .
```

### Fixture Not Found

**Problem**: `fixture 'test_client' not found`

**Solution**: Ensure `conftest.py` exists in `tests/` directory

---

## Resources

**Documentation:**
- [TESTING_POLICY.md](../docs/TESTING_POLICY.md) - Testing requirements
- [TESTING_GUIDE.md](../docs/TESTING_GUIDE.md) - How to write tests
- [TESTING_STATUS.md](../docs/TESTING_STATUS.md) - Current progress

**External:**
- [pytest documentation](https://docs.pytest.org/)
- [FastAPI testing guide](https://fastapi.tiangolo.com/tutorial/testing/)
- [Factory Boy documentation](https://factoryboy.readthedocs.io/)

---

## Getting Help

**Questions?**
- See [TESTING_GUIDE.md](../docs/TESTING_GUIDE.md)
- Check existing tests in `tests/unit/herald/test_words.py`
- Ask in #testing Slack channel

**Found a bug?**
1. Write a test that reproduces it
2. Fix the bug
3. Ensure test passes
4. Submit PR

---

**Remember**: Tests are not a burden - they're your safety net. Write tests, sleep well. 🛡️
