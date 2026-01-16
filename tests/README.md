# Comprehensive Test Suite

## Test Coverage

This test suite provides comprehensive coverage of all Squig League functionality.

### Test Structure

```
tests/
├── conftest.py          # Pytest configuration and fixtures
├── integration/         # API integration tests
│   ├── test_auth.py     # Authentication tests
│   └── test_matchup.py  # Matchup functionality tests
└── e2e/                 # End-to-end workflow tests
    └── test_workflows.py # Complete user workflows
```

## Running Tests

### All Tests
```bash
./scripts/run_all_tests.sh
```

### Integration Tests Only
```bash
python -m pytest tests/integration/ -v
```

### End-to-End Tests Only
```bash
python -m pytest tests/e2e/ -v
```

### Specific Test File
```bash
python -m pytest tests/integration/test_auth.py -v
```

### Specific Test Function
```bash
python -m pytest tests/integration/test_auth.py::TestAuthentication::test_user_registration -v
```

## Test Categories

### Authentication Tests (`test_auth.py`)
- ✅ User registration with valid credentials
- ✅ Registration with duplicate email (error handling)
- ✅ Registration with short password (validation)
- ✅ User login with valid credentials
- ✅ Login with wrong password (error handling)
- ✅ Login with non-existent user (error handling)
- ✅ Token authentication for protected endpoints
- ✅ Protected endpoint rejects missing token
- ✅ Protected endpoint rejects invalid token
- ✅ Get current user info (/auth/me)

### Matchup Tests (`test_matchup.py`)

#### Matchup Creation
- ✅ Authenticated user can create matchup
- ✅ Anonymous user can create matchup
- ✅ Creation fails with too short army list

#### Matchup Submission
- ✅ Player 2 can submit list (authenticated)
- ✅ Player 2 can submit list (anonymous)
- ✅ Submission fails for non-existent matchup

#### Matchup Retrieval
- ✅ Get matchup status before reveal
- ✅ Get non-existent matchup returns 404
- ✅ Get authenticated user's matchups
- ✅ /my-matchups requires authentication

#### Matchup Reveal
- ✅ Reveal complete matchup (both lists submitted)
- ✅ Reveal fails for incomplete matchup

#### Player Names Feature
- ✅ Player usernames appear in matchup status
- ✅ Player usernames appear in reveal
- ✅ Anonymous players have null username

### End-to-End Workflow Tests (`test_workflows.py`)

#### Complete Matchup Workflow
- ✅ Two users register, create, submit, and reveal matchup
- ✅ Player names display correctly throughout workflow
- ✅ Both players can access their matchup lists
- ✅ Reveal shows both lists and map assignment

#### Anonymous Workflow
- ✅ Anonymous users complete matchup
- ✅ Null usernames handled correctly

#### Mixed Authentication Workflow
- ✅ Authenticated vs anonymous user matchup
- ✅ Only authenticated player's name displays

#### Error Recovery
- ✅ Duplicate submission handling
- ⏸️ Expired matchup handling (requires time mocking)

## Test Metrics

### Current Coverage
- **Integration Tests**: 30 test cases
- **E2E Tests**: 4 comprehensive workflows
- **Total**: 34+ test cases

### Coverage Goals
- **Code Coverage**: 80% minimum
- **API Endpoints**: 100% coverage
- **User Workflows**: All critical paths tested

## Prerequisites

### Docker Environment Must Be Running
```bash
docker compose -f docker-compose.dev.yml up -d
```

### Required Python Packages
```bash
pip install pytest requests pytest-cov
```

## CI/CD Integration

### GitHub Actions Workflow
```yaml
name: Test Suite
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Start Docker environment
        run: docker compose -f docker-compose.dev.yml up -d
      - name: Run tests
        run: ./scripts/run_all_tests.sh
```

## Test Data Management

### Automatic Cleanup
- Each test uses timestamp-based unique identifiers
- No manual cleanup required
- Tests are isolated and can run in parallel

### Test Database
- Uses fresh Docker database
- No production data risk
- Can be reset with: `docker compose -f docker-compose.dev.yml down -v`

## Debugging Failed Tests

### View Detailed Output
```bash
python -m pytest tests/ -vv --tb=long
```

### Run Single Test in Debug Mode
```bash
python -m pytest tests/integration/test_auth.py::TestAuthentication::test_user_registration -vv -s
```

### Check Docker Logs
```bash
docker compose -f docker-compose.dev.yml logs backend --tail 50
```

## Adding New Tests

### Template for New Test
```python
class TestNewFeature:
    """Test suite for new feature."""

    def test_feature_works(self):
        """Test that new feature works as expected."""
        # Arrange
        timestamp = int(time.time())
        
        # Act
        response = requests.post(...)
        
        # Assert
        assert response.status_code == 200
        assert response.json()["expected_field"] == "expected_value"
```

### Checklist for New Tests
- [ ] Test filename starts with `test_`
- [ ] Test class starts with `Test`
- [ ] Test method starts with `test_`
- [ ] Docstring explains what is being tested
- [ ] Uses unique identifiers (timestamps)
- [ ] Asserts specific expected behaviors
- [ ] Handles both success and error cases

## Known Limitations

### Not Yet Tested
- Matchup expiration (requires time mocking)
- OAuth login flows (requires external service mocks)
- Rate limiting
- Concurrent access scenarios

### Future Enhancements
- Performance tests
- Load tests
- Security tests (SQL injection, XSS, etc.)
- Browser-based UI tests (Selenium/Playwright)
