# Quick Matchup Test

Write-Host "Testing Matchup System..." -ForegroundColor Cyan
Write-Host ""

# Create matchup
Write-Host "[1] Creating matchup..." -ForegroundColor Yellow
$createResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/squire/matchup/create" `
    -Method POST `
    -ContentType "application/json" `
    -Body '{"game_system": "age_of_sigmar"}'

$matchupId = $createResponse.matchup_id
Write-Host "   Matchup ID: $matchupId" -ForegroundColor Green
Write-Host "   Share URL: http://localhost$($createResponse.share_url)" -ForegroundColor Green
Write-Host ""

# Submit first list
Write-Host "[2] Submitting first list..." -ForegroundColor Yellow
$submit1 = Invoke-RestMethod -Uri "http://localhost:8000/api/squire/matchup/$matchupId/submit" `
    -Method POST `
    -ContentType "application/json" `
    -Body '{"player_name": "Player 1", "army_list": "Stormcast - 2000pts"}'

Write-Host "   Complete: $($submit1.is_complete)" -ForegroundColor $(if ($submit1.is_complete) { "Red" } else { "Green" })
Write-Host "   Waiting count: $($submit1.waiting_count)" -ForegroundColor Gray
Write-Host "   Battle plan: $(if ($submit1.battle_plan) { $submit1.battle_plan.name } else { 'Not yet generated' })" -ForegroundColor Gray
Write-Host ""

# Submit second list
Write-Host "[3] Submitting second list..." -ForegroundColor Yellow
$submit2 = Invoke-RestMethod -Uri "http://localhost:8000/api/squire/matchup/$matchupId/submit" `
    -Method POST `
    -ContentType "application/json" `
    -Body '{"player_name": "Player 2", "army_list": "Lumineth - 2000pts"}'

Write-Host "   Complete: $($submit2.is_complete)" -ForegroundColor $(if ($submit2.is_complete) { "Green" } else { "Red" })
Write-Host "   Waiting count: $($submit2.waiting_count)" -ForegroundColor Gray
Write-Host "   Battle plan: $($submit2.battle_plan.name)" -ForegroundColor Green
Write-Host "   Player 1: $($submit2.player1.name)" -ForegroundColor Gray
Write-Host "   Player 2: $($submit2.player2.name)" -ForegroundColor Gray
Write-Host ""

# Verify GET endpoint shows same data
Write-Host "[4] Verifying GET endpoint..." -ForegroundColor Yellow
$getResult = Invoke-RestMethod -Uri "http://localhost:8000/api/squire/matchup/$matchupId"

if ($getResult.battle_plan) {
    Write-Host "   SUCCESS: Battle plan visible via GET" -ForegroundColor Green
    Write-Host "   Battle plan: $($getResult.battle_plan.name)" -ForegroundColor Gray
} else {
    Write-Host "   ERROR: Battle plan not visible" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "TEST COMPLETE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Open in browser:" -ForegroundColor White
Write-Host "http://localhost/squire/matchup/$matchupId" -ForegroundColor Yellow
Write-Host ""
