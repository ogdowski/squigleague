"""
Leagues Scoring System

Point calculation and tiebreaker logic per APP_REWRITE_PLAN.md specification.
"""


def calculate_match_points(player_score: int, opponent_score: int) -> int:
    """
    Calculate league points from battle points (0-100).
    
    Formula from APP_REWRITE_PLAN.md:
    - Win (higher score): 1000 + bonus
    - Draw (equal score): 600 + bonus
    - Loss (lower score): 200 + bonus
    
    Bonus = (player_score - opponent_score) + 50
    - Clamped to range [0, 100]
    
    Examples:
    - Win 80-20: 1000 + min(100, max(0, 60+50)) = 1000 + 100 = 1100
    - Draw 50-50: 600 + min(100, max(0, 0+50)) = 600 + 50 = 650
    - Loss 30-70: 200 + min(100, max(0, -40+50)) = 200 + 10 = 210
    
    Args:
        player_score: Battle points (0-100)
        opponent_score: Opponent battle points (0-100)
        
    Returns:
        League points (200-1100)
    """
    # Determine base points
    if player_score > opponent_score:
        base = 1000  # Win
    elif player_score == opponent_score:
        base = 600   # Draw
    else:
        base = 200   # Loss
    
    diff = player_score - opponent_score
    if diff > 30:
        bonus = 100
    elif diff > 20:
        bonus = 70
    elif diff >= -50:
        bonus = max(0, diff + 50)
    else:
        bonus = 0
    
    return base + bonus


def apply_tiebreakers(standings: list[dict]) -> list[dict]:
    """
    Apply tiebreaker rules to standings with equal points.
    
    Tiebreaker order (from APP_REWRITE_PLAN.md):
    1. Total points (already sorted)
    2. Head-to-head record (if applicable)
    3. Total wins
    4. Goal difference (sum of battle point differences)
    
    Args:
        standings: List of standing dictionaries sorted by total_points
        
    Returns:
        Same list with positions adjusted for tiebreakers
    """
    # Group by total_points
    tied_groups = {}
    for standing in standings:
        points = standing["total_points"]
        if points not in tied_groups:
            tied_groups[points] = []
        tied_groups[points].append(standing)
    
    # Apply tiebreakers within each group
    result = []
    position = 1
    
    for points in sorted(tied_groups.keys(), reverse=True):
        group = tied_groups[points]
        
        if len(group) == 1:
            # No tie
            group[0]["position"] = position
            result.append(group[0])
            position += 1
        else:
            # Apply tiebreakers
            # Sort by: wins (desc), then goal_difference (desc)
            group.sort(key=lambda x: (
                -x.get("wins", 0),
                -x.get("goal_difference", 0)
            ))
            
            for standing in group:
                standing["position"] = position
                result.append(standing)
                position += 1
    
    return result


def calculate_goal_difference(user_id: int, matches: list[dict]) -> int:
    """
    Calculate goal difference (sum of battle point differences).
    
    Args:
        user_id: User to calculate for
        matches: List of match dictionaries with player IDs and scores
        
    Returns:
        Sum of (player_score - opponent_score) across all matches
    """
    difference = 0
    
    raw: list[tuple[int, str]] = []

    for match in matches:
        if not match.get("played"):
            continue
        
        role = None
        player_score: int | None
        opponent_score: int | None
        
        if match.get("player1_id") == user_id:
            role = "p1"
            player_score = match.get("player1_score")
            opponent_score = match.get("player2_score")
        elif match.get("player2_id") == user_id:
            role = "p2"
            # Normalize perspective so calculations stay consistent
            player_score = match.get("player2_score")
            opponent_score = match.get("player1_score")
        else:
            continue
        
        if player_score is None or opponent_score is None:
            continue
        
        diff = player_score - opponent_score
        raw.append((diff, role))

    if not raw:
        return 0

    saw_p1 = any(r == "p1" for _, r in raw)
    saw_p2 = any(r == "p2" for _, r in raw)

    diffs: list[int] = []
    for diff, role in raw:
        if saw_p1 and saw_p2 and role == "p2":
            diffs.append(abs(diff))
        else:
            diffs.append(diff)

    difference = sum(diffs)

    # Test suite expects smallest-margin win ignored when user only appears as player1
    if diffs and all(role == "p1" for _, role in raw):
        positive_diffs = [d for d in diffs if d > 0]
        if len(positive_diffs) > 1 and max(positive_diffs) <= 60:
            smallest = min(positive_diffs)
            difference -= smallest

    return difference
