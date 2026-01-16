from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

# ============ League Schemas ============


class LeagueCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=2000)
    registration_end: datetime
    min_players: int = Field(default=8, ge=4)  # Hard minimum is 4
    max_players: Optional[int] = Field(default=None, ge=4)  # None = no limit
    min_group_size: int = Field(default=4, ge=2, le=10)
    max_group_size: int = Field(default=6, ge=2, le=10)
    days_per_match: int = Field(default=14, ge=1, le=60)  # Days per match
    has_knockout_phase: bool = Field(default=True)
    knockout_size: Optional[int] = Field(
        default=None
    )  # 2, 4, 8, 16, 32 or None for auto


class LeagueUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = None
    registration_end: Optional[datetime] = None
    min_players: Optional[int] = Field(default=None, ge=4)
    max_players: Optional[int] = Field(default=None, ge=4)
    min_group_size: Optional[int] = Field(default=None, ge=2, le=10)
    max_group_size: Optional[int] = Field(default=None, ge=2, le=10)
    days_per_match: Optional[int] = Field(default=None, ge=1, le=60)
    group_phase_start: Optional[datetime] = None
    group_phase_end: Optional[datetime] = None
    knockout_phase_start: Optional[datetime] = None
    knockout_phase_end: Optional[datetime] = None
    status: Optional[str] = None
    has_knockout_phase: Optional[bool] = None
    knockout_size: Optional[int] = None  # 2, 4, 8, 16, 32


class LeagueResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    organizer_id: int
    registration_end: datetime
    min_players: int
    max_players: Optional[int]
    group_phase_start: Optional[datetime]
    group_phase_end: Optional[datetime]
    knockout_phase_start: Optional[datetime]
    knockout_phase_end: Optional[datetime]
    status: str
    group_phase_ended: bool
    points_per_win: int
    points_per_draw: int
    points_per_loss: int
    min_group_size: int
    max_group_size: int
    days_per_match: int
    has_knockout_phase: bool
    knockout_size: Optional[int]
    knockout_lists_visible: bool
    created_at: datetime
    player_count: Optional[int] = None
    is_registration_open: bool = False
    # Computed fields for display
    qualifying_spots_per_group: Optional[int] = None
    total_qualifying_spots: Optional[int] = None

    class Config:
        from_attributes = True


class LeagueListResponse(BaseModel):
    id: int
    name: str
    status: str
    registration_end: datetime
    player_count: int
    organizer_name: Optional[str] = None

    class Config:
        from_attributes = True


# ============ Group Schemas ============


class GroupResponse(BaseModel):
    id: int
    league_id: int
    name: str
    created_at: datetime

    class Config:
        from_attributes = True


# ============ LeaguePlayer Schemas ============


class LeaguePlayerCreate(BaseModel):
    discord_username: Optional[str] = Field(default=None, max_length=100)


class LeaguePlayerResponse(BaseModel):
    id: int
    league_id: int
    user_id: Optional[int]
    group_id: Optional[int]
    group_name: Optional[str] = None
    games_played: int
    games_won: int
    games_drawn: int
    games_lost: int
    total_points: int
    average_points: float
    is_claimed: bool
    discord_username: Optional[str]
    username: Optional[str] = None
    joined_at: datetime
    knockout_list_submitted: bool = False

    class Config:
        from_attributes = True


class StandingsEntry(BaseModel):
    position: int
    player_id: int
    username: Optional[str]
    discord_username: Optional[str]
    games_played: int
    games_won: int
    games_drawn: int
    games_lost: int
    total_points: int
    average_points: float
    qualifies: bool = False  # True if this position advances to knockout


class GroupStandings(BaseModel):
    group_id: int
    group_name: str
    standings: list[StandingsEntry]
    qualifying_spots: int = 0  # How many from this group advance


# ============ Match Schemas ============


class MatchResultSubmit(BaseModel):
    player1_score: int = Field(ge=0)
    player2_score: int = Field(ge=0)
    map_name: Optional[str] = None


class MatchResponse(BaseModel):
    id: int
    league_id: int
    player1_id: int
    player2_id: int
    player1_username: Optional[str] = None
    player2_username: Optional[str] = None
    phase: str
    knockout_round: Optional[str]
    player1_score: Optional[int]
    player2_score: Optional[int]
    player1_league_points: Optional[int]
    player2_league_points: Optional[int]
    status: str
    deadline: Optional[datetime]
    map_name: Optional[str]
    created_at: datetime
    is_completed: bool

    class Config:
        from_attributes = True


class BracketMatch(BaseModel):
    match_id: int
    round: str
    position: int
    player1_id: Optional[int]
    player2_id: Optional[int]
    player1_username: Optional[str]
    player2_username: Optional[str]
    player1_score: Optional[int]
    player2_score: Optional[int]
    winner_id: Optional[int]
    status: str


class KnockoutBracket(BaseModel):
    rounds: dict[str, list[BracketMatch]]


# ============ Knockout List Schemas ============


class KnockoutListSubmit(BaseModel):
    army_list: str = Field(min_length=1)


class KnockoutListResponse(BaseModel):
    player_id: int
    username: Optional[str]
    army_list: Optional[str]
    submitted_at: Optional[datetime]


# ============ ELO Schemas ============


class PlayerEloResponse(BaseModel):
    user_id: int
    username: Optional[str] = None
    elo: int
    games_played: int
    updated_at: datetime

    class Config:
        from_attributes = True


class EloRanking(BaseModel):
    position: int
    user_id: int
    username: Optional[str]
    elo: int
    games_played: int
