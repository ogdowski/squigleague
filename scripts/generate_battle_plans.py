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
from matplotlib import image as mpimg
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image
from extract_mission_objects import MISSIONS

# Constants
BATTLEFIELD_WIDTH = 60  # inches
BATTLEFIELD_HEIGHT = 44  # inches
GRID_WIDTH = 15  # inches per grid square
GRID_HEIGHT = 11  # inches per grid square
DPI = 100
OUTPUT_DIR = Path("assets/battle-plans-parchment")
PARCHMENT = mpimg.imread("../assets/textures/parchment-texture.png")

# Load PNG icons converted from SVG
ICON_PATHS = {
    'objective': Path('../assets/battle-icons/objectives/crosshair.png'),
    'forest': Path('../assets/battle-icons/forests/oak.png'),
    'ruins': Path('../assets/battle-icons/ruins/stone-tower.png'),
    'place_of_power': Path('../assets/battle-icons/places_of_power/magic-portal.png'),
}

def load_icon_image(icon_path):
    """Load PNG icon as matplotlib image."""
    return mpimg.imread(str(icon_path))

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
        elif zone.get('type') == 'semicircle':
            # Semicircle zone
            if zone.get('orientation') == 'top':
                theta1, theta2 = 0, 180
            elif zone.get('orientation') == 'bottom':
                theta1, theta2 = 180, 360
            elif zone.get('orientation') == 'left':
                theta1, theta2 = 90, 270
            else:  # right
                theta1, theta2 = 270, 90
            wedge = patches.Wedge(
                zone['center'],
                zone['radius'],
                theta1=theta1,
                theta2=theta2,
                facecolor=zone['color'],
                alpha=zone.get('alpha', 0.3),
                edgecolor='none'
            )
            ax.add_patch(wedge)
        elif zone.get('type') == 'quarter_circle':
            # Quarter circle zone
            theta1 = {'top_right': 0, 'top_left': 90, 'bottom_left': 180, 'bottom_right': 270}.get(zone.get('quadrant', 'top_right'), 0)
            theta2 = theta1 + 90
            wedge = patches.Wedge(
                zone['center'],
                zone['radius'],
                theta1=theta1,
                theta2=theta2,
                facecolor=zone['color'],
                alpha=zone.get('alpha', 0.3),
                edgecolor='none'
            )
            ax.add_patch(wedge)
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
    
    # Icon overlay (scaled to game size: 1 inch = 20px, icon is 512px)
    icon = load_icon_image(ICON_PATHS['objective'])
    imagebox = OffsetImage(icon, zoom=size/30)
    ab = AnnotationBbox(imagebox, (x, y), frameon=False, box_alignment=(0.5, 0.5))
    ax.add_artist(ab)

def draw_place_of_power(ax, terrain):
    """Draw a Place of Power."""
    x, y = terrain['x'], terrain['y']
    size = SIZES.get(terrain.get('size', 'small'), 3)
    
    # Icon (scaled to game size)
    icon = load_icon_image(ICON_PATHS['place_of_power'])
    imagebox = OffsetImage(icon, zoom=size/30)
    ab = AnnotationBbox(imagebox, (x, y), frameon=False, box_alignment=(0.5, 0.5))
    ax.add_artist(ab)

def draw_ruins(ax, terrain):
    """Draw Ruins."""
    x, y = terrain['x'], terrain['y']
    size = SIZES.get(terrain.get('size', 'medium'), 5)
    
    # Icon (scaled to game size)
    icon = load_icon_image(ICON_PATHS['ruins'])
    imagebox = OffsetImage(icon, zoom=size/30)
    ab = AnnotationBbox(imagebox, (x, y), frameon=False, box_alignment=(0.5, 0.5))
    ax.add_artist(ab)

def draw_forest(ax, terrain):
    """Draw Forest."""
    x, y = terrain['x'], terrain['y']
    size = SIZES.get(terrain.get('size', 'medium'), 4)
    
    # Icon (scaled to game size)
    icon = load_icon_image(ICON_PATHS['forest'])
    imagebox = OffsetImage(icon, zoom=size/30)
    ab = AnnotationBbox(imagebox, (x, y), frameon=False, box_alignment=(0.5, 0.5))
    ax.add_artist(ab)

def generate_battle_plan(mission_slug, mission_data):
    """Generate a battle plan image for a mission."""
    fig, ax = plt.subplots(figsize=(12, 8.8), dpi=DPI)
    
    # Set up the axes
    ax.set_xlim(0, BATTLEFIELD_WIDTH)
    ax.set_ylim(0, BATTLEFIELD_HEIGHT)
    ax.set_aspect('equal')
    ax.set_facecolor('#e8e8e8')
    
    # Add parchment background
    ax.imshow(PARCHMENT, extent=[0, BATTLEFIELD_WIDTH, 0, BATTLEFIELD_HEIGHT], 
              zorder=-1, alpha=0.9)
    
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

