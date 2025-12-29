# Show all 12 AoS battle plans from the API
Write-Host "`nFetching all Age of Sigmar battle plans from running API...`n" -ForegroundColor Cyan

for ($i=1; $i -le 12; $i++) {
    $response = docker exec squig curl -s "http://localhost:8000/api/squire/battle-plan/random?system=age_of_sigmar"
    $data = $response | ConvertFrom-Json
    Write-Host "$i. $($data.name)" -ForegroundColor Green
    Write-Host "   $($data.primary_objective.Substring(0, [Math]::Min(70, $data.primary_objective.Length)))..." -ForegroundColor Gray
}

Write-Host "`nAll 12 General's Handbook 2025-2026 missions available!`n" -ForegroundColor Cyan
