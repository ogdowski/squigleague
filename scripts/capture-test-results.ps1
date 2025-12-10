# Automated test result capture using browser console logging
# Requires: selenium WebDriver for PowerShell (or puppeteer alternative)

Write-Host "Attempting to capture test results from browser console..." -ForegroundColor Cyan

# Check if Selenium is available
try {
    Import-Module Selenium -ErrorAction Stop
    $seleniumAvailable = $true
} catch {
    $seleniumAvailable = $false
    Write-Host "Selenium module not available - trying curl approach" -ForegroundColor Yellow
}

if ($seleniumAvailable) {
    Write-Host "Using Selenium WebDriver..." -ForegroundColor Green
    
    $driver = Start-SeChrome -Headless
    
    try {
        Enter-SeUrl -Driver $driver -Url "http://localhost:3000/test-error-handling.html"
        
        # Wait for tests to complete (max 30 seconds)
        Start-Sleep -Seconds 5
        
        # Get console logs
        $logs = Get-SeDriverLog -Driver $driver -LogType Browser
        
        Write-Host "`n=== BROWSER CONSOLE OUTPUT ===" -ForegroundColor Cyan
        foreach ($log in $logs) {
            if ($log.Message -match "TEST") {
                Write-Host $log.Message
            }
        }
        
        # Try to get results from window object
        $results = Invoke-SeJavascript -Driver $driver -Script "return window.testResults;"
        
        if ($results) {
            Write-Host "`n=== TEST RESULTS ===" -ForegroundColor Cyan
            Write-Host "Total: $($results.total)" -ForegroundColor White
            Write-Host "Passed: $($results.passed)" -ForegroundColor Green
            Write-Host "Failed: $($results.failed)" -ForegroundColor Red
            Write-Host "Pass Rate: $($results.passRate)%" -ForegroundColor White
            
            if ($results.failedTests.Count -gt 0) {
                Write-Host "`nFailed Tests:" -ForegroundColor Red
                $results.failedTests | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
            }
        }
        
    } finally {
        Stop-SeDriver -Driver $driver
    }
    
} else {
    Write-Host "`nSelenium not available. Install with:" -ForegroundColor Yellow
    Write-Host "  Install-Module Selenium -Scope CurrentUser" -ForegroundColor White
    Write-Host "`nAlternatively, check browser console manually at:" -ForegroundColor Yellow
    Write-Host "  http://localhost:3000/test-error-handling.html" -ForegroundColor White
    Write-Host "`nLook for lines containing:" -ForegroundColor Yellow
    Write-Host "  === TEST RESULTS ===" -ForegroundColor White
}
