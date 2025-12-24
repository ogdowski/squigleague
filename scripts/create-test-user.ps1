# create-test-user.ps1
# Create a test user and verify email automatically

$ErrorActionPreference = "Stop"

Write-Host "=== Creating Test User ===" -ForegroundColor Cyan
Write-Host ""

$baseUrl = "http://localhost:8000/api/squire"
$timestamp = Get-Date -Format "yyyyMMddHHmmss"

# Create test user
$testUser = @{
    username = "testuser$timestamp"
    email = "test$timestamp@example.com"
    password = "TestPassword123!"
}

Write-Host "Registering user: $($testUser.username)" -ForegroundColor Yellow
$body = $testUser | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/auth/register" -Method POST -Body $body -ContentType "application/json"
    Write-Host "  User registered successfully" -ForegroundColor Green
} catch {
    Write-Host "  ERROR: Registration failed" -ForegroundColor Red
    Write-Host "  $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Waiting for email..." -ForegroundColor Yellow
Start-Sleep -Seconds 2

# Get verification token from MailHog
try {
    $messages = Invoke-RestMethod -Uri "http://localhost:8025/api/v2/messages" -Method GET
    
    if ($messages.count -eq 0) {
        Write-Host "  WARNING: No emails found in MailHog" -ForegroundColor Yellow
        Write-Host "  User created but not verified" -ForegroundColor Yellow
    } else {
        # Find the verification email
        $verificationEmail = $messages.items | Where-Object { 
            $_.Content.Headers.To -contains $testUser.email 
        } | Select-Object -First 1
        
        if ($verificationEmail) {
            # Extract token from email body
            $emailBody = $verificationEmail.Content.Body
            if ($emailBody -match 'token=([a-f0-9-]+)') {
                $token = $Matches[1]
                Write-Host "  Verification email received" -ForegroundColor Green
                
                # Verify email
                Write-Host ""
                Write-Host "Verifying email..." -ForegroundColor Yellow
                $verifyResponse = Invoke-RestMethod -Uri "$baseUrl/auth/verify-email?token=$token" -Method GET
                Write-Host "  Email verified!" -ForegroundColor Green
            }
        }
    }
} catch {
    Write-Host "  WARNING: Could not retrieve verification email" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== Test User Created ===" -ForegroundColor Green
Write-Host ""
Write-Host "Credentials:" -ForegroundColor Cyan
Write-Host "  Username: $($testUser.username)" -ForegroundColor White
Write-Host "  Email:    $($testUser.email)" -ForegroundColor White
Write-Host "  Password: $($testUser.password)" -ForegroundColor White
Write-Host ""
Write-Host "You can login at: http://localhost:8080/squire/login" -ForegroundColor Yellow
Write-Host ""
