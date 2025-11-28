#!/usr/bin/env pwsh
# push-pr.ps1
# Creates a feature branch, commits changes, and pushes for PR

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "=" * 60
Write-Host "PUSH CHANGES FOR PULL REQUEST"
Write-Host "=" * 60

# Read branch name from config
$branchConfigFile = Join-Path $PSScriptRoot "branch-name.txt"
if (-not (Test-Path $branchConfigFile)) {
    Write-Host "ERROR: Branch name file not found: $branchConfigFile"
    exit 1
}

$branchName = (Get-Content $branchConfigFile -Raw).Trim()
Write-Host "Feature branch: $branchName"
Write-Host ""

# Check if there are staged changes
Write-Host "Checking for staged changes..."
$stagedChanges = git diff --cached --name-only
if (-not $stagedChanges) {
    Write-Host "ERROR: No changes are staged. Run 'git add .' first."
    exit 1
}

Write-Host "Found $($stagedChanges.Count) staged files"
Write-Host ""

# Check if branch exists
$branchExists = git branch --list $branchName
if ($branchExists) {
    Write-Host "Switching to existing branch: $branchName"
    git checkout $branchName
} else {
    Write-Host "Creating new branch: $branchName"
    git checkout -b $branchName
}

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to create/switch branch"
    exit 1
}
Write-Host "   Done"
Write-Host ""

# Read commit message from file
$commitMessageFile = Join-Path $PSScriptRoot "commit-message.txt"
if (-not (Test-Path $commitMessageFile)) {
    Write-Host "ERROR: Commit message file not found: $commitMessageFile"
    exit 1
}

$commitMessage = Get-Content $commitMessageFile -Raw

Write-Host "Committing changes..."
git commit -m $commitMessage
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Commit failed"
    exit 1
}
Write-Host "   Done"
Write-Host ""

# Push to remote
Write-Host "Pushing to remote..."
git push -u origin $branchName
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Push failed"
    exit 1
}
Write-Host "   Done"
Write-Host ""

Write-Host "=" * 60
Write-Host "PUSH COMPLETE"
Write-Host "=" * 60
Write-Host "Branch pushed: $branchName"
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Go to GitHub: https://github.com/ogdowski/squigleague"
Write-Host "2. Create a Pull Request from $branchName to main"
Write-Host "3. Reference the artifacts in artifacts/release_* folder"
