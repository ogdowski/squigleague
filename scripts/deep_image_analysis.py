"""
Deep analysis of Wahapedia image structure to understand objective markers.
Will analyze shapes, patterns, and spatial distribution.
"""
from PIL import Image, ImageDraw
import numpy as np
from scipy import ndimage
from pathlib import Path

image_path = Path("assets/battle-plans/aos-passing-seasons.png")
img = Image.open(image_path)
img_array = np.array(img)

print(f"Image: {image_path.name}")
print(f"Expected: 4 objectives for Passing Seasons")
print(f"Description: 2 Gnarlroot + 2 Oakenbrow objectives")
print(f"Locations: 24\" and 48\" from long edge, 12\" from center")
print()

height, width = img_array.shape[:2]
print(f"Image dimensions: {width}x{height} pixels")
print(f"Battlefield: 60\" x 44\" inches")
print(f"Scale: {width/60:.1f} pixels per inch width, {height/44:.1f} pixels per inch height")
print()

# Convert to RGB
if len(img_array.shape) == 2:
    img_array = np.stack([img_array] * 3, axis=-1)
elif img_array.shape[2] == 4:
    img_array = img_array[:, :, :3]

r = img_array[:, :, 0]
g = img_array[:, :, 1]
b = img_array[:, :, 2]

# Expected objective locations based on description
# Objectives at 24" from long edge = 24" from bottom = y=24" 
# Objectives at 48" from long edge = 48" from bottom = y=48" (but battlefield is 44" tall, so this is wrong)
# Actually, "from long edge" likely means distance from one of the 60" edges
# Let's assume objectives are at y=12" and y=32" (symmetric around 22" center)
# And at x=12" from center = x=18" and x=42" (30" +/- 12")

expected_positions = [
    (18, 12, "Gnarlroot 1"),
    (42, 12, "Oakenbrow 1"),
    (18, 32, "Gnarlroot 2"),
    (42, 32, "Oakenbrow 2"),
]

print("Expected objective positions (inches):")
for x, y, name in expected_positions:
    px = int(x * width / 60)
    py = int((44 - y) * height / 44)  # Flip Y
    print(f"  {name}: ({x}\", {y}\") → pixel ({px}, {py})")
print()

# Sample pixels at expected locations
print("Sampling colors at expected objective locations:")
for x, y, name in expected_positions:
    px = int(x * width / 60)
    py = int((44 - y) * height / 44)  # Flip Y
    
    # Sample 10x10 region around expected center
    x1, x2 = max(0, px-5), min(width, px+5)
    y1, y2 = max(0, py-5), min(height, py+5)
    
    region = img_array[y1:y2, x1:x2]
    avg_r = np.mean(region[:,:,0])
    avg_g = np.mean(region[:,:,1])
    avg_b = np.mean(region[:,:,2])
    
    print(f"  {name}: RGB({avg_r:.0f}, {avg_g:.0f}, {avg_b:.0f}) = #{int(avg_r):02x}{int(avg_g):02x}{int(avg_b):02x}")

print()
print("="*70)
print("Looking for circular patterns (objectives are typically circular):")
print("="*70)

# Try to detect edges and circles
from scipy.ndimage import sobel

# Convert to grayscale
gray = np.mean(img_array, axis=2)

# Edge detection
edge_x = sobel(gray, axis=1)
edge_y = sobel(gray, axis=0)
edges = np.hypot(edge_x, edge_y)

# Threshold edges
edge_threshold = np.percentile(edges, 90)  # Top 10% of edges
strong_edges = edges > edge_threshold

print(f"Strong edges detected: {np.sum(strong_edges)} pixels")

# Find circular regions by looking for compact edge clusters
labeled_edges, num_edge_regions = ndimage.label(strong_edges)
print(f"Edge regions: {num_edge_regions}")

# Analyze compactness (circles have high area-to-perimeter ratio)
circular_candidates = []
for i in range(1, min(num_edge_regions + 1, 500)):  # Limit to first 500
    region_mask = (labeled_edges == i)
    area = np.sum(region_mask)
    
    if area < 10 or area > 5000:  # Filter by size
        continue
    
    y_coords, x_coords = np.where(region_mask)
    
    # Calculate bounding box
    x_min, x_max = x_coords.min(), x_coords.max()
    y_min, y_max = y_coords.min(), y_coords.max()
    
    width_px = x_max - x_min
    height_px = y_max - y_min
    
    # Circles have similar width and height
    aspect_ratio = min(width_px, height_px) / max(width_px, height_px + 0.01)
    
    if aspect_ratio > 0.7:  # Relatively square/circular
        center_x = (x_min + x_max) / 2
        center_y = (y_min + y_max) / 2
        
        circular_candidates.append({
            'center': (center_x, center_y),
            'size': area,
            'aspect': aspect_ratio,
            'dims': (width_px, height_px)
        })

print(f"Circular candidates (aspect ratio > 0.7): {len(circular_candidates)}")

# Sort by size and show top candidates
circular_candidates.sort(key=lambda x: x['size'], reverse=True)
print("\nTop 20 circular candidates:")
for i, cand in enumerate(circular_candidates[:20]):
    cx, cy = cand['center']
    # Convert to battlefield coordinates
    bf_x = (cx / width) * 60
    bf_y = ((height - cy) / height) * 44
    print(f"  {i+1}. Center: ({bf_x:.1f}\", {bf_y:.1f}\"), Size: {cand['size']} px, Aspect: {cand['aspect']:.2f}")

# Create visualization
print(f"\nCreating visualization...")
vis_img = img.copy()
draw = ImageDraw.Draw(vis_img)

# Mark expected positions
for x, y, name in expected_positions:
    px = int(x * width / 60)
    py = int((44 - y) * height / 44)
    draw.ellipse([px-10, py-10, px+10, py+10], outline='blue', width=3)
    draw.text((px+15, py), name, fill='blue')

# Mark detected circular candidates (top 10)
for i, cand in enumerate(circular_candidates[:10]):
    cx, cy = cand['center']
    size = min(cand['size'] / 5, 30)
    draw.ellipse([cx-size, cy-size, cx+size, cy+size], outline='red', width=2)

output_path = "assets/battle-plans-matplotlib/passing-seasons-deep-analysis.png"
vis_img.save(output_path)
print(f"Visualization saved to: {output_path}")
print("Blue circles = expected positions")
print("Red circles = detected circular patterns")
