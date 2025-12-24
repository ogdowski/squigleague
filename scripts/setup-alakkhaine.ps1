# Create and verify Alakkhaine user
Write-Host "=== Creating Alakkhaine User ===" -ForegroundColor Cyan

Write-Host "`n[1] Registering user..." -ForegroundColor Yellow
$registerBody = @{
    username = "Alakkhaine"
    email = "alakkhaine@example.com"
    password = "FinFan11"
} | ConvertTo-Json

try {
    $response = Invoke-WebRequest -Uri "http://localhost/api/squire/auth/register" `
        -Method POST `
        -ContentType "application/json" `
        -Body $registerBody `
        -UseBasicParsing
    
    Write-Host "  Registration successful!" -ForegroundColor Green
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    if ($statusCode -eq 400) {
        Write-Host "  User already exists, continuing..." -ForegroundColor Yellow
    } else {
        Write-Host "  Registration failed: Status $statusCode" -ForegroundColor Red
    }
}

Write-Host "`n[2] Verifying email in database..." -ForegroundColor Yellow
docker exec squig-postgres psql -U squig -d squigleague -c "UPDATE users SET email_verified = true WHERE username = 'Alakkhaine';" | Out-Null
$result = docker exec squig-postgres psql -U squig -d squigleague -c "SELECT username, email, email_verified FROM users WHERE username = 'Alakkhaine';"
Write-Host $result

Write-Host "`n[3] Testing login..." -ForegroundColor Yellow
$loginBody = '{"username_or_email":"Alakkhaine","password":"FinFan11"}'

try {
    $response = Invoke-WebRequest -Uri "http://localhost/api/squire/auth/login" `
        -Method POST `
        -ContentType "application/json" `
        -Body $loginBody `
        -UseBasicParsing
    
    $content = $response.Content | ConvertFrom-Json
    Write-Host "`n  SUCCESS: Login works!" -ForegroundColor Green
    Write-Host "  Token received: $($content.access_token.Substring(0, 30))..." -ForegroundColor Green
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    Write-Host "`n  FAILED: Status $statusCode" -ForegroundColor Red
}

Write-Host "`n=== Done ===" -ForegroundColor Cyan
Write-Host "You can now login at: http://localhost/squire/login" -ForegroundColor White
Write-Host "Username: Alakkhaine" -ForegroundColor White
Write-Host "Password: FinFan11" -ForegroundColor White
