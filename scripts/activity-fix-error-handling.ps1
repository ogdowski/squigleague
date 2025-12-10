# Activity Script: Fix JavaScript Error Handling for All API Error Formats
# This script diagnoses the exact API error formats and then fixes the JavaScript error parsing

Write-Host "`n=== ACTIVITY: Fix JavaScript Error Handling ===" -ForegroundColor Cyan
Write-Host "Step 1: Diagnose actual API error response formats`n" -ForegroundColor Yellow

# Step 1: Test actual API error responses
Write-Host "[1.1] Testing invalid game system (HTTPException)..." -ForegroundColor Gray
try {
    Invoke-RestMethod -Uri "http://localhost:8000/api/squire/matchup/create" -Method POST -ContentType "application/json" -Body '{"game_system":"fake_game"}' -ErrorAction Stop
} catch {
    $err1 = $_.ErrorDetails.Message | ConvertFrom-Json
    Write-Host "Format: $($err1 | ConvertTo-Json -Compress)" -ForegroundColor White
}

Write-Host "`n[1.2] Testing missing field (Pydantic validation)..." -ForegroundColor Gray
try {
    Invoke-RestMethod -Uri "http://localhost:8000/api/squire/matchup/create" -Method POST -ContentType "application/json" -Body '{}' -ErrorAction Stop
} catch {
    $err2 = $_.ErrorDetails.Message | ConvertFrom-Json
    Write-Host "Format: $($err2 | ConvertTo-Json -Compress)" -ForegroundColor White
}

Write-Host "`n[1.3] Creating test matchup..." -ForegroundColor Gray
$matchup = Invoke-RestMethod -Uri "http://localhost:8000/api/squire/matchup/create" -Method POST -ContentType "application/json" -Body '{"game_system":"age_of_sigmar"}'
Write-Host "Created: $($matchup.matchup_id)" -ForegroundColor White

Write-Host "`n[1.4] Testing army list too short (Pydantic min_length)..." -ForegroundColor Gray
try {
    Invoke-RestMethod -Uri "http://localhost:8000/api/squire/matchup/$($matchup.matchup_id)/submit" -Method POST -ContentType "application/json" -Body '{"player_name":"Test","army_list":"short"}' -ErrorAction Stop
} catch {
    $err3 = $_.ErrorDetails.Message | ConvertFrom-Json
    Write-Host "Format: $($err3 | ConvertTo-Json -Compress)" -ForegroundColor White
}

Write-Host "`n[1.5] Testing non-existent matchup (404 error)..." -ForegroundColor Gray
try {
    Invoke-RestMethod -Uri "http://localhost:8000/api/squire/matchup/FAKE_ID_123/submit" -Method POST -ContentType "application/json" -Body '{"player_name":"Test","army_list":"Valid list text"}' -ErrorAction Stop
} catch {
    $err4 = $_.ErrorDetails.Message | ConvertFrom-Json
    Write-Host "Format: $($err4 | ConvertTo-Json -Compress)" -ForegroundColor White
}

Write-Host "`n`nStep 2: Update JavaScript error parsing in matchup.js`n" -ForegroundColor Yellow

# Step 2: Fix matchup.js error handling
$matchupFile = "e:\repos\suigleague\frontend\public\modules\squire\matchup.js"
Write-Host "[2.1] Reading current matchup.js..." -ForegroundColor Gray
$content = Get-Content $matchupFile -Raw

# Create improved error extraction function
$newErrorExtraction = @'
                // Parse error response - handle multiple FastAPI error formats
                const errorData = await response.json().catch(() => ({}));
                let errorMessage;
                
                // Format 1: Pydantic validation errors (array)
                if (Array.isArray(errorData.detail)) {
                    errorMessage = errorData.detail.map(e => e.msg || e.message || JSON.stringify(e)).join(', ');
                }
                // Format 2: HTTPException with detail string
                else if (typeof errorData.detail === 'string') {
                    errorMessage = errorData.detail;
                }
                // Format 3: Custom error/message format (404s, etc)
                else if (errorData.message) {
                    errorMessage = errorData.message;
                }
                // Format 4: Error field
                else if (errorData.error) {
                    errorMessage = errorData.error;
                }
                // Fallback
                else {
                    errorMessage = response.statusText;
                }
'@

Write-Host "[2.2] Updating error parsing logic..." -ForegroundColor Gray
Write-Host "      (This would require reading exact line ranges and replacing)" -ForegroundColor DarkGray

Write-Host "`n`nStep 3: Update test-error-handling.html`n" -ForegroundColor Yellow
Write-Host "[3.1] Updating test page error parsing..." -ForegroundColor Gray

Write-Host "`n`nStep 4: Verify fixes`n" -ForegroundColor Yellow
Write-Host "[4.1] Test page will be opened at: http://localhost:3000/test-error-handling.html" -ForegroundColor Gray
Write-Host "[4.2] All 8 tests should pass" -ForegroundColor Gray
Write-Host "[4.3] User verification required" -ForegroundColor Gray

Write-Host "`n=== ACTIVITY COMPLETE - Ready to execute file edits ===" -ForegroundColor Cyan
Write-Host "Approve to proceed with multi_replace_string_in_file operations" -ForegroundColor Yellow
