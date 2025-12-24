# Open Browser for Testing Authentication
# Opens the registration page and shows test instructions

Write-Host "Opening Browser for Authentication Testing" -ForegroundColor Cyan
Write-Host "==========================================`n" -ForegroundColor Cyan

$frontendUrl = "http://localhost:8080/squire/register"
$mailhogUrl = "http://localhost:8025"

Write-Host "Test Instructions:" -ForegroundColor Yellow
Write-Host "1. Register a new user at: $frontendUrl" -ForegroundColor White
Write-Host "2. Check verification email at: $mailhogUrl" -ForegroundColor White
Write-Host "3. Click verification link in email" -ForegroundColor White
Write-Host "4. Login at: http://localhost:8080/squire/login`n" -ForegroundColor White

Write-Host "Password Requirements:" -ForegroundColor Yellow
Write-Host "- Minimum 8 characters" -ForegroundColor White
Write-Host "- No special characters required!" -ForegroundColor Green
Write-Host "- Example: 'password123' is valid`n" -ForegroundColor White

Write-Host "Opening registration page..." -ForegroundColor Cyan
Start-Process $frontendUrl

Write-Host "`nOpening MailHog..." -ForegroundColor Cyan
Start-Process $mailhogUrl

Write-Host "`nBrowsers opened! Follow the test instructions above." -ForegroundColor Green
