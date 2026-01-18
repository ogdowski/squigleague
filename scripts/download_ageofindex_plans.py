"""
Download battle plan images from ageofindex.com
Uses Playwright/Selenium to render JavaScript and capture images
"""
import time
from pathlib import Path

# Try to use playwright, fall back to instructions
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("Playwright not installed. Install with: pip install playwright")
    print("Then run: playwright install")

MISSIONS = [
    "passing-seasons",
    "paths-of-the-fey", 
    "roiling-roots",
    "cyclic-shifts",
    "surge-of-slaughter",
    "linked-ley-lines",
    "noxious-nexus",
    "the-liferoots",
    "bountiful-equinox",
    "lifecycle",
    "creeping-corruption",
    "grasp-of-thorns"
]

def download_with_playwright():
    """Download using Playwright browser automation."""
    output_dir = Path("assets/battle-plans-ageofindex")
    output_dir.mkdir(exist_ok=True, parents=True)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        
        for mission in MISSIONS:
            print(f"\nDownloading: {mission}")
            url = f"https://www.ageofindex.com/plans/{mission}"
            page.goto(url, wait_until="networkidle")
            
            # Wait for content to load
            time.sleep(2)
            
            # Take screenshot of the battle plan area
            output_path = output_dir / f"aos-{mission}.png"
            page.screenshot(path=str(output_path), full_page=False)
            print(f"  [OK] Saved: {output_path}")
        
        browser.close()
    
    print(f"\n[SUCCESS] All images downloaded to: {output_dir}")

def manual_instructions():
    """Print manual download instructions."""
    print("\n" + "="*60)
    print("MANUAL DOWNLOAD INSTRUCTIONS")
    print("="*60)
    print("\nThe site uses JavaScript. Two options:\n")
    
    print("OPTION 1: Install Playwright")
    print("  pip install playwright")
    print("  playwright install")
    print("  python scripts/download_ageofindex_plans.py")
    
    print("\nOPTION 2: Manual Download")
    print("  1. Open: https://www.ageofindex.com/plans")
    print("  2. For each mission:")
    for i, mission in enumerate(MISSIONS, 1):
        title = mission.replace('-', ' ').title()
        print(f"     {i:2d}. Select '{title}' from dropdown")
    print("  3. Right-click on battle plan → Save Image As")
    print("  4. Save to: assets/battle-plans-ageofindex/aos-{mission}.png")
    
    print("\nOPTION 3: Browser DevTools")
    print("  1. Open https://www.ageofindex.com/plans")
    print("  2. Open DevTools (F12)")
    print("  3. Network tab → Filter: Images")
    print("  4. Select each mission, find image URLs")
    print("  5. Download images directly")

if __name__ == "__main__":
    if PLAYWRIGHT_AVAILABLE:
        print("Playwright detected - starting automated download...")
        download_with_playwright()
    else:
        manual_instructions()
