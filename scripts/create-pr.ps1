#!/usr/bin/env pwsh
# create-pr.ps1
# Opens GitHub PR creation page with pre-filled information

$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "=" * 60
Write-Host "CREATE PULL REQUEST"
Write-Host "=" * 60

# Configuration
$owner = "ogdowski"
$repo = "squigleague"
$baseBranch = "main"

# Read branch name
$branchConfigFile = Join-Path $PSScriptRoot "branch-name.txt"
if (-not (Test-Path $branchConfigFile)) {
    Write-Host "ERROR: Branch name file not found: $branchConfigFile"
    exit 1
}
$headBranch = (Get-Content $branchConfigFile -Raw).Trim()

Write-Host "Opening PR creation page..."
Write-Host "  From: $headBranch"
Write-Host "  To: $baseBranch"
Write-Host ""

# Construct GitHub PR URL
$prUrl = "https://github.com/$owner/$repo/pull/new/$headBranch"

# Open in default browser
Start-Process $prUrl

Write-Host "=" * 60
Write-Host "BROWSER OPENED"
Write-Host "=" * 60
Write-Host "PR creation page opened in browser"
Write-Host ""
Write-Host "The following files contain PR content:"
Write-Host "  - Title: scripts/pr-title.txt"
Write-Host "  - Body: scripts/pr-body.txt"
Write-Host ""
Write-Host "Copy the content from these files into the PR form."
