# setup-database.ps1
# Sets up the database with Alembic migrations

$ErrorActionPreference = "Stop"

Write-Host "=== SquigLeague Database Setup ===" -ForegroundColor Cyan
Write-Host ""

# Ensure containers are running
Write-Host "Checking if containers are running..." -ForegroundColor Yellow
$postgresRunning = docker ps --filter "name=squig-postgres" --format "{{.Names}}" 2>$null
$backendRunning = docker ps --filter "name=squig" --format "{{.Names}}" 2>$null | Where-Object { $_ -eq "squig" }

if (-not $postgresRunning) {
    Write-Host "ERROR: PostgreSQL container is not running" -ForegroundColor Red
    Write-Host "Run 'docker-compose up -d' first" -ForegroundColor Yellow
    exit 1
}

if (-not $backendRunning) {
    Write-Host "WARNING: Backend container is not running" -ForegroundColor Yellow
    Write-Host "Starting backend container..." -ForegroundColor Yellow
    docker-compose up -d squig
    Start-Sleep -Seconds 5
}

# Wait for PostgreSQL to be ready
Write-Host "Waiting for PostgreSQL to be ready..." -ForegroundColor Yellow
$maxAttempts = 30
$attempt = 0
$ready = $false

while (-not $ready -and $attempt -lt $maxAttempts) {
    $attempt++
    $result = docker exec squig-postgres pg_isready -U squig 2>$null
    if ($LASTEXITCODE -eq 0) {
        $ready = $true
    } else {
        Write-Host "  Attempt $attempt/$maxAttempts - waiting..." -ForegroundColor Gray
        Start-Sleep -Seconds 1
    }
}

if (-not $ready) {
    Write-Host "ERROR: PostgreSQL did not become ready in time" -ForegroundColor Red
    exit 1
}

Write-Host "PostgreSQL is ready" -ForegroundColor Green
Write-Host ""

# Run Alembic migrations
Write-Host "Running database migrations..." -ForegroundColor Yellow
docker exec squig alembic upgrade head

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Database migration failed" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Database setup complete!" -ForegroundColor Green
Write-Host ""

# Show database status
Write-Host "Database tables:" -ForegroundColor Cyan
docker exec squig-postgres psql -U squig -d squigleague -c "\dt"

Write-Host ""
Write-Host "=== Setup Complete ===" -ForegroundColor Green
