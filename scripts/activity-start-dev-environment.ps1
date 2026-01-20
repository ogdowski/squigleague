#!/usr/bin/env pwsh
# Activity Script: Start Development Environment
# Purpose: Start all services with proper dev configuration
# Usage: .\scripts\activity-start-dev-environment.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Activity: Start Development Environment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Stop existing containers
Write-Host "[1/5] Stopping existing containers..." -ForegroundColor Yellow
docker-compose down
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to stop containers" -ForegroundColor Red
    exit 1
}
Write-Host "Containers stopped" -ForegroundColor Green
Write-Host ""

# Step 2: Start with dev configuration
Write-Host "[2/5] Starting containers with dev configuration..." -ForegroundColor Yellow
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to start containers" -ForegroundColor Red
    exit 1
}
Write-Host "Containers started" -ForegroundColor Green
Write-Host ""

# Step 3: Wait for services
Write-Host "[3/5] Waiting for services to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 15
Write-Host "Wait complete" -ForegroundColor Green
Write-Host ""

# Step 4: Check container status
Write-Host "[4/5] Checking container status..." -ForegroundColor Yellow
docker ps --filter "name=squig" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
Write-Host ""

# Step 5: Test API health
Write-Host "[5/5] Testing API health..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri 'http://localhost/api/health' -UseBasicParsing -TimeoutSec 5
    Write-Host "API is healthy" -ForegroundColor Green
    Write-Host $response.Content
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "Development environment is running" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Access the application at http://localhost" -ForegroundColor Cyan
    Write-Host ""
    exit 0
} catch {
    Write-Host "API health check failed" -ForegroundColor Red
    Write-Host $_.Exception.Message
    Write-Host ""
    Write-Host "Backend logs:" -ForegroundColor Yellow
    docker logs squig-backend --tail 30
    exit 1
}
