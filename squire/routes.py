"""
Squire API Routes - Battle Plan Randomization Endpoints

Provides REST API for generating random battle plans for AoS, 40k, and The Old World
"""

from enum import Enum
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from squire.battle_plans import (
    BattlePlan,
    DeploymentType,
    GameSystem,
    generate_battle_plan,
)
from squire.matchup import create_matchup, get_matchup, submit_list

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
                "name": "Grasp of Thorns",
                "game_system": "age_of_sigmar",
                "deployment": "frontal_assault",
                "deployment_description": "Quadrant deployment",
                "primary_objective": "5 VP per objective controlled",
                "secondary_objectives": [
                    "Gnarlroot 1",
                    "Oakenbrow 1",
                    "Winterleaf 1",
                    "Heartwood 1",
                ],
                "victory_conditions": "Player with most Victory Points at end of 5 battle rounds wins. VP scored from controlling objectives per mission rules.",
                "turn_limit": 5,
                "special_rules": [
                    "Matched Play format: 2000 points",
                    "General's Handbook 2025-2026",
                    'Underdog Ability: Entangle enemy units within 6" of objectives you control - they cannot make normal moves',
                ],
                "battle_tactics": None,
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


class MatchupCreateRequest(BaseModel):
    """Request to create a new matchup"""

    game_system: str = Field(
        ..., description="Game system: age_of_sigmar, warhammer_40k, or the_old_world"
    )


class MatchupCreateResponse(BaseModel):
    """Response after creating matchup"""

    matchup_id: str
    game_system: str
    share_url: str


class ListSubmitRequest(BaseModel):
    """Request to submit army list to matchup"""

    player_name: str = Field(..., min_length=1, max_length=100)
    army_list: str = Field(..., min_length=10)


class MatchupPlayerResponse(BaseModel):
    """Player information in matchup"""

    name: str
    army_list: str
    submitted_at: str


class MatchupResponse(BaseModel):
    """Full matchup details"""

    matchup_id: str
    game_system: str
    created_at: str
    player1: Optional[MatchupPlayerResponse] = None
    player2: Optional[MatchupPlayerResponse] = None
    battle_plan: Optional[BattlePlanResponse] = None
    is_complete: bool
    waiting_count: int


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
        battle_tactics=plan.battle_tactics,
    )


# ═══════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════


@router.get("/battle-plan/random", response_model=BattlePlanResponse)
async def get_random_battle_plan(
    system: str = Query(
        default="age_of_sigmar",
        description="Game system: age_of_sigmar, warhammer_40k, or the_old_world",
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
            detail=f"Invalid game system. Must be: age_of_sigmar, warhammer_40k, or the_old_world",
        )

    plan = generate_battle_plan(game_system)
    return battle_plan_to_response(plan)


@router.get("/battle-plan/multiple", response_model=List[BattlePlanResponse])
async def get_multiple_battle_plans(
    system: str = Query(
        default="age_of_sigmar",
        description="Game system: age_of_sigmar, warhammer_40k, or the_old_world",
    ),
    count: int = Query(
        default=3, ge=1, le=10, description="Number of battle plans to generate (1-10)"
    ),
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
            detail=f"Invalid game system. Must be: age_of_sigmar, warhammer_40k, or the_old_world",
        )

    plans = [generate_battle_plan(game_system) for _ in range(count)]
    return [battle_plan_to_response(plan) for plan in plans]


@router.get("/systems", response_model=List[SystemInfoResponse])
async def get_supported_systems():
    """
    List all supported game systems and their available deployments
    """
    from squire.battle_plans import (
        AOS_DEPLOYMENTS,
        OLD_WORLD_DEPLOYMENTS,
        W40K_DEPLOYMENTS,
    )

    systems = [
        SystemInfoResponse(
            game_system="age_of_sigmar",
            deployments=[d.value for d in AOS_DEPLOYMENTS.keys()],
            description="Age of Sigmar 4th Edition Matched Play - General's Handbook 2025-2026",
        ),
        SystemInfoResponse(
            game_system="warhammer_40k",
            deployments=[d.value for d in W40K_DEPLOYMENTS.keys()],
            description="Warhammer 40,000 10th Edition matched play",
        ),
        SystemInfoResponse(
            game_system="the_old_world",
            deployments=[d.value for d in OLD_WORLD_DEPLOYMENTS.keys()],
            description="Warhammer: The Old World legacy battles",
        ),
    ]

    return systems


# ═══════════════════════════════════════════════
# MATCHUP ENDPOINTS
# ═══════════════════════════════════════════════


@router.post("/matchup/create", response_model=MatchupCreateResponse)
async def create_new_matchup(request: MatchupCreateRequest):
    """
    Create a new matchup for exchanging lists and generating battle plan

    Args:
        request: Matchup creation request with game system

    Returns:
        Matchup ID and share URL
    """
    # Validate game system
    try:
        game_system = GameSystem(request.game_system)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid game system: {request.game_system}. Must be one of: age_of_sigmar, warhammer_40k, the_old_world",
        )

    matchup = create_matchup(game_system)

    return MatchupCreateResponse(
        matchup_id=matchup.matchup_id,
        game_system=matchup.game_system.value,
        share_url=f"/squire/matchup/{matchup.matchup_id}",
    )


