#!/usr/bin/env python3
"""
Generate battle plan diagrams from mission data.
Creates clean, accurate visualizations of AoS missions.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from extract_mission_objects import MISSIONS

# Constants
BATTLEFIELD_WIDTH = 60  # inches
BATTLEFIELD_HEIGHT = 44  # inches
GRID_WIDTH = 15  # inches per grid square
GRID_HEIGHT = 11  # inches per grid square
DPI = 100
OUTPUT_DIR = Path("assets/battle-plans-matplotlib")

# Colors
COLORS = {
    'red': '#dc3545',
    'green': '#28a745',
    'blue': '#007bff',
    'brown': '#8b4513',
    'gold': '#ffc107',
    'purple': '#9b59b6',
}

# Sizes (in inches)
SIZES = {
    'small': 3,
    'medium': 5,
    'large': 6,
}

def draw_deployment_zones(ax, zones):
    """Draw deployment zones (supports both polygon and circle types)."""
    for zone in zones:
        if zone.get('type') == 'circle':
            # Circular zone
            circle = patches.Circle(
                zone['center'],
                zone['radius'],
                facecolor=zone['color'],
                alpha=zone.get('alpha', 0.3),
                edgecolor='none'
            )
            ax.add_patch(circle)
        else:
            # Polygon zone (default)
            polygon = patches.Polygon(
                zone['coords'],
                facecolor=zone['color'],
                alpha=zone.get('alpha', 0.3),
                edgecolor='none'
            )
            ax.add_patch(polygon)

def draw_grid(ax):
    """Draw the battlefield grid."""
    # Grid lines
    for x in range(0, BATTLEFIELD_WIDTH + 1, GRID_WIDTH):
        ax.axvline(x, color='#666', linewidth=0.5, alpha=0.3)
    for y in range(0, BATTLEFIELD_HEIGHT + 1, GRID_HEIGHT):
        ax.axhline(y, color='#666', linewidth=0.5, alpha=0.3)
    
    # Border
    ax.add_patch(patches.Rectangle(
        (0, 0), BATTLEFIELD_WIDTH, BATTLEFIELD_HEIGHT,
        fill=False, edgecolor='black', linewidth=2
    ))

def draw_objective(ax, obj):
    """Draw an objective marker."""
    x, y = obj['x'], obj['y']
    color = COLORS.get(obj.get('color', 'gold'), '#ffc107')
    size = SIZES.get(obj.get('size', 'large'), 6)
    radius = size / 2
    
    # Outer circle
    circle = patches.Circle((x, y), radius, 
                           facecolor=color, 
                           edgecolor='black', 
                           linewidth=2,
                           alpha=0.8)
    ax.add_patch(circle)
    
    # Crosshair
    ax.plot([x - radius, x + radius], [y, y], 'k-', linewidth=1.5)
    ax.plot([x, x], [y - radius, y + radius], 'k-', linewidth=1.5)
    
    # Center dot
    ax.plot(x, y, 'ko', markersize=4)

def draw_place_of_power(ax, terrain):
    """Draw a Place of Power (tower)."""
    x, y = terrain['x'], terrain['y']
    size = SIZES.get(terrain.get('size', 'small'), 3)
    width = size * 0.6
    height = size * 0.8
    
    # Tower body (rectangle)
    rect = patches.Rectangle(
        (x - width/2, y - height/2), width, height,
        facecolor='#007bff',
        edgecolor='black',
        linewidth=1.5,
        alpha=0.7
    )
    ax.add_patch(rect)
    
    # Tower top (triangle)
    triangle = patches.Polygon(
        [[x - width/2, y + height/2],
         [x, y + height/2 + width/2],
         [x + width/2, y + height/2]],
        facecolor='#0056b3',
        edgecolor='black',
        linewidth=1.5
    )
    ax.add_patch(triangle)

def draw_ruins(ax, terrain):
    """Draw Ruins."""
    x, y = terrain['x'], terrain['y']
    size = SIZES.get(terrain.get('size', 'medium'), 5)  # Use size from terrain data
    
    # Main structure (broken rectangle)
    points = [
        [x - size/2, y - size/2],
        [x + size/2, y - size/2],
        [x + size/2, y + size/3],
        [x + size/4, y + size/2],
        [x - size/4, y + size/2],
        [x - size/2, y + size/3],
    ]
    polygon = patches.Polygon(
        points,
        facecolor='#8b4513',
        edgecolor='black',
        linewidth=1.5,
        alpha=0.6
    )
    ax.add_patch(polygon)

def draw_forest(ax, terrain):
    """Draw Forest."""
    x, y = terrain['x'], terrain['y']
    size = SIZES.get(terrain.get('size', 'medium'), 4)  # Use size from terrain data
    
    # Draw as irregular circle with tree-like texture
    circle = patches.Circle((x, y), size/2,
                           facecolor='#228b22',
                           edgecolor='#006400',
                           linewidth=2,
                           alpha=0.6)
    ax.add_patch(circle)
    
    # Add some "branches" for texture
    for i in range(3):
        angle = i * 120
        import math
        dx = (size/3) * math.cos(math.radians(angle))
        dy = (size/3) * math.sin(math.radians(angle))
        small_circle = patches.Circle((x + dx, y + dy), size/4,
                                     facecolor='#2d5016',
                                     edgecolor='none',
                                     alpha=0.4)
        ax.add_patch(small_circle)

def generate_battle_plan(mission_slug, mission_data):
    """Generate a battle plan image for a mission."""
    fig, ax = plt.subplots(figsize=(12, 8.8), dpi=DPI)
    
    # Set up the axes
    ax.set_xlim(0, BATTLEFIELD_WIDTH)
    ax.set_ylim(0, BATTLEFIELD_HEIGHT)
    ax.set_aspect('equal')
    ax.set_facecolor('#e8e8e8')
    
    # Draw deployment zones first (background)
    if 'deployment_zones' in mission_data:
        draw_deployment_zones(ax, mission_data['deployment_zones'])
    
    # Draw exclusion zones (9" from enemy territory)
    if 'exclusion_zones' in mission_data:
        draw_deployment_zones(ax, mission_data['exclusion_zones'])
    
    # Draw grid
    draw_grid(ax)
    
    # Draw objectives
    for obj in mission_data['objectives']:
        draw_objective(ax, obj)
    
    # Draw terrain
    for terrain in mission_data['terrain']:
        terrain_type = terrain['type']
        if terrain_type == 'place_of_power':
            draw_place_of_power(ax, terrain)
        elif terrain_type == 'ruins':
            draw_ruins(ax, terrain)
        elif terrain_type == 'forest':
            draw_forest(ax, terrain)
    
    # Labels and title
    ax.set_xlabel('Width (inches)', fontsize=10)
    ax.set_ylabel('Height (inches)', fontsize=10)
    ax.set_title(mission_data['name'], fontsize=14, fontweight='bold', pad=10)
    
    # Grid
    ax.grid(False)
    ax.set_xticks(range(0, BATTLEFIELD_WIDTH + 1, GRID_WIDTH))
    ax.set_yticks(range(0, BATTLEFIELD_HEIGHT + 1, GRID_HEIGHT))
    
    # Legend - positioned outside the plot area with sizes
    legend_elements = []
    if 'deployment_zones' in mission_data:
        legend_elements.append(patches.Patch(facecolor='#dc3545', alpha=0.3, label='Attacker Zone'))
        legend_elements.append(patches.Patch(facecolor='#007bff', alpha=0.3, label='Defender Zone'))
        legend_elements.append(patches.Patch(facecolor='#666666', alpha=0.15, label='Exclusion Zone (9")'))
    legend_elements.extend([
        patches.Patch(facecolor='#dc3545', alpha=0.8, label='Objectives - Large (6")'),
        patches.Patch(facecolor='#007bff', alpha=0.7, label='Place of Power - Large (6") / Small (3")'),
        patches.Patch(facecolor='#8b4513', alpha=0.6, label='Ruins (5")'),
        patches.Patch(facecolor='#228b22', alpha=0.6, label='Forest (4")'),
    ])
    ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1.02, 1), 
              fontsize=8, framealpha=0.95, edgecolor='black')
    
    # Save
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / f"{mission_slug}-matplotlib.png"
    plt.tight_layout()
    plt.savefig(output_path, dpi=DPI, bbox_inches='tight', facecolor='white')
    plt.close()
    
    return output_path

def main():
    """Generate all battle plan images."""
    import sys
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Check if specific mission requested
    if len(sys.argv) > 1:
        mission_slug = sys.argv[1]
        if mission_slug not in MISSIONS:
            print(f"Error: Mission '{mission_slug}' not found")
            print(f"Available missions: {', '.join(MISSIONS.keys())}")
            sys.exit(1)
        
        print(f"Generating {MISSIONS[mission_slug]['name']}...", end=' ')
        output_path = generate_battle_plan(mission_slug, MISSIONS[mission_slug])
        print(f"OK ({output_path.stat().st_size // 1024}KB)")
        return
    
    # Generate all missions
    print(f"Generating battle plans to {OUTPUT_DIR}/")
    print("=" * 60)
    
    for slug, data in MISSIONS.items():
        print(f"Generating {data['name']}...", end=' ')
        output_path = generate_battle_plan(slug, data)
        print(f"OK ({output_path.stat().st_size // 1024}KB)")
    
    print("=" * 60)
    print(f"Generated {len(MISSIONS)} battle plans")

if __name__ == "__main__":
    main()

