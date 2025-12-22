"""
Use template matching to find objective tokens.
Extract the tokens from the legend, then search for them in the battlefield.
"""
import cv2
import numpy as np
from PIL import Image
from pathlib import Path
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

def extract_templates_from_legend(image_path):
    """Extract objective token templates from the legend."""
    img = cv2.imread(str(image_path))
    height, width = img.shape[:2]
    
    # Legend is in bottom 25-30%
    legend_start = int(height * 0.72)
    legend = img[legend_start:, :]
    
    # Find circular contours in the legend
    gray = cv2.cvtColor(legend, cv2.COLOR_BGR2GRAY)
    
    # Use adaptive threshold to find tokens
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                    cv2.THRESH_BINARY_INV, 21, 10)
    
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    templates = []
    for contour in contours:
        area = cv2.contourArea(contour)
        
        # Legend tokens are medium-sized
        if 500 < area < 5000:
            x, y, w, h = cv2.boundingRect(contour)
            
            # Check circularity
            aspect = min(w, h) / max(w, h, 0.01)
            
            if aspect > 0.7:  # Circular
                # Extract template with some padding
                pad = 5
                x1 = max(0, x - pad)
                y1 = max(0, y - pad)
                x2 = min(legend.shape[1], x + w + pad)
                y2 = min(legend.shape[0], y + h + pad)
                
                template = legend[y1:y2, x1:x2]
                
                if template.shape[0] > 10 and template.shape[1] > 10:
                    templates.append({
                        'image': template,
                        'size': (w, h)
                    })
    
    # Sort by size and return ALL templates (not just top 4)
    templates.sort(key=lambda t: t['size'][0] * t['size'][1], reverse=True)
    
    return templates[:10]  # Return top 10 templates to cover all varieties

def find_objectives_by_template(filename, expected_count):
    """Find objectives using template matching."""
    image_path = Path(f"assets/battle-plans/{filename}")
    
    img = cv2.imread(str(image_path))
    height, width = img.shape[:2]
    
    # Extract templates from legend
    templates = extract_templates_from_legend(image_path)
    
    if not templates:
        return None
    
    # Search in battlefield area (top 70%)
    battlefield_height = int(height * 0.70)
    battlefield = img[:battlefield_height, :]
    
    all_matches = []
    
    # Try each template
    for template_data in templates:
        template = template_data['image']
        th, tw = template.shape[:2]
        
        # Multi-scale template matching
        for scale in [0.8, 0.9, 1.0, 1.1, 1.2]:
            scaled_template = cv2.resize(template, None, fx=scale, fy=scale)
            sth, stw = scaled_template.shape[:2]
            
            if sth > battlefield.shape[0] or stw > battlefield.shape[1]:
                continue
            
            # Template matching
            result = cv2.matchTemplate(battlefield, scaled_template, cv2.TM_CCOEFF_NORMED)
            
            # Find matches above threshold - be more lenient
            threshold = 0.55
            locations = np.where(result >= threshold)
            
            for pt in zip(*locations[::-1]):
                x, y = pt
                # Center of match
                center_x = x + stw // 2
                center_y = y + sth // 2
                match_value = result[y, x]
                
                all_matches.append({
                    'pos': (center_x, center_y),
                    'confidence': match_value,
                    'scale': scale
                })
    
    if not all_matches:
        return None
    
    # Remove duplicate detections (nearby matches)
    filtered_matches = []
    all_matches.sort(key=lambda m: m['confidence'], reverse=True)
    
    for match in all_matches:
        mx, my = match['pos']
        
        # Check if too close to existing match
        too_close = False
        for existing in filtered_matches:
            ex, ey = existing['pos']
            dist = np.sqrt((mx - ex)**2 + (my - ey)**2)
            if dist < 30:  # Within 30 pixels
                too_close = True
                break
        
        if not too_close:
            filtered_matches.append(match)
    
    # Take top N matches
    filtered_matches = filtered_matches[:expected_count]
    
    # Convert to battlefield coordinates
    objectives = []
    for match in filtered_matches:
        cx, cy = match['pos']
        bf_x = (cx / width) * 60
        bf_y = ((battlefield_height - cy) / battlefield_height) * 44
        
        objectives.append({
            'x': round(bf_x, 1),
            'y': round(bf_y, 1),
            'confidence': float(match['confidence'])
        })
    
    return objectives

# Process all battle plans
results = {}
print("Using template matching to find objectives...")
print("="*70)

for filename, metadata in BATTLE_PLANS.items():
    print(f"\n{metadata['name']} ({filename})")
    print(f"  Expected: {metadata['count']} objectives")
    
    objectives = find_objectives_by_template(filename, metadata['count'])
    
    if objectives:
        print(f"  Found: {len(objectives)} objectives")
        for i, obj in enumerate(objectives, 1):
            print(f"    {i}. ({obj['x']:5.1f}\", {obj['y']:5.1f}\") - confidence: {obj['confidence']:.2f}")
        
        results[filename] = {
            'name': metadata['name'],
            'objective_count': len(objectives),
            'objectives': [{'x': o['x'], 'y': o['y']} for o in objectives]
        }
    else:
        print(f"  ❌ Failed to extract")

# Save
output_path = "assets/battle-plans-matplotlib/objectives_template_matched.json"
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n{'='*70}")
print(f"✅ Results saved to: {output_path}")
print(f"Extracted: {len(results)}/{len(BATTLE_PLANS)} battle plans")
