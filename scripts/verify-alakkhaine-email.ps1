# Verify Alakkhaine Email Script
$ErrorActionPreference = "Stop"

Write-Host "Verifying email for user Alakkhaine..." -ForegroundColor Cyan
Write-Host ""

# Get the verification token from MailHog
Write-Host "1. Checking MailHog for verification email..." -ForegroundColor Yellow
try {
    $mailhogResponse = Invoke-RestMethod -Uri "http://localhost:8025/api/v2/messages"
    $messages = $mailhogResponse.items
    
    # Find the verification email for alakkhaine
    $verificationEmail = $messages | Where-Object { 
        $_.Content.Headers.To -match "alakkhaine@example.com" -and 
        $_.Content.Headers.Subject -match "verify|confirmation"
    } | Select-Object -First 1
    
    if ($verificationEmail) {
        Write-Host "   Found verification email" -ForegroundColor Green
        
        # Extract verification link from email body
        $body = $verificationEmail.Content.Body
        if ($body -match "(http://localhost[^\s]+verify[^\s]+)") {
            $verifyLink = $matches[1]
            Write-Host "   Verification link: $verifyLink" -ForegroundColor White
            
            # Click the verification link
            Write-Host ""
            Write-Host "2. Clicking verification link..." -ForegroundColor Yellow
            try {
                $verifyResponse = Invoke-WebRequest -Uri $verifyLink -Method Get
                Write-Host "   Email verified successfully!" -ForegroundColor Green
                
                Write-Host ""
                Write-Host "SUCCESS: User alakkhaine@example.com is now verified" -ForegroundColor Green
                Write-Host "You can now login at: http://localhost/squire/login" -ForegroundColor Cyan
                Write-Host "  Username: alakkhaine" -ForegroundColor White
                Write-Host "  Password: FinFan11" -ForegroundColor White
            }
            catch {
                Write-Host "   ERROR: Failed to verify - $($_.Exception.Message)" -ForegroundColor Red
                exit 1
            }
        }
        else {
            Write-Host "   ERROR: Could not extract verification link from email" -ForegroundColor Red
            Write-Host "   Manual verification needed at: http://localhost:8025" -ForegroundColor Yellow
            exit 1
        }
    }
    else {
        Write-Host "   No verification email found" -ForegroundColor Yellow
        Write-Host "   User may already be verified or email not sent yet" -ForegroundColor White
        
        # Check if user exists and is verified
        Write-Host ""
        Write-Host "2. Checking user status in database..." -ForegroundColor Yellow
        $checkUser = docker exec squig-postgres psql -U squig_user -d squig_db -t -c "SELECT email, is_verified FROM users WHERE email='alakkhaine@example.com';"
        
        if ($checkUser) {
            Write-Host "   User found: $checkUser" -ForegroundColor White
            if ($checkUser -match "t\s*$") {
                Write-Host "   User is already verified!" -ForegroundColor Green
            }
            else {
                Write-Host "   User exists but not verified" -ForegroundColor Yellow
                Write-Host "   Check MailHog manually at: http://localhost:8025" -ForegroundColor Cyan
            }
        }
    }
}
catch {
    Write-Host "ERROR: Failed to check MailHog - $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Check manually at: http://localhost:8025" -ForegroundColor Yellow
    exit 1
}
