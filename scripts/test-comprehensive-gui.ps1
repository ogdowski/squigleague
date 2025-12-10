# Comprehensive GUI Test for v0.3.0 Release
# Tests the ACTUAL user experience, not just API endpoints

$ErrorActionPreference = "Stop"

Write-Host "`n================================================================" -ForegroundColor Cyan
Write-Host "COMPREHENSIVE GUI TEST - v0.3.0 AoS Matchups" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan

$testResults = @{
    Passed = @()
    Failed = @()
}

function Test-Step {
    param(
        [string]$Name,
        [scriptblock]$Action
    )
    
    Write-Host "`n[TEST] $Name" -ForegroundColor Yellow
    try {
        & $Action
        Write-Host "  PASS" -ForegroundColor Green
        $script:testResults.Passed += $Name
        return $true
    } catch {
        Write-Host "  FAIL: $($_.Exception.Message)" -ForegroundColor Red
        $script:testResults.Failed += "$Name - $($_.Exception.Message)"
        return $false
    }
}

# Cleanup
Write-Host "`n[SETUP] Cleaning up existing servers..." -ForegroundColor Cyan
Get-Job | Remove-Job -Force -ErrorAction SilentlyContinue
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Start Backend
Write-Host "[SETUP] Starting backend server..." -ForegroundColor Cyan
$env:REQUIRE_DATABASE = "false"
$backendJob = Start-Job -ScriptBlock {
    Set-Location "e:\repos\suigleague"
    $env:REQUIRE_DATABASE = "false"
    & ".\.venv\Scripts\python.exe" -m uvicorn herald.main:app --reload --port 8000
}
Start-Sleep -Seconds 4

# Start Frontend
Write-Host "[SETUP] Starting frontend SPA server..." -ForegroundColor Cyan
$frontendJob = Start-Job -ScriptBlock {
    Set-Location "e:\repos\suigleague\frontend\public"
    python spa-server.py
}
Start-Sleep -Seconds 3

# TEST 1: Backend Health
Test-Step "Backend health check" {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing
    if ($response.StatusCode -ne 200) {
        throw "Backend returned status $($response.StatusCode)"
    }
}

# TEST 2: Frontend Responds
Test-Step "Frontend loads index.html" {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing
    if ($response.StatusCode -ne 200) {
        throw "Frontend returned status $($response.StatusCode)"
    }
    if ($response.Content -notmatch "Matchup System") {
        throw "Frontend content incorrect"
    }
}

# TEST 3: JavaScript Files Load
Test-Step "api-config.js loads" {
    $response = Invoke-WebRequest -Uri "http://localhost:3000/src/api-config.js" -UseBasicParsing
    if ($response.StatusCode -ne 200) {
        throw "api-config.js not found"
    }
    if ($response.Content -notmatch "getApiUrl") {
        throw "api-config.js missing getApiUrl function"
    }
}

Test-Step "matchup.js loads" {
    $response = Invoke-WebRequest -Uri "http://localhost:3000/modules/squire/matchup.js" -UseBasicParsing
    if ($response.StatusCode -ne 200) {
        throw "matchup.js not found"
    }
    if ($response.Content -notmatch "matchupManager") {
        throw "matchup.js missing matchupManager function"
    }
}

# TEST 4: API Endpoints
Test-Step "GET /api/squire/systems returns AoS" {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/squire/systems" -UseBasicParsing
    $data = $response.Content | ConvertFrom-Json
    $aos = $data | Where-Object { $_.game_system -eq 'age_of_sigmar' }
    if (-not $aos) {
        throw "AoS system not found"
    }
}

Test-Step "GET /api/squire/battle-plan/random" {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/squire/battle-plan/random?system=age_of_sigmar" -UseBasicParsing
    $data = $response.Content | ConvertFrom-Json
    if (-not $data.name) {
        throw "No name in response"
    }
    Write-Host "    Mission: $($data.name)" -ForegroundColor Gray
}

# TEST 5: Create Matchup
$global:testMatchupId = $null
Test-Step "POST /api/squire/matchup/create" {
    $body = @{ game_system = "age_of_sigmar" } | ConvertTo-Json
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/squire/matchup/create" -Method POST -Body $body -ContentType "application/json" -UseBasicParsing
    $data = $response.Content | ConvertFrom-Json
    
    if (-not $data.matchup_id) {
        throw "No matchup_id in response"
    }
    if (-not $data.share_url) {
        throw "No share_url in response"
    }
    
    $global:testMatchupId = $data.matchup_id
    Write-Host "    Created: $global:testMatchupId" -ForegroundColor Gray
}

