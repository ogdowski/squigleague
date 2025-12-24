# Check User Status Script
$ErrorActionPreference = "Continue"

Write-Host "Checking Alakkhaine user status..." -ForegroundColor Cyan
Write-Host ""

# Check if user exists in database
Write-Host "1. Querying database for user..." -ForegroundColor Yellow
$userQuery = docker exec squig-postgres psql -U squig_user -d squig_db -c "SELECT id, username, email, is_verified, created_at FROM users WHERE username='alakkhaine';"

if ($LASTEXITCODE -eq 0) {
    Write-Host $userQuery
}
else {
    Write-Host "   Database query failed" -ForegroundColor Red
}

# Check MailHog messages
Write-Host ""
Write-Host "2. Checking MailHog for any emails to alakkhaine..." -ForegroundColor Yellow
try {
    $mailhog = Invoke-RestMethod -Uri "http://localhost:8025/api/v2/messages?limit=50"
    $alakkhaineMails = $mailhog.items | Where-Object {
        $_.Content.Headers.To -like "*alakkhaine*"
    }
    
    if ($alakkhaineMails) {
        Write-Host "   Found $($alakkhaineMails.Count) email(s)" -ForegroundColor Green
        foreach ($mail in $alakkhaineMails) {
            Write-Host "   - Subject: $($mail.Content.Headers.Subject)" -ForegroundColor White
            Write-Host "     To: $($mail.Content.Headers.To)" -ForegroundColor Gray
        }
    }
    else {
        Write-Host "   No emails found for alakkhaine" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "   MailHog check failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "3. Testing login attempt..." -ForegroundColor Yellow
try {
    $loginBody = @{
        username = "alakkhaine"
        password = "FinFan11"
    } | ConvertTo-Json
    
    $loginResponse = Invoke-WebRequest -Uri "http://localhost/api/squire/auth/login" -Method Post -Body $loginBody -ContentType "application/json"
    
    if ($loginResponse.StatusCode -eq 200) {
        Write-Host "   LOGIN SUCCESS!" -ForegroundColor Green
        $result = $loginResponse.Content | ConvertFrom-Json
        Write-Host "   Token received: $($result.access_token.Substring(0, 20))..." -ForegroundColor White
    }
}
catch {
    $errorMsg = $_.Exception.Message
    if ($errorMsg -match "403") {
        Write-Host "   LOGIN BLOCKED: Email not verified" -ForegroundColor Yellow
    }
    elseif ($errorMsg -match "401") {
        Write-Host "   LOGIN FAILED: Invalid credentials" -ForegroundColor Red
    }
    else {
        Write-Host "   LOGIN ERROR: $errorMsg" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "You can check MailHog manually at: http://localhost:8025" -ForegroundColor Cyan
