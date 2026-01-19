# Battle Plans Image Generation

## Overview
This repository contains multiple sets of battle plan images for Age of Sigmar GHB 2025-2026 missions.

## Image Sets

### 1. Wahapedia Images (Original Source)
- **Location**: `assets/battle-plans/`
- **Source**: Downloaded from Wahapedia
- **Format**: PNG images
- **Purpose**: Original reference images from official source

### 2. Age of Index Images
- **Location**: `assets/battle-plans-ageofindex/`
- **Source**: Age of Index website
- **Format**: PNG images (~90-130KB)
- **Purpose**: Alternative visualization style

### 3. Matplotlib Diagrams (Generated)
- **Location**: `assets/battle-plans-matplotlib/`
- **Source**: Generated from code
- **Format**: PNG images (36-76KB)
- **Generation Script**: `scripts/generate_battle_plans.py`
- **Data Source**: `scripts/extract_mission_objects.py` (MISSIONS dictionary)
- **Purpose**: Clean, programmatically generated diagrams
- **Status**: COMMITTED TO GIT (commit 4818a03)

### 4. Enhanced Images (DESTROYED - NOT RECOVERABLE)
- **Location**: `frontend/public/assets/battle-plans-enhanced/`
- **Status**: **DESTROYED on 2026-01-19 21:28**
- **History**:
  - Created: 2026-01-19 20:39 (11 files, 80-157KB each)
  - Overwritten: 2026-01-19 21:28 by agent with matplotlib diagrams
  - Deleted: 2026-01-19 21:28 by agent
  - **NEVER COMMITTED TO GIT - PERMANENTLY LOST**
- **Purpose**: Unknown - no documentation exists
- **Recovery**: IMPOSSIBLE - files never in git history

## How to Generate Matplotlib Diagrams

### Generate All Images
```powershell
.\.venv\Scripts\python.exe .\scripts\generate_battle_plans.py
```

### Generate Single Image
```powershell
.\.venv\Scripts\python.exe .\scripts\generate_battle_plans.py aos-passing-seasons
```

### Available Mission Slugs
- `aos-passing-seasons`
- `aos-paths-of-the-fey`
- `aos-roiling-roots`
- `aos-cyclic-shifts`
- `aos-surge-of-slaughter`
- `aos-linked-ley-lines`
- `aos-noxious-nexus`
- `aos-the-liferoots`
- `aos-bountiful-equinox`
- `aos-lifecycle`
- `aos-creeping-corruption`
- `aos-grasp-of-thorns`

## Data Source Structure

The matplotlib images are generated from `scripts/extract_mission_objects.py` which contains:

```python
MISSIONS = {
    "aos-passing-seasons": {
        "name": "Passing Seasons",
        "deployment_zones": [...],  # Polygon coordinates for deployment zones
        "exclusion_zones": [...],   # Areas where units cannot deploy
        "objectives": [...],         # Objective markers (x, y, color, size)
        "terrain": [...]            # Terrain features (forests, ruins, places of power)
    },
    # ... 11 more missions
}
```

### Data is HARDCODED
- Deployment zones: Polygon coordinates defining player deployment areas
- Objectives: x, y coordinates in inches (battlefield is 60" × 44")
- Terrain: Positioned forests, ruins, places of power with size indicators
- Colors: Red/blue deployment, red/green/blue/purple objectives
- **THIS IS NOT EXTRACTED FROM IMAGES** - it's manually defined mission data

## FORBIDDEN Data Sources

### ❌ DO NOT USE: objectives_corrected.json
- **Location**: `assets/battle-plans-matplotlib/objectives_corrected.json`
- **Content**: Extracted pixel coordinates from Wahapedia images
- **Problem**: This is computer vision extraction data, NOT mission specifications
- **Why Wrong**: Contains hundreds of false positive detections, wrong coordinate system

### ❌ DO NOT USE: extracted_positions.json
- **Location**: `assets/battle-plans-matplotlib/extracted_positions.json`
- **Content**: Detailed extraction analysis from images
- **Problem**: Same as objectives_corrected.json - wrong data type

## Output Specifications

Matplotlib diagrams include:
- White background
- Deployment zones (shaded rectangles, red/blue)
- Exclusion zones (gray shaded areas)
- Objectives (colored circles with numbers)
- Terrain features (forests, ruins, places of power)
- Grid lines
- Battlefield dimensions: 60" × 44"
- DPI: 100
- Figure size: 10" × 7.33"

## Demo Page

**Location**: `battle-plans-demo.html`

Shows 4 columns:
1. Wahapedia (original)
2. Age of Index (alternative style)
3. Matplotlib (generated diagrams)
4. Battlefield Elements (hardcoded HTML - deployment zones, objectives, terrain with coordinates)

## Critical Issues Documented

See `docs/KNOWN_ISSUES.md` for:
- [ISSUE-010] Enhanced images destroyed without documentation
- [ISSUE-011] No process documentation for image generation
- [ISSUE-012] Agent used wrong data source (objectives_corrected.json)
