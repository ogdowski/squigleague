#!/usr/bin/env pwsh
# Download free battle plan icons from game-icons.net and create gallery

$ErrorActionPreference = "Stop"

# Create directories
$iconDir = "assets/battle-icons"
$galleryDir = "assets/icon-gallery"
New-Item -ItemType Directory -Force -Path $iconDir | Out-Null
New-Item -ItemType Directory -Force -Path $galleryDir | Out-Null

Write-Host "Downloading icons from game-icons.net (CC BY 3.0 license)..."

# Icon collections with working game-icons.net direct download URLs
$icons = @{
    objectives = @(
        @{name="crosshair"; url="https://api.iconify.design/game-icons/crosshair.svg?color=%23808080"}
    )
    forests = @(
        @{name="oak"; url="https://api.iconify.design/game-icons/oak.svg?color=%23808080"}
    )
    ruins = @(
        @{name="stone-tower"; url="https://api.iconify.design/game-icons/stone-tower.svg?color=%23808080"}
    )
    places_of_power = @(
        @{name="magic-portal"; url="https://api.iconify.design/game-icons/magic-portal.svg?color=%23808080"}
    )
}

# Download all icons
foreach ($category in $icons.Keys) {
    Write-Host "`nDownloading $category..."
    $categoryDir = Join-Path $iconDir $category
    New-Item -ItemType Directory -Force -Path $categoryDir | Out-Null
    
    foreach ($icon in $icons[$category]) {
        $filename = "$($icon.name).svg"
        $outPath = Join-Path $categoryDir $filename
        Write-Host "  - $filename"
        try {
            Invoke-WebRequest -Uri $icon.url -OutFile $outPath -UseBasicParsing -TimeoutSec 10
        } catch {
            Write-Host "    ERROR: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
}

# Create HTML gallery
$html = @"
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Battle Plan Icons Gallery</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            margin: 0;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        }
        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 10px;
        }
        .attribution {
            text-align: center;
            color: #666;
            font-size: 14px;
            margin-bottom: 30px;
        }
        .attribution a {
            color: #667eea;
            text-decoration: none;
        }
        .category {
            margin-bottom: 40px;
        }
        .category h2 {
            color: #764ba2;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        .icon-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            gap: 20px;
        }
        .icon-card {
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            padding: 15px;
            text-align: center;
            transition: all 0.3s ease;
            background: white;
        }
        .icon-card:hover {
            border-color: #667eea;
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
            transform: translateY(-5px);
        }
        .icon-card img {
            width: 80px;
            height: 80px;
            margin-bottom: 10px;
            filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
        }
        .icon-name {
            font-size: 12px;
            color: #666;
            word-wrap: break-word;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Battle Plan Icons Gallery</h1>
        <div class="attribution">
            Icons from <a href="https://game-icons.net" target="_blank">game-icons.net</a> 
            (CC BY 3.0 License)
        </div>
"@

foreach ($category in $icons.Keys) {
    $displayName = ($category -replace "_", " ").ToUpper()
    $html += "`n        <div class='category'>`n"
    $html += "            <h2>$displayName</h2>`n"
    $html += "            <div class='icon-grid'>`n"
    
    foreach ($icon in $icons[$category]) {
        $iconPath = "../battle-icons/$category/$($icon.name).svg"
        $html += "                <div class='icon-card'>`n"
        $html += "                    <img src='$iconPath' alt='$($icon.name)'>`n"
        $html += "                    <div class='icon-name'>$($icon.name)</div>`n"
        $html += "                </div>`n"
    }
    
    $html += "            </div>`n"
    $html += "        </div>`n"
}

$html += @"
    </div>
</body>
</html>
"@

$galleryPath = Join-Path $galleryDir "index.html"
$html | Out-File -FilePath $galleryPath -Encoding UTF8

Write-Host "`n============================================"
Write-Host "Gallery created: $galleryPath" -ForegroundColor Green
Write-Host "============================================"

# Open gallery
Start-Process $galleryPath
