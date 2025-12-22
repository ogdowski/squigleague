"""Inspect the templates to see what was extracted"""
import cv2
import numpy as np

# Load image
img = cv2.imread('assets/battle-plans/aos-passing-seasons.png')
print(f'Image size: {img.shape}')

# Extract legend
legend = img[-150:, :]
print(f'Legend size: {legend.shape}')

# Check where templates were extracted
for i, x_pct in enumerate([0.15, 0.35, 0.55, 0.75]):
    x = int(x_pct * legend.shape[1])
    y = legend.shape[0] // 2
    print(f'Token {i+1} extracted from: x={x}, y={y} (size 80x80)')
    
# Now try lower threshold
print("\n--- Searching with lower threshold ---")
battlefield = img[:int(img.shape[0] * 0.7), :]

for i in range(1, 5):
    template = cv2.imread(f'assets/battle-plans-matplotlib/debug_template_{i}.png')
    if template is None:
        continue
    
    result = cv2.matchTemplate(battlefield, template, cv2.TM_CCOEFF_NORMED)
    max_val = result.max()
    max_loc = result.argmax()
    max_y, max_x = np.unravel_index(max_loc, result.shape)
    
    print(f'\nToken {i}: max correlation = {max_val:.3f} at pixel ({max_x}, {max_y})')
    
    # Try threshold 0.3 instead of 0.5
    matches = np.where(result >= 0.3)
    print(f'  Matches at threshold 0.3: {len(matches[0])}')
    if len(matches[0]) > 0:
        # Show top 5 matches
        vals = result[matches]
        top_idx = np.argsort(vals)[-5:]
        for idx in top_idx:
            y, x = matches[0][idx], matches[1][idx]
            conf = result[y, x]
            print(f'    ({x}, {y}) confidence={conf:.3f}')
