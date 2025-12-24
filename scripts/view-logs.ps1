# view-logs.ps1
# View logs from all containers

param(
    [string]$Container = "all",
    [int]$Lines = 50
)

Write-Host "=== SquigLeague Container Logs ===" -ForegroundColor Cyan
Write-Host ""

if ($Container -eq "all") {
    Write-Host "Showing logs for all containers (last $Lines lines each)" -ForegroundColor Yellow
    Write-Host ""
    
    $containers = @("squig-postgres", "squig", "squig-frontend", "squig-nginx")
    
    foreach ($c in $containers) {
        $running = docker ps --filter "name=$c" --format "{{.Names}}" 2>$null
        if ($running) {
            Write-Host "========== $c ==========" -ForegroundColor Cyan
            docker logs $c --tail $Lines
            Write-Host ""
        }
    }
} else {
    Write-Host "Showing logs for: $Container" -ForegroundColor Yellow
    docker logs $Container --tail $Lines
}

Write-Host ""
Write-Host "To follow logs in real-time, use:" -ForegroundColor Yellow
Write-Host "  docker logs -f <container-name>" -ForegroundColor White
Write-Host ""
Write-Host "Available containers:" -ForegroundColor Yellow
docker ps --format "  {{.Names}}" 2>$null
