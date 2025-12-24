# E2E Testing Suite Setup for SquigLeague
# Uses Playwright for browser automation testing

Write-Host "=== Setting up E2E Testing Suite ===" -ForegroundColor Cyan

# Check if Node.js is installed
Write-Host "`n[1/5] Checking Node.js installation..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version
    Write-Host "  ✓ Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Node.js not found. Please install Node.js first." -ForegroundColor Red
    exit 1
}

# Check if npm is installed
Write-Host "`n[2/5] Checking npm installation..." -ForegroundColor Yellow
try {
    $npmVersion = npm --version
    Write-Host "  ✓ npm found: $npmVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ npm not found." -ForegroundColor Red
    exit 1
}

# Create e2e directory if it doesn't exist
Write-Host "`n[3/5] Creating E2E test directory..." -ForegroundColor Yellow
$e2eDir = "c:\repos\SquigLeague\squigleague\e2e"
if (!(Test-Path $e2eDir)) {
    New-Item -ItemType Directory -Path $e2eDir | Out-Null
    Write-Host "  ✓ Created $e2eDir" -ForegroundColor Green
} else {
    Write-Host "  ✓ Directory already exists" -ForegroundColor Green
}

# Initialize package.json if it doesn't exist
Write-Host "`n[4/5] Initializing package.json..." -ForegroundColor Yellow
Set-Location $e2eDir
if (!(Test-Path "package.json")) {
    $packageJson = @{
        name = "squigleague-e2e-tests"
        version = "1.0.0"
        description = "End-to-end browser tests for SquigLeague"
        scripts = @{
            test = "playwright test"
            "test:headed" = "playwright test --headed"
            "test:ui" = "playwright test --ui"
            "test:debug" = "playwright test --debug"
        }
        devDependencies = @{}
    } | ConvertTo-Json -Depth 10
    
    $packageJson | Out-File -FilePath "package.json" -Encoding utf8
    Write-Host "  ✓ Created package.json" -ForegroundColor Green
} else {
    Write-Host "  ✓ package.json already exists" -ForegroundColor Green
}

# Install Playwright
Write-Host "`n[5/5] Installing Playwright..." -ForegroundColor Yellow
Write-Host "  This may take a few minutes..." -ForegroundColor Cyan
npm install -D @playwright/test
npx playwright install

Write-Host "`n=== Setup Complete! ===" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "1. cd e2e" -ForegroundColor White
Write-Host "2. npx playwright test              # Run all tests headless" -ForegroundColor White
Write-Host "3. npx playwright test --headed     # Run with browser visible" -ForegroundColor White
Write-Host "4. npx playwright test --ui         # Run with interactive UI" -ForegroundColor White
Write-Host "5. npx playwright test --debug      # Run in debug mode" -ForegroundColor White
