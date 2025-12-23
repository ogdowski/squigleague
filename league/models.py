from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any, List
from datetime import date, datetime
from enum import Enum

class LeagueFormat(str, Enum):
    """Available league formats"""
    GROUP_PLAYOFF = "group_playoff"

class ScoringSystem(str, Enum):
    """Available scoring systems"""
    AOS_DIFFERENTIAL = "aos_differential"

class CompetitionClass(str, Enum):
    """Competition level for ELO K-factor adjustments"""
    LOCAL = "local"
    REGIONAL = "regional"
    NATIONAL = "national"
    INTERNATIONAL = "international"

class SeasonStatus(str, Enum):
    """Season status values"""
    REGISTRATION = "registration"
    GROUP_PHASE = "group_phase"
    PLAYOFFS = "playoffs"
    COMPLETED = "completed"

class SeasonCreateRequest(BaseModel):
    """Request to create a new season"""
    name: str = Field(..., min_length=1, max_length=100)
    season_number: int = Field(..., ge=1)
    start_date: date
    registration_deadline: Optional[date] = None

    league_format: LeagueFormat = LeagueFormat.GROUP_PLAYOFF
    format_config: Dict[str, Any] = Field(default_factory=dict)

    scoring_system: ScoringSystem = ScoringSystem.AOS_DIFFERENTIAL
    scoring_config: Dict[str, Any] = Field(default_factory=dict)

    elo_k_factor: int = Field(default=32, ge=16, le=64)
    competition_class: CompetitionClass = CompetitionClass.LOCAL

    @field_validator('format_config')
    @classmethod
    def validate_format_config(cls, v):
        if not isinstance(v, dict):
            raise ValueError('format_config must be a dict')
        return v

    @field_validator('scoring_config')
    @classmethod
    def validate_scoring_config(cls, v):
        if not isinstance(v, dict):
            raise ValueError('scoring_config must be a dict')
        return v

class PlayerRegisterRequest(BaseModel):
    """Request to register a player for a season"""
    season_id: int = Field(..., ge=1)
    discord_id: str = Field(..., min_length=1)
    discord_name: str = Field(..., min_length=1, max_length=100)
    discord_avatar: Optional[str] = None

class MatchSubmitRequest(BaseModel):
    """Request to submit a match result"""
    season_id: int = Field(..., ge=1)
    player1_discord_id: str
    player2_discord_id: str
    player1_score: int = Field(..., ge=0, le=100)
    player2_score: int = Field(..., ge=0, le=100)
    phase: Optional[str] = "group"
    mission: Optional[str] = None
    submitted_by: str

class PlayerResponse(BaseModel):
    """Player information"""
    id: int
    discord_id: str
    discord_name: str
    discord_avatar: Optional[str]
    global_elo: int
    total_games: int
    total_wins: int
    total_draws: int
    total_losses: int

class SeasonResponse(BaseModel):
    """Season information"""
    id: int
    name: str
    season_number: int
    start_date: date
    league_format: str
    scoring_system: str
    status: str
    participant_count: Optional[int] = None

class MatchResponse(BaseModel):
    """Match result information"""
    id: int
    phase: str
    player1_name: str
    player2_name: str
    player1_score: int
    player2_score: int
    player1_points: int
    player2_points: int
    winner_name: Optional[str]
    elo_change_p1: Optional[int]
    elo_change_p2: Optional[int]
    match_date: datetime

class StandingsResponse(BaseModel):
    """Universal standings response"""
    season_id: int
    season_name: str
    league_format: str
    standings: Dict[str, Any]
    display_format: Dict[str, Any]

class GroupStandingPlayer(BaseModel):
    """Player entry in group standings"""
    position: int
    player_id: int
    player_name: str
    points: int
    games_played: int
    avg_score: float
    current_elo: int

class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str
    module: str
