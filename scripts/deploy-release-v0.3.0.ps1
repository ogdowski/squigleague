# Release Deployment Script - v0.3.0
# Builds and starts Docker containers for testing/deployment

param(
    [switch]$Build,
    [switch]$Rebuild,
    [switch]$Logs,
    [switch]$Stop
)

$ErrorActionPreference = "Stop"

Write-Host "`n=== Squig League v0.3.0 Release Deployment ===" -ForegroundColor Cyan

# Check prerequisites
Write-Host "`nChecking prerequisites..." -ForegroundColor Yellow

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Docker not found. Please install Docker Desktop." -ForegroundColor Red
    Write-Host "Download: https://www.docker.com/products/docker-desktop/" -ForegroundColor Yellow
    exit 1
}

if (-not (Get-Command docker-compose -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: docker-compose not found." -ForegroundColor Red
    exit 1
}

# Ensure .env.local exists
if (-not (Test-Path ".env.local")) {
    Write-Host "Creating .env.local with default values..." -ForegroundColor Yellow
    @"
DB_PASSWORD=dev_password_change_in_production
HERALD_ADMIN_KEY=dev_admin_key_change_in_production
SQUIG_VERSION=0.3.0
"@ | Out-File -FilePath ".env.local" -Encoding UTF8
    Write-Host "✓ Created .env.local" -ForegroundColor Green
}

# Stop containers if requested
if ($Stop) {
    Write-Host "`nStopping containers..." -ForegroundColor Yellow
    docker-compose down
    Write-Host "✓ Containers stopped" -ForegroundColor Green
    exit 0
}

# Build or rebuild
if ($Rebuild) {
    Write-Host "`nRebuilding containers (no cache)..." -ForegroundColor Yellow
    docker-compose build --no-cache
} elseif ($Build) {
    Write-Host "`nBuilding containers..." -ForegroundColor Yellow
    docker-compose build
}

# Start containers
Write-Host "`nStarting containers..." -ForegroundColor Yellow
if ($Logs) {
    docker-compose up
} else {
    docker-compose up -d
    
    Write-Host "`n=== Deployment Complete ===" -ForegroundColor Green
    Write-Host "`nServices:" -ForegroundColor Cyan
    Write-Host "  Application:  http://localhost/" -ForegroundColor White
    Write-Host "  Gallery:      http://localhost/#/squire/battleplans" -ForegroundColor White
    Write-Host "  Matchup:      http://localhost/#/squire/matchup" -ForegroundColor White
    Write-Host "  API Docs:     http://localhost/docs" -ForegroundColor White
    
    Write-Host "`nContainer Status:" -ForegroundColor Cyan
    docker ps --filter "name=squig" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    
    Write-Host "`nUseful Commands:" -ForegroundColor Yellow
    Write-Host "  View logs:    docker-compose logs -f" -ForegroundColor White
    Write-Host "  Stop:         docker-compose down" -ForegroundColor White
    Write-Host "  Restart:      docker-compose restart" -ForegroundColor White
    Write-Host "  Shell access: docker exec -it squig /bin/bash" -ForegroundColor White
    
    Write-Host "`nWaiting for services to be ready..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
    
    # Health check
    try {
        $response = Invoke-WebRequest -Uri "http://localhost/api/herald/health" -UseBasicParsing -TimeoutSec 10
        if ($response.StatusCode -eq 200) {
            Write-Host "✓ Backend healthy" -ForegroundColor Green
        }
    } catch {
        Write-Host "⚠ Backend not responding yet (may need more time to start)" -ForegroundColor Yellow
    }
}
