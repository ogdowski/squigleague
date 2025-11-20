"""
Squire API Routes - Battle Plan Randomization Endpoints

Provides REST API for generating random battle plans for AoS, 40k, and The Old World
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

from squire.battle_plans import (
    generate_battle_plan,
    GameSystem,
    BattlePlan,
    DeploymentType
)


router = APIRouter(prefix="/api/squire", tags=["squire"])


# ═══════════════════════════════════════════════
# RESPONSE MODELS
# ═══════════════════════════════════════════════

class BattlePlanResponse(BaseModel):
    """Battle plan API response"""
    name: str
    game_system: str
    deployment: str
    deployment_description: str
    primary_objective: str
    secondary_objectives: List[str]
    victory_conditions: str
    turn_limit: int
    special_rules: Optional[List[str]] = None
    battle_tactics: Optional[List[str]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "AoS Spearhead - Frontal Assault",
                "game_system": "age_of_sigmar",
                "deployment": "frontal_assault",
                "deployment_description": "Players deploy in opposite halves...",
                "primary_objective": "Control the Center",
                "secondary_objectives": ["Slay the Leader", "Hold the Line"],
                "victory_conditions": "Score victory points from objectives...",
                "turn_limit": 5,
                "special_rules": ["Spearhead format: 1000 points"],
                "battle_tactics": ["Fierce Conquerors", "Unstoppable Advance"]
            }
        }


class BattlePlanSummary(BaseModel):
    """Condensed battle plan summary"""
    name: str
    deployment: str
    primary_objective: str
    

class SystemInfoResponse(BaseModel):
    """Supported game systems and their deployments"""
    game_system: str
    deployments: List[str]
    description: str


# ═══════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════

def battle_plan_to_response(plan: BattlePlan) -> BattlePlanResponse:
    """Convert BattlePlan dataclass to API response model"""
    return BattlePlanResponse(
        name=plan.name,
        game_system=plan.game_system.value,
        deployment=plan.deployment.value,
        deployment_description=plan.deployment_description,
        primary_objective=plan.primary_objective,
        secondary_objectives=plan.secondary_objectives,
        victory_conditions=plan.victory_conditions,
        turn_limit=plan.turn_limit,
        special_rules=plan.special_rules,
        battle_tactics=plan.battle_tactics
    )


# ═══════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════

@router.get("/battle-plan/random", response_model=BattlePlanResponse)
async def get_random_battle_plan(
    system: str = Query(
        default="age_of_sigmar",
        description="Game system: age_of_sigmar, warhammer_40k, or the_old_world"
    )
):
    """
    Generate a random battle plan for the specified game system
    
    Returns complete battle plan with deployment, objectives, and victory conditions
    """
    try:
        game_system = GameSystem(system)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid game system. Must be: age_of_sigmar, warhammer_40k, or the_old_world"
        )
    
    plan = generate_battle_plan(game_system)
    return battle_plan_to_response(plan)


@router.get("/battle-plan/multiple", response_model=List[BattlePlanResponse])
async def get_multiple_battle_plans(
    system: str = Query(
        default="age_of_sigmar",
        description="Game system: age_of_sigmar, warhammer_40k, or the_old_world"
    ),
    count: int = Query(
        default=3,
        ge=1,
        le=10,
        description="Number of battle plans to generate (1-10)"
    )
):
    """
    Generate multiple random battle plans for tournament planning
    
    Useful for pre-generating tournament rounds or giving players options
    """
    try:
        game_system = GameSystem(system)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid game system. Must be: age_of_sigmar, warhammer_40k, or the_old_world"
        )
    
    plans = [generate_battle_plan(game_system) for _ in range(count)]
    return [battle_plan_to_response(plan) for plan in plans]


@router.get("/systems", response_model=List[SystemInfoResponse])
async def get_supported_systems():
    """
    List all supported game systems and their available deployments
    """
    from squire.battle_plans import AOS_DEPLOYMENTS, W40K_DEPLOYMENTS, OLD_WORLD_DEPLOYMENTS
    
    systems = [
        SystemInfoResponse(
            game_system="age_of_sigmar",
            deployments=[d.value for d in AOS_DEPLOYMENTS.keys()],
            description="Age of Sigmar 4th Edition Spearhead format"
        ),
        SystemInfoResponse(
            game_system="warhammer_40k",
            deployments=[d.value for d in W40K_DEPLOYMENTS.keys()],
            description="Warhammer 40,000 10th Edition matched play"
        ),
        SystemInfoResponse(
            game_system="the_old_world",
            deployments=[d.value for d in OLD_WORLD_DEPLOYMENTS.keys()],
            description="Warhammer: The Old World legacy battles"
        )
    ]
    
    return systems


@router.get("/health")
async def squire_health():
    """Health check for Squire module"""
    return {
        "module": "squire",
        "status": "operational",
        "features": ["battle_plans"],
        "version": "0.1.0"
    }
