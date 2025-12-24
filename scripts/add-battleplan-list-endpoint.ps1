# Add Battle Plan List Endpoint Script
$ErrorActionPreference = "Stop"

Write-Host "Adding battle plan list endpoint..." -ForegroundColor Cyan

# Add endpoint to squire/routes.py
$routesFile = "squire\routes.py"
$routesContent = Get-Content $routesFile -Raw

if ($routesContent.Contains('/battle-plan/list')) {
    Write-Host "Battle plan list endpoint already exists" -ForegroundColor Yellow
    exit 0
}

# Define the new endpoint code
$newEndpoint = @"


@router.get("/battle-plan/list")
async def get_battle_plan_list(game_system: GameSystem):
    ""Get all battle plans for a game system.""
    plans = []
    
    if game_system == GameSystem.AOS:
        from squire.battle_plans import AOS_BATTLE_PLANS
        for bp_data in AOS_BATTLE_PLANS:
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
            plans.append(plan)
    else:
        # For other systems, generate a comprehensive sample
        seen = set()
        for _ in range(100):
            plan = generate_battle_plan(game_system)
            if plan.name not in seen:
                seen.add(plan.name)
                plans.append(plan)
    
    return plans
"@

# Find insertion point after random endpoint
$lines = $routesContent -split "`n"
$insertIndex = -1
$inRandomFunc = $false

for ($i = 0; $i -lt $lines.Count; $i++) {
    if ($lines[$i].Contains('/battle-plan/random')) {
        $inRandomFunc = $true
    }
    elseif ($inRandomFunc -and ($lines[$i] -match '^@router' -or $lines[$i] -match '^class ')) {
        $insertIndex = $i
        break
    }
}

if ($insertIndex -lt 0) {
    Write-Host "Could not find insertion point" -ForegroundColor Red
    exit 1
}

# Insert the new endpoint
$newLines = $lines[0..($insertIndex-1)] + $newEndpoint + $lines[$insertIndex..($lines.Count-1)]
$routesContent = $newLines -join "`n"
Set-Content $routesFile -Value $routesContent -NoNewline

Write-Host "Added /battle-plan/list endpoint" -ForegroundColor Green

# Update frontend
$frontendFile = "frontend\public\modules\squire\battleplan-reference.js"
$frontendContent = Get-Content $frontendFile -Raw

if (-not $frontendContent.Contains('const maxAttempts = 50')) {
    Write-Host "Frontend already updated" -ForegroundColor Yellow
    exit 0
}

# Replace probabilistic loading with direct list call
$oldCode = @'
const maxAttempts = 50;
        const plans = new Map();
        const seenPlans = new Set();
        
        for (let i = 0; i < maxAttempts; i++) {
            const response = await fetch(`/api/squire/battle-plan/random?game_system=${gameSystem}`);
            if (!response.ok) {
                throw new Error('Failed to load battle plan');
            }
            const plan = await response.json();
            
            if (!seenPlans.has(plan.name)) {
                plans.set(plan.name, plan);
                seenPlans.add(plan.name);
            }
            
            // Stop early if we're not finding new plans
            if (i > 10 && seenPlans.size < i / 2) {
                break;
            }
        }
        
        return Array.from(plans.values());
'@

$newCode = @'
// Use dedicated list endpoint
        const response = await fetch(`/api/squire/battle-plan/list?game_system=${gameSystem}`);
        if (!response.ok) {
            throw new Error('Failed to load battle plans');
        }
        const plans = await response.json();
        return plans;
'@

$frontendContent = $frontendContent.Replace($oldCode, $newCode)
Set-Content $frontendFile -Value $frontendContent -NoNewline

Write-Host "Updated frontend to use list endpoint" -ForegroundColor Green
Write-Host ""
Write-Host "Done! Rebuild with: .\scripts\runner.ps1 build-containers.ps1" -ForegroundColor Cyan
