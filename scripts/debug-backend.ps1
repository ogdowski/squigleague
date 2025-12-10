Write-Host "Checking what's listening on port 8000..." -ForegroundColor Cyan
netstat -ano | Select-String ":8000"

Write-Host "`nTrying direct HTTP test..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/squire/health" -UseBasicParsing -TimeoutSec 5
    Write-Host "Success: $($response.StatusCode)" -ForegroundColor Green
    Write-Host $response.Content
} catch {
    Write-Host "Failed: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.ErrorDetails) {
        Write-Host "Details: $($_.ErrorDetails.Message)" -ForegroundColor Yellow
    }
}
