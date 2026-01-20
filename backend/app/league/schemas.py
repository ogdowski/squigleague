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
    # Army lists configuration
    has_group_phase_lists: bool = Field(default=False)
    has_knockout_phase_lists: bool = Field(default=True)


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
    # Army lists
    has_group_phase_lists: bool
    has_knockout_phase_lists: bool
    group_lists_frozen: bool
    group_lists_visible: bool
    knockout_lists_frozen: bool
    knockout_lists_visible: bool
    current_knockout_round: Optional[str]
    created_at: datetime
    finished_at: Optional[datetime] = None
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
    finished_at: Optional[datetime] = None
    player_count: int
    organizer_name: Optional[str] = None
    is_organizer: bool = False
    is_player: bool = False

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


class GroupUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=50)


class ChangePlayerGroupRequest(BaseModel):
    group_id: int


class PlayerRemovalResponse(BaseModel):
    message: str
    deleted_matches: int
    walkover_matches: int


class ChangeGroupResponse(BaseModel):
    message: str
    deleted_matches: int
    created_matches: int
    new_group_id: int
    new_group_name: str


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
    avatar_url: Optional[str] = None
    joined_at: datetime
    group_army_faction: Optional[str] = None
    group_army_list: Optional[str] = None  # Only included if lists are visible
    group_list_submitted: bool = False
    knockout_army_faction: Optional[str] = None
    knockout_army_list: Optional[str] = None  # Only included if lists are visible
    knockout_list_submitted: bool = False
    knockout_placement: Optional[str] = None  # "1", "2", "top_4", "top_8", etc.

    class Config:
        from_attributes = True


class StandingsEntry(BaseModel):
    position: int
    player_id: int
    user_id: Optional[int] = None  # User ID for profile link (None if external player)
    username: Optional[str]
    discord_username: Optional[str]
    avatar_url: Optional[str] = None
    army_faction: Optional[str] = None  # Current phase army faction
    army_list: Optional[str] = None  # Army list text (if visible)
    list_submitted: bool = False  # Whether list is submitted for current phase
    games_played: int
    games_won: int
    games_drawn: int
    games_lost: int
    total_points: int
    average_points: float
    qualifies: bool = False  # True if guaranteed to advance
    qualifies_as_runner_up: bool = False  # True if qualifies as "best runner-up"


class GroupStandings(BaseModel):
    group_id: int
    group_name: str
    standings: list[StandingsEntry]
    qualifying_spots: int = 0  # Guaranteed spots per group
    runner_up_spots: int = 0  # Extra spots for best runners-up across all groups


# ============ Match Schemas ============


class MatchResultSubmit(BaseModel):
    player1_score: int = Field(ge=0)
    player2_score: int = Field(ge=0)
    map_name: Optional[str] = None


class MatchMapSet(BaseModel):
    map_name: Optional[str] = None  # If None, random map will be assigned
    random: bool = False  # If True, assign random map


class MatchResponse(BaseModel):
    id: int
    league_id: int
    player1_id: int
    player2_id: int
    player1_username: Optional[str] = None
    player2_username: Optional[str] = None
    player1_avatar: Optional[str] = None
    player2_avatar: Optional[str] = None
    player1_army_faction: Optional[str] = None
    player2_army_faction: Optional[str] = None
    group_id: Optional[int] = None
    group_name: Optional[str] = None
    phase: str
    knockout_round: Optional[str]
    player1_score: Optional[int]
    player2_score: Optional[int]
    player1_league_points: Optional[int]
    player2_league_points: Optional[int]
    status: str
    deadline: Optional[datetime]
    map_name: Optional[str]
    submitted_by_id: Optional[int] = None
    created_at: datetime
    is_completed: bool
    # Army lists (visible based on league settings)
    player1_army_list: Optional[str] = None
    player2_army_list: Optional[str] = None

    class Config:
        from_attributes = True


