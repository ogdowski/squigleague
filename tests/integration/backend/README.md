# Integration Tests for Backend

This directory contains integration tests that verify the interaction between:
- API endpoints
- Database layer
- Business logic
- Authentication/authorization
- External services (when applicable)

## Structure

```
integration/
├── backend/
│   ├── leagues/           # Leagues module integration tests
│   │   ├── __init__.py
│   │   └── test_leagues_integration.py
│   ├── auth/              # Auth integration tests
│   └── __init__.py
├── herald/                # Herald service integration tests
├── squire/                # Squire service integration tests
└── README.md             # This file
```

## Current Status

**Unit Test Coverage: ✅ 100%**
- Leagues module: 89 tests, 100% coverage
- All branches covered
- All error paths tested

**Integration Tests: 🚧 Planned**
- Template created in `backend/leagues/test_leagues_integration.py`
- Requires service orchestration setup
- Run with: `pwsh scripts/integration-test-runner.ps1`
**E2E Tests: ✅ COMPLIANT (Selenium)**
- Selenium pytest suite lives in `tests/e2e/selenium`
- Requires frontend + backend running and Chrome available
## Running Integration Tests

### Prerequisites

1. **Start test environment:**
   ```bash
   just test-db-up
   # OR for full stack:
   just dev
   ```

2. **Verify services are healthy:**
   ```bash
   docker-compose ps
   ```

### Run Tests

```bash
# All integration tests
pytest tests/integration -v

# Specific module
pytest tests/integration/backend/leagues -v

# With test database
pytest tests/integration/backend --db=postgresql://test_user:test_password@localhost:5433/test_squigleague

# Using helper script
pwsh scripts/integration-test-runner.ps1
```

### Using the Integration Test Runner

```powershell
# Run all integration tests with auto-setup
.\scripts\integration-test-runner.ps1

# Run only backend tests
.\scripts\integration-test-runner.ps1 -Service backend

# Keep services running for debugging
.\scripts\integration-test-runner.ps1 -KeepRunning

# Clean start (removes volumes)
.\scripts\integration-test-runner.ps1 -CleanStart
```

## Test Categories

### 1. API Integration Tests
- Full HTTP request/response cycle
- Real database connections
- Actual auth token validation
- Error response codes and messages

### 2. Database Integration Tests
- Transaction handling
- Concurrent access patterns
- Migration compatibility
- Data integrity constraints

### 3. Performance Tests
- Response time under load
- Query optimization verification
- Pagination performance
- Concurrent user simulation

### 4. End-to-End Flows
- Complete user workflows
- Multi-step operations
- State transitions
- Cross-module interactions

## Writing Integration Tests

### Example Structure

```python
import pytest
import requests

@pytest.fixture
def api_url():
    return "http://localhost:8000"

def test_create_league_integration(api_url, auth_token):
    """Test league creation with real HTTP request."""
    response = requests.post(
        f"{api_url}/api/leagues",
        json={"name": "Test League", "season": "2025"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 201
    league = response.json()
    assert league["name"] == "Test League"
    
    # Verify in database
    get_response = requests.get(
        f"{api_url}/api/leagues/{league['id']}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert get_response.status_code == 200
```

### Best Practices

1. **Isolation**: Each test should clean up its data
2. **Independence**: Tests should not depend on execution order
3. **Realistic Data**: Use production-like test data
4. **Clear Assertions**: Test one thing per test
5. **Proper Cleanup**: Use fixtures for setup/teardown

## Test Data Management

### Using Fixtures

```python
@pytest.fixture
def test_league(api_url, auth_token):
    """Create a test league and clean it up after."""
    response = requests.post(
        f"{api_url}/api/leagues",
        json={"name": "Test", "season": "2025"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    league = response.json()
    
    yield league
    
    # Cleanup
    requests.delete(
        f"{api_url}/api/leagues/{league['id']}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
```

### Test Database Reset

For integration tests, use a dedicated test database:

```python
@pytest.fixture(scope="session")
def test_db():
    """Set up test database."""
    # Run migrations
    # Seed test data
    yield
    # Cleanup
```

## CI/CD Integration

Integration tests run in GitHub Actions after unit tests pass:

```yaml
# .github/workflows/test.yml
- name: Run integration tests
  run: |
    docker-compose -f docker-compose.test.yml up -d
    pytest tests/integration -v --tb=short
    docker-compose -f docker-compose.test.yml down
```

## Troubleshooting

### Services Not Starting

```bash
# Check logs
docker-compose -f docker-compose.test.yml logs

# Restart services
docker-compose -f docker-compose.test.yml down
docker-compose -f docker-compose.test.yml up -d
```

### Connection Refused

- Verify services are running: `docker-compose ps`
- Check port mappings in `docker-compose.test.yml`
- Wait longer for services to initialize

### Database State Issues

```bash
# Reset database
docker-compose -f docker-compose.test.yml down -v
docker-compose -f docker-compose.test.yml up -d
```

## Migration to Integration Tests

While unit tests provide 100% coverage, integration tests verify:
- **Actual deployment behavior**
- **Service interactions**
- **Network/latency issues**
- **Configuration problems**
- **Performance under load**

The current 100% unit test coverage ensures code correctness. Integration tests will verify deployment correctness when services are orchestrated.

## Related Documentation

- [Testing Guide](../../../docs/TESTING_GUIDE.md)
- [Testing Policy](../../../docs/TESTING_POLICY.md)
- [UAT Test Plan](../../../docs/MATCHUP_TEST_PLAN.md)
- [Pre-Deployment Checklist](../../../scripts/pre-deployment-check.ps1)
