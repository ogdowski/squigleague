Write-Host "Starting backend..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\.venv\Scripts\python.exe -m uvicorn herald.main:app --host 127.0.0.1 --port 8000 --reload"

Start-Sleep -Seconds 5

Write-Host "Starting frontend..." -ForegroundColor Cyan  
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\frontend\public'; ..\..\..\.venv\Scripts\python.exe spa-server.py"

Start-Sleep -Seconds 3

Write-Host "`nTesting connections..." -ForegroundColor Yellow
try {
    $backend = Invoke-WebRequest -Uri "http://localhost:8000/api/squire/health" -UseBasicParsing -TimeoutSec 5
    Write-Host "Backend: OK ($($backend.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "Backend: FAILED" -ForegroundColor Red
}

try {
    $frontend = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 5
    Write-Host "Frontend: OK ($($frontend.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "Frontend: FAILED" -ForegroundColor Red
}
