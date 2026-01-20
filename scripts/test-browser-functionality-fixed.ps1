#!/usr/bin/env pwsh
# Test browser functionality via HTTP requests (simulation)
# Tests: Homepage, Login, Registration, Stats

$ErrorActionPreference = "Stop"

Write-Host "`n=== Browser Functionality Test ===" -ForegroundColor Cyan

# Test 1: Homepage loads
Write-Host "`n[1/5] Testing Homepage..." -ForegroundColor Yellow
try {
    $homePage = Invoke-WebRequest -Uri "http://localhost/" -UseBasicParsing -TimeoutSec 5
    if ($homePage.StatusCode -eq 200 -and $homePage.Content -like "*<!DOCTYPE html>*") {
        Write-Host "  Homepage: HTTP $($homePage.StatusCode)" -ForegroundColor Green
    } else {
        Write-Host "  ? Homepage returned unexpected content" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "  ? Homepage FAILED: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test 2: API Stats endpoint
Write-Host "`n[2/5] Testing API Stats..." -ForegroundColor Yellow
try {
    $stats = Invoke-WebRequest -Uri "http://localhost/api/matchup/stats" -UseBasicParsing -TimeoutSec 5
    $statsData = $stats.Content | ConvertFrom-Json
    Write-Host "  ? Stats: HTTP $($stats.StatusCode) - Version: $($statsData.version)" -ForegroundColor Green
} catch {
    Write-Host "  ? Stats FAILED: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test 3: Registration endpoint
Write-Host "`n[3/5] Testing Registration API..." -ForegroundColor Yellow
try {
    $testEmail = "test_$(Get-Date -Format 'yyyyMMddHHmmss')@test.com"
    $regBody = @{
        email = $testEmail
        username = "testuser_$(Get-Date -Format 'HHmmss')"
        password = "TestPass123!"
    } | ConvertTo-Json
    
    $reg = Invoke-WebRequest -Method POST -Uri "http://localhost/api/auth/register" `
        -ContentType "application/json" -Body $regBody -UseBasicParsing -TimeoutSec 5
    
    if ($reg.StatusCode -eq 201) {
        Write-Host "  ? Registration: HTTP $($reg.StatusCode)" -ForegroundColor Green
    } else {
        Write-Host "  ? Registration returned HTTP $($reg.StatusCode)" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "  ? Registration FAILED: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test 4: Login with test user
Write-Host "`n[4/5] Testing Login API..." -ForegroundColor Yellow
try {
    $loginBody = @{
        email = "alakhaine@dundrafts.com"
        password = "FinFan11"
    } | ConvertTo-Json
    
    $login = Invoke-WebRequest -Method POST -Uri "http://localhost/api/auth/login" `
        -ContentType "application/json" -Body $loginBody -UseBasicParsing -TimeoutSec 5
    
    $loginData = $login.Content | ConvertFrom-Json
    if ($login.StatusCode -eq 200 -and $loginData.access_token) {
        Write-Host "  ? Login: HTTP $($login.StatusCode) - Token received" -ForegroundColor Green
        $token = $loginData.access_token
    } else {
        Write-Host "  ? Login succeeded but no token" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "  ? Login FAILED: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test 5: Check frontend JavaScript loads correctly
Write-Host "`n[5/5] Testing Frontend Assets..." -ForegroundColor Yellow
try {
    $indexContent = $homePage.Content
    if ($indexContent -match 'src="/assets/index-[a-zA-Z0-9]+\.js"' -or $indexContent -match 'src="/assets/') {
        Write-Host "  Frontend JS bundle referenced in HTML" -ForegroundColor Green
        
        # Try to fetch the JS file
        if ($indexContent -match 'src="(/assets/[^"]+\.js)"') {
            $jsPath = $matches[1]
            try {
                $js = Invoke-WebRequest -Uri "http://localhost$jsPath" -UseBasicParsing -TimeoutSec 5
                if ($js.StatusCode -eq 200) {
                    Write-Host "  Frontend JS bundle loads: HTTP $($js.StatusCode)" -ForegroundColor Green
                    
                    # Check for localhost:8000 in built JS
                    if ($js.Content -like "*localhost:8000*") {
                        Write-Host "  WARNING: Found localhost:8000 in built JS" -ForegroundColor Red
                        Write-Host "    Frontend may bypass nginx routing" -ForegroundColor Red
                        exit 1
                    } else {
                        Write-Host "  No hardcoded localhost:8000 in JS" -ForegroundColor Green
                    }
                }
            } catch {
                Write-Host "  JS bundle fetch failed: $($_.Exception.Message)" -ForegroundColor Red
                exit 1
            }
        }
    } else {
        Write-Host "  No JS bundle found in HTML" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "  ? Frontend assets check FAILED: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host "`n=== ALL TESTS PASSED ===" -ForegroundColor Green
Write-Host "`nApplication is READY at: http://localhost/" -ForegroundColor Cyan
Write-Host "Test user: alakhaine@dundrafts.com / FinFan11`n" -ForegroundColor Cyan

exit 0
