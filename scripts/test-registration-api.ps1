# Test Registration API with Different Password Scenarios
# Tests password validation and identifies exact issue

Write-Host "Testing Registration API" -ForegroundColor Cyan
Write-Host "========================`n" -ForegroundColor Cyan

# Test 1: Password without special character (likely the issue)
Write-Host "Test 1: Password without special character (testpass123)" -ForegroundColor Yellow
$body1 = @{
    username = "testuser1"
    email = "test1@example.com"
    password = "testpass123"
} | ConvertTo-Json

$response1 = Invoke-WebRequest -Uri "http://localhost:8000/api/squire/auth/register" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body1 `
    -UseBasicParsing `
    -ErrorAction SilentlyContinue

if ($response1) {
    Write-Host "Status: $($response1.StatusCode)" -ForegroundColor Green
    Write-Host "Response: $($response1.Content)`n"
} else {
    Write-Host "Status: FAILED" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)`n"
}

# Test 2: Password WITH special character
Write-Host "Test 2: Password WITH special character (testpass123!)" -ForegroundColor Yellow
$body2 = @{
    username = "testuser2"
    email = "test2@example.com"
    password = "testpass123!"
} | ConvertTo-Json

$response2 = Invoke-WebRequest -Uri "http://localhost:8000/api/squire/auth/register" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body2 `
    -UseBasicParsing `
    -ErrorAction SilentlyContinue

if ($response2) {
    Write-Host "Status: $($response2.StatusCode)" -ForegroundColor Green
    Write-Host "Response: $($response2.Content)`n"
} else {
    Write-Host "Status: FAILED" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)`n"
}

# Test 3: Get exact error from first test
Write-Host "Test 3: Getting detailed error for password without special char" -ForegroundColor Yellow
try {
    $errorResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/squire/auth/register" `
        -Method POST `
        -ContentType "application/json" `
        -Body $body1 `
        -ErrorAction Stop
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    $errorBody = $_.ErrorDetails.Message
    Write-Host "Status Code: $statusCode" -ForegroundColor Red
    Write-Host "Error Detail: $errorBody`n" -ForegroundColor Red
}

Write-Host "Diagnosis Complete!" -ForegroundColor Green
Write-Host "If Test 1 fails but Test 2 succeeds, the issue is the password validator requiring special characters."
