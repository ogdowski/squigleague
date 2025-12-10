# Test actual API error response formats
Write-Host "`n=== Testing API Error Response Formats ===" -ForegroundColor Cyan

# Test 1: Invalid game system (HTTPException with string detail)
Write-Host "`n[Test 1] Invalid game system:" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/squire/matchup/create" `
        -Method POST `
        -ContentType "application/json" `
        -Body '{"game_system":"fake_game"}' `
        -ErrorAction Stop
} catch {
    if ($_.ErrorDetails.Message) {
        $errorResponse = $_.ErrorDetails.Message | ConvertFrom-Json
        Write-Host "Status: $($_.Exception.Response.StatusCode.value__)"
        if ($errorResponse.detail) {
            Write-Host "Detail type: $($errorResponse.detail.GetType().Name)"
            Write-Host "Detail value: $($errorResponse.detail)"
        }
        Write-Host "Raw JSON: $($_.ErrorDetails.Message)"
    } else {
        Write-Host "Error: $($_.Exception.Message)"
    }
}

# Test 2: Missing field (Pydantic validation with array detail)
Write-Host "`n[Test 2] Missing game_system field:" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/squire/matchup/create" `
        -Method POST `
        -ContentType "application/json" `
        -Body '{}' `
        -ErrorAction Stop
} catch {
    if ($_.ErrorDetails.Message) {
        $errorResponse = $_.ErrorDetails.Message | ConvertFrom-Json
        Write-Host "Status: $($_.Exception.Response.StatusCode.value__)"
        if ($errorResponse.detail -is [Array]) {
            Write-Host "Detail is array with $($errorResponse.detail.Count) items"
            Write-Host "First error msg: $($errorResponse.detail[0].msg)"
            Write-Host "First error type: $($errorResponse.detail[0].type)"
        }
        Write-Host "Raw JSON: $($_.ErrorDetails.Message)"
    } else {
        Write-Host "Error: $($_.Exception.Message)"
    }
}# Test 3: Create valid matchup for submission tests
Write-Host "`n[Test 3] Creating valid matchup:" -ForegroundColor Yellow
$matchup = Invoke-RestMethod -Uri "http://localhost:8000/api/squire/matchup/create" `
    -Method POST `
    -ContentType "application/json" `
    -Body '{"game_system":"age_of_sigmar"}'
Write-Host "Created matchup: $($matchup.matchup_id)"

# Test 4: Army list too short (Pydantic min_length validation)
Write-Host "`n[Test 4] Army list too short:" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/squire/matchup/$($matchup.matchup_id)/submit" `
        -Method POST `
        -ContentType "application/json" `
        -Body '{"player_name":"Test","army_list":"short"}' `
        -ErrorAction Stop
} catch {
    if ($_.ErrorDetails.Message) {
        $errorResponse = $_.ErrorDetails.Message | ConvertFrom-Json
        Write-Host "Status: $($_.Exception.Response.StatusCode.value__)"
        if ($errorResponse.detail -is [Array]) {
            Write-Host "Detail is array with $($errorResponse.detail.Count) items"
            Write-Host "First error msg: $($errorResponse.detail[0].msg)"
            Write-Host "First error type: $($errorResponse.detail[0].type)"
        }
        Write-Host "Raw JSON: $($_.ErrorDetails.Message)"
    } else {
        Write-Host "Error: $($_.Exception.Message)"
    }
}

# Test 5: Missing player_name (Pydantic required field)
Write-Host "`n[Test 5] Missing player_name:" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/squire/matchup/$($matchup.matchup_id)/submit" `
        -Method POST `
        -ContentType "application/json" `
        -Body '{"army_list":"Valid army list text here"}' `
        -ErrorAction Stop
} catch {
    if ($_.ErrorDetails.Message) {
        $errorResponse = $_.ErrorDetails.Message | ConvertFrom-Json
        Write-Host "Status: $($_.Exception.Response.StatusCode.value__)"
        if ($errorResponse.detail -is [Array]) {
            Write-Host "Detail is array with $($errorResponse.detail.Count) items"
            Write-Host "First error msg: $($errorResponse.detail[0].msg)"
        }
        Write-Host "Raw JSON: $($_.ErrorDetails.Message)"
    } else {
        Write-Host "Error: $($_.Exception.Message)"
    }
}

# Test 6: Non-existent matchup (ValueError -> HTTPException with string detail)
Write-Host "`n[Test 6] Non-existent matchup:" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/squire/matchup/FAKE_ID_123/submit" `
        -Method POST `
        -ContentType "application/json" `
        -Body '{"player_name":"Test","army_list":"Valid list text"}' `
        -ErrorAction Stop
} catch {
    if ($_.ErrorDetails.Message) {
        $errorResponse = $_.ErrorDetails.Message | ConvertFrom-Json
        Write-Host "Status: $($_.Exception.Response.StatusCode.value__)"
        if ($errorResponse.detail) {
            Write-Host "Detail type: $($errorResponse.detail.GetType().Name)"
            Write-Host "Detail value: $($errorResponse.detail)"
        }
        Write-Host "Raw JSON: $($_.ErrorDetails.Message)"
    } else {
        Write-Host "Error: $($_.Exception.Message)"
    }
}

Write-Host "`n=== Done ===" -ForegroundColor Cyan
