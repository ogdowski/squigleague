# diagnose-auth.ps1
# Diagnoses authentication system issues

Write-Host "=== Authentication System Diagnostics ===" -ForegroundColor Cyan
Write-Host ""

# Check 1: Backend health
Write-Host "[1] Checking backend health..." -ForegroundColor Yellow
try {
    $health = Invoke-WebRequest -Uri "http://localhost:8000/api/squire/health" -UseBasicParsing
    Write-Host "   ✓ Backend is responding: $($health.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "   ✗ Backend not responding: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Check 2: Database connection
Write-Host "[2] Checking database..." -ForegroundColor Yellow
try {
    $dbCheck = docker exec squig-postgres pg_isready -U squig_user -d squigleague
    Write-Host "   ✓ Database is ready" -ForegroundColor Green
} catch {
    Write-Host "   ✗ Database issue: $($_.Exception.Message)" -ForegroundColor Red
}

# Check 3: MailHog
Write-Host "[3] Checking MailHog..." -ForegroundColor Yellow
try {
    $mailhog = Invoke-WebRequest -Uri "http://localhost:8025" -UseBasicParsing
    Write-Host "   ✓ MailHog is running: $($mailhog.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "   ✗ MailHog not responding: $($_.Exception.Message)" -ForegroundColor Red
}

# Check 4: Auth endpoint exists
Write-Host "[4] Checking auth endpoints..." -ForegroundColor Yellow
try {
    $docs = Invoke-WebRequest -Uri "http://localhost:8000/docs" -UseBasicParsing
    if ($docs.Content -match "auth/register") {
        Write-Host "   ✓ Auth endpoints registered" -ForegroundColor Green
    } else {
        Write-Host "   ⚠ Auth endpoints may not be registered" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ✗ Cannot access API docs: $($_.Exception.Message)" -ForegroundColor Red
}

# Check 5: Test registration with detailed error
Write-Host "[5] Testing registration endpoint..." -ForegroundColor Yellow
$testBody = @{
    username = "diagtest$(Get-Random -Maximum 9999)"
    email = "diagtest$(Get-Random -Maximum 9999)@example.com"
    password = "TestPass123!"
} | ConvertTo-Json

try {
    $response = Invoke-WebRequest -Uri 'http://localhost:8000/api/squire/auth/register' `
        -Method POST `
        -Body $testBody `
        -ContentType 'application/json' `
        -UseBasicParsing
    
    Write-Host "   ✓ Registration successful: $($response.StatusCode)" -ForegroundColor Green
    $result = $response.Content | ConvertFrom-Json
    Write-Host "   User ID: $($result.user_id)" -ForegroundColor Gray
} catch {
    $statusCode = $_.Exception.Response.StatusCode.Value__
    Write-Host "   ✗ Registration failed: HTTP $statusCode" -ForegroundColor Red
    
    try {
        $reader = [System.IO.StreamReader]::new($_.Exception.Response.GetResponseStream())
        $errorBody = $reader.ReadToEnd()
        Write-Host "   Error details: $errorBody" -ForegroundColor Yellow
    } catch {
        Write-Host "   Could not read error details" -ForegroundColor Yellow
    }
}

# Check 6: Backend logs
Write-Host "[6] Recent backend logs..." -ForegroundColor Yellow
docker logs squig --tail 10 | Out-String | Write-Host -ForegroundColor Gray

Write-Host ""
Write-Host "=== Diagnostic Complete ===" -ForegroundColor Cyan
Write-Host "Services:" -ForegroundColor White
Write-Host "  Backend: http://localhost:8000" -ForegroundColor Gray
Write-Host "  API Docs: http://localhost:8000/docs" -ForegroundColor Gray
Write-Host "  MailHog: http://localhost:8025" -ForegroundColor Gray
Write-Host "  Frontend: http://localhost:8080" -ForegroundColor Gray
