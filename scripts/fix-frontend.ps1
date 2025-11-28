# Frontend Fix & Validation Script
# Diagnoses and fixes the frontend 502 error, then validates the Battle Plan UI

param(
    [switch]$Verbose
)

$ErrorActionPreference = "Continue"

Write-Host "`n========================================================================" -ForegroundColor Cyan
Write-Host "  FRONTEND FIX & VALIDATION" -ForegroundColor Cyan
Write-Host "  Diagnosing and fixing the Battle Plan Randomizer UI" -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ""

# ============================================================================
# STEP 1: Diagnose Current State
# ============================================================================
Write-Host "[1/5] Diagnosing Current State" -ForegroundColor Yellow
Write-Host "------------------------------------------------------------------------" -ForegroundColor DarkGray

Write-Host "  Checking container status..." -ForegroundColor Gray
$containers = docker ps --filter name=squig --format "{{.Names}}: {{.Status}}"
$containers | ForEach-Object { Write-Host "    $_" -ForegroundColor Gray }

Write-Host "`n  Testing direct API access..." -ForegroundColor Gray
try {
    $apiTest = Invoke-RestMethod -Uri "http://localhost:8000/api/squire/health" -TimeoutSec 3 -ErrorAction Stop
    Write-Host "    API: " -NoNewline
    Write-Host "WORKING" -ForegroundColor Green
} catch {
    Write-Host "    API: " -NoNewline
    Write-Host "FAILED - $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "`nERROR: Backend API not responding. Fix backend first." -ForegroundColor Red
    exit 1
}

Write-Host "`n  Testing frontend through nginx..." -ForegroundColor Gray
try {
    $frontendTest = Invoke-WebRequest -Uri "http://localhost/" -TimeoutSec 3 -ErrorAction Stop
    Write-Host "    Frontend: " -NoNewline
    Write-Host "WORKING (Status: $($frontendTest.StatusCode))" -ForegroundColor Green
    Write-Host "`nFrontend is already working! Opening browser..." -ForegroundColor Green
    Start-Process "http://localhost/squire/battle-plan"
    exit 0
} catch {
    Write-Host "    Frontend: " -NoNewline
    Write-Host "502 ERROR - Needs fixing" -ForegroundColor Red
}

Write-Host ""

# ============================================================================
# STEP 2: Check Network Configuration
# ============================================================================
Write-Host "[2/5] Checking Network Configuration" -ForegroundColor Yellow
Write-Host "------------------------------------------------------------------------" -ForegroundColor DarkGray

$networkInfo = docker network inspect squigleague_squig-network --format='{{range .Containers}}{{.Name}}:{{.IPv4Address}} {{end}}' 2>$null

if ($networkInfo) {
    Write-Host "  Container IPs:" -ForegroundColor Gray
    $networkInfo.Split(' ') | Where-Object { $_ } | ForEach-Object {
        Write-Host "    $_" -ForegroundColor Gray
    }
} else {
    Write-Host "  WARNING: Could not inspect network" -ForegroundColor Yellow
}

Write-Host "`n  Testing nginx -> frontend connectivity..." -ForegroundColor Gray
$ncTest = docker exec squig-nginx nc -zv frontend 80 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "    Connection: " -NoNewline
    Write-Host "OK" -ForegroundColor Green
} else {
    Write-Host "    Connection: " -NoNewline
    Write-Host "FAILED" -ForegroundColor Red
    Write-Host "    $ncTest" -ForegroundColor DarkGray
}

Write-Host ""

# ============================================================================
# STEP 3: Rebuild Frontend Container
# ============================================================================
Write-Host "[3/5] Rebuilding Frontend Container" -ForegroundColor Yellow
Write-Host "------------------------------------------------------------------------" -ForegroundColor DarkGray

Set-Location "C:\repos\SquigLeague\squigleague"

Write-Host "  Setting environment..." -ForegroundColor Gray
$env:DB_PASSWORD = 'dev_password_123'
$env:HERALD_ADMIN_KEY = 'dev_admin_key_123'
$env:SQUIG_VERSION = '0.2.1'

Write-Host "  Rebuilding frontend image..." -ForegroundColor Gray
$buildOutput = docker-compose -f docker-compose.yml -f docker-compose.dev.yml build frontend 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "    Build: " -NoNewline
    Write-Host "SUCCESS" -ForegroundColor Green
} else {
    Write-Host "    Build: " -NoNewline
    Write-Host "FAILED" -ForegroundColor Red
    if ($Verbose) {
        Write-Host "`n$buildOutput" -ForegroundColor DarkGray
    }
    exit 1
}

Write-Host "  Recreating frontend container..." -ForegroundColor Gray
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d --force-recreate frontend 2>&1 | Out-Null

if ($LASTEXITCODE -eq 0) {
    Write-Host "    Recreate: " -NoNewline
    Write-Host "SUCCESS" -ForegroundColor Green
} else {
    Write-Host "    Recreate: " -NoNewline
    Write-Host "FAILED" -ForegroundColor Red
    exit 1
}

Write-Host ""

# ============================================================================
# STEP 4: Restart Nginx
# ============================================================================
Write-Host "[4/5] Restarting Nginx (to refresh DNS)" -ForegroundColor Yellow
Write-Host "------------------------------------------------------------------------" -ForegroundColor DarkGray

Write-Host "  Restarting nginx container..." -ForegroundColor Gray
docker-compose -f docker-compose.yml -f docker-compose.dev.yml restart nginx 2>&1 | Out-Null

