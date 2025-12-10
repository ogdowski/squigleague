# Browser Automation Test - Actually clicks buttons and tests JavaScript
# Requires: Install-Module -Name Selenium -Scope CurrentUser

param(
    [switch]$SkipSetup
)

$ErrorActionPreference = "Stop"

Write-Host "`n================================================================" -ForegroundColor Cyan
Write-Host "BROWSER AUTOMATION TEST - v0.3.0" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan

# Check if Selenium module is installed
if (-not (Get-Module -ListAvailable -Name Selenium)) {
    Write-Host "`nSelenium module not found. Installing..." -ForegroundColor Yellow
    Install-Module -Name Selenium -Scope CurrentUser -Force -AllowClobber -SkipPublisherCheck
}

Import-Module Selenium

$testResults = @{
    Passed = @()
    Failed = @()
}

function Test-BrowserStep {
    param(
        [string]$Name,
        [scriptblock]$Action
    )
    
    Write-Host "`n[BROWSER TEST] $Name" -ForegroundColor Yellow
    try {
        & $Action
        Write-Host "  PASS" -ForegroundColor Green
        $script:testResults.Passed += $Name
        return $true
    } catch {
        Write-Host "  FAIL: $($_.Exception.Message)" -ForegroundColor Red
        $script:testResults.Failed += "$Name - $($_.Exception.Message)"
        return $false
    }
}

if (-not $SkipSetup) {
    # Cleanup and start servers
    Write-Host "`n[SETUP] Starting servers..." -ForegroundColor Cyan
    Get-Job | Remove-Job -Force -ErrorAction SilentlyContinue
    Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2

    # Start backend
    $env:REQUIRE_DATABASE = "false"
    $backendJob = Start-Job -ScriptBlock {
        Set-Location "e:\repos\suigleague"
        $env:REQUIRE_DATABASE = "false"
        & ".\.venv\Scripts\python.exe" -m uvicorn herald.main:app --reload --port 8000
    }
    Start-Sleep -Seconds 4

    # Start frontend
    $frontendJob = Start-Job -ScriptBlock {
        Set-Location "e:\repos\suigleague\frontend\public"
        python spa-server.py
    }
    Start-Sleep -Seconds 3

    # Wait for servers
    $maxRetries = 10
    $retry = 0
    while ($retry -lt $maxRetries) {
        try {
            Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 2 | Out-Null
            Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 2 | Out-Null
            Write-Host "  Servers ready" -ForegroundColor Green
            break
        } catch {
            $retry++
            if ($retry -eq $maxRetries) {
                throw "Servers failed to start after $maxRetries attempts"
            }
            Start-Sleep -Seconds 1
        }
    }
}

# Start Chrome browser
Write-Host "`n[SETUP] Starting Chrome browser..." -ForegroundColor Cyan
$driver = $null
try {
    $driver = Start-SeChrome -Quiet
    Write-Host "  Chrome started" -ForegroundColor Green
} catch {
    Write-Host "  Chrome failed to start: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "  Trying Edge instead..." -ForegroundColor Yellow
    try {
        $driver = Start-SeEdge -Quiet
        Write-Host "  Edge started" -ForegroundColor Green
    } catch {
        throw "Could not start browser. Install ChromeDriver or EdgeDriver."
    }
}

