# Check Container Code
$ErrorActionPreference = "Stop"

Write-Host "Checking what code is actually running in containers..." -ForegroundColor Cyan
Write-Host ""

# Check backend route
Write-Host "1. Checking backend /battle-plan/list endpoint code..." -ForegroundColor Yellow
$routeCode = docker exec squig grep -A 30 "@router.get(""/battle-plan/list"")" /app/squire/routes.py
if ($routeCode) {
    Write-Host "   Endpoint exists in container" -ForegroundColor Green
}
else {
    Write-Host "   ERROR: Endpoint NOT found in container!" -ForegroundColor Red
    exit 1
}

# Check if it's actually being called
Write-Host ""
Write-Host "2. Making API call and checking response structure..." -ForegroundColor Yellow
$response = Invoke-WebRequest -Uri "http://localhost/api/squire/battle-plan/list?game_system=age_of_sigmar"
$json = $response.Content | ConvertFrom-Json
Write-Host "   HTTP Status: $($response.StatusCode)" -ForegroundColor White
Write-Host "   Response is array: $($json -is [Array])" -ForegroundColor White
Write-Host "   Array length: $($json.Count)" -ForegroundColor White

# Check frontend code
Write-Host ""
Write-Host "3. Checking frontend container code..." -ForegroundColor Yellow
$frontendHasNew = docker exec squig-frontend grep -c "Use dedicated list endpoint" /usr/share/nginx/html/modules/squire/battleplan-reference.js
Write-Host "   Frontend has new code: $(if ($frontendHasNew -gt 0) { 'YES' } else { 'NO' })" -ForegroundColor $(if ($frontendHasNew -gt 0) { 'Green' } else { 'Red' })

Write-Host ""
Write-Host "Summary:" -ForegroundColor Cyan
Write-Host "- Backend returns: $($json.Count) battle plans" -ForegroundColor White
Write-Host "- If browser shows different number, it is still using cached JS" -ForegroundColor Yellow
Write-Host "- Hard refresh required: Ctrl+Shift+R or Ctrl+F5" -ForegroundColor Yellow
