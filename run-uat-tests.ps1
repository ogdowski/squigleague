# Squig League - UAT Test Suite for Battle Plan Randomizer
# Tests all functionality needed for User Acceptance Testing

param(
    [string]$BaseUrl = "http://localhost:8000",
    [int]$SampleSize = 50
)

$ErrorActionPreference = "Continue"
$results = @()

Write-Host "`n" -NoNewline
Write-Host "######################################################################" -ForegroundColor Cyan
Write-Host "# SQUIRE MODULE - UAT TEST SUITE" -ForegroundColor Cyan
Write-Host "# Testing General's Handbook 2025-2026 Battle Plans" -ForegroundColor Cyan
Write-Host "# Battle Plan Randomizer for Age of Sigmar" -ForegroundColor Cyan
Write-Host "######################################################################" -ForegroundColor Cyan
Write-Host ""

# Test 1: API Health Check
Write-Host "======================================================================" -ForegroundColor White
Write-Host "TEST 1: API Health Check" -ForegroundColor White
Write-Host "======================================================================" -ForegroundColor White

try {
    $health = Invoke-RestMethod -Uri "$BaseUrl/api/squire/health" -Headers @{"User-Agent"="Squire-UAT/1.0"} -TimeoutSec 5
    Write-Host "✅ API is operational" -ForegroundColor Green
    Write-Host "   Module: $($health.module)" -ForegroundColor Gray
    Write-Host "   Status: $($health.status)" -ForegroundColor Gray
    Write-Host "   Version: $($health.version)" -ForegroundColor Gray
    $results += @{Name="API Health"; Passed=$true}
} catch {
    Write-Host "❌ API Health check failed: $_" -ForegroundColor Red
    $results += @{Name="API Health"; Passed=$false}
    Write-Host "`n⚠️  Cannot continue without API. Exiting.`n" -ForegroundColor Yellow
    exit 1
}

# Test 2: Age of Sigmar Mission Coverage
Write-Host "`n======================================================================" -ForegroundColor White
Write-Host "TEST 2: Age of Sigmar Mission Coverage (12 Official Missions)" -ForegroundColor White
Write-Host "======================================================================" -ForegroundColor White

$expectedMissions = @(
    "Passing Seasons",
    "Paths of the Fey",
    "Roiling Roots",
    "Cyclic Shifts",
    "Surge of Slaughter",
    "Linked Ley Lines",
    "Noxious Nexus",
    "The Liferoots",
    "Bountiful Equinox",
    "Lifecycle",
    "Creeping Corruption",
    "Grasp of Thorns"
)

$foundMissions = @{}
$missionDetails = @{}

Write-Host "Generating $SampleSize random missions to verify all 12 are present..." -ForegroundColor Gray

for ($i = 1; $i -le $SampleSize; $i++) {
    try {
        $plan = Invoke-RestMethod -Uri "$BaseUrl/api/squire/battle-plan/random?system=age_of_sigmar" -Headers @{"User-Agent"="Squire-UAT/1.0"} -TimeoutSec 5
        $missionName = $plan.name
        $foundMissions[$missionName] = $true
        if (-not $missionDetails.ContainsKey($missionName)) {
            $missionDetails[$missionName] = $plan
        }
        if ($i % 10 -eq 0) {
            Write-Host "   Generated $i/$SampleSize (found $($foundMissions.Count) unique missions)..." -ForegroundColor Gray
        }
    } catch {
        Write-Host "❌ Request $i failed: $_" -ForegroundColor Red
    }
}

Write-Host "`n✅ Found $($foundMissions.Count) unique missions:" -ForegroundColor Green
$foundMissions.Keys | Sort-Object | ForEach-Object { Write-Host "   - $_" -ForegroundColor White }

$missing = $expectedMissions | Where-Object { -not $foundMissions.ContainsKey($_) }
$extra = $foundMissions.Keys | Where-Object { $_ -notin $expectedMissions }

if ($missing.Count -gt 0) {
    Write-Host "`n❌ Missing missions:" -ForegroundColor Red
    $missing | ForEach-Object { Write-Host "   - $_" -ForegroundColor Red }
    $results += @{Name="Mission Coverage"; Passed=$false}
} elseif ($extra.Count -gt 0) {
    Write-Host "`n⚠️  Unexpected missions:" -ForegroundColor Yellow
    $extra | ForEach-Object { Write-Host "   - $_" -ForegroundColor Yellow }
    $results += @{Name="Mission Coverage"; Passed=$true}
} else {
    Write-Host "`n✅ All 12 official missions found!" -ForegroundColor Green
    $results += @{Name="Mission Coverage"; Passed=$true}
}

# Test 3: Mission Data Integrity
Write-Host "`n======================================================================" -ForegroundColor White
Write-Host "TEST 3: Mission Data Integrity" -ForegroundColor White
Write-Host "======================================================================" -ForegroundColor White

$dataIntegrityPassed = $true
$foundMissions.Keys | ForEach-Object {
    $mission = $missionDetails[$_]
    $issues = @()
    
    if (-not $mission.name) { $issues += "Missing name" }
    if (-not $mission.deployment) { $issues += "Missing deployment" }
    if (-not $mission.deployment_description) { $issues += "Missing deployment_description" }
    if (-not $mission.primary_objective) { $issues += "Missing primary_objective" }
    if (-not $mission.victory_conditions) { $issues += "Missing victory_conditions" }
    if ($mission.turn_limit -le 0) { $issues += "Invalid turn_limit" }
    
    if ($issues.Count -gt 0) {
        Write-Host "❌ $($mission.name):" -ForegroundColor Red
        $issues | ForEach-Object { Write-Host "   - $_" -ForegroundColor Red }
        $dataIntegrityPassed = $false
    } else {
        Write-Host "✅ $($mission.name) - All required fields present" -ForegroundColor Green
    }
}