try {
    # TEST 1: Load homepage
    Test-BrowserStep "Load http://localhost:3000" {
        $driver.Navigate().GoToUrl("http://localhost:3000")
        Start-Sleep -Seconds 2
        
        $pageSource = $driver.PageSource
        if ($pageSource -notmatch "Matchup System") {
            throw "Page doesn't contain expected content"
        }
    }

    # TEST 2: Check for JavaScript errors in console
    Test-BrowserStep "Check browser console for errors" {
        $logs = $driver.Manage().Logs.GetLog("browser")
        $errors = $logs | Where-Object { $_.Level -eq "SEVERE" }
        
        if ($errors) {
            $errorMessages = ($errors | ForEach-Object { $_.Message }) -join "`n"
            throw "Console errors found:`n$errorMessages"
        }
    }

    # TEST 3: Find Create Matchup button
    Test-BrowserStep "Find Create Matchup button" {
        $button = $driver.FindElementByXPath("//button[contains(text(), 'Create Matchup')]")
        if (-not $button) {
            throw "Create Matchup button not found"
        }
        if (-not $button.Enabled) {
            throw "Create Matchup button is disabled"
        }
    }

    # TEST 4: Click Create Matchup button
    $matchupUrl = $null
    Test-BrowserStep "Click Create Matchup button" {
        $button = $driver.FindElementByXPath("//button[contains(text(), 'Create Matchup')]")
        $button.Click()
        
        # Wait for response (max 10 seconds)
        $waited = 0
        $maxWait = 10
        while ($waited -lt $maxWait) {
            Start-Sleep -Seconds 1
            $waited++
            
            # Check if URL changed
            if ($driver.Url -match "/squire/matchup/") {
                Write-Host "    URL changed to: $($driver.Url)" -ForegroundColor Gray
                $script:matchupUrl = $driver.Url
                break
            }
            
            # Check for error message
            try {
                $errorEl = $driver.FindElementByXPath("//*[contains(text(), 'Error')]")
                if ($errorEl.Displayed) {
                    # Get the actual error text
                    $errorBox = $driver.FindElementByXPath("//div[contains(@class, 'bg-red')]")
                    $errorText = $errorBox.Text
                    throw "Error displayed: $errorText"
                }
            } catch [OpenQA.Selenium.NoSuchElementException] {
                # No error found, continue waiting
            }
        }
        
        if (-not $script:matchupUrl) {
            # Take screenshot for debugging
            $screenshot = $driver.GetScreenshot()
            $screenshotPath = "e:\repos\suigleague\test-failure-screenshot.png"
            $screenshot.SaveAsFile($screenshotPath, [System.Drawing.Imaging.ImageFormat]::Png)
            
            throw "URL did not change after clicking button. Screenshot saved to $screenshotPath"
        }
    }

    # TEST 5: Verify share link appears
    Test-BrowserStep "Verify share link input appears" {
        try {
            $shareInput = $driver.FindElementByXPath("//input[@readonly]")
            if (-not $shareInput.Displayed) {
                throw "Share link input not visible"
            }
            
            $shareValue = $shareInput.GetAttribute("value")
            Write-Host "    Share link: $shareValue" -ForegroundColor Gray
            
            if (-not $shareValue -or $shareValue.Length -lt 10) {
                throw "Share link value is empty or invalid"
            }
        } catch [OpenQA.Selenium.NoSuchElementException] {
            throw "Share link input not found in DOM"
        }
    }

    # TEST 6: Check console for errors after button click
    Test-BrowserStep "Verify no console errors after button click" {
        $logs = $driver.Manage().Logs.GetLog("browser")
        $errors = $logs | Where-Object { $_.Level -eq "SEVERE" }
        
        if ($errors) {
            $errorMessages = ($errors | ForEach-Object { $_.Message }) -join "`n"
            throw "Console errors after button click:`n$errorMessages"
        }
    }

    # TEST 7: Open matchup URL in new window
    Test-BrowserStep "Open matchup URL in new window" {
        if (-not $script:matchupUrl) {
            throw "No matchup URL to test"
        }
        
        # Open new window
        $driver.ExecuteScript("window.open('');")
        $handles = $driver.WindowHandles
        $driver.SwitchTo().Window($handles[1])
        
        # Navigate to matchup URL
        $driver.Navigate().GoToUrl($script:matchupUrl)
        Start-Sleep -Seconds 2
        
        # Verify no error page
        $pageSource = $driver.PageSource
        if ($pageSource -match "404" -or $pageSource -match "Not Found") {
            throw "Matchup URL shows 404 error"
        }
        
        # Switch back to original window
        $driver.SwitchTo().Window($handles[0])
    }

    # TEST 8: Fill and submit Player 1 form
    Test-BrowserStep "Submit Player 1 army list" {
        # Find name input
        $nameInput = $driver.FindElementByXPath("//input[@x-model='playerName' or @placeholder='Your Name']")
        $nameInput.SendKeys("Automated Test Player 1")
        
        # Find army list textarea
        $listTextarea = $driver.FindElementByXPath("//textarea[@x-model='armyList' or contains(@placeholder, 'army list')]")
        $listTextarea.SendKeys("Test Army List for Player 1`nThis has enough characters to pass validation")
        
        # Click submit
        $submitBtn = $driver.FindElementByXPath("//button[contains(text(), 'Submit')]")
        $submitBtn.Click()
        
        # Wait for response
        Start-Sleep -Seconds 2
        
        # Check for success (waiting message should appear)
        try {
            $waitingText = $driver.FindElementByXPath("//*[contains(text(), 'Waiting') or contains(text(), 'opponent')]")
            Write-Host "    Status: Waiting for opponent" -ForegroundColor Gray
        } catch {
            # Check for error
            try {
                $errorEl = $driver.FindElementByXPath("//div[contains(@class, 'bg-red')]")
                if ($errorEl.Displayed) {
                    throw "Error after submit: $($errorEl.Text)"
                }
            } catch [OpenQA.Selenium.NoSuchElementException] {
                # No obvious error or waiting message - might be OK
                Write-Host "    Form submitted (no obvious error)" -ForegroundColor Gray
            }
        }
    }

} finally {
    # Cleanup
    Write-Host "`n[CLEANUP]" -ForegroundColor Cyan
    if ($driver) {
        Write-Host "  Closing browser..." -ForegroundColor Gray
        $driver.Quit()
    }
}

# Results
Write-Host "`n================================================================" -ForegroundColor Cyan
Write-Host "BROWSER AUTOMATION TEST RESULTS" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "PASSED: $($testResults.Passed.Count)" -ForegroundColor Green
foreach ($test in $testResults.Passed) {
    Write-Host "  $test" -ForegroundColor Green
}

if ($testResults.Failed.Count -gt 0) {
    Write-Host "`nFAILED: $($testResults.Failed.Count)" -ForegroundColor Red
    foreach ($test in $testResults.Failed) {
        Write-Host "  $test" -ForegroundColor Red
    }
    
    Write-Host "`nServers are still running for manual debugging." -ForegroundColor Yellow
    Write-Host "Frontend: http://localhost:3000" -ForegroundColor Yellow
    Write-Host "Backend: http://localhost:8000" -ForegroundColor Yellow
    exit 1
} else {
    Write-Host "`nAll browser tests passed!" -ForegroundColor Green
    Write-Host "`nServers are still running." -ForegroundColor Cyan
    Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
    Write-Host "Backend: http://localhost:8000" -ForegroundColor Cyan
}
