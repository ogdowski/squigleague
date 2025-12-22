"""
Extract objective token templates from Wahapedia legend and use pixel-perfect template matching.
The ghyran_objective.png contains 4 circular tokens in a horizontal strip.
Each token appears on battleplans as a circular marker with battlefield texture around it.
"""
import cv2
import numpy as np
from scipy.cluster.hierarchy import fclusterdata
import json
from pathlib import Path

# Load the objectives legend strip (446x132, 4 tokens side-by-side)
legend_img = cv2.imread('assets/battle-plans-matplotlib/ghyran_objective.png')
if legend_img is None:
    print("ERROR: Could not load ghyran_objective.png")
    exit(1)

print(f"Legend image: {legend_img.shape}")

# Divide into 4 equal sections (one per token type)
legend_height, legend_width = legend_img.shape[:2]
token_width = legend_width // 4

print(f"\nExtracting 4 objective tokens ({token_width}x{legend_height} each)...")

# Extract each token as a template
templates = []
token_names = ['Oakenbrow', 'Gnarlroot', 'Winterleaf', 'Heartwood']

for i in range(4):
    x_start = i * token_width
    x_end = (i + 1) * token_width
    
    token = legend_img[:, x_start:x_end]
    templates.append({
        'name': token_names[i],
        'image': token,
        'size': token.shape
    })
    
    # Save for inspection
    cv2.imwrite(f'assets/battle-plans-matplotlib/token_{token_names[i]}.png', token)
    print(f"  {token_names[i]}: {token.shape}")

# Battle plan configuration (from battle_plans.py)
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

DPI = 14  # pixels per inch
THRESHOLD = 0.6  # correlation threshold
CLUSTER_DISTANCE = 3 * DPI  # 3 inches in pixels

def extract_objectives(filename, expected_count):
    """Find objective markers in a battleplan image using template matching."""
    
    image_path = Path(f'assets/battle-plans/{filename}')
    if not image_path.exists():
        return None
    
    img = cv2.imread(str(image_path))
    if img is None:
        return None
    
    height, width = img.shape[:2]
    
    # Battlefield is top 70% (exclude legend at bottom)
    battlefield = img[:int(height * 0.7), :]
    
    print(f"\n{filename} - Expecting {expected_count} objectives")
    print(f"  Image: {width}x{height}, Battlefield: {battlefield.shape[1]}x{battlefield.shape[0]}")
    
    all_matches = []
    
    # Try each template
    for template_info in templates:
        template = template_info['image']
        token_name = template_info['name']
        
        # Template matching
        result = cv2.matchTemplate(battlefield, template, cv2.TM_CCOEFF_NORMED)
        
        # Find matches above threshold
        matches = np.where(result >= THRESHOLD)
        
        for y, x in zip(matches[0], matches[1]):
            confidence = result[y, x]
            
            # Convert to battlefield coordinates (60"x44")
            x_inch = x / DPI
            y_inch = y / DPI
            
            all_matches.append({
                'x_px': x,
                'y_px': y,
                'x_inch': round(x_inch, 1),
                'y_inch': round(y_inch, 1),
                'confidence': float(confidence),
                'token_type': token_name
            })
    
    if not all_matches:
        print(f"  WARNING: No matches found!")
        return {
            'name': BATTLE_PLANS[filename]['name'],
            'expected': expected_count,
            'found': 0,
            'objectives': []
        }
    
    # Sort by confidence
    all_matches.sort(key=lambda m: m['confidence'], reverse=True)
    
    print(f"  Found {len(all_matches)} raw matches, top confidence: {all_matches[0]['confidence']:.3f}")
    
    # Cluster nearby matches (same objective detected multiple times)
    positions = np.array([[m['x_px'], m['y_px']] for m in all_matches])
    clusters = fclusterdata(positions, CLUSTER_DISTANCE, criterion='distance', method='complete')
    
    # Take best match from each cluster
    unique_clusters = set(clusters)
    objectives = []
    
    for cluster_id in unique_clusters:
        cluster_matches = [m for i, m in enumerate(all_matches) if clusters[i] == cluster_id]
        best = max(cluster_matches, key=lambda m: m['confidence'])
        objectives.append(best)
    
    # Sort by confidence and take top N
    objectives.sort(key=lambda m: m['confidence'], reverse=True)
    objectives = objectives[:expected_count]
    
    print(f"  After clustering: {len(objectives)} unique objectives")
    for i, obj in enumerate(objectives, 1):
        print(f"    {i}. ({obj['x_inch']}\", {obj['y_inch']}\") - {obj['token_type']} [{obj['confidence']:.3f}]")
    
    return {
        'name': BATTLE_PLANS[filename]['name'],
        'expected': expected_count,
        'found': len(objectives),
        'objectives': objectives
    }

# Process all battle plans
print("\n" + "="*70)
print("EXTRACTING OBJECTIVES FROM ALL BATTLEPLANS")
print("="*70)

results = {}

for filename, config in BATTLE_PLANS.items():
    result = extract_objectives(filename, config['count'])
    if result:
        results[filename] = result

# Save results
output_file = 'assets/battle-plans-matplotlib/objectives_extracted.json'
with open(output_file, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n{'='*70}")
print(f"RESULTS SAVED: {output_file}")
print(f"{'='*70}")

# Summary
total_expected = sum(r['expected'] for r in results.values())
total_found = sum(r['found'] for r in results.values())
print(f"\nTotal: Found {total_found}/{total_expected} objectives")

for filename, result in results.items():
    status = "✓" if result['found'] == result['expected'] else "✗"
    print(f"  {status} {result['name']}: {result['found']}/{result['expected']}")
