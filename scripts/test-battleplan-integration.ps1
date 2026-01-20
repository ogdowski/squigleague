#!/usr/bin/env pwsh
# Test battle plan image integration
# CRITICAL: Must run after any backend/frontend changes affecting matchup display

$ErrorActionPreference = "Stop"

Write-Host "`n=== Battle Plan Integration Test ===" -ForegroundColor Cyan

# Test 1: Check backend MAP_IMAGES exists
Write-Host "`n[1/4] Checking backend MAP_IMAGES dictionary..." -ForegroundColor Yellow
$mapCheck = docker exec squig-backend sh -c "grep -c 'MAP_IMAGES = {' /app/app/matchup/service.py" 2>$null
if ($mapCheck -eq "1") {
    Write-Host "  Backend has MAP_IMAGES dictionary" -ForegroundColor Green
} else {
    Write-Host "  FAIL: MAP_IMAGES not found in service.py" -ForegroundColor Red
    exit 1
}

# Test 2: Check API returns map_image field
Write-Host "`n[2/4] Testing API map_image field..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost/api/matchup/stats" -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -ne 200) {
        Write-Host "  FAIL: Backend not responding" -ForegroundColor Red
        exit 1
    }
    
    # Get a revealed matchup (requires authentication)
    # For now, just check schema exists
    $schemaCheck = docker exec squig-backend sh -c "grep 'map_image:' /app/app/matchup/schemas.py" 2>$null
    if ($schemaCheck) {
        Write-Host "  Schema has map_image field" -ForegroundColor Green
    } else {
        Write-Host "  FAIL: map_image not in MatchupReveal schema" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "  FAIL: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test 3: Check frontend has images
Write-Host "`n[3/4] Checking frontend image files..." -ForegroundColor Yellow
$imageCount = docker exec squig-frontend sh -c "ls -1 /usr/share/nginx/html/assets/battle-plans/*.png 2>/dev/null | wc -l" 2>$null
if ([int]$imageCount -ge 20) {
    Write-Host "  Frontend has $imageCount battle plan images" -ForegroundColor Green
} else {
    Write-Host "  FAIL: Only $imageCount images found (expected 20+)" -ForegroundColor Red
    exit 1
}

# Test 4: Check specific image exists
Write-Host "`n[4/4] Verifying image accessibility..." -ForegroundColor Yellow
try {
    $testImage = Invoke-WebRequest -Uri "http://localhost/assets/battle-plans/aos-noxious-nexus-matplotlib.png" -UseBasicParsing -TimeoutSec 5
    if ($testImage.StatusCode -eq 200 -and $testImage.RawContentLength -gt 50000) {
        Write-Host "  Test image loads: HTTP $($testImage.StatusCode), $($testImage.RawContentLength) bytes" -ForegroundColor Green
    } else {
        Write-Host "  FAIL: Image too small or wrong status" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "  FAIL: Cannot load image - $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host "`n=== ALL TESTS PASSED ===" -ForegroundColor Green
Write-Host "Battle plan integration working correctly`n" -ForegroundColor Green

exit 0
