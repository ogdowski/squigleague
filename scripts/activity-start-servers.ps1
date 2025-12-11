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

Write-Host "Starting backend (Job)..." -ForegroundColor Yellow
$backend = Start-Job -ScriptBlock {
    Set-Location $args[0]
    $env:REQUIRE_DATABASE = "false"
    & ".\.venv\Scripts\python.exe" -m uvicorn herald.main:app --port 8000
} -ArgumentList $PWD.Path

Write-Host "Starting frontend (Job)..." -ForegroundColor Yellow  
$frontend = Start-Job -ScriptBlock {
    Set-Location "$($args[0])\frontend\public"
    & python spa-server.py
} -ArgumentList $PWD.Path

Write-Host "`nWaiting for servers to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host "`n=== Servers Started ===" -ForegroundColor Green
Write-Host "Backend Job:  $($backend.Id)" -ForegroundColor White
Write-Host "Frontend Job: $($frontend.Id)" -ForegroundColor White
Write-Host "`nBackend:  http://localhost:8000" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Cyan

Write-Host "`n=== Next Steps ===" -ForegroundColor Yellow
Write-Host "Run tests: .\scripts\test-error-extraction.ps1" -ForegroundColor White
Write-Host "Open app:  start http://localhost:3000" -ForegroundColor White
Write-Host "`nPress Ctrl+C to stop servers" -ForegroundColor Gray

try {
    while ($true) {
        Start-Sleep -Seconds 10
        
        $backendState = (Get-Job -Id $backend.Id -ErrorAction SilentlyContinue).State
        $frontendState = (Get-Job -Id $frontend.Id -ErrorAction SilentlyContinue).State
        
        if ($backendState -ne 'Running') {
            Write-Host "`nBackend job stopped!" -ForegroundColor Red
            Receive-Job -Id $backend.Id | Select-Object -Last 20 | ForEach-Object { Write-Host $_ }
            break
        }
        
        if ($frontendState -ne 'Running') {
            Write-Host "`nFrontend job stopped!" -ForegroundColor Red
            Receive-Job -Id $frontend.Id | Select-Object -Last 20 | ForEach-Object { Write-Host $_ }
            break
        }
    }
} finally {
    Write-Host "`nStopping servers..." -ForegroundColor Yellow
    Stop-Job $backend, $frontend -ErrorAction SilentlyContinue
    Remove-Job $backend, $frontend -ErrorAction SilentlyContinue
}
