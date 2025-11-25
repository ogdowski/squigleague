# Check Backend Routes
# Diagnoses why matchup routes aren't working

Write-Host "`nChecking backend routes..." -ForegroundColor Cyan
Write-Host ""

# Test if backend is running
Write-Host "[1] Backend container status..." -ForegroundColor Yellow
docker ps --filter "name=squig" --format "table {{.Names}}\t{{.Status}}"
Write-Host ""

# Check if matchup.py exists in container
Write-Host "[2] Checking matchup.py in container..." -ForegroundColor Yellow
docker exec squig test -f /app/squire/matchup.py
if ($LASTEXITCODE -eq 0) {
    Write-Host "    matchup.py EXISTS" -ForegroundColor Green
} else {
    Write-Host "    matchup.py MISSING" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Try to import matchup module
Write-Host "[3] Testing matchup module import..." -ForegroundColor Yellow
docker exec squig python -c "from squire import matchup; print('SUCCESS')" 2>&1 | Out-String
Write-Host ""

# Try to import routes
Write-Host "[4] Testing routes import..." -ForegroundColor Yellow
docker exec squig python -c "from squire import routes; print('SUCCESS')" 2>&1 | Out-String
Write-Host ""

# Check what routes are registered
Write-Host "[5] Checking registered routes..." -ForegroundColor Yellow
docker exec squig python -c "from squire.routes import router; routes = [(r.path, r.methods) for r in router.routes]; import json; print(json.dumps(routes, indent=2))" 2>&1 | Out-String
Write-Host ""

# Check main.py includes squire router
Write-Host "[6] Checking main.py router inclusion..." -ForegroundColor Yellow
docker exec squig grep -n "squire_router" /app/herald/main.py
Write-Host ""

Write-Host "Diagnosis complete" -ForegroundColor Cyan
