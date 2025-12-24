# test-auth-api.ps1
# Quick API test for authentication endpoints

$ErrorActionPreference = "Stop"

Write-Host "=== Testing Authentication API ===" -ForegroundColor Cyan
Write-Host ""

$baseUrl = "http://localhost:8000/api/squire"

# Test health check first
Write-Host "Testing backend health..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/api/herald/health" -Method GET
    Write-Host "  Backend is healthy" -ForegroundColor Green
} catch {
    Write-Host "  ERROR: Backend is not responding" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Test registration with simple data
Write-Host "Testing registration endpoint..." -ForegroundColor Yellow
$timestamp = Get-Date -Format "yyyyMMddHHmmss"
$body = @{
    username = "testuser$timestamp"
    email = "test$timestamp@example.com"
    password = "TestPassword123!"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/auth/register" -Method POST -Body $body -ContentType "application/json"
    Write-Host "  SUCCESS: Registration works!" -ForegroundColor Green
    Write-Host "  Message: $($response.message)" -ForegroundColor Gray
} catch {
    Write-Host "  FAILED: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Response details:" -ForegroundColor Yellow
    $_.Exception | Format-List *
    exit 1
}

Write-Host ""
Write-Host "=== Authentication API is working ===" -ForegroundColor Green
