"""
Data module - shared game data constants.

This module contains all game-related constants like maps, factions, and battle plans.
"""

from app.data.armies import ARMY_DETECTION_PATTERNS, ARMY_FACTIONS, detect_army_faction
from app.data.maps import BATTLE_PLAN_DATA, MAP_IMAGES, MISSION_MAPS, draw_random_map

__all__ = [
    # Maps
    "MISSION_MAPS",
    "MAP_IMAGES",
    "BATTLE_PLAN_DATA",
    "draw_random_map",
    # Armies
    "ARMY_FACTIONS",
    "ARMY_DETECTION_PATTERNS",
    "detect_army_faction",
]
