"""Update battle-plans-demo.html to show all 3 image sets"""
import re

missions = [
    ("Passing Seasons", "passing-seasons"),
    ("Paths of the Fey", "paths-of-the-fey"),
    ("Roiling Roots", "roiling-roots"),
    ("Cyclic Shifts", "cyclic-shifts"),
    ("Surge of Slaughter", "surge-of-slaughter"),
    ("Linked Ley Lines", "linked-ley-lines"),
    ("Noxious Nexus", "noxious-nexus"),
    ("The Liferoots", "the-liferoots"),
    ("Bountiful Equinox", "bountiful-equinox"),
    ("Lifecycle", "lifecycle"),
    ("Creeping Corruption", "creeping-corruption"),
    ("Grasp of Thorns", "grasp-of-thorns"),
]

template = '''            <div class="battleplan-card">
                <div class="battleplan-header">
                    <div class="mission-number">Mission {num} of 12</div>
                    <h2>{title}</h2>
                </div>
                <div class="comparison">
                    <div class="image-section">
                        <h3><span class="label label-reference">WAHAPEDIA</span></h3>
                        <div class="image-container">
                            <img src="assets/battle-plans/aos-{slug}.png" alt="{title} Wahapedia">
                            <div class="image-info">Original Source</div>
                        </div>
                    </div>
                    <div class="image-section">
                        <h3><span class="label label-aoi">AGE OF INDEX</span></h3>
                        <div class="image-container">
                            <img src="assets/battle-plans-ageofindex/aos-{slug}.png" alt="{title} AOI">
                            <div class="image-info">ageofindex.com</div>
                        </div>
                    </div>
                    <div class="image-section">
                        <h3><span class="label label-generated">MATPLOTLIB</span></h3>
                        <div class="image-container">
                            <img src="assets/battle-plans-matplotlib/aos-{slug}-matplotlib.png" alt="{title} Generated">
                            <div class="image-info">Generated Diagram</div>
                        </div>
                    </div>
                </div>
            </div>
'''

# Generate all mission cards
cards = []
for i, (title, slug) in enumerate(missions, 1):
    card = template.format(num=i, title=title, slug=slug)
    cards.append(card)

all_cards = "\n".join(cards)

# Read current HTML
with open("battle-plans-demo.html", "r", encoding="utf-8") as f:
    html = f.read()

# Replace the battleplan-grid content
pattern = r'(<div class="battleplan-grid">).*?(</div>\s*</div>\s*<script>)'
replacement = r'\1\n' + all_cards + r'\n        \2'
html = re.sub(pattern, replacement, html, flags=re.DOTALL)

# Write updated HTML
with open("battle-plans-demo.html", "w", encoding="utf-8") as f:
    f.write(html)

# VALIDATE before claiming success
import subprocess
result = subprocess.run(
    ["python", "scripts/validate_html.py", "battle-plans-demo.html"],
    capture_output=True,
    text=True
)

if result.returncode != 0:
    print("❌ HTML VALIDATION FAILED!")
    print(result.stdout)
    print(result.stderr)
    # Restore from git
    subprocess.run(["git", "checkout", "battle-plans-demo.html"])
    print("❌ Changes reverted - fix the script")
    exit(1)

print("✓ Updated battle-plans-demo.html with all 3 image sets")
print(f"✓ Generated {len(missions)} mission cards")
print(result.stdout)
