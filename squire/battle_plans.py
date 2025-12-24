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


# ═══════════════════════════════════════════════
# AGE OF SIGMAR 4TH EDITION - MATCHED PLAY
# General's Handbook 2025-2026
# ═══════════════════════════════════════════════

AOS_BATTLE_PLANS = [
    {
        "name": "Passing Seasons",
        "deployment": "Long edge deployment",
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
        "scoring": "Alternating turns: even turns score Gnarlroot objectives (5 VP each), odd turns score Oakenbrow objectives (5 VP each)",
        "underdog_ability": "If behind on VP, can choose which objective type scores this turn (Gnarlroot or Oakenbrow)",
        "special_rules": ["Seasonal rotation mechanic", "4 objectives total"],
    },
    {
        "name": "Paths of the Fey",
        "deployment": "Long edge deployment",
        "objectives": [
            {"name": "Central Heartwood", "location": "Center of battlefield"},
            {"name": "Gnarlroot", "location": '12" from center toward each long edge'},
            {"name": "Oakenbrow", "location": '12" from center toward each long edge'},
            {
                "name": "Winterleaf",
                "location": '24" from center on battlefield quarters',
            },
        ],
        "scoring": "Central objective: 5 VP. Other objectives: 3 VP each. End of turn scoring.",
        "underdog_ability": 'Teleport one unit wholly within 6" of an objective to within 6" of another objective',
        "special_rules": ["5 objectives total", "Fey teleportation mechanic"],
    },
    {
        "name": "Roiling Roots",
        "deployment": "Diagonal corner deployment",
        "objectives": [
            {
                "name": "Diagonal Row 1",
                "location": "6 objectives in diagonal line across battlefield",
            },
        ],
        "scoring": "Control objectives: 3 VP each. Bonus 2 VP if you control more than opponent.",
        "underdog_ability": "Units contesting objectives you control cause enemies to strike last",
        "special_rules": [
            "6 objectives in diagonal formation",
            "Strike-last defensive ability",
        ],
    },
    {
        "name": "Cyclic Shifts",
        "deployment": "Diagonal corner deployment",
        "objectives": [
            {
                "name": "Diagonal Row",
                "location": "6 objectives in diagonal rows, 3 per player's side",
            },
        ],
        "scoring": "3 VP per objective controlled. At end of each battle round, remove the objective furthest from the center.",
        "underdog_ability": "Choose which objective is removed instead of automatic removal",
        "special_rules": [
            "6 objectives diminishing to 1",
            "Shrinking battlefield mechanic",
        ],
    },
    {
        "name": "Surge of Slaughter",
        "deployment": "Long edge deployment",
        "objectives": [
            {"name": "Central Heartwood", "location": "Center"},
            {
                "name": "4 Corner Objectives",
                "location": "Near each corner of battlefield",
            },
        ],
        "scoring": "Central: 5 VP, corners: 3 VP each",
        "underdog_ability": "All your units gain +1 Rend to melee weapons",
        "special_rules": ["5 objectives total", "Aggressive combat bonus for underdog"],
    },
    {
        "name": "Linked Ley Lines",
        "deployment": "Long edge deployment",
        "objectives": [
            {
                "name": "Ley Line Network",
                "location": "5 objectives in diamond formation",
            },
        ],
        "scoring": "3 VP per objective. Bonus 5 VP if you control 3+ linked objectives.",
        "underdog_ability": "Bonuses to manifestations and prayers near controlled objectives",
        "special_rules": [
            "5 objectives",
            "Linked objective bonuses",
            "Magic/prayer enhancement",
        ],
    },
    {
        "name": "Noxious Nexus",
        "deployment": "Quadrant deployment",
        "objectives": [
            {"name": "3 Nexus Points", "location": "Spread across battlefield"},
        ],
        "scoring": "5 VP per objective controlled. Bonus 10 VP if you control all objectives at end of any turn.",
        "underdog_ability": 'Deal D3 mortal wounds to enemy units within 6" of objectives you control',
        "special_rules": [
            "3 objectives",
            "Mortal wound damage ability",
            "All-or-nothing bonus",
        ],
    },
    {
        "name": "The Liferoots",
        "deployment": "Diagonal corner deployment",
        "objectives": [
            {"name": "2 Liferoot Markers", "location": 'On diagonal, 24" apart'},
        ],
        "scoring": "10 VP per objective controlled at end of battle round",
        "underdog_ability": 'Return D3 slain models to a friendly unit within 6" of objective you control',
        "special_rules": [
            "2 objectives",
            "Diagonal obscuring terrain",
            "Model resurrection mechanic",
        ],
    },
    {
        "name": "Bountiful Equinox",
        "deployment": "Long edge deployment",
        "objectives": [
            {
                "name": "5 Objective Spread",
                "location": "Distributed across battlefield",
            },
        ],
        "scoring": "3 VP per objective. Bonus VP for controlling specific objective combinations.",
        "underdog_ability": 'Heal D3 wounds on a friendly monster within 6" of objective you control',
        "special_rules": [
            "5 objectives",
            "Combination scoring bonuses",
            "Healing mechanic",
        ],
    },
    {
        "name": "Lifecycle",
        "deployment": "Long edge deployment",
        "objectives": [
            {
                "name": "4 Lifecycle Objectives",
                "location": "Symmetrical placement across battlefield",
            },
        ],
        "scoring": "One objective is primary each turn (5 VP), others are secondary (2 VP). Primary objective rotates clockwise.",
        "underdog_ability": "Choose direction of primary objective rotation (clockwise or counter-clockwise)",
        "special_rules": ["4 objectives", "Rotating primary objective mechanic"],
    },
    {
        "name": "Creeping Corruption",
        "deployment": "Long edge deployment",
        "objectives": [
            {
                "name": "6 Objective Grid",
                "location": "Evenly spaced across battlefield",
            },
        ],
        "scoring": "2 VP per objective. Draw lines between controlled objectives - each line through enemy territory: +1 VP.",
        "underdog_ability": "Corrupt an objective: propagate control to adjacent objective",
        "special_rules": [
            "6 objectives",
            "Line-drawing propagation mechanic",
            "Territory corruption",
        ],
    },
    {
        "name": "Grasp of Thorns",
        "deployment": "Quadrant deployment",
        "objectives": [
            {"name": "4 Thorn Objectives", "location": "One in each table quarter"},
        ],
        "scoring": "5 VP per objective controlled",
        "underdog_ability": 'Entangle enemy units within 6" of objectives you control - they cannot make normal moves',
        "special_rules": [
            "4 objectives",
            "Movement restriction mechanic",
            "Entanglement effect",
        ],
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
# WARHAMMER 40,000 10TH EDITION - LEVIATHAN MISSION DECK
# Fixed 9 missions from matched play
# ═══════════════════════════════════════════════

LEVIATHAN_MISSIONS = [
    {
        "name": "Only War",
        "deployment": DeploymentType.DAWN_OF_WAR,
        "primary": "Take and Hold - Control objectives for VP each command phase",
        "rule": "5 objective markers. Score 5 VP per marker controlled at end of command phase.",
    },
    {
        "name": "Priority Targets",
        "deployment": DeploymentType.SEARCH_AND_DESTROY,
        "primary": "Destroy Priority Targets - Eliminate marked enemy units",
        "rule": "Mark 1 enemy unit as priority target each turn. Score VP for destroying marked units.",
    },
    {
        "name": "Purge the Foe",
        "deployment": DeploymentType.SWEEPING_ENGAGEMENT,
        "primary": "Destruction - Score VP for each enemy unit destroyed",
        "rule": "1 VP per enemy unit destroyed. Additional VP for destroying units in enemy deployment zone.",
    },
    {
        "name": "Scorched Earth",
        "deployment": DeploymentType.CRUCIBLE_OF_BATTLE,
        "primary": "Raze Objectives - Destroy objective markers",
        "rule": "Perform action to raze objectives. Score VP for each objective destroyed.",
    },
    {
        "name": "Supply Drop",
        "deployment": DeploymentType.DAWN_OF_WAR,
        "primary": "Secure Supply Caches - Control objectives in no man's land",
        "rule": "3 objectives in no man's land. Control for 5 VP each at end of turn.",
    },
    {
        "name": "Vital Ground",
        "deployment": DeploymentType.SEARCH_AND_DESTROY,
        "primary": "Hold the Center - Control central objectives",
        "rule": "Control objectives within 12\" of center. Progressive scoring each turn.",
    },
    {
        "name": "Deploy Servo-Skulls",
        "deployment": DeploymentType.SWEEPING_ENGAGEMENT,
        "primary": "Area Denial - Place servo-skulls on objectives",
        "rule": "Perform actions to place servo-skulls. Score VP and deny enemy objectives.",
    },
    {
        "name": "Sites of Power",
        "deployment": DeploymentType.CRUCIBLE_OF_BATTLE,
        "primary": "Mystical Sites - Control power sites for cumulative VP",
        "rule": "4 sites of power. Cumulative scoring - more controlled = higher VP.",
    },
    {
        "name": "The Ritual",
        "deployment": DeploymentType.DAWN_OF_WAR,
        "primary": "Complete the Ritual - Perform actions on objectives",
        "rule": "Perform ritual actions on 3+ objectives. Score VP for completed rituals.",
    },
]


def generate_40k_battle_plan() -> BattlePlan:
    """Generate Warhammer 40,000 battle plan from Leviathan Mission Deck"""

    # Randomly select one of the 9 Leviathan missions
    mission = random.choice(LEVIATHAN_MISSIONS)

    deployment_descriptions = {
        DeploymentType.DAWN_OF_WAR: 'Standard battle lines on opposite short table edges. Deploy wholly within 6" of your short table edge.',
        DeploymentType.SEARCH_AND_DESTROY: 'Diagonal corner deployment zones. Deploy in opposite diagonal corners within 6" of corner.',
        DeploymentType.SWEEPING_ENGAGEMENT: 'Offset deployment on long table edges. Deploy on long edges, offset 12" from corners.',
        DeploymentType.CRUCIBLE_OF_BATTLE: 'Center circle deployment with 24" gap. Deploy in 9" circles, 24" apart, along center line.',
    }

    return BattlePlan(
        name=f"{mission['name']}",
        game_system=GameSystem.WARHAMMER_40K,
        deployment=mission["deployment"],
        deployment_description=deployment_descriptions[mission["deployment"]],
        primary_objective=mission["primary"],
        secondary_objectives=[
            "Select 3 secondary objectives from your faction's list",
            "Score VP based on secondary objective conditions",
        ],
        victory_conditions=f"{mission['rule']}\nSecondaries add bonus VP. Most VP at end of Round 5 wins.",
        turn_limit=5,
        special_rules=[
            "Matched Play: 2000 points",
            "Leviathan Mission Deck",
            "Choose 3 secondary objectives before deployment",
        ],
    )


# ═══════════════════════════════════════════════
# THE OLD WORLD - CORE SCENARIOS
# 6 official scenarios from the rulebook
# ═══════════════════════════════════════════════

OLD_WORLD_SCENARIOS = [
    {
        "name": "Pitched Battle",
        "deployment": DeploymentType.FRONTAL_ASSAULT,
        "objective": "Destroy the enemy army and claim victory through superior tactics",
        "rule": "Score VP for enemy units destroyed and broken. Defeat enemy general for bonus VP.",
        "deployment_desc": 'Classic battle lines. Deploy within 12" of your table edge.',
    },
    {
        "name": "Blood and Glory",
        "deployment": DeploymentType.FRONTAL_ASSAULT,
        "objective": "Break enemy army morale by destroying their banners and generals",
        "rule": "Track Fortitude points. Destroy enemy banners and characters to reduce enemy Fortitude. Army breaks when Fortitude reaches 0.",
        "deployment_desc": 'Face each other across the field. Deploy within 12" of your table edge.',
    },
    {
        "name": "Meeting Engagement",
        "deployment": DeploymentType.HAMMER_AND_ANVIL,
        "objective": "Seize the center and drive back the enemy",
        "rule": "Control the center of the battlefield. Score VP for units within 12\" of center at end of turn.",
        "deployment_desc": 'Short edge deployment. Deploy within 12" of short table edge. First turn determined by roll-off.',
    },
    {
        "name": "Breakthrough",
        "deployment": DeploymentType.FRONTAL_ASSAULT,
        "objective": "Break through enemy lines and reach their deployment zone",
        "rule": "Score VP for friendly units wholly within enemy deployment zone at end of game.",
        "deployment_desc": 'Standard deployment. Deploy within 12" of your table edge.',
    },
    {
        "name": "Battle for the Pass",
        "deployment": DeploymentType.HAMMER_AND_ANVIL,
        "objective": "Control the narrow pass through terrain",
        "rule": "Place terrain to create narrow pass down center. Control the pass for VP each turn.",
        "deployment_desc": 'Deploy on short edges. Terrain creates central corridor. Deploy within 12" of short edge.',
    },
    {
        "name": "Dawn Assault",
        "deployment": DeploymentType.ENCIRCLE,
        "objective": "Catch the enemy off-guard and destroy them before they can organize",
        "rule": "Attacker deploys first and takes first turn. Defender reserves half army. Score VP for destroying enemy units.",
        "deployment_desc": 'Diagonal corners. Attacker in one corner, defender in opposite. Defender brings reserves from table edge.',
    },
]


def generate_old_world_battle_plan() -> BattlePlan:
    """Generate The Old World battle plan from core scenarios"""

    # Randomly select one of the 6 core scenarios
    scenario = random.choice(OLD_WORLD_SCENARIOS)

    return BattlePlan(
        name=scenario["name"],
        game_system=GameSystem.OLD_WORLD,
        deployment=scenario["deployment"],
        deployment_description=scenario["deployment_desc"],
        primary_objective=scenario["objective"],
        secondary_objectives=["Slay the General", "Break Their Lines", "Capture Standards"],
        victory_conditions=scenario["rule"],
        turn_limit=6,
        special_rules=[
            "2000 points standard",
            "Random game length: Roll at end of turn 6",
            "Leadership tests for broken units",
            "Pursue fleeing enemies off the table",
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
