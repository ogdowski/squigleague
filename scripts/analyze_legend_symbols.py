"""
Analyze Wahapedia legend to identify objective marker symbols, then search for them.
Uses template matching and OCR to understand legend labels.
"""
from PIL import Image, ImageDraw
import numpy as np
from pathlib import Path
from scipy import ndimage

image_path = Path("assets/battle-plans/aos-passing-seasons.png")
img = Image.open(image_path)
img_array = np.array(img)

height, width = img_array.shape[:2]

# Convert to RGB
if len(img_array.shape) == 2:
    img_array = np.stack([img_array] * 3, axis=-1)
elif img_array.shape[2] == 4:
    img_array = img_array[:, :, :3]

print(f"Analyzing: {image_path.name}")
print(f"Expected: 4 objectives (Passing Seasons)")
print()

# Legend is typically in bottom region
legend_start_y = int(height * 0.75)  # Start at 75% down
legend_region = img_array[legend_start_y:, :]

print(f"Legend region: rows {legend_start_y}-{height}")
print()

# Analyze the legend region for small circular icons
# These are typically the objective marker samples

# Look for circular patterns in legend
from scipy.ndimage import sobel

gray_legend = np.mean(legend_region, axis=2)
edge_x = sobel(gray_legend, axis=1)
edge_y = sobel(gray_legend, axis=0)
edges_legend = np.hypot(edge_x, edge_y)

threshold = np.percentile(edges_legend, 85)
strong_edges_legend = edges_legend > threshold

labeled_legend, num_legend_features = ndimage.label(strong_edges_legend)

print(f"\nLegend contains {num_legend_features} distinct shapes")

# Find circular shapes in legend (these are likely objective marker examples)
legend_circles = []
for i in range(1, min(num_legend_features + 1, 200)):
    region_mask = (labeled_legend == i)
    area = np.sum(region_mask)
    
    if 20 < area < 500:  # Small to medium shapes
        y_coords, x_coords = np.where(region_mask)
        x_min, x_max = x_coords.min(), x_coords.max()
        y_min, y_max = y_coords.min(), y_coords.max()
        
        w = x_max - x_min
        h = y_max - y_min
        
        # Check circularity
        aspect = min(w, h) / max(w, h, 0.01)
        
        if aspect > 0.6:  # Relatively circular
            center_x = (x_min + x_max) / 2
            center_y = (y_min + y_max) / 2
            
            # Sample the color at this location
            cy_abs = legend_start_y + int(center_y)
            cx_abs = int(center_x)
            
            if cy_abs < height and cx_abs < width:
                sample_color = img_array[cy_abs, cx_abs]
                
                legend_circles.append({
                    'center': (center_x, center_y),
                    'size': area,
                    'aspect': aspect,
                    'color': sample_color,
                    'bbox': (x_min, y_min, x_max, y_max)
                })

legend_circles.sort(key=lambda x: x['size'], reverse=True)

print(f"Found {len(legend_circles)} circular shapes in legend")
print("\nTop legend circles (likely objective markers):")
for i, circle in enumerate(legend_circles[:5]):
    r, g, b = circle['color']
    print(f"  {i+1}. Size: {circle['size']:3d}px, Color: RGB({r},{g},{b}) #{r:02x}{g:02x}{b:02x}")

# Now use the top legend circle colors to search the main battlefield
if legend_circles:
    print("\n" + "="*70)
    print("Searching battlefield for objective markers matching legend")
    print("="*70)
    
    # Use top 2-3 legend circles as templates
    for template_idx, template in enumerate(legend_circles[:3]):
        template_color = template['color']
        r_t, g_t, b_t = template_color
        
        print(f"\nSearching for color pattern {template_idx+1}: RGB({r_t},{g_t},{b_t})")
        
        # Search for similar colors in battlefield area (top 75%)
        battlefield = img_array[:legend_start_y, :]
        
        r = battlefield[:, :, 0]
        g = battlefield[:, :, 1]
        b = battlefield[:, :, 2]
        
        # Color tolerance
        tolerance = 40
        color_match = (
            (np.abs(r.astype(int) - r_t) < tolerance) &
            (np.abs(g.astype(int) - g_t) < tolerance) &
            (np.abs(b.astype(int) - b_t) < tolerance)
        )
        
        match_count = np.sum(color_match)
        print(f"  Matching pixels: {match_count}")
        
        if match_count > 0:
            # Find connected regions
            labeled, num_features = ndimage.label(color_match)
            
            objectives = []
            for i in range(1, num_features + 1):
                region_mask = (labeled == i)
                region_size = np.sum(region_mask)
                
                # Filter by size similar to legend marker
                min_size = template['size'] * 0.5
                max_size = template['size'] * 5
                
                if min_size < region_size < max_size:
                    y_coords, x_coords = np.where(region_mask)
                    center_x = np.mean(x_coords)
                    center_y = np.mean(y_coords)
                    
                    # Check circularity
                    x_min, x_max = x_coords.min(), x_coords.max()
                    y_min, y_max = y_coords.min(), y_coords.max()
                    w = x_max - x_min
                    h = y_max - y_min
                    aspect = min(w, h) / max(w, h, 0.01)
                    
                    if aspect > 0.5:  # Somewhat circular
                        bf_x = (center_x / width) * 60
                        bf_y = ((legend_start_y - center_y) / legend_start_y) * 44
                        
                        objectives.append({
                            'position': (bf_x, bf_y),
                            'size': region_size
                        })
            
            if objectives:
                objectives.sort(key=lambda x: x['size'], reverse=True)
                print(f"  Found {len(objectives)} potential objectives:")
                for i, obj in enumerate(objectives[:10]):
                    x, y = obj['position']
                    print(f"    {i+1}. ({x:4.1f}\", {y:4.1f}\") - {obj['size']}px")

# Create visualization
vis_img = img.copy()
draw = ImageDraw.Draw(vis_img)

# Mark legend region
draw.rectangle([0, legend_start_y, width, height], outline='yellow', width=3)

output_path = "assets/battle-plans-matplotlib/legend-and-battlefield.png"
vis_img.save(output_path)
print(f"\nVisualization saved to: {output_path}")
