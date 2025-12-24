# Test login with detailed error reporting
Write-Host "Testing login with detailed error handling..." -ForegroundColor Cyan

$loginBody = @{
    username_or_email = "Alakkhaine"
    password = "FinFan11"
} | ConvertTo-Json

Write-Host "Request body: $loginBody" -ForegroundColor Yellow

try {
    $response = Invoke-WebRequest -Uri "http://localhost/api/squire/auth/login" `
        -Method POST `
        -ContentType "application/json" `
        -Body $loginBody `
        -UseBasicParsing
    
    if ($response.StatusCode -eq 200) {
        Write-Host "SUCCESS: Login successful!" -ForegroundColor Green
        $content = $response.Content | ConvertFrom-Json
        Write-Host "JWT Token received: $($content.token.Substring(0, 20))..." -ForegroundColor Green
        Write-Host "Full response:" -ForegroundColor Green
        Write-Host ($content | ConvertTo-Json -Depth 3) -ForegroundColor Green
    }
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    Write-Host "FAILED: Login failed, Status: $statusCode" -ForegroundColor Red
    
    if ($_.Exception.Response) {
        $reader = [System.IO.StreamReader]::new($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "Error response body:" -ForegroundColor Yellow
        Write-Host $responseBody -ForegroundColor Yellow
        
        try {
            $errorJson = $responseBody | ConvertFrom-Json
            Write-Host "`nParsed error:" -ForegroundColor Yellow
            Write-Host ($errorJson | ConvertTo-Json -Depth 3) -ForegroundColor Yellow
        } catch {
            Write-Host "Could not parse error as JSON" -ForegroundColor Red
        }
    }
}

Write-Host "`nDone!" -ForegroundColor Cyan
