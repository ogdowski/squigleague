"""
Read the legend from Wahapedia images to understand what each symbol means.
The legend TELLS US what objectives, deployment zones, and terrain look like.
"""
from PIL import Image
import numpy as np
from pathlib import Path

# Just look at one image first to understand the structure
image_path = Path("assets/battle-plans/aos-passing-seasons.png")
img = Image.open(image_path)

print(f"Image: {image_path.name}")
print(f"Size: {img.size}")
print()

# The legend is typically in the bottom portion
# Let's look at different regions to find where the legend actually is
img_array = np.array(img)
height, width = img_array.shape[:2]

print("Image structure analysis:")
print(f"Total height: {height} pixels")
print()

# Sample different vertical regions to understand layout
regions = {
    "Top (0-25%)": (0, int(height * 0.25)),
    "Upper Mid (25-50%)": (int(height * 0.25), int(height * 0.50)),
    "Lower Mid (50-75%)": (int(height * 0.50), int(height * 0.75)),
    "Bottom (75-100%)": (int(height * 0.75), height),
}

for region_name, (y_start, y_end) in regions.items():
    region = img_array[y_start:y_end, :]
    
    # Check if this region has text (look for white/light pixels which indicate text)
    if len(region.shape) == 3:
        gray = np.mean(region, axis=2)
    else:
        gray = region
    
    # Count bright pixels (likely text on dark background or vice versa)
    bright_pixels = np.sum(gray > 200)
    dark_pixels = np.sum(gray < 50)
    total_pixels = region.shape[0] * region.shape[1]
    
    print(f"{region_name:20s} | Height: {y_end - y_start:4d}px | Bright: {bright_pixels/total_pixels*100:5.2f}% | Dark: {dark_pixels/total_pixels*100:5.2f}%")

print()
print("="*70)
print("Looking at the actual Wahapedia page structure...")
print()

# Wahapedia images typically have:
# - Title at top
# - Main battlefield diagram in middle
# - Legend/key at bottom
# The legend shows icons with text labels

# Extract the bottom region more carefully
legend_region_start = int(height * 0.70)  # Start at 70% down
legend_img = img.crop((0, legend_region_start, width, height))

# Save for inspection
output_path = "assets/battle-plans-matplotlib/legend_analysis.png"
legend_img.save(output_path)

print(f"Legend region saved to: {output_path}")
print(f"Legend region: rows {legend_region_start} to {height}")
print()
print("The legend should show:")
print("  - Objective marker icon + label")
print("  - Deployment zone colors")
print("  - Terrain types")
print()
print("Looking at the pixel data in the legend region...")

# Sample some specific areas in the legend to understand the layout
legend_array = np.array(legend_img)
legend_height = legend_array.shape[0]

# The legend typically has items arranged horizontally
# Let's look at the vertical middle of the legend region
mid_y = legend_height // 2

# Sample across the width to find distinct symbols
print(f"\nSampling legend at y={mid_y} (middle row):")
sample_points = [int(width * pct / 100) for pct in [10, 30, 50, 70, 90]]

for x in sample_points:
    if x < legend_array.shape[1]:
        pixel = legend_array[mid_y, x]
        if len(pixel) >= 3:
            r, g, b = pixel[0], pixel[1], pixel[2]
            print(f"  x={x:4d} ({x/width*100:3.0f}%): RGB({r:3d}, {g:3d}, {b:3d}) #{r:02x}{g:02x}{b:02x}")

print()
print("Next: Manually inspect legend_analysis.png to see what the legend actually shows")
print("Then we can identify the objective marker symbol and search for it in the battlefield")
