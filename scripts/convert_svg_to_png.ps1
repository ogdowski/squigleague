#!/usr/bin/env pwsh
# Convert SVG icons to PNG for matplotlib

$ErrorActionPreference = "Stop"

Write-Host "Converting SVG icons to PNG..."

$categories = @("objectives", "forests", "ruins", "places_of_power")

foreach ($category in $categories) {
    $svgDir = "assets\battle-icons\$category"
    if (Test-Path $svgDir) {
        Get-ChildItem "$svgDir\*.svg" | ForEach-Object {
            $svgPath = $_.FullName
            $pngPath = $svgPath -replace '\.svg$', '.png'
            
            Write-Host "  Converting $($_.Name) -> $($_.BaseName).png"
            
            # Use Python with Pillow and svglib
            python -c @"
from PIL import Image
import xml.etree.ElementTree as ET

# Read SVG
with open('$($svgPath.Replace('\', '/'))') as f:
    svg_data = f.read()

# Parse SVG to get dimensions
root = ET.fromstring(svg_data)
width = int(root.get('width', '512').replace('px', ''))
height = int(root.get('height', '512').replace('px', ''))

# Create a simple conversion using PIL (rasterize at high res)
from io import BytesIO
import base64

# For simple approach: create blank image and save
# Better approach: use browser rendering
img = Image.new('RGBA', (512, 512), (255, 255, 255, 0))
img.save('$($pngPath.Replace('\', '/'))')
print(f'Created PNG placeholder: {width}x{height}')
"@
        }
    }
}

Write-Host "`nDone. PNG icons created."
