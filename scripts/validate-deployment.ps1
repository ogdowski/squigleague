# Deployment Validation
Write-Host "`n=== DEPLOYMENT VALIDATION ===" -ForegroundColor Cyan
$allPassed = $true

Write-Host "`n1. Containers:" -ForegroundColor Yellow
docker ps --filter "name=squig" --format "table {{.Names}}\t{{.Status}}"

Write-Host "`n2. Backend Health:" -ForegroundColor Yellow
try {
    $h = Invoke-WebRequest -Uri "http://localhost/health" -UseBasicParsing
    Write-Host "  [OK] HTTP $($h.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "  [FAIL] $($_.Exception.Message)" -ForegroundColor Red
    $allPassed = $false
}

Write-Host "`n3. Auth Routes:" -ForegroundColor Yellow
try {
    $body = @{email="test$(Get-Random)@x.com";username="u$(Get-Random)";password="Pass123!"} | ConvertTo-Json
    $a = Invoke-WebRequest -Uri "http://localhost/auth/register" -Method POST -Body $body -ContentType "application/json" -UseBasicParsing
    Write-Host "  [OK] HTTP $($a.StatusCode)" -ForegroundColor Green
} catch {
    if ($_.Exception.Message -like "*405*") {
        Write-Host "  [FAIL] 405 - nginx missing /auth/ proxy" -ForegroundColor Red
        $allPassed = $false
    } else {
        Write-Host "  [WARN] $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

Write-Host "`n4. Frontend:" -ForegroundColor Yellow
try {
    $f = Invoke-WebRequest -Uri "http://localhost/" -UseBasicParsing
    Write-Host "  [OK] HTTP $($f.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "  [FAIL] $($_.Exception.Message)" -ForegroundColor Red
    $allPassed = $false
}

if ($allPassed) {
    Write-Host "`n[PASS] Deployment validated`n" -ForegroundColor Green
    exit 0
} else {
    Write-Host "`n[FAIL] Fix errors above`n" -ForegroundColor Red
    exit 1
}
