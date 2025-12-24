# Fix Battle Plan Endpoint - Rebuild Backend
$ErrorActionPreference = "Stop"

Write-Host "The backend container has old code - rebuilding..." -ForegroundColor Red
Write-Host ""

# Rebuild just the backend container
Write-Host "Rebuilding squig backend container..." -ForegroundColor Yellow
docker-compose build squig

if ($LASTEXITCODE -ne 0) {
    Write-Host "Build failed!" -ForegroundColor Red
    exit 1
}

Write-Host "Restarting squig container..." -ForegroundColor Yellow
docker-compose up -d squig

Start-Sleep -Seconds 5

# Verify
Write-Host ""
Write-Host "Verifying endpoint exists in container..." -ForegroundColor Yellow
$hasEndpoint = docker exec squig grep -c "@router.get(""/battle-plan/list"")" /app/squire/routes.py 2>$null

if ($hasEndpoint -gt 0) {
    Write-Host "SUCCESS: Endpoint code is now in container" -ForegroundColor Green
    
    # Test API
    Write-Host ""
    Write-Host "Testing API..." -ForegroundColor Yellow
    $response = Invoke-RestMethod -Uri "http://localhost/api/squire/battle-plan/list?game_system=age_of_sigmar"
    Write-Host "API now returns: $($response.Count) battle plans" -ForegroundColor Green
}
else {
    Write-Host "ERROR: Endpoint still not in container" -ForegroundColor Red
    exit 1
}
