"""
Matchup management for Squire module
Handles list submission and battle plan generation
"""

import random
import secrets
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from squire.battle_plans import BattlePlan, GameSystem, generate_battle_plan

# Herald-style ID generation (adjective-noun-4hex)
ADJECTIVES = [
    "ancient", "brave", "crimson", "dark", "eternal", "fierce", "golden", "heroic",
    "iron", "jade", "keen", "legendary", "mighty", "noble", "ominous", "powerful",
    "radiant", "savage", "terrible", "untamed", "valiant", "wicked", "zealous"
]

NOUNS = [
    "dragon", "phoenix", "wyvern", "griffin", "hydra", "kraken", "serpent", "wolf",
    "bear", "raven", "eagle", "lion", "tiger", "boar", "stag", "hawk",
    "scorpion", "spider", "wyrm", "drake", "beast", "champion", "warlord"
]


def generate_matchup_id() -> str:
    """
    Generate a Herald-style matchup ID: adjective-noun-4hex
    Example: brave-dragon-a3f2
    """
    adjective = random.choice(ADJECTIVES)
    noun = random.choice(NOUNS)
    hex_suffix = secrets.token_hex(2)  # 4 hex characters
    return f"{adjective}-{noun}-{hex_suffix}"


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
    created_at: datetime = field(default_factory=datetime.utcnow)
    player1: Optional[MatchupPlayer] = None
    player2: Optional[MatchupPlayer] = None
    battle_plan: Optional[BattlePlan] = None
    battleplan_selected_at: Optional[datetime] = None
    battleplan_selected_by: Optional[str] = None  # Player name or IP
    battleplan_locked: bool = False

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
            # Auto-generate and lock battleplan when second player submits
            self.battle_plan = generate_battle_plan(self.game_system)
            self.battleplan_selected_at = datetime.utcnow()
            self.battleplan_selected_by = "auto"
            self.battleplan_locked = True
            return True
        else:
            raise ValueError("Matchup already has two players")

    def select_battleplan(self, selected_by: str) -> BattlePlan:
        """
        Select and lock the battleplan for this matchup
        Can only be done once, by either player, after both lists submitted
        
        Args:
            selected_by: Player name or IP address who selected the plan
            
        Returns:
            The selected battle plan
            
        Raises:
            ValueError: If matchup not complete or battleplan already locked
        """
        if not self.is_complete():
            raise ValueError("Both players must submit lists before selecting battleplan")
        
        if self.battleplan_locked:
            raise ValueError("Battleplan already selected and locked")
        
        # Generate the battle plan
        self.battle_plan = generate_battle_plan(self.game_system)
        self.battleplan_selected_at = datetime.utcnow()
        self.battleplan_selected_by = selected_by
        self.battleplan_locked = True
        
        return self.battle_plan

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


def create_matchup(game_system: GameSystem) -> Matchup:
    """
    Create a new matchup for the given game system

    Args:
        game_system: Which game system this matchup is for

    Returns:
        New Matchup instance with unique ID (adjective-noun-4hex format)
    """
    # Generate unique matchup ID in Herald style
    matchup_id = generate_matchup_id()
    
    # Ensure uniqueness (retry if collision - extremely unlikely)
    while matchup_id in _matchups:
        matchup_id = generate_matchup_id()

    matchup = Matchup(matchup_id=matchup_id, game_system=game_system)

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


def select_battleplan(matchup_id: str, selected_by: str) -> Matchup:
    """
    Select and lock the battleplan for a matchup
    
    Args:
        matchup_id: The matchup ID
        selected_by: Player name or IP address who selected the plan
        
    Returns:
        Updated Matchup instance with battleplan
        
    Raises:
        ValueError: If matchup not found, not complete, or already locked
    """
    matchup = get_matchup(matchup_id)
    if matchup is None:
        raise ValueError(f"Matchup {matchup_id} not found")
    
    matchup.select_battleplan(selected_by)
    
    return matchup
