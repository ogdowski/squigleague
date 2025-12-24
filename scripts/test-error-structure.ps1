# Test what the actual error response looks like
Write-Host "Testing error response structure..." -ForegroundColor Cyan

# Test 1: Wrong password
Write-Host "`n[Test 1] Wrong password - checking response structure" -ForegroundColor Yellow
$badLogin = '{"username_or_email":"alakkhaine","password":"WrongPassword"}'

try {
    Invoke-WebRequest -Uri "http://localhost/api/squire/auth/login" -Method POST -ContentType "application/json" -Body $badLogin -UseBasicParsing
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    Write-Host "Status: $statusCode" -ForegroundColor Yellow
    
    if ($_.Exception.Response) {
        $reader = [System.IO.StreamReader]::new($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "Raw response body:" -ForegroundColor Cyan
        Write-Host $responseBody -ForegroundColor White
        
        try {
            $json = $responseBody | ConvertFrom-Json
            Write-Host "`nParsed JSON structure:" -ForegroundColor Cyan
            Write-Host "Type of detail: $($json.detail.GetType().Name)" -ForegroundColor Yellow
            Write-Host "Detail value: $($json.detail)" -ForegroundColor White
            if ($json.detail -is [PSCustomObject]) {
                Write-Host "Detail properties:" -ForegroundColor Yellow
                $json.detail | Get-Member -MemberType Properties | ForEach-Object {
                    Write-Host "  $($_.Name): $($json.detail.$($_.Name))" -ForegroundColor White
                }
            }
        } catch {
            Write-Host "Could not parse as JSON" -ForegroundColor Red
        }
    }
}

# Test 2: Unverified email
Write-Host "`n[Test 2] Unverified user - checking response structure" -ForegroundColor Yellow
docker exec squig-postgres psql -U squig -d squigleague -c "UPDATE users SET email_verified = false WHERE LOWER(username) = 'alakkhaine';" | Out-Null

try {
    Invoke-WebRequest -Uri "http://localhost/api/squire/auth/login" -Method POST -ContentType "application/json" -Body '{"username_or_email":"alakkhaine","password":"FinFan11"}' -UseBasicParsing
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    Write-Host "Status: $statusCode" -ForegroundColor Yellow
    
    if ($_.Exception.Response) {
        $reader = [System.IO.StreamReader]::new($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "Raw response body:" -ForegroundColor Cyan
        Write-Host $responseBody -ForegroundColor White
    }
}

# Restore verified status
docker exec squig-postgres psql -U squig -d squigleague -c "UPDATE users SET email_verified = true WHERE LOWER(username) = 'alakkhaine';" | Out-Null

Write-Host "`n=== Done ===" -ForegroundColor Cyan
