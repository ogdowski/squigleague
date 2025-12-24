"""
Matchup Schemas

Pydantic schemas for matchup-related requests and responses.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class MatchupCreate(BaseModel):
    """Request to create a new matchup"""
    game_system: str = Field(..., description="Game system: age_of_sigmar, warhammer_40k, the_old_world")


class MatchupCreateResponse(BaseModel):
    """Response after creating a matchup"""
    uuid: str
    game_system: str
    share_url: str
    created_at: datetime
    expires_at: datetime


class ListSubmit(BaseModel):
    """Request to submit an army list"""
    player_name: str = Field(..., min_length=1, max_length=100, description="Player display name")
    army_list: str = Field(..., min_length=1, description="Army list text")


class ListSubmitResponse(BaseModel):
    """Response after submitting a list"""
    message: str
    player_number: int  # 1 or 2
    waiting_for_opponent: bool
    both_submitted: bool


class MatchupStatus(BaseModel):
    """Status of a matchup (before both lists submitted)"""
    uuid: str
    game_system: str
    player1_submitted: bool
    player2_submitted: bool
    waiting_count: int
    is_complete: bool
    is_expired: bool
    created_at: datetime
    expires_at: datetime


class BattlePlanData(BaseModel):
    """Battle plan information"""
    name: str
    deployment: str
    deployment_description: str
    primary_objective: str
    secondary_objectives: list[str]
    victory_conditions: str
    turn_limit: int
    special_rules: Optional[list[str]] = None
    battle_tactics: Optional[list[str]] = None


class MatchupReveal(BaseModel):
    """Full matchup reveal (after both lists submitted)"""
    uuid: str
    game_system: str
    
    # Player 1 data
    player1_name: str
    player1_list: str
    player1_submitted_at: datetime
    
    # Player 2 data
    player2_name: str
    player2_list: str
    player2_submitted_at: datetime
    
    # Battle plan
    battle_plan: BattlePlanData
    map_name: str
    
    # Metadata
    created_at: datetime
    revealed_at: datetime


class MatchupHistoryItem(BaseModel):
    """Single matchup in user's history"""
    uuid: str
    game_system: str
    map_name: Optional[str]
    opponent_name: Optional[str]
    is_complete: bool
    created_at: datetime
    revealed_at: Optional[datetime]
    
    class Config:
        from_attributes = True
