# Simple PowerShell-only test that mimics the JavaScript tests
# This will show us the actual API responses

Write-Host "=== DIRECT API ERROR TESTING ===" -ForegroundColor Cyan
Write-Host "Replicating JavaScript test scenarios...`n" -ForegroundColor Yellow

$passed = 0
$failed = 0
$failedTests = @()

function Test-API {
    param($name, $uri, $method, $body, $expectedError)
    
    Write-Host "Testing: $name" -ForegroundColor Gray
    
    try {
        $response = Invoke-RestMethod -Uri $uri -Method $method -ContentType "application/json" -Body $body -ErrorAction Stop
        
        if ($expectedError) {
            $script:failed++
            $script:failedTests += $name
            Write-Host "  FAIL: Expected error but got success" -ForegroundColor Red
            return $false
        } else {
            $script:passed++
            Write-Host "  PASS" -ForegroundColor Green
            return $response
        }
        
    } catch {
        if ($expectedError) {
            $errorMsg = $_.ErrorDetails.Message
            $errorObj = $errorMsg | ConvertFrom-Json -ErrorAction SilentlyContinue
            
            # Extract error message using our JavaScript logic
            $extractedMsg = ""
            if ($errorObj.detail -is [Array]) {
                $extractedMsg = ($errorObj.detail | ForEach-Object { $_.msg }) -join ', '
            } elseif ($errorObj.detail) {
                $extractedMsg = $errorObj.detail
            } elseif ($errorObj.message) {
                $extractedMsg = $errorObj.message
            } elseif ($errorObj.error) {
                $extractedMsg = $errorObj.error
            }
            
            Write-Host "  Error response: $errorMsg" -ForegroundColor DarkGray
            Write-Host "  Extracted msg: $extractedMsg" -ForegroundColor DarkGray
            
            if ($extractedMsg -match $expectedError) {
                $script:passed++
                Write-Host "  PASS: Got expected error" -ForegroundColor Green
                return $true
            } else {
                $script:failed++
                $script:failedTests += $name
                Write-Host "  FAIL: Expected '$expectedError' but got '$extractedMsg'" -ForegroundColor Red
                return $false
            }
        } else {
            $script:failed++
            $script:failedTests += $name
            Write-Host "  FAIL: Unexpected error: $($_.Exception.Message)" -ForegroundColor Red
            Write-Host "  Details: $($_.ErrorDetails.Message)" -ForegroundColor DarkGray
            return $false
        }
    }
}

# Test 1: Valid matchup creation
$matchup = Test-API "Create matchup - valid" "http://localhost:8000/api/squire/matchup/create" "POST" '{"game_system":"age_of_sigmar"}' $null

# Test 2: Invalid game system
Test-API "Create matchup - invalid system" "http://localhost:8000/api/squire/matchup/create" "POST" '{"game_system":"fake_game"}' "Invalid game system" | Out-Null

# Test 3: Missing game_system
Test-API "Create matchup - missing field" "http://localhost:8000/api/squire/matchup/create" "POST" '{}' "Field required" | Out-Null

if ($matchup) {
    $matchupId = $matchup.matchup_id
    
    # Test 4: Valid submission
    Test-API "Submit list - valid" "http://localhost:8000/api/squire/matchup/$matchupId/submit" "POST" '{"player_name":"Test Player","army_list":"This is a valid army list with enough characters"}' $null | Out-Null
    
    # Create new matchup for remaining tests
    $matchup2 = Test-API "Create second matchup" "http://localhost:8000/api/squire/matchup/create" "POST" '{"game_system":"age_of_sigmar"}' $null
    $matchupId2 = $matchup2.matchup_id
    
    # Test 5: Army list too short (THE BUG)
    Test-API "Submit list - too short" "http://localhost:8000/api/squire/matchup/$matchupId2/submit" "POST" '{"player_name":"Player","army_list":"short"}' "at least 10 characters" | Out-Null
    
    # Test 6: Missing player_name
    Test-API "Submit list - missing name" "http://localhost:8000/api/squire/matchup/$matchupId2/submit" "POST" '{"army_list":"Valid army list with enough characters"}' "Field required" | Out-Null
    
    # Test 7: Missing army_list
    Test-API "Submit list - missing list" "http://localhost:8000/api/squire/matchup/$matchupId2/submit" "POST" '{"player_name":"Player"}' "Field required" | Out-Null
}

# Test 8: Non-existent matchup
Write-Host "`nTest 8 Debug:" -ForegroundColor Magenta
Test-API "Submit list - 404" "http://localhost:8000/api/squire/matchup/FAKE_ID_12345/submit" "POST" '{"player_name":"Player","army_list":"Valid list text"}' "not found" | Out-Null

# Summary
$total = $passed + $failed
$passRate = if ($total -gt 0) { [math]::Round(($passed / $total) * 100, 1) } else { 0 }

Write-Host "`n=== TEST SUMMARY ===" -ForegroundColor Cyan
Write-Host "Total:  $total" -ForegroundColor White
Write-Host "Passed: $passed" -ForegroundColor Green
Write-Host "Failed: $failed" -ForegroundColor $(if ($failed -eq 0) { "Green" } else { "Red" })
Write-Host "Rate:   $passRate%" -ForegroundColor White

if ($failedTests.Count -gt 0) {
    Write-Host "`nFailed Tests:" -ForegroundColor Red
    $failedTests | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
}

Write-Host "`n=== END ===" -ForegroundColor Cyan

if ($failed -gt 0) {
    exit 1
}
