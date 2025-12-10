$env:REQUIRE_DATABASE = "false"
Write-Host "Starting backend with REQUIRE_DATABASE=false..." -ForegroundColor Cyan
.\.venv\Scripts\python.exe -m uvicorn herald.main:app --host 127.0.0.1 --port 8000 --reload
