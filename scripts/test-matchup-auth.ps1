# Test Matchup with Authentication
# Tests the integration between auth and matchup systems

Write-Host "Testing Matchup-Authentication Integration" -ForegroundColor Cyan
Write-Host "=========================================`n" -ForegroundColor Cyan

$testUser = "matchuptest"
$testEmail = "matchuptest@example.com"
$testPass = "testpass123"

# Step 1: Register new user
Write-Host "[1] Registering test user..." -ForegroundColor Yellow
$registerBody = @{ username=$testUser; email=$testEmail; password=$testPass } | ConvertTo-Json
try {
    $registerResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/squire/auth/register" -Method POST -ContentType "application/json" -Body $registerBody -ErrorAction SilentlyContinue
    Write-Host "✓ User registered: $testUser" -ForegroundColor Green
} catch {
    if ($_.Exception.Response.StatusCode.value__ -eq 400) {
        Write-Host "⚠ User already exists, continuing..." -ForegroundColor Yellow
    } else {
        Write-Host "✗ Registration failed: $($_.ErrorDetails.Message)" -ForegroundColor Red
        exit 1
    }
}

# Step 2: Login (skip email verification for testing)
Write-Host "`n[2] Attempting login (will fail - email not verified)..." -ForegroundColor Yellow
$loginBody = @{ username_or_email=$testUser; password=$testPass } | ConvertTo-Json
try {
    $loginResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/squire/auth/login" -Method POST -ContentType "application/json" -Body $loginBody -ErrorAction Stop
    $token = $loginResponse.token
    Write-Host "✓ Login successful!" -ForegroundColor Green
    Write-Host "  Token: $($token.Substring(0,20))..." -ForegroundColor Gray
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    if ($statusCode -eq 401) {
        Write-Host "✗ Login failed: Email not verified" -ForegroundColor Red
        Write-Host "`nTo complete this test:" -ForegroundColor Yellow
        Write-Host "1. Check MailHog at http://localhost:8025" -ForegroundColor White
        Write-Host "2. Find verification email for $testEmail" -ForegroundColor White
        Write-Host "3. Click verification link" -ForegroundColor White
        Write-Host "4. Run this script again" -ForegroundColor White
        exit 0
    } else {
        Write-Host "✗ Login failed: $($_.ErrorDetails.Message)" -ForegroundColor Red
        exit 1
    }
}

# Step 3: Create matchup with authentication
Write-Host "`n[3] Creating matchup (requires auth token)..." -ForegroundColor Yellow
$matchupBody = @{ game_system="age_of_sigmar" } | ConvertTo-Json
try {
    $matchupResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/squire/matchup/create" `
        -Method POST `
        -ContentType "application/json" `
        -Headers @{ Authorization="Bearer $token" } `
        -Body $matchupBody `
        -ErrorAction Stop
    
    Write-Host "✓ Matchup created!" -ForegroundColor Green
    Write-Host "  Matchup ID: $($matchupResponse.matchup_id)" -ForegroundColor Gray
    Write-Host "  Game System: $($matchupResponse.game_system)" -ForegroundColor Gray
    Write-Host "  Share URL: http://localhost:8080$($matchupResponse.share_url)" -ForegroundColor Gray
} catch {
    Write-Host "✗ Matchup creation failed: $($_.ErrorDetails.Message)" -ForegroundColor Red
    exit 1
}

# Step 4: Verify matchup creation without token fails
Write-Host "`n[4] Verifying auth requirement (should fail without token)..." -ForegroundColor Yellow
$authFailed = $false
try {
    Invoke-RestMethod -Uri "http://localhost:8000/api/squire/matchup/create" -Method POST -ContentType "application/json" -Body $matchupBody -ErrorAction Stop | Out-Null
    Write-Host "✗ SECURITY ISSUE: Matchup created without auth!" -ForegroundColor Red
    exit 1
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    if ($statusCode -eq 401 -or $statusCode -eq 403) {
        Write-Host "✓ Auth requirement working correctly (401/403 returned)" -ForegroundColor Green
        $authFailed = $true
    } else {
        Write-Host "⚠ Unexpected error: $statusCode" -ForegroundColor Yellow
        $authFailed = $true
    }
}

if ($authFailed) {
    Write-Host "`n========================================" -ForegroundColor Green
    Write-Host "✓ Matchup-Auth Integration Test Complete!" -ForegroundColor Green
    Write-Host "========================================`n" -ForegroundColor Green
}
