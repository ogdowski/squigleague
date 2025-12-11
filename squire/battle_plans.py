"""
Battle Plan Randomization Module

Generates random battle plans for AoS 4th Edition, 40k 10th Edition, and The Old World.
Follows official matched play formats including deployment zones, objectives, and victory conditions.
"""

import random
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class GameSystem(str, Enum):
    """Supported game systems"""

    AOS = "age_of_sigmar"
    WARHAMMER_40K = "warhammer_40k"
    OLD_WORLD = "the_old_world"


class DeploymentType(str, Enum):
    """Standard deployment zone configurations"""

    # Age of Sigmar deployments
    FRONTAL_ASSAULT = "frontal_assault"  # Opposing edges
    ENCIRCLE = "encircle"  # Corner vs corner diagonal
    HAMMER_AND_ANVIL = "hammer_and_anvil"  # Short edges
    CLASH = "clash"  # Center deployments

    # 40k deployments
    DAWN_OF_WAR = "dawn_of_war"  # Short edges (40k)
    SEARCH_AND_DESTROY = "search_and_destroy"  # Diagonal corners (40k)
    SWEEPING_ENGAGEMENT = "sweeping_engagement"  # Long edges offset (40k)
    CRUCIBLE_OF_BATTLE = "crucible_of_battle"  # Center circle (40k)


@dataclass
class BattlePlan:
    """Complete battle plan configuration"""

    name: str
    game_system: GameSystem
    deployment: DeploymentType
    deployment_description: str
    primary_objective: str
    secondary_objectives: List[str]
    victory_conditions: str
    special_rules: Optional[List[str]] = None
    battle_tactics: Optional[List[str]] = None
    turn_limit: int = 5
    deployment_map_url: Optional[str] = None


# ═══════════════════════════════════════════════
# AGE OF SIGMAR 4TH EDITION - MATCHED PLAY
# General's Handbook 2025-2026
# ═══════════════════════════════════════════════

