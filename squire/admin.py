"""
Admin functionality for SquigLeague

Permission checks, user management, and admin-only operations
"""

from typing import List, Optional
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from squire.database import User, Faction, UserFaction, Matchup
from squire.auth import get_user_info


# ═══════════════════════════════════════════════
# PERMISSION CHECKS
# ═══════════════════════════════════════════════


def require_admin(user_payload: dict) -> dict:
    """Verify user has admin rights, raise 403 if not"""
    if not user_payload.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return user_payload


# ═══════════════════════════════════════════════
# USER MANAGEMENT MODELS
# ═══════════════════════════════════════════════


class UserListItem(BaseModel):
    """User item in admin list"""
    user_id: UUID
    username: str
    email: str
    email_verified: bool
    is_admin: bool
    country: Optional[str] = None
    city: Optional[str] = None
    created_at: datetime
    total_matchups: int
    last_active: Optional[datetime] = None


class UserListResponse(BaseModel):
    """Paginated user list response"""
    users: List[UserListItem]
    total: int
    page: int
    pages: int
    limit: int


class AdminStats(BaseModel):
    """Aggregated platform statistics"""
    total_users: int
    verified_users: int
    admin_users: int
    total_matchups: int
    active_users_today: int
    active_users_this_week: int
    active_users_this_month: int
    users_by_country: dict
    matchups_by_system: dict
    average_matchups_per_user: float


class UpdateUserRoleRequest(BaseModel):
    """Request to change user's admin status"""
    is_admin: bool


# ═══════════════════════════════════════════════
# FACTION MANAGEMENT MODELS
# ═══════════════════════════════════════════════


class FactionResponse(BaseModel):
    """Faction data for API responses"""
    id: UUID
    name: str
    game_system: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    user_count: int = 0  # How many users have this faction


class CreateFactionRequest(BaseModel):
    """Request to create a new faction"""
    name: str = Field(..., min_length=1, max_length=100)
    game_system: str = Field(..., regex="^(AoS|40K|Old World)$")
    description: Optional[str] = None
    image_url: Optional[str] = None


class UpdateFactionRequest(BaseModel):
    """Request to update faction"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    image_url: Optional[str] = None


# ═══════════════════════════════════════════════
# USER MANAGEMENT FUNCTIONS
# ═══════════════════════════════════════════════


def get_users_list(
    db: Session,
    page: int = 1,
    limit: int = 50,
    search: Optional[str] = None,
    is_admin: Optional[bool] = None,
    email_verified: Optional[bool] = None,
    country: Optional[str] = None
) -> UserListResponse:
    """Get paginated list of users with filters"""
    
    query = db.query(User)
    
    # Apply filters
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (User.username.ilike(search_term)) | 
            (User.email.ilike(search_term))
        )
    
    if is_admin is not None:
        query = query.filter(User.is_admin == is_admin)
    
    if email_verified is not None:
        query = query.filter(User.email_verified == email_verified)
    
    if country:
        query = query.filter(User.country == country)
    
    # Get total count
    total = query.count()
    
    # Calculate pagination
    pages = (total + limit - 1) // limit
    offset = (page - 1) * limit
    
    # Get users
    users = query.order_by(User.created_at.desc()).offset(offset).limit(limit).all()
    
    # Build response with matchup counts
    user_items = []
    for user in users:
        matchup_count = db.query(func.count(Matchup.id)).filter(
            (Matchup.player1_user_id == user.id) | (Matchup.player2_user_id == user.id)
        ).scalar()
        
        user_items.append(UserListItem(
            user_id=user.id,
            username=user.username,
            email=user.email,
            email_verified=user.email_verified,
            is_admin=user.is_admin,
            country=user.country,
            city=user.city,
            created_at=user.created_at,
            total_matchups=matchup_count or 0,
            last_active=user.updated_at
        ))
    
    return UserListResponse(
        users=user_items,
        total=total,
        page=page,
        pages=pages,
        limit=limit
    )


def get_admin_stats(db: Session) -> AdminStats:
    """Get aggregated platform statistics"""
    
    total_users = db.query(func.count(User.id)).scalar()
    verified_users = db.query(func.count(User.id)).filter(User.email_verified == True).scalar()
    admin_users = db.query(func.count(User.id)).filter(User.is_admin == True).scalar()
    total_matchups = db.query(func.count(Matchup.id)).scalar()
    
    # Users by country
    country_stats = db.query(
        User.country, func.count(User.id)
    ).filter(
        User.country.isnot(None)
    ).group_by(User.country).all()
    
    users_by_country = {country: count for country, count in country_stats}
    
    # Matchups by system
    system_stats = db.query(
        Matchup.game_system, func.count(Matchup.id)
    ).group_by(Matchup.game_system).all()
    
    matchups_by_system = {system: count for system, count in system_stats}
    
    # Average matchups per user
    avg_matchups = total_matchups / total_users if total_users > 0 else 0
    
    return AdminStats(
        total_users=total_users,
        verified_users=verified_users,
        admin_users=admin_users,
        total_matchups=total_matchups,
        active_users_today=0,  # TODO: Track last login
        active_users_this_week=0,
        active_users_this_month=0,
        users_by_country=users_by_country,
        matchups_by_system=matchups_by_system,
        average_matchups_per_user=round(avg_matchups, 2)
    )


def update_user_role(db: Session, user_id: UUID, is_admin: bool) -> User:
    """Update user's admin status"""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_admin = is_admin
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    
    return user


# ═══════════════════════════════════════════════
# FACTION MANAGEMENT FUNCTIONS
# ═══════════════════════════════════════════════


