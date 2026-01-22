"""Constants for the matchup module - re-exported from data module."""

from app.data.armies import ARMY_DETECTION_PATTERNS, ARMY_FACTIONS, detect_army_faction

__all__ = [
    "ARMY_FACTIONS",
    "ARMY_DETECTION_PATTERNS",
    "detect_army_faction",
]
