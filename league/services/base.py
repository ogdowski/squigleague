from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple

class BaseFormatHandler(ABC):
    """
    Abstract base class for league formats.
    Each new format (Swiss, Pure Playoff, etc.) implements these methods.
    """

    def __init__(self, season: dict):
        self.season = season
        self.config = season.get('format_config', {})

    @abstractmethod
    def validate_config(self) -> Tuple[bool, Optional[str]]:
        """
        Validate format configuration.
        Returns: (is_valid, error_message)
        """
        pass

    @abstractmethod
    def initialize_season(self, participants: List[dict]) -> bool:
        """
        Initialize season structure (e.g., assign groups).
        Returns: True if successful
        """
        pass

    @abstractmethod
    def get_next_matches(self) -> List[Dict[str, Any]]:
        """
        Get upcoming matches to be played.
        Returns: List of match pairings with metadata
        """
        pass

    @abstractmethod
    def record_match_result(self, match: dict, participant1: dict, participant2: dict) -> bool:
        """
        Update standings after match is recorded.
        Returns: True if successful
        """
        pass

    @abstractmethod
    def get_standings(self) -> Dict[str, Any]:
        """
        Get current standings in format-specific structure.
        Returns: Dict with standings data and type indicator
        """
        pass

    @abstractmethod
    def can_advance_phase(self) -> Tuple[bool, Optional[str]]:
        """
        Check if season can move to next phase.
        Returns: (can_advance, reason_if_not)
        """
        pass

    @abstractmethod
    def advance_phase(self) -> str:
        """
        Advance to next phase.
        Returns: New status string
        """
        pass

    @abstractmethod
    def determine_final_rankings(self) -> List[Dict[str, Any]]:
        """
        Determine final rankings after season completion.
        Returns: Ordered list of final positions
        """
        pass


class BaseScoringSystem(ABC):
    """
    Abstract base class for scoring systems.
    Each new scoring system (W/D/L, 20-0, etc.) implements these methods.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    @abstractmethod
    def validate_config(self) -> Tuple[bool, Optional[str]]:
        """
        Validate scoring configuration.
        Returns: (is_valid, error_message)
        """
        pass

    @abstractmethod
    def calculate_points(self, player_score: int, opponent_score: int) -> int:
        """
        Calculate ranking points for player based on match result.
        Returns: Points awarded (e.g., 1050 for AoS, 3 for W/D/L)
        """
        pass

    @abstractmethod
    def get_match_outcome(self, player_score: int, opponent_score: int) -> str:
        """
        Determine match outcome.
        Returns: 'win', 'draw', or 'loss'
        """
        pass

    @abstractmethod
    def get_display_format(self) -> Dict[str, Any]:
        """
        Return information about how to display points in UI.
        Returns: Dict with type, labels, and other display info
        """
        pass


class BaseTiebreakerSystem(ABC):
    """
    Abstract base class for tiebreaker systems.
    Used when players have equal points.
    """

    @abstractmethod
    def resolve_tie(
        self,
        participants: List[dict],
        context: Dict[str, Any]
    ) -> List[dict]:
        """
        Resolve tie between participants.
        Args:
            participants: List of tied participants
            context: Additional context (season data, head-to-head, etc.)
        Returns: Sorted list of participants
        """
        pass
