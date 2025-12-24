# Debug Battle Plan List Endpoint
$ErrorActionPreference = "Stop"

Write-Host "Debugging battle plan list endpoint..." -ForegroundColor Cyan
Write-Host ""

# Check source data
Write-Host "1. Checking AOS_BATTLE_PLANS array length..." -ForegroundColor Yellow
$arrayLength = docker exec squig python -c "from squire.battle_plans import AOS_BATTLE_PLANS; print(len(AOS_BATTLE_PLANS))"
Write-Host "   Source array has $arrayLength battle plans" -ForegroundColor White

# Check API response
Write-Host ""
Write-Host "2. Checking API response..." -ForegroundColor Yellow
$apiResponse = Invoke-RestMethod -Uri "http://localhost/api/squire/battle-plan/list?game_system=age_of_sigmar"
$apiCount = $apiResponse.Count
Write-Host "   API returns $apiCount battle plans" -ForegroundColor White

# List what API returns
Write-Host ""
Write-Host "3. Battle plans returned by API:" -ForegroundColor Yellow
foreach ($plan in $apiResponse) {
    Write-Host "   - $($plan.name)" -ForegroundColor White
}

# Check if there's a Python exception during BattlePlan creation
Write-Host ""
Write-Host "4. Testing BattlePlan object creation..." -ForegroundColor Yellow
$testScript = @'
from squire.battle_plans import AOS_BATTLE_PLANS
from squire.models import BattlePlan, GameSystem, DeploymentType

plans_created = 0
for bp_data in AOS_BATTLE_PLANS:
    try:
        plan = BattlePlan(
            name=bp_data["name"],
            game_system=GameSystem.AOS,
            deployment=DeploymentType.FRONTAL_ASSAULT,
            deployment_description=bp_data.get("deployment", ""),
            primary_objective=bp_data.get("scoring", ""),
            secondary_objectives=[obj.get("name", "") for obj in bp_data.get("objectives", []) if isinstance(obj, dict) and "name" in obj],
            victory_conditions="Player with most Victory Points wins",
            turn_limit=5,
            special_rules=bp_data.get("special_rules", [])
        )
        plans_created += 1
    except Exception as e:
        print(f"FAILED: {bp_data['name']} - {e}")

print(f"Successfully created {plans_created} BattlePlan objects")
'@

$result = docker exec squig python -c $testScript
Write-Host "   $result" -ForegroundColor White

Write-Host ""
if ($apiCount -eq 12) {
    Write-Host "SUCCESS: API returns all 12 battle plans" -ForegroundColor Green
}
else {
    Write-Host "PROBLEM FOUND: API returns only $apiCount out of 12 battle plans" -ForegroundColor Red
    Write-Host "Check the test output above for which plans failed to create" -ForegroundColor Yellow
}
