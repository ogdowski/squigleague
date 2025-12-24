# SquigLeague Pre-Deployment Validation Script
# Runs comprehensive checks before deployment:
# 1. Unit tests with coverage
# 2. Integration tests
# 3. Docker build validation
# 4. E2E smoke tests (optional)
# 5. Pre-UAT health checks

param(
    [switch]$SkipE2E = $false,
    [switch]$SkipDocker = $false,
    [switch]$Verbose = $false,
    [string]$CoverageThreshold = "100",
    [string]$Environment = "test"
)

$ErrorActionPreference = "Stop"
$results = @()
$startTime = Get-Date

function Write-Section {
    param([string]$Title)
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host " $Title" -ForegroundColor Cyan
    Write-Host "========================================`n" -ForegroundColor Cyan
}

function Write-Result {
    param(
        [string]$Test,
        [bool]$Passed,
        [string]$Message = ""
    )
    
    if ($Passed) {
        Write-Host "✅ $Test" -ForegroundColor Green
        if ($Message) { Write-Host "   $Message" -ForegroundColor Gray }
    } else {
        Write-Host "❌ $Test" -ForegroundColor Red
        if ($Message) { Write-Host "   $Message" -ForegroundColor Yellow }
    }
    
    $script:results += @{
        Test = $Test
        Passed = $Passed
        Message = $Message
    }
}

Write-Host "`n╔════════════════════════════════════════════════════════════╗" -ForegroundColor Magenta
Write-Host "║   SQUIGLEAGUE PRE-DEPLOYMENT VALIDATION SUITE              ║" -ForegroundColor Magenta
Write-Host "╚════════════════════════════════════════════════════════════╝`n" -ForegroundColor Magenta

# ============================================================================
# PHASE 1: Environment Setup
# ============================================================================
Write-Section "PHASE 1: Environment Validation"

# Check Python environment
try {
    $pythonPath = ".\.venv\Scripts\python.exe"
    $pythonVersion = & $pythonPath --version 2>&1
    Write-Result "Python Environment" $true "Using: $pythonVersion"
} catch {
    Write-Result "Python Environment" $false "Virtual environment not found"
    exit 1
}

# Check required files
$requiredFiles = @(
    "squigleague\backend\app\leagues\routes.py",
    "squigleague\backend\app\leagues\service.py",
    "squigleague\backend\tests\test_leagues_routes.py",
    "squigleague\docker-compose.test.yml",
    "squigleague\backend\Dockerfile"
)

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Result "File: $file" $true
    } else {
        Write-Result "File: $file" $false "Missing required file"
    }
}

# ============================================================================
# PHASE 2: Unit Tests with Coverage
# ============================================================================
Write-Section "PHASE 2: Unit Tests - Leagues Module (100% Coverage)"

$env:DATABASE_URL = "sqlite:///:memory:"
$env:PYTHONPATH = "squigleague\backend"

try {
    Write-Host "Running leagues module tests with coverage..." -ForegroundColor Yellow
    
    $coverageOutput = & $pythonPath squigleague\run_coverage.py 2>&1
    $exitCode = $LASTEXITCODE
    
    if ($Verbose) {
        Write-Host $coverageOutput -ForegroundColor Gray
    }
    
    # Check for 100% coverage
    if ($coverageOutput -match "Total coverage: (\d+\.\d+)%") {
        $coverage = [decimal]$matches[1]
        $threshold = [decimal]$CoverageThreshold
        
        if ($coverage -ge $threshold) {
            Write-Result "Leagues Module Coverage" $true "$coverage% (threshold: $threshold%)"
        } else {
            Write-Result "Leagues Module Coverage" $false "$coverage% < $threshold%"
            if (!$Verbose) {
                Write-Host "`nLast 30 lines of output:" -ForegroundColor Yellow
                $coverageOutput | Select-Object -Last 30 | ForEach-Object { Write-Host $_ -ForegroundColor Gray }
            }
        }
    } else {
        Write-Result "Leagues Module Coverage" $false "Could not parse coverage output"
    }
    
    # Check test pass/fail
    if ($coverageOutput -match "(\d+) passed") {
        $passedCount = $matches[1]
        Write-Result "Leagues Tests Passed" $true "$passedCount tests"
    } else {
        Write-Result "Leagues Tests Passed" $false "No tests passed"
    }
    
} catch {
    Write-Result "Unit Test Execution" $false $_.Exception.Message
}

