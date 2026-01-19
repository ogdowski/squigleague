#!/usr/bin/env python3
"""Convert SVG icons to PNG using Selenium + Chrome headless."""
import time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Setup Chrome headless
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=512,512')

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
        
        # Screenshot
        png_path = svg_dir / f'{svg_file.stem}.png'
        driver.save_screenshot(str(png_path))
        
        # Cleanup
        temp_html.unlink()
        
        print(f"    Created {png_path.name}")

driver.quit()
print("\nDone!")
