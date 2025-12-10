# Test that captures actual API error responses
# This will show us what FastAPI is actually rejecting

$ErrorActionPreference = "Continue"

Write-Host "`n================================================================" -ForegroundColor Cyan
Write-Host "API ERROR DIAGNOSIS TEST" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan

# Test 1: Valid request
Write-Host "`n[TEST 1] Valid request (like automated test)" -ForegroundColor Yellow
$body1 = @{ game_system = "age_of_sigmar" } | ConvertTo-Json
Write-Host "Body: $body1" -ForegroundColor Gray
try {
    $response1 = Invoke-WebRequest -Uri "http://localhost:8000/api/squire/matchup/create" `
        -Method POST `
        -Body $body1 `
        -ContentType "application/json" `
        -UseBasicParsing
    Write-Host "  SUCCESS: $($response1.StatusCode)" -ForegroundColor Green
    Write-Host "  Response: $($response1.Content)" -ForegroundColor Gray
} catch {
    Write-Host "  FAILED: $($_.Exception.Response.StatusCode.value__)" -ForegroundColor Red
    $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
    $responseBody = $reader.ReadToEnd()
    Write-Host "  Error body: $responseBody" -ForegroundColor Red
}

# Test 2: Request with exact fetch options from browser
Write-Host "`n[TEST 2] Request simulating browser fetch()" -ForegroundColor Yellow
$body2 = '{"game_system":"age_of_sigmar"}'
Write-Host "Body: $body2" -ForegroundColor Gray
Write-Host "Content-Type: application/json" -ForegroundColor Gray
try {
    $response2 = Invoke-WebRequest -Uri "http://localhost:8000/api/squire/matchup/create" `
        -Method POST `
        -Body $body2 `
        -ContentType "application/json" `
        -UseBasicParsing
    Write-Host "  SUCCESS: $($response2.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "  FAILED: $($_.Exception.Response.StatusCode.value__)" -ForegroundColor Red
    $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
    $responseBody = $reader.ReadToEnd()
    Write-Host "  Error body: $responseBody" -ForegroundColor Red
}

# Test 3: Check if CORS preflight is the issue
Write-Host "`n[TEST 3] OPTIONS request (CORS preflight)" -ForegroundColor Yellow
try {
    $response3 = Invoke-WebRequest -Uri "http://localhost:8000/api/squire/matchup/create" `
        -Method OPTIONS `
        -Headers @{
            "Origin" = "http://localhost:3000"
            "Access-Control-Request-Method" = "POST"
            "Access-Control-Request-Headers" = "content-type"
        } `
        -UseBasicParsing
    Write-Host "  SUCCESS: $($response3.StatusCode)" -ForegroundColor Green
    Write-Host "  CORS headers:" -ForegroundColor Gray
    $response3.Headers.GetEnumerator() | Where-Object { $_.Key -like "Access-Control-*" } | ForEach-Object {
        Write-Host "    $($_.Key): $($_.Value)" -ForegroundColor Gray
    }
} catch {
    Write-Host "  FAILED: $($_.Exception.Response.StatusCode.value__)" -ForegroundColor Red
    Write-Host "  CORS preflight may be blocked" -ForegroundColor Red
}

# Test 4: POST with Origin header (like browser)
Write-Host "`n[TEST 4] POST with Origin header (browser simulation)" -ForegroundColor Yellow
$body4 = '{"game_system":"age_of_sigmar"}'
try {
    $response4 = Invoke-WebRequest -Uri "http://localhost:8000/api/squire/matchup/create" `
        -Method POST `
        -Body $body4 `
        -ContentType "application/json" `
        -Headers @{ "Origin" = "http://localhost:3000" } `
        -UseBasicParsing
    Write-Host "  SUCCESS: $($response4.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "  FAILED: $($_.Exception.Response.StatusCode.value__)" -ForegroundColor Red
    $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
    $responseBody = $reader.ReadToEnd()
    Write-Host "  Error body: $responseBody" -ForegroundColor Red
}

# Test 5: Check backend logs
Write-Host "`n[TEST 5] Checking backend job logs" -ForegroundColor Yellow
$jobs = Get-Job | Where-Object { $_.Command -like "*uvicorn*" }
if ($jobs) {
    Write-Host "  Found $($jobs.Count) backend job(s)" -ForegroundColor Gray
    foreach ($job in $jobs) {
        $output = Receive-Job -Job $job -Keep | Select-Object -Last 20
        if ($output) {
            Write-Host "  Recent logs:" -ForegroundColor Gray
            $output | ForEach-Object { Write-Host "    $_" -ForegroundColor DarkGray }
        }
    }
} else {
    Write-Host "  No backend jobs found - server may not be running in job" -ForegroundColor Yellow
}

Write-Host "`n================================================================" -ForegroundColor Cyan
Write-Host "DIAGNOSIS COMPLETE" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
