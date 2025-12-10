Write-Host "Testing backend startup and capturing errors..." -ForegroundColor Cyan

$output = .\.venv\Scripts\python.exe -m uvicorn herald.main:app --host 127.0.0.1 --port 8000 2>&1

Write-Host "`nOutput:" -ForegroundColor Yellow
$output | ForEach-Object { Write-Host $_ }
