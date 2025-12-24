# Clear Frontend Cache Script
$ErrorActionPreference = "Stop"

Write-Host "Clearing frontend cache..." -ForegroundColor Cyan

# Restart nginx to clear any server-side cache
Write-Host "Restarting nginx container..." -ForegroundColor Yellow
docker restart squig-nginx | Out-Null

Start-Sleep -Seconds 3

# Check nginx is healthy
$status = docker ps --filter "name=squig-nginx" --format "{{.Status}}"
if ($status -match "Up") {
    Write-Host "Nginx restarted successfully" -ForegroundColor Green
}
else {
    Write-Host "Nginx failed to restart" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Frontend cache cleared!" -ForegroundColor Green
Write-Host ""
Write-Host "Next step: Press Ctrl+F5 in your browser to hard refresh" -ForegroundColor Cyan
Write-Host "Navigate to: http://localhost/squire/battleplan-reference" -ForegroundColor White
Write-Host "Select Age of Sigmar - should show 12 battle plans" -ForegroundColor White
