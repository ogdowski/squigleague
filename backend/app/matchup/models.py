from typing import Optional
from datetime import datetime, timedelta
from sqlmodel import Field, SQLModel
from app.matchup.words import generate_matchup_id


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

    # Players (nullable for anonymous users)
    player1_id: Optional[int] = Field(default=None, foreign_key="users.id")
    player2_id: Optional[int] = Field(default=None, foreign_key="users.id")

    # Army lists
    player1_list: Optional[str] = None
    player2_list: Optional[str] = None

    # Submission status
    player1_submitted: bool = Field(default=False)
    player2_submitted: bool = Field(default=False)

    # Map assignment (after both lists submitted)
    map_name: Optional[str] = None

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime = Field(
        default_factory=lambda: datetime.utcnow() + timedelta(days=90)  # 3 months
    )
    revealed_at: Optional[datetime] = None

    @property
    def is_revealed(self) -> bool:
        """Check if matchup is revealed (both lists submitted)."""
        return self.player1_submitted and self.player2_submitted

    @property
    def is_expired(self) -> bool:
        """Check if matchup has expired."""
        return datetime.utcnow() > self.expires_at
