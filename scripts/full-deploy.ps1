# full-deploy.ps1
# Complete deployment: rebuild, migrate, test

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  SquigLeague Full Deployment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Environment check
Write-Host "[1/7] Checking environment..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    if (Test-Path ".env.local") {
        Copy-Item ".env.local" ".env"
        Write-Host "  Created .env from .env.local" -ForegroundColor Green
    } else {
        Write-Host "  ERROR: No .env or .env.local file found" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "  .env file exists" -ForegroundColor Green
}

Write-Host ""

# Step 2: Stop containers
Write-Host "[2/7] Stopping containers..." -ForegroundColor Yellow
docker-compose down 2>&1 | Out-Null
Write-Host "  Containers stopped" -ForegroundColor Green

Write-Host ""

# Step 3: Build containers
Write-Host "[3/7] Building containers..." -ForegroundColor Yellow
docker-compose build --no-cache
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ERROR: Build failed" -ForegroundColor Red
    exit 1
}
Write-Host "  Build complete" -ForegroundColor Green

Write-Host ""

# Step 4: Start containers
Write-Host "[4/7] Starting containers..." -ForegroundColor Yellow
docker-compose up -d
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ERROR: Failed to start containers" -ForegroundColor Red
    exit 1
}
Write-Host "  Containers started" -ForegroundColor Green

Write-Host ""

# Step 5: Wait for services
Write-Host "[5/7] Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

$maxAttempts = 30
$attempt = 0
$ready = $false

while (-not $ready -and $attempt -lt $maxAttempts) {
    $attempt++
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/api/herald/health" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            $ready = $true
        }
    } catch {
        Write-Host "  Attempt $attempt/$maxAttempts..." -ForegroundColor Gray
        Start-Sleep -Seconds 1
    }
}

if (-not $ready) {
    Write-Host "  ERROR: Services did not become ready" -ForegroundColor Red
    exit 1
}
Write-Host "  Services ready" -ForegroundColor Green

Write-Host ""

# Step 6: Database migration
Write-Host "[6/7] Running database migrations..." -ForegroundColor Yellow
docker exec squig alembic upgrade head
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ERROR: Migration failed" -ForegroundColor Red
    exit 1
}
Write-Host "  Migrations complete" -ForegroundColor Green

Write-Host ""

# Step 7: Setup MailHog
Write-Host "[7/7] Setting up MailHog..." -ForegroundColor Yellow
$mailhogRunning = docker ps --filter "name=squig-mailhog" --format "{{.Names}}" 2>$null
if (-not $mailhogRunning) {
    docker run -d --name squig-mailhog --network squigleague_squig-network -p 1025:1025 -p 8025:8025 mailhog/mailhog 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  MailHog started" -ForegroundColor Green
    } else {
        Write-Host "  WARNING: MailHog failed to start (optional)" -ForegroundColor Yellow
    }
} else {
    Write-Host "  MailHog already running" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Deployment Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Services:" -ForegroundColor Cyan
Write-Host "  Frontend:    http://localhost:8080" -ForegroundColor White
Write-Host "  Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "  MailHog UI:  http://localhost:8025" -ForegroundColor White
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  .\scripts\check-services.ps1  - Verify all services" -ForegroundColor White
Write-Host "  .\scripts\test-auth-api.ps1   - Test auth endpoints" -ForegroundColor White
Write-Host ""
