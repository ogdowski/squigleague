from datetime import datetime
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class League(SQLModel, table=True):
    """League/Tournament season."""

    __tablename__ = "leagues"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, index=True)
    description: Optional[str] = Field(default=None, max_length=10000)
    organizer_id: int = Field(foreign_key="users.id")

    # Location (can be "Online" for online leagues)
    city: Optional[str] = Field(default=None, max_length=100)
    country: Optional[str] = Field(default=None, max_length=100)

    # Dates
    registration_end: datetime
    group_phase_start: Optional[datetime] = None
    group_phase_end: Optional[datetime] = None
    knockout_phase_start: Optional[datetime] = None
    knockout_phase_end: Optional[datetime] = None

    # Status: registration, group_phase, knockout_phase, finished
    status: str = Field(
        default="registration",
        max_length=20,
        sa_column_kwargs={"server_default": "registration"},
    )

    # Flag to indicate group phase has ended (ready for knockout)
    group_phase_ended: bool = Field(
        default=False, sa_column_kwargs={"server_default": "false"}
    )

    # Scoring configuration (fixed, not configurable)
    points_per_win: int = Field(
        default=1000, sa_column_kwargs={"server_default": "1000"}
    )
    points_per_draw: int = Field(
        default=600, sa_column_kwargs={"server_default": "600"}
    )
    points_per_loss: int = Field(
        default=200, sa_column_kwargs={"server_default": "200"}
    )

    # Player limits
    min_players: int = Field(default=8, sa_column_kwargs={"server_default": "8"})
    max_players: Optional[int] = Field(default=None)  # None = no limit

    # Group configuration
    min_group_size: int = Field(default=4, sa_column_kwargs={"server_default": "4"})
    max_group_size: int = Field(default=6, sa_column_kwargs={"server_default": "6"})

    # Scheduling
    days_per_match: int = Field(default=14, sa_column_kwargs={"server_default": "14"})

    # Knockout phase configuration
    has_knockout_phase: bool = Field(
        default=True, sa_column_kwargs={"server_default": "true"}
    )
    # knockout_size: 2, 4, 8, 16, 32 or None for auto
    knockout_size: Optional[int] = Field(default=None)

    # Army lists configuration
    has_group_phase_lists: bool = Field(
        default=False, sa_column_kwargs={"server_default": "false"}
    )
    has_knockout_phase_lists: bool = Field(
        default=True, sa_column_kwargs={"server_default": "true"}
    )

    # Group phase lists - frozen (no edits by players) and visible
    group_lists_frozen: bool = Field(
        default=False, sa_column_kwargs={"server_default": "false"}
    )
    group_lists_visible: bool = Field(
        default=False, sa_column_kwargs={"server_default": "false"}
    )

    # Knockout phase - are army lists visible?
    knockout_lists_visible: bool = Field(
        default=False, sa_column_kwargs={"server_default": "false"}
    )

    # Knockout phase - are army lists frozen (no more edits)?
    knockout_lists_frozen: bool = Field(
        default=False, sa_column_kwargs={"server_default": "false"}
    )

    # Current knockout round being played: round_of_32, round_of_16, quarter, semi, final
    # None = knockout not started yet
    current_knockout_round: Optional[str] = Field(default=None, max_length=20)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    finished_at: Optional[datetime] = Field(default=None)

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

    # Army list for group phase
    group_army_faction: Optional[str] = Field(default=None, max_length=50)
    group_army_list: Optional[str] = None
    group_list_submitted_at: Optional[datetime] = None

    # Army list for knockout phase
    knockout_army_faction: Optional[str] = Field(default=None, max_length=50)
    knockout_army_list: Optional[str] = None
    knockout_list_submitted_at: Optional[datetime] = None

    # League statistics
    games_played: int = Field(default=0, sa_column_kwargs={"server_default": "0"})
    games_won: int = Field(default=0, sa_column_kwargs={"server_default": "0"})
    games_drawn: int = Field(default=0, sa_column_kwargs={"server_default": "0"})
    games_lost: int = Field(default=0, sa_column_kwargs={"server_default": "0"})
    total_points: int = Field(default=0, sa_column_kwargs={"server_default": "0"})

    # Account claiming
    is_claimed: bool = Field(
        default=False, sa_column_kwargs={"server_default": "false"}
    )
    discord_username: Optional[str] = Field(default=None, max_length=100)

    # Knockout placement: "1", "2", "top_4", "top_8", "top_16", "top_32"
    knockout_placement: Optional[str] = Field(default=None, max_length=20)

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
    status: str = Field(
        default="scheduled",
        max_length=20,
        sa_column_kwargs={"server_default": "scheduled"},
    )

    # Who submitted the result
    submitted_by_id: Optional[int] = Field(default=None, foreign_key="users.id")
    confirmed_by_id: Optional[int] = Field(default=None, foreign_key="users.id")
    submitted_at: Optional[datetime] = None
    confirmed_at: Optional[datetime] = None

    # Match deadline
    deadline: Optional[datetime] = None

    # Map
    map_name: Optional[str] = Field(default=None, max_length=100)

    # ELO changes (set on confirmation)
    player1_elo_before: Optional[int] = None
    player1_elo_after: Optional[int] = None
    player2_elo_before: Optional[int] = None
    player2_elo_after: Optional[int] = None

    # Per-match army lists (optional, blind exchange like matchups)
    player1_army_list: Optional[str] = None
    player1_army_faction: Optional[str] = Field(default=None, max_length=50)
    player1_list_submitted_at: Optional[datetime] = None
    player2_army_list: Optional[str] = None
    player2_army_faction: Optional[str] = Field(default=None, max_length=50)
    player2_list_submitted_at: Optional[datetime] = None
    lists_revealed_at: Optional[datetime] = None

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

    @property
    def both_lists_submitted(self) -> bool:
        """Check if both players have submitted their army lists."""
        return self.player1_army_list is not None and self.player2_army_list is not None

    @property
    def lists_revealed(self) -> bool:
        """Check if army lists are revealed (both submitted)."""
        return self.lists_revealed_at is not None


