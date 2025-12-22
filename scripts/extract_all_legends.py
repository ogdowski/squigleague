"""
Detailed legend extraction - save each battle plan's legend separately
so we can visually inspect what objective markers actually look like.
"""
from PIL import Image
import numpy as np
from pathlib import Path

battle_plans = [
    "aos-passing-seasons.png",
    "aos-paths-of-the-fey.png",
    "aos-roiling-roots.png",
    "aos-cyclic-shifts.png",
    "aos-surge-of-slaughter.png",
    "aos-linked-ley-lines.png",
    "aos-noxious-nexus.png",
    "aos-the-liferoots.png",
    "aos-bountiful-equinox.png",
    "aos-lifecycle.png",
    "aos-creeping-corruption.png",
    "aos-grasp-of-thorns.png",
]

print("Extracting legends for visual inspection...")
print("="*70)

for filename in battle_plans:
    image_path = Path(f"assets/battle-plans/{filename}")
    
    if not image_path.exists():
        continue
    
    img = Image.open(image_path)
    width, height = img.size
    
    # Extract bottom portion (legend is typically at bottom)
    # Try different percentages to capture the legend
    legend_heights = {
        'bottom_20': int(height * 0.20),
        'bottom_25': int(height * 0.25),
        'bottom_30': int(height * 0.30),
    }
    
    for legend_name, legend_h in legend_heights.items():
        legend_start = height - legend_h
        legend_img = img.crop((0, legend_start, width, height))
        
        output_path = f"assets/battle-plans-matplotlib/legends/{filename.replace('.png', '')}_{legend_name}.png"
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        legend_img.save(output_path)
    
    print(f"✓ {filename} - legends extracted")

print(f"\n{'='*70}")
print("Legends saved to: assets/battle-plans-matplotlib/legends/")
print("\nPlease visually inspect the legends to identify:")
print("  1. What do objective markers look like?")
print("  2. What color/shape are they?")
print("  3. What text labels are next to them?")
