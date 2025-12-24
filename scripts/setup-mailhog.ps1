# setup-mailhog.ps1
# Sets up MailHog for email testing

$ErrorActionPreference = "Stop"

Write-Host "=== SquigLeague MailHog Setup ===" -ForegroundColor Cyan
Write-Host ""

# Check if MailHog is already running
Write-Host "Checking if MailHog is already running..." -ForegroundColor Yellow
$mailhogRunning = docker ps --filter "name=squig-mailhog" --format "{{.Names}}" 2>$null

if ($mailhogRunning) {
    Write-Host "MailHog is already running" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "Starting MailHog container..." -ForegroundColor Yellow
    
    docker run -d `
        --name squig-mailhog `
        --network squigleague_squig-network `
        -p 1025:1025 `
        -p 8025:8025 `
        mailhog/mailhog
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to start MailHog" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "MailHog started successfully" -ForegroundColor Green
    Write-Host ""
}

# Update .env.local if it exists
if (Test-Path ".env.local") {
    Write-Host "Checking .env.local configuration..." -ForegroundColor Yellow
    
    $envContent = Get-Content ".env.local" -Raw
    
    $needsUpdate = $false
    if ($envContent -notmatch "SMTP_HOST=mailhog") {
        $needsUpdate = $true
    }
    
    if ($needsUpdate) {
        Write-Host "Updating .env.local with MailHog settings..." -ForegroundColor Yellow
        
        # Backup existing .env.local
        Copy-Item ".env.local" ".env.local.backup" -Force
        
        # Update SMTP settings
        $envContent = $envContent -replace "SMTP_HOST=.*", "SMTP_HOST=mailhog"
        $envContent = $envContent -replace "SMTP_PORT=.*", "SMTP_PORT=1025"
        $envContent = $envContent -replace "SMTP_USERNAME=.*", "SMTP_USERNAME="
        $envContent = $envContent -replace "SMTP_PASSWORD=.*", "SMTP_PASSWORD="
        $envContent = $envContent -replace "SMTP_USE_TLS=.*", "SMTP_USE_TLS=false"
        
        Set-Content ".env.local" $envContent
        
        Write-Host "Updated .env.local (backup saved as .env.local.backup)" -ForegroundColor Green
    } else {
        Write-Host ".env.local already configured for MailHog" -ForegroundColor Green
    }
} else {
    Write-Host "WARNING: .env.local not found" -ForegroundColor Yellow
    Write-Host "Copy .env.local.example to .env.local and configure it" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== MailHog Setup Complete ===" -ForegroundColor Green
Write-Host ""
Write-Host "MailHog Web UI: http://localhost:8025" -ForegroundColor Cyan
Write-Host "SMTP Server: mailhog:1025 (from containers) or localhost:1025 (from host)" -ForegroundColor Cyan
Write-Host ""
Write-Host "To view emails, open: http://localhost:8025" -ForegroundColor Yellow
Write-Host ""

# Open MailHog in browser
$response = Read-Host "Open MailHog web UI in browser? (y/n)"
if ($response -eq 'y' -or $response -eq 'Y') {
    Start-Process "http://localhost:8025"
}
