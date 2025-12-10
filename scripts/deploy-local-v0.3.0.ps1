# Deploy Release v0.3.0 Locally

Write-Host "`n==================================================================" -ForegroundColor Cyan
Write-Host "RELEASE v0.3.0 - LOCAL DEPLOYMENT" -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan

# Stop any existing servers
Write-Host "`n[1/4] Stopping existing servers..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "*python*" } | Stop-Process -Force -ErrorAction SilentlyContinue
Get-Process uvicorn -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Start backend
Write-Host "`n[2/4] Starting backend on port 8000..." -ForegroundColor Yellow
$env:REQUIRE_DATABASE = "false"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd e:\repos\suigleague; .\.venv\Scripts\python.exe -m uvicorn herald.main:app --reload --port 8000"
Start-Sleep -Seconds 3

# Verify backend
Write-Host "[2/4] Verifying backend health..." -ForegroundColor Yellow
try {
    $health = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -ErrorAction Stop
    Write-Host "  Backend: OK" -ForegroundColor Green
} catch {
    Write-Host "  Backend: FAILED" -ForegroundColor Red
    exit 1
}

# Start frontend
Write-Host "`n[3/4] Starting frontend on port 3000..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd e:\repos\suigleague\frontend\public; python spa-server.py"
Start-Sleep -Seconds 2

# Verify frontend
Write-Host "[3/4] Verifying frontend..." -ForegroundColor Yellow
try {
    $frontend = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -ErrorAction Stop
    Write-Host "  Frontend: OK" -ForegroundColor Green
} catch {
    Write-Host "  Frontend: FAILED" -ForegroundColor Red
    exit 1
}

# Run tests
Write-Host "`n[4/4] Running API tests..." -ForegroundColor Yellow
Start-Sleep -Seconds 2
.\scripts\test-release-v0.3.0.ps1

Write-Host "`n==================================================================" -ForegroundColor Cyan
Write-Host "DEPLOYMENT COMPLETE" -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "`nBackend:  http://localhost:8000" -ForegroundColor Green
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Green
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Green
Write-Host "`nIMPORTANT: Open frontend in a NEW incognito/private window" -ForegroundColor Yellow
Write-Host "           to avoid browser cache issues" -ForegroundColor Yellow
Write-Host "`nReady for GUI testing!" -ForegroundColor Green