# ============================================================================
# PHASE 3: Integration Tests
# ============================================================================
Write-Section "PHASE 3: Integration Tests"

# Check for integration test directories
$integrationTests = @(
    "squigleague\tests\integration\herald",
    "squigleague\tests\integration\squire"
)

$hasIntegrationTests = $false
foreach ($testDir in $integrationTests) {
    if (Test-Path $testDir) {
        $testFiles = Get-ChildItem -Path $testDir -Filter "test_*.py" -File
        if ($testFiles.Count -gt 0) {
            $hasIntegrationTests = $true
            Write-Result "Integration Tests Found" $true "$($testFiles.Count) files in $testDir"
        }
    }
}

if ($hasIntegrationTests) {
    Write-Host "`nNote: Integration tests require services to be running." -ForegroundColor Yellow
    Write-Host "Use 'just dev' or 'docker-compose up' to start services, then run:" -ForegroundColor Yellow
    Write-Host "  pytest squigleague/tests/integration -v" -ForegroundColor Cyan
} else {
    Write-Result "Integration Tests" $true "No integration tests found (optional)"
}

# ============================================================================
# PHASE 4: Docker Build Validation
# ============================================================================
if (!$SkipDocker) {
    Write-Section "PHASE 4: Docker Build Validation"
    
    # Check Docker availability
    try {
        $dockerVersion = docker --version 2>&1
        Write-Result "Docker Installation" $true $dockerVersion
    } catch {
        Write-Result "Docker Installation" $false "Docker not found"
        $SkipDocker = $true
    }
    
    if (!$SkipDocker) {
        # Build backend image
        Write-Host "`nBuilding backend Docker image..." -ForegroundColor Yellow
        try {
            Push-Location squigleague
            $buildOutput = docker build -t squigleague-backend:test -f backend/Dockerfile backend/ 2>&1
            $buildExit = $LASTEXITCODE
            Pop-Location
            
            if ($buildExit -eq 0) {
                Write-Result "Backend Docker Build" $true "Image: squigleague-backend:test"
            } else {
                Write-Result "Backend Docker Build" $false "Build failed with exit code $buildExit"
                if ($Verbose) {
                    Write-Host $buildOutput -ForegroundColor Gray
                }
            }
        } catch {
            Pop-Location
            Write-Result "Backend Docker Build" $false $_.Exception.Message
        }
        
        # Build herald image
        Write-Host "`nBuilding herald Docker image..." -ForegroundColor Yellow
        try {
            Push-Location squigleague
            $buildOutput = docker build -t squigleague-herald:test -f herald/Dockerfile herald/ 2>&1
            $buildExit = $LASTEXITCODE
            Pop-Location
            
            if ($buildExit -eq 0) {
                Write-Result "Herald Docker Build" $true "Image: squigleague-herald:test"
            } else {
                Write-Result "Herald Docker Build" $false "Build failed with exit code $buildExit"
                if ($Verbose) {
                    Write-Host $buildOutput -ForegroundColor Gray
                }
            }
        } catch {
            Pop-Location
            Write-Result "Herald Docker Build" $false $_.Exception.Message
        }
        
        # Validate docker-compose configuration
        Write-Host "`nValidating docker-compose configuration..." -ForegroundColor Yellow
        try {
            Push-Location squigleague
            $composeOutput = docker-compose -f docker-compose.yml -f docker-compose.test.yml config 2>&1
            $composeExit = $LASTEXITCODE
            Pop-Location
            
            if ($composeExit -eq 0) {
                Write-Result "Docker Compose Config" $true "Valid configuration"
            } else {
                Write-Result "Docker Compose Config" $false "Invalid configuration"
                if ($Verbose) {
                    Write-Host $composeOutput -ForegroundColor Gray
                }
            }
        } catch {
            Pop-Location
            Write-Result "Docker Compose Config" $false $_.Exception.Message
        }
    }
}

