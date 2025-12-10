$processes = Get-Process python -ErrorAction SilentlyContinue
if ($processes) {
    Write-Host "Python processes running:" -ForegroundColor Green
    $processes | Format-Table Id, ProcessName, StartTime
} else {
    Write-Host "No Python processes found" -ForegroundColor Red
}

Write-Host "`nChecking port 8000..." -ForegroundColor Cyan
$connection = Test-NetConnection -ComputerName localhost -Port 8000 -WarningAction SilentlyContinue
if ($connection.TcpTestSucceeded) {
    Write-Host "Port 8000 is open" -ForegroundColor Green
} else {
    Write-Host "Port 8000 is NOT open" -ForegroundColor Red
}
