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

    class Config:
        from_attributes = True


class MatchupReveal(BaseModel):
    """Schema for revealed matchup (both lists + map)."""

    name: str
    player1_list: str
    player2_list: str
    map_name: str
    revealed_at: datetime

    class Config:
        from_attributes = True


class MatchupCreateResponse(BaseModel):
    """Schema for matchup creation response."""

    name: str
    link: str
    expires_at: datetime
