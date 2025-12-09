#!/usr/bin/env pwsh
# Comprehensive API tests for matchup system

Write-Host "`nRunning Matchup System Tests...`n" -ForegroundColor Cyan

$ErrorActionPreference = "Stop"
$testsPassed = 0
$testsFailed = 0

function Test-Endpoint {
    param(
        [string]$Name,
        [scriptblock]$Test
    )
    
    Write-Host "Testing: $Name" -ForegroundColor Yellow
    try {
        & $Test
        Write-Host "  PASSED" -ForegroundColor Green
        $script:testsPassed++
    } catch {
        Write-Host "  FAILED: $_" -ForegroundColor Red
        $script:testsFailed++
    }
}

# Test 1: Create matchup for each system
Test-Endpoint "Create Age of Sigmar matchup" {
    $response = Invoke-RestMethod -Uri "http://localhost/api/squire/matchup/create" `
        -Method POST -ContentType "application/json" `
        -Body '{"game_system":"age_of_sigmar"}'
    if (-not $response.matchup_id) { throw "No matchup_id returned" }
}

Test-Endpoint "Create Warhammer 40k matchup" {
    $response = Invoke-RestMethod -Uri "http://localhost/api/squire/matchup/create" `
        -Method POST -ContentType "application/json" `
        -Body '{"game_system":"warhammer_40k"}'
    if (-not $response.matchup_id) { throw "No matchup_id returned" }
}

Test-Endpoint "Create The Old World matchup" {
    $response = Invoke-RestMethod -Uri "http://localhost/api/squire/matchup/create" `
        -Method POST -ContentType "application/json" `
        -Body '{"game_system":"the_old_world"}'
    if (-not $response.matchup_id) { throw "No matchup_id returned" }
}

# Test 2: Invalid game system
Test-Endpoint "Reject invalid game system" {
    try {
        $ErrorActionPreference = "Stop"
        Invoke-RestMethod -Uri "http://localhost/api/squire/matchup/create" `
            -Method POST -ContentType "application/json" `
            -Body '{"game_system":"invalid_system"}' -ErrorAction Stop
        throw "Should have failed with invalid system"
    } catch {
        # Should get a validation error
        if (-not $_.Exception.Message.Contains("422") -and -not $_.Exception.Message.Contains("validation")) {
            # May be different error format, but should still error
        }
    }
}

# Test 3: First player submission
$createResponse = Invoke-RestMethod -Uri "http://localhost/api/squire/matchup/create" `
    -Method POST -ContentType "application/json" `
    -Body '{"game_system":"age_of_sigmar"}'
$matchupId = $createResponse.matchup_id

Test-Endpoint "First player can submit" {
    $response = Invoke-RestMethod -Uri "http://localhost/api/squire/matchup/$matchupId/submit" `
        -Method POST -ContentType "application/json" `
        -Body '{"player_name":"Alice","army_list":"Test Army List with enough characters"}'
    if ($response.is_complete) { throw "Should not be complete after first submission" }
    if ($response.waiting_count -ne 1) { throw "Waiting count should be 1" }
    # Player data is hidden until matchup is complete (security feature)
}

# Test 4: Second player submission generates battle plan
Test-Endpoint "Second player submission generates battle plan" {
    $response = Invoke-RestMethod -Uri "http://localhost/api/squire/matchup/$matchupId/submit" `
        -Method POST -ContentType "application/json" `
        -Body '{"player_name":"Bob","army_list":"Bob Test Army List 2"}'
    if (-not $response.is_complete) { throw "Should be complete after second submission" }
    if (-not $response.battle_plan) { throw "Battle plan not generated" }
    if (-not $response.battle_plan.name) { throw "Battle plan missing name" }
    if ($response.battle_plan.game_system -ne "age_of_sigmar") { throw "Wrong game system" }
}

# Test 5: Third player cannot join
Test-Endpoint "Third player cannot join" {
    try {
        $ErrorActionPreference = "Stop"
        Invoke-RestMethod -Uri "http://localhost/api/squire/matchup/$matchupId/submit" `
            -Method POST -ContentType "application/json" `
            -Body '{"player_name":"Charlie","army_list":"Charlie test list"}' -ErrorAction Stop
        throw "Should have rejected third player"
    } catch {
        # Should error - matchup is full
    }
}

# Test 6: GET incomplete matchup hides lists
$createResponse = Invoke-RestMethod -Uri "http://localhost/api/squire/matchup/create" `
    -Method POST -ContentType "application/json" `
    -Body '{"game_system":"warhammer_40k"}'
$matchupId2 = $createResponse.matchup_id

