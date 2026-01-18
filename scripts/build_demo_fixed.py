#!/usr/bin/env python3
"""Build battle plans demo with 4 columns: Wahapedia, AOI, Matplotlib, Elements"""
import sys
import subprocess
from extract_mission_objects import MISSIONS as MISSION_DATA

# Current mission being worked on (shows first in gallery)
CURRENT_MISSION = ""

# Locked missions (completed and verified)
LOCKED_MISSIONS = [
    "aos-passing-seasons",
    "aos-creeping-corruption",
    "aos-bountiful-equinox",
    "aos-cyclic-shifts",
    "aos-grasp-of-thorns",
    "aos-lifecycle",
    "aos-linked-ley-lines",
    "aos-noxious-nexus",
    "aos-paths-of-the-fey",
    "aos-roiling-roots",
    "aos-surge-of-slaughter",
    "aos-the-liferoots",
]

# Convert MISSIONS dict to list format for template
missions = []
mission_order = [k for k in MISSION_DATA.keys()] if not CURRENT_MISSION else [CURRENT_MISSION] + [k for k in MISSION_DATA.keys() if k != CURRENT_MISSION]

for slug in mission_order:
    data = MISSION_DATA[slug]
    elements = []
    
    # Add deployment zones
    if 'deployment_zones' in data:
        for zone in data['deployment_zones']:
            coords_str = ' → '.join([f"({x}\", {y}\")" for x, y in zone['coords']])
            elements.append({
                'type': 'deployment_zone',
                'name': f"{zone['player']} Zone",
                'coords': coords_str
            })
    
    # Add exclusion zones
    if 'exclusion_zones' in data:
        for zone in data['exclusion_zones']:
            # Handle circular zones
            if zone.get('type') == 'circle':
                coords_str = f"Center: ({zone['center'][0]}\", {zone['center'][1]}\"), Radius: {zone['radius']}\""
                name = zone.get('note', 'Exclusion Zone')
            elif zone.get('type') == 'semicircle':
                coords_str = f"Center: ({zone['center'][0]}\", {zone['center'][1]}\"), Radius: {zone['radius']}\", Orientation: {zone.get('orientation', 'N/A')}"
                name = zone.get('note', 'Semicircle Exclusion')
            elif zone.get('type') == 'quarter_circle':
                coords_str = f"Center: ({zone['center'][0]}\", {zone['center'][1]}\"), Radius: {zone['radius']}\", Quadrant: {zone.get('quadrant', 'N/A')}"
                name = zone.get('note', 'Quarter Circle Exclusion')
            else:
                # Handle polygon zones
                coords_str = ' → '.join([f"({x}\", {y}\")" for x, y in zone['coords']])
                name = zone.get('note', zone.get('player', 'Exclusion Zone (9\")'))
            
            elements.append({
                'type': 'exclusion_zone',
                'name': name,
                'coords': coords_str
            })
    
    # Add objectives and terrain with x,y coordinates
    for item in data['objectives'] + data['terrain']:
        elem = item.copy()
        if 'x' in elem and 'y' in elem:
            elem['coords'] = f"({elem['x']}\", {elem['y']}\")"
        elements.append(elem)
    
    missions.append({
        'name': data['name'],
        'slug': slug,
        'elements': elements,
        'locked': slug in LOCKED_MISSIONS
    })

# Build mission cards
cards = []
for i, mission in enumerate(missions, 1):
    title = mission['name']
    slug = mission['slug']
    elements = mission['elements']
    locked_badge = ' <span style="color: #28a745; font-weight: bold;">[LOCKED]</span>' if mission['locked'] else ''
    
    # Build elements list
    elem_html = []
    for e in elements:
        etype = e['type'].capitalize().replace('_', ' ')
        name = e.get('name', '')
        color = e.get('color', '')
        size = e.get('size', '')
        coords = e.get('coords', '')
        
        # For zones with full coordinate paths
        if 'coords' in e and isinstance(coords, str) and '→' in coords:
            elem_html.append(
                f'<div class="elem-item zone-item">'
                f'<span class="elem-type">{etype}</span> {name}'
                f'<div class="zone-coords">{coords}</div>'
                f'</div>'
            )
        else:
            # Regular items with x,y coordinates
            badge = f'<span class="color-badge color-{color}"></span>' if color else ''
            size_txt = f'({size})' if size else ''
            elem_html.append(
                f'<div class="elem-item">'
                f'<span class="elem-type">{etype}</span> {badge}{name} {size_txt}'
                f'<span class="coords">{coords}</span>'
                f'</div>'
            )
    
    elems = '\n                                '.join(elem_html)
    
    cards.append(f'''
            <div class="card">
                <div class="card-header">
                    <div class="mission-num">Mission {i} of 12</div>
                    <h2>{title}{locked_badge}</h2>
                </div>
                <div class="grid4">
                    <div class="col">
                        <h3><span class="badge badge-waha">WAHAPEDIA</span></h3>
                        <div class="img-box">
                            <img src="assets/battle-plans/{slug}.png" alt="{title} Wahapedia">
                            <div class="img-label">Original Source</div>
                        </div>
                    </div>
                    <div class="col">
                        <h3><span class="badge badge-aoi">AGE OF INDEX</span></h3>
                        <div class="img-box">
                            <img src="assets/battle-plans-ageofindex/{slug}.png" alt="{title} AOI">
                            <div class="img-label">ageofindex.com</div>
                        </div>
                    </div>
                    <div class="col">
                        <h3><span class="badge badge-matplot">MATPLOTLIB</span></h3>
                        <div class="img-box">
                            <img src="assets/battle-plans-matplotlib/{slug}-matplotlib.png" alt="{title} Generated">
                            <div class="img-label">Generated Diagram</div>
                        </div>
                    </div>
                    <div class="col">
                        <h3><span class="badge badge-elem">BATTLEFIELD ELEMENTS</span></h3>
                        <div class="elem-list">
                            {elems}
                        </div>
                    </div>
                </div>
            </div>''')

