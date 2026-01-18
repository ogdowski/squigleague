"""Generate battle-plans-demo.html with proper validation"""

missions = [
    ('Passing Seasons', 'passing-seasons', [
        {'type': 'objective', 'name': 'Gnarlroot 1', 'x': 15, 'y': 18, 'color': 'green'},
        {'type': 'objective', 'name': 'Oakenbrow 1', 'x': 45, 'y': 18, 'color': 'brown'},
        {'type': 'objective', 'name': 'Gnarlroot 2', 'x': 15, 'y': 26, 'color': 'green'},
        {'type': 'objective', 'name': 'Oakenbrow 2', 'x': 45, 'y': 26, 'color': 'brown'},
    ]),
    ('Paths of the Fey', 'paths-of-the-fey', [
        {'type': 'objective', 'name': 'Heartwood', 'x': 30, 'y': 22, 'color': 'gold'},
        {'type': 'objective', 'name': 'Gnarlroot', 'x': 18, 'y': 22, 'color': 'green'},
        {'type': 'objective', 'name': 'Oakenbrow', 'x': 42, 'y': 22, 'color': 'brown'},
        {'type': 'objective', 'name': 'Winterleaf 1', 'x': 30, 'y': 14, 'color': 'blue'},
        {'type': 'objective', 'name': 'Winterleaf 2', 'x': 30, 'y': 30, 'color': 'blue'},
    ]),
    ('Roiling Roots', 'roiling-roots', [
        {'type': 'objective', 'name': 'Obj 1', 'x': 10, 'y': 7, 'color': 'gold'},
        {'type': 'objective', 'name': 'Obj 2', 'x': 20, 'y': 13, 'color': 'gold'},
        {'type': 'objective', 'name': 'Obj 3', 'x': 30, 'y': 19, 'color': 'gold'},
        {'type': 'objective', 'name': 'Obj 4', 'x': 40, 'y': 25, 'color': 'gold'},
        {'type': 'objective', 'name': 'Obj 5', 'x': 50, 'y': 31, 'color': 'gold'},
        {'type': 'objective', 'name': 'Obj 6', 'x': 60, 'y': 37, 'color': 'gold'},
    ]),
    ('Cyclic Shifts', 'cyclic-shifts', [
        {'type': 'objective', 'name': 'Obj 1', 'x': 15, 'y': 12, 'color': 'gold'},
        {'type': 'objective', 'name': 'Obj 2', 'x': 25, 'y': 18, 'color': 'gold'},
        {'type': 'objective', 'name': 'Obj 3', 'x': 35, 'y': 24, 'color': 'gold'},
        {'type': 'objective', 'name': 'Obj 4', 'x': 25, 'y': 26, 'color': 'gold'},
        {'type': 'objective', 'name': 'Obj 5', 'x': 35, 'y': 32, 'color': 'gold'},
        {'type': 'objective', 'name': 'Obj 6', 'x': 45, 'y': 38, 'color': 'gold'},
    ]),
    ('Surge of Slaughter', 'surge-of-slaughter', [
        {'type': 'objective', 'name': 'Heartwood', 'x': 30, 'y': 22, 'color': 'gold'},
        {'type': 'objective', 'name': 'Corner 1', 'x': 12, 'y': 12, 'color': 'green'},
        {'type': 'objective', 'name': 'Corner 2', 'x': 48, 'y': 12, 'color': 'brown'},
        {'type': 'objective', 'name': 'Corner 3', 'x': 12, 'y': 32, 'color': 'green'},
        {'type': 'objective', 'name': 'Corner 4', 'x': 48, 'y': 32, 'color': 'brown'},
    ]),
    ('Linked Ley Lines', 'linked-ley-lines', [
        {'type': 'objective', 'name': 'Heartwood', 'x': 30, 'y': 22, 'color': 'gold'},
        {'type': 'objective', 'name': 'Gnarlroot', 'x': 18, 'y': 22, 'color': 'green'},
        {'type': 'objective', 'name': 'Oakenbrow', 'x': 42, 'y': 22, 'color': 'brown'},
        {'type': 'objective', 'name': 'Winterleaf 1', 'x': 30, 'y': 14, 'color': 'blue'},
        {'type': 'objective', 'name': 'Winterleaf 2', 'x': 30, 'y': 30, 'color': 'blue'},
    ]),
    ('Noxious Nexus', 'noxious-nexus', [
        {'type': 'objective', 'name': 'Oakenbrow', 'x': 20, 'y': 16, 'color': 'brown', 'size': 'large'},
        {'type': 'objective', 'name': 'Gnarlroot', 'x': 40, 'y': 28, 'color': 'green', 'size': 'medium'},
        {'type': 'objective', 'name': 'Heartwood', 'x': 30, 'y': 22, 'color': 'gold', 'size': 'small'},
    ]),
    ('The Liferoots', 'the-liferoots', [
        {'type': 'objective', 'name': 'Liferoot 1', 'x': 22, 'y': 16, 'color': 'gold', 'size': 'large'},
        {'type': 'objective', 'name': 'Liferoot 2', 'x': 38, 'y': 28, 'color': 'gold', 'size': 'large'},
        {'type': 'terrain', 'name': 'Forest', 'x': 15, 'y': 20, 'size': 'small'},
        {'type': 'terrain', 'name': 'Forest', 'x': 33, 'y': 18, 'size': 'small'},
        {'type': 'terrain', 'name': 'Forest', 'x': 27, 'y': 26, 'size': 'small'},
        {'type': 'terrain', 'name': 'Forest', 'x': 45, 'y': 24, 'size': 'small'},
    ]),
    ('Bountiful Equinox', 'bountiful-equinox', [
        {'type': 'objective', 'name': 'Oakenbrow 1', 'x': 15, 'y': 18, 'color': 'brown'},
        {'type': 'objective', 'name': 'Gnarlroot 1', 'x': 45, 'y': 18, 'color': 'green'},
        {'type': 'objective', 'name': 'Heartwood', 'x': 30, 'y': 22, 'color': 'gold'},
        {'type': 'objective', 'name': 'Oakenbrow 2', 'x': 22, 'y': 28, 'color': 'brown'},
        {'type': 'objective', 'name': 'Gnarlroot 2', 'x': 38, 'y': 26, 'color': 'green'},
    ]),
    ('Lifecycle', 'lifecycle', [
        {'type': 'objective', 'name': 'Obj 1', 'x': 20, 'y': 18, 'color': 'gold'},
        {'type': 'objective', 'name': 'Obj 2', 'x': 40, 'y': 18, 'color': 'gold'},
        {'type': 'objective', 'name': 'Obj 3', 'x': 20, 'y': 26, 'color': 'gold'},
        {'type': 'objective', 'name': 'Obj 4', 'x': 40, 'y': 26, 'color': 'gold'},
    ]),
    ('Creeping Corruption', 'creeping-corruption', [
        {'type': 'objective', 'name': 'Obj 1', 'x': 18, 'y': 16, 'color': 'gold'},
        {'type': 'objective', 'name': 'Obj 2', 'x': 30, 'y': 16, 'color': 'gold'},
        {'type': 'objective', 'name': 'Obj 3', 'x': 42, 'y': 16, 'color': 'gold'},
        {'type': 'objective', 'name': 'Obj 4', 'x': 18, 'y': 28, 'color': 'gold'},
        {'type': 'objective', 'name': 'Obj 5', 'x': 30, 'y': 28, 'color': 'gold'},
        {'type': 'objective', 'name': 'Obj 6', 'x': 42, 'y': 28, 'color': 'gold'},
    ]),
    ('Grasp of Thorns', 'grasp-of-thorns', [
        {'type': 'objective', 'name': 'Obj 1', 'x': 15, 'y': 11, 'color': 'gold'},
        {'type': 'objective', 'name': 'Obj 2', 'x': 45, 'y': 11, 'color': 'gold'},
        {'type': 'objective', 'name': 'Obj 3', 'x': 15, 'y': 33, 'color': 'gold'},
        {'type': 'objective', 'name': 'Obj 4', 'x': 45, 'y': 33, 'color': 'gold'},
    ]),
]