# Re-export PlayerElo from player module for backward compatibility
from app.player.models import PlayerElo  # noqa: E402, F401


class AppSettings(SQLModel, table=True):
    """Global application settings."""

    __tablename__ = "app_settings"

    id: Optional[int] = Field(default=None, primary_key=True)
    key: str = Field(unique=True, index=True, max_length=50)
    value: str = Field(max_length=500)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ArmyStats(SQLModel, table=True):
    """Cached army faction statistics updated after each match."""

    __tablename__ = "army_stats"

    id: Optional[int] = Field(default=None, primary_key=True)
    faction: str = Field(unique=True, index=True, max_length=100)

    games_played: int = Field(default=0, sa_column_kwargs={"server_default": "0"})
    wins: int = Field(default=0, sa_column_kwargs={"server_default": "0"})
    draws: int = Field(default=0, sa_column_kwargs={"server_default": "0"})
    losses: int = Field(default=0, sa_column_kwargs={"server_default": "0"})

    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ArmyMatchupStats(SQLModel, table=True):
    """Cached faction vs faction statistics (excludes mirror matches)."""

    __tablename__ = "army_matchup_stats"

    id: Optional[int] = Field(default=None, primary_key=True)
    faction: str = Field(index=True, max_length=100)
    opponent_faction: str = Field(index=True, max_length=100)

    games_played: int = Field(default=0, sa_column_kwargs={"server_default": "0"})
    wins: int = Field(default=0, sa_column_kwargs={"server_default": "0"})
    draws: int = Field(default=0, sa_column_kwargs={"server_default": "0"})
    losses: int = Field(default=0, sa_column_kwargs={"server_default": "0"})

    updated_at: datetime = Field(default_factory=datetime.utcnow)
