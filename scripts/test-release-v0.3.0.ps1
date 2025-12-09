# Release v0.3.0 Testing Activity Script
# Tests matchup system with battle plan generation end-to-end

Write-Host "`n==================================================================" -ForegroundColor Cyan
Write-Host "RELEASE v0.3.0 TESTING - AoS Matchup System" -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan

# Configuration
$baseUrl = "http://localhost:8000"
$apiPrefix = "/api/squire"

# Test counters
$testsPassed = 0
$testsFailed = 0

function Test-Endpoint {
    param(
        [string]$Name,
        [scriptblock]$Test
    )
    
    Write-Host "`n--- TEST: $Name ---" -ForegroundColor Yellow
    try {
        & $Test
        $script:testsPassed++
        Write-Host "[PASS] $Name" -ForegroundColor Green
        return $true
    } catch {
        $script:testsFailed++
        Write-Host "[FAIL] $Name" -ForegroundColor Red
        Write-Host "Error: $_" -ForegroundColor Red
        return $false
    }
}

# TEST 1: Health Check
Test-Endpoint "Backend Health Check" {
    $response = Invoke-WebRequest -Uri "$baseUrl/health" -UseBasicParsing
    $data = $response.Content | ConvertFrom-Json
    Write-Host "Status: $($data.status)"
    Write-Host "Module: $($data.module)"
    if ($response.StatusCode -ne 200) {
        throw "Health check failed"
    }
}

# TEST 2: Battle Plan Generation
Test-Endpoint "Battle Plan Random Generation" {
    $response = Invoke-WebRequest -Uri "$baseUrl$apiPrefix/battle-plan/random?system=age_of_sigmar" -UseBasicParsing
    $battlePlan = $response.Content | ConvertFrom-Json
    Write-Host "Mission: $($battlePlan.name)"
    Write-Host "Deployment: $($battlePlan.deployment)"
    Write-Host "Objectives: $($battlePlan.primary_objective)"
    if (-not $battlePlan.name) {
        throw "Battle plan missing name"
    }
}

# TEST 3: Systems List
Test-Endpoint "Game Systems Endpoint" {
    $response = Invoke-WebRequest -Uri "$baseUrl$apiPrefix/systems" -UseBasicParsing
    $systems = $response.Content | ConvertFrom-Json
    $aos = $systems | Where-Object { $_.game_system -eq "age_of_sigmar" }
    Write-Host "Found $($systems.Count) game systems"
    Write-Host "AoS Deployment Types: $($aos.deployments.Count)"
    Write-Host "Deployments: $($aos.deployments -join ', ')"
    # Note: There are 12 missions but only 3 unique deployment types
    if ($aos.deployments.Count -lt 1) {
        throw "Expected at least 1 AoS deployment type, got $($aos.deployments.Count)"
    }
}

# TEST 4: Create Matchup
$matchupId = $null
Test-Endpoint "Create New Matchup" {
    $body = @{ game_system = "age_of_sigmar" } | ConvertTo-Json
    $response = Invoke-WebRequest -Uri "$baseUrl$apiPrefix/matchup/create" -Method POST -Body $body -ContentType "application/json" -UseBasicParsing
    $matchup = $response.Content | ConvertFrom-Json
    $script:matchupId = $matchup.matchup_id
    Write-Host "Matchup ID: $matchupId"
    Write-Host "Share URL: $($matchup.share_url)"
    if (-not $matchupId) {
        throw "Matchup ID not generated"
    }
}

