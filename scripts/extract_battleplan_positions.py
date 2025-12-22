"""
Extract deployment zones, objectives, and terrain positions from Wahapedia images.
Analyzes pixel data to identify elements and convert to battlefield coordinates.
"""
from PIL import Image
import numpy as np
from pathlib import Path
import json

def analyze_image(image_path):
    """Analyze Wahapedia image to extract tactical elements."""
    img = Image.open(image_path)
    img_array = np.array(img)
    
    height, width = img_array.shape[:2]
    
    # Convert image coordinates to battlefield coordinates (60x44 inches)
    def pixel_to_battlefield(x, y):
        bf_x = (x / width) * 60
        bf_y = ((height - y) / height) * 44  # Flip Y axis
        return round(bf_x, 1), round(bf_y, 1)
    
    # Identify colored regions (objectives are usually bright yellow/orange circles)
    # Deployment zones are usually blue/red rectangles
    # Terrain is usually green/gray shapes
    
    results = {
        'filename': image_path.name,
        'size': f'{width}x{height}',
        'deployment_zones': [],
        'objectives': [],
        'terrain': [],
        'special_features': []
    }
    
    # Simple color detection for objectives (yellow/orange hues)
    hsv = img.convert('HSV')
    hsv_array = np.array(hsv)
    
    # Yellow/orange objectives (hue 20-60 in HSV)
    objective_mask = (hsv_array[:,:,0] >= 20) & (hsv_array[:,:,0] <= 60) & (hsv_array[:,:,1] > 100)
    
    # Find connected components (objectives)
    from scipy import ndimage
    labeled, num_features = ndimage.label(objective_mask)
    
    for i in range(1, num_features + 1):
        positions = np.where(labeled == i)
        if len(positions[0]) > 50:  # Filter noise
            center_y = int(np.mean(positions[0]))
            center_x = int(np.mean(positions[1]))
            bf_x, bf_y = pixel_to_battlefield(center_x, center_y)
            results['objectives'].append({'x': bf_x, 'y': bf_y, 'number': i})
    
    return results

def main():
    """Analyze all Wahapedia images."""
    wahapedia_dir = Path('assets/battle-plans')
    output_file = Path('assets/battle-plans-matplotlib/extracted_positions.json')
    
    print("Analyzing Wahapedia images...")
    print("=" * 60)
    
    all_results = {}
    
    for image_path in sorted(wahapedia_dir.glob('aos-*.png')):
        print(f"\nAnalyzing: {image_path.name}")
        try:
            results = analyze_image(image_path)
            battle_plan_name = image_path.stem.replace('aos-', '').replace('-', ' ').title()
            all_results[image_path.stem] = results
            
            print(f"  Found {len(results['objectives'])} objectives")
            for obj in results['objectives']:
                print(f"    Objective at ({obj['x']}\", {obj['y']}\")")
                
        except Exception as e:
            print(f"  ERROR: {e}")
    
    # Save extracted data
    output_file.parent.mkdir(exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n✅ Extracted positions saved to: {output_file}")
    print("\nNext: Review extracted_positions.json and use for matplotlib generation")

if __name__ == "__main__":
    main()
