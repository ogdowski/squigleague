"""Look for ALL large circular shapes regardless of color"""
import cv2
import numpy as np

# Load image
img = cv2.imread('assets/battle-plans/aos-passing-seasons.png')
battlefield = img[:int(img.shape[0] * 0.7), :]
gray = cv2.cvtColor(battlefield, cv2.COLOR_BGR2GRAY)

# Use Hough circles to find ALL circles
circles = cv2.HoughCircles(
    gray,
    cv2.HOUGH_GRADIENT,
    dp=1,
    minDist=50,  # Minimum distance between circles
    param1=50,   # Canny edge threshold
    param2=30,   # Accumulator threshold (lower = more circles)
    minRadius=30,  # Minimum radius
    maxRadius=80   # Maximum radius
)

DPI = 14

if circles is not None:
    circles = np.uint16(np.around(circles))
    print(f"Found {len(circles[0])} circles:")
    
    vis = battlefield.copy()
    for i, (x, y, r) in enumerate(circles[0]):
        x_inch = x / DPI
        y_inch = y / DPI
        print(f"  Circle {i+1}: ({x_inch:.1f}\", {y_inch:.1f}\"), radius={r}px")
        
        # Draw circle
        cv2.circle(vis, (x, y), r, (0, 255, 0), 2)
        cv2.circle(vis, (x, y), 2, (0, 0, 255), 3)
        cv2.putText(vis, f'{i+1}', (x-10, y-r-15), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
    
    cv2.imwrite('assets/battle-plans-matplotlib/all_circles_hough.png', vis)
    print("\nSaved visualization")
else:
    print("No circles found")
