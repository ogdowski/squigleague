# Complete Authentication Flow Test - Simplified Version
Write-Host "Complete Authentication Flow Test" -ForegroundColor Cyan

$testEmail = "flowtest2@example.com"
$testUser = "flowtest2"
$testPass = "password123"

# Step 1: Register
Write-Host "`n[1] Registering..." -ForegroundColor Yellow
$registerBody = @{ username=$testUser; email=$testEmail; password=$testPass } | ConvertTo-Json
try {
    $registerResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/squire/auth/register" -Method POST -ContentType "application/json" -Body $registerBody -ErrorAction Stop
    Write-Host "✓ Registration successful!" -ForegroundColor Green
} catch {
    Write-Host "✗ Registration failed" -ForegroundColor Red
    exit 1
}

# Step 2: Get verification token from MailHog
Write-Host "`n[2] Fetching verification email..." -ForegroundColor Yellow
Start-Sleep -Seconds 2
$verificationToken = ""
try {
    $mailhog = Invoke-RestMethod -Uri "http://localhost:8025/api/v2/messages" -ErrorAction Stop
    $email = $mailhog.items | Where-Object { $_.Content.Headers.To -contains $testEmail } | Select-Object -First 1
    if ($email -and ($email.Content.Body -match 'token=([a-f0-9\-]+)')) {
        $verificationToken = $Matches[1]
        Write-Host "✓ Token found!" -ForegroundColor Green
    } else {
        Write-Host "✗ Email not found" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "✗ MailHog error" -ForegroundColor Red
    exit 1
}

# Step 3: Verify email
Write-Host "`n[3] Verifying email..." -ForegroundColor Yellow
try {
    $verify = Invoke-RestMethod -Uri "http://localhost:8000/api/squire/auth/verify-email?token=$verificationToken" -Method GET -ErrorAction Stop
    Write-Host "✓ Email verified!" -ForegroundColor Green
} catch {
    Write-Host "✗ Verification failed" -ForegroundColor Red
    exit 1
}

# Step 4: Login
Write-Host "`n[4] Logging in..." -ForegroundColor Yellow
$loginBody = @{ username_or_email=$testUser; password=$testPass } | ConvertTo-Json
try {
    $login = Invoke-RestMethod -Uri "http://localhost:8000/api/squire/auth/login" -Method POST -ContentType "application/json" -Body $loginBody -ErrorAction Stop
    Write-Host "✓ Login successful!" -ForegroundColor Green
    Write-Host "  Token: $($login.token.Substring(0,20))..." -ForegroundColor Gray
} catch {
    Write-Host "✗ Login failed" -ForegroundColor Red
    exit 1
}

# Step 5: Test authenticated request
Write-Host "`n[5] Testing authenticated request..." -ForegroundColor Yellow
try {
    $userInfo = Invoke-RestMethod -Uri "http://localhost:8000/api/squire/auth/me" -Method GET -Headers @{ Authorization="Bearer $($login.token)" } -ErrorAction Stop
    Write-Host "✓ Authenticated request successful!" -ForegroundColor Green
    Write-Host "  Username: $($userInfo.username)" -ForegroundColor Gray
    Write-Host "  Email Verified: $($userInfo.email_verified)" -ForegroundColor Gray
} catch {
    Write-Host "✗ Auth request failed" -ForegroundColor Red
    exit 1
}

Write-Host "`n✓ Complete authentication flow SUCCESS!" -ForegroundColor Green
