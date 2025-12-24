# quick-restart.ps1
# Quick restart without rebuild (for code changes)

param(
    [string]$Service = "all"
)

$ErrorActionPreference = "Stop"

Write-Host "=== Quick Restart ===" -ForegroundColor Cyan
Write-Host ""

if ($Service -eq "all") {
    Write-Host "Restarting all services..." -ForegroundColor Yellow
    docker-compose restart
} else {
    Write-Host "Restarting $Service..." -ForegroundColor Yellow
    docker-compose restart $Service
}

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Restart failed" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Waiting for services..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Check health
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/herald/health" -UseBasicParsing -TimeoutSec 5
    Write-Host "Backend is healthy" -ForegroundColor Green
} catch {
    Write-Host "WARNING: Backend health check failed" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== Restart Complete ===" -ForegroundColor Green
