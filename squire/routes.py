"""
Squire API Routes - Battle Plan Randomization Endpoints

Provides REST API for generating random battle plans for AoS, 40k, and The Old World
"""

from enum import Enum
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field

from squire.battle_plans import (
    BattlePlan,
    DeploymentType,
    GameSystem,
    generate_battle_plan,
)
from squire.matchup import create_matchup, get_matchup, submit_list
from squire.auth import (
    RegisterRequest,
    RegisterResponse,
    LoginRequest,
    LoginResponse,
    UserResponse,
    UserProfileResponse,
    ResendVerificationRequest,
    register_user,
    verify_email as verify_email_func,
    resend_verification_email as resend_verification_func,
    login_user,
    get_user_info,
    get_user_profile,
    get_current_user,
)
from squire.admin import (
    require_admin,
    get_users_list,
    get_admin_stats,
    update_user_role,
    get_all_factions,
    create_faction,
    update_faction,
    delete_faction,
    get_user_factions,
    add_user_faction,
    remove_user_faction,
    set_primary_faction,
    UserListResponse,
    AdminStats,
    UpdateUserRoleRequest,
    FactionResponse,
    CreateFactionRequest,
    UpdateFactionRequest,
    UserFactionResponse,
    AddUserFactionRequest,
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




@router.get("/battle-plan/list")
async def get_battle_plan_list(game_system: GameSystem):
    """Get all battle plans for a game system."""
    plans = []
    
    if game_system == GameSystem.AOS:
        from squire.battle_plans import AOS_BATTLE_PLANS
        for bp_data in AOS_BATTLE_PLANS:
            plan = BattlePlan(
                name=bp_data["name"],
                game_system=GameSystem.AOS,
                deployment=DeploymentType.FRONTAL_ASSAULT,
                deployment_description=bp_data.get("deployment", ""),
                primary_objective=bp_data.get("scoring", ""),
                secondary_objectives=[obj.get("name", "") for obj in bp_data.get("objectives", []) if isinstance(obj, dict) and "name" in obj],
                victory_conditions="Player with most Victory Points wins",
                turn_limit=5,
                special_rules=bp_data.get("special_rules", [])
            )
            plans.append(plan)
    
    elif game_system == GameSystem.WARHAMMER_40K:
        from squire.battle_plans import LEVIATHAN_MISSIONS
        deployment_descriptions = {
            DeploymentType.DAWN_OF_WAR: 'Standard battle lines on opposite short table edges. Deploy wholly within 6" of your short table edge.',
            DeploymentType.SEARCH_AND_DESTROY: 'Diagonal corner deployment zones. Deploy in opposite diagonal corners within 6" of corner.',
            DeploymentType.SWEEPING_ENGAGEMENT: 'Offset deployment on long table edges. Deploy on long edges, offset 12" from corners.',
            DeploymentType.CRUCIBLE_OF_BATTLE: 'Center circle deployment with 24" gap. Deploy in 9" circles, 24" apart, along center line.',
        }
        for mission in LEVIATHAN_MISSIONS:
            plan = BattlePlan(
                name=mission["name"],
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
            plans.append(plan)
    
    elif game_system == GameSystem.OLD_WORLD:
        from squire.battle_plans import OLD_WORLD_SCENARIOS
        for scenario in OLD_WORLD_SCENARIOS:
            plan = BattlePlan(
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
            plans.append(plan)
    
    return plans
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
async def create_new_matchup(
    request: MatchupCreateRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new matchup for exchanging lists and generating battle plan
    
    Requires authentication.

    Args:
        request: Matchup creation request with game system
        current_user: Authenticated user (from JWT token)

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

    matchup = create_matchup(game_system, creator_user_id=current_user["user_id"])

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
        "features": ["battle_plans", "matchups", "authentication"],
        "version": "0.2.0",
    }


# ═══════════════════════════════════════════════
# AUTHENTICATION ROUTES
# ═══════════════════════════════════════════════


@router.post("/auth/register", response_model=RegisterResponse)
async def register(request: RegisterRequest):
    """
    Register new user account
    
    Creates unverified account and sends verification email.
    User cannot login until email is verified.
    """
    return await register_user(request)


@router.get("/auth/verify-email")
async def verify_email_endpoint(token: str):
    """
    Verify user email address with token
    
    Token valid for 24 hours after registration.
    """
    return await verify_email_func(token)


@router.post("/auth/resend-verification")
async def resend_verification(request: ResendVerificationRequest):
    """
    Resend verification email to unverified user
    
    Rate limited to prevent abuse.
    """
    return await resend_verification_func(request.email)


@router.post("/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Authenticate user and return JWT token
    
    Requires email to be verified.
    Token valid for 24 hours.
    """
    return await login_user(request.username_or_email, request.password)


@router.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(user: dict = Depends(get_current_user)):
    """
    Get current authenticated user information
    
    Requires valid JWT token in Authorization header.
    """
    return await get_user_info(user)


@router.get("/user/profile", response_model=UserProfileResponse)
async def get_user_profile_endpoint(user: dict = Depends(get_current_user)):
    """
    Get user profile with statistics
    
    Requires valid JWT token in Authorization header.
    Returns user info plus matchup statistics.
    """
    return await get_user_profile(user)


@router.get("/user/matchups")
async def get_user_matchup_history(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    system: str = Query('all'),
    status: str = Query('all'),
    user: dict = Depends(get_current_user)
):
    """
    Get matchup history for authenticated user
    
    Requires valid JWT token in Authorization header.
    Returns paginated list of matchups.
    """
    from squire.matchup import get_matchups_for_user, GameSystem
    
    # Get all user's matchups
    all_matchups = get_matchups_for_user(user["user_id"])
    
    # Filter by game system
    if system != 'all':
        try:
            game_system = GameSystem(system)
            all_matchups = [m for m in all_matchups if m.game_system == game_system]
        except ValueError:
            pass  # Invalid system, ignore filter
    
    # Filter by status
    if status == 'completed':
        all_matchups = [m for m in all_matchups if m.is_complete()]
    elif status == 'in_progress':
        all_matchups = [m for m in all_matchups if not m.is_complete()]
    
    # Sort by created_at descending (newest first)
    all_matchups.sort(key=lambda m: m.created_at, reverse=True)
    
    # Paginate
    total = len(all_matchups)
    total_pages = (total + limit - 1) // limit if total > 0 else 1
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    matchups_page = all_matchups[start_idx:end_idx]
    
    # Convert to response format
    matchup_list = []
    for m in matchups_page:
        matchup_data = {
            "matchup_id": m.matchup_id,
            "game_system": m.game_system.value,
            "created_at": m.created_at.isoformat(),
            "is_complete": m.is_complete(),
            "creator_username": user["username"],  # Current user is creator
            "player1": {
                "name": m.player1.name,
                "submitted_at": m.player1.submitted_at.isoformat()
            } if m.player1 else None,
            "player2": {
                "name": m.player2.name,
                "submitted_at": m.player2.submitted_at.isoformat()
            } if m.player2 else None,
            "battle_plan": {
                "name": m.battle_plan.name,
                "deployment": m.battle_plan.deployment.value,
                "primary_objective": m.battle_plan.primary_objective
            } if m.battle_plan else None
        }
        matchup_list.append(matchup_data)
    
    return {
        "matchups": matchup_list,
        "total": total,
        "page": page,
        "pages": total_pages,
        "limit": limit
    }


# ═══════════════════════════════════════════════════════════════════
# ADMIN ENDPOINTS
# ═══════════════════════════════════════════════════════════════════


@router.get("/api/admin/users", response_model=UserListResponse)
async def get_users_endpoint(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = None,
    is_admin: Optional[bool] = None,
    email_verified: Optional[bool] = None,
    country: Optional[str] = None,
    user: dict = Depends(get_current_user)
):
    """Get paginated list of users (admin only)"""
    from squire.database import get_session
    
    # Verify admin access
    require_admin(user)
    
    db = next(get_session())
    try:
        return get_users_list(
            db=db,
            page=page,
            limit=limit,
            search=search,
            is_admin=is_admin,
            email_verified=email_verified,
            country=country
        )
    finally:
        db.close()


@router.get("/api/admin/stats", response_model=AdminStats)
async def get_stats_endpoint(user: dict = Depends(get_current_user)):
    """Get aggregated platform statistics (admin only)"""
    from squire.database import get_session
    
    # Verify admin access
    require_admin(user)
    
    db = next(get_session())
    try:
        return get_admin_stats(db)
    finally:
        db.close()


@router.patch("/api/admin/users/{user_id}/role")
async def update_user_role_endpoint(
    user_id: str,
    role_data: UpdateUserRoleRequest,
    user: dict = Depends(get_current_user)
):
    """Update user's admin status (admin only)"""
    from squire.database import get_session
    from uuid import UUID
    
    # Verify admin access
    require_admin(user)
    
    # Parse UUID
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    
    db = next(get_session())
    try:
        updated_user = update_user_role(db, user_uuid, role_data.is_admin)
        return {
            "user_id": str(updated_user.id),
            "username": updated_user.username,
            "is_admin": updated_user.is_admin,
            "updated_at": updated_user.updated_at.isoformat()
        }
    finally:
        db.close()


@router.get("/api/admin/factions", response_model=List[FactionResponse])
async def get_factions_admin_endpoint(
    game_system: Optional[str] = Query(None, regex="^(AoS|40K|Old World)$"),
    user: dict = Depends(get_current_user)
):
    """Get all factions (admin only)"""
    from squire.database import get_session
    
    # Verify admin access
    require_admin(user)
    
    db = next(get_session())
    try:
        return get_all_factions(db, game_system)
    finally:
        db.close()


@router.post("/api/admin/factions", status_code=201)
async def create_faction_endpoint(
    faction_data: CreateFactionRequest,
    user: dict = Depends(get_current_user)
):
    """Create a new faction (admin only)"""
    from squire.database import get_session
    
    # Verify admin access
    require_admin(user)
    
    db = next(get_session())
    try:
        faction = create_faction(db, faction_data)
        return {
            "id": str(faction.id),
            "name": faction.name,
            "game_system": faction.game_system,
            "description": faction.description,
            "image_url": faction.image_url,
            "created_at": faction.created_at.isoformat()
        }
    finally:
        db.close()


@router.put("/api/admin/factions/{faction_id}")
async def update_faction_endpoint(
    faction_id: str,
    faction_data: UpdateFactionRequest,
    user: dict = Depends(get_current_user)
):
    """Update a faction (admin only)"""
    from squire.database import get_session
    from uuid import UUID
    
    # Verify admin access
    require_admin(user)
    
    # Parse UUID
    try:
        faction_uuid = UUID(faction_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid faction ID format")
    
    db = next(get_session())
    try:
        faction = update_faction(db, faction_uuid, faction_data)
        return {
            "id": str(faction.id),
            "name": faction.name,
            "game_system": faction.game_system,
            "description": faction.description,
            "image_url": faction.image_url,
            "updated_at": faction.updated_at.isoformat()
        }
    finally:
        db.close()


@router.delete("/api/admin/factions/{faction_id}", status_code=204)
async def delete_faction_endpoint(
    faction_id: str,
    user: dict = Depends(get_current_user)
):
    """Delete a faction (admin only)"""
    from squire.database import get_session
    from uuid import UUID
    
    # Verify admin access
    require_admin(user)
    
    # Parse UUID
    try:
        faction_uuid = UUID(faction_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid faction ID format")
    
    db = next(get_session())
    try:
        delete_faction(db, faction_uuid)
    finally:
        db.close()


# ═══════════════════════════════════════════════════════════════════
# PUBLIC FACTION ENDPOINTS (Non-admin)
# ═══════════════════════════════════════════════════════════════════


@router.get("/api/squire/factions", response_model=List[FactionResponse])
async def get_factions_public_endpoint(
    game_system: Optional[str] = Query(None, regex="^(AoS|40K|Old World)$")
):
    """Get all factions (public access for faction selection)"""
    from squire.database import get_session
    
    db = next(get_session())
    try:
        return get_all_factions(db, game_system)
    finally:
        db.close()


@router.get("/api/squire/user/factions", response_model=List[UserFactionResponse])
async def get_user_factions_endpoint(user: dict = Depends(get_current_user)):
    """Get current user's faction selections"""
    from squire.database import get_session
    from uuid import UUID
    
    db = next(get_session())
    try:
        user_id = UUID(user["user_id"])
        return get_user_factions(db, user_id)
    finally:
        db.close()


@router.post("/api/squire/user/factions", status_code=201)
async def add_user_faction_endpoint(
    faction_data: AddUserFactionRequest,
    user: dict = Depends(get_current_user)
):
    """Add a faction to current user's list"""
    from squire.database import get_session, Faction
    from uuid import UUID
    
    db = next(get_session())
    try:
        user_id = UUID(user["user_id"])
        user_faction = add_user_faction(db, user_id, faction_data)
        
        # Get faction details for response
        faction = db.query(Faction).filter(Faction.id == user_faction.faction_id).first()
        
        return {
            "id": str(user_faction.id),
            "faction_id": str(user_faction.faction_id),
            "faction_name": faction.name if faction else "",
            "game_system": faction.game_system if faction else "",
            "is_primary": user_faction.is_primary,
            "created_at": user_faction.created_at.isoformat()
        }
    finally:
        db.close()


@router.delete("/api/squire/user/factions/{user_faction_id}", status_code=204)
async def remove_user_faction_endpoint(
    user_faction_id: str,
    user: dict = Depends(get_current_user)
):
    """Remove a faction from current user's list"""
    from squire.database import get_session
    from uuid import UUID
    
    # Parse UUID
    try:
        uf_uuid = UUID(user_faction_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid faction ID format")
    
    db = next(get_session())
    try:
        user_id = UUID(user["user_id"])
        remove_user_faction(db, user_id, uf_uuid)
    finally:
        db.close()


@router.patch("/api/squire/user/factions/{user_faction_id}/primary")
async def set_primary_faction_endpoint(
    user_faction_id: str,
    user: dict = Depends(get_current_user)
):
    """Set a faction as primary for its game system"""
    from squire.database import get_session, Faction
    from uuid import UUID
    
    # Parse UUID
    try:
        uf_uuid = UUID(user_faction_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid faction ID format")
    
    db = next(get_session())
    try:
        user_id = UUID(user["user_id"])
        user_faction = set_primary_faction(db, user_id, uf_uuid)
        
        # Get faction details for response
        faction = db.query(Faction).filter(Faction.id == user_faction.faction_id).first()
        
        return {
            "id": str(user_faction.id),
            "faction_id": str(user_faction.faction_id),
            "faction_name": faction.name if faction else "",
            "game_system": faction.game_system if faction else "",
            "is_primary": user_faction.is_primary
        }
    finally:
        db.close()
