"""
Battle Plan Randomization Module

Generates random battle plans for AoS 4th Edition, 40k 10th Edition, and The Old World.
Follows official matched play formats including deployment zones, objectives, and victory conditions.
"""

import random
from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass


class GameSystem(str, Enum):
    """Supported game systems"""
    AOS = "age_of_sigmar"
    WARHAMMER_40K = "warhammer_40k"
    OLD_WORLD = "the_old_world"


class DeploymentType(str, Enum):
    """Standard deployment zone configurations"""
    # Age of Sigmar Spearhead deployments
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
# AGE OF SIGMAR 4TH EDITION - SPEARHEAD
# ═══════════════════════════════════════════════

AOS_DEPLOYMENTS = {
    DeploymentType.FRONTAL_ASSAULT: {
        "name": "Frontal Assault",
        "description": "Players deploy in opposite halves of the battlefield, divided by a line down the center. Standard battle lines 9\" from center.",
        "zones": "Player zones: 18\" from center line on your side"
    },
    DeploymentType.ENCIRCLE: {
        "name": "Encircle",
        "description": "Players deploy in opposite diagonal corners. Deployment zones are 12\" triangles in corners.",
        "zones": "Diagonal deployment: NW corner vs SE corner (or NE vs SW)"
    },
    DeploymentType.HAMMER_AND_ANVIL: {
        "name": "Hammer and Anvil",
        "description": "Players deploy on opposite short table edges. 9\" deployment zones from short edges.",
        "zones": "Deploy within 9\" of your short table edge"
    },
    DeploymentType.CLASH: {
        "name": "Clash",
        "description": "Both players deploy in 12\" circles 24\" apart in center of battlefield.",
        "zones": "12\" radius deployment circles, 24\" apart, centered on table"
    }
}

AOS_PRIMARY_OBJECTIVES = [
    "Control the Center - Hold the central objective marker",
    "Secure the Flanks - Control objective markers in left and right table quarters",
    "Domination - Control more objectives than your opponent at end of each turn",
    "Breakthrough - Control objectives in enemy territory",
    "King of the Hill - Hold central terrain feature for victory points"
]

AOS_SECONDARY_OBJECTIVES = [
    "Slay the Leader - Destroy enemy general",
    "Break Their Ranks - Destroy half of enemy's starting models",
    "Hold the Line - No enemies in your deployment zone at battle end",
    "Aggressive Expansion - Have units in all four table quarters",
    "Tactical Supremacy - Complete more battle tactics than opponent"
]

AOS_BATTLE_TACTICS = [
    "Fierce Conquerors - Control an objective you didn't control at start of turn",
    "Endless Legions - Return destroyed unit to battlefield",
    "Aggressive Expansion - Move a unit into enemy territory",
    "Unstoppable Advance - Charge with 3+ units this turn",
    "Magical Dominance - Successfully cast 3+ spells this turn",
    "Slaughter and Plunder - Destroy enemy unit and control objective",
    "Strategic Withdrawal - Fall back and still shoot/charge",
    "Hold or Die - Keep control of an objective all turn"
]


def generate_aos_battle_plan() -> BattlePlan:
    """Generate randomized Age of Sigmar Spearhead battle plan"""
    
    deployment_type = random.choice(list(AOS_DEPLOYMENTS.keys()))
    deployment_info = AOS_DEPLOYMENTS[deployment_type]
    
    primary = random.choice(AOS_PRIMARY_OBJECTIVES)
    
    # Select 2-3 random secondary objectives
    num_secondaries = random.randint(2, 3)
    secondaries = random.sample(AOS_SECONDARY_OBJECTIVES, num_secondaries)
    
    # Select battle tactics for the game
    battle_tactics = random.sample(AOS_BATTLE_TACTICS, 6)  # 6 tactics available per game
    
    return BattlePlan(
        name=f"AoS Spearhead - {deployment_info['name']}",
        game_system=GameSystem.AOS,
        deployment=deployment_type,
        deployment_description=f"{deployment_info['description']}\n{deployment_info['zones']}",
        primary_objective=primary,
        secondary_objectives=secondaries,
        victory_conditions="Score victory points from primary objective, secondary objectives, and completed battle tactics. Most VP at end of Round 5 wins.",
        battle_tactics=battle_tactics,
        turn_limit=5,
        special_rules=[
            "Spearhead format: 1000 points maximum",
            "First turn determined by priority roll",
            "Battle tactics chosen secretly each turn"
        ]
    )


# ═══════════════════════════════════════════════
# WARHAMMER 40,000 10TH EDITION
# ═══════════════════════════════════════════════

W40K_DEPLOYMENTS = {
    DeploymentType.DAWN_OF_WAR: {
        "name": "Dawn of War",
        "description": "Standard battle lines on opposite short table edges.",
        "zones": "Deploy wholly within 6\" of your short table edge"
    },
    DeploymentType.SEARCH_AND_DESTROY: {
        "name": "Search and Destroy",
        "description": "Diagonal corner deployment zones.",
        "zones": "Deploy in opposite diagonal corners within 6\" of corner"
    },
    DeploymentType.SWEEPING_ENGAGEMENT: {
        "name": "Sweeping Engagement",
        "description": "Offset deployment on long table edges.",
        "zones": "Deploy on long edges, offset 12\" from corners"
    },
    DeploymentType.CRUCIBLE_OF_BATTLE: {
        "name": "Crucible of Battle",
        "description": "Center circle deployment with 24\" gap.",
        "zones": "Deploy in 9\" circles, 24\" apart, along center line"
    }
}

W40K_PRIMARY_MISSIONS = [
    "Take and Hold - Control objective markers for VP each command phase",
    "The Ritual - Perform actions on objective markers",
    "Purge the Foe - Destroy enemy units for VP",
    "Vital Ground - Control objectives in no man's land",
    "Scorched Earth - Destroy terrain objectives"
]

W40K_SECONDARY_OBJECTIVES = [
    "Assassinate - Destroy enemy characters",
    "Bring It Down - Destroy enemy vehicles/monsters",
    "Behind Enemy Lines - Have units in enemy deployment zone",
    "First Strike - Destroy units in first battle round",
    "Overwhelming Force - Destroy units with specific weapon types"
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
            "Score primary objective each command phase"
        ]
    )


# ═══════════════════════════════════════════════
# THE OLD WORLD
# ═══════════════════════════════════════════════

OLD_WORLD_DEPLOYMENTS = {
    DeploymentType.FRONTAL_ASSAULT: {
        "name": "Pitched Battle",
        "description": "Classic battle lines facing each other across the field.",
        "zones": "Deploy within 12\" of your table edge"
    },
    DeploymentType.ENCIRCLE: {
        "name": "Corner Deployment",
        "description": "Armies deploy in opposite corners.",
        "zones": "Deploy in 18\" square in your corner"
    },
    DeploymentType.HAMMER_AND_ANVIL: {
        "name": "Meeting Engagement",
        "description": "Short edge deployment.",
        "zones": "Deploy within 12\" of short table edge"
    }
}

OLD_WORLD_SCENARIOS = [
    "Pitched Battle - Destroy enemy army",
    "Capture the Flags - Control battlefield standards",
    "Breakthrough - Get units to enemy table edge",
    "Hold the Ground - Control central terrain",
    "Blood and Glory - Break enemy army morale"
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
            "Leadership tests for broken units"
        ]
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
        GameSystem.OLD_WORLD: generate_old_world_battle_plan
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
