# Mission Data Collection & Management Guide

**Purpose**: Guidelines for collecting, verifying, and maintaining official mission data for Squire module

**Last Updated**: November 20, 2025

---

## Overview

The Squire module requires accurate, up-to-date mission data from official Warhammer publications. This guide outlines the process for collecting, verifying, storing, and updating mission data.

---

## Supported Game Systems

| System | Current Edition | Current Season | Official Source |
|--------|----------------|----------------|-----------------|
| Age of Sigmar | 4th Edition | 2024-2025 | General's Handbook 2024-2025 |
| Warhammer 40,000 | 10th Edition | Leviathan | Leviathan Mission Pack |
| The Old World | 1st Edition | Current | The Old World Rulebook |

---

## Mission Data Structure

### JSON Schema

Each mission must follow this structure:

```json
{
  "id": "aos-pitched-battle-2024",
  "game_system_id": "aos",
  "edition": "4th",
  "season": "2024-2025",
  "mission_name": "Pitched Battle",
  "points_category": "any",
  "game_type": null,
  "deployment_type": "Standard",
  "objectives": "Control objectives at the end of each battle round. 2 VP per objective controlled.",
  "special_rules": "Deploy wholly within your territory. Roll off for first turn.",
  "deployment_map_url": "https://example.com/aos-pitched-battle-map.png",
  "is_active": true,
  "source_url": "https://www.warhammer-community.com/...",
  "version": 1
}
```

### Required Fields

- **id**: Unique identifier (format: `{system}-{mission-slug}-{year}`)
- **game_system_id**: Reference to game system (`aos`, `40k`, `old_world`)
- **edition**: Edition number/name (`4th`, `10th`, `1st`)
- **season**: Season/publication identifier (or `null`)
- **mission_name**: Official mission name
- **points_category**: Points range (`1000`, `2000`, `3000`, `any`, or game type)
- **deployment_type**: Deployment zone configuration
- **objectives**: Victory conditions and scoring
- **special_rules**: Special mission rules
- **source_url**: Link to official source for verification

### Optional Fields

- **deployment_map_url**: Link to deployment map image
- **game_type**: For 40k (`combat_patrol`, `incursion`, `strike_force`, `onslaught`)

---

## Data Collection Process

### Step 1: Identify Official Source

**Age of Sigmar**
- General's Handbook (annual publication)
- Warhammer Community articles
- Official FAQs and errata

**Warhammer 40,000**
- Core rulebook missions
- Chapter Approved / Leviathan Mission Pack
- Warhammer Community articles
- Official FAQs and errata

**The Old World**
- Core rulebook missions
- Warhammer Community articles
- Official supplements

### Step 2: Extract Mission Data

For each mission, record:

1. **Mission Name** - Exact official name
2. **Deployment** - How armies deploy (zones, restrictions)
3. **Objectives** - Victory points, control conditions
4. **Special Rules** - Mission-specific rules
5. **Points Range** - Recommended points or game size
6. **Source Page** - Page number in publication

### Step 3: Create JSON File

Create file in: `squire/data/missions/{system}_missions.json`

```json
{
  "metadata": {
    "game_system": "aos",
    "edition": "4th",
    "season": "2024-2025",
    "source": "General's Handbook 2024-2025",
    "collected_date": "2025-11-20",
    "verified_by": "Your Name"
  },
  "missions": [
    {
      "id": "aos-battle-tactics-2024",
      "mission_name": "Battle Tactics",
      ...
    },
    ...
  ]
}
```

### Step 4: Verification

- [ ] Cross-reference with official publication (page numbers)
- [ ] Check for typos or transcription errors
- [ ] Verify points categories match official recommendations
- [ ] Confirm all special rules are included
- [ ] Test mission randomizer with new data
- [ ] Peer review by another contributor

### Step 5: Documentation

Include in commit message:
```
feat(squire): Add AoS 4th Edition missions (GH 2024-2025)

- Added 12 Pitched Battle missions
- Source: General's Handbook 2024-2025, pages 45-67
- Verified against official publication
- All missions tested with randomizer

Refs: SQUIRE-017
```

---

## Mission Versioning

### When to Create New Version

Create a new version when:
- Official errata changes mission rules
- New season/publication replaces old missions
- Typo corrections in mission text
- Clarifications from official FAQs

### Version Update Process

1. **Mark old version inactive**:
   ```sql
   UPDATE squire_missions
   SET is_active = FALSE
   WHERE id = 'aos-pitched-battle-2024';
   ```

2. **Create new version**:
   ```json
   {
     "id": "aos-pitched-battle-2025",
     "version": 2,
     "supersedes": "aos-pitched-battle-2024",
     ...
   }
   ```

3. **Migration script**:
   - Create migration file: `migrations/YYYY-MM-DD_update_aos_missions.sql`
   - Include rollback capability
   - Document changes in changelog

4. **Update documentation**:
   - Add entry to CHANGELOG.md
   - Update source URLs
   - Note what changed (errata, new season, etc.)

---

## Adding New Game System

### Prerequisites

