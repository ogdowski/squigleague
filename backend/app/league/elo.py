"""ELO system - re-exported from player module for backward compatibility."""

from app.player.elo import (
    DEFAULT_K_FACTOR,
    DEFAULT_NEW_PLAYER_GAMES,
    DEFAULT_NEW_PLAYER_K,
    calculate_elo_change,
    calculate_expected_score,
    get_global_k_factor,
    get_k_factor,
    get_new_player_games_threshold,
    get_new_player_k_factor,
    get_or_create_player_elo,
    get_setting,
    set_setting,
    update_elo_after_match,
)

__all__ = [
    "calculate_elo_change",
    "calculate_expected_score",
    "get_global_k_factor",
    "get_k_factor",
    "get_new_player_games_threshold",
    "get_new_player_k_factor",
    "get_or_create_player_elo",
    "get_setting",
    "set_setting",
    "update_elo_after_match",
    "DEFAULT_K_FACTOR",
    "DEFAULT_NEW_PLAYER_GAMES",
    "DEFAULT_NEW_PLAYER_K",
]
