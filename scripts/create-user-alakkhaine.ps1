# Create User and Open Login Page
# Creates user "Alakkhaine" and opens browser to login page

Write-Host "Creating User and Opening Login Page" -ForegroundColor Cyan
Write-Host "====================================`n" -ForegroundColor Cyan

$username = "Alakkhaine"
$email = "alakkhaine@example.com"
$password = "FinFan11"

# Step 1: Register user
Write-Host "[1] Registering user: $username" -ForegroundColor Yellow
$registerBody = @{
    username = $username
    email = $email
    password = $password
} | ConvertTo-Json

$userExists = $false
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/squire/auth/register" -Method POST -ContentType "application/json" -Body $registerBody -ErrorAction Stop
    Write-Host "Success: User registered successfully!" -ForegroundColor Green
    Write-Host "  User ID: $($response.user_id)" -ForegroundColor Gray
    Write-Host "  Username: $($response.username)" -ForegroundColor Gray
    Write-Host "  Email: $($response.email)" -ForegroundColor Gray
}
catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    if ($statusCode -eq 400) {
        Write-Host "Warning: User already exists, continuing..." -ForegroundColor Yellow
        $userExists = $true
    }
    else {
        Write-Host "Error: Registration failed" -ForegroundColor Red
        Write-Host $_.ErrorDetails.Message -ForegroundColor Red
        exit 1
    }
}

# Step 2: Note about email verification
Write-Host "`n[2] Email Verification Required" -ForegroundColor Yellow
if (-not $userExists) {
    Write-Host "Check MailHog at http://localhost:8025 and click verification link" -ForegroundColor White
}
else {
    Write-Host "User already exists - may already be verified" -ForegroundColor White
}

# Step 3: Open login page and MailHog
Write-Host "`n[3] Opening browser..." -ForegroundColor Cyan
$loginUrl = "http://localhost:8080/squire/login"
$mailhogUrl = "http://localhost:8025"

Write-Host "`nLogin Credentials:" -ForegroundColor Yellow
Write-Host "==================" -ForegroundColor Yellow
Write-Host "URL:      $loginUrl" -ForegroundColor White
Write-Host "Username: $username" -ForegroundColor White
Write-Host "Password: $password" -ForegroundColor White

Start-Process $loginUrl
Start-Sleep -Seconds 1
Start-Process $mailhogUrl

Write-Host "`nBrowser windows opened!" -ForegroundColor Green
Write-Host "  - Login page: $loginUrl" -ForegroundColor Gray
Write-Host "  - MailHog: $mailhogUrl" -ForegroundColor Gray

