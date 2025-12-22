# Battle Plans Data Analysis

## Source File
`squire/battle_plans.py` - Contains ALL battle plan data for AOS, 40k, and The Old World

## AOS Battle Plans Structure

Each battle plan in `AOS_BATTLE_PLANS` list contains:
- **name**: Battle plan name
- **deployment**: Deployment type description (text)
- **deployment_map_url**: Path to Wahapedia reference image
- **objectives**: List of objective dictionaries with:
  - `name`: Objective name
  - `location`: TEXT DESCRIPTION of objective location (NOT coordinates!)
- **scoring**: VP scoring rules
- **underdog_ability**: Special ability for player behind on VP
- **special_rules**: Additional rules

## Objective Location Data (from battle_plans.py)

### Passing Seasons (4 objectives)
1. Gnarlroot 1: '24" from long edge, 12" from center'
2. Oakenbrow 1: '24" from long edge, 12" from center (opposite side)'
3. Gnarlroot 2: '48" from long edge, 12" from center'
4. Oakenbrow 2: '48" from long edge, 12" from center (opposite side)'

### Paths of the Fey (4 objectives)
1. Central Heartwood: "Center of battlefield"
2. Gnarlroot: '12" from center toward each long edge'
3. Oakenbrow: '12" from center toward each long edge'
4. Winterleaf: '24" from center on battlefield quarters'

### Roiling Roots (6 objectives)
1. Diagonal Row 1: "6 objectives in diagonal line across battlefield"

### Cyclic Shifts (6 objectives)
1. Diagonal Row: "6 objectives in diagonal rows, 3 per player's side"

### Surge of Slaughter (5 objectives)
1. Central Heartwood: "Center"
2. 4 Corner Objectives: "Near each corner of battlefield"

### Linked Ley Lines (5 objectives)
1. Ley Line Network: "5 objectives in diamond formation"

### Noxious Nexus (3 objectives)
1. 3 Nexus Points: "Spread across battlefield"

### The Liferoots (2 objectives)
1. 2 Liferoot Markers: 'On diagonal, 24" apart'

### Bountiful Equinox (5 objectives)
1. 5 Objective Spread: "Distributed across battlefield"

### Lifecycle (4 objectives)
1. 4 Lifecycle Objectives: "Symmetrical placement across battlefield"

### Creeping Corruption (6 objectives)
1. 6 Objective Grid: "Evenly spaced across battlefield"

### Grasp of Thorns (4 objectives)
1. 4 Thorn Objectives: "One in each table quarter"

## CRITICAL FINDING

**The objective locations are VAGUE TEXT DESCRIPTIONS, not precise coordinates!**

Examples:
- "Center of battlefield"
- "Near each corner"
- "Evenly spaced"
- '24" from long edge, 12" from center'

This means:
1. ✅ We MUST extract coordinates from Wahapedia images (no alternative source)
2. ✅ Template matching is correct approach (matching visual tokens)
3. ❌ No JSON file with precise coordinates exists
4. ❌ Cannot generate diagrams without extracting from reference images first

## Battlefield Dimensions

From code context:
- Standard AOS battlefield: 44" x 60" (assumed)
- DPI for image analysis: 14 pixels per inch (used in scripts)

## Next Steps

1. Perfect template matching on Passing Seasons to extract 4 objectives
2. Apply method to all 12 battle plans
3. Generate objectives_final.json with extracted coordinates
4. Use coordinates to create matplotlib IP-neutral diagrams
