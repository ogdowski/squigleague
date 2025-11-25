#!/usr/bin/env pwsh
# Rebuild all containers from scratch
# Usage: .\scripts\rebuild-all.ps1

$ErrorActionPreference = "Continue"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "REBUILD ALL CONTAINERS" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Step 1: Stop and remove containers
Write-Host "[1/4] Stopping containers..." -ForegroundColor Yellow
docker-compose -f docker-compose.yml -f docker-compose.dev.yml down 2>&1 | Out-Null
Write-Host "   Done" -ForegroundColor Green

# Step 2: Build with no cache
Write-Host "`n[2/4] Building containers (no cache)..." -ForegroundColor Yellow
docker-compose -f docker-compose.yml -f docker-compose.dev.yml build --no-cache
if ($LASTEXITCODE -ne 0) {
    Write-Host "   FAILED: Build error" -ForegroundColor Red
    exit 1
}
Write-Host "   Done" -ForegroundColor Green

# Step 3: Start services
Write-Host "`n[3/4] Starting services..." -ForegroundColor Yellow
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
if ($LASTEXITCODE -ne 0) {
    Write-Host "   FAILED: Startup error" -ForegroundColor Red
    exit 1
}
Write-Host "   Done" -ForegroundColor Green

# Step 4: Wait for health check
Write-Host "`n[4/4] Waiting for services to be ready..." -ForegroundColor Yellow
$maxAttempts = 30
$attempt = 0
$ready = $false

while ($attempt -lt $maxAttempts -and !$ready) {
    Start-Sleep -Seconds 2
    $attempt++
    
    try {
        $health = Invoke-RestMethod -Uri "http://localhost/api/squire/health" -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($health.status -eq "operational") {
            $ready = $true
        }
    } catch {
        # Not ready yet
    }
    
    Write-Host "   Attempt $attempt/$maxAttempts..." -ForegroundColor Gray
}

if ($ready) {
    Write-Host "   Ready!" -ForegroundColor Green
    
    # Show container status
    Write-Host "`nContainer Status:" -ForegroundColor Cyan
    docker ps --filter "name=squig" --format "table {{.Names}}\t{{.Status}}"
    
    Write-Host "`nServices ready at http://localhost" -ForegroundColor Green
    exit 0
} else {
    Write-Host "   TIMEOUT: Services not ready after $maxAttempts attempts" -ForegroundColor Red
    Write-Host "`nChecking logs..." -ForegroundColor Yellow
    docker logs squig --tail 20
    exit 1
}
