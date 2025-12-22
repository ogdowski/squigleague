"""Show what we extracted as templates from the legend"""
import cv2

# Load the original image
img = cv2.imread('assets/battle-plans/aos-passing-seasons.png')

# Get the legend (bottom 200px)
legend = img[-200:, :]

# Save it large
cv2.imwrite('assets/battle-plans-matplotlib/LEGEND_REGION.png', legend)

# Show where we extracted templates from
import matplotlib.pyplot as plt

fig, axes = plt.subplots(2, 2, figsize=(12, 8))
fig.suptitle('Extracted Templates from Legend')

for i in range(1, 5):
    template = cv2.imread(f'assets/battle-plans-matplotlib/debug_template_{i}.png')
    if template is not None:
        template_rgb = cv2.cvtColor(template, cv2.COLOR_BGR2RGB)
        ax = axes[(i-1)//2, (i-1)%2]
        ax.imshow(template_rgb)
        ax.set_title(f'Template {i} (80x80 px)')
        ax.axis('off')

plt.tight_layout()
plt.savefig('assets/battle-plans-matplotlib/TEMPLATES_EXTRACTED.png', dpi=150)
print("Saved TEMPLATES_EXTRACTED.png")

# Also show legend with boxes around where we extracted
legend_vis = legend.copy()
for i, x_pct in enumerate([0.15, 0.35, 0.55, 0.75]):
    x = int(x_pct * legend.shape[1])
    y = legend.shape[0] - 150 + 75  # Middle of bottom 150px region
    
    # Draw box
    cv2.rectangle(legend_vis, (x-40, y-40), (x+40, y+40), (0, 255, 0), 2)
    cv2.putText(legend_vis, f'T{i+1}', (x-15, y-50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

cv2.imwrite('assets/battle-plans-matplotlib/LEGEND_WITH_EXTRACTION_BOXES.png', legend_vis)
print("Saved LEGEND_WITH_EXTRACTION_BOXES.png")