# Calculate status counts
total_missions = len(missions)
locked_count = len(LOCKED_MISSIONS)
in_progress_count = 1  # Current mission
remaining_count = total_missions - locked_count - in_progress_count

html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Battle Plans - 4-Column Comparison</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: system-ui, sans-serif; background: #1a1a1a; color: #e0e0e0; padding: 20px; }}
        .header {{ text-align: center; padding: 40px; background: linear-gradient(135deg, #2c3e50, #34495e); border-radius: 12px; margin-bottom: 20px; }}
        .header h1 {{ font-size: 2.5em; color: #ecf0f1; margin-bottom: 10px; }}
        .header p {{ color: #bdc3c7; font-size: 1.1em; }}
        .status-summary {{ background: #34495e; border-radius: 8px; padding: 20px; margin-bottom: 40px; display: flex; justify-content: center; gap: 40px; }}
        .status-item {{ text-align: center; }}
        .status-count {{ font-size: 2em; font-weight: bold; display: block; }}
        .status-count.locked {{ color: #28a745; }}
        .status-count.progress {{ color: #ffc107; }}
        .status-count.remaining {{ color: #6c757d; }}
        .status-label {{ color: #bdc3c7; font-size: 0.9em; margin-top: 5px; }}
        .card {{ background: #2c3e50; border-radius: 12px; margin-bottom: 30px; overflow: hidden; }}
        .card-header {{ background: linear-gradient(135deg, #2c3e50, #34495e); padding: 20px; border-bottom: 3px solid #3498db; }}
        .card-header h2 {{ color: #ecf0f1; margin-bottom: 5px; }}
        .mission-num {{ color: rgba(255,255,255,0.8); font-size: 0.9em; }}
        .grid4 {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; padding: 20px; }}
        .col {{ background: #34495e; border-radius: 8px; padding: 15px; }}
        .col h3 {{ color: #ecf0f1; margin-bottom: 10px; font-size: 1em; text-align: center; }}
        .badge {{ display: inline-block; padding: 4px 12px; border-radius: 4px; font-size: 0.85em; font-weight: bold; }}
        .badge-waha {{ background: #9b59b6; color: white; }}
        .badge-aoi {{ background: #27ae60; color: white; }}
        .badge-matplot {{ background: #f39c12; color: white; }}
        .badge-elem {{ background: #3498db; color: white; }}
        .img-box {{ background: #1a1a1a; border-radius: 4px; padding: 10px; text-align: center; }}
        .img-box img {{ max-width: 100%; height: auto; border-radius: 4px; }}
        .img-label {{ margin-top: 10px; font-size: 0.85em; color: #95a5a6; }}
        .elem-list {{ background: #2c3e50; border-radius: 4px; padding: 15px; max-height: 400px; overflow-y: auto; }}
        .elem-item {{ padding: 8px; margin: 4px 0; background: #1a1a1a; border-radius: 4px; font-size: 0.9em; display: flex; justify-content: space-between; align-items: center; }}
        .zone-item {{ flex-direction: column; align-items: flex-start; }}
        .zone-coords {{ color: #95a5a6; font-family: monospace; font-size: 0.75em; margin-top: 4px; white-space: nowrap; overflow-x: auto; }}
        .elem-type {{ font-weight: bold; color: #3498db; min-width: 100px; }}
        .coords {{ color: #95a5a6; font-family: monospace; font-size: 0.85em; }}
        .color-badge {{ display: inline-block; width: 12px; height: 12px; border-radius: 50%; margin: 0 6px; border: 1px solid #555; }}
        .color-gold {{ background: #f39c12; }}
        .color-red {{ background: #e74c3c; }}
        .color-green {{ background: #27ae60; }}
        .color-brown {{ background: #8b4513; }}
        .color-blue {{ background: #3498db; }}
        .color-purple {{ background: #9b59b6; }}
        @media (max-width: 1600px) {{ .grid4 {{ grid-template-columns: repeat(2, 1fr); }} }}
        @media (min-width: 1601px) and (max-width: 2000px) {{ .grid4 {{ grid-template-columns: repeat(3, 1fr); }} }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Battle Plans Gallery</h1>
        <p>Age of Sigmar GH 2025-2026 - 4-Column Comparison</p>
    </div>
    <div class="status-summary">
        <div class="status-item">
            <span class="status-count locked">{locked_count}</span>
            <div class="status-label">LOCKED</div>
        </div>
        <div class="status-item">
            <span class="status-count progress">{in_progress_count}</span>
            <div class="status-label">IN PROGRESS</div>
        </div>
        <div class="status-item">
            <span class="status-count remaining">{remaining_count}</span>
            <div class="status-label">REMAINING</div>
        </div>
    </div>
    <div class="container">
{''.join(cards)}
    </div>
</body>
</html>'''

# Write
with open('battle-plans-demo.html', 'w', encoding='utf-8') as f:
    f.write(html)

# Validate
result = subprocess.run(['python', 'scripts/validate_html.py', 'battle-plans-demo.html'], 
                       capture_output=True, text=True)
print(result.stdout)
if result.returncode != 0:
    print("Validation failed")
    print(result.stderr)
    sys.exit(1)

print("Generated: battle-plans-demo.html")
print("Serve: python -m http.server 8080")
