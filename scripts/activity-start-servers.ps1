# Activity Script: Start v0.3.0 Development Servers
# Starts backend and frontend servers for manual testing
# Runs until Ctrl+C

param(
    [switch]$SkipCleanup
)

$ErrorActionPreference = "Stop"

Write-Host "`n=== Starting v0.3.0 Development Servers ===" -ForegroundColor Cyan

if (-not $SkipCleanup) {
    Write-Host "Cleaning up existing processes..." -ForegroundColor Yellow
    Get-Job | Stop-Job -ErrorAction SilentlyContinue
    Get-Job | Remove-Job -ErrorAction SilentlyContinue
    Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
}

Write-Host "Starting backend..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; `$env:DATABASE_URL='sqlite:///./squigleague.db'; .\.venv\Scripts\python.exe -m uvicorn herald.main:app --reload --port 8000"

Write-Host "Starting frontend..." -ForegroundColor Yellow  
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\frontend\public'; python spa-server.py"

Write-Host "`nWaiting for servers to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host "`n=== Servers Started ===" -ForegroundColor Green
Write-Host "`nBackend:  http://localhost:8000" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Cyan

Write-Host "`n=== Servers Running in Separate Windows ===" -ForegroundColor Yellow
Write-Host "Close the PowerShell windows to stop servers" -ForegroundColor Gray