- Official publication available
- Sufficient mission pool (minimum 6 missions)
- Community demand for system
- Maintenance commitment

### Process

1. **Add to game_systems table**:
   ```sql
   INSERT INTO squire_game_systems (id, display_name, current_edition, is_active)
   VALUES ('new_system', 'New Warhammer System', '1st', true);
   ```

2. **Create faction list**:
   - `squire/data/factions/new_system_factions.json`
   - Include all armies/factions

3. **Collect mission data**:
   - Follow Mission Data Structure above
   - Create `squire/data/missions/new_system_missions.json`

4. **Update frontend**:
   - Add system to dropdown in mission randomizer
   - Add faction options to battle creation
   - Update point value options if different

5. **Documentation**:
   - Update README.md with new system
   - Add system-specific notes if needed
   - Update ROADMAP.md

6. **Testing**:
   - Test mission randomizer with new system
   - Test battle creation with new factions
   - Verify statistics calculations work

---

## Data Quality Standards

### Accuracy Requirements

- ✅ **100% Official** - Only use official Games Workshop publications
- ✅ **Current** - Use most recent edition/season
- ✅ **Verified** - Cross-checked against source
- ✅ **Complete** - All mission details included
- ✅ **Cited** - Source URL provided

### What NOT to Include

- ❌ **Fan-made missions** - Only official GW content
- ❌ **Outdated missions** - Unless historical archive
- ❌ **Homebrew rules** - Only official rules
- ❌ **Speculation** - Only published content
- ❌ **Unofficial sources** - Only official GW publications

---

## Maintenance Schedule

### Quarterly Review (Every 3 months)

- Check for new publications
- Check for errata/FAQs
- Review community feedback on mission data
- Update deprecated missions

### Annual Update (Once per year)

- New General's Handbook (AoS)
- New Chapter Approved (40k)
- Any new game system releases
- Comprehensive data audit

### Ad-hoc Updates

- When errata published
- When new season announced
- When community reports errors
- When new game system launches

---

## Mission Data Files Location

```
squire/
├── data/
│   ├── missions/
│   │   ├── aos_missions.json          # AoS 4th Edition
│   │   ├── 40k_missions.json          # 40k 10th Edition
│   │   ├── old_world_missions.json    # Old World
│   │   └── schema.json                # JSON schema validation
│   ├── factions/
│   │   ├── aos_factions.json
│   │   ├── 40k_factions.json
│   │   └── old_world_factions.json
│   └── game_systems.json              # Game system definitions
└── scripts/
    ├── seed_missions.py               # Seed database from JSON
    ├── validate_missions.py           # Validate JSON against schema
    └── update_missions.py             # Update missions (new season)
```

---

## Validation Script

Before committing mission data:

```bash
# Validate JSON schema
python squire/scripts/validate_missions.py squire/data/missions/aos_missions.json

# Test seeding
python squire/scripts/seed_missions.py --dry-run

# Run tests
pytest tests/unit/squire/test_missions.py -v
```

---

## Community Contributions

### How to Contribute Mission Data

1. **Fork repository**
2. **Create branch**: `git checkout -b data/aos-missions-2025`
3. **Add/update mission JSON** following this guide
4. **Validate data**: Run validation script
5. **Test**: Ensure missions load and randomize correctly
6. **Document sources**: Include page numbers and URLs
7. **Submit PR**: Reference this guide in description

### Mission Data PR Checklist

- [ ] JSON follows schema
- [ ] All required fields present
- [ ] Source URL included
- [ ] Verified against official publication
- [ ] Validation script passes
- [ ] Tests pass
- [ ] No typos or transcription errors
- [ ] Season/edition clearly labeled

---

## FAQ

**Q: Can I add fan-made missions?**  
A: No. Only official Games Workshop missions are accepted.

**Q: What if a mission has regional variants?**  
A: Include the most widely used official version. Note variants in comments.

**Q: How do I handle missions with multiple deployment maps?**  
A: Create separate mission entries, one per deployment option.

**Q: What if the official source is behind a paywall?**  
A: You must have legal access to verify. Include page numbers for others to verify.

**Q: Can I submit missions in another language?**  
A: English only for now. We may support localization in Phase 3.

**Q: How often are missions updated?**  
A: Quarterly review, annual major update, ad-hoc for errata.

---

## References

- **Official Sources**:
  - [Warhammer Community](https://www.warhammer-community.com)
  - [Games Workshop](https://www.games-workshop.com)
  - [Warhammer 40,000 Rules](https://www.warhammer40000.com)
  - [Age of Sigmar Rules](https://www.ageofsigmar.com)

- **Internal Docs**:
  - [ROADMAP.md](../ROADMAP.md) - Squire module roadmap
  - [BACKLOG.md](../BACKLOG.md) - Mission data tasks (SQUIRE-017, SQUIRE-018, SQUIRE-018A)
  - [CONTRIBUTING.md](../CONTRIBUTING.md) - General contribution guidelines

---

**Maintained by**: Squig League Community  
**Questions?**: Open an issue with label `data:missions`
