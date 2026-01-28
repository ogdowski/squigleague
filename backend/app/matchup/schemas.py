from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class MatchupCreate(BaseModel):
    """Schema for creating a new matchup with Player 1's list."""

    army_list: str = Field(min_length=10, max_length=10000)


class MatchupSubmit(BaseModel):
    """Schema for submitting an army list."""

    army_list: str = Field(min_length=10, max_length=10000)


class MatchupStatus(BaseModel):
    """Schema for matchup status response."""

    name: str
    player1_submitted: bool
    player2_submitted: bool
    is_revealed: bool
    created_at: datetime
    expires_at: datetime
    played_on: datetime
    player1_username: Optional[str] = None
    player2_username: Optional[str] = None

    class Config:
        from_attributes = True


class MatchupReveal(BaseModel):
    """Schema for revealed matchup (both lists + map)."""

    name: str
    player1_list: str
    player2_list: str
    map_name: str
    map_image: Optional[str] = None
    deployment: Optional[str] = None
    objectives: Optional[str] = None
    scoring: Optional[str] = None
    underdog_ability: Optional[str] = None
    objective_types: Optional[list[str]] = None
    revealed_at: datetime
    played_on: datetime
    player1_username: Optional[str] = None
    player2_username: Optional[str] = None

    class Config:
        from_attributes = True


class MatchupUpdateDate(BaseModel):
    """Schema for updating matchup played_on date."""

    played_on: datetime = Field(
        ...,
        description="Date when the matchup was played (cannot be in future)"
    )

    @property
    def validate_date(self):
        """Validate that played_on is not in the future."""
        if self.played_on > datetime.utcnow():
            raise ValueError("played_on cannot be in the future")
        return self.played_on


class MatchupCreateResponse(BaseModel):
    """Schema for matchup creation response."""

    name: str
    link: str
    expires_at: datetime
