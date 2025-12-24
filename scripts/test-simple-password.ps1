# Test Registration with Simple Password (After Fix)
# Tests that password validation no longer requires special characters

Write-Host "Testing Registration with Simple Password" -ForegroundColor Cyan
Write-Host "=========================================`n" -ForegroundColor Cyan

# Test with simple password (no special character, just alphanumeric)
Write-Host "Registering user with password: testpass123" -ForegroundColor Yellow
$body = @{
    username = "simpleuser"
    email = "simple@example.com"
    password = "testpass123"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/squire/auth/register" `
        -Method POST `
        -ContentType "application/json" `
        -Body $body `
        -ErrorAction Stop
    
    Write-Host "`nSUCCESS!" -ForegroundColor Green
    Write-Host "User ID: $($response.user_id)" -ForegroundColor Green
    Write-Host "Username: $($response.username)" -ForegroundColor Green
    Write-Host "Email: $($response.email)" -ForegroundColor Green
    Write-Host "Message: $($response.message)" -ForegroundColor Green
    
    Write-Host "`nCheck MailHog for verification email:" -ForegroundColor Cyan
    Write-Host "http://localhost:8025" -ForegroundColor Yellow
    
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    $errorBody = $_.ErrorDetails.Message | ConvertFrom-Json
    
    Write-Host "`nFAILED!" -ForegroundColor Red
    Write-Host "Status Code: $statusCode" -ForegroundColor Red
    Write-Host "Error: $($errorBody.detail)" -ForegroundColor Red
}

Write-Host "`nTest Complete!" -ForegroundColor Cyan
