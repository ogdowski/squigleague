# Configure Real Email Service (Gmail SMTP)
# Sets up truthful email sending instead of fake MailHog

Write-Host "Email Service Configuration" -ForegroundColor Cyan
Write-Host "===========================`n" -ForegroundColor Cyan

Write-Host "To use REAL email instead of MailHog, you need:" -ForegroundColor Yellow
Write-Host "1. A Gmail account (or other email provider)" -ForegroundColor White
Write-Host "2. App password (for Gmail: https://myaccount.google.com/apppasswords)" -ForegroundColor White
Write-Host "`n"

Write-Host "Steps to configure:" -ForegroundColor Cyan
Write-Host "1. Go to your Gmail account settings" -ForegroundColor White
Write-Host "2. Enable 2-factor authentication" -ForegroundColor White
Write-Host "3. Create an App Password for 'Mail'" -ForegroundColor White
Write-Host "4. Add these to .env.local:" -ForegroundColor White
Write-Host "`n"

Write-Host "Required .env.local variables:" -ForegroundColor Yellow
Write-Host @"
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_USE_TLS=true
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_FROM_NAME=SquigLeague
BASE_URL=http://localhost:8080
"@ -ForegroundColor Green

Write-Host "`n"
Write-Host "Alternative Email Providers:" -ForegroundColor Cyan
Write-Host "- SendGrid: smtp.sendgrid.net:587" -ForegroundColor White
Write-Host "- Mailgun: smtp.mailgun.org:587" -ForegroundColor White
Write-Host "- AWS SES: email-smtp.us-east-1.amazonaws.com:587" -ForegroundColor White
Write-Host "- Outlook: smtp-mail.outlook.com:587" -ForegroundColor White
Write-Host "`n"

Write-Host "Current .env.local settings:" -ForegroundColor Yellow
if (Test-Path .env.local) {
    $envContent = Get-Content .env.local
    $smtpLines = $envContent | Select-String "SMTP_|BASE_URL"
    if ($smtpLines) {
        $smtpLines | ForEach-Object { Write-Host $_ -ForegroundColor White }
    } else {
        Write-Host "No SMTP configuration found" -ForegroundColor Red
    }
} else {
    Write-Host ".env.local not found!" -ForegroundColor Red
}

Write-Host "`n"
Write-Host "After configuring, restart backend with:" -ForegroundColor Cyan
Write-Host ".\scripts\runner.ps1 -Script restart-backend.ps1" -ForegroundColor Yellow
