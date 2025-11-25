#!/usr/bin/env pwsh
# Run all tests and generate report
# Usage: .\scripts\run-tests.ps1

$ErrorActionPreference = "Continue"
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$artifactsDir = "artifacts"
$reportFile = "$artifactsDir/test-results_$timestamp.txt"

# Create artifacts directory
if (!(Test-Path $artifactsDir)) {
    New-Item -ItemType Directory -Path $artifactsDir | Out-Null
}

# Start capturing output
Start-Transcript -Path $reportFile -Append

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "TEST RUN - $timestamp" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Check if services are running
Write-Host "[1/3] Checking services..." -ForegroundColor Yellow
$containers = docker ps --filter "name=squig" --format "{{.Names}}" 2>$null
if ($LASTEXITCODE -ne 0 -or !$containers) {
    Write-Host "   ERROR: Docker containers not running" -ForegroundColor Red
    Write-Host "   Run: .\scripts\rebuild-all.ps1" -ForegroundColor Yellow
    Stop-Transcript
    exit 1
}
Write-Host "   OK: Containers running" -ForegroundColor Green

# Run API tests
Write-Host "`n[2/3] Running API tests..." -ForegroundColor Yellow
.\scripts\test-api.ps1
$apiTestResult = $LASTEXITCODE

# Run matchup flow test
Write-Host "`n[3/3] Running matchup flow test..." -ForegroundColor Yellow
.\scripts\test-matchup-flow.ps1
$flowTestResult = $LASTEXITCODE

# Summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "TEST SUMMARY" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "API Tests:      $(if ($apiTestResult -eq 0) { 'PASSED' } else { 'FAILED' })" -ForegroundColor $(if ($apiTestResult -eq 0) { 'Green' } else { 'Red' })
Write-Host "Matchup Flow:   $(if ($flowTestResult -eq 0) { 'PASSED' } else { 'FAILED' })" -ForegroundColor $(if ($flowTestResult -eq 0) { 'Green' } else { 'Red' })
Write-Host "Report:         $reportFile" -ForegroundColor White

Stop-Transcript

if ($apiTestResult -eq 0 -and $flowTestResult -eq 0) {
    Write-Host "`nALL TESTS PASSED`n" -ForegroundColor Green
    exit 0
} else {
    Write-Host "`nSOME TESTS FAILED`n" -ForegroundColor Red
    exit 1
}
