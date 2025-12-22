"""Visualize where matches were found"""
import cv2
import numpy as np

# Load image
img = cv2.imread('assets/battle-plans/aos-passing-seasons.png')
battlefield = img[:int(img.shape[0] * 0.7), :].copy()
DPI = 14
pixels_per_inch = DPI

# Draw where the 3 found objectives are
found_objectives = [
    (55.0, 35.4),  # Token 1
    (51.5, 19.2),  # Token 2
    (45.0, 39.5),  # Token 4
]

for x_inch, y_inch in found_objectives:
    x_px = int(x_inch * pixels_per_inch)
    y_px = int(y_inch * pixels_per_inch)
    cv2.circle(battlefield, (x_px, y_px), 60, (0, 255, 0), 3)  # Green
    cv2.putText(battlefield, f'({x_inch:.1f}", {y_inch:.1f}")', 
                (x_px - 50, y_px - 70), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

# Draw where token 3's best match was (even though correlation was low)
x_px, y_px = 720, 219
x_inch = x_px / pixels_per_inch
y_inch = y_px / pixels_per_inch
cv2.circle(battlefield, (x_px, y_px), 60, (0, 0, 255), 3)  # Red - suspicious
cv2.putText(battlefield, f'Token 3? ({x_inch:.1f}", {y_inch:.1f}")\ncorr=0.334', 
            (x_px - 50, y_px - 70), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

cv2.imwrite('assets/battle-plans-matplotlib/matches_visualization.png', battlefield)
print("Saved visualization to matches_visualization.png")
print("\nFound positions:")
for i, (x, y) in enumerate(found_objectives, 1):
    print(f"  Objective {i}: ({x:.1f}\", {y:.1f}\")")
print(f"\nToken 3 best match (low confidence): ({x_inch:.1f}\", {y_inch:.1f}\")")

# Now let's manually check the legend to see if there ARE 4 different token types
legend = img[-150:, :]
cv2.imwrite('assets/battle-plans-matplotlib/full_legend.png', legend)
print("\nSaved full legend for inspection")
