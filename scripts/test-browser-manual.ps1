# Simple Browser Test - Uses Edge/Chrome with DevTools Protocol
# No Selenium required - uses native browser automation

$ErrorActionPreference = "Stop"

Write-Host "`n================================================================" -ForegroundColor Cyan
Write-Host "BROWSER JAVASCRIPT TEST - v0.3.0" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan

# Check servers
Write-Host "`n[CHECK] Verifying servers are running..." -ForegroundColor Cyan
try {
    Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 2 | Out-Null
    Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 2 | Out-Null
    Write-Host "  Servers OK" -ForegroundColor Green
} catch {
    Write-Host "  Servers not running!" -ForegroundColor Red
    Write-Host "  Run: .\scripts\test-comprehensive-gui.ps1" -ForegroundColor Yellow
    exit 1
}

# Find Edge
$edgePath = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if (-not (Test-Path $edgePath)) {
    $edgePath = "C:\Program Files\Microsoft\Edge\Application\msedge.exe"
}

if (-not (Test-Path $edgePath)) {
    Write-Host "Microsoft Edge not found. Opening default browser..." -ForegroundColor Yellow
    Start-Process "http://localhost:3000"
    Write-Host ""
    Write-Host "MANUAL TEST REQUIRED:" -ForegroundColor Yellow
    Write-Host "1. Click 'Create Matchup' button" -ForegroundColor White
    Write-Host "2. Open DevTools (F12)" -ForegroundColor White
    Write-Host "3. Check Console tab for errors" -ForegroundColor White
    Write-Host "4. Screenshot any errors and report" -ForegroundColor White
    exit 0
}

Write-Host "`n[TEST] Opening Edge with remote debugging..." -ForegroundColor Cyan
# Start Edge with remote debugging enabled
$port = 9222
$userDataDir = "$env:TEMP\edge-test-profile"

# Clean old profile
if (Test-Path $userDataDir) {
    Remove-Item $userDataDir -Recurse -Force -ErrorAction SilentlyContinue
}

# Start Edge
$edgeArgs = @(
    "--remote-debugging-port=$port",
    "--user-data-dir=$userDataDir",
    "--no-first-run",
    "--no-default-browser-check",
    "http://localhost:3000"
)

$edgeProcess = Start-Process -FilePath $edgePath -ArgumentList $edgeArgs -PassThru
Start-Sleep -Seconds 3

Write-Host "  Edge started (PID: $($edgeProcess.Id))" -ForegroundColor Green
Write-Host "  Remote debugging on port $port" -ForegroundColor Gray

# Connect to Chrome DevTools Protocol
Write-Host "`n[TEST] Connecting to DevTools Protocol..." -ForegroundColor Cyan
try {
    $devtoolsJson = Invoke-RestMethod -Uri "http://localhost:$port/json" -TimeoutSec 5
    $pageTab = $devtoolsJson | Where-Object { $_.type -eq 'page' } | Select-Object -First 1
    
    if (-not $pageTab) {
        throw "No page tab found"
    }
    
    Write-Host "  Connected to tab: $($pageTab.title)" -ForegroundColor Green
    Write-Host "  URL: $($pageTab.url)" -ForegroundColor Gray
    
    # Get WebSocket debugger URL
    $wsUrl = $pageTab.webSocketDebuggerUrl
    Write-Host "  WebSocket: $wsUrl" -ForegroundColor Gray
    
} catch {
    Write-Host "  Failed to connect: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "BROWSER IS OPEN - MANUAL TEST:" -ForegroundColor Yellow
    Write-Host "1. Press F12 to open DevTools" -ForegroundColor White
    Write-Host "2. Go to Console tab" -ForegroundColor White
    Write-Host "3. Click 'Create Matchup' button" -ForegroundColor White
    Write-Host "4. Check for any red error messages" -ForegroundColor White
    Write-Host "5. Screenshot and report errors" -ForegroundColor White
    Write-Host ""
    Write-Host "Press Enter when done testing..." -ForegroundColor Yellow
    Read-Host
    
    $edgeProcess.Kill()
    exit 0
}

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "MANUAL BROWSER TESTING" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Edge is open at http://localhost:3000" -ForegroundColor Green
Write-Host ""
Write-Host "PERFORM THESE TESTS:" -ForegroundColor Yellow
Write-Host "1. Press F12 to open DevTools" -ForegroundColor White
Write-Host "2. Select Console tab" -ForegroundColor White
Write-Host "3. Click the 'Create Matchup' button" -ForegroundColor White
Write-Host "4. Watch for:" -ForegroundColor White
Write-Host "   - Red error messages in console" -ForegroundColor Gray
Write-Host "   - Error banner on page" -ForegroundColor Gray
Write-Host "   - URL should change to /squire/matchup/..." -ForegroundColor Gray
Write-Host "   - Share link should appear" -ForegroundColor Gray
Write-Host ""
Write-Host "5. If you see '[object Object]' error:" -ForegroundColor White
Write-Host "   - Look at console for actual error" -ForegroundColor Gray
Write-Host "   - Copy the full error message" -ForegroundColor Gray
Write-Host ""
Write-Host "Press Enter when done testing..." -ForegroundColor Yellow
Read-Host

# Cleanup
Write-Host "`n[CLEANUP] Closing browser..." -ForegroundColor Cyan
$edgeProcess.Kill()
Start-Sleep -Seconds 1

Write-Host ""
Write-Host "Did you see any errors? (Y/N): " -NoNewline -ForegroundColor Yellow
$sawErrors = Read-Host

if ($sawErrors -eq 'Y' -or $sawErrors -eq 'y') {
    Write-Host ""
    Write-Host "Please provide the error details:" -ForegroundColor Yellow
    Write-Host "(Paste the console error, then press Enter twice)" -ForegroundColor Gray
    $errorLines = @()
    while ($true) {
        $line = Read-Host
        if ([string]::IsNullOrWhiteSpace($line)) { break }
        $errorLines += $line
    }
    
    if ($errorLines) {
        $errorReport = $errorLines -join "`n"
        Write-Host ""
        Write-Host "ERROR REPORT:" -ForegroundColor Red
        Write-Host "================================================================" -ForegroundColor Red
        Write-Host $errorReport -ForegroundColor White
        Write-Host "================================================================" -ForegroundColor Red
        
        # Save to file
        $reportPath = "e:\repos\suigleague\test-error-report.txt"
        $errorReport | Out-File -FilePath $reportPath -Encoding UTF8
        Write-Host ""
        Write-Host "Error saved to: $reportPath" -ForegroundColor Yellow
    }
    
    exit 1
} else {
    Write-Host ""
    Write-Host "Great! All tests passed." -ForegroundColor Green
    exit 0
}
