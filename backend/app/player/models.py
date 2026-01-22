"""Player-related models."""

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class PlayerElo(SQLModel, table=True):
    """Global player ELO rating."""

    __tablename__ = "player_elo"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", unique=True, index=True)

    elo: int = Field(default=1000, sa_column_kwargs={"server_default": "1000"})
    games_played: int = Field(default=0, sa_column_kwargs={"server_default": "0"})

    # Number of games with K=50 (new players have K=50 for first 5 matches)
    k_factor_games: int = Field(default=0, sa_column_kwargs={"server_default": "0"})

    updated_at: datetime = Field(default_factory=datetime.utcnow)
