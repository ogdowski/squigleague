"""Tests for league scoring system."""

import pytest
from app.league.scoring import calculate_match_points, determine_match_result


class TestDetermineMatchResult:
    """Test match result determination."""

    def test_win(self):
        """Higher score is a win."""
        assert determine_match_result(72, 65) == "win"
        assert determine_match_result(100, 0) == "win"
        assert determine_match_result(51, 50) == "win"

    def test_loss(self):
        """Lower score is a loss."""
        assert determine_match_result(65, 72) == "loss"
        assert determine_match_result(0, 100) == "loss"
        assert determine_match_result(50, 51) == "loss"

    def test_draw(self):
        """Equal scores is a draw."""
        assert determine_match_result(70, 70) == "draw"
        assert determine_match_result(0, 0) == "draw"
        assert determine_match_result(50, 50) == "draw"


class TestCalculateMatchPoints:
    """Test league points calculation."""

    def test_win_base_points(self):
        """Win gives 1000 base points."""
        # Win 72-68 (diff=4): 1000 + min(100, max(0, 4+50)) = 1000 + 54 = 1054
        points = calculate_match_points(72, 68)
        assert points == 1054

    def test_loss_base_points(self):
        """Loss gives 200 base points."""
        # Loss 68-72 (diff=-4): 200 + min(100, max(0, -4+50)) = 200 + 46 = 246
        points = calculate_match_points(68, 72)
        assert points == 246

    def test_draw_base_points(self):
        """Draw gives 600 base points."""
        # Draw 70-70 (diff=0): 600 + min(100, max(0, 0+50)) = 600 + 50 = 650
        points = calculate_match_points(70, 70)
        assert points == 650

    def test_max_bonus_on_big_win(self):
        """Max bonus is 100 points (for diff >= 50)."""
        # Win 100-40 (diff=60): 1000 + min(100, max(0, 60+50)) = 1000 + 100 = 1100
        points = calculate_match_points(100, 40)
        assert points == 1100

    def test_min_bonus_on_big_loss(self):
        """Min bonus is 0 points (for diff <= -50)."""
        # Loss 40-100 (diff=-60): 200 + min(100, max(0, -60+50)) = 200 + 0 = 200
        points = calculate_match_points(40, 100)
        assert points == 200

    def test_close_loss_gets_more_bonus(self):
        """Close loss gets higher bonus than big loss."""
        close_loss = calculate_match_points(69, 72)  # diff=-3: 200 + 47 = 247
        big_loss = calculate_match_points(50, 80)  # diff=-30: 200 + 20 = 220

        assert close_loss > big_loss

    def test_big_win_gets_more_bonus(self):
        """Big win gets higher bonus than close win."""
        big_win = calculate_match_points(80, 50)  # diff=30: 1000 + 80 = 1080
        close_win = calculate_match_points(72, 69)  # diff=3: 1000 + 53 = 1053

        assert big_win > close_win

    def test_custom_points_config(self):
        """Custom points per win/draw/loss work correctly."""
        # Win with custom config
        points = calculate_match_points(
            72, 68, points_per_win=500, points_per_draw=300, points_per_loss=100
        )
        # 500 base + 54 bonus = 554
        assert points == 554

        # Loss with custom config
        points = calculate_match_points(
            68, 72, points_per_win=500, points_per_draw=300, points_per_loss=100
        )
        # 100 base + 46 bonus = 146
        assert points == 146

    def test_symmetry_win_loss(self):
        """Win and loss points sum should be predictable."""
        win_points = calculate_match_points(72, 68)  # 1054
        loss_points = calculate_match_points(68, 72)  # 246

        # Total points distributed = 1054 + 246 = 1300
        # This is: 1000 (win) + 200 (loss) + 100 (bonuses sum to 100)
        assert win_points + loss_points == 1300

    def test_draw_symmetry(self):
        """Both players get same points on draw."""
        points_p1 = calculate_match_points(70, 70)
        points_p2 = calculate_match_points(70, 70)

        assert points_p1 == points_p2

    def test_edge_case_zero_scores(self):
        """Zero scores handled correctly."""
        # Draw 0-0
        points = calculate_match_points(0, 0)
        assert points == 650  # 600 + 50

        # Win with zero opponent
        points = calculate_match_points(1, 0)
        assert points == 1051  # 1000 + 51

    def test_bonus_formula_examples(self):
        """Verify bonus formula: min(100, max(0, diff + 50))."""
        test_cases = [
            # (player, opponent, expected_bonus)
            (100, 0, 100),  # diff=100 -> min(100, 150) = 100
            (75, 25, 100),  # diff=50 -> min(100, 100) = 100
            (70, 30, 90),  # diff=40 -> min(100, 90) = 90
            (60, 40, 70),  # diff=20 -> min(100, 70) = 70
            (55, 45, 60),  # diff=10 -> min(100, 60) = 60
            (50, 50, 50),  # diff=0 -> min(100, 50) = 50
            (45, 55, 40),  # diff=-10 -> min(100, 40) = 40
            (30, 60, 20),  # diff=-30 -> min(100, 20) = 20
            (25, 75, 0),  # diff=-50 -> min(100, 0) = 0
            (0, 100, 0),  # diff=-100 -> max(0, -50) = 0
        ]

        for player, opponent, expected_bonus in test_cases:
            points = calculate_match_points(player, opponent)
            if player > opponent:
                base = 1000
            elif player < opponent:
                base = 200
            else:
                base = 600
            assert points == base + expected_bonus, f"Failed for {player}-{opponent}"
