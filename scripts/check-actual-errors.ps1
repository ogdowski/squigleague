Write-Host "Testing actual API error responses..." -ForegroundColor Cyan

Write-Host "`n1. Invalid game system:" -ForegroundColor Yellow
try {
    Invoke-RestMethod -Uri "http://localhost:8000/api/squire/matchup/create" -Method POST -ContentType "application/json" -Body '{"game_system":"fake"}' 
} catch {
    Write-Host $_.ErrorDetails.Message
}

Write-Host "`n2. Missing field:" -ForegroundColor Yellow
try {
    Invoke-RestMethod -Uri "http://localhost:8000/api/squire/matchup/create" -Method POST -ContentType "application/json" -Body '{}'
} catch {
    Write-Host $_.ErrorDetails.Message
}

Write-Host "`n3. Creating matchup for test..." -ForegroundColor Yellow
$matchup = Invoke-RestMethod -Uri "http://localhost:8000/api/squire/matchup/create" -Method POST -ContentType "application/json" -Body '{"game_system":"age_of_sigmar"}'
Write-Host "ID: $($matchup.matchup_id)"

Write-Host "`n4. Army list too short:" -ForegroundColor Yellow
try {
    Invoke-RestMethod -Uri "http://localhost:8000/api/squire/matchup/$($matchup.matchup_id)/submit" -Method POST -ContentType "application/json" -Body '{"player_name":"Test","army_list":"short"}'
} catch {
    Write-Host $_.ErrorDetails.Message
}

Write-Host "`n5. Non-existent matchup (404):" -ForegroundColor Yellow
try {
    Invoke-RestMethod -Uri "http://localhost:8000/api/squire/matchup/FAKE123/submit" -Method POST -ContentType "application/json" -Body '{"player_name":"Test","army_list":"Valid text here"}'
} catch {
    Write-Host $_.ErrorDetails.Message
}
