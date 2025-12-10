Write-Host "Starting frontend server..." -ForegroundColor Cyan
Set-Location frontend\public
.\..\..\.venv\Scripts\python.exe spa-server.py
