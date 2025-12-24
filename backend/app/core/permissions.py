"""
Permission System

Role-based access control for routes.
"""

from typing import List
from fastapi import Depends, HTTPException, status
from app.core.deps import get_current_active_user


def require_role(*allowed_roles: str):
    """
    Dependency factory for role-based access control.
    
    Usage:
        @router.get("/admin", dependencies=[Depends(require_role("admin"))])
        def admin_only_route():
            ...
        
        @router.post("/leagues", dependencies=[Depends(require_role("organizer", "admin"))])
        def create_league():
            ...
    
    Args:
        *allowed_roles: Role names that are allowed (e.g., "admin", "organizer")
        
    Returns:
        Dependency function that checks user role
    """
    async def role_checker(current_user = Depends(get_current_active_user)):
        # Admin always has access
        if hasattr(current_user, 'role') and current_user.role == "admin":
            return current_user
            
        # Check if user has required role
        if hasattr(current_user, 'role') and current_user.role in allowed_roles:
            return current_user
            
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Requires one of roles: {', '.join(allowed_roles)}"
        )
    
    return role_checker


# Permission definitions (as specified in the plan)
PERMISSIONS = {
    "matchup.create": ["anonymous", "player", "organizer", "admin"],
    "matchup.view": ["anonymous", "player", "organizer", "admin"],
    "league.view": ["anonymous", "player", "organizer", "admin"],
    "league.create": ["organizer", "admin"],
    "league.manage_own": ["organizer", "admin"],
    "league.manage_all": ["admin"],
    "league.delete": ["admin"],
    "users.manage": ["admin"],
    "data_importer.sync": ["admin"],
    "elo.view": ["anonymous", "player", "organizer", "admin"],
    "elo.config": ["admin"],
}


def has_permission(user_role: str, permission: str) -> bool:
    """
    Check if a role has a specific permission.
    
    Args:
        user_role: User's role (e.g., "player", "admin")
        permission: Permission to check (e.g., "league.create")
        
    Returns:
        True if role has permission, False otherwise
    """
    allowed_roles = PERMISSIONS.get(permission, [])
    return user_role in allowed_roles
