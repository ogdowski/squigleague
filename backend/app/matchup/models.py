"""
Matchup Models

SQLModel models for matchup functionality with database persistence.
Replaces in-memory storage from original squire/matchup.py
"""

from datetime import datetime, timedelta
from typing import Optional
from sqlmodel import Field, SQLModel, Column, JSON
from sqlalchemy import Text


class Matchup(SQLModel, table=True):
    """
    A matchup between two players for list exchange and battle plan generation.
    
    Flow:
    1. Player 1 creates matchup, gets UUID link
    2. Player 1 submits their list
    3. Player 1 shares link with Player 2
    4. Player 2 submits their list
    5. Battle plan is generated automatically
    6. Both players can view lists + battle plan
    """
    __tablename__ = "matchups"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    uuid: str = Field(unique=True, index=True, max_length=50, nullable=False)
    
    # Game system
    game_system: str = Field(max_length=50, nullable=False)  # "age_of_sigmar", "warhammer_40k", etc.
    
    # Players (nullable for anonymous users)
    player1_user_id: Optional[int] = Field(default=None, foreign_key="users.id")
    player2_user_id: Optional[int] = Field(default=None, foreign_key="users.id")
    
    # Player names (for anonymous or display)
    player1_name: Optional[str] = Field(default=None, max_length=100)
    player2_name: Optional[str] = Field(default=None, max_length=100)
    
    # Army lists (text content)
    player1_list: Optional[str] = Field(default=None, sa_column=Column(Text))
    player2_list: Optional[str] = Field(default=None, sa_column=Column(Text))
    
    # Submission status
    player1_submitted: bool = Field(default=False, nullable=False)
    player2_submitted: bool = Field(default=False, nullable=False)
    
    # Battle plan data (stored as JSON)
    battle_plan: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    
    # Map name (extracted from battle plan for easy display)
    map_name: Optional[str] = Field(default=None, max_length=200)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    expires_at: datetime = Field(
        default_factory=lambda: datetime.utcnow() + timedelta(days=7),
        nullable=False
    )
    revealed_at: Optional[datetime] = None  # When both lists were submitted
    
    def is_complete(self) -> bool:
        """Check if both players have submitted lists"""
        return self.player1_submitted and self.player2_submitted
    
    def is_expired(self) -> bool:
        """Check if matchup has expired"""
        return datetime.utcnow() > self.expires_at
    
    def get_waiting_count(self) -> int:
        """Return number of players who have submitted (0, 1, or 2)"""
        count = 0
        if self.player1_submitted:
            count += 1
        if self.player2_submitted:
            count += 1
        return count
    
    def __repr__(self):
        return f"<Matchup(uuid='{self.uuid}', system='{self.game_system}', complete={self.is_complete()})>"