AOS_BATTLE_PLANS = [
    {
        "name": "Passing Seasons",
        "deployment": "Long edge deployment",
        "deployment_map_url": "/static/battle-plans/aos-passing-seasons.png",
        "objectives": [
            {"name": "Gnarlroot 1", "location": '24" from long edge, 12" from center'},
            {
                "name": "Oakenbrow 1",
                "location": '24" from long edge, 12" from center (opposite side)',
            },
            {"name": "Gnarlroot 2", "location": '48" from long edge, 12" from center'},
            {
                "name": "Oakenbrow 2",
                "location": '48" from long edge, 12" from center (opposite side)',
            },
        ],
        "scoring": "Battle rounds 1,3,5: 5 VP per Gnarlroot objective. Battle rounds 2,4: 5 VP per Oakenbrow objective.",
        "underdog_ability": "Burgeoning Rejuvenation: Heal D3 on Oakenbrow objectives OR add ward save to Gnarlroot objectives",
        "special_rules": [],
    },
    {
        "name": "Paths of the Fey",
        "deployment": "Long edge deployment",
        "deployment_map_url": "/static/battle-plans/aos-paths-of-the-fey.png",
        "objectives": [
            {"name": "Central Heartwood", "location": "Center of battlefield"},
            {"name": "Gnarlroot", "location": '12" from center toward each long edge'},
            {"name": "Oakenbrow", "location": '12" from center toward each long edge'},
            {
                "name": "Winterleaf",
                "location": '24" from center on battlefield quarters',
            },
        ],
        "scoring": "5 VP if you control at least 1 objective. 3 VP if you control 2 or more objectives. 2 VP if you control more objectives than opponent.",
        "underdog_ability": "The Spirit Paths Open: Pick 2 objectives - remove nearby units and set them up within 3\" of those objectives",
        "special_rules": [],
    },
    {
        "name": "Roiling Roots",
        "deployment": "Diagonal corner deployment",
        "deployment_map_url": "/static/battle-plans/aos-roiling-roots.png",
        "objectives": [
            {
                "name": "Diagonal Row 1",
                "location": "6 objectives in diagonal line across battlefield",
            },
        ],
        "scoring": "5 VP if you control at least 1 objective. 3 VP if you control any pairs of objectives. 2 VP if you control more objectives than opponent.",
        "underdog_ability": "Tangling Tendrils: Pick a pair of objectives - units contesting them have STRIKE-LAST",
        "special_rules": [],
    },
    {
        "name": "Cyclic Shifts",
        "deployment": "Diagonal corner deployment",
        "deployment_map_url": "/static/battle-plans/aos-cyclic-shifts.png",
        "objectives": [
            {
                "name": "Diagonal Row",
                "location": "6 objectives in diagonal rows, 3 per player's side",
            },
        ],
        "scoring": "5 VP if you control at least 1 objective. 3 VP if you control 2 or more objectives. 2 VP if you control more objectives than opponent.",
        "underdog_ability": "Unpredictable Evolution: Pick a pair of objectives - they cannot be controlled this battle round",
        "special_rules": [],
    },
    {
        "name": "Surge of Slaughter",
        "deployment": "Long edge deployment",
        "deployment_map_url": "/static/battle-plans/aos-surge-of-slaughter.png",
        "objectives": [
            {"name": "Central Heartwood", "location": "Center"},
            {
                "name": "4 Corner Objectives",
                "location": "Near each corner of battlefield",
            },
        ],
        "scoring": "5 VP if you control at least 1 objective. 3 VP if you control any pairs of objectives. 2 VP if you control more objectives than opponent.",
        "underdog_ability": "Defence of the Realm: Pick a pair of objectives - add 1 to Rend for units contesting them",
        "special_rules": [],
    },
    {
        "name": "Linked Ley Lines",
        "deployment": "Long edge deployment",
        "deployment_map_url": "/static/battle-plans/aos-linked-ley-lines.png",
        "objectives": [
            {
                "name": "Ley Line Network",
                "location": "5 objectives in diamond formation",
            },
        ],
        "scoring": "3 VP if you control at least 1 objective. 3 VP if you control 2+ objectives. 2 VP if you control any pairs. 2 VP if you control all objectives on a linked ley line.",
        "underdog_ability": "Rooted in the Realm: Anti-MANIFESTATION(+1 Rend) on linked ley lines. MANIFESTATIONS have STRIKE-FIRST",
        "special_rules": [],
    },
    {
        "name": "Noxious Nexus",
        "deployment": "Quadrant deployment",
        "deployment_map_url": "/static/battle-plans/aos-noxious-nexus.png",
        "objectives": [
            {"name": "3 Nexus Points", "location": "Spread across battlefield"},
        ],
        "scoring": "Cannot control in round 1. 5 VP for Oakenbrow, 3 VP for Gnarlroot, 2 VP for Heartwood. Bonus 10 VP at end of battle if you control Heartwood.",
        "underdog_ability": "Caustic Sap: Pick an objective - roll D3 for each unit contesting it, on 2+ inflict that many mortal wounds (D6 for Heartwood)",
        "special_rules": [],
    },
    {
        "name": "The Liferoots",
        "deployment": "Diagonal corner deployment",
        "deployment_map_url": "/static/battle-plans/aos-the-liferoots.png",
        "objectives": [
            {"name": "2 Liferoot Markers", "location": 'On diagonal, 24" apart'},
        ],
        "scoring": "5 VP if you control at least 1 objective. 3 VP if you control both objectives. 2 VP if you have more liferoot points. (Liferoot points: 1 per terrain feature controlled)",
        "underdog_ability": "Life Begets Life: Return 1 slain model to a unit within 1\" of terrain",
        "special_rules": [],
    },
    {
        "name": "Bountiful Equinox",
        "deployment": "Long edge deployment",
        "deployment_map_url": "/static/battle-plans/aos-bountiful-equinox.png",
        "objectives": [
            {
                "name": "5 Objective Spread",
                "location": "Distributed across battlefield",
            },
        ],
        "scoring": "5 VP if you control at least 1 objective. 3 VP if you control 2+ objectives. 2 VP if you control at least 1 Oakenbrow, 1 Gnarlroot, and 1 Heartwood.",
        "underdog_ability": "Rejuvenating Bloom: Pick an objective - Heal(3) each unit contesting it",
        "special_rules": [],
    },
    {
        "name": "Lifecycle",
        "deployment": "Long edge deployment",
        "deployment_map_url": "/static/battle-plans/aos-lifecycle.png",
        "objectives": [
            {
                "name": "4 Lifecycle Objectives",
                "location": "Symmetrical placement across battlefield",
            },
        ],
        "scoring": "4 VP if you control at least 1 objective. 2 VP if you control more objectives. Round 1 only: 4 VP for both Oakenbrow and Gnarlroot. Otherwise: 2 VP for primary, 1 VP per secondary.",
        "underdog_ability": "Lifecycle: Pick which objective starts as primary. Rotates each round. Primary worth 2 VP, adjacent secondaries worth 1 VP each",
        "special_rules": [],
    },
    {
        "name": "Creeping Corruption",
        "deployment": "Long edge deployment",
        "deployment_map_url": "/static/battle-plans/aos-creeping-corruption.png",
        "objectives": [
            {
                "name": "6 Objective Grid",
                "location": "Evenly spaced across battlefield",
            },
        ],
        "scoring": "5 VP if you control at least 1 objective. 3 VP if you control 2+ objectives. 2 VP if you control more objectives than opponent.",
        "underdog_ability": "Pulsing Life Energies: Draw line between 2 objectives - Propagation (+1 to casts/chants) OR Corruption (D3 mortal wounds to units crossed)",
        "special_rules": [],
    },
    {
        "name": "Grasp of Thorns",
        "deployment": "Quadrant deployment",
        "deployment_map_url": "/static/battle-plans/aos-grasp-of-thorns.png",
        "objectives": [
            {"name": "4 Thorn Objectives", "location": "One in each table quarter"},
        ],
        "scoring": "5 VP if you control at least 1 objective. 3 VP if you control 2+ objectives. 2 VP if you control more objectives than opponent.",
        "underdog_ability": "Carnivorous Flora: Pick an objective - roll for each contesting unit, on 3+ models in control zone are entangled (can't move out or be removed)",
        "special_rules": [],
    },
]