# Generate mission cards
cards = []
for i, (title, slug, elements) in enumerate(missions, 1):
    # Build elements list HTML
    elements_html = []
    for elem in elements:
        elem_type = elem['type'].capitalize()
        name = elem.get('name', '')
        color = elem.get('color', '')
        size = elem.get('size', '')
        x, y = elem['x'], elem['y']
        
        color_badge = f'<span class="color-badge color-{color}"></span>' if color else ''
        size_text = f'({size})' if size else ''
        elements_html.append(
            f'<div class="element-item">'
            f'<span class="element-type">{elem_type}</span> '
            f'{color_badge}{name} {size_text}'
            f'<span class="coords">({x}", {y}")</span>'
            f'</div>'
        )
    
    elements_list = '\n                                '.join(elements_html)
    cards.append(f'''
            <div class="battleplan-card">
                <div class="battleplan-header">
                    <div class="mission-number">Mission {i} of 12</div>
                    <h2>{title}</h2>
                </div>
                <div class="comparison">
                    <div class="image-section">
                    <div class="elements-section">
                        <h3><span class="label label-elements">BATTLEFIELD ELEMENTS</span></h3>
                        <div class="elements-list">
                            {elements_list}
                        </div>
                    </div>
                        <h3><span class="label label-wahapedia">WAHAPEDIA</span></h3>
                        <div class="image-container">
                            <img src="assets/battle-plans/aos-{slug}.png" alt="{title} Wahapedia">
                            <div class="image-info">Original Source</div>
                        </div>
                    </div>
                    <div class="image-section">
                        <h3><span class="label label-aoi">AGE OF INDEX</span></h3>
                        <div class="image-container">
                            <img src="assets/battle-plans-ageofindex/aos-{slug}.png" alt="{title} AOI">
                            <div class="image-info">ageofindex.com</div>
                        </div>
                    </div>
                    <div class="image-section">
                        <h3><span class="label label-matplotlib">MATPLOTLIB</span></h3>
                        <div class="image-container">
                            <img src="assets/battle-plans-matplotlib/aos-{slug}-matplotlib.png" alt="{title} Generated">
                            <div class="image-info">Generated Diagram</div>
                        </div>
                    </div>
                </div>
            </div>''')

