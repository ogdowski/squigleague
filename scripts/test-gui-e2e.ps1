# End-to-End GUI Testing Script
# ACTUALLY tests the GUI by creating a matchup and verifying the URL works

Write-Host "`n==================================================================" -ForegroundColor Cyan
Write-Host "GUI END-TO-END TEST" -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan

$ErrorActionPreference = "Stop"

# Kill existing servers
Write-Host "`n[1/6] Stopping existing servers..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "*python*" } | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Start backend
Write-Host "[2/6] Starting backend..." -ForegroundColor Yellow
$env:REQUIRE_DATABASE = "false"
$backendJob = Start-Job -ScriptBlock {
    Set-Location "e:\repos\suigleague"
    & ".\.venv\Scripts\python.exe" -m uvicorn herald.main:app --reload --port 8000
}
Start-Sleep -Seconds 4

# Verify backend
Write-Host "[3/6] Verifying backend..." -ForegroundColor Yellow
try {
    $health = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing
    Write-Host "  Backend: OK" -ForegroundColor Green
} catch {
    Write-Host "  Backend: FAILED - $($_.Exception.Message)" -ForegroundColor Red
    Stop-Job $backendJob
    exit 1
}

# Start frontend
Write-Host "[4/6] Starting frontend..." -ForegroundColor Yellow
$frontendJob = Start-Job -ScriptBlock {
    Set-Location "e:\repos\suigleague\frontend\public"
    python spa-server.py
}
Start-Sleep -Seconds 3

# Test API matchup creation
Write-Host "[5/6] Creating test matchup via API..." -ForegroundColor Yellow
try {
    $createBody = @{ game_system = "age_of_sigmar" } | ConvertTo-Json
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/squire/matchup/create" -Method POST -Body $createBody -ContentType "application/json" -UseBasicParsing
    $matchup = $response.Content | ConvertFrom-Json
    $matchupId = $matchup.matchup_id
    $shareUrl = $matchup.share_url
    Write-Host "  Matchup created: $matchupId" -ForegroundColor Green
    Write-Host "  Share URL: $shareUrl" -ForegroundColor Green
} catch {
    Write-Host "  Failed to create matchup: $($_.Exception.Message)" -ForegroundColor Red
    Stop-Job $backendJob, $frontendJob
    exit 1
}

# Test if frontend URL returns HTML (not 404)
Write-Host "[6/6] Testing frontend URL..." -ForegroundColor Yellow
$frontendUrl = "http://localhost:3000$shareUrl"
Write-Host "  Testing: $frontendUrl" -ForegroundColor Cyan

try {
    $pageResponse = Invoke-WebRequest -Uri $frontendUrl -UseBasicParsing
    
    if ($pageResponse.StatusCode -eq 200) {
        # Check if it's HTML (not error page)
        if ($pageResponse.Content -like "*Matchup System*") {
            Write-Host "  Frontend URL: OK - Page loads correctly" -ForegroundColor Green
        } else {
            Write-Host "  Frontend URL: WARNING - Page loads but content unexpected" -ForegroundColor Yellow
            Write-Host "  Content preview: $($pageResponse.Content.Substring(0, 200))" -ForegroundColor Gray
        }
    } else {
        Write-Host "  Frontend URL: FAILED - Status $($pageResponse.StatusCode)" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "  Frontend URL: FAILED - $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "  This means the routing is STILL broken" -ForegroundColor Red
    Stop-Job $backendJob, $frontendJob
    exit 1
}

Write-Host "`n==================================================================" -ForegroundColor Cyan
Write-Host "MANUAL VERIFICATION REQUIRED" -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "`nServers are running. Now MANUALLY test:" -ForegroundColor Yellow
Write-Host "1. Open: http://localhost:3000" -ForegroundColor Cyan
Write-Host "2. Click 'Create Matchup'" -ForegroundColor Cyan
Write-Host "3. Verify it creates matchup without errors" -ForegroundColor Cyan
Write-Host "4. Copy the share URL" -ForegroundColor Cyan
Write-Host "5. Open share URL in incognito window" -ForegroundColor Cyan
Write-Host "6. Verify it loads the matchup page (not 404)" -ForegroundColor Cyan
Write-Host "`nTest matchup URL: $frontendUrl" -ForegroundColor Green
Write-Host "`nPress Ctrl+C to stop servers when done testing" -ForegroundColor Yellow

# Keep script running so servers stay alive
try {
    while ($true) {
        Start-Sleep -Seconds 5
        # Check if jobs are still running
        if ($backendJob.State -ne 'Running' -or $frontendJob.State -ne 'Running') {
            Write-Host "`nServer died! Check logs." -ForegroundColor Red
            break
        }
    }
} finally {
    Write-Host "`nStopping servers..." -ForegroundColor Yellow
    Stop-Job $backendJob, $frontendJob -ErrorAction SilentlyContinue
    Remove-Job $backendJob, $frontendJob -ErrorAction SilentlyContinue
}
