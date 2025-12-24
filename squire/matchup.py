"""
Matchup management for Squire module
Handles list submission and battle plan generation
"""

import secrets
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from squire.battle_plans import BattlePlan, GameSystem, generate_battle_plan


@dataclass
class MatchupPlayer:
    """Player in a matchup"""

    name: str
    army_list: str
    submitted_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Matchup:
    """
    A matchup between two players
    Created when players want to exchange lists and get a battle plan
    """

    matchup_id: str
    game_system: GameSystem
    creator_user_id: Optional[str] = None  # User who created the matchup
    created_at: datetime = field(default_factory=datetime.utcnow)
    player1: Optional[MatchupPlayer] = None
    player2: Optional[MatchupPlayer] = None
    battle_plan: Optional[BattlePlan] = None

    def is_complete(self) -> bool:
        """Check if both players have submitted lists"""
        return self.player1 is not None and self.player2 is not None

    def add_player(self, name: str, army_list: str) -> bool:
        """
        Add a player to the matchup
        Returns True if this was the second player (matchup now complete)
        """
        player = MatchupPlayer(name=name, army_list=army_list)

        if self.player1 is None:
            self.player1 = player
            return False
        elif self.player2 is None:
            self.player2 = player
            # Generate battle plan when second player submits
            self.battle_plan = generate_battle_plan(self.game_system)
            return True
        else:
            raise ValueError("Matchup already has two players")

    def get_waiting_count(self) -> int:
        """Return number of players who have submitted (0, 1, or 2)"""
        count = 0
        if self.player1 is not None:
            count += 1
        if self.player2 is not None:
            count += 1
        return count


# In-memory storage for matchups (replace with database in production)
_matchups: dict[str, Matchup] = {}


def create_matchup(game_system: GameSystem, creator_user_id: Optional[str] = None) -> Matchup:
    """
    Create a new matchup for the given game system

    Args:
        game_system: Which game system this matchup is for
        creator_user_id: Optional user ID of the matchup creator

    Returns:
        New Matchup instance with unique ID
    """
    # Generate unique matchup ID
    matchup_id = secrets.token_urlsafe(12)

    matchup = Matchup(
        matchup_id=matchup_id,
        game_system=game_system,
        creator_user_id=creator_user_id,
    )

    _matchups[matchup_id] = matchup

    return matchup


def get_matchup(matchup_id: str) -> Optional[Matchup]:
    """
    Retrieve a matchup by ID

    Args:
        matchup_id: The unique matchup identifier

    Returns:
        Matchup if found, None otherwise
    """
    return _matchups.get(matchup_id)


def submit_list(matchup_id: str, player_name: str, army_list: str) -> Matchup:
    """
    Submit a player's army list to a matchup

    Args:
        matchup_id: The matchup to submit to
        player_name: Name of the player submitting
        army_list: The army list text

    Returns:
        Updated Matchup instance

    Raises:
        ValueError: If matchup not found or already full
    """
    matchup = get_matchup(matchup_id)
    if matchup is None:
        raise ValueError(f"Matchup {matchup_id} not found")

    matchup.add_player(player_name, army_list)

    return matchup


def get_matchups_for_user(user_id: str) -> list[Matchup]:
    """
    Get all matchups created by a specific user
    
    Args:
        user_id: The user ID to filter by
        
    Returns:
        List of Matchup instances for this user
    """
    return [m for m in _matchups.values() if m.creator_user_id == user_id]
