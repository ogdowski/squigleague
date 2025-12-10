# Kill existing python processes
Write-Host "Stopping existing Python processes..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

Write-Host "Starting backend server..." -ForegroundColor Cyan
.\.venv\Scripts\python.exe -m uvicorn herald.main:app --host 0.0.0.0 --port 8000 --reload
