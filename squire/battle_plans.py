"""
Battle Plan Data Module for Age of Sigmar 4th Edition

Contains battle plan definitions from General's Handbook 2025-2026.
"""

import random
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class BattlePlan:
    """Complete battle plan configuration"""

    name: str
    deployment: str
    deployment_description: str
    objectives: str
    scoring: str
    underdog_ability: str
    special_rules: Optional[List[str]] = None
    turn_limit: int = 5
    deployment_map_url: Optional[str] = None


# GHB 2025-2026 Battle Plans
AOS_BATTLE_PLANS = [
    {
        "name": "Passing Seasons",
        "deployment": "Long edge deployment",
        "deployment_map_url": "/static/battle-plans-matplotlib/aos-passing-seasons-matplotlib.png",
        "objectives": 'Gnarlroot and Oakenbrow objectives at 24" and 48" from long edges',
        "scoring": "Battle rounds 1,3,5: 5 VP per Gnarlroot objective. Battle rounds 2,4: 5 VP per Oakenbrow objective.",
        "underdog_ability": "Burgeoning Rejuvenation: Heal D3 on Oakenbrow objectives OR add ward save to Gnarlroot objectives",
        "special_rules": [],
    },
    {
        "name": "Paths of the Fey",
        "deployment": "Long edge deployment",
        "deployment_map_url": "/static/battle-plans-matplotlib/aos-paths-of-the-fey-matplotlib.png",
        "objectives": 'Central Heartwood, Gnarlroot at 12" from center, Oakenbrow at 12" from center, Winterleaf at 24" from center',
        "scoring": "5 VP if you control at least 1 objective. 3 VP if you control 2 or more objectives. 2 VP if you control more objectives than opponent.",
        "underdog_ability": 'The Spirit Paths Open: Pick 2 objectives - remove nearby units and set them up within 3" of those objectives',
        "special_rules": [],
    },
    {
        "name": "Roiling Roots",
        "deployment": "Diagonal corner deployment",
        "deployment_map_url": "/static/battle-plans-matplotlib/aos-roiling-roots-matplotlib.png",
        "objectives": "6 objectives in diagonal line across battlefield",
        "scoring": "5 VP if you control at least 1 objective. 3 VP if you control any pairs of objectives. 2 VP if you control more objectives than opponent.",
        "underdog_ability": "Tangling Tendrils: Pick a pair of objectives - units contesting them have STRIKE-LAST",
        "special_rules": [],
    },
    {
        "name": "Cyclic Shifts",
        "deployment": "Diagonal corner deployment",
        "deployment_map_url": "/static/battle-plans-matplotlib/aos-cyclic-shifts-matplotlib.png",
        "objectives": "6 objectives in diagonal rows, 3 per player's side",
        "scoring": "5 VP if you control at least 1 objective. 3 VP if you control 2 or more objectives. 2 VP if you control more objectives than opponent.",
        "underdog_ability": "Unpredictable Evolution: Pick a pair of objectives - they cannot be controlled this battle round",
        "special_rules": [],
    },
    {
        "name": "Surge of Slaughter",
        "deployment": "Long edge deployment",
        "deployment_map_url": "/static/battle-plans-matplotlib/aos-surge-of-slaughter-matplotlib.png",
        "objectives": "Central Heartwood objective and 4 corner objectives",
        "scoring": "5 VP if you control at least 1 objective. 3 VP if you control any pairs of objectives. 2 VP if you control more objectives than opponent.",
        "underdog_ability": "Defence of the Realm: Pick a pair of objectives - add 1 to Rend for units contesting them",
        "special_rules": [],
    },
    {
        "name": "Linked Ley Lines",
        "deployment": "Long edge deployment",
        "deployment_map_url": "/static/battle-plans-matplotlib/aos-linked-ley-lines-matplotlib.png",
        "objectives": "5 objectives in diamond formation with linked ley lines",
        "scoring": "3 VP if you control at least 1 objective. 3 VP if you control 2+ objectives. 2 VP if you control any pairs. 2 VP if you control all objectives on a linked ley line.",
        "underdog_ability": "Rooted in the Realm: Anti-MANIFESTATION(+1 Rend) on linked ley lines. MANIFESTATIONS have STRIKE-FIRST",
        "special_rules": [],
    },
    {
        "name": "Noxious Nexus",
        "deployment": "Quadrant deployment",
        "deployment_map_url": "/static/battle-plans-matplotlib/aos-noxious-nexus-matplotlib.png",
        "objectives": "3 Nexus Points: Oakenbrow, Gnarlroot, and Heartwood",
        "scoring": "Cannot control in round 1. 5 VP for Oakenbrow, 3 VP for Gnarlroot, 2 VP for Heartwood. Bonus 10 VP at end of battle if you control Heartwood.",
        "underdog_ability": "Caustic Sap: Pick an objective - roll D3 for each unit contesting it, on 2+ inflict that many mortal wounds (D6 for Heartwood)",
        "special_rules": [],
    },
    {
        "name": "The Liferoots",
        "deployment": "Diagonal corner deployment",
        "deployment_map_url": "/static/battle-plans-matplotlib/aos-the-liferoots-matplotlib.png",
        "objectives": '2 Liferoot markers on diagonal, 24" apart. Terrain features provide liferoot points.',
        "scoring": "5 VP if you control at least 1 objective. 3 VP if you control both objectives. 2 VP if you have more liferoot points (1 per terrain feature controlled).",
        "underdog_ability": 'Life Begets Life: Return 1 slain model to a unit within 1" of terrain',
        "special_rules": [],
    },
    {
        "name": "Bountiful Equinox",
        "deployment": "Long edge deployment",
        "deployment_map_url": "/static/battle-plans-matplotlib/aos-bountiful-equinox-matplotlib.png",
        "objectives": "5 objectives spread across battlefield: Oakenbrow, Gnarlroot, and Heartwood types",
        "scoring": "5 VP if you control at least 1 objective. 3 VP if you control 2+ objectives. 2 VP if you control at least 1 Oakenbrow, 1 Gnarlroot, and 1 Heartwood.",
        "underdog_ability": "Rejuvenating Bloom: Pick an objective - Heal(3) each unit contesting it",
        "special_rules": [],
    },
    {
        "name": "Lifecycle",
        "deployment": "Long edge deployment",
        "deployment_map_url": "/static/battle-plans-matplotlib/aos-lifecycle-matplotlib.png",
        "objectives": "4 lifecycle objectives in symmetrical placement with rotating primary/secondary status",
        "scoring": "4 VP if you control at least 1 objective. 2 VP if you control more objectives. Round 1: 4 VP for both Oakenbrow and Gnarlroot. After: 2 VP for primary, 1 VP per secondary.",
        "underdog_ability": "Lifecycle: Pick which objective starts as primary. Rotates each round. Primary worth 2 VP, adjacent secondaries worth 1 VP each",
        "special_rules": [],
    },
    {
        "name": "Creeping Corruption",
        "deployment": "Long edge deployment",
        "deployment_map_url": "/static/battle-plans-matplotlib/aos-creeping-corruption-matplotlib.png",
        "objectives": "6 objective grid evenly spaced across battlefield",
        "scoring": "5 VP if you control at least 1 objective. 3 VP if you control 2+ objectives. 2 VP if you control more objectives than opponent.",
        "underdog_ability": "Pulsing Life Energies: Draw line between 2 objectives - Propagation (+1 to casts/chants) OR Corruption (D3 mortal wounds to units crossed)",
        "special_rules": [],
    },
    {
        "name": "Grasp of Thorns",
        "deployment": "Quadrant deployment",
        "deployment_map_url": "/static/battle-plans-matplotlib/aos-grasp-of-thorns-matplotlib.png",
        "objectives": "4 thorn objectives, one in each table quarter",
        "scoring": "5 VP if you control at least 1 objective. 3 VP if you control 2+ objectives. 2 VP if you control more objectives than opponent.",
        "underdog_ability": "Carnivorous Flora: Pick an objective - roll for each contesting unit, on 3+ models in control zone are entangled (can't move out or be removed)",
        "special_rules": [],
    },
]