if ($LASTEXITCODE -eq 0) {
    Write-Host "    Restart: " -NoNewline
    Write-Host "SUCCESS" -ForegroundColor Green
} else {
    Write-Host "    Restart: " -NoNewline
    Write-Host "FAILED" -ForegroundColor Red
    exit 1
}

Write-Host "  Waiting for nginx to be ready..." -ForegroundColor Gray
Start-Sleep -Seconds 3

Write-Host ""

# ============================================================================
# STEP 5: Validate Frontend is Working
# ============================================================================
Write-Host "[5/5] Validating Frontend" -ForegroundColor Yellow
Write-Host "------------------------------------------------------------------------" -ForegroundColor DarkGray

$validationPassed = $true

# Test 1: Root path
Write-Host "  [Test 1] Root path (/)..." -NoNewline
try {
    $rootTest = Invoke-WebRequest -Uri "http://localhost/" -TimeoutSec 5 -ErrorAction Stop
    if ($rootTest.StatusCode -eq 200 -and $rootTest.Content -match "SQUIG LEAGUE") {
        Write-Host " PASS" -ForegroundColor Green
    } else {
        Write-Host " FAIL (unexpected content)" -ForegroundColor Red
        $validationPassed = $false
    }
} catch {
    Write-Host " FAIL ($($_.Exception.Message))" -ForegroundColor Red
    $validationPassed = $false
}

# Test 2: Squire battle plan route
Write-Host "  [Test 2] Squire UI route..." -NoNewline
try {
    $squireTest = Invoke-WebRequest -Uri "http://localhost/squire/battle-plan" -TimeoutSec 5 -ErrorAction Stop
    if ($squireTest.StatusCode -eq 200 -and $squireTest.Content -match "Battle Plan Randomizer") {
        Write-Host " PASS" -ForegroundColor Green
    } else {
        Write-Host " FAIL (unexpected content)" -ForegroundColor Red
        $validationPassed = $false
    }
} catch {
    Write-Host " FAIL ($($_.Exception.Message))" -ForegroundColor Red
    $validationPassed = $false
}

# Test 3: Static assets
Write-Host "  [Test 3] JavaScript modules..." -NoNewline
try {
    $jsTest = Invoke-WebRequest -Uri "http://localhost/modules/squire/battleplan.js" -TimeoutSec 5 -ErrorAction Stop
    if ($jsTest.StatusCode -eq 200 -and $jsTest.Content -match "renderSquireBattlePlan") {
        Write-Host " PASS" -ForegroundColor Green
    } else {
        Write-Host " FAIL (file not found or invalid)" -ForegroundColor Red
        $validationPassed = $false
    }
} catch {
    Write-Host " FAIL ($($_.Exception.Message))" -ForegroundColor Red
    $validationPassed = $false
}

# Test 4: API through nginx
Write-Host "  [Test 4] API through nginx..." -NoNewline
try {
    $apiNginxTest = Invoke-RestMethod -Uri "http://localhost/api/squire/health" -TimeoutSec 5 -ErrorAction Stop
    if ($apiNginxTest.status -eq "operational") {
        Write-Host " PASS" -ForegroundColor Green
    } else {
        Write-Host " FAIL (unexpected response)" -ForegroundColor Red
        $validationPassed = $false
    }
} catch {
    Write-Host " FAIL ($($_.Exception.Message))" -ForegroundColor Red
    $validationPassed = $false
}

Write-Host ""

# ============================================================================
# Summary
# ============================================================================
Write-Host "========================================================================" -ForegroundColor Cyan

if ($validationPassed) {
    Write-Host "  STATUS: " -NoNewline
    Write-Host "ALL TESTS PASSED - Frontend is working!" -ForegroundColor Green
    Write-Host ""
    Write-Host "  Battle Plan Randomizer UI:" -ForegroundColor White
    Write-Host "    http://localhost/squire/battle-plan" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  Opening browser..." -ForegroundColor Gray
    Start-Process "http://localhost/squire/battle-plan"
    Write-Host ""
    Write-Host "  Next Steps:" -ForegroundColor White
    Write-Host "    1. Select a game system (Age of Sigmar, 40k, or Old World)" -ForegroundColor Gray
    Write-Host "    2. Click 'Generate Battle Plan'" -ForegroundColor Gray
    Write-Host "    3. Review the randomized mission details" -ForegroundColor Gray
    Write-Host "    4. Test generating multiple plans for tournament mode" -ForegroundColor Gray
    Write-Host ""
    exit 0
} else {
    Write-Host "  STATUS: " -NoNewline
    Write-Host "SOME TESTS FAILED" -ForegroundColor Red
    Write-Host ""
    Write-Host "  Debug Information:" -ForegroundColor White
    Write-Host "    View nginx logs:      docker logs squig-nginx" -ForegroundColor Gray
    Write-Host "    View frontend logs:   docker logs squig-frontend" -ForegroundColor Gray
    Write-Host "    View all services:    docker ps" -ForegroundColor Gray
    Write-Host "    Re-run with verbose:  .\scripts\fix-frontend.ps1 -Verbose" -ForegroundColor Gray
    Write-Host ""
    
    if ($Verbose) {
        Write-Host "  Recent nginx errors:" -ForegroundColor Yellow
        docker logs squig-nginx 2>&1 | Select-String "error" | Select-Object -Last 5 | ForEach-Object {
            Write-Host "    $_" -ForegroundColor DarkGray
        }
    }
    
    Write-Host ""
    exit 1
}
