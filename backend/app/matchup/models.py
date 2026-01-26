from datetime import datetime, timedelta
from typing import Optional

from app.matchup.words import generate_matchup_id
from sqlmodel import Field, SQLModel


class Matchup(SQLModel, table=True):
    """Matchup model for blind army list exchange (Herald functionality)."""

    __tablename__ = "matchups"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(
        default_factory=generate_matchup_id,
        unique=True,
        index=True,
        max_length=50,
    )

    # Optional title for display
    title: Optional[str] = Field(default=None, max_length=100)

    # Players (nullable for anonymous users)
    player1_id: Optional[int] = Field(default=None, foreign_key="users.id")
    player2_id: Optional[int] = Field(default=None, foreign_key="users.id")

    # Army lists
    player1_list: Optional[str] = None
    player2_list: Optional[str] = None

    # Army factions (detected or selected)
    player1_army_faction: Optional[str] = Field(default=None, max_length=50)
    player2_army_faction: Optional[str] = Field(default=None, max_length=50)

    # Submission status
    player1_submitted: bool = Field(default=False)
    player2_submitted: bool = Field(default=False)

    # Map assignment (after both lists submitted)
    map_name: Optional[str] = None

    # Visibility - if True, matchup appears in public completed matchups list
    is_public: bool = Field(default=True)

    # Game result fields
    player1_score: Optional[int] = None
    player2_score: Optional[int] = None

    # Result submission workflow
    # Status: null (no result), pending_confirmation, confirmed, disputed
    result_status: Optional[str] = Field(default=None, max_length=30)
    result_submitted_by_id: Optional[int] = Field(default=None, foreign_key="users.id")
    result_submitted_at: Optional[datetime] = None
    result_confirmed_by_id: Optional[int] = Field(default=None, foreign_key="users.id")
    result_confirmed_at: Optional[datetime] = None
    # Auto-confirm after 24h if opponent doesn't respond
    result_auto_confirm_at: Optional[datetime] = None

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    revealed_at: Optional[datetime] = None

    # Cancellation
    is_cancelled: bool = Field(default=False)
    cancelled_at: Optional[datetime] = None

    @property
    def is_revealed(self) -> bool:
        """Check if matchup is revealed (both lists submitted)."""
        return self.player1_submitted and self.player2_submitted

    @property
    def has_result(self) -> bool:
        """Check if matchup has a submitted result."""
        return self.result_status is not None

    @property
    def is_result_confirmed(self) -> bool:
        """Check if result is confirmed."""
        return self.result_status == "confirmed"

    @property
    def winner_id(self) -> Optional[int]:
        """Return winner's player_id if result is confirmed, None if draw or no result."""
        if not self.is_result_confirmed or self.player1_score is None:
            return None
        if self.player1_score > self.player2_score:
            return self.player1_id
        elif self.player2_score > self.player1_score:
            return self.player2_id
        return None  # Draw

    def can_submit_result(self, user_id: Optional[int]) -> bool:
        """Check if user can submit a result."""
        if not self.is_revealed:
            return False
        if self.result_status == "confirmed":
            return False
        # At least one player must be registered for result submission
        if self.player1_id is None and self.player2_id is None:
            return False
        # User must be one of the players
        if user_id is None:
            return False
        return user_id in (self.player1_id, self.player2_id)

    def can_confirm_result(self, user_id: Optional[int]) -> bool:
        """Check if user can confirm the result."""
        if self.result_status != "pending_confirmation":
            return False
        if user_id is None:
            return False
        # Only the opponent of who submitted can confirm
        if self.result_submitted_by_id == self.player1_id:
            return user_id == self.player2_id
        elif self.result_submitted_by_id == self.player2_id:
            return user_id == self.player1_id
        return False
