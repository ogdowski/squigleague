Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Activity: Generate Enhanced Battle Plans" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/3] Checking dependencies..." -ForegroundColor Yellow

$matplotlibCheck = & .\.venv\Scripts\python.exe -c "import matplotlib; print('OK')" 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "matplotlib not found. Installing..." -ForegroundColor Yellow
    & .\.venv\Scripts\python.exe -m pip install matplotlib numpy --quiet
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to install matplotlib" -ForegroundColor Red
        exit 1
    }
    Write-Host "matplotlib installed" -ForegroundColor Green
} else {
    Write-Host "matplotlib available" -ForegroundColor Green
}

Write-Host ""
Write-Host "[2/3] Generating enhanced battle plan images..." -ForegroundColor Yellow
Write-Host ""

& .\.venv\Scripts\python.exe .\scripts\generate_enhanced_battleplans.py

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Image generation failed" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[3/3] Verifying output..." -ForegroundColor Yellow

$enhancedDir = "frontend\public\assets\battle-plans-enhanced"
if (Test-Path $enhancedDir) {
    $images = Get-ChildItem $enhancedDir -Filter "*.png"
    $imageCount = $images.Count
    $totalSizeBytes = ($images | Measure-Object -Property Length -Sum).Sum
    $totalSizeMB = [math]::Round($totalSizeBytes / 1MB, 2)
    
    Write-Host "Generated $imageCount images" -ForegroundColor Green
    Write-Host "Total size: $totalSizeMB MB" -ForegroundColor Green
    Write-Host "Location: $enhancedDir" -ForegroundColor Green
} else {
    Write-Host "Output directory not found" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Enhanced battle plan generation complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

exit 0
