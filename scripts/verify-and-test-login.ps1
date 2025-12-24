# Verify email for Alakkhaine user
Write-Host "=== Email Verification for Alakkhaine ===" -ForegroundColor Cyan

Write-Host "`nUpdating database to mark email as verified..." -ForegroundColor Yellow
$result = docker exec squig-postgres psql -U squig -d squigleague -c "UPDATE users SET email_verified = true WHERE username = 'Alakkhaine'; SELECT username, email, email_verified FROM users WHERE username = 'Alakkhaine';"

Write-Host $result

Write-Host "`n=== Testing Login ===" -ForegroundColor Cyan
$loginBody = '{"username_or_email":"Alakkhaine","password":"FinFan11"}'

try {
    $response = Invoke-WebRequest -Uri "http://localhost/api/squire/auth/login" `
        -Method POST `
        -ContentType "application/json" `
        -Body $loginBody `
        -UseBasicParsing
    
    $content = $response.Content | ConvertFrom-Json
    Write-Host "`nSUCCESS: Login successful!" -ForegroundColor Green
    Write-Host "JWT Token: $($content.access_token.Substring(0, 50))..." -ForegroundColor Green
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    Write-Host "`nFAILED: Status $statusCode" -ForegroundColor Red
    
    if ($_.Exception.Response) {
        $reader = [System.IO.StreamReader]::new($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "Error: $responseBody" -ForegroundColor Yellow
    }
}

Write-Host "`n=== Done ===" -ForegroundColor Cyan
