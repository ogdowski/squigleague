"""
ELO Calculator

Core ELO rating calculations following standard ELO formula.
"""

import math
from typing import Tuple


def calculate_expected_score(rating_a: int, rating_b: int) -> float:
    """
    Calculate expected score for player A against player B.
    
    Uses standard ELO formula:
    E_A = 1 / (1 + 10^((R_B - R_A) / 400))
    
    Args:
        rating_a: Current rating of player A
        rating_b: Current rating of player B
    
    Returns:
        Expected score (0.0 to 1.0)
        - 0.5 means equal chances
        - > 0.5 means player A is favored
        - < 0.5 means player B is favored
    """
    return 1 / (1 + math.pow(10, (rating_b - rating_a) / 400))


def calculate_new_rating(
    current_rating: int,
    expected_score: float,
    actual_score: float,
    k_factor: int
) -> int:
    """
    Calculate new ELO rating after a match.
    
    Formula:
    R_new = R_old + K * (S - E)
    
    Where:
    - R_old: Current rating
    - K: K-factor (determines rating volatility)
    - S: Actual score (1.0 win, 0.5 draw, 0.0 loss)
    - E: Expected score
    
    Args:
        current_rating: Player's current rating
        expected_score: Expected score (from calculate_expected_score)
        actual_score: Actual result (1.0, 0.5, or 0.0)
        k_factor: K-factor for this match
    
    Returns:
        New rating (rounded to nearest integer)
    """
    rating_change = k_factor * (actual_score - expected_score)
    return round(current_rating + rating_change)


def get_k_factor(games_played: int, base_k_factor: int) -> int:
    """
    Determine K-factor based on player experience.
    
    New players (< 5 games) have a higher K-factor to help their rating
    stabilize faster. This is known as "provisional rating" period.
    
    Args:
        games_played: Number of games the player has played
        base_k_factor: Base K-factor from ELOConfig
    
    Returns:
        K-factor to use for this match
    """
    if games_played < 5:
        return 50  # Provisional rating: faster movement
    return base_k_factor


def calculate_elo_change(
    player1_rating: int,
    player2_rating: int,
    player1_games: int,
    player2_games: int,
    result: str,
    base_k_factor: int
) -> Tuple[int, int, dict]:
    """
    Calculate ELO changes for both players after a match.
    
    Args:
        player1_rating: Current rating of player 1
        player2_rating: Current rating of player 2
        player1_games: Games played by player 1
        player2_games: Games played by player 2
        result: Match result ("player1_win", "player2_win", "draw")
        base_k_factor: Base K-factor from config
    
    Returns:
        Tuple of (new_player1_rating, new_player2_rating, details_dict)
        
        details_dict contains:
        - player1_expected: Expected score for player 1
        - player2_expected: Expected score for player 2
        - player1_actual: Actual score for player 1
        - player2_actual: Actual score for player 2
        - player1_k: K-factor used for player 1
        - player2_k: K-factor used for player 2
        - player1_change: Rating change for player 1
        - player2_change: Rating change for player 2
    """
    # Calculate expected scores
    player1_expected = calculate_expected_score(player1_rating, player2_rating)
    player2_expected = calculate_expected_score(player2_rating, player1_rating)
    
    # Convert result to actual scores
    if result == "player1_win":
        player1_actual = 1.0
        player2_actual = 0.0
    elif result == "player2_win":
        player1_actual = 0.0
        player2_actual = 1.0
    elif result == "draw":
        player1_actual = 0.5
        player2_actual = 0.5
    else:
        raise ValueError(f"Invalid result: {result}. Must be 'player1_win', 'player2_win', or 'draw'")
    
    # Get K-factors (higher for new players)
    player1_k = get_k_factor(player1_games, base_k_factor)
    player2_k = get_k_factor(player2_games, base_k_factor)
    
    # Calculate new ratings
    new_player1_rating = calculate_new_rating(
        player1_rating,
        player1_expected,
        player1_actual,
        player1_k
    )
    new_player2_rating = calculate_new_rating(
        player2_rating,
        player2_expected,
        player2_actual,
        player2_k
    )
    
    # Build details dict
    details = {
        "player1_expected": round(player1_expected, 4),
        "player2_expected": round(player2_expected, 4),
        "player1_actual": player1_actual,
        "player2_actual": player2_actual,
        "player1_k": player1_k,
        "player2_k": player2_k,
        "player1_change": new_player1_rating - player1_rating,
        "player2_change": new_player2_rating - player2_rating,
    }
    
    return new_player1_rating, new_player2_rating, details


def rating_to_rank(rating: int) -> str:
    """
    Convert ELO rating to a rank/tier.
    
    Provides a friendly representation of player skill level.
    
    Args:
        rating: ELO rating
    
    Returns:
        Rank name
    """
    if rating >= 1800:
        return "Grandmaster"
    elif rating >= 1600:
        return "Master"
    elif rating >= 1400:
        return "Expert"
    elif rating >= 1200:
        return "Advanced"
    elif rating >= 1000:
        return "Intermediate"
    elif rating >= 800:
        return "Beginner"
    else:
        return "Novice"
