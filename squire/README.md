# Squire Module

**Battle Planning and Matchup Tracking for Tabletop Wargames**

Version: 0.1.0  
Status: ✅ Operational  
Games Supported: Age of Sigmar, Warhammer 40,000, The Old World

---

## Overview

The Squire module provides automated battle plan generation for tournament organizers and casual gaming groups. Generate random, balanced battle scenarios with proper deployment zones, objectives, and victory conditions that follow official matched play formats.

### Core Features

- **Battle Plan Randomization**: Generate random missions for supported game systems
- **Tournament Support**: Create multiple battle plans for tournament rounds
- **Official Formats**: Follows current edition rules for each game system
- **REST API**: Easy integration with frontends and external tools

---

## Supported Game Systems

### Age of Sigmar (4th Edition - Matched Play)

**Format**: 2000 points, 5 battle rounds, General's Handbook 2025-2026

**Battle Plans** (12 official missions):
1. **Passing Seasons** - Alternating objective scoring with seasonal rotation
2. **Paths of the Fey** - Central objective with fey teleportation mechanics
3. **Roiling Roots** - Diagonal objectives with strike-last defensive ability
4. **Cyclic Shifts** - Shrinking battlefield as objectives are removed
5. **Surge of Slaughter** - Aggressive combat bonuses for underdog
6. **Linked Ley Lines** - Connected objectives with magic/prayer enhancement
7. **Noxious Nexus** - Mortal wound damage and all-or-nothing bonus
8. **The Liferoots** - Model resurrection on obscuring diagonal
9. **Bountiful Equinox** - Combination scoring with healing mechanic
10. **Lifecycle** - Rotating primary objective system
11. **Creeping Corruption** - Territory corruption with line propagation
12. **Grasp of Thorns** - Movement restriction and entanglement effects

**Key Mechanics**:
- Ghyranite objective naming (Gnarlroot, Oakenbrow, Winterleaf, Heartwood)
- Underdog abilities (special powers for player behind on VP)
- Mission-specific deployment types (long edge, diagonal, quadrant)
- Unique victory point scoring per mission

---

### Warhammer 40,000 (10th Edition)

**Format**: 2000 points, 5 rounds, Matched Play

**Deployments**:
- Dawn of War (short edges)
- Search and Destroy (diagonal corners)
- Sweeping Engagement (offset long edges)
- Crucible of Battle (center circles)

**Primary Missions**:
- Take and Hold
- The Ritual
- Purge the Foe
- Vital Ground
- Scorched Earth

**Secondary Objectives**:
- Assassinate
- Bring It Down
- Behind Enemy Lines
- First Strike
- Overwhelming Force

---

### The Old World

**Format**: 2000 points, 6 rounds (random length), Rank & Flank battles

**Deployments**:
- Pitched Battle (classic battle lines)
- Corner Deployment
- Meeting Engagement (short edges)

**Scenarios**:
- Pitched Battle
- Capture the Flags
- Breakthrough
- Hold the Ground
- Blood and Glory

---

## API Endpoints

### Base URL
```
http://localhost:8000/api/squire
```

### GET `/battle-plan/random`

Generate a single random battle plan for the specified game system.

**Query Parameters**:
- `system` (string, required): Game system identifier
  - `age_of_sigmar`
  - `warhammer_40k`
  - `the_old_world`

**Example Request**:
```bash
curl "http://localhost:8000/api/squire/battle-plan/random?system=age_of_sigmar"
```

**Example Response**:
```json
{
  "name": "AoS Spearhead - Frontal Assault",
  "game_system": "age_of_sigmar",
  "deployment": "frontal_assault",
  "deployment_description": "Players deploy in opposite halves of the battlefield, divided by a line down the center. Standard battle lines 9\" from center.\nPlayer zones: 18\" from center line on your side",
  "primary_objective": "Control the Center - Hold the central objective marker",
  "secondary_objectives": [
    "Hold the Line - No enemies in your deployment zone at battle end",
    "Break Their Ranks - Destroy half of enemy's starting models",
    "Aggressive Expansion - Have units in all four table quarters"
  ],
  "victory_conditions": "Score victory points from primary objective, secondary objectives, and completed battle tactics. Most VP at end of Round 5 wins.",
  "turn_limit": 5,
  "special_rules": [
    "Spearhead format: 1000 points maximum",
    "First turn determined by priority roll",
    "Battle tactics chosen secretly each turn"
  ],
  "battle_tactics": [
    "Fierce Conquerors - Control an objective you didn't control at start of turn",
    "Unstoppable Advance - Charge with 3+ units this turn",
    "Magical Dominance - Successfully cast 3+ spells this turn",
    "Slaughter and Plunder - Destroy enemy unit and control objective",
    "Strategic Withdrawal - Fall back and still shoot/charge",
    "Endless Legions - Return destroyed unit to battlefield"
  ]
}
```

---

### GET `/battle-plan/multiple`

Generate multiple battle plans for tournament rounds.

**Query Parameters**:
- `system` (string, required): Game system identifier
- `count` (integer, optional): Number of plans to generate (default: 3, min: 1, max: 10)

**Example Request**:
```bash
curl "http://localhost:8000/api/squire/battle-plan/multiple?system=warhammer_40k&count=5"
```

**Example Response**:
```json
[
  {
    "name": "40k 10th Edition - Search and Destroy",
    "game_system": "warhammer_40k",
    "deployment": "search_and_destroy",
    ...
  },
  {
    "name": "40k 10th Edition - Dawn of War",
    "game_system": "warhammer_40k",
    "deployment": "dawn_of_war",
    ...
  }
  // ... 3 more battle plans
]
```

