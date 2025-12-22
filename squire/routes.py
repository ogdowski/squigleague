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
from squire.matchup import create_matchup, get_matchup, select_battleplan, submit_list

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
    deployment_map_url: Optional[str] = None

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
    battleplan_locked: bool = False
    battleplan_selected_at: Optional[str] = None
    battleplan_selected_by: Optional[str] = None


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
        deployment_map_url=plan.deployment_map_url,
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
    Randomly select a battle plan for the specified game system

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
        default=3, ge=1, le=10, description="Number of battle plans to select (1-10)"
    ),
):
    """
    Randomly select multiple battle plans for tournament planning

    Useful for pre-selecting tournament rounds or giving players options
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
    from squire.battle_plans import AOS_BATTLE_PLANS

    # Extract unique deployment types from AoS battle plans
    aos_deployments = list(set([plan["deployment"] for plan in AOS_BATTLE_PLANS]))

    systems = [
        SystemInfoResponse(
            game_system="age_of_sigmar",
            deployments=aos_deployments,
            description="Age of Sigmar 4th Edition Matched Play - General's Handbook 2025-2026",
        ),
        SystemInfoResponse(
            game_system="warhammer_40k",
            deployments=["Hammer and Anvil", "Search and Destroy", "Sweeping Engagement", "Crucible of Battle"],
            description="Warhammer 40,000 10th Edition matched play",
        ),
        SystemInfoResponse(
            game_system="the_old_world",
            deployments=["Pitched Battle", "Flank Attack", "Meeting Engagement"],
            description="Warhammer: The Old World legacy battles",
        ),
    ]

    return systems


@router.get("/battle-plans/gallery", response_model=List[BattlePlanResponse])
async def get_battle_plans_gallery(
    system: str = Query(
        default="age_of_sigmar",
        description="Game system: age_of_sigmar, warhammer_40k, or the_old_world",
    )
):
    """
    Get all battle plans for a game system (for gallery display)
    
    Returns all available battle plans with deployment map URLs for the specified system.
    Currently only Age of Sigmar has deployment maps.
    """
    try:
        game_system = GameSystem(system)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid game system. Must be: age_of_sigmar, warhammer_40k, or the_old_world",
        )
    
    if game_system == GameSystem.AOS:
        from squire.battle_plans import AOS_BATTLE_PLANS
        
        # Convert AoS battle plans to BattlePlan objects
        plans = []
        for plan_dict in AOS_BATTLE_PLANS:
            # Extract objective names from dict objectives
            objective_list = []
            if "objectives" in plan_dict and isinstance(plan_dict["objectives"], list):
                objective_list = [
                    obj.get("name", "") for obj in plan_dict["objectives"] if "name" in obj
                ]
            
            plan = BattlePlan(
                name=plan_dict["name"],
                game_system=GameSystem.AOS,
                deployment=DeploymentType.FRONTAL_ASSAULT,  # Placeholder
                deployment_description=plan_dict["deployment"],
                primary_objective=plan_dict["scoring"],  # scoring is the string
                secondary_objectives=objective_list,  # List of objective names as strings
                victory_conditions="Player with most Victory Points at end of 5 battle rounds wins. VP scored from controlling objectives per mission rules.",
                turn_limit=5,
                special_rules=plan_dict.get("special_rules", []),
                deployment_map_url=plan_dict.get("deployment_map_url"),
            )
            plans.append(battle_plan_to_response(plan))
        
        return plans
    else:
        raise HTTPException(
            status_code=404,
            detail=f"Gallery not available for {system}. Currently only age_of_sigmar battle plans have deployment maps.",
        )


# ═══════════════════════════════════════════════
# MATCHUP ENDPOINTS
# ═══════════════════════════════════════════════


@router.post("/matchup/create", response_model=MatchupCreateResponse)
async def create_new_matchup(request: MatchupCreateRequest):
    """
    Create a new matchup for exchanging lists and selecting random battle plan

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


@router.post("/matchup/{matchup_id}/select-battleplan", response_model=MatchupResponse)
async def select_matchup_battleplan(matchup_id: str, selected_by: str = "unknown"):
    """
    Select and lock the battleplan for a matchup
    Can only be done once after both players have submitted lists

    Args:
        matchup_id: The matchup ID
        selected_by: Player name or IP who selected (default: "unknown")

    Returns:
        Updated matchup with selected battleplan
    """
    try:
        matchup = select_battleplan(matchup_id, selected_by)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

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
            deployment_map_url=bp.deployment_map_url,
        )

    # Helper to convert player - show player info once they've submitted
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
        player1=player_to_response(matchup.player1),
        player2=player_to_response(matchup.player2),
        battle_plan=battle_plan_to_response(matchup.battle_plan) if matchup.battleplan_locked else None,
        is_complete=is_complete,
        waiting_count=matchup.get_waiting_count(),
        battleplan_locked=matchup.battleplan_locked,
        battleplan_selected_at=matchup.battleplan_selected_at.isoformat() if matchup.battleplan_selected_at else None,
        battleplan_selected_by=matchup.battleplan_selected_by,
    )


@router.get("/health")
async def squire_health():
    """Health check for Squire module"""
    return {
        "module": "squire",
        "status": "operational",
        "features": ["battle_plans", "matchups"],
        "version": "0.3.0",
    }