class MatchDetailResponse(BaseModel):
    """Full match details including ELO changes."""

    id: int
    league_id: int
    league_name: str
    # Players
    player1_id: int
    player2_id: int
    player1_user_id: Optional[int] = None
    player2_user_id: Optional[int] = None
    player1_username: Optional[str] = None
    player2_username: Optional[str] = None
    player1_avatar: Optional[str] = None
    player2_avatar: Optional[str] = None
    player1_army_faction: Optional[str] = None
    player2_army_faction: Optional[str] = None
    player1_army_list: Optional[str] = None
    player2_army_list: Optional[str] = None
    # Match info
    phase: str
    knockout_round: Optional[str] = None
    group_name: Optional[str] = None
    player1_score: Optional[int] = None
    player2_score: Optional[int] = None
    player1_league_points: Optional[int] = None
    player2_league_points: Optional[int] = None
    status: str
    map_name: Optional[str] = None
    deadline: Optional[datetime] = None
    # ELO changes
    player1_elo_before: Optional[int] = None
    player1_elo_after: Optional[int] = None
    player2_elo_before: Optional[int] = None
    player2_elo_after: Optional[int] = None
    # Metadata
    submitted_by_id: Optional[int] = None
    submitted_at: Optional[datetime] = None
    confirmed_by_id: Optional[int] = None
    confirmed_at: Optional[datetime] = None
    created_at: datetime
    # Permissions (for current user)
    can_edit: bool = False
    can_set_map: bool = False


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


# ============ Army List Schemas ============


class ArmyListSubmit(BaseModel):
    army_faction: str = Field(min_length=1, max_length=50)
    army_list: str = Field(min_length=1)


class ArmyListResponse(BaseModel):
    player_id: int
    username: Optional[str]
    army_faction: Optional[str]
    army_list: Optional[str]
    submitted_at: Optional[datetime]


# Legacy alias for backward compatibility
KnockoutListSubmit = ArmyListSubmit
KnockoutListResponse = ArmyListResponse


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


# ============ Player Profile Schemas ============


class ProfileMatchResponse(BaseModel):
    """Match info for player profile."""

    match_id: int
    phase: str
    knockout_round: Optional[str]
    opponent_id: int
    opponent_username: Optional[str]
    player_score: Optional[int]
    opponent_score: Optional[int]
    player_league_points: Optional[int]
    result: Optional[str]  # "win", "loss", "draw", None (not played)
    status: str
    played_at: Optional[datetime]
    # Army list (only if visible)
    player_army_list: Optional[str] = None
    opponent_army_list: Optional[str] = None


class ProfileLeagueResponse(BaseModel):
    """League participation info for player profile."""

    league_id: int
    league_name: str
    league_status: str
    # Player stats in this league
    games_played: int
    games_won: int
    games_drawn: int
    games_lost: int
    total_points: int
    average_points: float
    # Knockout list for this league (if visible)
    knockout_army_list: Optional[str] = None
    knockout_list_submitted: bool = False
    # Final placement in knockout (if applicable)
    knockout_placement: Optional[str] = None  # "1", "2", "top_4", etc.
    # Matches in this league
    matches: list[ProfileMatchResponse]


class ArmyStatEntry(BaseModel):
    """Stats for a single army faction."""

    army_faction: str
    games_played: int
    wins: int
    draws: int
    losses: int
    percentage: float


class PlayerProfileResponse(BaseModel):
    """Full player profile with matches and ELO."""

    user_id: int
    username: str
    avatar_url: Optional[str] = None
    # Contact info (email only if user allows)
    email: Optional[str] = None
    discord_username: Optional[str] = None
    # ELO info
    elo: int
    elo_games_played: int
    # Global stats (aggregated across all leagues)
    total_games: int
    total_wins: int
    total_draws: int
    total_losses: int
    win_rate: float
    # Army stats
    most_played_army: Optional[str] = None
    army_stats: list[ArmyStatEntry] = []
    # Leagues participation (matches grouped by league)
    leagues: list[ProfileLeagueResponse]
