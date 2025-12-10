# Comprehensive Edge Case Testing
# Tests error handling, validation, and edge cases

$ErrorActionPreference = "Continue"

Write-Host "`n================================================================" -ForegroundColor Cyan
Write-Host "EDGE CASE & ERROR HANDLING TESTS" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan

$testResults = @{
    Passed = @()
    Failed = @()
}

function Test-Case {
    param(
        [string]$Name,
        [scriptblock]$Action,
        [string]$ExpectedError = $null
    )
    
    Write-Host "`n[TEST] $Name" -ForegroundColor Yellow
    try {
        $result = & $Action
        if ($ExpectedError) {
            Write-Host "  FAIL: Expected error but got success" -ForegroundColor Red
            $script:testResults.Failed += "$Name - Should have failed with: $ExpectedError"
            return $false
        } else {
            Write-Host "  PASS" -ForegroundColor Green
            $script:testResults.Passed += $Name
            return $true
        }
    } catch {
        $errorMsg = $_.Exception.Message
        if ($ExpectedError) {
            if ($errorMsg -like "*$ExpectedError*") {
                Write-Host "  PASS: Got expected error" -ForegroundColor Green
                Write-Host "    Error: $errorMsg" -ForegroundColor Gray
                $script:testResults.Passed += $Name
                return $true
            } else {
                Write-Host "  FAIL: Wrong error" -ForegroundColor Red
                Write-Host "    Expected: $ExpectedError" -ForegroundColor Gray
                Write-Host "    Got: $errorMsg" -ForegroundColor Gray
                $script:testResults.Failed += "$Name - Wrong error"
                return $false
            }
        } else {
            Write-Host "  FAIL: Unexpected error" -ForegroundColor Red
            Write-Host "    Error: $errorMsg" -ForegroundColor Gray
            $script:testResults.Failed += "$Name - $errorMsg"
            return $false
        }
    }
}

# Check servers with retries
Write-Host "`nChecking servers..." -ForegroundColor Cyan
$maxRetries = 5
$retry = 0
$serversOk = $false

while ($retry -lt $maxRetries -and -not $serversOk) {
    try {
        Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 5 | Out-Null
        Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 5 | Out-Null
        Write-Host "  Servers OK" -ForegroundColor Green
        $serversOk = $true
    } catch {
        $retry++
        if ($retry -lt $maxRetries) {
            Write-Host "  Retry $retry/$maxRetries..." -ForegroundColor Yellow
            Start-Sleep -Seconds 2
        }
    }
}

if (-not $serversOk) {
    Write-Host "  Servers not running!" -ForegroundColor Red
    Write-Host "  Run: .\scripts\test-comprehensive-gui.ps1" -ForegroundColor Yellow
    exit 1
}

# ===================================================================
# MATCHUP CREATION TESTS
# ===================================================================

Test-Case "Create matchup - valid AoS system" {
    $body = @{ game_system = "age_of_sigmar" } | ConvertTo-Json
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/squire/matchup/create" -Method POST -Body $body -ContentType "application/json" -UseBasicParsing
    $data = $response.Content | ConvertFrom-Json
    if (-not $data.matchup_id) { throw "No matchup_id" }
    $global:testMatchupId = $data.matchup_id
}

Test-Case "Create matchup - invalid system" {
    $body = @{ game_system = "invalid_system" } | ConvertTo-Json
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/squire/matchup/create" -Method POST -Body $body -ContentType "application/json" -UseBasicParsing
} -ExpectedError "Invalid game system"

Test-Case "Create matchup - missing game_system field" {
    $body = '{}' 
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/squire/matchup/create" -Method POST -Body $body -ContentType "application/json" -UseBasicParsing
} -ExpectedError "field required"

Test-Case "Create matchup - empty game_system" {
    $body = @{ game_system = "" } | ConvertTo-Json
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/squire/matchup/create" -Method POST -Body $body -ContentType "application/json" -UseBasicParsing
} -ExpectedError "Invalid"

# ===================================================================
# ARMY LIST SUBMISSION TESTS
# ===================================================================

Test-Case "Submit list - valid data" {
    $body = @{ 
        player_name = "Test Player"
        army_list = "Valid army list with enough characters" 
    } | ConvertTo-Json
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/squire/matchup/$global:testMatchupId/submit" -Method POST -Body $body -ContentType "application/json" -UseBasicParsing
}

# Create new matchup for next tests
$body = @{ game_system = "age_of_sigmar" } | ConvertTo-Json
$response = Invoke-WebRequest -Uri "http://localhost:8000/api/squire/matchup/create" -Method POST -Body $body -ContentType "application/json" -UseBasicParsing
$global:testMatchupId2 = ($response.Content | ConvertFrom-Json).matchup_id

Test-Case "Submit list - army_list too short (under 10 chars)" {
    $body = @{ 
        player_name = "Player"
        army_list = "short" 
    } | ConvertTo-Json
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/squire/matchup/$global:testMatchupId2/submit" -Method POST -Body $body -ContentType "application/json" -UseBasicParsing
} -ExpectedError "at least 10 characters"

Test-Case "Submit list - missing player_name" {
    $body = @{ 
        army_list = "Valid army list with enough characters" 
    } | ConvertTo-Json
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/squire/matchup/$global:testMatchupId2/submit" -Method POST -Body $body -ContentType "application/json" -UseBasicParsing
} -ExpectedError "field required"

