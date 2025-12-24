# show-status.ps1
# Shows comprehensive status of SquigLeague system

Write-Host "=== SquigLeague System Status ===" -ForegroundColor Cyan
Write-Host ""

# Container Status
Write-Host "[Containers]" -ForegroundColor Yellow
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | Out-String | Write-Host

# Recent Runner Activity
Write-Host "`n[Recent Activity Script Executions]" -ForegroundColor Yellow
if (Test-Path scripts\runner.log) {
    Get-Content scripts\runner.log -Tail 10 | ForEach-Object {
        if ($_ -match "SUCCESS") {
            Write-Host $_ -ForegroundColor Green
        } elseif ($_ -match "REFUSED|FAIL") {
            Write-Host $_ -ForegroundColor Red
        } elseif ($_ -match "EXECUTE") {
            Write-Host $_ -ForegroundColor Cyan
        } else {
            Write-Host $_ -ForegroundColor Gray
        }
    }
} else {
    Write-Host "  No activity log found" -ForegroundColor Gray
}

# Approved Scripts Count
Write-Host "`n[Approved Activity Scripts]" -ForegroundColor Yellow
if (Test-Path scripts\allowed-scripts.json) {
    $whitelist = Get-Content scripts\allowed-scripts.json -Raw | ConvertFrom-Json
    $count = ($whitelist.scripts.PSObject.Properties | Measure-Object).Count
    Write-Host "  Total approved: $count scripts" -ForegroundColor Green
    Write-Host "  Last updated: $($whitelist.generated)" -ForegroundColor Gray
} else {
    Write-Host "  Whitelist not found" -ForegroundColor Red
}

# Service URLs
Write-Host "`n[Service URLs]" -ForegroundColor Yellow
Write-Host "  Backend API:    http://localhost:8000" -ForegroundColor White
Write-Host "  API Docs:       http://localhost:8000/docs" -ForegroundColor White
Write-Host "  Frontend:       http://localhost:8080" -ForegroundColor White
Write-Host "  MailHog:        http://localhost:8025" -ForegroundColor White

# Quick Health Checks
Write-Host "`n[Quick Health Check]" -ForegroundColor Yellow
$checks = @(
    @{Name="Backend API"; URL="http://localhost:8000/api/squire/health"},
    @{Name="MailHog"; URL="http://localhost:8025"}
)

foreach ($check in $checks) {
    try {
        $response = Invoke-WebRequest -Uri $check.URL -UseBasicParsing -TimeoutSec 2
        Write-Host "  ✓ $($check.Name): $($response.StatusCode)" -ForegroundColor Green
    } catch {
        Write-Host "  ✗ $($check.Name): Not responding" -ForegroundColor Red
    }
}

Write-Host "`n[Enforcement Status]" -ForegroundColor Yellow
$enforcements = @(
    @{Name="Runner Script"; Path=".github\copilot-instructions.md"},
    @{Name="Copilot Instructions"; Path="scripts\runner.ps1"},
    @{Name="Whitelist"; Path="scripts\allowed-scripts.json"},
    @{Name="Documentation"; Path="scripts\README.md"}
)

foreach ($enforce in $enforcements) {
    if (Test-Path $enforce.Path) {
        Write-Host "  ✓ $($enforce.Name)" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $($enforce.Name) missing" -ForegroundColor Red
    }
}

Write-Host "`n=== Status Check Complete ===" -ForegroundColor Cyan
