"""Analyze the legend to extract ACTUAL objective token templates"""
import cv2
import numpy as np

# Load image
img = cv2.imread('assets/battle-plans/aos-passing-seasons.png')
print(f"Image size: {img.shape}")

# The legend is at the bottom
legend = img[-150:, :]
print(f"Legend size: {legend.shape}")

# Save full legend for inspection
cv2.imwrite('assets/battle-plans-matplotlib/legend_full.png', legend)

# The legend shows "OBJECTIVES LOCATIONS" and "TERRAIN LOCATIONS"
# Based on user screenshots, objective tokens are smaller gold-bordered circles
# Let me look at the entire bottom region more carefully

# Try bottom 200px instead of 150px
legend_expanded = img[-200:, :]
cv2.imwrite('assets/battle-plans-matplotlib/legend_expanded.png', legend_expanded)

# Let's also check if there are small circles in the top-left corner (common in Wahapedia layouts)
top_left = img[:150, :300]
cv2.imwrite('assets/battle-plans-matplotlib/top_left_corner.png', top_left)

print("\nSaved legend_full.png, legend_expanded.png, and top_left_corner.png for manual inspection")
print("\nLet me search for ALL small circles on the battlefield (20-50px radius):")

battlefield = img[:int(img.shape[0] * 0.7), :]
gray = cv2.cvtColor(battlefield, cv2.COLOR_BGR2GRAY)

circles = cv2.HoughCircles(
    gray,
    cv2.HOUGH_GRADIENT,
    dp=1,
    minDist=80,  # Objectives should be spaced apart
    param1=50,
    param2=25,
    minRadius=20,
    maxRadius=50
)

DPI = 14

if circles is not None:
    circles = np.uint16(np.around(circles))
    print(f"\nFound {len(circles[0])} small circles:")
    
    vis = battlefield.copy()
    for i, (x, y, r) in enumerate(circles[0]):
        x_inch = x / DPI
        y_inch = y / DPI
        print(f"  Circle {i+1}: ({x_inch:.1f}\", {y_inch:.1f}\"), radius={r}px")
        
        cv2.circle(vis, (x, y), r, (0, 255, 0), 2)
        cv2.circle(vis, (x, y), 2, (0, 0, 255), 3)
        cv2.putText(vis, f'{i+1}', (x-10, y-r-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
    
    cv2.imwrite('assets/battle-plans-matplotlib/small_circles.png', vis)
    print("\nSaved visualization")
else:
    print("\nNo small circles found")
