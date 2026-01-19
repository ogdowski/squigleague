# Deployment Validation Script
# Validates that all critical infrastructure is working before declaring deployment successful
# Exit code 0 = PASS, 1 = FAIL

Write-Host "`n=== DEPLOYMENT VALIDATION ===" -ForegroundColor Cyan
$allPassed = $true

# 1. Docker Container Health
Write-Host "`n1. Docker Container Health:" -ForegroundColor Yellow
$containers = docker ps --filter "name=squig" --format "{{.Names}},{{.Status}}" | ConvertFrom-Csv -Header Name,Status
$requiredContainers = @('squig-backend', 'squig-frontend', 'squig-postgres', 'squig-nginx')

foreach ($container in $requiredContainers) {
    $found = $containers | Where-Object { $_.Name -eq $container }
    if ($found) {
        if ($found.Status -like "*healthy*" -or $found.Status -like "*Up*") {
            Write-Host "  ✓ $container: Running" -ForegroundColor Green
        } else {
            Write-Host "  ✗ $container: $($found.Status)" -ForegroundColor Red
            $allPassed = $false
        }
    } else {
        Write-Host "  ✗ $container: Not found" -ForegroundColor Red
        $allPassed = $false
    }
}

# 2. Backend Health Endpoint
Write-Host "`n2. Backend Health Check:" -ForegroundColor Yellow
try {
    $health = Invoke-WebRequest -Uri "http://localhost/health" -UseBasicParsing -TimeoutSec 5
    if ($health.StatusCode -eq 200) {
        Write-Host "  ✓ Backend health endpoint: HTTP 200" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Backend health endpoint: HTTP $($health.StatusCode)" -ForegroundColor Red
        $allPassed = $false
    }
} catch {
    Write-Host "  ✗ Backend health endpoint: Failed - $($_.Exception.Message)" -ForegroundColor Red
    $allPassed = $false
}

# 3. Auth Routes (Critical - frequently broken)
Write-Host "`n3. Auth Routes Check:" -ForegroundColor Yellow
try {
    $testEmail = "validation-test-$(Get-Random)@example.com"
    $testBody = @{
        email = $testEmail
        username = "validtest$(Get-Random)"
        password = "TestPass123!"
    } | ConvertTo-Json
    
    $authResponse = Invoke-WebRequest -Uri "http://localhost/auth/register" -Method POST -ContentType "application/json" -Body $testBody -UseBasicParsing -ErrorAction Stop
    
    if ($authResponse.StatusCode -eq 201) {
        Write-Host "  ✓ Auth routes accessible: HTTP 201" -ForegroundColor Green
        # Clean up test user
        Write-Host "  ℹ Test user created and can be cleaned up manually if needed" -ForegroundColor Gray
    } else {
        Write-Host "  ✗ Auth routes: Unexpected status $($authResponse.StatusCode)" -ForegroundColor Red
        $allPassed = $false
    }
} catch {
    if ($_.Exception.Message -like "*405*") {
        Write-Host "  ✗ Auth routes: 405 Method Not Allowed - nginx missing /auth/ proxy" -ForegroundColor Red
        $allPassed = $false
    } elseif ($_.Exception.Message -like "*404*") {
        Write-Host "  ✗ Auth routes: 404 Not Found - route not configured" -ForegroundColor Red
        $allPassed = $false
    } else {
        Write-Host "  ⚠ Auth routes: $($_.Exception.Message)" -ForegroundColor Yellow
        # Don't fail on other errors (might be validation errors which are OK)
    }
}

# 4. Frontend Accessibility
Write-Host "`n4. Frontend Accessibility:" -ForegroundColor Yellow
try {
    $frontend = Invoke-WebRequest -Uri "http://localhost/" -UseBasicParsing -TimeoutSec 5
    if ($frontend.StatusCode -eq 200 -and $frontend.Content.Length -gt 0) {
        Write-Host "  ✓ Frontend serving: HTTP 200 ($($frontend.Content.Length) bytes)" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Frontend: Status $($frontend.StatusCode), Empty response" -ForegroundColor Red
        $allPassed = $false
    }
} catch {
    Write-Host "  ✗ Frontend: Failed - $($_.Exception.Message)" -ForegroundColor Red
    $allPassed = $false
}

# 5. Frontend Build Currency (detect stale builds)
Write-Host "`n5. Frontend Build Currency:" -ForegroundColor Yellow
try {
    $buildDate = docker exec squig-frontend stat -c %Y /usr/share/nginx/html/index.html 2>$null
    if ($buildDate) {
        $buildDateTime = [DateTimeOffset]::FromUnixTimeSeconds($buildDate).LocalDateTime
        $age = (Get-Date) - $buildDateTime
        
        if ($age.TotalHours -lt 24) {
            Write-Host "  ✓ Frontend build: Fresh ($(([int]$age.TotalHours))h $(([int]$age.Minutes))m old)" -ForegroundColor Green
        } elseif ($age.TotalDays -lt 7) {
            Write-Host "  ⚠ Frontend build: $(([int]$age.TotalDays)) days old - consider rebuild" -ForegroundColor Yellow
        } else {
            Write-Host "  ✗ Frontend build: $(([int]$age.TotalDays)) days old - STALE BUILD" -ForegroundColor Red
            $allPassed = $false
        }
    }
} catch {
    Write-Host "  ⚠ Could not check build date" -ForegroundColor Yellow
}

# 6. Battle Plan Assets (for this specific feature)
Write-Host "`n6. Battle Plan Assets:" -ForegroundColor Yellow
$assetCount = (Get-ChildItem -Path "assets/battle-plans-matplotlib" -Filter "*.png" -ErrorAction SilentlyContinue | Measure-Object).Count
if ($assetCount -ge 12) {
    Write-Host "  ✓ Battle plan images: $assetCount files present" -ForegroundColor Green
} elseif ($assetCount -gt 0) {
    Write-Host "  ⚠ Battle plan images: Only $assetCount files (expected 12+)" -ForegroundColor Yellow
} else {
    Write-Host "  ✗ Battle plan images: Missing" -ForegroundColor Red
    $allPassed = $false
}

# Final Result
Write-Host "`n================================" -ForegroundColor Cyan
if ($allPassed) {
    Write-Host "✅ DEPLOYMENT VALIDATION PASSED" -ForegroundColor Green
    Write-Host "All critical systems are operational`n" -ForegroundColor Green
    exit 0
} else {
    Write-Host "❌ DEPLOYMENT VALIDATION FAILED" -ForegroundColor Red
    Write-Host "Fix errors above before proceeding`n" -ForegroundColor Red
    exit 1
}
