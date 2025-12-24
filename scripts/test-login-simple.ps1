# End-to-End Login Test
Write-Host "=== End-to-End Login Test ===" -ForegroundColor Cyan

# Test 1: Correct credentials
Write-Host "`n[TEST 1] Login with correct credentials..." -ForegroundColor Yellow
$loginBody = '{"username_or_email":"Alakkhaine","password":"FinFan11"}'

try {
    $response = Invoke-WebRequest -Uri "http://localhost/api/squire/auth/login" `
        -Method POST `
        -ContentType "application/json" `
        -Body $loginBody `
        -UseBasicParsing
    
    Write-Host "  PASS: Login successful (Status: $($response.StatusCode))" -ForegroundColor Green
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    Write-Host "  FAIL: Login failed (Status: $statusCode)" -ForegroundColor Red
}

# Test 2: Wrong password
Write-Host "`n[TEST 2] Login with wrong password..." -ForegroundColor Yellow
$badLoginBody = '{"username_or_email":"Alakkhaine","password":"WrongPassword"}'

try {
    $response = Invoke-WebRequest -Uri "http://localhost/api/squire/auth/login" `
        -Method POST `
        -ContentType "application/json" `
        -Body $badLoginBody `
        -UseBasicParsing
    
    Write-Host "  FAIL: Should have rejected bad password" -ForegroundColor Red
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    Write-Host "  PASS: Rejected bad credentials (Status: $statusCode)" -ForegroundColor Green
}

# Test 3: Old field name (should get 422)
Write-Host "`n[TEST 3] Login with old field name 'username'..." -ForegroundColor Yellow
$oldFieldBody = '{"username":"Alakkhaine","password":"FinFan11"}'

try {
    $response = Invoke-WebRequest -Uri "http://localhost/api/squire/auth/login" `
        -Method POST `
        -ContentType "application/json" `
        -Body $oldFieldBody `
        -UseBasicParsing
    
    Write-Host "  FAIL: Should have rejected old field name" -ForegroundColor Red
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    if ($statusCode -eq 422) {
        Write-Host "  PASS: Got 422 validation error as expected" -ForegroundColor Green
    } else {
        Write-Host "  FAIL: Got status $statusCode, expected 422" -ForegroundColor Red
    }
}

Write-Host "`n=== Done ===" -ForegroundColor Cyan
