# Battle Plan Icon Integration

## Overview
Integration of SVG icons (crosshair, oak, stone-tower, magic-portal) into matplotlib battle plan diagrams with parchment background.

## Icon Source
- **Provider**: game-icons.net (CC BY 3.0 license)
- **API**: Iconify API for direct download
- **Color**: Gray (#808080) for all icons
- **Format**: SVG converted to PNG via Selenium headless Chrome

## Icon Specifications

### Selected Icons
1. **Objectives**: `crosshair.svg` - Simple crosshair targeting symbol
2. **Forests**: `oak.svg` - Oak tree silhouette
3. **Ruins**: `stone-tower.svg` - Ruined tower structure
4. **Places of Power**: `magic-portal.svg` - Swirling magical portal

### Conversion Process
- SVG rendered in headless Chrome at 512x512px
- Transparent background maintained
- PNG export via Selenium screenshot
- Script: `scripts/convert_svg_to_png.py`

## Integration Method

### Scale Calculation
**Battlefield dimensions:**
- Game size: 60" × 44"
- Figure size: 12" × 8.8" at DPI 100
- Pixel dimensions: 1200 × 880 pixels
- **Scale factor: 1 game inch = 20 pixels**

**Icon sizing:**
- PNG source: 512 × 512 pixels
- Target size on diagram: `size_in_inches × 20 pixels`
- OffsetImage zoom formula: `zoom = size / 30`
  - Objectives (6"): zoom ≈ 0.2 → ~120px on diagram
  - Forests (4"): zoom ≈ 0.133 → ~80px on diagram
  - Ruins (5"): zoom ≈ 0.167 → ~100px on diagram
  - Places of Power (3"): zoom ≈ 0.1 → ~60px on diagram

### Previous Errors
1. **Attempt 1**: zoom = size/80 → icons too small (barely visible)
2. **Attempt 2**: zoom = size/15 → icons too large (dominated entire battlefield)
3. **Correct**: zoom = size/30 → icons proportional to game size

## Implementation Details

### Drawing Functions
Each terrain type overlays icon on existing matplotlib markers:
- **Objectives**: Icon over colored circle (keeps colored circle visible)
- **Forests/Ruins/Places of Power**: Icon only (replaces matplotlib primitives)

### Code Changes
- Added imports: `OffsetImage`, `AnnotationBbox`, `PIL.Image`
- Added `load_icon_image()` function for PNG loading
- Modified all draw functions to use `AnnotationBbox` with centered alignment
- Parchment background at `zorder=-1` (behind all elements)

## File Structure
```
assets/
  battle-icons/
    objectives/
      crosshair.svg
      crosshair.png
    forests/
      oak.svg
      oak.png
    ruins/
      stone-tower.svg
      stone-tower.png
    places_of_power/
      magic-portal.svg
      magic-portal.png
  textures/
    parchment-texture.png
  battle-plans-parchment/
    aos-*.png (generated output)
```

## Scripts
1. `download_battle_icons.ps1` - Download SVGs from Iconify API
2. `convert_svg_to_png.py` - Convert SVG to PNG with transparency
3. `generate_battle_plans.py` - Generate diagrams with icons + parchment

## Attribution
Icons by various artists via game-icons.net (CC BY 3.0):
- Crosshair, Oak, Stone Tower, Magic Portal
- Full attribution: https://game-icons.net