html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Battle Plans - 3-Way Comparison</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: system-ui, -apple-system, sans-serif; background: #1a1a1a; color: #e0e0e0; padding: 20px; }}
        .header {{ text-align: center; padding: 40px; background: linear-gradient(135deg, #2c3e50, #34495e); border-radius: 12px; margin-bottom: 40px; }}
        .header h1 {{ font-size: 2.5em; color: #ecf0f1; margin-bottom: 10px; }}
        .header p {{ color: #bdc3c7; font-size: 1.1em; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 40px; }}
        .stat-card {{ background: #2c3e50; padding: 20px; border-radius: 8px; text-align: center; }}
        .stat-number {{ font-size: 2.5em; font-weight: bold; color: #3498db; }}
        .stat-label {{ color: #95a5a6; margin-top: 5px; }}4, 1fr); gap: 15px; padding: 20px; }}
        .image-section {{ background: #34495e; border-radius: 8px; padding: 15px; }}
        .image-section h3 {{ color: #ecf0f1; margin-bottom: 10px; font-size: 1em; text-align: center; }}
        .label {{ display: inline-block; padding: 4px 12px; border-radius: 4px; font-size: 0.85em; font-weight: bold; }}
        .label-wahapedia {{ background: #9b59b6; color: white; }}
        .label-aoi {{ background: #27ae60; color: white; }}
        .label-matplotlib {{ background: #f39c12; color: white; }}
        .label-elements {{ background: #3498db; color: white; }}
        .image-container {{ background: #1a1a1a; border-radius: 4px; padding: 10px; text-align: center; }}
        .image-container img {{ max-width: 100%; height: auto; border-radius: 4px; }}
        .image-info {{ margin-top: 10px; font-size: 0.85em; color: #95a5a6; }}
        .elements-section {{ background: #34495e; border-radius: 8px; padding: 15px; }}
        .elements-list {{ background: #2c3e50; border-radius: 4px; padding: 15px; max-height: 400px; overflow-y: auto; }}
        .element-item {{ padding: 8px; margin: 4px 0; background: #1a1a1a; border-radius: 4px; font-size: 0.9em; display: flex; justify-content: space-between; align-items: center; }}
        .element-type {{ font-weight: bold; color: #3498db; min-width: 80px; }}
        .coords {{ color: #95a5a6; font-family: monospace; font-size: 0.85em; }}
        .color-badge {{ display: inline-block; width: 12px; height: 12px; border-radius: 50%; margin: 0 6px; border: 1px solid #555; }}
        .color-gold {{ background: #f39c12; }}
        .color-green {{ background: #27ae60; }}
        .color-brown {{ background: #8b4513; }}
        .color-blue {{ background: #3498db; }}
        @media (max-width: 1600px) {{ .comparison {{ grid-template-columns: repeat(2, 1fr); }} }}
        @media (min-width: 1601px) and (max-width: 2000px) {{ .comparison {{ grid-template-columns: repeat(3
        .label-matplotlib {{ background: #f39c12; color: white; }}
        .image-container {{ background: #1a1a1a; border-radius: 4px; padding: 10px; text-align: center; }}
        .image-container img {{ max-width: 100%; height: auto; border-radius: 4px; }}
        .image-info {{ margin-top: 10px; font-size: 0.85em; color: #95a5a6; }}
        @media (max-width: 1400px) {{ .comparison {{ grid-template-columns: 1fr; }} }}
        @media (min-width: 1401px) and (max-width: 1800px) {{ .comparison {{ grid-template-columns: repeat(2, 1fr); }} }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Battle Plans Gallery</h1>
        <p>Age of Sigmar General's Handbook 2025-2026 - 3-Way Comparison</p>
    </div>
    <div class="stats">
        <div class="stat-card"><div class="stat-number">12</div><div class="stat-label">Battle Plans</div></div>
        <div class="stat-card"><div class="stat-number">3</div><div class="stat-label">Image Sets</div></div>
        <div class="stat-card"><div class="stat-number">36</div><div class="stat-label">Total Images</div></div>
    </div>
    <div class="battleplan-grid">{''.join(cards)}
    </div>
</body>
</html>'''

# Write file
with open('battle-plans-demo.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

# VALIDATE
import subprocess
result = subprocess.run(['python', 'scripts/validate_html.py', 'battle-plans-demo.html'], capture_output=True, text=True)
print(result.stdout)
if result.returncode != 0:
    print("Validation failed")
    print(result.stderr)
    exit(1)

# Verify all image files exist
from pathlib import Path
missing_images = []
for title, slug, elements in missions:
    for folder in ['battle-plans', 'battle-plans-ageofindex', 'battle-plans-matplotlib']:
        suffix = '-matplotlib.png' if 'matplotlib' in folder else '.png'
        img_path = Path(f'assets/{folder}/aos-{slug}{suffix}')
        if not img_path.exists():
            missing_images.append(str(img_path))

if missing_images:
    print("❌ MISSING IMAGE FILES:")
    for img in missing_images:
        print(f"  - {img}")
    exit(1)

print(f"✓ Generated {len(missions)} missions with 3-way comparison")
print(f"✓ All {len(missions) * 3} images verified")
