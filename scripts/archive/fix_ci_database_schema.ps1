# Activity Script: Fix CI Database Schema Initialization
# Purpose: Add database schema initialization step to CI workflow and push

Write-Host "=== FIX CI DATABASE SCHEMA INITIALIZATION ===" -ForegroundColor Cyan
Write-Host ""

# Step 1: Modify CI workflow to add schema initialization
Write-Host "[1/3] Adding database schema initialization to CI workflow..." -ForegroundColor Yellow

$workflowPath = "e:\repos\suigleague\.github\workflows\test.yml"
$content = Get-Content $workflowPath -Raw

# Check if already added
if ($content -match "Initialize test database schema") {
    Write-Host "    Schema initialization step already exists" -ForegroundColor Green
} else {
    Write-Host "    ERROR: Workflow file needs manual edit" -ForegroundColor Red
    exit 1
}

# Step 2: Commit changes
Write-Host ""
Write-Host "[2/3] Committing changes..." -ForegroundColor Yellow
git add -A
git commit -m "Add database schema initialization to CI workflow"

if ($LASTEXITCODE -ne 0) {
    Write-Host "    ERROR: Git commit failed" -ForegroundColor Red
    exit 1
}

Write-Host "    Committed successfully" -ForegroundColor Green

# Step 3: Push to GitHub
Write-Host ""
Write-Host "[3/3] Pushing to GitHub..." -ForegroundColor Yellow
git push

if ($LASTEXITCODE -ne 0) {
    Write-Host "    ERROR: Git push failed" -ForegroundColor Red
    exit 1
}

Write-Host "    Pushed successfully" -ForegroundColor Green

# Done
Write-Host ""
Write-Host "=== COMPLETE ===" -ForegroundColor Green
Write-Host ""
Write-Host "CI workflow updated to initialize database schema before tests."
Write-Host "New CI run should start automatically."
Write-Host ""
Write-Host "Check PR status: https://github.com/ogdowski/squigleague/pull/1"
