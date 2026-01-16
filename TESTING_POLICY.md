# Testing Policy

## Mandatory Testing Requirements

### 1. All Code Changes Require Tests
- **Zero tolerance**: No code changes without corresponding tests
- **Pre-commit validation**: All tests must pass before commit
- **Coverage requirement**: Minimum 80% code coverage for new code

### 2. Testing Levels

#### Unit Tests
- Test individual functions/methods in isolation
- Mock external dependencies
- Fast execution (< 1 second per test)
- Location: `tests/unit/`

#### Integration Tests
- Test API endpoints end-to-end
- Use real database (test database)
- Test authentication flow
- Location: `tests/integration/`

#### End-to-End Tests
- Test complete user workflows
- Simulate real user interactions
- Test through Docker environment
- Location: `tests/e2e/`

### 3. Test Execution

#### Before Every Commit
```bash
python -m pytest tests/ -v
```

#### Before Every Push
```bash
python -m pytest tests/ -v --cov=backend/app --cov=squire
```

#### Before Deployment
```bash
./scripts/run_all_tests.sh
```

### 4. Continuous Integration
- All tests run automatically on PR creation
- Tests must pass before merge approval
- Failed tests block deployment

### 5. Test Documentation
- Every test must have a docstring explaining what it tests
- Complex tests must include inline comments
- Test data must be documented

## Test Categories

### Authentication Tests
- User registration
- User login
- Token validation
- Session persistence
- Logout

### Matchup Tests
- Matchup creation
- List submission (player 1 & 2)
- Matchup retrieval
- Reveal functionality
- Player names display
- Expiration handling

### API Tests
- All endpoints tested
- Success cases (200, 201)
- Error cases (400, 401, 404, 410)
- Authorization header passing

### Docker Environment Tests
- Container health checks
- Service connectivity
- Nginx proxy configuration
- Database persistence
- Volume management

## Failure Protocol

### When Tests Fail
1. **DO NOT** bypass failing tests
2. **DO NOT** disable tests
3. **FIX** the underlying issue
4. **UPDATE** tests if requirements changed
5. **DOCUMENT** why the failure occurred

### Process-First Approach
When discovering a bug:
1. Write a test that reproduces the bug
2. Confirm the test fails
3. Fix the bug
4. Confirm the test passes
5. Add test to CI pipeline

## Testing Tools

### Required
- `pytest` - Python testing framework
- `requests` - HTTP testing
- `coverage` - Code coverage measurement

### Recommended
- `pytest-cov` - Coverage plugin for pytest
- `pytest-xdist` - Parallel test execution
- `faker` - Generate test data

## Automated Testing Schedule

### On Every File Save (Dev Environment)
- Syntax validation
- Type checking (if applicable)

### On Every Commit
- All unit tests
- Critical integration tests

### On Every Push
- All tests
- Coverage report

### Nightly
- Full end-to-end test suite
- Performance tests
- Load tests

## Test Data Management

### Principles
- Use unique identifiers (timestamps) to avoid collisions
- Clean up test data after tests complete
- Never use production data in tests
- Use realistic but anonymized data

### Test Database
- Separate database for tests
- Reset before test runs
- Isolated from production and development databases

## Responsibilities

### Developer
- Write tests for all new code
- Run tests before committing
- Fix failing tests immediately
- Maintain test quality

### Reviewer
- Verify tests exist for all changes
- Check test quality and coverage
- Run tests locally before approval
- Reject PRs with insufficient testing

### CI/CD
- Run all tests automatically
- Report coverage metrics
- Block deployment on failures
- Archive test results

## Exceptions

### When Tests Can Be Skipped
- **NEVER** - No exceptions

### Emergency Hotfix Process
1. Fix the critical issue
2. Deploy with approval
3. **IMMEDIATELY** write tests for the fix
4. Commit tests within 24 hours
