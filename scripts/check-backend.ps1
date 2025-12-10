try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health"
    Write-Host "Backend is running: $($health | ConvertTo-Json)" -ForegroundColor Green
} catch {
    Write-Host "Backend is NOT running" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)"
}
