"""Use all 4 templates and find best matches across entire battlefield"""
import cv2
import numpy as np
from scipy.cluster.hierarchy import fclusterdata

# Load battlefield
img = cv2.imread('assets/battle-plans/aos-passing-seasons.png')
battlefield = img[:int(img.shape[0] * 0.7), :]
DPI = 14

# Load all 4 templates
templates = []
for i in range(1, 5):
    template = cv2.imread(f'assets/battle-plans-matplotlib/debug_template_{i}.png')
    if template is not None:
        templates.append((i, template))
        print(f"Loaded template {i}: {template.shape}")

print(f"\nSearching battlefield ({battlefield.shape}) with {len(templates)} templates...")

# For each pixel position, find the BEST matching template
height, width = battlefield.shape[:2]
all_matches = []

for template_id, template in templates:
    result = cv2.matchTemplate(battlefield, template, cv2.TM_CCOEFF_NORMED)
    
    # Find all matches above threshold 0.3
    matches = np.where(result >= 0.3)
    
    for y, x in zip(matches[0], matches[1]):
        confidence = result[y, x]
        all_matches.append({
            'x': x,
            'y': y,
            'confidence': confidence,
            'template_id': template_id,
            'x_inch': x / DPI,
            'y_inch': y / DPI
        })

print(f"Found {len(all_matches)} raw matches across all templates")

# Sort by confidence
all_matches.sort(key=lambda m: m['confidence'], reverse=True)

print("\nTop 20 matches:")
for i, m in enumerate(all_matches[:20]):
    print(f"  {i+1}. Template {m['template_id']}: ({m['x_inch']:.1f}\", {m['y_inch']:.1f}\") confidence={m['confidence']:.3f}")

# Cluster nearby matches (within 3 inches)
if all_matches:
    positions = np.array([[m['x'], m['y']] for m in all_matches])
    threshold_px = 3 * DPI
    
    clusters = fclusterdata(positions, threshold_px, criterion='distance', method='complete')
    
    # For each cluster, take the highest confidence match
    unique_clusters = set(clusters)
    objectives = []
    
    for cluster_id in unique_clusters:
        cluster_matches = [m for i, m in enumerate(all_matches) if clusters[i] == cluster_id]
        best = max(cluster_matches, key=lambda m: m['confidence'])
        objectives.append(best)
    
    # Sort by confidence
    objectives.sort(key=lambda m: m['confidence'], reverse=True)
    
    print(f"\n=== FOUND {len(objectives)} UNIQUE OBJECTIVES ===")
    for i, obj in enumerate(objectives, 1):
        print(f"  {i}. ({obj['x_inch']:.1f}\", {obj['y_inch']:.1f}\") - Template {obj['template_id']}, confidence={obj['confidence']:.3f}")
    
    # Visualize
    vis = battlefield.copy()
    for i, obj in enumerate(objectives, 1):
        cv2.circle(vis, (obj['x'], obj['y']), 50, (0, 255, 0), 3)
        cv2.putText(vis, f"{i}", (obj['x']-15, obj['y']-60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.putText(vis, f"T{obj['template_id']}", (obj['x']-20, obj['y']+80), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
    
    cv2.imwrite('assets/battle-plans-matplotlib/all_templates_matched.png', vis)
    print("\nSaved visualization to all_templates_matched.png")
    
    # Save result
    import json
    result = {
        'name': 'Passing Seasons',
        'expected': 4,
        'found': len(objectives),
        'objectives': [{'x': obj['x_inch'], 'y': obj['y_inch'], 'template': obj['template_id'], 
                       'confidence': obj['confidence']} for obj in objectives]
    }
    
    with open('assets/battle-plans-matplotlib/all_templates_result.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\nExpected: 4 objectives")
    print(f"Found: {len(objectives)} objectives")