# TEST 5: First Player Submission
Test-Endpoint "Submit First Player List" {
    if (-not $matchupId) {
        throw "No matchup ID from previous test"
    }
    
    $body = @{
        player_name = "Alice"
        army_list = @"
Stormcast Eternals - 2000pts

Lord-Imperatant (General)
3x Vindictors
5x Liberators
"@
    } | ConvertTo-Json
    
    $response = Invoke-WebRequest -Uri "$baseUrl$apiPrefix/matchup/$matchupId/submit" -Method POST -Body $body -ContentType "application/json" -UseBasicParsing
    $data = $response.Content | ConvertFrom-Json
    
    Write-Host "Complete: $($data.is_complete)"
    Write-Host "Waiting: $($data.waiting_count)"
    
    if ($data.is_complete) {
        throw "Matchup should not be complete after first submission"
    }
    if ($data.waiting_count -ne 1) {
        throw "Expected waiting_count=1, got $($data.waiting_count)"
    }
}

# TEST 6: Second Player Submission (Triggers Battle Plan)
Test-Endpoint "Submit Second Player List - Battle Plan Generation" {
    if (-not $matchupId) {
        throw "No matchup ID from previous test"
    }
    
    $body = @{
        player_name = "Bob"
        army_list = @"
Lumineth Realm-lords - 2000pts

Scinari Cathallar (General)
10x Vanari Auralan Wardens
5x Vanari Dawnriders
"@
    } | ConvertTo-Json
    
    $response = Invoke-WebRequest -Uri "$baseUrl$apiPrefix/matchup/$matchupId/submit" -Method POST -Body $body -ContentType "application/json" -UseBasicParsing
    $data = $response.Content | ConvertFrom-Json
    
    Write-Host "Complete: $($data.is_complete)"
    Write-Host "Player 1: $($data.player1.name)"
    Write-Host "Player 2: $($data.player2.name)"
    Write-Host "Battle Plan: $($data.battle_plan.name)"
    
    if (-not $data.is_complete) {
        throw "Matchup should be complete after second submission"
    }
    if (-not $data.battle_plan) {
        throw "Battle plan should be generated"
    }
    if ($data.player1.name -ne "Alice") {
        throw "Player 1 name mismatch"
    }
    if ($data.player2.name -ne "Bob") {
        throw "Player 2 name mismatch"
    }
}

# TEST 7: Retrieve Complete Matchup
Test-Endpoint "Retrieve Complete Matchup" {
    if (-not $matchupId) {
        throw "No matchup ID from previous test"
    }
    
    $response = Invoke-WebRequest -Uri "$baseUrl$apiPrefix/matchup/$matchupId" -UseBasicParsing
    $data = $response.Content | ConvertFrom-Json
    
    Write-Host "Matchup ID: $($data.matchup_id)"
    Write-Host "Complete: $($data.is_complete)"
    Write-Host "Both Lists Visible: $($data.player1 -and $data.player2)"
    Write-Host "Battle Plan: $($data.battle_plan.name)"
    
    if (-not $data.player1.army_list) {
        throw "Player 1 army list should be visible"
    }
    if (-not $data.player2.army_list) {
        throw "Player 2 army list should be visible"
    }
}

# TEST 8: Multiple Battle Plans
Test-Endpoint "Generate Multiple Battle Plans" {
    $response = Invoke-WebRequest -Uri "$baseUrl$apiPrefix/battle-plan/multiple?system=age_of_sigmar&count=5" -UseBasicParsing
    $plans = $response.Content | ConvertFrom-Json
    
    Write-Host "Generated $($plans.Count) battle plans"
    foreach ($plan in $plans) {
        Write-Host "  - $($plan.name)"
    }
    
    if ($plans.Count -ne 5) {
        throw "Expected 5 battle plans, got $($plans.Count)"
    }
}

# Summary
Write-Host "`n==================================================================" -ForegroundColor Cyan
Write-Host "TEST SUMMARY" -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "Passed: $testsPassed" -ForegroundColor Green
Write-Host "Failed: $testsFailed" -ForegroundColor Red
Write-Host "Total:  $($testsPassed + $testsFailed)" -ForegroundColor Yellow

if ($testsFailed -eq 0) {
    Write-Host "`nALL TESTS PASSED - Release v0.3.0 is ready!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "`nSOME TESTS FAILED - Release NOT ready" -ForegroundColor Red
    exit 1
}