$results += @{Name="Mission Data Integrity"; Passed=$dataIntegrityPassed}

# Test 4: Tournament Mode (Multiple Plans)
Write-Host "`n======================================================================" -ForegroundColor White
Write-Host "TEST 4: Tournament Mode - Multiple Battle Plans" -ForegroundColor White
Write-Host "======================================================================" -ForegroundColor White

try {
    $tournamentPlans = @()
    Write-Host "Generating 5 battle plans for tournament..." -ForegroundColor Gray
    
    for ($i = 1; $i -le 5; $i++) {
        $plan = Invoke-RestMethod -Uri "$BaseUrl/api/squire/battle-plan/random?system=age_of_sigmar" -Headers @{"User-Agent"="Squire-UAT/1.0"} -TimeoutSec 5
        $tournamentPlans += $plan
        Write-Host "   Round $i : $($plan.name)" -ForegroundColor White
    }
    
    Write-Host "`n✅ Tournament mode test passed" -ForegroundColor Green
    $results += @{Name="Tournament Mode"; Passed=$true}
} catch {
    Write-Host "❌ Tournament mode test failed: $_" -ForegroundColor Red
    $results += @{Name="Tournament Mode"; Passed=$false}
}

# Test 5: Game Systems Endpoint
Write-Host "`n======================================================================" -ForegroundColor White
Write-Host "TEST 5: Game Systems Information Endpoint" -ForegroundColor White
Write-Host "======================================================================" -ForegroundColor White

try {
    $systems = Invoke-RestMethod -Uri "$BaseUrl/api/squire/systems" -Headers @{"User-Agent"="Squire-UAT/1.0"} -TimeoutSec 5
    Write-Host "✅ Systems endpoint accessible" -ForegroundColor Green
    Write-Host "`nSupported Systems:" -ForegroundColor Cyan
    $systems | ForEach-Object {
        Write-Host "   • $($_.game_system)" -ForegroundColor White
        Write-Host "     Description: $($_.description)" -ForegroundColor Gray
        Write-Host "     Deployments: $($_.deployments -join ', ')" -ForegroundColor Gray
    }
    $results += @{Name="Systems Endpoint"; Passed=$true}
} catch {
    Write-Host "❌ Systems endpoint test failed: $_" -ForegroundColor Red
    $results += @{Name="Systems Endpoint"; Passed=$false}
}

# Test 6: Sample Battle Plan Display
Write-Host "`n======================================================================" -ForegroundColor White
Write-Host "TEST 6: Sample Battle Plan Full Details" -ForegroundColor White
Write-Host "======================================================================" -ForegroundColor White

try {
    $sample = Invoke-RestMethod -Uri "$BaseUrl/api/squire/battle-plan/random?system=age_of_sigmar" -Headers @{"User-Agent"="Squire-UAT/1.0"} -TimeoutSec 5
    
    Write-Host "`n$($sample.name)" -ForegroundColor Cyan
    Write-Host "---------------------------------------------------------------------" -ForegroundColor DarkGray
    Write-Host "Game System:  $($sample.game_system)" -ForegroundColor White
    Write-Host "Deployment:   $($sample.deployment_description)" -ForegroundColor White
    Write-Host "Turn Limit:   $($sample.turn_limit) rounds" -ForegroundColor White
    Write-Host ""
    Write-Host "Primary Objective:" -ForegroundColor Yellow
    Write-Host "  $($sample.primary_objective)" -ForegroundColor White
    Write-Host ""
    Write-Host "Victory Conditions:" -ForegroundColor Yellow
    Write-Host "  $($sample.victory_conditions)" -ForegroundColor White
    
    if ($sample.special_rules -and $sample.special_rules.Count -gt 0) {
        Write-Host ""
        Write-Host "Special Rules:" -ForegroundColor Yellow
        $sample.special_rules | ForEach-Object { Write-Host "  - $_" -ForegroundColor White }
    }
    
    if ($sample.secondary_objectives -and $sample.secondary_objectives.Count -gt 0) {
        Write-Host ""
        Write-Host "Secondary Objectives:" -ForegroundColor Yellow
        $sample.secondary_objectives | ForEach-Object { Write-Host "  - $_" -ForegroundColor White }
    }
    
    Write-Host ""
    $results += @{Name="Sample Display"; Passed=$true}
} catch {
    Write-Host "Failed: $_" -ForegroundColor Red
    $results += @{Name="Sample Display"; Passed=$false}
}

# Summary
Write-Host "`n======================================================================" -ForegroundColor White
Write-Host "UAT TEST SUMMARY" -ForegroundColor White
Write-Host "======================================================================" -ForegroundColor White

$passed = ($results | Where-Object { $_.Passed -eq $true }).Count
$total = $results.Count

$results | ForEach-Object {
    $status = if ($_.Passed) { "✅ PASS" } else { "❌ FAIL" }
    $color = if ($_.Passed) { "Green" } else { "Red" }
    Write-Host "$status : $($_.Name)" -ForegroundColor $color
}

Write-Host "`nTotal: $passed/$total tests passed" -ForegroundColor $(if ($passed -eq $total) { "Green" } else { "Yellow" })

if ($passed -eq $total) {
    Write-Host "`nAll UAT tests passed! Battle Plan Randomizer is ready for deployment." -ForegroundColor Green
    Write-Host ""
    exit 0
} else {
    Write-Host "`nSome UAT tests failed. Review output above for details." -ForegroundColor Yellow
    Write-Host ""
    exit 1
}
