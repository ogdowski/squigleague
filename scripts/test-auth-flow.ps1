# test-auth-flow.ps1
# Tests the complete authentication flow

$ErrorActionPreference = "Stop"

Write-Host "=== SquigLeague Authentication Flow Test ===" -ForegroundColor Cyan
Write-Host ""

$baseUrl = "http://localhost:8000/api/squire"

# Helper function to make API calls
function Invoke-ApiCall {
    param(
        [string]$Method,
        [string]$Endpoint,
        [object]$Body = $null,
        [string]$Token = $null
    )
    
    $uri = "$baseUrl$Endpoint"
    $headers = @{
        "Content-Type" = "application/json"
    }
    
    if ($Token) {
        $headers["Authorization"] = "Bearer $Token"
    }
    
    try {
        if ($Body) {
            $jsonBody = $Body | ConvertTo-Json
            $response = Invoke-WebRequest -Uri $uri -Method $Method -Headers $headers -Body $jsonBody -UseBasicParsing
        } else {
            $response = Invoke-WebRequest -Uri $uri -Method $Method -Headers $headers -UseBasicParsing
        }
        
        return @{
            Success = $true
            StatusCode = $response.StatusCode
            Content = $response.Content | ConvertFrom-Json
        }
    } catch {
        return @{
            Success = $false
            StatusCode = $_.Exception.Response.StatusCode.value__
            Error = $_.Exception.Message
        }
    }
}

# Test 1: Register a new user
Write-Host "Test 1: User Registration" -ForegroundColor Yellow
$timestamp = Get-Date -Format "yyyyMMddHHmmss"
$testUser = @{
    username = "testuser_$timestamp"
    email = "test_$timestamp@example.com"
    password = "TestPassword123!"
}

$result = Invoke-ApiCall -Method POST -Endpoint "/auth/register" -Body $testUser

if ($result.Success) {
    Write-Host "  SUCCESS: User registered" -ForegroundColor Green
    Write-Host "  Username: $($testUser.username)" -ForegroundColor Gray
    Write-Host "  Email: $($testUser.email)" -ForegroundColor Gray
} else {
    Write-Host "  FAILED: Registration failed" -ForegroundColor Red
    Write-Host "  Error: $($result.Error)" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Test 2: Try to login before email verification
Write-Host "Test 2: Login Before Email Verification (should fail)" -ForegroundColor Yellow
$loginData = @{
    username = $testUser.username
    password = $testUser.password
}

$result = Invoke-ApiCall -Method POST -Endpoint "/auth/login" -Body $loginData

if (-not $result.Success -and $result.StatusCode -eq 403) {
    Write-Host "  SUCCESS: Login correctly blocked (email not verified)" -ForegroundColor Green
} else {
    Write-Host "  FAILED: Login should have been blocked" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Test 3: Get verification token from MailHog
Write-Host "Test 3: Retrieve Verification Email from MailHog" -ForegroundColor Yellow
Start-Sleep -Seconds 2  # Wait for email to be sent

try {
    $mailhogUrl = "http://localhost:8025/api/v2/messages"
    $messages = Invoke-RestMethod -Uri $mailhogUrl -Method GET
    
    if ($messages.count -eq 0) {
        Write-Host "  FAILED: No emails found in MailHog" -ForegroundColor Red
        Write-Host "  Check SMTP configuration in .env.local" -ForegroundColor Yellow
        exit 1
    }
    
    # Find the verification email
    $verificationEmail = $messages.items | Where-Object { 
        $_.Content.Headers.To -contains $testUser.email 
    } | Select-Object -First 1
    
    if (-not $verificationEmail) {
        Write-Host "  FAILED: Verification email not found" -ForegroundColor Red
        exit 1
    }
    
    # Extract token from email body
    $emailBody = $verificationEmail.Content.Body
    if ($emailBody -match 'token=([a-f0-9-]+)') {
        $verificationToken = $Matches[1]
        Write-Host "  SUCCESS: Verification email received" -ForegroundColor Green
        Write-Host "  Token: $verificationToken" -ForegroundColor Gray
    } else {
        Write-Host "  FAILED: Could not extract verification token from email" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "  FAILED: Could not retrieve emails from MailHog" -ForegroundColor Red
    Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "  Make sure MailHog is running (run setup-mailhog.ps1)" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Test 4: Verify email
Write-Host "Test 4: Email Verification" -ForegroundColor Yellow
$result = Invoke-ApiCall -Method GET -Endpoint "/auth/verify-email?token=$verificationToken"

if ($result.Success) {
    Write-Host "  SUCCESS: Email verified" -ForegroundColor Green
} else {
    Write-Host "  FAILED: Email verification failed" -ForegroundColor Red
    Write-Host "  Error: $($result.Error)" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Test 5: Login after verification
Write-Host "Test 5: Login After Email Verification" -ForegroundColor Yellow
$result = Invoke-ApiCall -Method POST -Endpoint "/auth/login" -Body $loginData

if ($result.Success) {
    $jwtToken = $result.Content.access_token
    Write-Host "  SUCCESS: Login successful" -ForegroundColor Green
    Write-Host "  Token: $($jwtToken.Substring(0, 20))..." -ForegroundColor Gray
} else {
    Write-Host "  FAILED: Login failed" -ForegroundColor Red
    Write-Host "  Error: $($result.Error)" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Test 6: Get current user info
Write-Host "Test 6: Get Current User Info" -ForegroundColor Yellow
$result = Invoke-ApiCall -Method GET -Endpoint "/auth/me" -Token $jwtToken

if ($result.Success) {
    Write-Host "  SUCCESS: Retrieved user info" -ForegroundColor Green
    Write-Host "  User ID: $($result.Content.id)" -ForegroundColor Gray
    Write-Host "  Username: $($result.Content.username)" -ForegroundColor Gray
    Write-Host "  Email: $($result.Content.email)" -ForegroundColor Gray
    Write-Host "  Verified: $($result.Content.email_verified)" -ForegroundColor Gray
} else {
    Write-Host "  FAILED: Could not retrieve user info" -ForegroundColor Red
    Write-Host "  Error: $($result.Error)" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Test 7: Try to access protected endpoint without token
Write-Host "Test 7: Access Protected Endpoint Without Token (should fail)" -ForegroundColor Yellow
$result = Invoke-ApiCall -Method GET -Endpoint "/auth/me"

if (-not $result.Success -and $result.StatusCode -eq 401) {
    Write-Host "  SUCCESS: Access correctly denied without token" -ForegroundColor Green
} else {
    Write-Host "  FAILED: Should have been denied access" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=== All Tests Passed ===" -ForegroundColor Green
Write-Host ""
Write-Host "Test User Credentials:" -ForegroundColor Cyan
Write-Host "  Username: $($testUser.username)" -ForegroundColor White
Write-Host "  Email: $($testUser.email)" -ForegroundColor White
Write-Host "  Password: $($testUser.password)" -ForegroundColor White
Write-Host "  JWT Token: $jwtToken" -ForegroundColor White
Write-Host ""
Write-Host "You can use these credentials to test the frontend:" -ForegroundColor Yellow
Write-Host "  http://localhost:8080/squire/login" -ForegroundColor Cyan
Write-Host ""
