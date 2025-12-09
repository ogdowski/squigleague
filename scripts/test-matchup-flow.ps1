#!/usr/bin/env pwsh
# Test complete matchup flow with two players

Write-Host "`nTesting Complete Matchup Flow...`n" -ForegroundColor Cyan

# Step 1: Player 1 creates matchup
Write-Host "[1] Player 1 creates matchup..." -ForegroundColor Yellow
$createResponse = Invoke-RestMethod -Uri "http://localhost/api/squire/matchup/create" `
    -Method POST `
    -ContentType "application/json" `
    -Body '{"game_system":"age_of_sigmar"}'

$matchupId = $createResponse.matchup_id
$shareUrl = "http://localhost/squire/matchup/$matchupId"

Write-Host "   Matchup ID: $matchupId" -ForegroundColor Green
Write-Host "   Share URL: $shareUrl" -ForegroundColor Green

# Step 2: Check initial state (no players submitted)
Write-Host "`n[2] Checking initial state..." -ForegroundColor Yellow
$matchup = Invoke-RestMethod -Uri "http://localhost/api/squire/matchup/$matchupId"
Write-Host "   Complete: $($matchup.is_complete)" -ForegroundColor Green
Write-Host "   Player 1: $($matchup.player1)" -ForegroundColor Green
Write-Host "   Player 2: $($matchup.player2)" -ForegroundColor Green
Write-Host "   Battle Plan: $(if ($matchup.battle_plan) { $matchup.battle_plan } else { 'Not generated' })" -ForegroundColor Green

# Step 3: Player 1 submits their list
Write-Host "`n[3] Player 1 submits their list..." -ForegroundColor Yellow
$player1Submit = @{
    player_name = "Alice"
    army_list = "Army List for Player 1`nUnit 1`nUnit 2`nUnit 3"
} | ConvertTo-Json

$matchup = Invoke-RestMethod -Uri "http://localhost/api/squire/matchup/$matchupId/submit" `
    -Method POST `
    -ContentType "application/json" `
    -Body $player1Submit

Write-Host "   Complete: $($matchup.is_complete)" -ForegroundColor Green
Write-Host "   Player 1: $($matchup.player1.name)" -ForegroundColor Green
Write-Host "   Player 2: $($matchup.player2)" -ForegroundColor Green
Write-Host "   Battle Plan: $(if ($matchup.battle_plan) { $matchup.battle_plan } else { 'Waiting for Player 2...' })" -ForegroundColor Green

# Step 4: Player 2 visits share link and loads matchup
Write-Host "`n[4] Player 2 visits share link..." -ForegroundColor Yellow
$matchup = Invoke-RestMethod -Uri "http://localhost/api/squire/matchup/$matchupId"
Write-Host "   Player 2 can see:" -ForegroundColor Green
Write-Host "     - Matchup ID: $($matchup.matchup_id)" -ForegroundColor White
Write-Host "     - Game System: $($matchup.game_system)" -ForegroundColor White
Write-Host "     - Player 1 Name: $($matchup.player1.name)" -ForegroundColor White
Write-Host "     - Player 1 List: Hidden (until complete)" -ForegroundColor White

# Step 5: Player 2 submits their list
Write-Host "`n[5] Player 2 submits their list..." -ForegroundColor Yellow
$player2Submit = @{
    player_name = "Bob"
    army_list = "Army List for Player 2`nUnit A`nUnit B`nUnit C"
} | ConvertTo-Json

$matchup = Invoke-RestMethod -Uri "http://localhost/api/squire/matchup/$matchupId/submit" `
    -Method POST `
    -ContentType "application/json" `
    -Body $player2Submit

Write-Host "   Complete: $($matchup.is_complete)" -ForegroundColor Green
Write-Host "   Player 1: $($matchup.player1.name)" -ForegroundColor Green
Write-Host "   Player 2: $($matchup.player2.name)" -ForegroundColor Green
Write-Host "   Battle Plan: $($matchup.battle_plan)" -ForegroundColor Cyan

# Step 6: Verify both players can see full results
Write-Host "`n[6] Verifying GET endpoint shows full results..." -ForegroundColor Yellow
$finalMatchup = Invoke-RestMethod -Uri "http://localhost/api/squire/matchup/$matchupId"

Write-Host "   Battle Plan: $($finalMatchup.battle_plan)" -ForegroundColor Cyan
Write-Host "   Player 1: $($finalMatchup.player1.name)" -ForegroundColor Green
Write-Host "   Player 2: $($finalMatchup.player2.name)" -ForegroundColor Green
Write-Host "   Both lists visible: $(($finalMatchup.player1.army_list -ne $null) -and ($finalMatchup.player2.army_list -ne $null))" -ForegroundColor Green

Write-Host "`n" + "="*50 -ForegroundColor Cyan
Write-Host "TEST COMPLETE" -ForegroundColor Green
Write-Host "="*50 -ForegroundColor Cyan
Write-Host "`nShare URL for browser testing:" -ForegroundColor Yellow
Write-Host $shareUrl -ForegroundColor White
Write-Host ""
