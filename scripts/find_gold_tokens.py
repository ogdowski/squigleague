"""
Search for Ghyranite objective tokens - gold-bordered circles with colored centers.
Based on Wahapedia legend: circular tokens with gold/bronze borders and colored backgrounds.
"""
from PIL import Image
import numpy as np
from pathlib import Path
from scipy import ndimage
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import pdist
import json

BATTLE_PLANS = {
    "aos-passing-seasons.png": {"count": 4, "name": "Passing Seasons"},
    "aos-paths-of-the-fey.png": {"count": 5, "name": "Paths of the Fey"},
    "aos-roiling-roots.png": {"count": 6, "name": "Roiling Roots"},
    "aos-cyclic-shifts.png": {"count": 6, "name": "Cyclic Shifts"},
    "aos-surge-of-slaughter.png": {"count": 5, "name": "Surge of Slaughter"},
    "aos-linked-ley-lines.png": {"count": 5, "name": "Linked Ley Lines"},
    "aos-noxious-nexus.png": {"count": 3, "name": "Noxious Nexus"},
    "aos-the-liferoots.png": {"count": 2, "name": "The Liferoots"},
    "aos-bountiful-equinox.png": {"count": 5, "name": "Bountiful Equinox"},
    "aos-lifecycle.png": {"count": 4, "name": "Lifecycle"},
    "aos-creeping-corruption.png": {"count": 6, "name": "Creeping Corruption"},
    "aos-grasp-of-thorns.png": {"count": 4, "name": "Grasp of Thorns"},
}

def find_objective_tokens(filename, expected_count):
    """Find gold-bordered circular objective tokens."""
    image_path = Path(f"assets/battle-plans/{filename}")
    
    img = Image.open(image_path)
    img_array = np.array(img)
    
    height, width = img_array.shape[:2]
    
    if len(img_array.shape) == 2:
        img_array = np.stack([img_array] * 3, axis=-1)
    elif img_array.shape[2] == 4:
        img_array = img_array[:, :, :3]
    
    # Exclude legend area (bottom 30%)
    battlefield_height = int(height * 0.70)
    battlefield = img_array[:battlefield_height, :]
    
    r = battlefield[:, :, 0]
    g = battlefield[:, :, 1]
    b = battlefield[:, :, 2]
    
    # Look for GOLD/BRONZE borders - be more lenient
    # The tokens might have darker gold or bronze tones
    gold_mask = (
        (r > 100) & (r < 255) &
        (g > 80) & (g < 220) &
        (b > 15) & (b < 150) &
        ((r > g * 0.9) | (r > b * 1.2))  # Gold-ish tones
    )
    
    # Find connected gold regions
    labeled, num_features = ndimage.label(gold_mask)
    
    candidates = []
    
    for i in range(1, num_features + 1):
        region_mask = (labeled == i)
        region_size = np.sum(region_mask)
        
        # Objective tokens can be quite small (the icons are only ~100-1000 pixels)
        if 80 < region_size < 2000:
            y_coords, x_coords = np.where(region_mask)
            
            x_min, x_max = x_coords.min(), x_coords.max()
            y_min, y_max = y_coords.min(), y_coords.max()
            
            w = x_max - x_min
            h = y_max - y_min
            
            # Check if roughly circular - be more lenient
            aspect = min(w, h) / max(w, h, 0.01)
            
            if aspect > 0.5:  # More lenient circularity check
                center_x = np.mean(x_coords)
                center_y = np.mean(y_coords)
                
                # Check if there's a colored center (red, green, purple, blue)
                cy = int(center_y)
                cx = int(center_x)
                
                # Sample the center area
                if 0 <= cy < battlefield.shape[0] and 0 <= cx < battlefield.shape[1]:
                    center_color = battlefield[cy, cx]
                    
                    # Check if center has distinct color (not gold, not gray)
                    cr, cg, cb = center_color
                    
                    # Has colored center if one channel dominates or has distinct hue
                    has_colored_center = (
                        (cr > cg + 20) or  # Reddish
                        (cg > cr + 20) or  # Greenish
                        (cb > cr + 20) or  # Bluish
                        (cr > 100 and cb > 100)  # Purple
                    )
                    
                    if has_colored_center:
                        candidates.append({
                            'pixel_pos': (center_x, center_y),
                            'size': region_size,
                            'center_color': (int(cr), int(cg), int(cb))
                        })
    
    if not candidates:
        return None
    
    # Cluster nearby candidates
    if len(candidates) > expected_count:
        positions = np.array([c['pixel_pos'] for c in candidates])
        
        if len(positions) > 1:
            distances = pdist(positions)
            Z = linkage(distances, method='single')
            clusters = fcluster(Z, t=30, criterion='distance')
            
            clustered = []
            for cluster_id in range(1, max(clusters) + 1):
                members = [candidates[i] for i in range(len(candidates)) if clusters[i] == cluster_id]
                best = max(members, key=lambda x: x['size'])
                clustered.append(best)
            
            candidates = clustered
    
    # Sort by size and take top N
    candidates.sort(key=lambda x: x['size'], reverse=True)
    top_objectives = candidates[:expected_count]
    
    # Convert to battlefield coordinates
    objectives = []
    for obj in top_objectives:
        cx, cy = obj['pixel_pos']
        bf_x = (cx / width) * 60
        bf_y = ((battlefield_height - cy) / battlefield_height) * 44
        
        objectives.append({
            'x': round(bf_x, 1),
            'y': round(bf_y, 1),
            'color': f"RGB{obj['center_color']}"
        })
    
    return objectives

# Process all battle plans
results = {}
print("Searching for gold-bordered objective tokens...")
print("="*70)

for filename, metadata in BATTLE_PLANS.items():
    print(f"\n{metadata['name']} ({filename})")
    print(f"  Expected: {metadata['count']} objectives")
    
    objectives = find_objective_tokens(filename, metadata['count'])
    
    if objectives:
        print(f"  Found: {len(objectives)} objectives")
        for i, obj in enumerate(objectives, 1):
            print(f"    {i}. ({obj['x']:5.1f}\", {obj['y']:5.1f}\") - {obj['color']}")
        
        results[filename] = {
            'name': metadata['name'],
            'objective_count': len(objectives),
            'objectives': [{'x': o['x'], 'y': o['y']} for o in objectives]
        }
    else:
        print(f"  ❌ Failed to find tokens")

# Save
output_path = "assets/battle-plans-matplotlib/objectives_corrected.json"
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n{'='*70}")
print(f"✅ Results saved to: {output_path}")
print(f"Extracted: {len(results)}/{len(BATTLE_PLANS)} battle plans")
