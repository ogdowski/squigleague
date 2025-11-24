# Test Environment Setup Guide

## Prerequisites
✅ Python 3.9+ installed  
❌ **Docker Desktop NOT RUNNING** - YOU NEED TO START THIS

## Quick Start

### Step 1: Start Docker Desktop
**CRITICAL:** Open Docker Desktop application and wait for it to fully start.

Verify Docker is running:
```powershell
docker ps
```
Should show a table of containers (may be empty), not an error.

### Step 2: Run Setup Script
```powershell
cd e:\repos\suigleague
.\setup-test-env.ps1
```

This will:
- Start PostgreSQL test database on port 5433
- Create Herald schema (herald_exchanges, herald_request_log tables)
- Install Python dependencies
- Run smoke test

### Step 3: Run Tests
```powershell
# Set Python path
$env:PYTHONPATH = "e:\repos\suigleague"

# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=herald --cov-report=term --cov-report=html

# Run specific test file
python -m pytest tests/unit/herald/test_words.py -v
```

## Manual Setup (if script fails)

### 1. Start Test Database
```powershell
cd e:\repos\suigleague
docker-compose -f docker-compose.test.yml up -d
```

### 2. Wait for Database
```powershell
# Check if ready (run multiple times until success)
docker exec squigleague_test_db pg_isready -U test_user -d test_squigleague
```

### 3. Verify Schema
```powershell
docker exec squigleague_test_db psql -U test_user -d test_squigleague -c "\dt"
```

Should show:
- `herald_exchanges` table
- `herald_request_log` table

### 4. Install Dependencies
```powershell
# Herald dependencies
python -m pip install -r herald/requirements.txt

# Test dependencies
python -m pip install pytest pytest-asyncio pytest-cov httpx factory-boy faker
```

### 5. Run Tests
```powershell
$env:PYTHONPATH = "e:\repos\suigleague"
python -m pytest tests/unit/herald/test_words.py -v
```

## Database Connection Details

**Test Database:**
- Host: localhost
- Port: 5433 (different from production 5432)
- Database: test_squigleague
- User: test_user
- Password: test_password

**Connection String:**
```
postgresql://test_user:test_password@localhost:5433/test_squigleague
```

## Troubleshooting

### Problem: "Docker is not running"
**Solution:** Start Docker Desktop and wait 1-2 minutes for it to fully initialize.

### Problem: Port 5433 already in use
**Solution:** 
```powershell
# Stop existing container
docker-compose -f docker-compose.test.yml down

# Or use different port in docker-compose.test.yml
```

### Problem: "connection refused" errors in tests
**Solution:**
```powershell
# Check database is running
docker ps | Select-String "squigleague_test_db"

# Check database logs
docker-compose -f docker-compose.test.yml logs

# Restart database
docker-compose -f docker-compose.test.yml restart
```

### Problem: Schema not created
**Solution:**
```powershell
# Remove container and volumes
docker-compose -f docker-compose.test.yml down -v

# Recreate (will run init-test-db.sql again)
docker-compose -f docker-compose.test.yml up -d
```

### Problem: Tests fail with import errors
**Solution:**
```powershell
# Ensure PYTHONPATH is set
$env:PYTHONPATH = "e:\repos\suigleague"

# Reinstall dependencies
python -m pip install -r herald/requirements.txt
```

## Cleanup

### Stop Test Database
```powershell
docker-compose -f docker-compose.test.yml down
```

### Remove Database and Volumes
```powershell
docker-compose -f docker-compose.test.yml down -v
```

## Current Status

✅ Test infrastructure complete (119 tests written)  
✅ Docker Compose configuration ready  
✅ Database schema script ready  
❌ **Docker Desktop not running (USER ACTION REQUIRED)**  
⏳ Waiting for environment setup to run tests

## Next Steps After Setup

1. Run full test suite: `pytest tests/ -v`
2. Check coverage: `pytest tests/ --cov=herald --cov-report=html`
3. Fix 2 validation issues in `herald/models.py` (see TEST_EXECUTION_REPORT.md)
4. Re-run tests to verify 100% pass rate
5. Open `htmlcov/index.html` to view coverage report