Test-Case "Submit list - missing army_list" {
    $body = @{ 
        player_name = "Player" 
    } | ConvertTo-Json
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/squire/matchup/$global:testMatchupId2/submit" -Method POST -Body $body -ContentType "application/json" -UseBasicParsing
} -ExpectedError "field required"

Test-Case "Submit list - empty player_name" {
    $body = @{ 
        player_name = ""
        army_list = "Valid army list with enough characters" 
    } | ConvertTo-Json
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/squire/matchup/$global:testMatchupId2/submit" -Method POST -Body $body -ContentType "application/json" -UseBasicParsing
} -ExpectedError "String should have at least 1 character"

Test-Case "Submit list - non-existent matchup ID" {
    $body = @{ 
        player_name = "Player"
        army_list = "Valid army list with enough characters" 
    } | ConvertTo-Json
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/squire/matchup/FAKEID12345/submit" -Method POST -Body $body -ContentType "application/json" -UseBasicParsing
} -ExpectedError "Not found"

# Create matchup and fill both slots
$body = @{ game_system = "age_of_sigmar" } | ConvertTo-Json
$response = Invoke-WebRequest -Uri "http://localhost:8000/api/squire/matchup/create" -Method POST -Body $body -ContentType "application/json" -UseBasicParsing
$fullMatchupId = ($response.Content | ConvertFrom-Json).matchup_id

$body = @{ player_name = "Player 1"; army_list = "Army list one with text" } | ConvertTo-Json
Invoke-WebRequest -Uri "http://localhost:8000/api/squire/matchup/$fullMatchupId/submit" -Method POST -Body $body -ContentType "application/json" -UseBasicParsing | Out-Null

$body = @{ player_name = "Player 2"; army_list = "Army list two with text" } | ConvertTo-Json
Invoke-WebRequest -Uri "http://localhost:8000/api/squire/matchup/$fullMatchupId/submit" -Method POST -Body $body -ContentType "application/json" -UseBasicParsing | Out-Null

Test-Case "Submit list - matchup already full (3rd player)" {
    $body = @{ 
        player_name = "Player 3"
        army_list = "Army list three with text" 
    } | ConvertTo-Json
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/squire/matchup/$fullMatchupId/submit" -Method POST -Body $body -ContentType "application/json" -UseBasicParsing
} -ExpectedError "already has two players"

# ===================================================================
# MATCHUP RETRIEVAL TESTS
# ===================================================================

Test-Case "Get matchup - valid ID" {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/squire/matchup/$fullMatchupId" -UseBasicParsing
    $data = $response.Content | ConvertFrom-Json
    if (-not $data.is_complete) { throw "Matchup should be complete" }
}

Test-Case "Get matchup - non-existent ID" {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/squire/matchup/FAKEID99999" -UseBasicParsing
} -ExpectedError "Not found"

# ===================================================================
# BATTLE PLAN TESTS
# ===================================================================

Test-Case "Get battle plan - valid system" {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/squire/battle-plan/random?system=age_of_sigmar" -UseBasicParsing
    $data = $response.Content | ConvertFrom-Json
    if (-not $data.name) { throw "No battle plan name" }
}

Test-Case "Get battle plan - invalid system" {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/squire/battle-plan/random?system=invalid_game" -UseBasicParsing
} -ExpectedError "Invalid game system"

# ===================================================================
# CORS TESTS
# ===================================================================

Test-Case "CORS - OPTIONS preflight from localhost:3000" {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/squire/matchup/create" `
        -Method OPTIONS `
        -Headers @{
            "Origin" = "http://localhost:3000"
            "Access-Control-Request-Method" = "POST"
            "Access-Control-Request-Headers" = "content-type"
        } -UseBasicParsing
    
    $corsOrigin = $response.Headers['Access-Control-Allow-Origin']
    if ($corsOrigin -ne "http://localhost:3000") {
        throw "CORS origin mismatch: $corsOrigin"
    }
}

Test-Case "CORS - POST from localhost:3000 with Origin header" {
    $body = @{ game_system = "age_of_sigmar" } | ConvertTo-Json
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/squire/matchup/create" `
        -Method POST `
        -Body $body `
        -ContentType "application/json" `
        -Headers @{ "Origin" = "http://localhost:3000" } `
        -UseBasicParsing
    
    $corsOrigin = $response.Headers['Access-Control-Allow-Origin']
    if ($corsOrigin -ne "http://localhost:3000") {
        throw "CORS origin not set correctly"
    }
}

# ===================================================================
# RESULTS
# ===================================================================

Write-Host "`n================================================================" -ForegroundColor Cyan
Write-Host "TEST RESULTS" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "PASSED: $($testResults.Passed.Count)" -ForegroundColor Green
foreach ($test in $testResults.Passed) {
    Write-Host "  ✓ $test" -ForegroundColor Green
}

if ($testResults.Failed.Count -gt 0) {
    Write-Host "`nFAILED: $($testResults.Failed.Count)" -ForegroundColor Red
    foreach ($test in $testResults.Failed) {
        Write-Host "  ✗ $test" -ForegroundColor Red
    }
    exit 1
} else {
    Write-Host "`nAll edge case tests passed! ✓" -ForegroundColor Green
    exit 0
}
