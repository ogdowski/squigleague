# Download battle plans from ageofindex.com
# This site has clean, official-looking battle plan diagrams

$missions = @(
    "passing-seasons",
    "paths-of-the-fey",
    "roiling-roots",
    "cyclic-shifts",
    "surge-of-slaughter",
    "linked-ley-lines",
    "noxious-nexus",
    "the-liferoots",
    "bountiful-equinox",
    "lifecycle",
    "creeping-corruption",
    "grasp-of-thorns"
)

$outputDir = "assets\battle-plans-ageofindex"
New-Item -ItemType Directory -Force -Path $outputDir | Out-Null

Write-Host "Downloading battle plans from ageofindex.com..." -ForegroundColor Cyan
Write-Host "=" * 60

foreach ($mission in $missions) {
    $url = "https://www.ageofindex.com/plans/$mission"
    Write-Host "`nMission: $mission" -ForegroundColor Green
    Write-Host "URL: $url"
    
    # Try to download the page and extract image URLs
    # Note: This is a JavaScript site, may need manual download
    Write-Host "  → Please visit URL and save screenshot/image" -ForegroundColor Yellow
}

Write-Host "`n" + ("=" * 60)
Write-Host "MANUAL DOWNLOAD REQUIRED:" -ForegroundColor Yellow
Write-Host "The site uses JavaScript rendering. Please:" -ForegroundColor Gray
Write-Host "1. Visit https://www.ageofindex.com/plans" -ForegroundColor Gray
Write-Host "2. Select each mission from dropdown" -ForegroundColor Gray
Write-Host "3. Take screenshot or right-click → Save image" -ForegroundColor Gray
Write-Host "4. Save to: $outputDir\aos-{mission-name}.png" -ForegroundColor Gray
Write-Host "`nOr use browser DevTools to find image URLs" -ForegroundColor Gray
