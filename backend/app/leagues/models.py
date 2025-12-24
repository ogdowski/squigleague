"""
Leagues Models

Database models for league management system.
"""

from datetime import datetime, date, timezone
from typing import Optional
from sqlmodel import Field, SQLModel, Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func


class League(SQLModel, table=True):
    """
    League configuration and metadata.
    
    Represents a competitive league with group and playoff phases.
    """
    __tablename__ = "leagues"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    season: str = Field(index=True)
    organizer_id: int = Field(foreign_key="users.id")
    
    format_type: str = Field(default="group_playoff")  # "group_playoff", "round_robin", "single_elimination"
    config: dict = Field(default={}, sa_column=Column(JSON))  # Format-specific configuration
    
    status: str = Field(default="draft", index=True)  # draft, registration, group_phase, playoff, finished
    
    start_date: date
    registration_deadline: date
    
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    )


class LeagueParticipant(SQLModel, table=True):
    """
    Participant registration in a league.
    
    Tracks which group a player is assigned to.
    """
    __tablename__ = "league_participants"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    league_id: int = Field(foreign_key="leagues.id", index=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    
    group_number: Optional[int] = None  # Assigned during group phase start
    playoff_list: Optional[str] = None  # Army list submitted for playoffs
    
    registered_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )


class LeagueMatch(SQLModel, table=True):
    """
    Individual match in a league.
    
    Tracks both battle points (0-100) and league points calculated from them.
    """
    __tablename__ = "league_matches"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    league_id: int = Field(foreign_key="leagues.id", index=True)
    
    player1_id: int = Field(foreign_key="users.id")
    player2_id: int = Field(foreign_key="users.id")
    
    phase: str = Field(index=True)  # "group", "playoff"
    round_number: int
    
    # Battle results (0-100 battle points from mission)
    player1_score: Optional[int] = None
    player2_score: Optional[int] = None
    
    # League points (calculated from battle points)
    player1_points: Optional[int] = None
    player2_points: Optional[int] = None
    
    played: bool = Field(default=False, index=True)
    deadline: datetime
    
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    )


class LeagueStandings(SQLModel, table=True):
    """
    Current standings for a participant in a league phase.
    
    Aggregates match results into overall standings.
    """
    __tablename__ = "league_standings"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    league_id: int = Field(foreign_key="leagues.id", index=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    
    phase: str = Field(index=True)  # "group", "playoff", "overall"
    
    total_points: int = Field(default=0)
    matches_played: int = Field(default=0)
    matches_total: int = Field(default=0)
    
    wins: int = Field(default=0)
    draws: int = Field(default=0)
    losses: int = Field(default=0)
    
    position: int = Field(default=0, index=True)
    
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    )
