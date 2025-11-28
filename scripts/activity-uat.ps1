# Activity Script - UAT Deployment for Battle Plan Randomizer
# This script automates the complete UAT deployment and testing cycle

param(
    [switch]$SkipBuild,
    [switch]$SkipTests,
    [switch]$Verbose
)

$ErrorActionPreference = "Continue"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$rootDir = Split-Path -Parent $scriptDir

Write-Host "`n" -NoNewline
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "  SQUIG LEAGUE - UAT ACTIVITY SCRIPT" -ForegroundColor Cyan
Write-Host "  Battle Plan Randomizer Deployment & Validation" -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ""

$startTime = Get-Date

# ============================================================================
# STEP 1: Pre-flight Checks
# ============================================================================
Write-Host "[1/6] Pre-flight Checks" -ForegroundColor Yellow
Write-Host "------------------------------------------------------------------------" -ForegroundColor DarkGray

# Check Docker is running
Write-Host "  Checking Docker..." -NoNewline
try {
    $null = docker info 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host " OK" -ForegroundColor Green
    } else {
        Write-Host " FAILED" -ForegroundColor Red
        Write-Host "`nERROR: Docker is not running. Please start Docker Desktop." -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host " FAILED" -ForegroundColor Red
    Write-Host "`nERROR: Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

# Check environment file
Write-Host "  Checking environment file..." -NoNewline
if (Test-Path "$rootDir\.env.local") {
    Write-Host " OK" -ForegroundColor Green
} else {
    Write-Host " MISSING" -ForegroundColor Yellow
    Write-Host "  Creating .env.local from template..." -NoNewline
    Copy-Item "$rootDir\.env.local.example" "$rootDir\.env.local"
    Write-Host " CREATED" -ForegroundColor Green
}

# Check required files
$requiredFiles = @(
    "$rootDir\docker-compose.yml",
    "$rootDir\docker-compose.dev.yml",
    "$rootDir\frontend\public\modules\squire\battleplan.js",
    "$rootDir\run-uat-tests.ps1"
)

foreach ($file in $requiredFiles) {
    $fileName = Split-Path -Leaf $file
    Write-Host "  Checking $fileName..." -NoNewline
    if (Test-Path $file) {
        Write-Host " OK" -ForegroundColor Green
    } else {
        Write-Host " MISSING" -ForegroundColor Red
        Write-Host "`nERROR: Required file not found: $file" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""

# ============================================================================
# STEP 2: Build & Deploy
# ============================================================================
if (-not $SkipBuild) {
    Write-Host "[2/6] Building and Deploying Services" -ForegroundColor Yellow
    Write-Host "------------------------------------------------------------------------" -ForegroundColor DarkGray
    
    Set-Location $rootDir
    
    Write-Host "  Setting environment variables..." -ForegroundColor Gray
    $env:DB_PASSWORD = 'dev_password_123'
    $env:HERALD_ADMIN_KEY = 'dev_admin_key_123'
    $env:SQUIG_VERSION = '0.2.1'
    
    Write-Host "  Building images and starting containers..." -ForegroundColor Gray
    Write-Host "  (This may take a few minutes on first run)" -ForegroundColor DarkGray
    
    $buildOutput = docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build -d 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  Build and deployment: " -NoNewline
        Write-Host "SUCCESS" -ForegroundColor Green
    } else {
        Write-Host "  Build and deployment: " -NoNewline
        Write-Host "FAILED" -ForegroundColor Red
        if ($Verbose) {
            Write-Host "`n$buildOutput" -ForegroundColor DarkGray
        }
        Write-Host "`nERROR: Docker build/deployment failed. Run with -Verbose for details." -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "[2/6] Building and Deploying Services - SKIPPED" -ForegroundColor Yellow
    Write-Host "------------------------------------------------------------------------" -ForegroundColor DarkGray
}

Write-Host ""

# ============================================================================
# STEP 3: Wait for Services to be Healthy
# ============================================================================
Write-Host "[3/6] Waiting for Services to Start" -ForegroundColor Yellow
Write-Host "------------------------------------------------------------------------" -ForegroundColor DarkGray

$maxAttempts = 30
$attempt = 0
$allHealthy = $false

while (-not $allHealthy -and $attempt -lt $maxAttempts) {
    $attempt++
    Start-Sleep -Seconds 2
    
    # Check if squig container is healthy
    $squigHealth = docker inspect --format='{{.State.Health.Status}}' squig 2>$null
    $postgresHealth = docker inspect --format='{{.State.Health.Status}}' squig-postgres 2>$null
    
    if ($squigHealth -eq "healthy" -and $postgresHealth -eq "healthy") {
        $allHealthy = $true
        Write-Host "  All services are healthy!" -ForegroundColor Green
    } else {
        Write-Host "  Attempt $attempt/$maxAttempts - Squig: $squigHealth, Postgres: $postgresHealth" -ForegroundColor Gray
    }
}

if (-not $allHealthy) {
    Write-Host "`n  WARNING: Services did not become healthy within 60 seconds." -ForegroundColor Yellow
    Write-Host "  Continuing anyway - tests may fail if services aren't ready." -ForegroundColor Yellow
} else {
    Write-Host "  Services ready in $($attempt * 2) seconds" -ForegroundColor Green
}

Write-Host ""

# ============================================================================
# STEP 4: Quick Smoke Tests
# ============================================================================
Write-Host "[4/6] Running Quick Smoke Tests" -ForegroundColor Yellow
Write-Host "------------------------------------------------------------------------" -ForegroundColor DarkGray

$smokeTestsPassed = $true

# Test 1: API Health
Write-Host "  [Test 1] API Health Check..." -NoNewline
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/api/squire/health" -TimeoutSec 5 -ErrorAction Stop
    if ($health.status -eq "operational") {
        Write-Host " PASS" -ForegroundColor Green
    } else {
        Write-Host " FAIL" -ForegroundColor Red
        $smokeTestsPassed = $false
    }
} catch {
    Write-Host " FAIL" -ForegroundColor Red
    Write-Host "    Error: $_" -ForegroundColor DarkGray
    $smokeTestsPassed = $false
}

# Test 2: Battle Plan Generation
Write-Host "  [Test 2] Battle Plan Generation..." -NoNewline
try {
    $plan = Invoke-RestMethod -Uri "http://localhost:8000/api/squire/battle-plan/random?system=age_of_sigmar" -TimeoutSec 5 -ErrorAction Stop
    if ($plan.name -and $plan.deployment -and $plan.primary_objective) {
        Write-Host " PASS" -ForegroundColor Green
        Write-Host "    Generated: $($plan.name)" -ForegroundColor DarkGray
    } else {
        Write-Host " FAIL" -ForegroundColor Red
        $smokeTestsPassed = $false
    }
} catch {
    Write-Host " FAIL" -ForegroundColor Red
    Write-Host "    Error: $_" -ForegroundColor DarkGray
    $smokeTestsPassed = $false
}

# Test 3: Frontend Accessibility
Write-Host "  [Test 3] Frontend Accessibility..." -NoNewline
try {
    $response = Invoke-WebRequest -Uri "http://localhost/" -TimeoutSec 5 -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-Host " PASS" -ForegroundColor Green
    } else {
        Write-Host " FAIL (Status: $($response.StatusCode))" -ForegroundColor Red
        $smokeTestsPassed = $false
    }
} catch {
    Write-Host " FAIL" -ForegroundColor Red
    Write-Host "    Error: $_" -ForegroundColor DarkGray
    $smokeTestsPassed = $false
}

# Test 4: Squire UI Route
Write-Host "  [Test 4] Squire UI Route..." -NoNewline
try {
    $response = Invoke-WebRequest -Uri "http://localhost/squire/battle-plan" -TimeoutSec 5 -ErrorAction Stop
    if ($response.StatusCode -eq 200 -and $response.Content -match "Battle Plan Randomizer") {
        Write-Host " PASS" -ForegroundColor Green
    } else {
        Write-Host " FAIL" -ForegroundColor Red
        $smokeTestsPassed = $false
    }
} catch {
    Write-Host " FAIL" -ForegroundColor Red
    Write-Host "    Error: $_" -ForegroundColor DarkGray
    $smokeTestsPassed = $false
}

if ($smokeTestsPassed) {
    Write-Host "`n  Smoke tests: " -NoNewline
    Write-Host "ALL PASSED" -ForegroundColor Green
} else {
    Write-Host "`n  Smoke tests: " -NoNewline
    Write-Host "SOME FAILED" -ForegroundColor Yellow
}

Write-Host ""

# ============================================================================
# STEP 5: Full UAT Test Suite
# ============================================================================
if (-not $SkipTests) {
    Write-Host "[5/6] Running Full UAT Test Suite" -ForegroundColor Yellow
    Write-Host "------------------------------------------------------------------------" -ForegroundColor DarkGray
    Write-Host ""
    
    if (Test-Path "$rootDir\run-uat-tests.ps1") {
        & "$rootDir\run-uat-tests.ps1"
        $uatResult = $LASTEXITCODE
    } else {
        Write-Host "  WARNING: UAT test script not found at: $rootDir\run-uat-tests.ps1" -ForegroundColor Yellow
        $uatResult = 1
    }
} else {
    Write-Host "[5/6] Running Full UAT Test Suite - SKIPPED" -ForegroundColor Yellow
    Write-Host "------------------------------------------------------------------------" -ForegroundColor DarkGray
    $uatResult = 0
}

Write-Host ""

# ============================================================================
# STEP 6: Summary & Next Steps
# ============================================================================
Write-Host "[6/6] Summary & Next Steps" -ForegroundColor Yellow
Write-Host "========================================================================" -ForegroundColor DarkGray

$elapsed = (Get-Date) - $startTime
Write-Host ""
Write-Host "  Deployment completed in $([math]::Round($elapsed.TotalSeconds, 1)) seconds" -ForegroundColor Cyan
Write-Host ""

# Show running containers
Write-Host "  Running Containers:" -ForegroundColor White
$containers = docker ps --format "table {{.Names}}\t{{.Status}}" | Select-Object -Skip 1
$containers | ForEach-Object {
    Write-Host "    $_" -ForegroundColor Gray
}

Write-Host ""
Write-Host "  Access Points:" -ForegroundColor White
Write-Host "    Frontend (Herald):         http://localhost" -ForegroundColor Cyan
Write-Host "    Squire UI:                 http://localhost/squire/battle-plan" -ForegroundColor Cyan
Write-Host "    API Documentation:         http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "    Battle Plan API (direct):  http://localhost:8000/api/squire/battle-plan/random?system=age_of_sigmar" -ForegroundColor Cyan

Write-Host ""
Write-Host "  Quick Commands:" -ForegroundColor White
Write-Host "    View logs:        docker-compose logs -f" -ForegroundColor Gray
Write-Host "    Restart:          docker-compose restart" -ForegroundColor Gray
Write-Host "    Stop:             docker-compose down" -ForegroundColor Gray
Write-Host "    Rebuild frontend: docker-compose up --build -d frontend nginx" -ForegroundColor Gray

Write-Host ""

if ($smokeTestsPassed -and $uatResult -eq 0) {
    Write-Host "  Status: " -NoNewline
    Write-Host "ALL TESTS PASSED - Ready for UAT" -ForegroundColor Green
    Write-Host ""
    Write-Host "  Next Steps:" -ForegroundColor White
    Write-Host "    1. Open browser to http://localhost/squire/battle-plan" -ForegroundColor Gray
    Write-Host "    2. Test battle plan generation for all 3 game systems" -ForegroundColor Gray
    Write-Host "    3. Verify UI responsiveness and error handling" -ForegroundColor Gray
    Write-Host "    4. Share with stakeholders for acceptance testing" -ForegroundColor Gray
} elseif ($smokeTestsPassed) {
    Write-Host "  Status: " -NoNewline
    Write-Host "SMOKE TESTS PASSED - UAT tests had issues" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  Next Steps:" -ForegroundColor White
    Write-Host "    1. Review UAT test output above" -ForegroundColor Gray
    Write-Host "    2. Address any failing tests" -ForegroundColor Gray
    Write-Host "    3. Re-run: .\scripts\activity-uat.ps1 -SkipBuild" -ForegroundColor Gray
} else {
    Write-Host "  Status: " -NoNewline
    Write-Host "SMOKE TESTS FAILED - Review output above" -ForegroundColor Red
    Write-Host ""
    Write-Host "  Next Steps:" -ForegroundColor White
    Write-Host "    1. Check Docker logs: docker-compose logs" -ForegroundColor Gray
    Write-Host "    2. Verify services are running: docker ps" -ForegroundColor Gray
    Write-Host "    3. Re-run with verbose: .\scripts\activity-uat.ps1 -Verbose" -ForegroundColor Gray
}

Write-Host ""
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ""

# Set exit code based on overall success
if ($smokeTestsPassed -and $uatResult -eq 0) {
    exit 0
} else {
    exit 1
}
