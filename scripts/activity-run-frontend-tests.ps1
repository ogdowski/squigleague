#!/usr/bin/env pwsh
# Activity Script: Run Frontend Tests with Selenium
# Purpose: Execute browser-based tests for registration, login, and matchup flows
# Usage: .\scripts\activity-run-frontend-tests.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Activity: Run Frontend Tests (Selenium)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check if environment is running
Write-Host "[1/4] Checking if development environment is running..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri 'http://localhost/api/health' -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
    Write-Host "Environment is running" -ForegroundColor Green
} catch {
    Write-Host "Environment is NOT running. Start it first with:" -ForegroundColor Red
    Write-Host "  .\scripts\activity-start-dev-environment.ps1" -ForegroundColor Yellow
    exit 1
}
Write-Host ""

# Step 2: Install Selenium if needed
Write-Host "[2/4] Checking Selenium installation..." -ForegroundColor Yellow
$seleniumInstalled = .\.venv\Scripts\python.exe -c "import selenium; print('OK')" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installing Selenium..." -ForegroundColor Yellow
    .\.venv\Scripts\python.exe -m pip install selenium
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to install Selenium" -ForegroundColor Red
        exit 1
    }
}
Write-Host "Selenium is installed" -ForegroundColor Green
Write-Host ""

# Step 3: Check ChromeDriver
Write-Host "[3/4] Checking ChromeDriver..." -ForegroundColor Yellow
$chromeDriverCheck = .\.venv\Scripts\python.exe -c "from selenium import webdriver; from selenium.webdriver.chrome.options import Options; opts = Options(); opts.add_argument('--headless'); driver = webdriver.Chrome(options=opts); driver.quit(); print('OK')" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "ChromeDriver not found or not working" -ForegroundColor Red
    Write-Host "Install ChromeDriver: pip install webdriver-manager" -ForegroundColor Yellow
    Write-Host "Or download from: https://chromedriver.chromium.org/" -ForegroundColor Yellow
    exit 1
}
Write-Host "ChromeDriver is working" -ForegroundColor Green
Write-Host ""

# Step 4: Run frontend tests
Write-Host "[4/4] Running frontend tests..." -ForegroundColor Yellow
.\.venv\Scripts\python.exe -m pytest tests/frontend/ -v --tb=short
$testResult = $LASTEXITCODE

Write-Host ""
if ($testResult -eq 0) {
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "Frontend tests PASSED" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    exit 0
} else {
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "Frontend tests FAILED" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    exit 1
}