@router.post("/matchup/{matchup_id}/submit", response_model=MatchupResponse)
async def submit_army_list(matchup_id: str, request: ListSubmitRequest):
    """
    Submit an army list to a matchup

    Args:
        matchup_id: The matchup ID
        request: Player name and army list

    Returns:
        Updated matchup (lists hidden until both submitted)
    """
    try:
        matchup = submit_list(matchup_id, request.player_name, request.army_list)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    # Convert matchup to response
    return _matchup_to_response(matchup)


@router.get("/matchup/{matchup_id}", response_model=MatchupResponse)
async def get_matchup_details(matchup_id: str):
    """
    Get matchup details

    Args:
        matchup_id: The matchup ID

    Returns:
        Matchup details (lists only shown if both players submitted)
    """
    matchup = get_matchup(matchup_id)
    if matchup is None:
        raise HTTPException(status_code=404, detail=f"Matchup {matchup_id} not found")

    return _matchup_to_response(matchup)


def _matchup_to_response(matchup) -> MatchupResponse:
    """Convert Matchup to API response"""
    is_complete = matchup.is_complete()

    # Helper to convert battle plan
    def battle_plan_to_response(bp):
        if bp is None:
            return None
        return BattlePlanResponse(
            name=bp.name,
            game_system=bp.game_system.value,
            deployment=bp.deployment.value,
            deployment_description=bp.deployment_description,
            primary_objective=bp.primary_objective,
            secondary_objectives=bp.secondary_objectives,
            victory_conditions=bp.victory_conditions,
            turn_limit=bp.turn_limit,
            special_rules=bp.special_rules,
            battle_tactics=bp.battle_tactics,
        )

    # Helper to convert player
    def player_to_response(player):
        if player is None:
            return None
        return MatchupPlayerResponse(
            name=player.name,
            army_list=player.army_list,
            submitted_at=player.submitted_at.isoformat(),
        )

    return MatchupResponse(
        matchup_id=matchup.matchup_id,
        game_system=matchup.game_system.value,
        created_at=matchup.created_at.isoformat(),
        player1=player_to_response(matchup.player1) if is_complete else None,
        player2=player_to_response(matchup.player2) if is_complete else None,
        battle_plan=battle_plan_to_response(matchup.battle_plan) if is_complete else None,
        is_complete=is_complete,
        waiting_count=matchup.get_waiting_count(),
    )


@router.get("/health")
async def squire_health():
    """Health check for Squire module"""
    return {
        "module": "squire",
        "status": "operational",
        "features": ["battle_plans"],
        "version": "0.1.0",
    }
