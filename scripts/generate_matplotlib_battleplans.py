"""
Generate matplotlib battle plan diagrams matching AOS_BATTLE_PLANS data.
Creates IP-neutral tactical diagrams for all 12 GH 2025-26 battle plans.
"""
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path
import numpy as np

# Consistent style for all diagrams
STYLE = {
    'figure_size': (16, 9),
    'dpi': 150,
    'bg_color': '#2b2b2b',
    'grid_color': '#404040',
    'deployment_colors': {'p1': '#3498db', 'p2': '#e74c3c'},
    'objective_color': '#f39c12',
    'terrain_color': '#27ae60',
    'text_color': '#ecf0f1',
}

def setup_battlefield(ax, title):
    """Setup standard 60x44 battlefield."""
    ax.set_xlim(0, 60)
    ax.set_ylim(0, 44)
    ax.set_aspect('equal')
    ax.set_facecolor(STYLE['bg_color'])
    
    # Grid every 6"
    for x in range(0, 61, 6):
        ax.axvline(x, color=STYLE['grid_color'], linewidth=0.5, alpha=0.3)
    for y in range(0, 45, 6):
        ax.axhline(y, color=STYLE['grid_color'], linewidth=0.5, alpha=0.3)
    
    # Title
    ax.text(30, 42, title.upper(), fontsize=20, fontweight='bold',
           ha='center', va='top', color=STYLE['text_color'])
    
    ax.set_xticks([])
    ax.set_yticks([])

def draw_deployment_zone(ax, x, y, width, height, player):
    """Draw deployment zone."""
    color = STYLE['deployment_colors'][player]
    rect = patches.Rectangle((x, y), width, height, linewidth=2,
                            edgecolor=color, facecolor=color, alpha=0.3)
    ax.add_patch(rect)
    ax.text(x + width/2, y + height/2, f'DEPLOYMENT\nZONE {player[-1]}',
           ha='center', va='center', fontsize=10, fontweight='bold', color=color)

def draw_objective(ax, x, y, number, size=2):
    """Draw objective marker."""
    circle = patches.Circle((x, y), size, linewidth=2,
                           edgecolor=STYLE['objective_color'],
                           facecolor=STYLE['objective_color'], alpha=0.6)
    ax.add_patch(circle)
    ax.text(x, y, str(number), ha='center', va='center',
           fontsize=12, fontweight='bold', color='#2b2b2b')

def generate_passing_seasons():
    """Passing Seasons: 4 objectives, seasonal rotation."""
    fig, ax = plt.subplots(figsize=STYLE['figure_size'], dpi=STYLE['dpi'])
    setup_battlefield(ax, 'Passing Seasons')
    
    # Long edge deployment
    draw_deployment_zone(ax, 0, 0, 60, 9, 'p1')
    draw_deployment_zone(ax, 0, 35, 60, 9, 'p2')
    
    # 4 objectives: 2 Gnarlroot, 2 Oakenbrow
    draw_objective(ax, 15, 18, 1)  # Gnarlroot 1
    draw_objective(ax, 45, 18, 2)  # Oakenbrow 1
    draw_objective(ax, 15, 26, 3)  # Gnarlroot 2
    draw_objective(ax, 45, 26, 4)  # Oakenbrow 2
    
    ax.text(30, 4, 'Rounds 1,3,5: Gnarlroot | Rounds 2,4: Oakenbrow',
           fontsize=8, ha='center', color=STYLE['text_color'], alpha=0.7)
    
    plt.tight_layout()
    return fig

