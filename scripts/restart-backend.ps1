# Restart Backend Container to Apply Auth Changes
# Rebuilds and restarts the backend service

Write-Host "Restarting Backend Container..." -ForegroundColor Cyan
Write-Host "================================`n" -ForegroundColor Cyan

# Stop backend
Write-Host "Stopping squig container..." -ForegroundColor Yellow
docker stop squig

# Remove backend
Write-Host "Removing squig container..." -ForegroundColor Yellow
docker rm squig

# Rebuild and restart backend
Write-Host "Rebuilding and starting backend..." -ForegroundColor Yellow
docker-compose up -d --build squig

# Wait for health check
Write-Host "`nWaiting for backend to be healthy..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Check status
Write-Host "`nContainer Status:" -ForegroundColor Cyan
docker ps --filter "name=squig" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

Write-Host "`nBackend Logs (last 10 lines):" -ForegroundColor Cyan
docker logs squig --tail 10

Write-Host "`nBackend restart complete!" -ForegroundColor Green
