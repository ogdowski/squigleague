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

    class Config:
        from_attributes = True


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
