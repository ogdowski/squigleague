# Test login with correct field name (username_or_email)
Write-Host "Testing login with corrected field name..." -ForegroundColor Cyan

# Test with username
$loginBody = @{
    username_or_email = "Alakkhaine"
    password = "FinFan11"
} | ConvertTo-Json

try {
    $response = Invoke-WebRequest -Uri "http://localhost/api/squire/auth/login" `
        -Method POST `
        -ContentType "application/json" `
        -Body $loginBody `
        -UseBasicParsing
    
    if ($response.StatusCode -eq 200) {
        Write-Host "SUCCESS: Login successful!" -ForegroundColor Green
        $content = $response.Content | ConvertFrom-Json
        Write-Host "Response: $($content | ConvertTo-Json -Depth 3)" -ForegroundColor Green
    }
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    Write-Host "FAILED: Login failed, Status: $statusCode" -ForegroundColor Red
    
    if ($_.Exception.Response) {
        $reader = [System.IO.StreamReader]::new($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "Error response: $responseBody" -ForegroundColor Yellow
    }
}

Write-Host "`nDone!" -ForegroundColor Cyan