def generate_aos_battle_plan() -> BattlePlan:
    """Generate randomized Age of Sigmar Matched Play battle plan from General's Handbook 2025-2026"""

    battle_plan = random.choice(AOS_BATTLE_PLANS)

    # Extract objective names for display
    objective_list = []
    if "objectives" in battle_plan and isinstance(battle_plan["objectives"], list):
        objective_list = [
            obj.get("name", "") for obj in battle_plan["objectives"] if "name" in obj
        ]

    # Build special rules list
    special_rules = battle_plan.get("special_rules", [])
    special_rules.extend(
        [
            "Matched Play format: 2000 points",
            "General's Handbook 2025-2026",
            f"Underdog Ability: {battle_plan.get('underdog_ability', 'Special ability for player behind on VP')}",
        ]
    )

    return BattlePlan(
        name=battle_plan["name"],
        game_system=GameSystem.AOS,
        deployment=DeploymentType.FRONTAL_ASSAULT,  # Placeholder - actual deployment varies by mission
        deployment_description=battle_plan.get("deployment", "Standard deployment"),
        primary_objective=battle_plan.get(
            "scoring", "Control objectives for victory points"
        ),
        secondary_objectives=objective_list,
        victory_conditions="Player with most Victory Points at end of 5 battle rounds wins. VP scored from controlling objectives per mission rules.",
        battle_tactics=None,
        turn_limit=5,
        special_rules=special_rules,
    )


# ═══════════════════════════════════════════════
# WARHAMMER 40,000 10TH EDITION
# ═══════════════════════════════════════════════

W40K_DEPLOYMENTS = {
    DeploymentType.DAWN_OF_WAR: {
        "name": "Dawn of War",
        "description": "Standard battle lines on opposite short table edges.",
        "zones": 'Deploy wholly within 6" of your short table edge',
    },
    DeploymentType.SEARCH_AND_DESTROY: {
        "name": "Search and Destroy",
        "description": "Diagonal corner deployment zones.",
        "zones": 'Deploy in opposite diagonal corners within 6" of corner',
    },
    DeploymentType.SWEEPING_ENGAGEMENT: {
        "name": "Sweeping Engagement",
        "description": "Offset deployment on long table edges.",
        "zones": 'Deploy on long edges, offset 12" from corners',
    },
    DeploymentType.CRUCIBLE_OF_BATTLE: {
        "name": "Crucible of Battle",
        "description": 'Center circle deployment with 24" gap.',
        "zones": 'Deploy in 9" circles, 24" apart, along center line',
    },
}

W40K_PRIMARY_MISSIONS = [
    "Take and Hold - Control objective markers for VP each command phase",
    "The Ritual - Perform actions on objective markers",
    "Purge the Foe - Destroy enemy units for VP",
    "Vital Ground - Control objectives in no man's land",
    "Scorched Earth - Destroy terrain objectives",
]

W40K_SECONDARY_OBJECTIVES = [
    "Assassinate - Destroy enemy characters",
    "Bring It Down - Destroy enemy vehicles/monsters",
    "Behind Enemy Lines - Have units in enemy deployment zone",
    "First Strike - Destroy units in first battle round",
    "Overwhelming Force - Destroy units with specific weapon types",
]


