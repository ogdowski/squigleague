#!/usr/bin/env pwsh
# Export all battle plans to JSON and Markdown for reference
# Usage: .\scripts\export-battleplans.ps1

$ErrorActionPreference = "Stop"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "EXPORT BATTLE PLANS" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$systems = @("age_of_sigmar", "warhammer_40k", "the_old_world")
$allPlans = @{}

foreach ($system in $systems) {
    Write-Host "Collecting $system battle plans..." -ForegroundColor Yellow
    
    $plans = @()
    $seenNames = @{}
    $attempts = 0
    $maxAttempts = 100
    
    # Collect unique battle plans
    while ($attempts -lt $maxAttempts) {
        try {
            $plan = Invoke-RestMethod -Uri "http://localhost/api/squire/battle-plan/random?system=$system" -ErrorAction Stop
            
            if (!$seenNames.ContainsKey($plan.name)) {
                $seenNames[$plan.name] = $true
                $plans += $plan
            }
            
            $attempts++
            
            # If we've seen the same plans repeatedly, probably found them all
            if ($attempts -gt 20 -and $plans.Count -lt ($attempts / 3)) {
                break
            }
        } catch {
            Write-Host "   Error fetching plan: $_" -ForegroundColor Red
            break
        }
    }
    
    $allPlans[$system] = $plans | Sort-Object -Property name
    Write-Host "   Found $($plans.Count) unique battle plans" -ForegroundColor Green
}

# Export to JSON
$jsonPath = "scripts/battleplan-reference.json"
$allPlans | ConvertTo-Json -Depth 10 | Set-Content $jsonPath
Write-Host "`nExported JSON: $jsonPath" -ForegroundColor Green

# Generate Markdown
$mdPath = "scripts/battleplan-reference.md"
$md = @"
# Battle Plan Reference
Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

"@

foreach ($system in $systems) {
    $systemName = switch ($system) {
        "age_of_sigmar" { "Age of Sigmar" }
        "warhammer_40k" { "Warhammer 40,000" }
        "the_old_world" { "The Old World" }
    }
    
    $plans = $allPlans[$system]
    $md += "`n## $systemName ($($plans.Count) Battle Plans)`n`n"
    
    foreach ($plan in $plans) {
        $md += "### $($plan.name)`n`n"
        $md += "- **Deployment:** $($plan.deployment_description)`n"
        $md += "- **Primary Objective:** $($plan.primary_objective)`n"
        
        if ($plan.secondary_objectives -and $plan.secondary_objectives.Count -gt 0) {
            $md += "- **Secondary Objectives:**`n"
            foreach ($obj in $plan.secondary_objectives) {
                $md += "  - $obj`n"
            }
        }
        
        $md += "- **Victory Conditions:** $($plan.victory_conditions)`n"
        $md += "- **Turn Limit:** $($plan.turn_limit) rounds`n"
        
        if ($plan.special_rules -and $plan.special_rules.Count -gt 0) {
            $md += "- **Special Rules:**`n"
            foreach ($rule in $plan.special_rules) {
                $md += "  - $rule`n"
            }
        }
        
        if ($plan.battle_tactics) {
            $md += "- **Battle Tactics:** $($plan.battle_tactics)`n"
        }
        
        $md += "`n"
    }
}

$md | Set-Content $mdPath
Write-Host "Exported Markdown: $mdPath" -ForegroundColor Green

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "EXPORT COMPLETE" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Total battle plans: $(($allPlans.Values | ForEach-Object { $_.Count } | Measure-Object -Sum).Sum)" -ForegroundColor White
Write-Host ""

exit 0
