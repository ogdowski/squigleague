"""Extract battle plans from ageofindex.com - handle SVG/Canvas/generated content"""
from playwright.sync_api import sync_playwright
import time
import hashlib
from pathlib import Path

MISSIONS = [
    "Passing Seasons",
    "Paths of the Fey", 
    "Roiling Roots",
    "Cyclic Shifts",
    "Surge of Slaughter",
    "Linked Ley Lines",
    "Noxious Nexus",
    "The Liferoots",
    "Bountiful Equinox",
    "Lifecycle",
    "Creeping Corruption",
    "Grasp of Thorns"
]

def extract_plans():
    import hashlib
    output_dir = Path("assets/battle-plans-ageofindex")
    output_dir.mkdir(exist_ok=True, parents=True)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        
        print("Loading ageofindex.com/plans...")
        page.goto("https://www.ageofindex.com/plans", wait_until="networkidle")
        time.sleep(3)
        
        # Inspect page structure to find plan selector
        print("\nClicking dropdown to reveal all options...")
        
        # Click the MUI Select to open dropdown
        select = page.locator("#plan-select")
        select.click()
        time.sleep(1)
        
        # Get all options from the dropdown menu
        options = page.locator("[role='option']").all()
        print(f"Found {len(options)} plan options:")
        
        image_map = {}
        for opt in options:
            text = opt.text_content()
            # Get the associated image URL - check data attributes or hidden input
            print(f"  - {text}")
            
            # Click option to select it
            opt.click()
            time.sleep(0.5)
            
            # Read the hidden input value which contains image path
            hidden_input = page.locator(".MuiSelect-nativeInput").first
            img_path = hidden_input.get_attribute("value")
            print(f"      Image: {img_path}")
            
            slug = text.lower().replace(' ', '-')
            # Extract just the filename
            filename = img_path.split('/')[-1] if '/' in img_path else img_path
            image_map[slug] = filename
            
            # Reopen dropdown for next iteration
            if opt != options[-1]:
                select.click()
                time.sleep(0.3)
        
        print("\nImage mapping:")
        for slug, filename in image_map.items():
            print(f"  '{slug}': '{filename}',")
        
        browser.close()
        return  # Exit - use this mapping to download directly
        
        for i, mission in enumerate(MISSIONS):
            print(f"\nProcessing {i+1}/12: {mission}")
            
            try:
                if i == 0:
                    # First mission - already loaded, just capture
                    time.sleep(2)
                else:
                    # Get current canvas hash before navigation
                    canvas = page.locator("canvas").first
                    if canvas.count() > 0:
                        before_screenshot = canvas.screenshot()
                        before_hash = hashlib.md5(before_screenshot).hexdigest()
                    
                    # Navigate to next plan
                    page.keyboard.press("ArrowDown")
                    
                    # Wait for canvas to update (poll until hash changes)
                    max_attempts = 10
                    for attempt in range(max_attempts):
                        time.sleep(0.3)
                        canvas = page.locator("canvas").first
                        if canvas.count() > 0:
                            after_screenshot = canvas.screenshot()
                            after_hash = hashlib.md5(after_screenshot).hexdigest()
                            if after_hash != before_hash:
                                print(f"  Canvas updated (attempt {attempt+1})")
                                break
                    else:
                        print(f"  WARNING: Canvas did not change after navigation")
                
                # Capture canvas
                canvas = page.locator("canvas").first
                if canvas.count() > 0:
                    png_file = output_dir / f"aos-{mission.lower().replace(' ', '-')}.png"
                    canvas.screenshot(path=str(png_file))
                    size_kb = png_file.stat().st_size / 1024
                    print(f"  Saved: {png_file.name} ({size_kb:.1f}KB)")
                else:
                    print(f"  WARNING: No canvas found")
                
            except Exception as e:
                print(f"  ERROR: {e}")
                continue
        
        print("\n\nDone. Check assets/battle-plans-ageofindex/")
        
        # Verify uniqueness
        from collections import defaultdict
        hashes = defaultdict(list)
        for png in output_dir.glob("aos-*.png"):
            import hashlib
            hash_val = hashlib.md5(png.read_bytes()).hexdigest()
            hashes[hash_val].append(png.name)
        
        print(f"\nUnique images: {len(hashes)}/12")
        if len(hashes) < 12:
            print("WARNING: Some images are duplicates!")
            for hash_val, files in hashes.items():
                if len(files) > 1:
                    print(f"  Duplicates: {', '.join(files)}")
        
        browser.close()

if __name__ == "__main__":
    extract_plans()
