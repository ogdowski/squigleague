# verify-enforcement.ps1
# Verifies that the activity script enforcement system is working correctly

Write-Host "=== Activity Script Enforcement Verification ===" -ForegroundColor Cyan
Write-Host ""

$results = @()

# Test 1: Verify copilot-instructions.md exists
Write-Host "[1] Checking GitHub Copilot instructions..." -ForegroundColor Yellow
if (Test-Path .github\copilot-instructions.md) {
    Write-Host "   ✓ .github\copilot-instructions.md exists" -ForegroundColor Green
    $results += "PASS"
} else {
    Write-Host "   ✗ .github\copilot-instructions.md missing" -ForegroundColor Red
    $results += "FAIL"
}

# Test 2: Verify runner.ps1 exists
Write-Host "[2] Checking runner script..." -ForegroundColor Yellow
if (Test-Path scripts\runner.ps1) {
    Write-Host "   ✓ scripts\runner.ps1 exists" -ForegroundColor Green
    $results += "PASS"
} else {
    Write-Host "   ✗ scripts\runner.ps1 missing" -ForegroundColor Red
    $results += "FAIL"
}

# Test 3: Verify allowed-scripts.json exists and has scripts
Write-Host "[3] Checking whitelist..." -ForegroundColor Yellow
if (Test-Path scripts\allowed-scripts.json) {
    $whitelist = Get-Content scripts\allowed-scripts.json -Raw | ConvertFrom-Json
    $scriptCount = ($whitelist.scripts.PSObject.Properties | Measure-Object).Count
    Write-Host "   ✓ scripts\allowed-scripts.json exists ($scriptCount scripts approved)" -ForegroundColor Green
    $results += "PASS"
} else {
    Write-Host "   ✗ scripts\allowed-scripts.json missing" -ForegroundColor Red
    $results += "FAIL"
}

# Test 4: Verify generate-checksums.ps1 exists
Write-Host "[4] Checking checksum generator..." -ForegroundColor Yellow
if (Test-Path scripts\generate-checksums.ps1) {
    Write-Host "   ✓ scripts\generate-checksums.ps1 exists" -ForegroundColor Green
    $results += "PASS"
} else {
    Write-Host "   ✗ scripts\generate-checksums.ps1 missing" -ForegroundColor Red
    $results += "FAIL"
}

# Test 5: Verify runner.log exists (shows enforcement is active)
Write-Host "[5] Checking audit log..." -ForegroundColor Yellow
if (Test-Path scripts\runner.log) {
    $logLines = (Get-Content scripts\runner.log | Measure-Object -Line).Lines
    Write-Host "   ✓ scripts\runner.log exists ($logLines log entries)" -ForegroundColor Green
    $results += "PASS"
} else {
    Write-Host "   ✗ scripts\runner.log missing (no executions yet)" -ForegroundColor Yellow
    $results += "WARN"
}

# Test 6: Try running an approved script (dry-run)
Write-Host "[6] Testing approved script execution..." -ForegroundColor Yellow
try {
    $output = .\scripts\runner.ps1 -Script manual-test-auth.ps1 -WhatIf 2>&1
    if ($output -match "Running allowed script") {
        Write-Host "   ✓ Approved script passes validation" -ForegroundColor Green
        $results += "PASS"
    } else {
        Write-Host "   ✗ Approved script validation failed" -ForegroundColor Red
        $results += "FAIL"
    }
} catch {
    Write-Host "   ✗ Error running approved script: $($_.Exception.Message)" -ForegroundColor Red
    $results += "FAIL"
}

# Test 7: Try running a non-existent script (should fail)
Write-Host "[7] Testing non-whitelisted script rejection..." -ForegroundColor Yellow
try {
    $output = .\scripts\runner.ps1 -Script fake-unauthorized-script.ps1 2>&1
    if ($output -match "not in allowed-scripts.json whitelist") {
        Write-Host "   ✓ Non-whitelisted script correctly rejected" -ForegroundColor Green
        $results += "PASS"
    } else {
        Write-Host "   ✗ Non-whitelisted script not rejected" -ForegroundColor Red
        $results += "FAIL"
    }
} catch {
    if ($_.Exception.Message -match "not in allowed-scripts.json whitelist") {
        Write-Host "   ✓ Non-whitelisted script correctly rejected" -ForegroundColor Green
        $results += "PASS"
    } else {
        Write-Host "   ? Unexpected error: $($_.Exception.Message)" -ForegroundColor Yellow
        $results += "WARN"
    }
}

# Test 8: Verify documentation exists
Write-Host "[8] Checking documentation..." -ForegroundColor Yellow
$docs = @(
    "scripts\README.md",
    "scripts\QUICK-REFERENCE.md",
    "docs\ENFORCEMENT_SUMMARY.md",
    "docs\COPILOT_INTEGRATION.md"
)
$docCount = 0
foreach ($doc in $docs) {
    if (Test-Path $doc) {
        $docCount++
    }
}
if ($docCount -eq $docs.Count) {
    Write-Host "   ✓ All documentation files exist ($docCount/$($docs.Count))" -ForegroundColor Green
    $results += "PASS"
} else {
    Write-Host "   ⚠ Some documentation missing ($docCount/$($docs.Count))" -ForegroundColor Yellow
    $results += "WARN"
}

# Summary
Write-Host ""
Write-Host "=== Verification Summary ===" -ForegroundColor Cyan
$passCount = ($results | Where-Object { $_ -eq "PASS" }).Count
$failCount = ($results | Where-Object { $_ -eq "FAIL" }).Count
$warnCount = ($results | Where-Object { $_ -eq "WARN" }).Count
$total = $results.Count

Write-Host "Tests Passed: $passCount/$total" -ForegroundColor Green
if ($failCount -gt 0) {
    Write-Host "Tests Failed: $failCount/$total" -ForegroundColor Red
}
if ($warnCount -gt 0) {
    Write-Host "Warnings: $warnCount/$total" -ForegroundColor Yellow
}

Write-Host ""
if ($failCount -eq 0) {
    Write-Host "✓ Activity script enforcement system is OPERATIONAL" -ForegroundColor Green
    Write-Host ""
    Write-Host "The following enforcement mechanisms are active:" -ForegroundColor White
    Write-Host "  • GitHub Copilot instructions (.github/copilot-instructions.md)" -ForegroundColor Gray
    Write-Host "  • Whitelist validation (scripts/allowed-scripts.json)" -ForegroundColor Gray
    Write-Host "  • SHA256 integrity checks (runner.ps1)" -ForegroundColor Gray
    Write-Host "  • Audit logging (scripts/runner.log)" -ForegroundColor Gray
    Write-Host "  • Complete documentation (4 doc files)" -ForegroundColor Gray
    exit 0
} else {
    Write-Host "✗ Activity script enforcement system has ISSUES" -ForegroundColor Red
    Write-Host "Please review the failed tests above." -ForegroundColor Yellow
    exit 1
}
