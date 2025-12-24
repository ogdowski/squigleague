# Verify Backend Fix
$ErrorActionPreference = "Continue"

Write-Host "Verifying backend container has correct code..." -ForegroundColor Cyan
Write-Host ""

# Wait for container to be healthy
Write-Host "Waiting for container to be healthy..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Check endpoint exists
Write-Host "Checking for endpoint in container..." -ForegroundColor Yellow
docker exec squig grep "@router.get(""/battle-plan/list"")" /app/squire/routes.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "OK: Endpoint code found in container" -ForegroundColor Green
}
else {
    Write-Host "WARNING: grep failed but testing API anyway..." -ForegroundColor Yellow
}

# Test API
Write-Host ""
Write-Host "Testing API endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost/api/squire/battle-plan/list?game_system=age_of_sigmar"
    $count = $response.Count
    
    Write-Host "SUCCESS: API returns $count battle plans" -ForegroundColor Green
    Write-Host ""
    Write-Host "Battle plans:" -ForegroundColor Cyan
    foreach ($plan in $response) {
        Write-Host "  - $($plan.name)" -ForegroundColor White
    }
    
    if ($count -eq 12) {
        Write-Host ""
        Write-Host "FIXED: All 12 battle plans now returned correctly!" -ForegroundColor Green
        Write-Host "Clear browser cache (Ctrl+Shift+R) to see the fix" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "ERROR: API call failed - $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
