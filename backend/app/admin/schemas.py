from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class UserResponse(BaseModel):
    id: int
    email: str
    username: Optional[str]
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class RoleUpdate(BaseModel):
    role: str = Field(pattern="^(player|organizer|admin)$")


class ClaimApproval(BaseModel):
    league_player_id: int
    user_id: int


class SettingResponse(BaseModel):
    key: str
    value: str


class SettingUpdate(BaseModel):
    value: str


class EloSettingsResponse(BaseModel):
    k_factor: int
    new_player_k: int
    new_player_games: int


class EloSettingsUpdate(BaseModel):
    k_factor: Optional[int] = Field(default=None, ge=1, le=100)
    new_player_k: Optional[int] = Field(default=None, ge=1, le=100)
    new_player_games: Optional[int] = Field(default=None, ge=1, le=50)


class AdminMatchupResponse(BaseModel):
    """Matchup info for admin panel (respects list visibility)."""

    id: int
    name: str
    title: Optional[str] = None
    player1_id: Optional[int] = None
    player2_id: Optional[int] = None
    player1_username: Optional[str] = None
    player2_username: Optional[str] = None
    player1_submitted: bool
    player2_submitted: bool
    is_revealed: bool
    is_public: bool
    created_at: datetime
    # Lists only if revealed
    player1_list: Optional[str] = None
    player2_list: Optional[str] = None
    player1_army_faction: Optional[str] = None
    player2_army_faction: Optional[str] = None
    map_name: Optional[str] = None
    # Result info
    player1_score: Optional[int] = None
    player2_score: Optional[int] = None
    result_status: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
