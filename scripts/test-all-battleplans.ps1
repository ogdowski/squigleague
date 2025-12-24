# Test battle plan generation for all game systems
Write-Host "=== Testing Battle Plan Generation ===" -ForegroundColor Cyan

# Test AoS
Write-Host "`n[AoS] Testing Age of Sigmar battle plans..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost/api/squire/battle-plan/list?game_system=age_of_sigmar" -UseBasicParsing
    $data = $response.Content | ConvertFrom-Json
    Write-Host "  Count: $($data.Count) battle plans" -ForegroundColor $(if ($data.Count -eq 12) { "Green" } else { "Red" })
    if ($data.Count -gt 0) {
        Write-Host "  Sample: $($data[0].name)" -ForegroundColor Cyan
    }
} catch {
    Write-Host "  ERROR: Failed to fetch AoS battle plans" -ForegroundColor Red
}

# Test 40K
Write-Host "`n[40K] Testing Warhammer 40,000 battle plans..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost/api/squire/battle-plan/list?game_system=warhammer_40k" -UseBasicParsing
    $data = $response.Content | ConvertFrom-Json
    Write-Host "  Count: $($data.Count) battle plans (should be 9 Leviathan missions)" -ForegroundColor $(if ($data.Count -eq 9) { "Green" } else { "Yellow" })
    if ($data.Count -gt 0) {
        Write-Host "  Sample missions:" -ForegroundColor Cyan
        $data | Select-Object -First 3 | ForEach-Object {
            Write-Host "    - $($_.name)" -ForegroundColor Cyan
        }
    }
} catch {
    Write-Host "  ERROR: Failed to fetch 40K battle plans" -ForegroundColor Red
}

# Test Old World
Write-Host "`n[TOW] Testing The Old World battle plans..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost/api/squire/battle-plan/list?game_system=the_old_world" -UseBasicParsing
    $data = $response.Content | ConvertFrom-Json
    Write-Host "  Count: $($data.Count) battle plans (should be 6 core scenarios)" -ForegroundColor $(if ($data.Count -eq 6) { "Green" } else { "Yellow" })
    if ($data.Count -gt 0) {
        Write-Host "  Sample scenarios:" -ForegroundColor Cyan
        $data | Select-Object -First 3 | ForEach-Object {
            Write-Host "    - $($_.name)" -ForegroundColor Cyan
        }
    }
} catch {
    Write-Host "  ERROR: Failed to fetch Old World battle plans" -ForegroundColor Red
}

Write-Host "`n=== Done ===" -ForegroundColor Cyan
