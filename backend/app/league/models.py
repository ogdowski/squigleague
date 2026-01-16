from datetime import datetime
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class League(SQLModel, table=True):
    """League/Tournament season."""

    __tablename__ = "leagues"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, index=True)
    description: Optional[str] = Field(default=None, max_length=2000)
    organizer_id: int = Field(foreign_key="users.id")

    # Dates
    registration_end: datetime
    group_phase_start: Optional[datetime] = None
    group_phase_end: Optional[datetime] = None
    knockout_phase_start: Optional[datetime] = None
    knockout_phase_end: Optional[datetime] = None

    # Status: registration, group_phase, knockout_phase, finished
    status: str = Field(default="registration", max_length=20)

    # Scoring configuration (fixed, not configurable)
    points_per_win: int = Field(default=1000)
    points_per_draw: int = Field(default=600)
    points_per_loss: int = Field(default=200)

    # Player limits
    min_players: int = Field(default=8)  # Hard minimum is 4
    max_players: Optional[int] = Field(default=None)  # None = no limit

    # Group configuration
    min_group_size: int = Field(default=4)
    max_group_size: int = Field(default=6)

    # Knockout phase configuration
    has_knockout_phase: bool = Field(default=True)
    # knockout_size: 2, 4, 8, 16, 32 or None for auto
    knockout_size: Optional[int] = Field(default=None)

    # Knockout phase - are army lists visible?
    knockout_lists_visible: bool = Field(default=False)

    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    groups: list["Group"] = Relationship(back_populates="league")
    players: list["LeaguePlayer"] = Relationship(back_populates="league")
    matches: list["Match"] = Relationship(back_populates="league")

    @property
    def is_registration_open(self) -> bool:
        now = datetime.utcnow()
        return self.status == "registration" and now <= self.registration_end


class Group(SQLModel, table=True):
    """Group in the group phase."""

    __tablename__ = "groups"

    id: Optional[int] = Field(default=None, primary_key=True)
    league_id: int = Field(foreign_key="leagues.id", index=True)
    name: str = Field(max_length=50)  # "Group A", "Group B"

    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    league: League = Relationship(back_populates="groups")
    players: list["LeaguePlayer"] = Relationship(back_populates="group")


class LeaguePlayer(SQLModel, table=True):
    """League participant."""

    __tablename__ = "league_players"

    id: Optional[int] = Field(default=None, primary_key=True)
    league_id: int = Field(foreign_key="leagues.id", index=True)
    user_id: Optional[int] = Field(default=None, foreign_key="users.id", index=True)

    # Group assignment (null before draw)
    group_id: Optional[int] = Field(default=None, foreign_key="groups.id", index=True)

    # Army list for knockout phase
    knockout_army_list: Optional[str] = None
    knockout_list_submitted_at: Optional[datetime] = None

    # League statistics
    games_played: int = Field(default=0)
    games_won: int = Field(default=0)
    games_drawn: int = Field(default=0)
    games_lost: int = Field(default=0)
    total_points: int = Field(default=0)

    # Account claiming
    is_claimed: bool = Field(default=False)
    discord_username: Optional[str] = Field(default=None, max_length=100)

    joined_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    league: League = Relationship(back_populates="players")
    group: Optional[Group] = Relationship(back_populates="players")

    @property
    def average_points(self) -> float:
        if self.games_played == 0:
            return 0.0
        return self.total_points / self.games_played


class Match(SQLModel, table=True):
    """Match in the league."""

    __tablename__ = "matches"

    id: Optional[int] = Field(default=None, primary_key=True)
    league_id: int = Field(foreign_key="leagues.id", index=True)

    # Players
    player1_id: int = Field(foreign_key="league_players.id", index=True)
    player2_id: int = Field(foreign_key="league_players.id", index=True)

    # Match type: group, knockout
    phase: str = Field(max_length=20)
    # Knockout round: round_of_16, quarter, semi, final
    knockout_round: Optional[str] = Field(default=None, max_length=20)

    # Scores (game points, e.g. 72-68)
    player1_score: Optional[int] = None
    player2_score: Optional[int] = None

    # League points (calculated after result submission)
    player1_league_points: Optional[int] = None
    player2_league_points: Optional[int] = None

    # Status: scheduled, pending_confirmation, confirmed, disputed
    status: str = Field(default="scheduled", max_length=20)

    # Who submitted the result
    submitted_by_id: Optional[int] = Field(default=None, foreign_key="users.id")
    confirmed_by_id: Optional[int] = Field(default=None, foreign_key="users.id")
    submitted_at: Optional[datetime] = None
    confirmed_at: Optional[datetime] = None

    # Match deadline
    deadline: Optional[datetime] = None

    # Map
    map_name: Optional[str] = Field(default=None, max_length=100)

    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    league: League = Relationship(back_populates="matches")

    @property
    def is_completed(self) -> bool:
        return self.status == "confirmed"

    @property
    def winner_id(self) -> Optional[int]:
        if not self.is_completed or self.player1_score is None:
            return None
        if self.player1_score > self.player2_score:
            return self.player1_id
        elif self.player2_score > self.player1_score:
            return self.player2_id
        return None  # Draw


class PlayerElo(SQLModel, table=True):
    """Global player ELO rating."""

    __tablename__ = "player_elo"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", unique=True, index=True)

    elo: int = Field(default=1000)
    games_played: int = Field(default=0)

    # Number of games with K=50 (new players have K=50 for first 5 matches)
    k_factor_games: int = Field(default=0)

    updated_at: datetime = Field(default_factory=datetime.utcnow)


class AppSettings(SQLModel, table=True):
    """Global application settings."""

    __tablename__ = "app_settings"

    id: Optional[int] = Field(default=None, primary_key=True)
    key: str = Field(unique=True, index=True, max_length=50)
    value: str = Field(max_length=500)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
