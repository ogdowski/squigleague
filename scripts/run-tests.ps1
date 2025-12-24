# Run all tests (unit + integration) with coverage
# Usage: .\scripts\run-tests.ps1

$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SQUIGLEAGUE TEST SUITE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if containers are running
Write-Host "Checking services..." -ForegroundColor Yellow
$containers = docker ps --filter "name=squig" --format "{{.Names}}" 2>$null
if ($LASTEXITCODE -ne 0 -or !$containers) {
    Write-Host "X Docker containers not running" -ForegroundColor Red
    Write-Host "Run: docker-compose up -d" -ForegroundColor Yellow
    exit 1
}
Write-Host "OK Containers running" -ForegroundColor Green
Write-Host ""

# Check if pytest is available
Write-Host "Checking test environment..." -ForegroundColor Yellow
$pytestCheck = docker exec squig python -m pytest --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "pytest not found, installing..." -ForegroundColor Yellow
    docker exec squig pip install pytest pytest-cov pytest-asyncio httpx 2>&1 | Out-Null
    Write-Host "OK Test dependencies installed" -ForegroundColor Green
    Write-Host ""
}
else {
    Write-Host "OK pytest available" -ForegroundColor Green
    Write-Host ""
}

# Run Unit Tests
Write-Host "[1] Running Unit Tests..." -ForegroundColor Cyan
Write-Host "========================" -ForegroundColor Cyan
docker exec squig python -m pytest tests/unit/squire/ -v --tb=short --color=yes

$unitResult = $LASTEXITCODE
if ($unitResult -eq 0) {
    Write-Host ""
    Write-Host "OK Unit tests passed!" -ForegroundColor Green
}
else {
    Write-Host ""
    Write-Host "X Unit tests failed" -ForegroundColor Red
}

# Run Integration Tests
Write-Host ""
Write-Host "[2] Running Integration Tests..." -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
docker exec squig python -m pytest tests/integration/squire/ -v --tb=short --color=yes

$integrationResult = $LASTEXITCODE
if ($integrationResult -eq 0) {
    Write-Host ""
    Write-Host "OK Integration tests passed!" -ForegroundColor Green
}
else {
    Write-Host ""
    Write-Host "X Integration tests failed" -ForegroundColor Red
}

# Run All Tests with Coverage
Write-Host ""
Write-Host "[3] Generating Coverage Report..." -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
docker exec squig python -m pytest tests/unit/squire/ tests/integration/squire/ --cov=squire --cov-report=term-missing --cov-report=html --tb=short

$coverageResult = $LASTEXITCODE

# Test Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "TEST SUMMARY" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
if ($unitResult -eq 0) {
    Write-Host "Unit Tests:        OK PASSED" -ForegroundColor Green
}
else {
    Write-Host "Unit Tests:        X FAILED" -ForegroundColor Red
}

if ($integrationResult -eq 0) {
    Write-Host "Integration Tests: OK PASSED" -ForegroundColor Green
}
else {
    Write-Host "Integration Tests: X FAILED" -ForegroundColor Red
}

Write-Host "Coverage Report:   htmlcov/index.html (inside container)" -ForegroundColor White

# Overall result
if ($unitResult -eq 0 -and $integrationResult -eq 0) {
    Write-Host ""
    Write-Host "OK ALL TESTS PASSED!" -ForegroundColor Green
    exit 0
}
else {
    Write-Host ""
    Write-Host "X SOME TESTS FAILED" -ForegroundColor Red
    exit 1
}
