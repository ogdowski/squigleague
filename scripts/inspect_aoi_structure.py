"""Inspect ageofindex.com structure to find actual battle plan images"""
from playwright.sync_api import sync_playwright
import time

def inspect_aoi():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        # Capture network requests
        image_urls = []
        def handle_response(response):
            if '.png' in response.url or '.jpg' in response.url or '.svg' in response.url:
                print(f"Image: {response.url}")
                image_urls.append(response.url)
        
        page.on("response", handle_response)
        
        print("Loading https://www.ageofindex.com/plans")
        page.goto("https://www.ageofindex.com/plans", wait_until="networkidle")
        time.sleep(3)
        
        # Get all img elements
        imgs = page.locator("img").all()
        print(f"\nFound {len(imgs)} img elements:")
        for i, img in enumerate(imgs[:10]):  # First 10
            src = img.get_attribute("src")
            alt = img.get_attribute("alt")
            print(f"  {i+1}. src={src}, alt={alt}")
        
        # Check for canvas elements (might be rendering images there)
        canvases = page.locator("canvas").all()
        print(f"\nFound {len(canvases)} canvas elements")
        
        # Get page content
        content = page.content()
        with open("temp_aoi_rendered.html", "w", encoding="utf-8") as f:
            f.write(content)
        print("\nSaved rendered HTML to temp_aoi_rendered.html")
        
        print(f"\nCaptured {len(image_urls)} image URLs:")
        for url in image_urls[:20]:
            print(f"  {url}")
        
        input("\nPress Enter to close browser...")
        browser.close()

if __name__ == "__main__":
    inspect_aoi()
