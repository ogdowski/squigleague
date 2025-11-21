# Show Live API Working - Generate 5 Random Missions
Write-Host "`n=== SQUIRE API - LIVE DEMONSTRATION ===" -ForegroundColor Cyan
Write-Host "Generating 5 random Age of Sigmar battle plans...`n" -ForegroundColor Yellow

for ($i=1; $i -le 5; $i++) {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/squire/battle-plan/random?system=age_of_sigmar" `
        -Headers @{"User-Agent"="PowerShell-Demo"} -UseBasicParsing
    $data = $response.Content | ConvertFrom-Json
    
    Write-Host "[$i] " -NoNewline -ForegroundColor Green
    Write-Host "$($data.name)" -ForegroundColor White
    Write-Host "    Deployment: " -NoNewline -ForegroundColor Gray
    Write-Host "$($data.deployment_description)" -ForegroundColor White
    Write-Host "    Scoring: " -NoNewline -ForegroundColor Gray
    Write-Host "$($data.primary_objective.Substring(0, [Math]::Min(60, $data.primary_objective.Length)))..." -ForegroundColor White
    Write-Host ""
}

Write-Host "`n=== ALL 12 MISSIONS AVAILABLE ===" -ForegroundColor Cyan
Write-Host "API running at: http://localhost:8000" -ForegroundColor Green
Write-Host "Docs available at: http://localhost:8000/docs`n" -ForegroundColor Green
