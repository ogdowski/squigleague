"""Find battle plan images by inspecting browser DevTools network tab"""
import subprocess
import time

# Open browser to the page so user can inspect DevTools
print("Opening browser to ageofindex.com/plans")
print("\nINSTRUCTIONS:")
print("1. Open DevTools (F12)")
print("2. Go to Network tab")
print("3. Filter by 'Img' or 'png'")
print("4. Navigate through battle plans")
print("5. Look for image URLs being loaded")
print("6. Check if images are:")
print("   - Direct URLs (https://.../*.png)")
print("   - Base64 encoded (data:image/png;base64,...)")
print("   - Canvas rendered (check canvas element)")
print("   - SVG inline")
print("\nOpening browser...")

subprocess.Popen(['cmd', '/c', 'start', 'https://www.ageofindex.com/plans'])

print("\nPress Ctrl+C when done inspecting")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nDone")
