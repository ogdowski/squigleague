"""Find ALL circular tokens by looking for gold borders"""
import cv2
import numpy as np

# Load image
img = cv2.imread('assets/battle-plans/aos-passing-seasons.png')
battlefield = img[:int(img.shape[0] * 0.7), :]

# Convert to HSV
hsv = cv2.cvtColor(battlefield, cv2.COLOR_BGR2HSV)

# Gold/yellow range for borders
lower_gold = np.array([15, 100, 100])
upper_gold = np.array([35, 255, 255])

# Create mask
gold_mask = cv2.inRange(hsv, lower_gold, upper_gold)

# Find contours
contours, _ = cv2.findContours(gold_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

print(f"Found {len(contours)} gold contours")

# Filter for circular shapes
circles = []
DPI = 14

for i, cnt in enumerate(contours):
    area = cv2.contourArea(cnt)
    if area < 100:  # Too small
        continue
        
    perimeter = cv2.arcLength(cnt, True)
    if perimeter == 0:
        continue
        
    circularity = 4 * np.pi * area / (perimeter ** 2)
    
    # Get bounding circle
    (x, y), radius = cv2.minEnclosingCircle(cnt)
    
    # Check if it's roughly circular and reasonable size
    # Objective tokens are SMALLER than terrain circles (which are ~65px radius)
    if circularity > 0.3 and 15 < radius < 50:
        x_inch = int(x) / DPI
        y_inch = int(y) / DPI
        circles.append((int(x), int(y), int(radius), circularity, area))
        print(f"  Circle {i}: center=({x_inch:.1f}\", {y_inch:.1f}\"), radius={radius:.1f}px, circularity={circularity:.2f}, area={area:.0f}")

print(f"\nFound {len(circles)} potential objective tokens")

# Draw them on visualization
vis = battlefield.copy()
for i, (x, y, r, circ, area) in enumerate(circles):
    cv2.circle(vis, (x, y), r, (0, 255, 0), 2)
    cv2.putText(vis, f'{i+1}', (x-10, y-r-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

cv2.imwrite('assets/battle-plans-matplotlib/gold_circles_found.png', vis)
cv2.imwrite('assets/battle-plans-matplotlib/gold_mask.png', gold_mask)
print("Saved visualizations")
