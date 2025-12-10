Write-Host "Opening test page..." -ForegroundColor Yellow
Start-Process "http://localhost:3000/test-error-handling.html"
Start-Sleep -Seconds 1
Write-Host "Test page opened - check browser for results" -ForegroundColor Green
