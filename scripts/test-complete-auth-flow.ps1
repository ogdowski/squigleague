# Complete Authentication Flow Test
# Tests: Register → Get verification token → Verify email → Login

Write-Host "Complete Authentication Flow Test" -ForegroundColor Cyan
Write-Host "=================================`n" -ForegroundColor Cyan

$testEmail = "flowtest@example.com"
$testUser = "flowtest"
$testPass = "password123"

# Step 1: Register
Write-Host "[Step 1] Registering new user..." -ForegroundColor Yellow
$registerBody = @{
    username = $testUser
    email = $testEmail
    password = $testPass
} | ConvertTo-Json

try {
    $registerResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/squire/auth/register" `
        -Method POST `
        -ContentType "application/json" `
        -Body $registerBody `
        -ErrorAction Stop
    
    Write-Host "✓ Registration successful!" -ForegroundColor Green
    Write-Host "  User ID: $($registerResponse.user_id)" -ForegroundColor Gray
    
} catch {
    Write-Host "✗ Registration failed: $($_.ErrorDetails.Message)" -ForegroundColor Red
    exit 1
}

# Step 2: Get verification token from MailHog
Write-Host "`n[Step 2] Fetching verification email from MailHog..." -ForegroundColor Yellow
Start-Sleep -Seconds 2  # Wait for email to arrive

$verificationToken = $null
try {
    $mailhogMessages = Invoke-RestMethod -Uri "http://localhost:8025/api/v2/messages" -ErrorAction Stop
    $verificationEmail = $mailhogMessages.items | Where-Object { 
        $_.Content.Headers.To -contains $testEmail 
    } | Select-Object -First 1
    
    if ($verificationEmail) {
        # Extract token from email body
        $emailBody = $verificationEmail.Content.Body
        $tokenMatch = $emailBody -match 'token=([a-f0-9\-]+)'
        
        if ($tokenMatch) {
            $verificationToken = $Matches[1]
            Write-Host "✓ Verification token found!" -ForegroundColor Green
            Write-Host "  Token: $verificationToken" -ForegroundColor Gray
        } else {
            Write-Host "✗ Could not extract token from email" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "✗ Verification email not found in MailHog" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "✗ Failed to fetch email: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Step 3: Verify email
Write-Host "`n[Step 3] Verifying email..." -ForegroundColor Yellow
try {
    $verifyResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/squire/auth/verify-email?token=$verificationToken" `
        -Method GET `
        -ErrorAction Stop
    
    Write-Host "✓ Email verified!" -ForegroundColor Green
    Write-Host "  Message: $($verifyResponse.message)" -ForegroundColor Gray
    
} catch {
    Write-Host "✗ Email verification failed: $($_.ErrorDetails.Message)" -ForegroundColor Red
    exit 1
}

# Step 4: Login
Write-Host "`n[Step 4] Logging in..." -ForegroundColor Yellow
$loginBody = @{
    username_or_email = $testUser
    password = $testPass
} | ConvertTo-Json

try {
    $loginResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/squire/auth/login" `
        -Method POST `
        -ContentType "application/json" `
        -Body $loginBody `
        -ErrorAction Stop
    
    Write-Host "✓ Login successful!" -ForegroundColor Green
    Write-Host "  User ID: $($loginResponse.user_id)" -ForegroundColor Gray
    Write-Host "  Username: $($loginResponse.username)" -ForegroundColor Gray
    Write-Host "  Token: $($loginResponse.token.Substring(0, 20))..." -ForegroundColor Gray
    Write-Host "  Expires: $($loginResponse.expires_at)" -ForegroundColor Gray
    
} catch {
    Write-Host "✗ Login failed: $($_.ErrorDetails.Message)" -ForegroundColor Red
    exit 1
}

# Step 5: Test authenticated request
Write-Host "`n[Step 5] Testing authenticated request..." -ForegroundColor Yellow
try {
    $userInfoResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/squire/auth/me" `
        -Method GET `
        -Headers @{ Authorization = "Bearer $($loginResponse.token)" } `
        -ErrorAction Stop
    
    Write-Host "✓ Authenticated request successful!" -ForegroundColor Green
    Write-Host "  Username: $($userInfoResponse.username)" -ForegroundColor Gray
    Write-Host "  Email: $($userInfoResponse.email)" -ForegroundColor Gray
    Write-Host "  Email Verified: $($userInfoResponse.email_verified)" -ForegroundColor Gray
    Write-Host "  Is Admin: $($userInfoResponse.is_admin)" -ForegroundColor Gray
    
} catch {
    Write-Host "✗ Authenticated request failed: $($_.ErrorDetails.Message)" -ForegroundColor Red
    exit 1
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "✓ Complete authentication flow SUCCESS!" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan
