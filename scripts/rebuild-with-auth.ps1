# rebuild-with-auth.ps1
# Rebuilds the entire system with authentication dependencies

$ErrorActionPreference = "Stop"

Write-Host "=== SquigLeague Rebuild with Authentication ===" -ForegroundColor Cyan
Write-Host ""

# Stop all containers
Write-Host "Stopping all containers..." -ForegroundColor Yellow
docker-compose down

if ($LASTEXITCODE -ne 0) {
    Write-Host "WARNING: docker-compose down had issues (this is usually OK)" -ForegroundColor Yellow
}

Write-Host ""

# Check if .env.local exists
if (-not (Test-Path ".env.local")) {
    Write-Host "Creating .env.local from .env.local.example..." -ForegroundColor Yellow
    Copy-Item ".env.local.example" ".env.local"
    
    Write-Host ""
    Write-Host "IMPORTANT: Please update .env.local with:" -ForegroundColor Yellow
    Write-Host "  1. JWT_SECRET - Generate a secure random string" -ForegroundColor Yellow
    Write-Host "  2. SMTP settings - For email verification" -ForegroundColor Yellow
    Write-Host ""
    
    $continue = Read-Host "Press Enter to continue after updating .env.local, or 'q' to quit"
    if ($continue -eq 'q') {
        exit 0
    }
}

# Build containers
Write-Host "Building containers with new dependencies..." -ForegroundColor Yellow
docker-compose build --no-cache

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Docker build failed" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Build complete!" -ForegroundColor Green
Write-Host ""

# Start containers
Write-Host "Starting containers..." -ForegroundColor Yellow
docker-compose up -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to start containers" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Containers started!" -ForegroundColor Green
Write-Host ""

# Wait for services to be ready
Write-Host "Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Setup database
Write-Host ""
Write-Host "Setting up database..." -ForegroundColor Cyan
& "$PSScriptRoot\setup-database.ps1"

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Database setup failed" -ForegroundColor Red
    exit 1
}

# Setup MailHog
Write-Host ""
Write-Host "Setting up MailHog..." -ForegroundColor Cyan
& "$PSScriptRoot\setup-mailhog.ps1"

Write-Host ""
Write-Host "=== Rebuild Complete ===" -ForegroundColor Green
Write-Host ""
Write-Host "Services:" -ForegroundColor Cyan
Write-Host "  Frontend: http://localhost:8080" -ForegroundColor White
Write-Host "  Backend API: http://localhost:8080/api" -ForegroundColor White
Write-Host "  MailHog UI: http://localhost:8025" -ForegroundColor White
Write-Host ""
Write-Host "New Routes:" -ForegroundColor Cyan
Write-Host "  Register: http://localhost:8080/squire/register" -ForegroundColor White
Write-Host "  Login: http://localhost:8080/squire/login" -ForegroundColor White
Write-Host "  Verify Email: http://localhost:8080/squire/verify-email?token=..." -ForegroundColor White
Write-Host ""
Write-Host "API Endpoints:" -ForegroundColor Cyan
Write-Host "  POST /api/squire/auth/register" -ForegroundColor White
Write-Host "  POST /api/squire/auth/login" -ForegroundColor White
Write-Host "  GET /api/squire/auth/verify-email?token=..." -ForegroundColor White
Write-Host "  POST /api/squire/auth/resend-verification" -ForegroundColor White
Write-Host "  GET /api/squire/auth/me" -ForegroundColor White
Write-Host ""

# Show logs
$showLogs = Read-Host "Show container logs? (y/n)"
if ($showLogs -eq 'y' -or $showLogs -eq 'Y') {
    docker-compose logs --tail=50
}
