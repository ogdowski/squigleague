# Verify Frontend Files Script
$ErrorActionPreference = "Stop"

Write-Host "Verifying frontend files..." -ForegroundColor Cyan
Write-Host ""

# Check the actual file in the nginx container
Write-Host "Checking battleplan-reference.js in nginx container..." -ForegroundColor Yellow
$hasNewCode = docker exec squig-nginx grep -c "Use dedicated list endpoint" /usr/share/nginx/html/modules/squire/battleplan-reference.js 2>$null

if ($hasNewCode -gt 0) {
    Write-Host "OK: Frontend container has updated code" -ForegroundColor Green
}
else {
    Write-Host "ERROR: Frontend container still has old code" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Checking for old probabilistic code..." -ForegroundColor Yellow
$hasOldCode = docker exec squig-nginx grep -c "const maxAttempts = 50" /usr/share/nginx/html/modules/squire/battleplan-reference.js 2>$null

if ($hasOldCode -gt 0) {
    Write-Host "WARNING: File still contains old code snippet" -ForegroundColor Red
    Write-Host "The frontend container needs to be rebuilt" -ForegroundColor Yellow
}
else {
    Write-Host "OK: Old code has been removed" -ForegroundColor Green
}

Write-Host ""
Write-Host "Testing API directly..." -ForegroundColor Yellow
$apiResult = Invoke-RestMethod -Uri "http://localhost/api/squire/battle-plan/list?game_system=age_of_sigmar"
Write-Host "API returns: $($apiResult.Count) battle plans" -ForegroundColor $(if ($apiResult.Count -eq 12) { "Green" } else { "Red" })

Write-Host ""
Write-Host "Summary:" -ForegroundColor Cyan
if ($hasNewCode -gt 0 -and $hasOldCode -eq 0 -and $apiResult.Count -eq 12) {
    Write-Host "Everything is correct on the server side" -ForegroundColor Green
    Write-Host "If you see 8 plans in browser, it is browser cache" -ForegroundColor Yellow
    Write-Host "Solution: Press Ctrl+Shift+Delete, clear cache, then Ctrl+F5" -ForegroundColor Cyan
}
else {
    Write-Host "Server-side issue detected - frontend container needs rebuild" -ForegroundColor Red
}
