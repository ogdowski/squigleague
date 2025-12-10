Write-Host "Starting backend server..." -ForegroundColor Cyan
.\.venv\Scripts\python.exe -m uvicorn herald.main:app --host 0.0.0.0 --port 8000 --reload
