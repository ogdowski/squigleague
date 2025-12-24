"""
Test ELO Calculator

Unit tests for ELO math functions.
"""

import pytest
from app.elo.calculator import (
    calculate_expected_score,
    calculate_new_rating,
    get_k_factor,
    calculate_elo_change,
    rating_to_rank,
)


def test_expected_score_equal_ratings():
    """Equal ratings should give 50% expected score"""
    expected = calculate_expected_score(1000, 1000)
    assert abs(expected - 0.5) < 0.001


def test_expected_score_higher_rated():
    """Higher rated player should have > 50% expected score"""
    expected = calculate_expected_score(1200, 1000)
    assert expected > 0.5
    assert expected < 1.0


def test_expected_score_lower_rated():
    """Lower rated player should have < 50% expected score"""
    expected = calculate_expected_score(1000, 1200)
    assert expected < 0.5
    assert expected > 0.0


def test_new_rating_win_as_expected():
    """Winning when expected (E=0.75, S=1.0) gives moderate gain"""
    new_rating = calculate_new_rating(
        current_rating=1200,
        expected_score=0.75,
        actual_score=1.0,
        k_factor=50
    )
    # K * (S - E) = 50 * (1.0 - 0.75) = 50 * 0.25 = 12.5
    assert new_rating == 1200 + 13  # Rounded from 12.5


def test_new_rating_upset_win():
    """Upset win (E=0.25, S=1.0) gives large gain"""
    new_rating = calculate_new_rating(
        current_rating=1000,
        expected_score=0.25,
        actual_score=1.0,
        k_factor=50
    )
    # K * (S - E) = 50 * (1.0 - 0.25) = 50 * 0.75 = 37.5
    assert new_rating == 1000 + 38  # Rounded from 37.5


def test_new_rating_expected_loss():
    """Losing when expected (E=0.25, S=0.0) gives small loss"""
    new_rating = calculate_new_rating(
        current_rating=1000,
        expected_score=0.25,
        actual_score=0.0,
        k_factor=50
    )
    # K * (S - E) = 50 * (0.0 - 0.25) = -12.5
    assert new_rating == 1000 - 13  # Rounded from -12.5


def test_new_rating_upset_loss():
    """Upset loss (E=0.75, S=0.0) gives large loss"""
    new_rating = calculate_new_rating(
        current_rating=1200,
        expected_score=0.75,
        actual_score=0.0,
        k_factor=50
    )
    # K * (S - E) = 50 * (0.0 - 0.75) = -37.5
    assert new_rating == 1200 - 38  # Rounded from -37.5


def test_new_rating_draw():
    """Draw against equal opponent (E=0.5, S=0.5) gives no change"""
    new_rating = calculate_new_rating(
        current_rating=1000,
        expected_score=0.5,
        actual_score=0.5,
        k_factor=50
    )
    assert new_rating == 1000


def test_k_factor_provisional():
    """New players (< 5 games) get K=50"""
    assert get_k_factor(0, 30) == 50
    assert get_k_factor(4, 30) == 50


def test_k_factor_established():
    """Established players (>= 5 games) get base K-factor"""
    assert get_k_factor(5, 30) == 30
    assert get_k_factor(100, 30) == 30


def test_calculate_elo_change_player1_win():
    """Test full ELO calculation for player 1 win"""
    new_p1, new_p2, details = calculate_elo_change(
        player1_rating=1000,
        player2_rating=1000,
        player1_games=10,
        player2_games=10,
        result="player1_win",
        base_k_factor=50
    )
    
    # Both expected 0.5, player 1 got 1.0, player 2 got 0.0
    # K=50 for both (>5 games)
    # Change = 50 * (1.0 - 0.5) = 25
    assert new_p1 == 1000 + 25
    assert new_p2 == 1000 - 25
    
    assert details["player1_actual"] == 1.0
    assert details["player2_actual"] == 0.0
    assert details["player1_change"] == 25
    assert details["player2_change"] == -25


def test_calculate_elo_change_draw():
    """Test ELO calculation for draw"""
    new_p1, new_p2, details = calculate_elo_change(
        player1_rating=1000,
        player2_rating=1000,
        player1_games=10,
        player2_games=10,
        result="draw",
        base_k_factor=50
    )
    
    # Both expected 0.5, both got 0.5
    # Change = 50 * (0.5 - 0.5) = 0
    assert new_p1 == 1000
    assert new_p2 == 1000
    
    assert details["player1_actual"] == 0.5
    assert details["player2_actual"] == 0.5
    assert details["player1_change"] == 0
    assert details["player2_change"] == 0


def test_calculate_elo_change_upset():
    """Test ELO calculation when underdog wins"""
    new_p1, new_p2, details = calculate_elo_change(
        player1_rating=900,   # Underdog
        player2_rating=1100,  # Favorite
        player1_games=10,
        player2_games=10,
        result="player1_win",  # Upset!
        base_k_factor=50
    )
    
    # Player 1 expected less than 0.5, got 1.0 (big gain)
    # Player 2 expected more than 0.5, got 0.0 (big loss)
    assert new_p1 > 900 + 25  # More than if equal
    assert new_p2 < 1100 - 25  # More loss than if equal
    
    assert details["player1_change"] > 25
    assert details["player2_change"] < -25


def test_calculate_elo_change_new_player():
    """Test new players get provisional K=50"""
    new_p1, new_p2, details = calculate_elo_change(
        player1_rating=1000,
        player2_rating=1000,
        player1_games=2,  # New player
        player2_games=20,  # Established
        result="player1_win",
        base_k_factor=30
    )
    
    # Player 1: K=50 (provisional)
    # Player 2: K=30 (base)
    assert details["player1_k"] == 50
    assert details["player2_k"] == 30
    
    # Player 1 gains more than player 2 loses
    assert abs(details["player1_change"]) > abs(details["player2_change"])


def test_rating_to_rank():
    """Test rating tier labels"""
    assert rating_to_rank(1900) == "Grandmaster"
    assert rating_to_rank(1700) == "Master"
    assert rating_to_rank(1500) == "Expert"
    assert rating_to_rank(1300) == "Advanced"
    assert rating_to_rank(1100) == "Intermediate"
    assert rating_to_rank(900) == "Beginner"
    assert rating_to_rank(700) == "Novice"


def test_invalid_result():
    """Test invalid result raises error"""
    with pytest.raises(ValueError, match="Invalid result"):
        calculate_elo_change(
            1000, 1000, 10, 10,
            result="invalid",
            base_k_factor=50
        )
