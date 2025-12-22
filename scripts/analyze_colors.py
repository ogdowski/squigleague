"""
Analyze color distribution in Wahapedia image to understand what objective markers actually look like.
"""
from PIL import Image
import numpy as np
from pathlib import Path
from collections import Counter

image_path = Path("assets/battle-plans/aos-passing-seasons.png")
img = Image.open(image_path)
img_array = np.array(img)

print(f"Image: {image_path.name}")
print(f"Size: {img_array.shape}")

# Convert to RGB if needed
if len(img_array.shape) == 2:
    img_array = np.stack([img_array] * 3, axis=-1)
elif img_array.shape[2] == 4:  # RGBA
    img_array = img_array[:, :, :3]

# Sample some unique colors
height, width = img_array.shape[:2]

# Create color histogram (group similar colors)
colors = img_array.reshape(-1, 3)

# Quantize to reduce color space (group similar colors)
quantized = (colors // 16) * 16  # Group into 16-step bins

# Count unique colors
unique, counts = np.unique(quantized, axis=0, return_counts=True)

# Sort by frequency
sorted_indices = np.argsort(counts)[::-1]

print("\nTop 30 colors by frequency:")
print("Rank | Count    | R   G   B   | Hex     | Description")
print("-----|----------|-------------|---------|--------------------")
for i, idx in enumerate(sorted_indices[:30]):
    color = unique[idx]
    count = counts[idx]
    hex_color = '#{:02x}{:02x}{:02x}'.format(color[0], color[1], color[2])
    
    # Describe color
    r, g, b = color
    if r > 200 and g > 200 and b > 200:
        desc = "White/Light gray"
    elif r < 50 and g < 50 and b < 50:
        desc = "Black/Dark"
    elif r > g + 50 and r > b + 50:
        desc = "Red/Orange"
    elif g > r + 50 and g > b + 50:
        desc = "Green"
    elif b > r + 50 and b > g + 50:
        desc = "Blue"
    elif r > 150 and g > 150 and b < 100:
        desc = "Yellow/Gold"
    elif r > 100 and g > 50 and b < 50:
        desc = "Brown/Red-brown"
    else:
        desc = "Mixed/Gray"
    
    print(f"{i+1:4d} | {count:8d} | {r:3d} {g:3d} {b:3d} | {hex_color} | {desc}")

# Look for specific color ranges that might be objectives
print("\n" + "="*70)
print("Analyzing potential objective marker colors:")
print("="*70)

# Try different color patterns
patterns = [
    ("Bright Yellow", lambda r,g,b: r > 200 and g > 150 and b < 100),
    ("Orange", lambda r,g,b: r > 180 and 100 < g < 180 and b < 100),
    ("Gold/Brown-Yellow", lambda r,g,b: 150 < r < 220 and 120 < g < 180 and 50 < b < 120),
    ("Red", lambda r,g,b: r > 150 and g < 100 and b < 100),
    ("Bright Green", lambda r,g,b: g > 150 and r < 120 and b < 120),
    ("Dark Green", lambda r,g,b: 50 < g < 150 and r < 100 and b < 100),
    ("Blue", lambda r,g,b: b > 150 and r < 120 and g < 120),
    ("Purple/Magenta", lambda r,g,b: r > 150 and b > 150 and g < 120),
]

for name, pattern_func in patterns:
    r = img_array[:, :, 0]
    g = img_array[:, :, 1]
    b = img_array[:, :, 2]
    
    # Vectorize the pattern check
    mask = np.vectorize(pattern_func)(r, g, b)
    count = np.sum(mask)
    
    if count > 0:
        print(f"{name:20s}: {count:7d} pixels")

print("\nThis will help identify what color the objective markers actually are.")
