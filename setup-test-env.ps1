# Test Environment Setup Script
# Run this to set up the complete testing environment

Write-Host "=== Squig League Test Environment Setup ===" -ForegroundColor Cyan
Write-Host ""

# Check Docker is running
Write-Host "1. Checking Docker..." -ForegroundColor Yellow
$dockerRunning = docker info 2>$null
if (-not $dockerRunning) {
    Write-Host "ERROR: Docker is not running!" -ForegroundColor Red
    Write-Host "Please start Docker Desktop and try again." -ForegroundColor Red
    exit 1
}
Write-Host "   Docker is running ✓" -ForegroundColor Green

# Stop and remove existing test container if it exists
Write-Host ""
Write-Host "2. Cleaning up old test containers..." -ForegroundColor Yellow
docker-compose -f docker-compose.test.yml down -v 2>$null | Out-Null
Write-Host "   Cleanup complete ✓" -ForegroundColor Green

# Start test database
Write-Host ""
Write-Host "3. Starting test database..." -ForegroundColor Yellow
docker-compose -f docker-compose.test.yml up -d
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to start test database!" -ForegroundColor Red
    exit 1
}

# Wait for database to be ready
Write-Host ""
Write-Host "4. Waiting for database to be ready..." -ForegroundColor Yellow
$maxAttempts = 30
$attempt = 0
$ready = $false

while (-not $ready -and $attempt -lt $maxAttempts) {
    $attempt++
    $healthCheck = docker exec squigleague_test_db pg_isready -U test_user -d test_squigleague 2>$null
    if ($LASTEXITCODE -eq 0) {
        $ready = $true
        Write-Host "   Database is ready ✓" -ForegroundColor Green
    } else {
        Write-Host "   Attempt $attempt/$maxAttempts..." -ForegroundColor Gray
        Start-Sleep -Seconds 1
    }
}

if (-not $ready) {
    Write-Host "ERROR: Database failed to start within 30 seconds!" -ForegroundColor Red
    docker-compose -f docker-compose.test.yml logs
    exit 1
}

# Verify schema was created
Write-Host ""
Write-Host "5. Verifying database schema..." -ForegroundColor Yellow
$tableCheck = docker exec squigleague_test_db psql -U test_user -d test_squigleague -c "\dt" 2>$null
if ($tableCheck -match "herald_exchanges" -and $tableCheck -match "herald_request_log") {
    Write-Host "   Schema verified ✓" -ForegroundColor Green
} else {
    Write-Host "WARNING: Schema may not be complete" -ForegroundColor Yellow
    Write-Host $tableCheck
}

# Install Python dependencies
Write-Host ""
Write-Host "6. Installing Python dependencies..." -ForegroundColor Yellow
$env:PYTHONPATH = "e:\repos\suigleague"
python -m pip install -q -r herald/requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install Herald dependencies!" -ForegroundColor Red
    exit 1
}

python -m pip install -q pytest pytest-asyncio pytest-cov httpx factory-boy faker
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install test dependencies!" -ForegroundColor Red
    exit 1
}
Write-Host "   Dependencies installed ✓" -ForegroundColor Green

# Run a quick test to verify everything works
Write-Host ""
Write-Host "7. Running smoke test..." -ForegroundColor Yellow
$smokeTest = python -m pytest tests/unit/herald/test_words.py -v -x 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "   Smoke test passed ✓" -ForegroundColor Green
} else {
    Write-Host "WARNING: Smoke test had issues" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== Setup Complete ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Test database is running on localhost:5433" -ForegroundColor White
Write-Host "To run tests: pytest tests/ -v" -ForegroundColor White
Write-Host "To stop database: docker-compose -f docker-compose.test.yml down" -ForegroundColor White
Write-Host ""
