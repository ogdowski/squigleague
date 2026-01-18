"""Download battle plan PNGs directly from ageofindex.com static media"""
import requests
from pathlib import Path

# Image filenames extracted from dropdown
IMAGES = {
    'passing-seasons': 'Passing_Seasons.e0e4ef9cf84dd1a765eb.png',
    'paths-of-the-fey': 'Paths_Of_The_Fey.10c7f9ef884daff43539.png',
    'roiling-roots': 'Roiling_Roots.fa268b1ff0b45c1aed26.png',
    'cyclic-shifts': 'Cyclic_Shifts.647f39547a95e61a276d.png',
    'surge-of-slaughter': 'Surge_Of_Slaughter.75b0dfbfdc0d15cccb67.png',
    'linked-ley-lines': 'Linked_Ley_Lines.99c7ce0f34aabb2a0d26.png',
    'noxious-nexus': 'Noxious_Nexus.ce345f31ad3197041d7e.png',
    'the-liferoots': 'The_Liferoots.55a2c9614fc7db34b4b4.png',
    'bountiful-equinox': 'Bountiful_Equinox.32357783c8df1bed9e63.png',
    'lifecycle': 'Lifecycle.28a464989463a702f5f3.png',
    'creeping-corruption': 'Creeping_Corruption.4db29ddb7de635452649.png',
    'grasp-of-thorns': 'Grasp_Of_Thorns.2cbb7a34ab52b8a172ab.png',
}

BASE_URL = "https://www.ageofindex.com/static/media/"

def download_direct():
    output_dir = Path("assets/battle-plans-ageofindex")
    output_dir.mkdir(exist_ok=True, parents=True)
    
    for slug, filename in IMAGES.items():
        url = BASE_URL + filename
        print(f"Downloading: {slug}")
        print(f"  URL: {url}")
        
        response = requests.get(url)
        if response.status_code == 200:
            output_path = output_dir / f"aos-{slug}.png"
            output_path.write_bytes(response.content)
            size_kb = len(response.content) / 1024
            print(f"  Saved: {output_path.name} ({size_kb:.1f}KB)")
        else:
            print(f"  ERROR: HTTP {response.status_code}")

if __name__ == "__main__":
    download_direct()
