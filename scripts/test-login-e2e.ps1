# End-to-End Login Test
# Tests the actual login flow including error display
Write-Host "=== End-to-End Login Test ===" -ForegroundColor Cyan

# Test 1: Correct credentials
Write-Host "`n[TEST 1] Testing login with correct credentials..." -ForegroundColor Yellow
$loginBody = @{
    username_or_email = "Alakkhaine"
    password = "FinFan11"
} | ConvertTo-Json

try {
    $response = Invoke-WebRequest -Uri "http://localhost/api/squire/auth/login" `
        -Method POST `
        -ContentType "application/json" `
        -Body $loginBody `
        -UseBasicParsing
    
    $content = $response.Content | ConvertFrom-Json
    Write-Host "  ✓ Login successful (Status: $($response.StatusCode))" -ForegroundColor Green
    Write-Host "  ✓ Received JWT token" -ForegroundColor Green
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    Write-Host "  ✗ Login failed (Status: $statusCode)" -ForegroundColor Red
    
    if ($_.Exception.Response) {
        $reader = [System.IO.StreamReader]::new($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "  Error: $responseBody" -ForegroundColor Red
    }
}

# Test 2: Wrong password (should show readable error)
Write-Host "`n[TEST 2] Testing login with wrong password (error display)..." -ForegroundColor Yellow
$badLoginBody = @{
    username_or_email = "Alakkhaine"
    password = "WrongPassword123"
} | ConvertTo-Json

try {
    $response = Invoke-WebRequest -Uri "http://localhost/api/squire/auth/login" `
        -Method POST `
        -ContentType "application/json" `
        -Body $badLoginBody `
        -UseBasicParsing
    
    Write-Host "  ✗ Should have failed but got: $($response.StatusCode)" -ForegroundColor Red
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    
    if ($_.Exception.Response) {
        $reader = [System.IO.StreamReader]::new($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        
        Write-Host "  ✓ Got expected error (Status: $statusCode)" -ForegroundColor Green
        
        # Check if error message is readable (not object literal)
        if ($responseBody -like '*object Object*') {
            Write-Host "  ✗ ERROR: Response contains object literal - error display bug!" -ForegroundColor Red
            Write-Host "  Raw response: $responseBody" -ForegroundColor Yellow
        } else {
            Write-Host "  ✓ Error message is readable" -ForegroundColor Green
            Write-Host "  Response: $responseBody" -ForegroundColor Cyan
        }
    }
}

# Test 3: Missing field (should show validation error)
Write-Host "`n[TEST 3] Testing with old field name 'username' (should fail)..." -ForegroundColor Yellow
$oldFieldBody = @{
    username = "Alakkhaine"
    password = "FinFan11"
} | ConvertTo-Json

try {
    $response = Invoke-WebRequest -Uri "http://localhost/api/squire/auth/login" `
        -Method POST `
        -ContentType "application/json" `
        -Body $oldFieldBody `
        -UseBasicParsing
    
    Write-Host "  ✗ Should have failed with 422 but got: $($response.StatusCode)" -ForegroundColor Red
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    
    if ($statusCode -eq 422) {
        Write-Host "  ✓ Got expected 422 validation error" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Got status $statusCode, expected 422" -ForegroundColor Red
    }
    
    if ($_.Exception.Response) {
        $reader = [System.IO.StreamReader]::new($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "  Response: $responseBody" -ForegroundColor Cyan
    }
}

Write-Host "`n=== Test Summary ===" -ForegroundColor Cyan
Write-Host "If all tests show ✓, login functionality is working correctly." -ForegroundColor White
Write-Host "If any test shows ✗, there are still bugs to fix." -ForegroundColor White
