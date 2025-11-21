# Activity Script: Fix Herald Test Schema and Verify Locally
# Purpose: Fix INET type mismatch and run tests locally before pushing

Write-Host "=== FIX HERALD TEST SCHEMA ===" -ForegroundColor Cyan
Write-Host ""

# Step 1: Verify changes to init-test-db.sql
Write-Host "[1/5] Verifying test schema changes..." -ForegroundColor Yellow
$testSchema = Get-Content "e:\repos\suigleague\init-test-db.sql" -Raw
if ($testSchema -match "ip TEXT") {
    Write-Host "    Test schema fixed: ip column is TEXT" -ForegroundColor Green
} else {
    Write-Host "    ERROR: Test schema still has INET type" -ForegroundColor Red
    exit 1
}

# Step 2: Set up test database locally
Write-Host ""
Write-Host "[2/5] Setting up local test database..." -ForegroundColor Yellow
Write-Host "    Checking if postgres container is running..."

$container = docker ps --filter "name=postgres" --format "{{.Names}}"
if (-not $container) {
    Write-Host "    Starting docker-compose services..." -ForegroundColor Yellow
    docker-compose up -d postgres
    Start-Sleep -Seconds 10
}

# Step 3: Initialize test database schema
Write-Host ""
Write-Host "[3/5] Initializing test database schema..." -ForegroundColor Yellow
$env:PGPASSWORD = "password"
docker exec -i squigleague-postgres-1 psql -U squig -d squigleague -c "\dt herald_*" 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "    Creating tables from init-test-db.sql..."
    Get-Content "e:\repos\suigleague\init-test-db.sql" | docker exec -i squigleague-postgres-1 psql -U squig -d squigleague
    if ($LASTEXITCODE -ne 0) {
        Write-Host "    ERROR: Failed to create tables" -ForegroundColor Red
        exit 1
    }
    Write-Host "    Tables created successfully" -ForegroundColor Green
} else {
    Write-Host "    Tables already exist" -ForegroundColor Green
}

# Step 4: Run tests locally
Write-Host ""
Write-Host "[4/5] Running pytest locally..." -ForegroundColor Yellow
$env:TEST_DATABASE_URL = "postgresql://squig:password@localhost:5432/squigleague"

.\.venv\Scripts\python.exe -m pytest tests/ -v --tb=short

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "    TESTS FAILED - Fix errors before pushing" -ForegroundColor Red
    exit 1
}

Write-Host "    All tests passed" -ForegroundColor Green

# Step 5: Commit and push
Write-Host ""
Write-Host "[5/5] Committing and pushing changes..." -ForegroundColor Yellow
git add init-test-db.sql
git commit -m "Fix test schema: Change ip column from INET to TEXT for test compatibility"

if ($LASTEXITCODE -ne 0) {
    Write-Host "    Nothing to commit or commit failed" -ForegroundColor Yellow
} else {
    git push
    if ($LASTEXITCODE -ne 0) {
        Write-Host "    ERROR: Push failed" -ForegroundColor Red
        exit 1
    }
    Write-Host "    Pushed successfully" -ForegroundColor Green
}

# Done
Write-Host ""
Write-Host "=== COMPLETE ===" -ForegroundColor Green
Write-Host ""
Write-Host "Test schema fixed and verified locally."
Write-Host "Tests are passing. CI should now succeed."
