"""
Quick analysis tool to visually inspect a single Wahapedia image and manually extract positions.
This will help us understand what the objective markers actually look like.
"""
from PIL import Image, ImageDraw
import numpy as np
from pathlib import Path

# Target image
image_path = Path("assets/battle-plans/aos-passing-seasons.png")

img = Image.open(image_path)
img_array = np.array(img)

print(f"Image: {image_path.name}")
print(f"Size: {img_array.shape}")
print(f"Expected objectives: 4 (Passing Seasons)")

# Convert to RGB if needed
if len(img_array.shape) == 2:
    img_array = np.stack([img_array] * 3, axis=-1)
elif img_array.shape[2] == 4:  # RGBA
    img_array = img_array[:, :, :3]

# Look for bright yellow/orange pixels (objective markers)
# Yellow is high R, high G, low B
# Orange is high R, medium G, low B

r = img_array[:, :, 0]
g = img_array[:, :, 1]
b = img_array[:, :, 2]

# Find pixels that are yellowish (high R and G, low B)
yellow_mask = (r > 200) & (g > 150) & (b < 100)

# Count yellow regions
print(f"\nYellow pixels found: {np.sum(yellow_mask)}")

# Find contiguous regions
from scipy import ndimage

labeled, num_features = ndimage.label(yellow_mask)
print(f"Connected regions: {num_features}")

# Get region properties
regions = []
for i in range(1, num_features + 1):
    region_mask = (labeled == i)
    region_size = np.sum(region_mask)
    
    # Only consider regions with substantial size (filter noise)
    if region_size > 50:  # At least 50 pixels
        y_coords, x_coords = np.where(region_mask)
        center_x = np.mean(x_coords)
        center_y = np.mean(y_coords)
        
        regions.append({
            'size': region_size,
            'center': (center_x, center_y),
            'bbox': (x_coords.min(), y_coords.min(), x_coords.max(), y_coords.max())
        })

print(f"\nSubstantial regions (>50 pixels): {len(regions)}")

# Sort by size
regions.sort(key=lambda x: x['size'], reverse=True)

# Print top regions
print("\nLargest regions:")
for i, region in enumerate(regions[:10]):
    print(f"  {i+1}. Size: {region['size']} px, Center: {region['center']}")

# Visualize the detection
vis_img = img.copy()
draw = ImageDraw.Draw(vis_img)

for region in regions[:20]:  # Draw top 20
    x, y = region['center']
    size = min(region['size'] / 10, 50)  # Scale marker size
    draw.ellipse([x-size, y-size, x+size, y+size], outline='red', width=3)

output_path = "assets/battle-plans-matplotlib/passing-seasons-analysis.png"
vis_img.save(output_path)
print(f"\nVisualization saved to: {output_path}")
print("Open this file to see detected objective markers.")
