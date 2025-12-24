# check-services.ps1
# Verify all services are running and accessible

$ErrorActionPreference = "Continue"

Write-Host "=== SquigLeague Services Check ===" -ForegroundColor Cyan
Write-Host ""

# Check Docker containers
Write-Host "Docker Containers:" -ForegroundColor Yellow
$containers = @("squig-postgres", "squig", "squig-frontend", "squig-nginx", "squig-mailhog")
foreach ($container in $containers) {
    $status = docker ps --filter "name=$container" --format '{{.Status}}' 2>$null
    if ($status) {
        Write-Host "  ✓ $container : $status" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $container : Not running" -ForegroundColor Red
    }
}

Write-Host ""

# Check service endpoints
Write-Host "Service Endpoints:" -ForegroundColor Yellow

# Backend API
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/herald/health" -UseBasicParsing -TimeoutSec 5
    Write-Host "  ✓ Backend API (8000) : $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Backend API (8000) : Not accessible" -ForegroundColor Red
}

# Frontend
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8080/" -UseBasicParsing -TimeoutSec 5
    Write-Host "  ✓ Frontend (8080) : $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Frontend (8080) : Not accessible" -ForegroundColor Red
}

# MailHog
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8025/" -UseBasicParsing -TimeoutSec 5
    Write-Host "  ✓ MailHog UI (8025) : $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "  ✗ MailHog UI (8025) : Not accessible" -ForegroundColor Red
}

Write-Host ""

# Check database
Write-Host "Database:" -ForegroundColor Yellow
$dbCheck = docker exec squig-postgres pg_isready -U squig 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ PostgreSQL : Ready" -ForegroundColor Green
} else {
    Write-Host "  ✗ PostgreSQL : Not ready" -ForegroundColor Red
}

# Check migrations
Write-Host ""
Write-Host "Database Migrations:" -ForegroundColor Yellow
$migration = docker exec squig alembic current 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Migrations : Applied" -ForegroundColor Green
    Write-Host "    $migration" -ForegroundColor Gray
} else {
    Write-Host "  ✗ Migrations : Not applied" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== Services Check Complete ===" -ForegroundColor Green
