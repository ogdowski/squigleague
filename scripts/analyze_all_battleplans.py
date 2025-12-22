"""
Analyze all battle plan images to find common objective marker patterns.
This will help us understand the visual signature of objectives across all maps.
"""
from PIL import Image
import numpy as np
from scipy import ndimage
from pathlib import Path
import json

battle_plans = {
    "aos-passing-seasons.png": 4,
    "aos-paths-of-the-fey.png": 4,
    "aos-roiling-roots.png": 1,
    "aos-cyclic-shifts.png": 1,
    "aos-surge-of-slaughter.png": 2,
    "aos-linked-ley-lines.png": 1,
    "aos-noxious-nexus.png": 1,
    "aos-the-liferoots.png": 1,
    "aos-bountiful-equinox.png": 1,
    "aos-lifecycle.png": 1,
    "aos-creeping-corruption.png": 1,
    "aos-grasp-of-thorns.png": 1,
}

results = {}

for filename, expected_count in battle_plans.items():
    image_path = Path(f"assets/battle-plans/{filename}")
    
    if not image_path.exists():
        continue
    
    img = Image.open(image_path)
    img_array = np.array(img)
    
    height, width = img_array.shape[:2]
    
    # Convert to RGB
    if len(img_array.shape) == 2:
        img_array = np.stack([img_array] * 3, axis=-1)
    elif img_array.shape[2] == 4:
        img_array = img_array[:, :, :3]
    
    # Edge detection for circular patterns
    gray = np.mean(img_array, axis=2)
    from scipy.ndimage import sobel
    
    edge_x = sobel(gray, axis=1)
    edge_y = sobel(gray, axis=0)
    edges = np.hypot(edge_x, edge_y)
    
    edge_threshold = np.percentile(edges, 90)
    strong_edges = edges > edge_threshold
    
    labeled_edges, num_edge_regions = ndimage.label(strong_edges)
    
    # Find circular regions
    circular_candidates = []
    for i in range(1, min(num_edge_regions + 1, 1000)):
        region_mask = (labeled_edges == i)
        area = np.sum(region_mask)
        
        # Size filter - objectives should be medium-sized (not tiny text, not huge zones)
        if area < 50 or area > 3000:
            continue
        
        y_coords, x_coords = np.where(region_mask)
        
        x_min, x_max = x_coords.min(), x_coords.max()
        y_min, y_max = y_coords.min(), y_coords.max()
        
        width_px = x_max - x_min
        height_px = y_max - y_min
        
        # Circles have similar width and height
        aspect_ratio = min(width_px, height_px) / max(width_px, height_px + 0.01)
        
        if aspect_ratio > 0.75:  # Relatively circular
            center_x = (x_min + x_max) / 2
            center_y = (y_min + y_max) / 2
            
            # Convert to battlefield coordinates
            bf_x = (center_x / width) * 60
            bf_y = ((height - center_y) / height) * 44
            
            circular_candidates.append({
                'position': (bf_x, bf_y),
                'size': area,
                'aspect': aspect_ratio
            })
    
    # Sort by size
    circular_candidates.sort(key=lambda x: x['size'], reverse=True)
    
    # Take top N based on expected count, plus a few extra
    top_candidates = circular_candidates[:expected_count + 3]
    
    results[filename] = {
        'expected': expected_count,
        'total_circular': len(circular_candidates),
        'top_candidates': top_candidates
    }
    
    print(f"\n{filename} (expect {expected_count} objectives):")
    print(f"  Found {len(circular_candidates)} circular patterns")
    print(f"  Top {len(top_candidates)} candidates:")
    for i, cand in enumerate(top_candidates):
        x, y = cand['position']
        print(f"    {i+1}. ({x:4.1f}\", {y:4.1f}\")  size={cand['size']:4d}px  aspect={cand['aspect']:.2f}")

# Save results
output_path = "assets/battle-plans-matplotlib/all_battleplans_analysis.json"
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n\nResults saved to: {output_path}")
print("\nPattern Analysis:")
print("Looking for commonalities across all battle plans...")

# Find size patterns
all_sizes = []
for filename, data in results.items():
    for cand in data['top_candidates'][:data['expected']]:
        all_sizes.append(cand['size'])

if all_sizes:
    print(f"\nObjective marker sizes:")
    print(f"  Min: {min(all_sizes)} px")
    print(f"  Max: {max(all_sizes)} px")
    print(f"  Avg: {np.mean(all_sizes):.0f} px")
    print(f"  Median: {np.median(all_sizes):.0f} px")
