# Test Battle Plan API with Browser Parameters
$ErrorActionPreference = "Stop"

Write-Host "Testing battle plan API with actual frontend parameters..." -ForegroundColor Cyan
Write-Host ""

# Test with the exact parameter the frontend sends
Write-Host "Testing with game_system=age_of_sigmar (what frontend sends)..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost/api/squire/battle-plan/list?game_system=age_of_sigmar" -Method Get
    Write-Host "Result: $($response.Count) battle plans" -ForegroundColor Green
    $response | ForEach-Object { Write-Host "  - $($_.name)" -ForegroundColor White }
}
catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Response: $($_.ErrorDetails.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "Testing browser cache clear needed..." -ForegroundColor Yellow
Write-Host "Press Ctrl+F5 in browser to hard refresh and clear cache" -ForegroundColor Cyan