def generate_paths_of_the_fey():
    """Paths of the Fey: 5 objectives with fey paths."""
    fig, ax = plt.subplots(figsize=STYLE['figure_size'], dpi=STYLE['dpi'])
    setup_battlefield(ax, 'Paths of the Fey')
    
    # Long edge deployment
    draw_deployment_zone(ax, 0, 0, 60, 9, 'p1')
    draw_deployment_zone(ax, 0, 35, 60, 9, 'p2')
    
    # 5 objectives
    draw_objective(ax, 30, 22, 1)  # Central Heartwood
    draw_objective(ax, 18, 22, 2)  # Gnarlroot
    draw_objective(ax, 42, 22, 3)  # Oakenbrow
    draw_objective(ax, 30, 14, 4)  # Winterleaf
    draw_objective(ax, 30, 30, 5)  # Winterleaf
    
    # Fey paths
    for i in range(1, 5):
        ax.plot([30, [18,42,30,30][i-1]], [22, [22,22,14,30][i-1]],
               color='#9b59b6', linewidth=1, alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    return fig

def generate_roiling_roots():
    """Roiling Roots: 6 objectives diagonal line."""
    fig, ax = plt.subplots(figsize=STYLE['figure_size'], dpi=STYLE['dpi'])
    setup_battlefield(ax, 'Roiling Roots')
    
    # Diagonal corner deployment
    draw_deployment_zone(ax, 0, 0, 12, 12, 'p1')
    draw_deployment_zone(ax, 48, 32, 12, 12, 'p2')
    
    # 6 objectives diagonal line
    for i in range(6):
        x = 10 + i * 10
        y = 7.3 + i * 6.1
        draw_objective(ax, x, y, i+1)
    
    plt.tight_layout()
    return fig

def generate_cyclic_shifts():
    """Cyclic Shifts: 6 objectives in diagonal rows."""
    fig, ax = plt.subplots(figsize=STYLE['figure_size'], dpi=STYLE['dpi'])
    setup_battlefield(ax, 'Cyclic Shifts')
    
    # Diagonal corner deployment
    draw_deployment_zone(ax, 0, 0, 12, 12, 'p1')
    draw_deployment_zone(ax, 48, 32, 12, 12, 'p2')
    
    # 6 objectives: 3 per side diagonally
    positions = [(15,12), (25,18), (35,24), (25,26), (35,32), (45,38)]
    for i, (x, y) in enumerate(positions, 1):
        draw_objective(ax, x, y, i)
    
    plt.tight_layout()
    return fig

def generate_surge_of_slaughter():
    """Surge of Slaughter: Center + 4 corners."""
    fig, ax = plt.subplots(figsize=STYLE['figure_size'], dpi=STYLE['dpi'])
    setup_battlefield(ax, 'Surge of Slaughter')
    
    # Long edge deployment
    draw_deployment_zone(ax, 0, 0, 60, 9, 'p1')
    draw_deployment_zone(ax, 0, 35, 60, 9, 'p2')
    
    # 5 objectives
    draw_objective(ax, 30, 22, 1)  # Center
    draw_objective(ax, 12, 12, 2)  # Corner
    draw_objective(ax, 48, 12, 3)
    draw_objective(ax, 12, 32, 4)
    draw_objective(ax, 48, 32, 5)
    
    plt.tight_layout()
    return fig

def generate_linked_ley_lines():
    """Linked Ley Lines: Diamond formation."""
    fig, ax = plt.subplots(figsize=STYLE['figure_size'], dpi=STYLE['dpi'])
    setup_battlefield(ax, 'Linked Ley Lines')
    
    # Long edge deployment
    draw_deployment_zone(ax, 0, 0, 60, 9, 'p1')
    draw_deployment_zone(ax, 0, 35, 60, 9, 'p2')
    
    # 5 objectives diamond
    draw_objective(ax, 30, 22, 1)  # Center
    draw_objective(ax, 18, 22, 2)
    draw_objective(ax, 42, 22, 3)
    draw_objective(ax, 30, 14, 4)
    draw_objective(ax, 30, 30, 5)
    
    # Ley lines
    lines = [(1,2), (1,3), (1,4), (1,5), (2,4), (3,5)]
    positions = {1:(30,22), 2:(18,22), 3:(42,22), 4:(30,14), 5:(30,30)}
    for a, b in lines:
        ax.plot([positions[a][0], positions[b][0]],
               [positions[a][1], positions[b][1]],
               color='#3498db', linewidth=1, alpha=0.2, linestyle='--')
    
    plt.tight_layout()
    return fig

def generate_noxious_nexus():
    """Noxious Nexus: 3 nexus points."""
    fig, ax = plt.subplots(figsize=STYLE['figure_size'], dpi=STYLE['dpi'])
    setup_battlefield(ax, 'Noxious Nexus')
    
    # Quadrant deployment
    draw_deployment_zone(ax, 0, 0, 15, 15, 'p1')
    draw_deployment_zone(ax, 45, 29, 15, 15, 'p2')
    
    # 3 nexus objectives
    draw_objective(ax, 20, 16, 1, size=3)  # Oakenbrow (larger)
    draw_objective(ax, 40, 28, 2, size=2.5)  # Gnarlroot
    draw_objective(ax, 30, 22, 3, size=2)  # Heartwood
    
    plt.tight_layout()
    return fig

def generate_the_liferoots():
    """The Liferoots: 2 liferoot markers."""
    fig, ax = plt.subplots(figsize=STYLE['figure_size'], dpi=STYLE['dpi'])
    setup_battlefield(ax, 'The Liferoots')
    
    # Diagonal corner deployment
    draw_deployment_zone(ax, 0, 0, 12, 12, 'p1')
    draw_deployment_zone(ax, 48, 32, 12, 12, 'p2')
    
    # 2 liferoots 24" apart
    draw_objective(ax, 22, 16, 1, size=3)
    draw_objective(ax, 38, 28, 2, size=3)
    
    # Terrain markers
    for x, y in [(15, 20), (33, 18), (27, 26), (45, 24)]:
        circle = patches.Circle((x, y), 1.5, edgecolor=STYLE['terrain_color'],
                               facecolor='none', linewidth=1.5, linestyle='--', alpha=0.5)
        ax.add_patch(circle)
    
    plt.tight_layout()
    return fig

def generate_bountiful_equinox():
    """Bountiful Equinox: 5 objectives spread."""
    fig, ax = plt.subplots(figsize=STYLE['figure_size'], dpi=STYLE['dpi'])
    setup_battlefield(ax, 'Bountiful Equinox')
    
    # Long edge deployment
    draw_deployment_zone(ax, 0, 0, 60, 9, 'p1')
    draw_deployment_zone(ax, 0, 35, 60, 9, 'p2')
    
    # 5 objectives distributed
    draw_objective(ax, 15, 18, 1)  # Oakenbrow
    draw_objective(ax, 45, 18, 2)  # Gnarlroot
    draw_objective(ax, 30, 22, 3)  # Heartwood
    draw_objective(ax, 22, 28, 4)  # Oakenbrow
    draw_objective(ax, 38, 26, 5)  # Gnarlroot
    
    plt.tight_layout()
    return fig

def generate_lifecycle():
    """Lifecycle: 4 objectives with rotation."""
    fig, ax = plt.subplots(figsize=STYLE['figure_size'], dpi=STYLE['dpi'])
    setup_battlefield(ax, 'Lifecycle')
    
    # Long edge deployment
    draw_deployment_zone(ax, 0, 0, 60, 9, 'p1')
    draw_deployment_zone(ax, 0, 35, 60, 9, 'p2')
    
    # 4 objectives symmetrical
    draw_objective(ax, 20, 18, 1)
    draw_objective(ax, 40, 18, 2)
    draw_objective(ax, 20, 26, 3)
    draw_objective(ax, 40, 26, 4)
    
    # Rotation arrows
    ax.annotate('', xy=(40, 18), xytext=(20, 18),
               arrowprops=dict(arrowstyle='->', color='#f39c12', lw=1.5, alpha=0.5))
    ax.text(30, 16, 'PRIMARY ROTATES', fontsize=7, ha='center',
           color=STYLE['objective_color'], alpha=0.7)
    
    plt.tight_layout()
    return fig

def generate_creeping_corruption():
    """Creeping Corruption: 6 objective grid."""
    fig, ax = plt.subplots(figsize=STYLE['figure_size'], dpi=STYLE['dpi'])
    setup_battlefield(ax, 'Creeping Corruption')
    
    # Long edge deployment
    draw_deployment_zone(ax, 0, 0, 60, 9, 'p1')
    draw_deployment_zone(ax, 0, 35, 60, 9, 'p2')
    
    # 6 objectives grid
    positions = [(18,16), (30,16), (42,16), (18,28), (30,28), (42,28)]
    for i, (x, y) in enumerate(positions, 1):
        draw_objective(ax, x, y, i)
    
    # Corruption spreading
    ax.plot([18,30,42], [16,16,16], color='#27ae60', linewidth=1, alpha=0.3, linestyle=':')
    ax.plot([18,30,42], [28,28,28], color='#27ae60', linewidth=1, alpha=0.3, linestyle=':')
    
    plt.tight_layout()
    return fig

def generate_grasp_of_thorns():
    """Grasp of Thorns: 4 objectives in quadrants."""
    fig, ax = plt.subplots(figsize=STYLE['figure_size'], dpi=STYLE['dpi'])
    setup_battlefield(ax, 'Grasp of Thorns')
    
    # Quadrant deployment
    draw_deployment_zone(ax, 0, 0, 15, 15, 'p1')
    draw_deployment_zone(ax, 45, 29, 15, 15, 'p2')
    
    # 4 objectives, one per quarter
    draw_objective(ax, 15, 11, 1)
    draw_objective(ax, 45, 11, 2)
    draw_objective(ax, 15, 33, 3)
    draw_objective(ax, 45, 33, 4)
    
    # Thorn markers
    for x, y in [(15,11), (45,11), (15,33), (45,33)]:
        ax.plot(x, y, marker='^', markersize=15, color='#e74c3c', alpha=0.3)
    
    plt.tight_layout()
    return fig

def main():
    """Generate all 12 battle plan diagrams."""
    generators = [
        ('aos-passing-seasons.png', generate_passing_seasons),
        ('aos-paths-of-the-fey.png', generate_paths_of_the_fey),
        ('aos-roiling-roots.png', generate_roiling_roots),
        ('aos-cyclic-shifts.png', generate_cyclic_shifts),
        ('aos-surge-of-slaughter.png', generate_surge_of_slaughter),
        ('aos-linked-ley-lines.png', generate_linked_ley_lines),
        ('aos-noxious-nexus.png', generate_noxious_nexus),
        ('aos-the-liferoots.png', generate_the_liferoots),
        ('aos-bountiful-equinox.png', generate_bountiful_equinox),
        ('aos-lifecycle.png', generate_lifecycle),
        ('aos-creeping-corruption.png', generate_creeping_corruption),
        ('aos-grasp-of-thorns.png', generate_grasp_of_thorns),
    ]
    
    output_dir = Path('assets/battle-plans-matplotlib')
    output_dir.mkdir(exist_ok=True, parents=True)
    
    print("Generating matplotlib tactical diagrams...")
    print("=" * 60)
    
    for filename, generator in generators:
        output_path = output_dir / filename
        print(f"\n{filename}")
        try:
            fig = generator()
            fig.savefig(output_path, facecolor='#2b2b2b', edgecolor='none')
            plt.close(fig)
            size_kb = output_path.stat().st_size // 1024
            print(f"  ✅ Generated ({size_kb}KB)")
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    print()
    print("=" * 60)
    print(f"✅ All diagrams generated: {output_dir}")

if __name__ == "__main__":
    main()
