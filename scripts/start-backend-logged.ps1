$ErrorActionPreference = "Continue"

Write-Host "Killing existing Python processes..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2

Write-Host "Starting backend with REQUIRE_DATABASE=false..." -ForegroundColor Cyan

# Start backend in background with environment variable
$env:REQUIRE_DATABASE = "false"

Start-Job -ScriptBlock {
    param($path)
    Set-Location $path
    $env:REQUIRE_DATABASE = "false"
    & ".\.venv\Scripts\python.exe" -m uvicorn herald.main:app --host 127.0.0.1 --port 8000 --reload 2>&1
} -ArgumentList $PWD -Name "BackendServer" | Out-Null

Write-Host "Backend starting in background job..." -ForegroundColor Green

# Wait for startup
Write-Host "Waiting 10 seconds for initialization..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Test if server is responding
Write-Host "`n=== Testing HTTP Response ===" -ForegroundColor Yellow

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/squire/health" -UseBasicParsing -TimeoutSec 5
    Write-Host "SUCCESS: Backend is responding" -ForegroundColor Green
    Write-Host "Status: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "Content: $($response.Content)" -ForegroundColor White
} catch {
    Write-Host "FAILED: Backend not responding" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    
    # Show job output
    Write-Host "`n=== Job Output ===" -ForegroundColor Yellow
    Receive-Job -Name "BackendServer"
}

Write-Host "`n=== Complete ===" -ForegroundColor Cyan
Write-Host "Check job output with: Receive-Job -Name BackendServer -Keep" -ForegroundColor Gray
