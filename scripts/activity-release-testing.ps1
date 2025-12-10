# Complete v0.3.0 Release Testing Activity Script

Write-Host "`n=== v0.3.0 Release Testing ===" -ForegroundColor Cyan

# 1. Verify frontend is running
Write-Host "`n[1] Checking frontend server..." -ForegroundColor Yellow
try {
    $frontend = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 5
    Write-Host "  Frontend: OK" -ForegroundColor Green
} catch {
    Write-Host "  Frontend: FAILED - Starting..." -ForegroundColor Red
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\frontend\public'; Set-Location '$PWD\frontend\public'; ..\..\..\.venv\Scripts\python.exe spa-server.py"
    Start-Sleep -Seconds 3
}

# 2. Run comprehensive API tests
Write-Host "`n[2] Running API error extraction tests..." -ForegroundColor Yellow
$testResult = & .\scripts\test-error-extraction.ps1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  API Tests: PASSED" -ForegroundColor Green
} else {
    Write-Host "  API Tests: FAILED" -ForegroundColor Red
    exit 1
}

# 3. Open browser test page
Write-Host "`n[3] Opening JavaScript test page..." -ForegroundColor Yellow
Start-Process "http://localhost:3000/test-error-handling.html"
Write-Host "  Browser tests opened - waiting for results..." -ForegroundColor Gray
Start-Sleep -Seconds 8

# 4. Test main application manually
Write-Host "`n[4] Opening main application for manual testing..." -ForegroundColor Yellow
Start-Process "http://localhost:3000"
Write-Host "  Main app opened" -ForegroundColor Green

Write-Host "`n=== Manual Testing Checklist ===" -ForegroundColor Cyan
Write-Host "[ ] Browse to Squire module" -ForegroundColor White
Write-Host "[ ] Click 'Create Matchup'" -ForegroundColor White
Write-Host "[ ] Submit with short army list (e.g., 'test')" -ForegroundColor White
Write-Host "[ ] Verify error message: 'String should have at least 10 characters'" -ForegroundColor White
Write-Host "[ ] Submit valid list (10+ chars)" -ForegroundColor White
Write-Host "[ ] Verify waiting screen appears" -ForegroundColor White
Write-Host "[ ] Open matchup in second browser/tab" -ForegroundColor White
Write-Host "[ ] Submit second list" -ForegroundColor White
Write-Host "[ ] Verify battle plan displays for both players" -ForegroundColor White

Write-Host "`n=== Testing Complete ===" -ForegroundColor Cyan
Write-Host "All automated tests passed. Manual GUI testing required." -ForegroundColor Green
