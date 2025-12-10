Start-Sleep -Seconds 3
Write-Host "Testing health..." -ForegroundColor Cyan
Invoke-RestMethod -Uri "http://localhost:8000/health" | ConvertTo-Json
Write-Host "`nTesting Squire health..." -ForegroundColor Cyan
Invoke-RestMethod -Uri "http://localhost:8000/api/squire/health" | ConvertTo-Json
