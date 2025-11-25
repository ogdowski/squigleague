# Force Rebuild and Deploy
# Rebuilds everything without cache

Write-Host "`n========================================================================" -ForegroundColor Cyan
Write-Host "  FORCE REBUILD - NO CACHE" -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/3] Stopping containers..." -ForegroundColor Yellow
docker-compose down
Write-Host "    Containers stopped" -ForegroundColor Green
Write-Host ""

Write-Host "[2/3] Building with --no-cache..." -ForegroundColor Yellow
docker-compose build --no-cache squig frontend
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Build failed" -ForegroundColor Red
    exit 1
}
Write-Host "    Build complete" -ForegroundColor Green
Write-Host ""

Write-Host "[3/3] Starting containers..." -ForegroundColor Yellow
docker-compose up -d
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Start failed" -ForegroundColor Red
    exit 1
}
Write-Host "    Containers started" -ForegroundColor Green
Write-Host ""

Write-Host "Waiting for services..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/api/squire/health" -TimeoutSec 10
    Write-Host "Backend: READY" -ForegroundColor Green
} catch {
    Write-Host "Backend: NOT READY - $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================================================" -ForegroundColor Green
Write-Host "  REBUILD COMPLETE" -ForegroundColor Green
Write-Host "========================================================================" -ForegroundColor Green
Write-Host ""
