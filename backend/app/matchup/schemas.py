from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class MatchupCreate(BaseModel):
    """Schema for creating a new matchup with Player 1's list."""

    army_list: str = Field(min_length=10, max_length=10000)
    title: Optional[str] = Field(default=None, max_length=100)
    is_public: bool = Field(default=True)
    player2_username: Optional[str] = Field(
        default=None, description="Username of player 2 to assign"
    )
    army_faction: Optional[str] = Field(default=None, max_length=50)


class MatchupSubmit(BaseModel):
    """Schema for submitting an army list."""

    army_list: str = Field(min_length=10, max_length=10000)
    army_faction: Optional[str] = Field(default=None, max_length=50)


class MatchupStatus(BaseModel):
    """Schema for matchup status response."""

    name: str
    title: Optional[str] = None
    player1_submitted: bool
    player2_submitted: bool
    is_revealed: bool
    is_public: bool = True
    created_at: datetime
    expires_at: Optional[datetime] = None
    player1_id: Optional[int] = None
    player2_id: Optional[int] = None
    player1_username: Optional[str] = None
    player2_username: Optional[str] = None
    player1_avatar: Optional[str] = None
    player2_avatar: Optional[str] = None
    player1_army_faction: Optional[str] = None
    player2_army_faction: Optional[str] = None
    # Result fields
    player1_score: Optional[int] = None
    player2_score: Optional[int] = None
    result_status: Optional[str] = None
    result_submitted_by_id: Optional[int] = None
    result_auto_confirm_at: Optional[datetime] = None
    # Permissions for current user
    can_submit_result: bool = False
    can_confirm_result: bool = False
    # Info message for anonymous users
    result_info_message: Optional[str] = None

    class Config:
        from_attributes = True


class MatchupPublicToggle(BaseModel):
    """Schema for toggling matchup public visibility."""

    is_public: bool


class MatchupReveal(BaseModel):
    """Schema for revealed matchup (both lists + map)."""

    name: str
    title: Optional[str] = None
    player1_list: str
    player2_list: str
    player1_army_faction: Optional[str] = None
    player2_army_faction: Optional[str] = None
    map_name: str
    map_image: Optional[str] = None
    deployment: Optional[str] = None
    objectives: Optional[str] = None
    scoring: Optional[str] = None
    underdog_ability: Optional[str] = None
    objective_types: Optional[list[str]] = None
    revealed_at: datetime
    player1_id: Optional[int] = None
    player2_id: Optional[int] = None
    player1_username: Optional[str] = None
    player2_username: Optional[str] = None
    player1_avatar: Optional[str] = None
    player2_avatar: Optional[str] = None
    # Result fields
    player1_score: Optional[int] = None
    player2_score: Optional[int] = None
    result_status: Optional[str] = None
    result_submitted_by_id: Optional[int] = None
    result_confirmed_at: Optional[datetime] = None
    result_auto_confirm_at: Optional[datetime] = None
    # Permissions for current user
    can_submit_result: bool = False
    can_confirm_result: bool = False
    # Info message for anonymous users
    result_info_message: Optional[str] = None

    class Config:
        from_attributes = True


class MatchupCreateResponse(BaseModel):
    """Schema for matchup creation response."""

    name: str
    link: str
    expires_at: Optional[datetime] = None


class ResultSubmit(BaseModel):
    """Schema for submitting a match result."""

    player1_score: int = Field(ge=0)
    player2_score: int = Field(ge=0)


class ResultResponse(BaseModel):
    """Schema for result submission/confirmation response."""

    message: str
    result_status: str
    player1_score: int
    player2_score: int
    auto_confirm_at: Optional[datetime] = None
