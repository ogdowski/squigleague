#!/usr/bin/env pwsh
# Validate that frontend build has correct API_URL value
# CRITICAL: Run after EVERY frontend Docker rebuild

$ErrorActionPreference = "Stop"

Write-Host "`n=== Frontend Build Validation ===" -ForegroundColor Cyan

# Check if frontend container is running
$container = docker ps --filter "name=squig-frontend" --format "{{.Names}}" 2>$null
if (-not $container) {
    Write-Host "ERROR: squig-frontend container not running" -ForegroundColor Red
    exit 1
}

Write-Host "Extracting API_URL from built JavaScript..." -ForegroundColor Yellow

# Extract all API_URL or f="/api" patterns from built JS files
$jsContent = docker exec squig-frontend sh -c "cat /usr/share/nginx/html/assets/*.js" 2>$null

if (-not $jsContent) {
    Write-Host "ERROR: Could not read JavaScript files from container" -ForegroundColor Red
    exit 1
}

# Search for various API_URL patterns in minified code
# Pattern 1: const API_URL="..."
# Pattern 2: f="/api" or similar single-letter vars
# Pattern 3: API_URL:"/api"
$apiUrlPatterns = @(
    'API_URL\s*[:=]\s*"[^"]*"',
    '[a-z]="/api"',
    'localhost:8000'
)

$findings = @()
foreach ($pattern in $apiUrlPatterns) {
    $matches = [regex]::Matches($jsContent, $pattern)
    if ($matches.Count -gt 0) {
        $findings += $matches.Value
    }
}

if ($findings.Count -eq 0) {
    Write-Host "WARNING: Could not find API_URL patterns" -ForegroundColor Yellow
    Write-Host "Checking for any /api references..." -ForegroundColor Yellow
    
    if ($jsContent -match '/api') {
        Write-Host "Found /api string in JavaScript (likely correct)" -ForegroundColor Green
        exit 0
    } else {
        Write-Host "ERROR: No /api found in built JavaScript" -ForegroundColor Red
        exit 1
    }
}

Write-Host "`nFound API URL patterns:" -ForegroundColor Yellow
$findings | Select-Object -Unique | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }

# Check for localhost:8000 (FAILURE)
$hasLocalhost = $findings | Where-Object { $_ -match 'localhost:8000' }
if ($hasLocalhost) {
    Write-Host "`nFAILURE: Frontend built with hardcoded localhost:8000" -ForegroundColor Red
    Write-Host "Found: $hasLocalhost" -ForegroundColor Red
    Write-Host "VITE_API_URL was NOT applied during build" -ForegroundColor Red
    Write-Host "`nRequired fix:" -ForegroundColor Yellow
    Write-Host "  1. Verify Dockerfile has: RUN VITE_API_URL=`$VITE_API_URL npm run build" -ForegroundColor Yellow
    Write-Host "  2. Rebuild: docker-compose build --no-cache --build-arg VITE_API_URL=/api frontend" -ForegroundColor Yellow
    exit 1
}

# Check for /api (SUCCESS)
$hasApi = $findings | Where-Object { $_ -match '/api' }
if ($hasApi) {
    Write-Host "`nSUCCESS: Frontend built with /api routing" -ForegroundColor Green
    Write-Host "Vite environment variable correctly applied" -ForegroundColor Green
    exit 0
}

# Unknown state
Write-Host "`nWARNING: API_URL found but not /api or localhost:8000" -ForegroundColor Yellow
Write-Host "Manual verification required" -ForegroundColor Yellow
exit 1
