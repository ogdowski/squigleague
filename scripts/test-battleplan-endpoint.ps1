# Test Battle Plan List Endpoint
$ErrorActionPreference = "Stop"

Write-Host "Testing Battle Plan List Endpoint..." -ForegroundColor Cyan
Write-Host ""
Write-Host "Testing Age of Sigmar battle plans..." -ForegroundColor Yellow

try {
    $response = Invoke-RestMethod -Uri "http://localhost/api/squire/battle-plan/list?game_system=age_of_sigmar" -Method Get
    
    $count = $response.Count
    Write-Host "Received $count battle plans" -ForegroundColor Green
    
    if ($count -eq 12) {
        Write-Host "PASS: Correct count - 12 AoS battle plans" -ForegroundColor Green
    } else {
        Write-Host "FAIL: Expected 12 plans, got $count" -ForegroundColor Red
        exit 1
    }
    
    Write-Host ""
    Write-Host "Battle Plan Names:" -ForegroundColor Cyan
    foreach ($plan in $response) {
        Write-Host "  - $($plan.name)" -ForegroundColor White
    }
    
    Write-Host ""
    Write-Host "Battle plan endpoint test PASSED!" -ForegroundColor Green
}
catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
