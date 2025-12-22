"""
Generate matplotlib battle plan diagrams using extracted objective positions.
This version uses ACTUAL positions from Wahapedia images.
"""
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import json
from pathlib import Path

# Load extracted positions
with open('assets/battle-plans-matplotlib/extracted_objectives.json', 'r') as f:
    extracted_data = json.load(f)

# Battlefield dimensions
BATTLEFIELD_WIDTH = 60  # inches
BATTLEFIELD_HEIGHT = 44  # inches

def create_battlefield():
    """Create base battlefield figure."""
    fig, ax = plt.subplots(figsize=(12, 8.8))
    ax.set_xlim(0, BATTLEFIELD_WIDTH)
    ax.set_ylim(0, BATTLEFIELD_HEIGHT)
    ax.set_aspect('equal')
    
    # Draw battlefield border
    border = patches.Rectangle((0, 0), BATTLEFIELD_WIDTH, BATTLEFIELD_HEIGHT,
                               linewidth=3, edgecolor='black', facecolor='#f5f5dc')
    ax.add_patch(border)
    
    # Grid lines
    for x in range(0, BATTLEFIELD_WIDTH + 1, 12):
        ax.axvline(x, color='gray', linestyle=':', alpha=0.3, linewidth=0.5)
    for y in range(0, BATTLEFIELD_HEIGHT + 1, 12):
        ax.axhline(y, color='gray', linestyle=':', alpha=0.3, linewidth=0.5)
    
    ax.set_xlabel('Width (inches)', fontsize=10)
    ax.set_ylabel('Height (inches)', fontsize=10)
    ax.grid(False)
    
    return fig, ax

def draw_objective(ax, x, y, number, color='#D4AF37'):
    """Draw objective marker at position."""
    # Outer circle
    circle = patches.Circle((x, y), 1.5, facecolor=color, edgecolor='black', linewidth=2)
    ax.add_patch(circle)
    
    # Inner marker
    inner = patches.Circle((x, y), 0.8, facecolor='white', edgecolor='black', linewidth=1)
    ax.add_patch(inner)
    
    # Number label
    ax.text(x, y, str(number), ha='center', va='center',
           fontsize=10, fontweight='bold', color='black')

def draw_deployment_zone(ax, x, y, width, height, label, color):
    """Draw deployment zone."""
    zone = patches.Rectangle((x, y), width, height,
                            linewidth=2, edgecolor=color, facecolor=color, alpha=0.2)
    ax.add_patch(zone)
    
    # Label
    center_x = x + width / 2
    center_y = y + height / 2
    ax.text(center_x, center_y, label,
           ha='center', va='center', fontsize=14, fontweight='bold',
           color=color, alpha=0.7)

def generate_battleplan(filename, battle_plan_data):
    """Generate a single battle plan diagram."""
    fig, ax = create_battlefield()
    
    name = battle_plan_data['name']
    objectives = battle_plan_data['objectives']
    
    # Add title
    ax.set_title(f'{name}\n{len(objectives)} Objectives', fontsize=16, fontweight='bold', pad=20)
    
    # Draw objectives using extracted positions
    for i, obj in enumerate(objectives, 1):
        draw_objective(ax, obj['x'], obj['y'], i)
    
    # Add deployment zones based on battle plan type
    # Most AoS plans use long edge deployment (9" deep zones)
    if 'passing' in name.lower() or 'paths' in name.lower() or 'linked' in name.lower() or 'lifecycle' in name.lower() or 'bountiful' in name.lower():
        # Long edge deployment
        draw_deployment_zone(ax, 0, 0, BATTLEFIELD_WIDTH, 9, 'Player 1 Deployment', '#4169E1')
        draw_deployment_zone(ax, 0, BATTLEFIELD_HEIGHT - 9, BATTLEFIELD_WIDTH, 9, 'Player 2 Deployment', '#DC143C')
    
    elif 'cyclic' in name.lower() or 'roiling' in name.lower() or 'liferoots' in name.lower():
        # Diagonal corner deployment
        draw_deployment_zone(ax, 0, 0, 18, 18, 'P1', '#4169E1')
        draw_deployment_zone(ax, BATTLEFIELD_WIDTH - 18, BATTLEFIELD_HEIGHT - 18, 18, 18, 'P2', '#DC143C')
    
    elif 'noxious' in name.lower() or 'grasp' in name.lower():
        # Quadrant deployment
        draw_deployment_zone(ax, 0, 0, BATTLEFIELD_WIDTH / 2, 12, 'Player 1 Deployment', '#4169E1')
        draw_deployment_zone(ax, BATTLEFIELD_WIDTH / 2, BATTLEFIELD_HEIGHT - 12, BATTLEFIELD_WIDTH / 2, 12, 'Player 2 Deployment', '#DC143C')
    
    elif 'surge' in name.lower() or 'creeping' in name.lower():
        # Long edge deployment
        draw_deployment_zone(ax, 0, 0, BATTLEFIELD_WIDTH, 9, 'Player 1 Deployment', '#4169E1')
        draw_deployment_zone(ax, 0, BATTLEFIELD_HEIGHT - 9, BATTLEFIELD_WIDTH, 9, 'Player 2 Deployment', '#DC143C')
    
    # Add legend
    legend_elements = [
        patches.Patch(facecolor='#D4AF37', edgecolor='black', label='Objective Marker'),
        patches.Patch(facecolor='#4169E1', alpha=0.2, edgecolor='#4169E1', label='Player 1 Zone'),
        patches.Patch(facecolor='#DC143C', alpha=0.2, edgecolor='#DC143C', label='Player 2 Zone')
    ]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=9)
    
    # Save
    output_filename = filename.replace('.png', '-matplotlib.png')
    output_path = f'assets/battle-plans-matplotlib/{output_filename}'
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    return output_path

# Generate all battle plans
print("Generating matplotlib diagrams from extracted positions...")
print("="*70)

generated = []
for filename, data in extracted_data.items():
    print(f"\nGenerating: {data['name']}")
    print(f"  Objectives: {data['objective_count']}")
    
    output_path = generate_battleplan(filename, data)
    generated.append(output_path)
    
    print(f"  ✅ Saved: {output_path}")

print(f"\n{'='*70}")
print(f"✅ Generated {len(generated)} battle plan diagrams")
print(f"\nOutput directory: assets/battle-plans-matplotlib/")
print(f"\nNext: Visual comparison with Wahapedia originals for accuracy verification")
