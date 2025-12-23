from typing import Dict, Any, Tuple, Optional
from league.services.base import BaseScoringSystem

class AOSDifferentialScoring(BaseScoringSystem):
    """
    Age of Sigmar Differential scoring system.

    Points awarded:
    - Win: 1000 + bonus
    - Draw: 600 + bonus
    - Loss: 200 + bonus

    Bonus calculation:
    - bonus = (player_score - opponent_score + offset)
    - Clamped to [bonus_min, bonus_max]
    - Default: offset=50, range=[0, 100]

    Example:
    - Win 65-35: 1000 + (65-35+50) = 1080
    - Loss 40-60: 200 + (40-60+50) = 230
    - Draw 50-50: 600 + (50-50+50) = 650
    """

    DEFAULT_CONFIG = {
        "base_win": 1000,
        "base_draw": 600,
        "base_loss": 200,
        "bonus_offset": 50,
        "bonus_min": 0,
        "bonus_max": 100
    }

    def __init__(self, config: Dict[str, Any] = None):
        merged_config = {**self.DEFAULT_CONFIG, **(config or {})}
        super().__init__(merged_config)

    def validate_config(self) -> Tuple[bool, Optional[str]]:
        required = ["base_win", "base_draw", "base_loss", "bonus_max"]
        for field in required:
            if field not in self.config:
                return False, f"Missing required field: {field}"

        if self.config["base_win"] < self.config["base_draw"]:
            return False, "base_win must be >= base_draw"

        if self.config["base_draw"] < self.config["base_loss"]:
            return False, "base_draw must be >= base_loss"

        return True, None

    def calculate_points(self, player_score: int, opponent_score: int) -> int:
        """Calculate ranking points"""
        if player_score > opponent_score:
            base = self.config["base_win"]
        elif player_score == opponent_score:
            base = self.config["base_draw"]
        else:
            base = self.config["base_loss"]

        diff = player_score - opponent_score
        bonus = diff + self.config["bonus_offset"]
        bonus = max(self.config["bonus_min"], min(self.config["bonus_max"], bonus))

        return base + bonus

    def get_match_outcome(self, player_score: int, opponent_score: int) -> str:
        """Determine match outcome"""
        if player_score > opponent_score:
            return "win"
        elif player_score == opponent_score:
            return "draw"
        else:
            return "loss"

    def get_display_format(self) -> Dict[str, Any]:
        """Return display format information"""
        return {
            "type": "differential",
            "labels": {
                "points_column": "Points",
                "description": (
                    f"Win: {self.config['base_win']}+bonus, "
                    f"Draw: {self.config['base_draw']}+bonus, "
                    f"Loss: {self.config['base_loss']}+bonus"
                )
            },
            "max_points": self.config["base_win"] + self.config["bonus_max"],
            "min_points": self.config["base_loss"] + self.config["bonus_min"]
        }
