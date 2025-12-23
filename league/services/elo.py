import math
from typing import Tuple

class EloService:
    """
    ELO rating calculation service.

    Standard ELO formula:
    - Expected score: E = 1 / (1 + 10^((R_opponent - R_player) / 400))
    - New rating: R_new = R_old + K * (S - E)

    Where:
    - R = rating
    - K = K-factor (volatility, typically 16-64)
    - S = actual score (1.0 for win, 0.5 for draw, 0.0 for loss)
    - E = expected score
    """

    @staticmethod
    def calculate_expected_score(rating_a: int, rating_b: int) -> float:
        """
        Calculate expected score for player A against player B.

        Args:
            rating_a: Player A's current ELO
            rating_b: Player B's current ELO

        Returns:
            Expected score between 0 and 1
        """
        return 1 / (1 + math.pow(10, (rating_b - rating_a) / 400))

    @staticmethod
    def calculate_new_ratings(
        rating_a: int,
        rating_b: int,
        score_a: float,
        k_factor: int = 32
    ) -> Tuple[int, int, int, int]:
        """
        Calculate new ELO ratings after a match.

        Args:
            rating_a: Player A's current ELO
            rating_b: Player B's current ELO
            score_a: Actual score for player A (1.0=win, 0.5=draw, 0.0=loss)
            k_factor: K-factor for rating volatility

        Returns:
            Tuple of (new_rating_a, new_rating_b, change_a, change_b)
        """
        expected_a = EloService.calculate_expected_score(rating_a, rating_b)
        expected_b = 1 - expected_a
        score_b = 1 - score_a

        change_a = round(k_factor * (score_a - expected_a))
        change_b = round(k_factor * (score_b - expected_b))

        new_rating_a = rating_a + change_a
        new_rating_b = rating_b + change_b

        return new_rating_a, new_rating_b, change_a, change_b

    @staticmethod
    def get_k_factor(
        games_played: int,
        rating: int,
        competition_class: str = "local"
    ) -> int:
        """
        Calculate K-factor based on player experience and competition level.

        Args:
            games_played: Total games played by player
            rating: Current ELO rating
            competition_class: Competition level (local, regional, national, international)

        Returns:
            K-factor value
        """
        if games_played < 10:
            base_k = 64
        elif games_played < 30:
            base_k = 40
        elif rating >= 2400:
            base_k = 16
        else:
            base_k = 32

        multipliers = {
            "local": 1.0,
            "regional": 1.2,
            "national": 1.5,
            "international": 2.0
        }

        multiplier = multipliers.get(competition_class, 1.0)
        return round(base_k * multiplier)
