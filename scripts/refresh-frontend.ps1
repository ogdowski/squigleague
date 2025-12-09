# Force frontend refresh by killing server and clearing browser cache

Write-Host "Killing frontend server..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "*python*" } | Stop-Process -Force

Write-Host "Waiting 2 seconds..." -ForegroundColor Yellow
Start-Sleep -Seconds 2

Write-Host "Starting frontend server on port 3000..." -ForegroundColor Green
cd e:\repos\suigleague\frontend\public
Start-Process python -ArgumentList "-m","http.server","3000" -PassThru

Write-Host "`nFrontend restarted!" -ForegroundColor Green
Write-Host "IMPORTANT: In your browser, do a HARD REFRESH:" -ForegroundColor Cyan
Write-Host "  - Chrome/Edge: Ctrl+Shift+R or Ctrl+F5" -ForegroundColor Yellow
Write-Host "  - Firefox: Ctrl+Shift+R" -ForegroundColor Yellow
Write-Host "`nOr open in INCOGNITO/PRIVATE window to bypass cache" -ForegroundColor Cyan
Write-Host "`nURL: http://localhost:3000" -ForegroundColor Green