---

### GET `/systems`

List all supported game systems and their available deployments.

**Example Request**:
```bash
curl "http://localhost:8000/api/squire/systems"
```

**Example Response**:
```json
[
  {
    "game_system": "age_of_sigmar",
    "deployments": ["frontal_assault", "encircle", "hammer_and_anvil", "clash"],
    "description": "Age of Sigmar 4th Edition Spearhead format"
  },
  {
    "game_system": "warhammer_40k",
    "deployments": ["dawn_of_war", "search_and_destroy", "sweeping_engagement", "crucible_of_battle"],
    "description": "Warhammer 40,000 10th Edition matched play"
  },
  {
    "game_system": "the_old_world",
    "deployments": ["frontal_assault", "encircle", "hammer_and_anvil"],
    "description": "Warhammer: The Old World legacy battles"
  }
]
```

---

### GET `/health`

Health check endpoint for Squire module.

**Example Request**:
```bash
curl "http://localhost:8000/api/squire/health"
```

**Example Response**:
```json
{
  "module": "squire",
  "status": "operational",
  "features": ["battle_plans"],
  "version": "0.1.0"
}
```

---

## Usage Examples

### Python (requests)

```python
import requests

# Generate random AoS battle plan
response = requests.get(
    "http://localhost:8000/api/squire/battle-plan/random",
    params={"system": "age_of_sigmar"}
)
battle_plan = response.json()
print(f"Deployment: {battle_plan['deployment']}")
print(f"Primary Objective: {battle_plan['primary_objective']}")
```

### JavaScript (fetch)

```javascript
// Generate 3 battle plans for a tournament
fetch('http://localhost:8000/api/squire/battle-plan/multiple?system=warhammer_40k&count=3')
  .then(response => response.json())
  .then(plans => {
    plans.forEach((plan, index) => {
      console.log(`Round ${index + 1}: ${plan.name}`);
    });
  });
```

### PowerShell

```powershell
# Generate random 40k battle plan
$plan = curl "http://localhost:8000/api/squire/battle-plan/random?system=warhammer_40k" | ConvertFrom-Json
Write-Host "Mission: $($plan.primary_objective)"
```

---

## Architecture

### Data Models

**BattlePlan** (dataclass):
- `name`: Display name for the battle plan
- `game_system`: GameSystem enum value
- `deployment`: DeploymentType enum value
- `deployment_description`: Full text description of deployment zones
- `primary_objective`: Main mission objective
- `secondary_objectives`: List of additional scoring opportunities
- `victory_conditions`: How to win the game
- `turn_limit`: Number of battle rounds
- `special_rules`: Optional list of format-specific rules
- `battle_tactics`: Optional list of available tactics (AoS only)

**GameSystem** (enum):
- `AOS`: Age of Sigmar
- `WARHAMMER_40K`: Warhammer 40,000
- `OLD_WORLD`: The Old World

**DeploymentType** (enum):
- `FRONTAL_ASSAULT`: Opposing battle lines
- `ENCIRCLE`: Diagonal corners
- `HAMMER_AND_ANVIL`: Short edge deployment
- `CLASH`: Center circle deployment
- Plus 40k-specific deployments

---

## Testing

### Standalone Test

```bash
# Test all game systems
python test_battle_plans.py
```

### Manual API Testing

```bash
# Test Squire health
curl http://localhost:8000/api/squire/health

# Generate AoS battle plan
curl "http://localhost:8000/api/squire/battle-plan/random?system=age_of_sigmar"

# Generate multiple Old World scenarios
curl "http://localhost:8000/api/squire/battle-plan/multiple?system=the_old_world&count=5"
```

---

## Development

### Adding a New Game System

1. Add enum value to `GameSystem` in `battle_plans.py`
2. Create deployment dictionary (e.g., `NEW_SYSTEM_DEPLOYMENTS`)
3. Create objectives/missions lists
4. Implement generator function (e.g., `generate_new_system_battle_plan()`)
5. Add to `generators` dict in `generate_battle_plan()`
6. Update documentation and examples

### Adding New Deployments

1. Add to `DeploymentType` enum
2. Add deployment details to appropriate `*_DEPLOYMENTS` dictionary
3. Update documentation

---

## Roadmap

### v0.2.0 (Planned)
- [ ] Save battle plans to database
- [ ] Battle plan history tracking
- [ ] Custom deployment zone editor
- [ ] Terrain generation rules

### v0.3.0 (Future)
- [ ] Player matchup tracking
- [ ] Tournament bracket management
- [ ] Swiss pairing algorithm
- [ ] Tiebreaker calculations

### v0.4.0 (Future)
- [ ] Army list integration with Herald module
- [ ] Battle results recording
- [ ] Player statistics dashboard
- [ ] ELO rating system

---

## Known Limitations

- Battle plan data based on general knowledge of current editions
- Official battle pack scenarios not included (proprietary)
- No terrain placement randomization yet
- No custom scenario support

---

## Contributing

When contributing battle plan data:

1. Verify against official rulebooks
2. Include edition number in comments
3. Follow existing data structure patterns
4. Add tests for new game systems
5. Update this README with new features

---

## License

Part of Squig League project - See repository LICENSE file

---

## Support

- Repository: https://github.com/ogdowski/squigleague
- Issues: Use GitHub Issues for bug reports
- Discussions: Use GitHub Discussions for feature requests

---

**Built with**: FastAPI, Python 3.11, Pydantic  
**Integrated with**: Herald API  
**Deployed via**: Docker Compose
