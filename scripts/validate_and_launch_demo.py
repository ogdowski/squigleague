"""Validate battle plans demo and launch if tests pass"""
import sys
import subprocess
import hashlib
import time
from pathlib import Path
from collections import defaultdict

def test_html_exists():
    """Test 1: HTML file exists"""
    html_file = Path("battle-plans-demo.html")
    if not html_file.exists():
        print("FAIL: battle-plans-demo.html not found")
        return False
    
    size_kb = html_file.stat().st_size / 1024
    if size_kb < 10:
        print(f"FAIL: HTML too small ({size_kb:.1f}KB)")
        return False
    
    print(f"PASS: HTML exists ({size_kb:.1f}KB)")
    return True

def test_all_images_exist():
    """Test 2: All 36 images exist"""
    missions = [
        'passing-seasons', 'paths-of-the-fey', 'roiling-roots', 'cyclic-shifts',
        'surge-of-slaughter', 'linked-ley-lines', 'noxious-nexus', 'the-liferoots',
        'bountiful-equinox', 'lifecycle', 'creeping-corruption', 'grasp-of-thorns'
    ]
    
    missing = []
    for mission in missions:
        for folder, suffix in [
            ('battle-plans', '.png'),
            ('battle-plans-ageofindex', '.png'),
            ('battle-plans-matplotlib', '-matplotlib.png')
        ]:
            img = Path(f"assets/{folder}/aos-{mission}{suffix}")
            if not img.exists():
                missing.append(str(img))
    
    if missing:
        print(f"FAIL: {len(missing)} images missing:")
        for m in missing[:5]:
            print(f"  - {m}")
        return False
    
    print("PASS: All 36 images exist")
    return True

def test_aoi_images_unique():
    """Test 3: All 12 AOI images are unique"""
    aoi_dir = Path("assets/battle-plans-ageofindex")
    images = list(aoi_dir.glob("aos-*.png"))
    
    if len(images) != 12:
        print(f"FAIL: Expected 12 AOI images, found {len(images)}")
        return False
    
    hashes = defaultdict(list)
    for img in images:
        hash_val = hashlib.md5(img.read_bytes()).hexdigest()
        hashes[hash_val].append(img.name)
    
    if len(hashes) != 12:
        print(f"FAIL: AOI images not unique ({len(hashes)}/12 unique)")
        for hash_val, files in hashes.items():
            if len(files) > 1:
                print(f"  Duplicates: {', '.join(files)}")
        return False
    
    print(f"PASS: All 12 AOI images unique")
    return True

def test_aoi_different_from_others():
    """Test 4: AOI images different from Wahapedia/Matplotlib"""
    sample = "aos-passing-seasons.png"
    
    aoi_hash = hashlib.md5(Path(f"assets/battle-plans-ageofindex/{sample}").read_bytes()).hexdigest()
    waha_hash = hashlib.md5(Path(f"assets/battle-plans/{sample}").read_bytes()).hexdigest()
    
    if aoi_hash == waha_hash:
        print("FAIL: AOI images identical to Wahapedia")
        return False
    
    print("PASS: AOI images different from Wahapedia")
    return True

def start_server_if_needed():
    """Start HTTP server if not running"""
    # Check if port 8080 is listening
    result = subprocess.run(
        ['powershell', '-Command', 'Get-NetTCPConnection -LocalPort 8080 -ErrorAction SilentlyContinue'],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0 or not result.stdout.strip():
        print("Starting HTTP server on port 8080...")
        subprocess.Popen(
            ['python', '-m', 'http.server', '8080'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        time.sleep(2)
        print("Server started")
    else:
        print("Server already running")

def open_browser():
    """Open browser to demo page"""
    subprocess.run(['powershell', '-Command', 'Start-Process "http://localhost:8080/battle-plans-demo.html"'])
    print("Browser opened: http://localhost:8080/battle-plans-demo.html")

def main():
    print("=" * 60)
    print("BATTLE PLANS DEMO VALIDATION")
    print("=" * 60)
    
    tests = [
        ("HTML exists", test_html_exists),
        ("All images exist", test_all_images_exist),
        ("AOI images unique", test_aoi_images_unique),
        ("AOI different from others", test_aoi_different_from_others),
    ]
    
    failed = []
    for name, test_func in tests:
        print(f"\nTest: {name}")
        if not test_func():
            failed.append(name)
    
    print("\n" + "=" * 60)
    if failed:
        print(f"VALIDATION FAILED: {len(failed)}/{len(tests)} tests failed")
        for name in failed:
            print(f"  - {name}")
        print("=" * 60)
        sys.exit(1)
    
    print(f"VALIDATION PASSED: {len(tests)}/{len(tests)} tests passed")
    print("=" * 60)
    
    start_server_if_needed()
    open_browser()

if __name__ == "__main__":
    main()