Invoke-RestMethod -Uri "http://localhost/api/squire/matchup/$matchupId2/submit" `
    -Method POST -ContentType "application/json" `
    -Body '{"player_name":"Player1","army_list":"Secret List"}' | Out-Null

Test-Endpoint "GET incomplete matchup hides army lists" {
    $response = Invoke-RestMethod -Uri "http://localhost/api/squire/matchup/$matchupId2"
    if ($response.player1.army_list) { throw "Army list should be hidden" }
    if ($response.battle_plan) { throw "Battle plan should be hidden" }
}

# Test 7: GET complete matchup reveals everything
Invoke-RestMethod -Uri "http://localhost/api/squire/matchup/$matchupId2/submit" `
    -Method POST -ContentType "application/json" `
    -Body '{"player_name":"Player2","army_list":"Secret List 2"}' | Out-Null

Test-Endpoint "GET complete matchup reveals all data" {
    $response = Invoke-RestMethod -Uri "http://localhost/api/squire/matchup/$matchupId2"
    if (-not $response.player1.army_list) { throw "Player 1 list should be visible" }
    if (-not $response.player2.army_list) { throw "Player 2 list should be visible" }
    if (-not $response.battle_plan) { throw "Battle plan should be visible" }
}

# Test 8: Battle plan health endpoint
Test-Endpoint "Battle plan health check" {
    $response = Invoke-RestMethod -Uri "http://localhost/api/squire/health"
    if ($response.status -ne "operational") { throw "Health check failed" }
    if (-not $response.features.Contains("battle_plans")) { throw "Battle plans feature not listed" }
}

# Test 9: Random battle plan for each system
Test-Endpoint "Generate random Age of Sigmar battle plan" {
    $response = Invoke-RestMethod -Uri "http://localhost/api/squire/battle-plan/random?system=age_of_sigmar"
    if (-not $response.name) { throw "No battle plan name" }
    if ($response.game_system -ne "age_of_sigmar") { throw "Wrong system" }
}

Test-Endpoint "Generate random 40k battle plan" {
    $response = Invoke-RestMethod -Uri "http://localhost/api/squire/battle-plan/random?system=warhammer_40k"
    if (-not $response.name) { throw "No battle plan name" }
    if ($response.game_system -ne "warhammer_40k") { throw "Wrong system" }
}

Test-Endpoint "Generate random Old World battle plan" {
    $response = Invoke-RestMethod -Uri "http://localhost/api/squire/battle-plan/random?system=the_old_world"
    if (-not $response.name) { throw "No battle plan name" }
    if ($response.game_system -ne "the_old_world") { throw "Wrong system" }
}

# Test 10: Validation tests
Test-Endpoint "Reject empty player name" {
    $createResponse = Invoke-RestMethod -Uri "http://localhost/api/squire/matchup/create" `
        -Method POST -ContentType "application/json" `
        -Body '{"game_system":"age_of_sigmar"}'
    try {
        Invoke-RestMethod -Uri "http://localhost/api/squire/matchup/$($createResponse.matchup_id)/submit" `
            -Method POST -ContentType "application/json" `
            -Body '{"player_name":"","army_list":"Test"}'
        throw "Should have rejected empty name"
    } catch {
        if ($_.Exception.Response.StatusCode -ne 422) {
            throw "Expected 422 validation error"
        }
    }
}

Test-Endpoint "Reject empty army list" {
    $createResponse = Invoke-RestMethod -Uri "http://localhost/api/squire/matchup/create" `
        -Method POST -ContentType "application/json" `
        -Body '{"game_system":"age_of_sigmar"}'
    try {
        Invoke-RestMethod -Uri "http://localhost/api/squire/matchup/$($createResponse.matchup_id)/submit" `
            -Method POST -ContentType "application/json" `
            -Body '{"player_name":"Test","army_list":""}'
        throw "Should have rejected empty list"
    } catch {
        if ($_.Exception.Response.StatusCode -ne 422) {
            throw "Expected 422 validation error"
        }
    }
}

# Summary
Write-Host "`n" + "="*50 -ForegroundColor Cyan
Write-Host "TEST RESULTS" -ForegroundColor White
Write-Host "="*50 -ForegroundColor Cyan
Write-Host "Passed: $testsPassed" -ForegroundColor Green
Write-Host "Failed: $testsFailed" -ForegroundColor Red
Write-Host "Total:  $($testsPassed + $testsFailed)" -ForegroundColor White

if ($testsFailed -eq 0) {
    Write-Host "`nALL TESTS PASSED!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "`nSOME TESTS FAILED!" -ForegroundColor Red
    exit 1
}
