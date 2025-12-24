# SquigLeague Integration Test Runner
# Starts services and runs integration tests against live instances

param(
    [switch]$CleanStart = $false,
    [switch]$KeepRunning = $false,
    [string]$TestPath = "squigleague\tests\integration",
    [string]$Service = "all"  # all, herald, squire, backend
)

$ErrorActionPreference = "Stop"

Write-Host "`n╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   SQUIGLEAGUE INTEGRATION TEST RUNNER                      ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# ============================================================================
# Step 1: Start Test Environment
# ============================================================================
Write-Host "[1/4] Starting test environment..." -ForegroundColor Yellow

try {
    Push-Location squigleague
    
    if ($CleanStart) {
        Write-Host "  Cleaning existing containers..." -ForegroundColor Gray
        docker-compose -f docker-compose.test.yml down -v
    }
    
    Write-Host "  Starting services..." -ForegroundColor Gray
    docker-compose -f docker-compose.test.yml up -d
    
    # Wait for services to be healthy
    Write-Host "  Waiting for services to be ready..." -ForegroundColor Gray
    Start-Sleep -Seconds 5
    
    # Check health
    $healthCheck = docker-compose -f docker-compose.test.yml ps
    Write-Host $healthCheck -ForegroundColor Gray
    
    Pop-Location
} catch {
    Pop-Location
    Write-Host "❌ Failed to start test environment: $_" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Test environment ready`n" -ForegroundColor Green

# ============================================================================
# Step 2: Set Environment Variables
# ============================================================================
Write-Host "[2/4] Configuring test environment..." -ForegroundColor Yellow

$env:TEST_DATABASE_URL = "postgresql://test_user:test_password@localhost:5433/test_squigleague"
$env:PYTHONPATH = "squigleague\backend"
$env:API_BASE_URL = "http://localhost:8000"

Write-Host "  DATABASE_URL: $env:TEST_DATABASE_URL" -ForegroundColor Gray
Write-Host "  API_BASE_URL: $env:API_BASE_URL" -ForegroundColor Gray
Write-Host "✅ Environment configured`n" -ForegroundColor Green

# ============================================================================
# Step 3: Run Integration Tests
# ============================================================================
Write-Host "[3/4] Running integration tests..." -ForegroundColor Yellow

$testFilter = switch ($Service) {
    "herald" { "squigleague\tests\integration\herald" }
    "squire" { "squigleague\tests\integration\squire" }
    "backend" { "squigleague\tests\integration\backend" }
    default { $TestPath }
}

if (!(Test-Path $testFilter)) {
    Write-Host "⚠️  Test path not found: $testFilter" -ForegroundColor Yellow
    Write-Host "  Creating integration test structure..." -ForegroundColor Gray
    
    # Create integration test structure if it doesn't exist
    $dirs = @(
        "squigleague\tests\integration\backend",
        "squigleague\tests\integration\backend\leagues"
    )
    
    foreach ($dir in $dirs) {
        if (!(Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            New-Item -ItemType File -Path "$dir\__init__.py" | Out-Null
        }
    }
    
    Write-Host "  Note: No integration tests found. Unit tests cover current functionality." -ForegroundColor Yellow
    Write-Host "✅ Test structure created`n" -ForegroundColor Green
} else {
    try {
        Write-Host "  Test Path: $testFilter" -ForegroundColor Gray
        
        $testOutput = & .\.venv\Scripts\python.exe -m pytest $testFilter -v --tb=short --color=yes 2>&1
        $testExit = $LASTEXITCODE
        
        Write-Host $testOutput
        
        if ($testExit -eq 0) {
            Write-Host "`n✅ All integration tests passed`n" -ForegroundColor Green
        } else {
            Write-Host "`n❌ Integration tests failed (exit code: $testExit)`n" -ForegroundColor Red
        }
    } catch {
        Write-Host "❌ Test execution failed: $_" -ForegroundColor Red
        $testExit = 1
    }
}

# ============================================================================
# Step 4: Cleanup
# ============================================================================
Write-Host "[4/4] Cleanup..." -ForegroundColor Yellow

if (!$KeepRunning) {
    try {
        Push-Location squigleague
        Write-Host "  Stopping test services..." -ForegroundColor Gray
        docker-compose -f docker-compose.test.yml down
        Pop-Location
        Write-Host "✅ Services stopped`n" -ForegroundColor Green
    } catch {
        Pop-Location
        Write-Host "⚠️  Warning: Failed to stop services: $_" -ForegroundColor Yellow
    }
} else {
    Write-Host "  Services left running (use -KeepRunning:$false to stop)" -ForegroundColor Gray
    Write-Host "  To stop manually: docker-compose -f docker-compose.test.yml down" -ForegroundColor Cyan
}

# ============================================================================
# Summary
# ============================================================================
Write-Host "`n╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   INTEGRATION TEST SUMMARY                                 ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

if ($testExit -eq 0) {
    Write-Host "Status: ✅ PASSED" -ForegroundColor Green
    exit 0
} else {
    Write-Host "Status: ❌ FAILED" -ForegroundColor Red
    exit 1
}
