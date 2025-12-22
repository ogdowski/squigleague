"""
Extract and analyze the legend from Wahapedia battle plan images.
The legend shows what objectives, deployment zones, and terrain look like.
"""
from PIL import Image
import numpy as np
from pathlib import Path

image_path = Path("assets/battle-plans/aos-passing-seasons.png")
img = Image.open(image_path)
img_array = np.array(img)

height, width = img_array.shape[:2]
print(f"Image: {image_path.name}")
print(f"Dimensions: {width}x{height}")
print()

# Legends are typically at the bottom of the image
# Let's look at the bottom 20% of the image
legend_height = int(height * 0.2)
legend_region = img_array[height - legend_height:, :]

print(f"Analyzing bottom region (legend area): {width}x{legend_height} pixels")
print()

# Convert to RGB if needed
if len(img_array.shape) == 2:
    img_array = np.stack([img_array] * 3, axis=-1)
elif img_array.shape[2] == 4:
    img_array = img_array[:, :, :3]

# Sample legend region to understand structure
# Look for text patterns and color samples
print("Legend region analysis:")
print("="*70)

# Check if legend has distinct color blocks
legend_rgb = legend_region if len(legend_region.shape) == 3 else np.stack([legend_region]*3, axis=-1)
if legend_rgb.shape[2] == 4:
    legend_rgb = legend_rgb[:, :, :3]

# Find unique colors in legend (quantized)
legend_colors = legend_rgb.reshape(-1, 3)
quantized = (legend_colors // 32) * 32  # Group into 32-step bins
unique, counts = np.unique(quantized, axis=0, return_counts=True)
sorted_indices = np.argsort(counts)[::-1]

print("\nTop colors in legend region:")
for i, idx in enumerate(sorted_indices[:15]):
    color = unique[idx]
    count = counts[idx]
    hex_color = '#{:02x}{:02x}{:02x}'.format(color[0], color[1], color[2])
    pct = (count / len(legend_colors)) * 100
    print(f"  {i+1}. {hex_color} - {pct:5.2f}%")

# Extract legend region as separate image for visual inspection
legend_img = Image.fromarray(legend_rgb.astype('uint8'))
output_path = "assets/battle-plans-matplotlib/legend-extracted.png"
legend_img.save(output_path)
print(f"\nLegend region saved to: {output_path}")

# Now analyze the full image to look for patterns matching legend colors
print("\n" + "="*70)
print("Searching full image for legend-matched patterns")
print("="*70)

# Look for specific color patterns that might be objectives
# Based on the legend, objectives are often a specific color/symbol

# Let's try to find small circular markers of consistent colors
from scipy import ndimage

full_rgb = img_array if len(img_array.shape) == 3 else np.stack([img_array]*3, axis=-1)
if full_rgb.shape[2] == 4:
    full_rgb = full_rgb[:, :, :3]

# Try looking for orange/gold markers (common for objectives)
r = full_rgb[:, :, 0]
g = full_rgb[:, :, 1]
b = full_rgb[:, :, 2]

# Orange/gold objectives: high R, medium-high G, low B
objective_mask = (r > 180) & (g > 140) & (g < 200) & (b < 120)
obj_count = np.sum(objective_mask)

if obj_count > 0:
    print(f"\nOrange/gold markers: {obj_count} pixels")
    
    # Find connected regions
    labeled, num_features = ndimage.label(objective_mask)
    print(f"Connected regions: {num_features}")
    
    # Filter by size
    objectives = []
    for i in range(1, num_features + 1):
        region_mask = (labeled == i)
        region_size = np.sum(region_mask)
        
        if 100 < region_size < 1000:  # Reasonable objective marker size
            y_coords, x_coords = np.where(region_mask)
            center_x = np.mean(x_coords)
            center_y = np.mean(y_coords)
            
            bf_x = (center_x / width) * 60
            bf_y = ((height - center_y) / height) * 44
            
            objectives.append({
                'position': (bf_x, bf_y),
                'size': region_size
            })
    
    objectives.sort(key=lambda x: x['size'], reverse=True)
    
    print(f"\nObjective markers (100-1000 px):")
    for i, obj in enumerate(objectives):
        x, y = obj['position']
        print(f"  {i+1}. ({x:4.1f}\", {y:4.1f}\") - {obj['size']} px")

# Try different color ranges
print("\n\nTrying alternative color patterns...")

# Yellow objectives
yellow_mask = (r > 200) & (g > 180) & (b < 120)
yellow_count = np.sum(yellow_mask)
print(f"Yellow markers: {yellow_count} pixels")

# Red objectives
red_mask = (r > 180) & (g < 100) & (b < 100)
red_count = np.sum(red_mask)
print(f"Red markers: {red_count} pixels")

# White/light markers
white_mask = (r > 200) & (g > 200) & (b > 200)
white_count = np.sum(white_mask)
print(f"White markers: {white_count} pixels")

print("\nNext: Visually inspect legend-extracted.png to identify objective marker appearance")
