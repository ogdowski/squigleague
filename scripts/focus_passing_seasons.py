"""
Focus on ONE battle plan (Passing Seasons) to perfect the detection method.
Extract objective token templates from legend, use template matching.
"""
import cv2
import numpy as np
from pathlib import Path
import json

# Focus on Passing Seasons - 4 objectives expected
image_path = "assets/battle-plans/aos-passing-seasons.png"

# Load image
img = cv2.imread(image_path)
if img is None:
    print(f"Failed to load {image_path}")
    exit(1)

height, width = img.shape[:2]
print(f"Image: {image_path}")
print(f"Size: {width}x{height}")
print(f"Expected objectives: 4")
print()

# The legend shows 4 token types at the bottom
# Based on the Wahapedia screenshot provided, the legend is around the bottom portion
# Let's look at the bottom 150 pixels for the legend

legend_height = 150
legend_region = img[height - legend_height:, :]

# Save legend for inspection
cv2.imwrite("assets/battle-plans-matplotlib/debug_legend.png", legend_region)
print(f"Legend region saved: debug_legend.png (bottom {legend_height}px)")
print()

# The 4 objective tokens should be visible in the legend
# They are circular tokens approximately 80-100 pixels in diameter
# Let's manually extract them from known positions in the legend

# Based on the legend layout, the tokens are typically arranged horizontally
# Let's sample 4 regions across the legend width

legend_w = legend_region.shape[1]
legend_h = legend_region.shape[0]

# Estimate token positions in legend (horizontally spaced)
# Tokens are usually in the middle vertically, spaced evenly horizontally
token_size = 80  # approximate diameter

# Sample 4 positions across the legend
sample_x_positions = [
    int(legend_w * 0.15),  # ~15% from left
    int(legend_w * 0.35),  # ~35%
    int(legend_w * 0.55),  # ~55%
    int(legend_w * 0.75),  # ~75%
]

# Y position is likely in the middle of the legend
sample_y = legend_h // 2

print("Extracting token templates from legend...")
templates = []

for i, x in enumerate(sample_x_positions):
    # Extract region around this position
    half_size = token_size // 2
    
    x1 = max(0, x - half_size)
    x2 = min(legend_w, x + half_size)
    y1 = max(0, sample_y - half_size)
    y2 = min(legend_h, sample_y + half_size)
    
    template = legend_region[y1:y2, x1:x2]
    
    if template.size > 0:
        templates.append({
            'image': template,
            'name': f'token_{i+1}',
            'position': (x, sample_y)
        })
        
        # Save template for inspection
        cv2.imwrite(f"assets/battle-plans-matplotlib/debug_template_{i+1}.png", template)
        print(f"  Template {i+1}: extracted from legend at ({x}, {sample_y}), size {template.shape}")

print()
print(f"Extracted {len(templates)} templates")
print()

# Now search for these templates in the battlefield (top 70% of image)
battlefield_height = int(height * 0.70)
battlefield = img[:battlefield_height, :]

print(f"Searching battlefield (top {battlefield_height}px)...")
print()

# Convert to grayscale for template matching
battlefield_gray = cv2.cvtColor(battlefield, cv2.COLOR_BGR2GRAY)

all_matches = []

for template_data in templates:
    template = template_data['image']
    template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    
    # Template matching
    result = cv2.matchTemplate(battlefield_gray, template_gray, cv2.TM_CCOEFF_NORMED)
    
    # Find all matches above threshold
    threshold = 0.5  # Start conservative
    locations = np.where(result >= threshold)
    
    print(f"Template '{template_data['name']}':")
    print(f"  Max correlation: {result.max():.3f}")
    print(f"  Matches above {threshold}: {len(locations[0])}")
    
    for pt in zip(*locations[::-1]):
        match_x = pt[0] + template.shape[1] // 2
        match_y = pt[1] + template.shape[0] // 2
        
        # Convert to battlefield coordinates
        bf_x = (match_x / width) * 60
        bf_y = ((battlefield_height - match_y) / battlefield_height) * 44
        
        all_matches.append({
            'x': round(bf_x, 1),
            'y': round(bf_y, 1),
            'confidence': float(result[pt[1], pt[0]]),
            'template': template_data['name']
        })
        
        print(f"    Match at ({bf_x:.1f}\", {bf_y:.1f}\") - confidence: {result[pt[1], pt[0]]:.3f}")
    
    print()

print(f"Total matches found: {len(all_matches)}")
print()

# Cluster nearby matches (might be duplicates from overlapping templates)
if len(all_matches) > 4:
    print("Clustering nearby matches...")
    from scipy.cluster.hierarchy import linkage, fcluster
    from scipy.spatial.distance import pdist
    
    positions = np.array([[m['x'], m['y']] for m in all_matches])
    distances = pdist(positions)
    Z = linkage(distances, method='single')
    clusters = fcluster(Z, t=3, criterion='distance')  # 3" threshold
    
    # Take highest confidence match from each cluster
    clustered_matches = []
    for cluster_id in range(1, max(clusters) + 1):
        cluster_members = [all_matches[i] for i in range(len(all_matches)) if clusters[i] == cluster_id]
        best = max(cluster_members, key=lambda x: x['confidence'])
        clustered_matches.append(best)
    
    all_matches = clustered_matches
    print(f"After clustering: {len(all_matches)} unique objectives")
    print()

# Sort by confidence and take top 4
all_matches.sort(key=lambda x: x['confidence'], reverse=True)
final_objectives = all_matches[:4]

print("="*70)
print("FINAL RESULT:")
print("="*70)
for i, obj in enumerate(final_objectives, 1):
    print(f"{i}. ({obj['x']:5.1f}\", {obj['y']:5.1f}\") - confidence: {obj['confidence']:.3f} - from {obj['template']}")

# Save result
result = {
    'name': 'Passing Seasons',
    'objective_count': len(final_objectives),
    'objectives': [{'x': o['x'], 'y': o['y']} for o in final_objectives]
}

with open('assets/battle-plans-matplotlib/passing_seasons_result.json', 'w') as f:
    json.dump(result, f, indent=2)

print()
print("Result saved to: passing_seasons_result.json")
print()
print("Next steps:")
print("1. Inspect debug_legend.png to see if legend was extracted correctly")
print("2. Inspect debug_template_*.png to see if token templates look correct")
print("3. If templates look wrong, manually specify correct pixel coordinates")
