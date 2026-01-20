"""League match scoring system."""


def calculate_match_points(
    player_score: int,
    opponent_score: int,
    points_per_win: int = 1000,
    points_per_draw: int = 600,
    points_per_loss: int = 200,
) -> int:
    """
    Calculates league points for a match.

    Scoring:
    - Win: points_per_win (default 1000)
    - Draw: points_per_draw (default 600)
    - Loss: points_per_loss (default 200)

    Plus bonus for score difference:
    - diff = player_score - opponent_score
    - bonus = min(100, max(0, diff + 50))

    Example:
    - Won 72-68: 1000 + min(100, max(0, 4+50)) = 1000 + 54 = 1054
    - Lost 68-72: 200 + min(100, max(0, -4+50)) = 200 + 46 = 246
    """
    if player_score > opponent_score:
        base = points_per_win
    elif player_score < opponent_score:
        base = points_per_loss
    else:
        base = points_per_draw

    diff = player_score - opponent_score
    bonus = min(100, max(0, diff + 50))

    return base + bonus


def determine_match_result(player_score: int, opponent_score: int) -> str:
    """Determines match result: win, draw, loss."""
    if player_score > opponent_score:
        return "win"
    elif player_score < opponent_score:
        return "loss"
    else:
        return "draw"
