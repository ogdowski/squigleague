# Test What's Actually Working
$ErrorActionPreference = "Continue"

Write-Host "Testing what is actually working..." -ForegroundColor Cyan
Write-Host ""

# 1. Check containers
Write-Host "1. Container Status:" -ForegroundColor Yellow
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# 2. Test main routes
Write-Host ""
Write-Host "2. Testing Routes:" -ForegroundColor Yellow

$routes = @(
    @{Name="Main Page"; Url="http://localhost"},
    @{Name="Squire Main"; Url="http://localhost/squire"},
    @{Name="Login Page"; Url="http://localhost/squire/login"},
    @{Name="Battle Plan Reference"; Url="http://localhost/squire/battleplan-reference"},
    @{Name="API Health"; Url="http://localhost/api/squire/health"},
    @{Name="Battle Plan List API"; Url="http://localhost/api/squire/battle-plan/list?game_system=age_of_sigmar"}
)

foreach ($route in $routes) {
    try {
        $response = Invoke-WebRequest -Uri $route.Url -Method Get -TimeoutSec 5
        $status = $response.StatusCode
        Write-Host "  [$status] $($route.Name): $($route.Url)" -ForegroundColor $(if ($status -eq 200) {"Green"} else {"Yellow"})
    }
    catch {
        $statusCode = $_.Exception.Response.StatusCode.value__
        if ($statusCode) {
            Write-Host "  [$statusCode] $($route.Name): $($route.Url)" -ForegroundColor Red
        }
        else {
            Write-Host "  [ERR] $($route.Name): $($route.Url) - $($_.Exception.Message)" -ForegroundColor Red
        }
    }
}

# 3. Test API specifically
Write-Host ""
Write-Host "3. Battle Plan API Test:" -ForegroundColor Yellow
try {
    $apiResponse = Invoke-RestMethod -Uri "http://localhost/api/squire/battle-plan/list?game_system=age_of_sigmar"
    Write-Host "  SUCCESS: API returns $($apiResponse.Count) battle plans" -ForegroundColor Green
}
catch {
    Write-Host "  FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "Summary:" -ForegroundColor Cyan
Write-Host "Check which URLs return 404 vs 200 above" -ForegroundColor White
