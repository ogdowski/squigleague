#!/usr/bin/env pwsh
# Start development environment with proper configuration

Write-Host "Starting development environment..." -ForegroundColor Cyan

# Stop any existing containers
Write-Host "Stopping existing containers..." -ForegroundColor Yellow
docker-compose down

# Start with dev configuration
Write-Host "Starting containers with dev configuration..." -ForegroundColor Yellow
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Wait for services to be healthy
Write-Host "Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check health
Write-Host "`nChecking service health..." -ForegroundColor Cyan
docker ps --filter "name=squig" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

Write-Host "`nChecking backend logs..." -ForegroundColor Cyan
docker logs squig-backend --tail 10

Write-Host "`nTesting API endpoint..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri 'http://localhost/api/squire/health' -UseBasicParsing -TimeoutSec 5
    Write-Host "✓ API is responding: $($response.StatusCode)" -ForegroundColor Green
    Write-Host $response.Content
} catch {
    Write-Host "✗ API is not responding: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "`nBackend error logs:" -ForegroundColor Red
    docker logs squig-backend --tail 30
}

Write-Host "`nDevelopment environment started. Access at http://localhost" -ForegroundColor Green
