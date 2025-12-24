#!/usr/bin/env pwsh
# push-changes.ps1
# Commits and pushes all staged changes to the remote repository

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "=" * 60
Write-Host "PUSH CHANGES TO REMOTE"
Write-Host "=" * 60

# Check if there are staged changes
Write-Host "Checking for staged changes..."
$stagedChanges = git diff --cached --name-only
if (-not $stagedChanges) {
    Write-Host "ERROR: No changes are staged. Run 'git add .' first."
    exit 1
}

Write-Host "Found staged changes:"
$stagedChanges | ForEach-Object { Write-Host "  - $_" }
Write-Host ""

# Read commit message from file or generate one
$commitMessageFile = Join-Path $PSScriptRoot "commit-message.txt"
if (Test-Path $commitMessageFile) {
    $commitMessage = Get-Content $commitMessageFile -Raw
    Write-Host "Using commit message from file"
} else {
    # Generate commit message from staged files
    $commitMessage = "chore: Update $(($stagedChanges | Measure-Object).Count) files`n`nStaged changes:`n"
    $stagedChanges | ForEach-Object { $commitMessage += "- $_`n" }
    Write-Host "Generated commit message (no commit-message.txt found)"
}

Write-Host "Commit message:"
Write-Host "---"
Write-Host $commitMessage
Write-Host "---"
Write-Host ""

# Commit changes
Write-Host "Committing changes..."
git commit -m $commitMessage
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Commit failed"
    exit 1
}
Write-Host "   Done"
Write-Host ""

# Get current branch
$currentBranch = git branch --show-current
Write-Host "Current branch: $currentBranch"

# Push to remote
Write-Host "Pushing to remote..."
git push origin $currentBranch
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Push failed"
    exit 1
}
Write-Host "   Done"
Write-Host ""

Write-Host "=" * 60
Write-Host "PUSH COMPLETE"
Write-Host "=" * 60
Write-Host "Changes pushed to origin/$currentBranch"
