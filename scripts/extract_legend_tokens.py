"""Extract objective tokens manually from the legend by finding circular tokens"""
import cv2
import numpy as np

# Load the image
img = cv2.imread('assets/battle-plans/aos-passing-seasons.png')

# The legend is at the bottom - let's look at bottom 200px
legend = img[-200:, :]

# Find all circles in the legend to identify objective token examples
gray = cv2.cvtColor(legend, cv2.COLOR_BGR2GRAY)

circles = cv2.HoughCircles(
    gray,
    cv2.HOUGH_GRADIENT,
    dp=1,
    minDist=80,  # Tokens should be spaced in legend
    param1=50,
    param2=25,
    minRadius=30,
    maxRadius=60
)

print(f"Legend size: {legend.shape}")

if circles is not None:
    circles = np.uint16(np.around(circles))
    print(f"\nFound {len(circles[0])} circular tokens in legend:")
    
    # Extract each as a template
    for i, (x, y, r) in enumerate(circles[0][:4]):  # Only take first 4
        print(f"  Token {i+1}: center=({x}, {y}), radius={r}px")
        
        # Extract with padding
        padding = 10
        y1 = max(0, y - r - padding)
        y2 = min(legend.shape[0], y + r + padding)
        x1 = max(0, x - r - padding)
        x2 = min(legend.shape[1], x + r + padding)
        
        token = legend[y1:y2, x1:x2]
        
        cv2.imwrite(f'assets/battle-plans-matplotlib/objective_token_{i+1}.png', token)
        print(f"    Saved objective_token_{i+1}.png ({token.shape})")
    
    # Visualize
    legend_vis = legend.copy()
    for i, (x, y, r) in enumerate(circles[0][:4]):
        cv2.circle(legend_vis, (x, y), r, (0, 255, 0), 2)
        cv2.putText(legend_vis, f'{i+1}', (x-10, y-r-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    
    cv2.imwrite('assets/battle-plans-matplotlib/legend_tokens_found.png', legend_vis)
    print("\nSaved legend_tokens_found.png")
else:
    print("No circles found in legend")
