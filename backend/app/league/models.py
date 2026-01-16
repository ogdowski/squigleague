from datetime import datetime
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class League(SQLModel, table=True):
    """Liga/Sezon turniejowy."""

    __tablename__ = "leagues"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, index=True)
    description: Optional[str] = Field(default=None, max_length=2000)
    organizer_id: int = Field(foreign_key="users.id")

    # Daty
    registration_start: datetime
    registration_end: datetime
    group_phase_start: Optional[datetime] = None
    group_phase_end: Optional[datetime] = None
    knockout_phase_start: Optional[datetime] = None
    knockout_phase_end: Optional[datetime] = None

    # Status: registration, group_phase, knockout_phase, finished
    status: str = Field(default="registration", max_length=20)

    # Konfiguracja punktacji
    points_per_win: int = Field(default=1000)
    points_per_draw: int = Field(default=600)
    points_per_loss: int = Field(default=200)

    # Faza pucharowa - listy widoczne?
    knockout_lists_visible: bool = Field(default=False)

    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    groups: list["Group"] = Relationship(back_populates="league")
    players: list["LeaguePlayer"] = Relationship(back_populates="league")
    matches: list["Match"] = Relationship(back_populates="league")

    @property
    def is_registration_open(self) -> bool:
        now = datetime.utcnow()
        return (
            self.status == "registration"
            and self.registration_start <= now <= self.registration_end
        )


class Group(SQLModel, table=True):
    """Grupa w fazie grupowej."""

    __tablename__ = "groups"

    id: Optional[int] = Field(default=None, primary_key=True)
    league_id: int = Field(foreign_key="leagues.id", index=True)
    name: str = Field(max_length=50)  # "Grupa A", "Grupa B"

    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    league: League = Relationship(back_populates="groups")
    players: list["LeaguePlayer"] = Relationship(back_populates="group")


class LeaguePlayer(SQLModel, table=True):
    """Uczestnik ligi."""

    __tablename__ = "league_players"

    id: Optional[int] = Field(default=None, primary_key=True)
    league_id: int = Field(foreign_key="leagues.id", index=True)
    user_id: Optional[int] = Field(default=None, foreign_key="users.id", index=True)

    # Przypisanie do grupy (null przed losowaniem)
    group_id: Optional[int] = Field(default=None, foreign_key="groups.id", index=True)

    # Lista armii na faze pucharowa
    knockout_army_list: Optional[str] = None
    knockout_list_submitted_at: Optional[datetime] = None

    # Statystyki w lidze
    games_played: int = Field(default=0)
    games_won: int = Field(default=0)
    games_drawn: int = Field(default=0)
    games_lost: int = Field(default=0)
    total_points: int = Field(default=0)

    # Przejmowanie kont
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
    """Mecz w lidze."""

    __tablename__ = "matches"

    id: Optional[int] = Field(default=None, primary_key=True)
    league_id: int = Field(foreign_key="leagues.id", index=True)

    # Gracze
    player1_id: int = Field(foreign_key="league_players.id", index=True)
    player2_id: int = Field(foreign_key="league_players.id", index=True)

    # Typ meczu: group, knockout
    phase: str = Field(max_length=20)
    # Runda pucharowa: round_of_16, quarter, semi, final
    knockout_round: Optional[str] = Field(default=None, max_length=20)

    # Wyniki (punkty w grze, np. 72-68)
    player1_score: Optional[int] = None
    player2_score: Optional[int] = None

    # Punkty ligowe (obliczone po wpisaniu wyniku)
    player1_league_points: Optional[int] = None
    player2_league_points: Optional[int] = None

    # Status: scheduled, pending_confirmation, confirmed, disputed
    status: str = Field(default="scheduled", max_length=20)

    # Kto zglosil wynik
    submitted_by_id: Optional[int] = Field(default=None, foreign_key="users.id")
    confirmed_by_id: Optional[int] = Field(default=None, foreign_key="users.id")
    submitted_at: Optional[datetime] = None
    confirmed_at: Optional[datetime] = None

    # Termin rozegrania
    deadline: Optional[datetime] = None

    # Mapa
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
    """Globalne ELO gracza."""

    __tablename__ = "player_elo"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", unique=True, index=True)

    elo: int = Field(default=1000)
    games_played: int = Field(default=0)

    # Ile gier z K=50 (nowy gracz ma K=50 przez pierwsze 5 meczy)
    k_factor_games: int = Field(default=0)

    updated_at: datetime = Field(default_factory=datetime.utcnow)


class AppSettings(SQLModel, table=True):
    """Global application settings."""

    __tablename__ = "app_settings"

    id: Optional[int] = Field(default=None, primary_key=True)
    key: str = Field(unique=True, index=True, max_length=50)
    value: str = Field(max_length=500)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
