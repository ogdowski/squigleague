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

# Get current branch BEFORE checking for staged changes
$currentBranch = git branch --show-current
Write-Host "Current branch: $currentBranch"

# Check if we need to switch branches
if ($currentBranch -ne $branchName) {
    # Check for uncommitted changes
    $uncommittedChanges = git status --porcelain
    if ($uncommittedChanges) {
        Write-Host "ERROR: Cannot switch branches with uncommitted changes."
        Write-Host "Changes detected:"
        Write-Host $uncommittedChanges
        Write-Host ""
        Write-Host "Either:"
        Write-Host "1. You're already on $branchName (no switch needed), or"
        Write-Host "2. Commit changes first, then switch branches"
        exit 1
    }
    
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
}

# Check if there are staged changes
Write-Host "Checking for staged changes..."
$stagedChanges = git diff --cached --name-only
if (-not $stagedChanges) {
    Write-Host "ERROR: No changes are staged. Run 'git add .' first."
    exit 1
}

Write-Host "Found staged files:"
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