def get_all_factions(db: Session, game_system: Optional[str] = None) -> List[FactionResponse]:
    """Get all factions, optionally filtered by game system"""
    
    query = db.query(Faction)
    
    if game_system:
        query = query.filter(Faction.game_system == game_system)
    
    factions = query.order_by(Faction.game_system, Faction.name).all()
    
    # Count users for each faction
    result = []
    for faction in factions:
        user_count = db.query(func.count(UserFaction.id)).filter(
            UserFaction.faction_id == faction.id
        ).scalar()
        
        result.append(FactionResponse(
            id=faction.id,
            name=faction.name,
            game_system=faction.game_system,
            description=faction.description,
            image_url=faction.image_url,
            created_at=faction.created_at,
            updated_at=faction.updated_at,
            user_count=user_count or 0
        ))
    
    return result


def create_faction(db: Session, faction_data: CreateFactionRequest) -> Faction:
    """Create a new faction"""
    
    # Check if faction already exists
    existing = db.query(Faction).filter(
        Faction.name == faction_data.name,
        Faction.game_system == faction_data.game_system
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Faction '{faction_data.name}' already exists for {faction_data.game_system}"
        )
    
    faction = Faction(
        name=faction_data.name,
        game_system=faction_data.game_system,
        description=faction_data.description,
        image_url=faction_data.image_url
    )
    
    db.add(faction)
    db.commit()
    db.refresh(faction)
    
    return faction


def update_faction(db: Session, faction_id: UUID, faction_data: UpdateFactionRequest) -> Faction:
    """Update an existing faction"""
    
    faction = db.query(Faction).filter(Faction.id == faction_id).first()
    if not faction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Faction not found"
        )
    
    if faction_data.name is not None:
        faction.name = faction_data.name
    if faction_data.description is not None:
        faction.description = faction_data.description
    if faction_data.image_url is not None:
        faction.image_url = faction_data.image_url
    
    faction.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(faction)
    
    return faction


def delete_faction(db: Session, faction_id: UUID) -> None:
    """Delete a faction (cascades to user_factions)"""
    
    faction = db.query(Faction).filter(Faction.id == faction_id).first()
    if not faction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Faction not found"
        )
    
    db.delete(faction)
    db.commit()


# ═══════════════════════════════════════════════
# USER FACTION PREFERENCES
# ═══════════════════════════════════════════════


class UserFactionResponse(BaseModel):
    """User's faction selection"""
    id: UUID
    faction_id: UUID
    faction_name: str
    game_system: str
    is_primary: bool
    created_at: datetime


class AddUserFactionRequest(BaseModel):
    """Request to add a faction to user's list"""
    faction_id: UUID
    is_primary: bool = False


def get_user_factions(db: Session, user_id: UUID) -> List[UserFactionResponse]:
    """Get all factions for a user"""
    
    user_factions = db.query(UserFaction).filter(
        UserFaction.user_id == user_id
    ).all()
    
    result = []
    for uf in user_factions:
        faction = db.query(Faction).filter(Faction.id == uf.faction_id).first()
        if faction:
            result.append(UserFactionResponse(
                id=uf.id,
                faction_id=uf.faction_id,
                faction_name=faction.name,
                game_system=faction.game_system,
                is_primary=uf.is_primary,
                created_at=uf.created_at
            ))
    
    return result


def add_user_faction(db: Session, user_id: UUID, faction_data: AddUserFactionRequest) -> UserFaction:
    """Add a faction to user's list"""
    
    # Check if faction exists
    faction = db.query(Faction).filter(Faction.id == faction_data.faction_id).first()
    if not faction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Faction not found"
        )
    
    # Check if already added
    existing = db.query(UserFaction).filter(
        UserFaction.user_id == user_id,
        UserFaction.faction_id == faction_data.faction_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Faction already added to your list"
        )
    
    # If setting as primary, unset other primaries for this system
    if faction_data.is_primary:
        db.query(UserFaction).filter(
            UserFaction.user_id == user_id
        ).join(Faction).filter(
            Faction.game_system == faction.game_system
        ).update({"is_primary": False}, synchronize_session=False)
    
    user_faction = UserFaction(
        user_id=user_id,
        faction_id=faction_data.faction_id,
        is_primary=faction_data.is_primary
    )
    
    db.add(user_faction)
    db.commit()
    db.refresh(user_faction)
    
    return user_faction


def remove_user_faction(db: Session, user_id: UUID, user_faction_id: UUID) -> None:
    """Remove a faction from user's list"""
    
    user_faction = db.query(UserFaction).filter(
        UserFaction.id == user_faction_id,
        UserFaction.user_id == user_id
    ).first()
    
    if not user_faction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Faction not found in your list"
        )
    
    db.delete(user_faction)
    db.commit()


def set_primary_faction(db: Session, user_id: UUID, user_faction_id: UUID) -> UserFaction:
    """Set a faction as primary for its system"""
    
    user_faction = db.query(UserFaction).filter(
        UserFaction.id == user_faction_id,
        UserFaction.user_id == user_id
    ).first()
    
    if not user_faction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Faction not found in your list"
        )
    
    # Get faction to determine game system
    faction = db.query(Faction).filter(Faction.id == user_faction.faction_id).first()
    
    # Unset other primaries for this system
    db.query(UserFaction).filter(
        UserFaction.user_id == user_id,
        UserFaction.id != user_faction_id
    ).join(Faction).filter(
        Faction.game_system == faction.game_system
    ).update({"is_primary": False}, synchronize_session=False)
    
    # Set this one as primary
    user_faction.is_primary = True
    db.commit()
    db.refresh(user_faction)
    
    return user_faction
