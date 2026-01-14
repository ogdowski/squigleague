"""Role-based access control permissions."""

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


def has_permission(role: str, permission: str) -> bool:
    """Check if a role has a specific permission."""
    if permission not in PERMISSIONS:
        return False

    allowed_roles = PERMISSIONS[permission]
    return role in allowed_roles or role == "admin"
