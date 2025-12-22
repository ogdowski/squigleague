"""
Final extraction: Use legend to identify objective markers, cluster detections, 
and extract the exact N objectives for each battle plan.
"""
from PIL import Image, ImageDraw
import numpy as np
from pathlib import Path
from scipy import ndimage
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import pdist
import json

# Battle plan metadata
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

def analyze_battleplan(filename):
    """Extract objective positions from a single battle plan image."""
    image_path = Path(f"assets/battle-plans/{filename}")
    
    if not image_path.exists():
        return None
    
    img = Image.open(image_path)
    img_array = np.array(img)
    
    height, width = img_array.shape[:2]
    
    # Convert to RGB
    if len(img_array.shape) == 2:
        img_array = np.stack([img_array] * 3, axis=-1)
    elif img_array.shape[2] == 4:
        img_array = img_array[:, :, :3]
    
    expected_count = BATTLE_PLANS[filename]["count"]
    
    # Legend is in bottom 25%
    legend_start_y = int(height * 0.75)
    legend_region = img_array[legend_start_y:, :]
    
    # Find circular shapes in legend
    from scipy.ndimage import sobel
    
    gray_legend = np.mean(legend_region, axis=2)
    edge_x = sobel(gray_legend, axis=1)
    edge_y = sobel(gray_legend, axis=0)
    edges_legend = np.hypot(edge_x, edge_y)
    
    threshold = np.percentile(edges_legend, 85)
    strong_edges_legend = edges_legend > threshold
    
    labeled_legend, num_legend_features = ndimage.label(strong_edges_legend)
    
    # Extract legend marker colors
    legend_colors = []
    for i in range(1, min(num_legend_features + 1, 200)):
        region_mask = (labeled_legend == i)
        area = np.sum(region_mask)
        
        if 20 < area < 500:
            y_coords, x_coords = np.where(region_mask)
            x_min, x_max = x_coords.min(), x_coords.max()
            y_min, y_max = y_coords.min(), y_coords.max()
            
            w = x_max - x_min
            h = y_max - y_min
            aspect = min(w, h) / max(w, h, 0.01)
            
            if aspect > 0.6:
                cy_abs = legend_start_y + int((y_min + y_max) / 2)
                cx_abs = int((x_min + x_max) / 2)
                
                if cy_abs < height and cx_abs < width:
                    color = img_array[cy_abs, cx_abs]
                    legend_colors.append({
                        'color': color,
                        'size': area
                    })
    
    # Sort by size
    legend_colors.sort(key=lambda x: x['size'], reverse=True)
    
    # Search battlefield for markers matching legend colors
    battlefield = img_array[:legend_start_y, :]
    all_candidates = []
    
    for template in legend_colors[:3]:  # Try top 3 legend colors
        r_t, g_t, b_t = template['color']
        
        r = battlefield[:, :, 0]
        g = battlefield[:, :, 1]
        b = battlefield[:, :, 2]
        
        tolerance = 40
        color_match = (
            (np.abs(r.astype(int) - r_t) < tolerance) &
            (np.abs(g.astype(int) - g_t) < tolerance) &
            (np.abs(b.astype(int) - b_t) < tolerance)
        )
        
        if np.sum(color_match) == 0:
            continue
        
        labeled, num_features = ndimage.label(color_match)
        
        for i in range(1, num_features + 1):
            region_mask = (labeled == i)
            region_size = np.sum(region_mask)
            
            # Reasonable objective size
            if 30 < region_size < 500:
                y_coords, x_coords = np.where(region_mask)
                
                # Check circularity
                x_min, x_max = x_coords.min(), x_coords.max()
                y_min, y_max = y_coords.min(), y_coords.max()
                w = x_max - x_min
                h = y_max - y_min
                aspect = min(w, h) / max(w, h, 0.01)
                
                if aspect > 0.5:
                    center_x = np.mean(x_coords)
                    center_y = np.mean(y_coords)
                    
                    all_candidates.append({
                        'pixel_pos': (center_x, center_y),
                        'size': region_size
                    })
    
    if not all_candidates:
        return None
    
    # Cluster nearby candidates (they might be duplicates from different color matches)
    if len(all_candidates) > expected_count:
        positions = np.array([c['pixel_pos'] for c in all_candidates])
        
        # Hierarchical clustering to merge nearby detections
        if len(positions) > 1:
            distances = pdist(positions)
            Z = linkage(distances, method='single')
            # Cluster with distance threshold (merge if within 20 pixels)
            clusters = fcluster(Z, t=20, criterion='distance')
            
            # Take largest candidate from each cluster
            clustered_candidates = []
            for cluster_id in range(1, max(clusters) + 1):
                cluster_members = [all_candidates[i] for i in range(len(all_candidates)) if clusters[i] == cluster_id]
                # Pick largest
                best = max(cluster_members, key=lambda x: x['size'])
                clustered_candidates.append(best)
            
            all_candidates = clustered_candidates
    
    # Sort by size and take top N
    all_candidates.sort(key=lambda x: x['size'], reverse=True)
    top_objectives = all_candidates[:expected_count]
    
    # Convert to battlefield coordinates
    objectives = []
    for obj in top_objectives:
        cx, cy = obj['pixel_pos']
        bf_x = (cx / width) * 60
        bf_y = ((legend_start_y - cy) / legend_start_y) * 44
        
        objectives.append({
            'x': round(bf_x, 1),
            'y': round(bf_y, 1)
        })
    
    return objectives

# Process all battle plans
results = {}

for filename, metadata in BATTLE_PLANS.items():
    print(f"\n{metadata['name']} ({filename})")
    print(f"  Expected: {metadata['count']} objectives")
    
    objectives = analyze_battleplan(filename)
    
    if objectives:
        print(f"  Found: {len(objectives)} objectives")
        for i, obj in enumerate(objectives):
            print(f"    {i+1}. ({obj['x']:5.1f}\", {obj['y']:5.1f}\")")
        
        results[filename] = {
            'name': metadata['name'],
            'objective_count': len(objectives),
            'objectives': objectives
        }
    else:
        print(f"  ❌ Failed to extract objectives")

# Save results
output_path = "assets/battle-plans-matplotlib/extracted_objectives.json"
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n\n✅ Results saved to: {output_path}")
print(f"Extracted objectives for {len(results)}/{len(BATTLE_PLANS)} battle plans")
