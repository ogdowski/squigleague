# Complete Authentication Flow Test
Write-Host "Complete Authentication Flow Test" -ForegroundColor Cyan

$testEmail = "flowtest3@example.com"
$testUser = "flowtest3"
$testPass = "password123"

# Step 1: Register
Write-Host "`n[1] Registering..." -ForegroundColor Yellow
$registerBody = @{ username=$testUser; email=$testEmail; password=$testPass } | ConvertTo-Json
$registerResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/squire/auth/register" -Method POST -ContentType "application/json" -Body $registerBody
if ($registerResponse) {
    Write-Host "✓ Registration successful!" -ForegroundColor Green
} else {
    Write-Host "✗ Registration failed" -ForegroundColor Red
    exit 1
}

# Step 2: Get verification token from MailHog
Write-Host "`n[2] Fetching verification email..." -ForegroundColor Yellow
Start-Sleep -Seconds 2
$mailhog = Invoke-RestMethod -Uri "http://localhost:8025/api/v2/messages"
$email = $mailhog.items | Where-Object { $_.Content.Headers.To -contains $testEmail } | Select-Object -First 1
if (-not $email) {
    Write-Host "✗ Email not found in MailHog" -ForegroundColor Red
    exit 1
}

$emailBody = $email.Content.Body
if ($emailBody -match 'token=([a-f0-9\-]+)') {
    $verificationToken = $Matches[1]
    Write-Host "✓ Token found: $verificationToken" -ForegroundColor Green
} else {
    Write-Host "✗ Could not extract token" -ForegroundColor Red
    exit 1
}

# Step 3: Verify email
Write-Host "`n[3] Verifying email..." -ForegroundColor Yellow
$verify = Invoke-RestMethod -Uri "http://localhost:8000/api/squire/auth/verify-email?token=$verificationToken" -Method GET
if ($verify.message) {
    Write-Host "✓ Email verified: $($verify.message)" -ForegroundColor Green
} else {
    Write-Host "✗ Verification failed" -ForegroundColor Red
    exit 1
}

# Step 4: Login
Write-Host "`n[4] Logging in..." -ForegroundColor Yellow
$loginBody = @{ username_or_email=$testUser; password=$testPass } | ConvertTo-Json
$login = Invoke-RestMethod -Uri "http://localhost:8000/api/squire/auth/login" -Method POST -ContentType "application/json" -Body $loginBody
if ($login.token) {
    Write-Host "✓ Login successful!" -ForegroundColor Green
    Write-Host "  Username: $($login.username)" -ForegroundColor Gray
    Write-Host "  Token: $($login.token.Substring(0,20))..." -ForegroundColor Gray
} else {
    Write-Host "✗ Login failed" -ForegroundColor Red
    exit 1
}

# Step 5: Test authenticated request
Write-Host "`n[5] Testing authenticated request..." -ForegroundColor Yellow
$userInfo = Invoke-RestMethod -Uri "http://localhost:8000/api/squire/auth/me" -Method GET -Headers @{ Authorization="Bearer $($login.token)" }
if ($userInfo.username) {
    Write-Host "✓ Authenticated request successful!" -ForegroundColor Green
    Write-Host "  Username: $($userInfo.username)" -ForegroundColor Gray
    Write-Host "  Email: $($userInfo.email)" -ForegroundColor Gray
    Write-Host "  Email Verified: $($userInfo.email_verified)" -ForegroundColor Gray
} else {
    Write-Host "✗ Auth request failed" -ForegroundColor Red
    exit 1
}

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "✓ COMPLETE AUTH FLOW SUCCESS!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