def generate_40k_battle_plan() -> BattlePlan:
    """Generate randomized Warhammer 40,000 battle plan"""

    deployment_type = random.choice(list(W40K_DEPLOYMENTS.keys()))
    deployment_info = W40K_DEPLOYMENTS[deployment_type]

    primary = random.choice(W40K_PRIMARY_MISSIONS)
    secondaries = random.sample(W40K_SECONDARY_OBJECTIVES, 3)

    return BattlePlan(
        name=f"40k 10th Edition - {deployment_info['name']}",
        game_system=GameSystem.WARHAMMER_40K,
        deployment=deployment_type,
        deployment_description=f"{deployment_info['description']}\n{deployment_info['zones']}",
        primary_objective=primary,
        secondary_objectives=secondaries,
        victory_conditions="Score VP from primary mission and secondary objectives. Most VP at end of Round 5 wins.",
        turn_limit=5,
        special_rules=[
            "Matched Play: 2000 points",
            "Roll for first turn after deployment",
            "Score primary objective each command phase",
        ],
    )


# ═══════════════════════════════════════════════
# THE OLD WORLD
# ═══════════════════════════════════════════════

OLD_WORLD_DEPLOYMENTS = {
    DeploymentType.FRONTAL_ASSAULT: {
        "name": "Pitched Battle",
        "description": "Classic battle lines facing each other across the field.",
        "zones": 'Deploy within 12" of your table edge',
    },
    DeploymentType.ENCIRCLE: {
        "name": "Corner Deployment",
        "description": "Armies deploy in opposite corners.",
        "zones": 'Deploy in 18" square in your corner',
    },
    DeploymentType.HAMMER_AND_ANVIL: {
        "name": "Meeting Engagement",
        "description": "Short edge deployment.",
        "zones": 'Deploy within 12" of short table edge',
    },
}

OLD_WORLD_SCENARIOS = [
    "Pitched Battle - Destroy enemy army",
    "Capture the Flags - Control battlefield standards",
    "Breakthrough - Get units to enemy table edge",
    "Hold the Ground - Control central terrain",
    "Blood and Glory - Break enemy army morale",
]


def generate_old_world_battle_plan() -> BattlePlan:
    """Generate randomized The Old World battle plan"""

    deployment_type = random.choice(list(OLD_WORLD_DEPLOYMENTS.keys()))
    deployment_info = OLD_WORLD_DEPLOYMENTS[deployment_type]

    scenario = random.choice(OLD_WORLD_SCENARIOS)

    return BattlePlan(
        name=f"The Old World - {deployment_info['name']}",
        game_system=GameSystem.OLD_WORLD,
        deployment=deployment_type,
        deployment_description=f"{deployment_info['description']}\n{deployment_info['zones']}",
        primary_objective=scenario,
        secondary_objectives=["Slay the General", "Break Their Lines"],
        victory_conditions="Complete primary scenario objective. Additional VP from breaking units and killing characters.",
        turn_limit=6,
        special_rules=[
            "2000 points standard",
            "Random game length: Roll at end of turn 6",
            "Leadership tests for broken units",
        ],
    )


# ═══════════════════════════════════════════════
# MAIN RANDOMIZER FUNCTION
# ═══════════════════════════════════════════════


def generate_battle_plan(game_system: GameSystem) -> BattlePlan:
    """
    Generate a random battle plan for the specified game system

    Args:
        game_system: Which game system to generate plan for

    Returns:
        Complete BattlePlan with all configuration details
    """
    generators = {
        GameSystem.AOS: generate_aos_battle_plan,
        GameSystem.WARHAMMER_40K: generate_40k_battle_plan,
        GameSystem.OLD_WORLD: generate_old_world_battle_plan,
    }

    generator = generators.get(game_system)
    if not generator:
        raise ValueError(f"Unsupported game system: {game_system}")

    return generator()


def format_battle_plan(plan: BattlePlan) -> str:
    """Format battle plan as readable text"""
    output = []
    output.append(f"═══════════════════════════════════════")
    output.append(f"  {plan.name}")
    output.append(f"═══════════════════════════════════════\n")

    output.append(f"DEPLOYMENT: {plan.deployment.value}")
    output.append(f"{plan.deployment_description}\n")

    output.append(f"PRIMARY OBJECTIVE:")
    output.append(f"  {plan.primary_objective}\n")

    output.append(f"SECONDARY OBJECTIVES:")
    for i, obj in enumerate(plan.secondary_objectives, 1):
        output.append(f"  {i}. {obj}")
    output.append("")

    if plan.battle_tactics:
        output.append(f"BATTLE TACTICS AVAILABLE:")
        for tactic in plan.battle_tactics:
            output.append(f"  • {tactic}")
        output.append("")

    output.append(f"VICTORY CONDITIONS:")
    output.append(f"  {plan.victory_conditions}\n")

    if plan.special_rules:
        output.append(f"SPECIAL RULES:")
        for rule in plan.special_rules:
            output.append(f"  • {rule}")
        output.append("")

    output.append(f"GAME LENGTH: {plan.turn_limit} rounds")
    output.append(f"═══════════════════════════════════════")

    return "\n".join(output)
