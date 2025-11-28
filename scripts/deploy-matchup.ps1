# Deploy Matchup Feature
# Rebuilds backend and frontend with matchup system

Write-Host "`n========================================================================" -ForegroundColor Cyan
Write-Host "  DEPLOY MATCHUP FEATURE" -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Rebuild backend
Write-Host "[1/4] Rebuilding backend (squig)..." -ForegroundColor Yellow
docker-compose build squig
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Backend build failed" -ForegroundColor Red
    exit 1
}
Write-Host "    Backend built successfully" -ForegroundColor Green
Write-Host ""

# Step 2: Rebuild frontend
Write-Host "[2/4] Rebuilding frontend..." -ForegroundColor Yellow
docker-compose build frontend
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Frontend build failed" -ForegroundColor Red
    exit 1
}
Write-Host "    Frontend built successfully" -ForegroundColor Green
Write-Host ""

# Step 3: Restart services
Write-Host "[3/4] Restarting services..." -ForegroundColor Yellow
docker-compose restart squig frontend nginx
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Service restart failed" -ForegroundColor Red
    exit 1
}
Write-Host "    Services restarted" -ForegroundColor Green
Write-Host ""

# Step 4: Wait for services
Write-Host "[4/4] Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Test backend
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/api/squire/health" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "    Backend: READY" -ForegroundColor Green
} catch {
    Write-Host "    Backend: NOT READY" -ForegroundColor Red
    exit 1
}

# Test frontend
try {
    $frontend = Invoke-WebRequest -Uri "http://localhost/" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "    Frontend: READY" -ForegroundColor Green
} catch {
    Write-Host "    Frontend: NOT READY" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================================================" -ForegroundColor Green
Write-Host "  DEPLOYMENT COMPLETE" -ForegroundColor Green
Write-Host "========================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Matchup System:" -ForegroundColor Cyan
Write-Host "  UI:  http://localhost/squire/matchup" -ForegroundColor White
Write-Host "  API: http://localhost:8000/api/squire/matchup/*" -ForegroundColor White
Write-Host ""
Write-Host "Battle Plan Reference:" -ForegroundColor Cyan
Write-Host "  UI:  http://localhost/squire/battle-plan" -ForegroundColor White
Write-Host ""
