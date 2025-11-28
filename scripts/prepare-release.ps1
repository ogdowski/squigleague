#!/usr/bin/env pwsh
# Prepare release artifacts - orchestrates rebuild, test, export
# Usage: .\scripts\prepare-release.ps1

$ErrorActionPreference = "Continue"
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "RELEASE PREPARATION - $timestamp" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$allPassed = $true

# Step 1: Rebuild
Write-Host "[1/4] Rebuilding containers..." -ForegroundColor Yellow
.\scripts\rebuild-all.ps1
if ($LASTEXITCODE -ne 0) {
    Write-Host "   FAILED: Rebuild failed" -ForegroundColor Red
    $allPassed = $false
} else {
    Write-Host "   PASSED: Rebuild successful" -ForegroundColor Green
}

# Step 2: Run tests
if ($allPassed) {
    Write-Host "`n[2/4] Running tests..." -ForegroundColor Yellow
    .\scripts\run-tests.ps1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "   FAILED: Tests failed" -ForegroundColor Red
        $allPassed = $false
    } else {
        Write-Host "   PASSED: All tests passed" -ForegroundColor Green
    }
}

# Step 3: Export battle plans
if ($allPassed) {
    Write-Host "`n[3/4] Exporting battle plans..." -ForegroundColor Yellow
    .\scripts\export-battleplans.ps1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "   FAILED: Export failed" -ForegroundColor Red
        $allPassed = $false
    } else {
        Write-Host "   PASSED: Export successful" -ForegroundColor Green
    }
}

# Step 4: Create artifacts package
if ($allPassed) {
    Write-Host "`n[4/4] Creating release artifacts..." -ForegroundColor Yellow
    
    $artifactsDir = "artifacts"
    $releaseDir = "$artifactsDir/release_$timestamp"
    
    if (!(Test-Path $artifactsDir)) {
        New-Item -ItemType Directory -Path $artifactsDir | Out-Null
    }
    
    New-Item -ItemType Directory -Path $releaseDir -Force | Out-Null
    
    # Copy relevant files
    Copy-Item "scripts/battleplan-reference.json" "$releaseDir/" -ErrorAction SilentlyContinue
    Copy-Item "scripts/battleplan-reference.md" "$releaseDir/" -ErrorAction SilentlyContinue
    Copy-Item "PR-SUMMARY.md" "$releaseDir/" -ErrorAction SilentlyContinue
    Copy-Item "scripts/MATCHUP-FLOW.md" "$releaseDir/" -ErrorAction SilentlyContinue
    
    # Copy latest test results
    $latestTest = Get-ChildItem "$artifactsDir/test-results_*.txt" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($latestTest) {
        Copy-Item $latestTest.FullName "$releaseDir/test-results.txt"
    }
    
    # Create changed files list
    $changedFiles = @"
# Changed Files for PR

## Backend
- squire/matchup.py (NEW) - Matchup data models and business logic
- squire/routes.py (MODIFIED) - Added matchup API endpoints
- tests/integration/squire/test_matchup.py (NEW) - Comprehensive test suite

## Frontend  
- frontend/public/modules/squire/matchup.js (NEW) - Matchup UI component
- frontend/public/modules/squire/battleplan-reference.js (NEW) - Battle plan reference page
- frontend/public/modules/squire/battleplan.js (MODIFIED) - Removed emoji
- frontend/public/modules/herald/home.js (MODIFIED) - Removed emoji
- frontend/public/modules/herald/waiting.js (MODIFIED) - Removed emoji
- frontend/public/modules/herald/reveal.js (MODIFIED) - Removed emoji
- frontend/public/src/main.js (MODIFIED) - Added routing
- frontend/public/index.html (MODIFIED) - Added navigation

## Configuration
- nginx/nginx.conf (MODIFIED) - Fixed syntax errors, removed 'just', fixed admin IP

## Scripts
- scripts/run-tests.ps1 (NEW) - Automated test runner
- scripts/rebuild-all.ps1 (NEW) - Container rebuild script
- scripts/export-battleplans.ps1 (NEW) - Battle plan export script
- scripts/prepare-release.ps1 (NEW) - Release preparation orchestration
- scripts/test-api.ps1 (NEW) - API integration tests
- scripts/test-matchup-flow.ps1 (NEW) - End-to-end flow test
- scripts/MATCHUP-FLOW.md (NEW) - User flow documentation

## Documentation
- PR-SUMMARY.md (NEW) - Pull request summary
"@
    
    $changedFiles | Set-Content "$releaseDir/CHANGED-FILES.md"
    
    # Create ZIP
    $zipPath = "$artifactsDir/release_$timestamp.zip"
    Compress-Archive -Path $releaseDir -DestinationPath $zipPath -Force
    
    Write-Host "   Created: $zipPath" -ForegroundColor Green
}

# Final summary
Write-Host "`n========================================" -ForegroundColor Cyan
if ($allPassed) {
    Write-Host "RELEASE READY!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "`nArtifacts: artifacts/release_$timestamp/" -ForegroundColor White
    Write-Host "ZIP: artifacts/release_$timestamp.zip" -ForegroundColor White
    Write-Host "`nAll checks passed. Ready for PR submission.`n" -ForegroundColor Green
    exit 0
} else {
    Write-Host "RELEASE FAILED" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "`nPlease fix errors and run again.`n" -ForegroundColor Red
    exit 1
}