# Mission map names for matchups
MISSION_MAPS = [bp["name"] for bp in AOS_BATTLE_PLANS]

# Map names to battle plan image filenames
MAP_IMAGES = {bp["name"]: bp["deployment_map_url"].split("/")[-1] for bp in AOS_BATTLE_PLANS}

# Battle plan detailed data
BATTLE_PLAN_DATA = {
    bp["name"]: {
        "deployment": bp["deployment"],
        "objectives": bp["objectives"],
        "scoring": bp["scoring"],
        "underdog_ability": bp["underdog_ability"],
    }
    for bp in AOS_BATTLE_PLANS
}


def draw_random_battle_plan() -> BattlePlan:
    """Draw a random battle plan from GHB 2025-2026."""
    battle_plan = random.choice(AOS_BATTLE_PLANS)

    return BattlePlan(
        name=battle_plan["name"],
        deployment=battle_plan["deployment"],
        deployment_description=battle_plan["deployment"],
        objectives=battle_plan["objectives"],
        scoring=battle_plan["scoring"],
        underdog_ability=battle_plan["underdog_ability"],
        special_rules=battle_plan.get("special_rules", []),
        deployment_map_url=battle_plan.get("deployment_map_url"),
    )


def get_battle_plan_by_name(name: str) -> Optional[BattlePlan]:
    """Get a specific battle plan by name."""
    for bp in AOS_BATTLE_PLANS:
        if bp["name"] == name:
            return BattlePlan(
                name=bp["name"],
                deployment=bp["deployment"],
                deployment_description=bp["deployment"],
                objectives=bp["objectives"],
                scoring=bp["scoring"],
                underdog_ability=bp["underdog_ability"],
                special_rules=bp.get("special_rules", []),
                deployment_map_url=bp.get("deployment_map_url"),
            )
    return None
