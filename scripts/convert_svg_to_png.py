#!/usr/bin/env python3
"""Convert SVG icons to PNG using Selenium + Chrome headless."""
import time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
from io import BytesIO

# Setup Chrome headless
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=512,512')
options.add_argument('--force-device-scale-factor=1')

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Icon directories
categories = {
    'objectives': Path('../assets/battle-icons/objectives'),
    'forests': Path('../assets/battle-icons/forests'),
    'ruins': Path('../assets/battle-icons/ruins'),
    'places_of_power': Path('../assets/battle-icons/places_of_power'),
}

html_template = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ margin: 0; padding: 0; width: 512px; height: 512px; }}
        svg {{ width: 100%; height: 100%; display: block; }}
    </style>
</head>
<body>{svg_content}</body>
</html>
"""

print("Converting SVG to PNG using Chrome headless...")

for category, svg_dir in categories.items():
    if not svg_dir.exists():
        continue
    
    for svg_file in svg_dir.glob('*.svg'):
        print(f"  Converting {svg_file.name}...")
        
        # Read SVG
        svg_content = svg_file.read_text(encoding='utf-8')
        html = html_template.format(svg_content=svg_content)
        
        # Create temp HTML
        temp_html = svg_dir / f'temp_{svg_file.stem}.html'
        temp_html.write_text(html, encoding='utf-8')
        
        # Load in browser
        driver.get(f'file:///{temp_html.absolute()}')
        time.sleep(0.5)
        
        # Screenshot to bytes
        png_bytes = driver.get_screenshot_as_png()
        
        # Convert white to transparent
        img = Image.open(BytesIO(png_bytes)).convert('RGBA')
        data = img.getdata()
        new_data = []
        for item in data:
            # Change white (also shades of white) to transparent
            if item[0] > 240 and item[1] > 240 and item[2] > 240:
                new_data.append((255, 255, 255, 0))
            else:
                new_data.append(item)
        img.putdata(new_data)
        
        # Save with transparency
        png_path = svg_dir / f'{svg_file.stem}.png'
        img.save(str(png_path), 'PNG')
        
        # Cleanup
        temp_html.unlink()
        
        print(f"    Created {png_path.name}")

driver.quit()
print("\nDone!")