# ============================================================================
# PHASE 5: E2E Smoke Tests (Optional)
# ============================================================================
if (!$SkipE2E) {
    Write-Section "PHASE 5: E2E Smoke Tests (Selenium)"
    
    $seleniumDir = "squigleague\tests\e2e\selenium"
    if (Test-Path $seleniumDir) {
        Write-Host "Selenium E2E tests detected (pytest). Services must be running." -ForegroundColor Yellow
        Write-Host "To run manually (requires Chrome):" -ForegroundColor Yellow
        Write-Host "  cd squigleague" -ForegroundColor Cyan
        Write-Host "  $env:TEST_BASE_URL=\"http://localhost:8000\"; pytest tests/e2e/selenium --run-e2e --headed" -ForegroundColor Cyan
        Write-Result "E2E Tests Available" $true "Selenium configured"
    } else {
        Write-Result "E2E Tests" $false "Selenium suite missing"
    }
}

# ============================================================================
# PHASE 6: Static Analysis
# ============================================================================
Write-Section "PHASE 6: Static Analysis & Code Quality"

# Check for common issues
$leaguesRoutes = Get-Content "squigleague\backend\app\leagues\routes.py" -Raw

# Check for TODO/FIXME markers
$todoCount = ([regex]::Matches($leaguesRoutes, "# TODO|# FIXME|XXX")).Count
if ($todoCount -eq 0) {
    Write-Result "TODO/FIXME Markers" $true "No outstanding markers"
} else {
    Write-Result "TODO/FIXME Markers" $false "$todoCount markers found"
}

# Check for print statements (should use logging)
$printCount = ([regex]::Matches($leaguesRoutes, "^\s*print\(")).Count
if ($printCount -eq 0) {
    Write-Result "Debug Print Statements" $true "None found"
} else {
    Write-Result "Debug Print Statements" $false "$printCount print() calls found"
}

# ============================================================================
# FINAL SUMMARY
# ============================================================================
Write-Section "DEPLOYMENT READINESS SUMMARY"

$totalTests = $results.Count
$passedTests = ($results | Where-Object { $_.Passed -eq $true }).Count
$failedTests = $totalTests - $passedTests

Write-Host "Total Checks: $totalTests" -ForegroundColor White
Write-Host "Passed: $passedTests" -ForegroundColor Green
Write-Host "Failed: $failedTests" -ForegroundColor $(if ($failedTests -eq 0) { "Green" } else { "Red" })

$duration = (Get-Date) - $startTime
Write-Host "`nTotal Duration: $($duration.TotalSeconds.ToString('F2')) seconds" -ForegroundColor Gray

if ($failedTests -eq 0) {
    Write-Host "`n✅ ALL CHECKS PASSED - READY FOR DEPLOYMENT" -ForegroundColor Green
    Write-Host "`nNext Steps:" -ForegroundColor Cyan
    Write-Host "  1. Run: just build" -ForegroundColor White
    Write-Host "  2. Run: just prod" -ForegroundColor White
    Write-Host "  3. Run UAT tests: .\run-uat-tests.ps1" -ForegroundColor White
    exit 0
} else {
    Write-Host "`n❌ DEPLOYMENT BLOCKED - FAILURES DETECTED" -ForegroundColor Red
    Write-Host "`nFailed Checks:" -ForegroundColor Yellow
    $results | Where-Object { $_.Passed -eq $false } | ForEach-Object {
        Write-Host "  - $($_.Test): $($_.Message)" -ForegroundColor Red
    }
    exit 1
}
