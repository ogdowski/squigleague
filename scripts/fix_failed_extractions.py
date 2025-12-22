"""
Fix extraction for Roiling Roots and Creeping Corruption.
These have 6 objectives each - may need adjusted detection parameters.
"""
from PIL import Image
import numpy as np
from pathlib import Path
from scipy import ndimage
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import pdist

def extract_objectives_robust(filename, expected_count):
    """More robust extraction with multiple strategies."""
    image_path = Path(f"assets/battle-plans/{filename}")
    
    img = Image.open(image_path)
    img_array = np.array(img)
    
    height, width = img_array.shape[:2]
    
    if len(img_array.shape) == 2:
        img_array = np.stack([img_array] * 3, axis=-1)
    elif img_array.shape[2] == 4:
        img_array = img_array[:, :, :3]
    
    legend_start_y = int(height * 0.75)
    battlefield = img_array[:legend_start_y, :]
    
    # Strategy 1: Dark circular markers (common in many maps)
    r = battlefield[:, :, 0]
    g = battlefield[:, :, 1]
    b = battlefield[:, :, 2]
    
    # Look for dark spots that are objectives
    dark_mask = (r < 60) & (g < 60) & (b < 60)
    
    labeled, num_features = ndimage.label(dark_mask)
    
    candidates = []
    for i in range(1, num_features + 1):
        region_mask = (labeled == i)
        region_size = np.sum(region_mask)
        
        if 30 < region_size < 500:
            y_coords, x_coords = np.where(region_mask)
            
            x_min, x_max = x_coords.min(), x_coords.max()
            y_min, y_max = y_coords.min(), y_coords.max()
            w = x_max - x_min
            h = y_max - y_min
            aspect = min(w, h) / max(w, h, 0.01)
            
            if aspect > 0.4:  # More lenient
                center_x = np.mean(x_coords)
                center_y = np.mean(y_coords)
                
                candidates.append({
                    'pixel_pos': (center_x, center_y),
                    'size': region_size
                })
    
    # Strategy 2: Edge-based circular detection
    from scipy.ndimage import sobel
    gray = np.mean(battlefield, axis=2)
    edge_x = sobel(gray, axis=1)
    edge_y = sobel(gray, axis=0)
    edges = np.hypot(edge_x, edge_y)
    
    threshold = np.percentile(edges, 92)
    strong_edges = edges > threshold
    
    labeled_edges, num_edge_features = ndimage.label(strong_edges)
    
    for i in range(1, min(num_edge_features + 1, 1000)):
        region_mask = (labeled_edges == i)
        region_size = np.sum(region_mask)
        
        if 30 < region_size < 500:
            y_coords, x_coords = np.where(region_mask)
            
            x_min, x_max = x_coords.min(), x_coords.max()
            y_min, y_max = y_coords.min(), y_coords.max()
            w = x_max - x_min
            h = y_max - y_min
            aspect = min(w, h) / max(w, h, 0.01)
            
            if aspect > 0.6:
                center_x = np.mean(x_coords)
                center_y = np.mean(y_coords)
                
                candidates.append({
                    'pixel_pos': (center_x, center_y),
                    'size': region_size
                })
    
    if not candidates:
        return None
    
    # Cluster nearby candidates
    if len(candidates) > expected_count:
        positions = np.array([c['pixel_pos'] for c in candidates])
        
        if len(positions) > 1:
            distances = pdist(positions)
            Z = linkage(distances, method='single')
            clusters = fcluster(Z, t=25, criterion='distance')
            
            clustered_candidates = []
            for cluster_id in range(1, max(clusters) + 1):
                cluster_members = [candidates[i] for i in range(len(candidates)) if clusters[i] == cluster_id]
                best = max(cluster_members, key=lambda x: x['size'])
                clustered_candidates.append(best)
            
            candidates = clustered_candidates
    
    # Sort by size and take top N
    candidates.sort(key=lambda x: x['size'], reverse=True)
    top_objectives = candidates[:expected_count]
    
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

# Test on failed battle plans
for filename, expected in [("aos-roiling-roots.png", 6), ("aos-creeping-corruption.png", 6)]:
    print(f"\n{filename} (expect {expected} objectives)")
    objectives = extract_objectives_robust(filename, expected)
    
    if objectives:
        print(f"  Found: {len(objectives)} objectives")
        for i, obj in enumerate(objectives):
            print(f"    {i+1}. ({obj['x']:5.1f}\", {obj['y']:5.1f}\")")
    else:
        print(f"  ❌ Still failed")