# TEST 6: SPA Routing
Test-Step "Frontend serves matchup URL via SPA routing" {
    $url = "http://localhost:3000/squire/matchup/$global:testMatchupId"
    $response = Invoke-WebRequest -Uri $url -UseBasicParsing
    
    if ($response.StatusCode -ne 200) {
        throw "Matchup URL returned $($response.StatusCode)"
    }
    if ($response.Content -notmatch "Matchup System") {
        throw "SPA routing broken"
    }
    
    Write-Host "    SPA routing works" -ForegroundColor Gray
}

# TEST 7: CORS
Test-Step "CORS allows localhost:3000" {
    $headers = @{ "Origin" = "http://localhost:3000" }
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/squire/systems" -Headers $headers -UseBasicParsing
    
    $corsHeader = $response.Headers['Access-Control-Allow-Origin']
    if (-not $corsHeader) {
        throw "No CORS header"
    }
}

# TEST 8: Submit Player 1
Test-Step "Submit Player 1 army list" {
    $body = @{
        player_name = "Test Player 1"
        army_list = "Army List 1 with enough characters"
    } | ConvertTo-Json
    
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/squire/matchup/$global:testMatchupId/submit" -Method POST -Body $body -ContentType "application/json" -UseBasicParsing
    $data = $response.Content | ConvertFrom-Json
    
    if ($data.waiting_count -ne 1) {
        throw "Expected waiting_count=1, got $($data.waiting_count)"
    }
}

# TEST 9: Submit Player 2
Test-Step "Submit Player 2 triggers battle plan" {
    $body = @{
        player_name = "Test Player 2"
        army_list = "Army List 2 with enough characters"
    } | ConvertTo-Json
    
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/squire/matchup/$global:testMatchupId/submit" -Method POST -Body $body -ContentType "application/json" -UseBasicParsing
    $data = $response.Content | ConvertFrom-Json
    
    if (-not $data.is_complete) {
        throw "Expected is_complete=true"
    }
    if (-not $data.battle_plan.name) {
        throw "No battle plan generated"
    }
    
    Write-Host "    Battle plan: $($data.battle_plan.name)" -ForegroundColor Gray
}

# TEST 10: Retrieve Complete Matchup
Test-Step "GET complete matchup data" {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/squire/matchup/$global:testMatchupId" -UseBasicParsing
    $data = $response.Content | ConvertFrom-Json
    
    if (-not $data.is_complete) {
        throw "Matchup not complete"
    }
    if (-not $data.player1 -or -not $data.player2 -or -not $data.battle_plan) {
        throw "Missing matchup data"
    }
}

# TEST 11: JavaScript Syntax
Test-Step "matchup.js has no obvious errors" {
    $js = Get-Content "e:\repos\suigleague\frontend\public\modules\squire\matchup.js" -Raw
    
    if ($js -match 'this\.error\s*=\s*err\s*;') {
        throw "Found error object assignment bug"
    }
    if ($js -notmatch 'getApiUrl') {
        throw "Not using getApiUrl function"
    }
}

# TEST 12: Deployment Script
Test-Step "Deployment uses spa-server.py" {
    $script = Get-Content "e:\repos\suigleague\scripts\deploy-local-v0.3.0.ps1" -Raw
    
    if ($script -notmatch 'spa-server') {
        throw "Deployment script not using spa-server"
    }
}

# Results
Write-Host "`n================================================================" -ForegroundColor Cyan
Write-Host "AUTOMATED TEST RESULTS" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "PASSED: $($testResults.Passed.Count)" -ForegroundColor Green
foreach ($test in $testResults.Passed) {
    Write-Host "  $test" -ForegroundColor Green
}

if ($testResults.Failed.Count -gt 0) {
    Write-Host "`nFAILED: $($testResults.Failed.Count)" -ForegroundColor Red
    foreach ($test in $testResults.Failed) {
        Write-Host "  $test" -ForegroundColor Red
    }
    exit 1
}

# Manual Testing Required
Write-Host "`n================================================================" -ForegroundColor Cyan
Write-Host "MANUAL BROWSER TESTING REQUIRED" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "Servers are running. Complete these tests in browser:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Open http://localhost:3000" -ForegroundColor White
Write-Host "2. Click Create Matchup button" -ForegroundColor White
Write-Host "3. Verify NO errors appear" -ForegroundColor White
Write-Host "4. Copy share link and open in incognito window" -ForegroundColor White
Write-Host "5. Submit lists in both windows" -ForegroundColor White
Write-Host "6. Verify battle plan appears with mission name" -ForegroundColor White
Write-Host "7. Check browser console for JavaScript errors" -ForegroundColor White
Write-Host ""
Write-Host "All automated tests PASSED" -ForegroundColor Green
