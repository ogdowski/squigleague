# League System Implementation Plan - Squig League

**Project:** Squig League (FastAPI + SQLAlchemy + Alpine.js + PostgreSQL)
**Date:** 2025-12-23
**Status:** Planning Phase

---

## Executive Summary

This plan adapts the proposed extensible league system architecture to match Squig League's existing tech stack:
- **Backend:** FastAPI + SQLAlchemy (functional style, raw SQL)
- **Frontend:** Alpine.js SPA with Tailwind CSS
- **Database:** PostgreSQL with schema initialization (no migrations)
- **Architecture:** Module-based (following Herald pattern)

The implementation will create a new `league` module alongside `herald`, using the same architectural patterns while introducing Strategy Pattern for league formats and scoring systems.

---

## Phase 1: Database Schema Design

### 1.1 Core Tables

**File:** `database/init.sql` (append to existing file)

```sql
-- ═══════════════════════════════════════════════
-- LEAGUE SCHEMA (Phase 2)
-- ═══════════════════════════════════════════════

-- Seasons table - represents a league season
CREATE TABLE IF NOT EXISTS league_seasons (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,                           -- e.g., "Season 1", "Winter 2025"
    season_number INTEGER NOT NULL,               -- Sequential season number
    start_date DATE NOT NULL,
    registration_deadline DATE,

    -- Format configuration (Strategy Pattern via JSON)
    league_format TEXT NOT NULL DEFAULT 'group_playoff',  -- group_playoff, swiss, pure_playoff
    format_config JSONB DEFAULT '{}',             -- Format-specific config
    -- Example: {"num_groups": 4, "max_unplayed_games": 1, "use_elo_for_grouping": false}

    -- Scoring system configuration
    scoring_system TEXT NOT NULL DEFAULT 'aos_differential',  -- aos_differential, win_draw_loss
    scoring_config JSONB DEFAULT '{}',            -- Scoring-specific config
    -- Example: {"base_win": 1000, "base_draw": 600, "base_loss": 200, "bonus_max": 100}

    -- ELO configuration
    elo_k_factor INTEGER NOT NULL DEFAULT 32,     -- ELO volatility factor
    counts_for_elo BOOLEAN DEFAULT FALSE,         -- Does this season count for global ELO?
    competition_class TEXT DEFAULT 'local',       -- local, regional, national, international

    -- Status tracking (universal - format determines meaning)
    status TEXT NOT NULL DEFAULT 'registration',  -- registration, group_phase, playoffs, completed

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_league_seasons_status ON league_seasons(status);
CREATE INDEX idx_league_seasons_number ON league_seasons(season_number);
COMMENT ON TABLE league_seasons IS 'League seasons with extensible format and scoring configs';

-- Players table - represents individual players
CREATE TABLE IF NOT EXISTS league_players (
    id SERIAL PRIMARY KEY,
    discord_id TEXT UNIQUE NOT NULL,              -- Discord user ID
    discord_name TEXT NOT NULL,                   -- Display name
    discord_avatar TEXT,                          -- Avatar URL

    -- Global ELO rating
    global_elo INTEGER NOT NULL DEFAULT 1500,     -- Starting ELO
    peak_elo INTEGER NOT NULL DEFAULT 1500,       -- Highest ELO ever reached

    -- Career statistics
    total_games INTEGER DEFAULT 0,
    total_wins INTEGER DEFAULT 0,
    total_draws INTEGER DEFAULT 0,
    total_losses INTEGER DEFAULT 0,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_active TIMESTAMPTZ DEFAULT NOW(),

    -- Phase 3: Link to core_users when auth is added
    user_id UUID REFERENCES core_users(id) ON DELETE SET NULL
);

CREATE INDEX idx_league_players_discord ON league_players(discord_id);
CREATE INDEX idx_league_players_elo ON league_players(global_elo DESC);
COMMENT ON TABLE league_players IS 'Players with global ELO ratings';

-- Season participants - links players to seasons
CREATE TABLE IF NOT EXISTS league_participants (
    id SERIAL PRIMARY KEY,
    season_id INTEGER NOT NULL REFERENCES league_seasons(id) ON DELETE CASCADE,
    player_id INTEGER NOT NULL REFERENCES league_players(id) ON DELETE CASCADE,

    -- Group assignment (format-specific - NULL for non-group formats)
    group_number INTEGER,                         -- 1, 2, 3, 4 for group_playoff

    -- Group phase statistics
    group_points INTEGER DEFAULT 0,               -- Total ranking points in group phase
    group_games_played INTEGER DEFAULT 0,
    group_avg_score DECIMAL(6,2),                 -- Average battle score in group

    -- Playoff tracking
    qualified_for_playoffs BOOLEAN DEFAULT FALSE,
    playoff_position INTEGER,                     -- Final playoff position (1-8)

    -- ELO tracking for this season
    starting_elo INTEGER NOT NULL,                -- ELO at season start
    current_season_elo INTEGER NOT NULL,          -- Current ELO during season

    -- Registration
    registered_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(season_id, player_id)
);

CREATE INDEX idx_league_participants_season ON league_participants(season_id);
CREATE INDEX idx_league_participants_player ON league_participants(player_id);
CREATE INDEX idx_league_participants_group ON league_participants(season_id, group_number);
COMMENT ON TABLE league_participants IS 'Players enrolled in specific seasons';

-- Matches table - stores match results
CREATE TABLE IF NOT EXISTS league_matches (
    id SERIAL PRIMARY KEY,
    season_id INTEGER NOT NULL REFERENCES league_seasons(id) ON DELETE CASCADE,

    -- Match phase (format-specific)
    phase TEXT NOT NULL,                          -- 'group', 'quarterfinal', 'semifinal', 'final'

    -- Players
    player1_id INTEGER NOT NULL REFERENCES league_players(id) ON DELETE CASCADE,
    player2_id INTEGER NOT NULL REFERENCES league_players(id) ON DELETE CASCADE,

    -- Battle scores
    player1_score INTEGER NOT NULL,               -- 0-100 (AoS battle score)
    player2_score INTEGER NOT NULL,

    -- Ranking points (calculated by scoring system)
    player1_points INTEGER NOT NULL,              -- e.g., 1050 in AoS differential
    player2_points INTEGER NOT NULL,

    -- Match outcome
    winner_id INTEGER REFERENCES league_players(id),  -- NULL for draws

    -- ELO changes
    elo_change_p1 INTEGER,                        -- +15, -12, etc.
    elo_change_p2 INTEGER,
    k_factor_p1 INTEGER,                          -- K-factor used for player 1
    k_factor_p2 INTEGER,
    counted_for_elo BOOLEAN DEFAULT FALSE,        -- Did this match count for ELO?

    -- Match metadata
    mission TEXT,                                 -- Scenario/mission played
    match_date TIMESTAMPTZ DEFAULT NOW(),
    status TEXT DEFAULT 'confirmed',              -- confirmed, disputed, voided

    -- Submission tracking
    submitted_by TEXT,                            -- Discord ID of submitter
    submitted_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_league_matches_season ON league_matches(season_id);
CREATE INDEX idx_league_matches_players ON league_matches(player1_id, player2_id);
CREATE INDEX idx_league_matches_date ON league_matches(match_date);
COMMENT ON TABLE league_matches IS 'Match results with ELO and ranking points';

-- ELO history - tracks ELO changes over time
CREATE TABLE IF NOT EXISTS league_elo_history (
    id SERIAL PRIMARY KEY,
    player_id INTEGER NOT NULL REFERENCES league_players(id) ON DELETE CASCADE,
    match_id INTEGER REFERENCES league_matches(id) ON DELETE SET NULL,
    season_id INTEGER REFERENCES league_seasons(id) ON DELETE CASCADE,

    -- ELO change
    old_elo INTEGER NOT NULL,
    new_elo INTEGER NOT NULL,
    change INTEGER NOT NULL,                      -- new_elo - old_elo
    k_factor INTEGER NOT NULL,                    -- K-factor used

    -- Match context
    opponent_id INTEGER REFERENCES league_players(id) ON DELETE SET NULL,
    match_result TEXT,                            -- 'win', 'draw', 'loss'

    timestamp TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_league_elo_player ON league_elo_history(player_id, timestamp DESC);
CREATE INDEX idx_league_elo_season ON league_elo_history(season_id);
COMMENT ON TABLE league_elo_history IS 'Historical ELO rating changes';
```

### 1.2 Initial Data (Optional)

```sql
-- Example season for testing
INSERT INTO league_seasons (
    name, season_number, start_date,
    league_format, format_config,
    scoring_system, scoring_config,
    elo_k_factor, counts_for_elo,
    status
) VALUES (
    'Season 1 - Inaugural',
    1,
    CURRENT_DATE,
    'group_playoff',
    '{"num_groups": 4, "max_unplayed_games": 1, "use_elo_for_grouping": false}',
    'aos_differential',
    '{"base_win": 1000, "base_draw": 600, "base_loss": 200, "bonus_offset": 50, "bonus_max": 100}',
    32,
    false,
    'registration'
) ON CONFLICT DO NOTHING;
```

---

## Phase 2: Backend - Pydantic Models

### 2.1 Request/Response Models

**File:** `league/models.py` (new file)

```python
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any, List
from datetime import date, datetime
from enum import Enum

# ═══════════════════════════════════════════════
# ENUMS
# ═══════════════════════════════════════════════

class LeagueFormat(str, Enum):
    """Available league formats"""
    GROUP_PLAYOFF = "group_playoff"
    # Future formats (commented for extensibility):
    # SWISS = "swiss"
    # PURE_PLAYOFF = "pure_playoff"
    # ROUND_ROBIN = "round_robin"

class ScoringSystem(str, Enum):
    """Available scoring systems"""
    AOS_DIFFERENTIAL = "aos_differential"
    # Future systems:
    # WIN_DRAW_LOSS = "win_draw_loss"
    # TWENTY_ZERO = "twenty_zero"

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

# ═══════════════════════════════════════════════
# REQUEST MODELS
# ═══════════════════════════════════════════════

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
    submitted_by: str  # Discord ID of submitter

# ═══════════════════════════════════════════════
# RESPONSE MODELS
# ═══════════════════════════════════════════════

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
    standings: Dict[str, Any]  # Format-specific structure
    display_format: Dict[str, Any]  # How to display points

class GroupStandingPlayer(BaseModel):
    """Player entry in group standings"""
    position: int
    player_id: int
    player_name: str
    points: int
    games_played: int
    avg_score: float
    current_elo: int
```

---

## Phase 3: Backend - Database Operations

### 3.1 Database Functions

**File:** `league/database.py` (new file)

Following Herald's pattern: functional style with context manager and raw SQL.

```python
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

# Reuse Herald's database connection
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://squig:password@postgres:5432/squigleague"
)

engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@contextmanager
def get_db():
    """Context manager for database sessions"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        db.close()

# ═══════════════════════════════════════════════
# SEASON OPERATIONS
# ═══════════════════════════════════════════════

def create_season(
    name: str,
    season_number: int,
    start_date: date,
    league_format: str,
    format_config: dict,
    scoring_system: str,
    scoring_config: dict,
    elo_k_factor: int,
    competition_class: str,
    registration_deadline: Optional[date] = None
) -> Optional[int]:
    """Create a new season"""
    try:
        with get_db() as db:
            query = text("""
                INSERT INTO league_seasons (
                    name, season_number, start_date, registration_deadline,
                    league_format, format_config, scoring_system, scoring_config,
                    elo_k_factor, competition_class
                )
                VALUES (
                    :name, :season_number, :start_date, :registration_deadline,
                    :league_format, :format_config::jsonb, :scoring_system, :scoring_config::jsonb,
                    :elo_k_factor, :competition_class
                )
                RETURNING id
            """)
            result = db.execute(query, {
                "name": name,
                "season_number": season_number,
                "start_date": start_date,
                "registration_deadline": registration_deadline,
                "league_format": league_format,
                "format_config": json.dumps(format_config),
                "scoring_system": scoring_system,
                "scoring_config": json.dumps(scoring_config),
                "elo_k_factor": elo_k_factor,
                "competition_class": competition_class
            }).fetchone()
            return result[0] if result else None
    except Exception as e:
        logger.error(f"Error creating season: {e}")
        return None

def get_season(season_id: int) -> Optional[dict]:
    """Get season by ID"""
    try:
        with get_db() as db:
            query = text("""
                SELECT id, name, season_number, start_date, registration_deadline,
                       league_format, format_config, scoring_system, scoring_config,
                       elo_k_factor, competition_class, status, created_at
                FROM league_seasons
                WHERE id = :id
            """)
            result = db.execute(query, {"id": season_id}).fetchone()

            if not result:
                return None

            return {
                "id": result[0],
                "name": result[1],
                "season_number": result[2],
                "start_date": result[3],
                "registration_deadline": result[4],
                "league_format": result[5],
                "format_config": result[6],  # PostgreSQL returns JSONB as dict
                "scoring_system": result[7],
                "scoring_config": result[8],
                "elo_k_factor": result[9],
                "competition_class": result[10],
                "status": result[11],
                "created_at": result[12]
            }
    except Exception as e:
        logger.error(f"Error getting season: {e}")
        return None

def list_seasons(limit: int = 20) -> List[dict]:
    """List all seasons (most recent first)"""
    try:
        with get_db() as db:
            query = text("""
                SELECT s.id, s.name, s.season_number, s.start_date,
                       s.league_format, s.scoring_system, s.status,
                       COUNT(p.id) as participant_count
                FROM league_seasons s
                LEFT JOIN league_participants p ON s.id = p.season_id
                GROUP BY s.id
                ORDER BY s.season_number DESC
                LIMIT :limit
            """)
            results = db.execute(query, {"limit": limit}).fetchall()

            return [
                {
                    "id": row[0],
                    "name": row[1],
                    "season_number": row[2],
                    "start_date": row[3],
                    "league_format": row[4],
                    "scoring_system": row[5],
                    "status": row[6],
                    "participant_count": row[7]
                }
                for row in results
            ]
    except Exception as e:
        logger.error(f"Error listing seasons: {e}")
        return []

# ═══════════════════════════════════════════════
# PLAYER OPERATIONS
# ═══════════════════════════════════════════════

def get_or_create_player(discord_id: str, discord_name: str, discord_avatar: Optional[str] = None) -> Optional[int]:
    """Get existing player or create new one"""
    try:
        with get_db() as db:
            # Try to get existing
            query = text("SELECT id FROM league_players WHERE discord_id = :discord_id")
            result = db.execute(query, {"discord_id": discord_id}).fetchone()

            if result:
                return result[0]

            # Create new
            insert_query = text("""
                INSERT INTO league_players (discord_id, discord_name, discord_avatar)
                VALUES (:discord_id, :discord_name, :discord_avatar)
                RETURNING id
            """)
            result = db.execute(insert_query, {
                "discord_id": discord_id,
                "discord_name": discord_name,
                "discord_avatar": discord_avatar
            }).fetchone()

            return result[0] if result else None
    except Exception as e:
        logger.error(f"Error getting/creating player: {e}")
        return None

def get_player_by_discord_id(discord_id: str) -> Optional[dict]:
    """Get player by Discord ID"""
    try:
        with get_db() as db:
            query = text("""
                SELECT id, discord_id, discord_name, discord_avatar,
                       global_elo, peak_elo, total_games, total_wins, total_draws, total_losses
                FROM league_players
                WHERE discord_id = :discord_id
            """)
            result = db.execute(query, {"discord_id": discord_id}).fetchone()

            if not result:
                return None

            return {
                "id": result[0],
                "discord_id": result[1],
                "discord_name": result[2],
                "discord_avatar": result[3],
                "global_elo": result[4],
                "peak_elo": result[5],
                "total_games": result[6],
                "total_wins": result[7],
                "total_draws": result[8],
                "total_losses": result[9]
            }
    except Exception as e:
        logger.error(f"Error getting player: {e}")
        return None

# Additional CRUD functions for participants, matches, etc.
# ... (continue with similar pattern)
```

---

## Phase 4: Backend - Service Layer (Strategy Pattern)

### 4.1 Abstract Base Classes

**File:** `league/services/base.py` (new file)

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple

class BaseFormatHandler(ABC):
    """Abstract base class for league formats"""

    def __init__(self, season: dict):
        self.season = season
        self.config = season.get('format_config', {})

    @abstractmethod
    def validate_config(self) -> Tuple[bool, Optional[str]]:
        """Validate format configuration"""
        pass

    @abstractmethod
    def initialize_season(self, participants: List[dict]) -> bool:
        """Initialize season structure (e.g., assign groups)"""
        pass

    @abstractmethod
    def get_next_matches(self) -> List[Dict[str, Any]]:
        """Get upcoming matches to be played"""
        pass

    @abstractmethod
    def record_match_result(self, match: dict, participant1: dict, participant2: dict) -> bool:
        """Update standings after match"""
        pass

    @abstractmethod
    def get_standings(self) -> Dict[str, Any]:
        """Get current standings"""
        pass

    @abstractmethod
    def can_advance_phase(self) -> Tuple[bool, Optional[str]]:
        """Check if can move to next phase"""
        pass

    @abstractmethod
    def advance_phase(self) -> str:
        """Advance to next phase"""
        pass

class BaseScoringSystem(ABC):
    """Abstract base class for scoring systems"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    @abstractmethod
    def validate_config(self) -> Tuple[bool, Optional[str]]:
        """Validate scoring configuration"""
        pass

    @abstractmethod
    def calculate_points(self, player_score: int, opponent_score: int) -> int:
        """Calculate ranking points for player"""
        pass

    @abstractmethod
    def get_match_outcome(self, player_score: int, opponent_score: int) -> str:
        """Determine match outcome: 'win', 'draw', 'loss'"""
        pass

    @abstractmethod
    def get_display_format(self) -> Dict[str, Any]:
        """Return display format information"""
        pass
```

### 4.2 Concrete Implementation - Group Playoff Format

**File:** `league/services/formats/group_playoff.py` (new file)

```python
from typing import List, Dict, Any, Optional, Tuple
import random
import logging
from league.services.base import BaseFormatHandler
import league.database as db

logger = logging.getLogger(__name__)

class GroupPlayoffHandler(BaseFormatHandler):
    """
    Group + Playoff format handler

    Expected config:
    {
        "num_groups": 4,
        "max_unplayed_games": 1,
        "use_elo_for_grouping": false
    }
    """

    def validate_config(self) -> Tuple[bool, Optional[str]]:
        if "num_groups" not in self.config:
            return False, "num_groups required in format_config"

        if self.config["num_groups"] < 2:
            return False, "num_groups must be at least 2"

        return True, None

    def initialize_season(self, participants: List[dict]) -> bool:
        """Assign players to groups"""
        try:
            num_groups = self.config["num_groups"]
            use_elo = self.config.get("use_elo_for_grouping", False)

            if use_elo:
                # Sort by starting ELO (snake draft style)
                participants.sort(key=lambda p: p['starting_elo'], reverse=True)
            else:
                # Random assignment
                random.shuffle(participants)

            # Assign group numbers
            for i, participant in enumerate(participants):
                group_num = (i % num_groups) + 1
                db.update_participant_group(participant['id'], group_num)

            return True
        except Exception as e:
            logger.error(f"Error initializing season: {e}")
            return False

    def get_standings(self) -> Dict[str, Any]:
        """Get group standings"""
        num_groups = self.config["num_groups"]
        standings = {}

        for group_num in range(1, num_groups + 1):
            participants = db.get_group_participants(self.season['id'], group_num)

            # Sort by points
            participants.sort(key=lambda p: p['group_points'], reverse=True)

            standings[f"group_{group_num}"] = [
                {
                    "position": i + 1,
                    "player_id": p['player_id'],
                    "player_name": p['player_name'],
                    "points": p['group_points'],
                    "games_played": p['group_games_played'],
                    "avg_score": float(p['group_avg_score'] or 0),
                    "current_elo": p['current_season_elo']
                }
                for i, p in enumerate(participants)
            ]

        return {
            "type": "group_standings",
            "groups": standings
        }

    # ... additional methods
```

### 4.3 Concrete Implementation - AoS Differential Scoring

**File:** `league/services/scoring/aos_differential.py` (new file)

```python
from typing import Dict, Any, Tuple, Optional
from league.services.base import BaseScoringSystem

class AOSDifferentialScoring(BaseScoringSystem):
    """
    AoS Differential scoring system

    Win: 1000 + bonus
    Draw: 600 + bonus
    Loss: 200 + bonus
    Bonus: (score - opponent_score + 50), capped [0, 100]

    Default config:
    {
        "base_win": 1000,
        "base_draw": 600,
        "base_loss": 200,
        "bonus_offset": 50,
        "bonus_min": 0,
        "bonus_max": 100
    }
    """

    DEFAULT_CONFIG = {
        "base_win": 1000,
        "base_draw": 600,
        "base_loss": 200,
        "bonus_offset": 50,
        "bonus_min": 0,
        "bonus_max": 100
    }

    def __init__(self, config: Dict[str, Any] = None):
        merged = {**self.DEFAULT_CONFIG, **(config or {})}
        super().__init__(merged)

    def validate_config(self) -> Tuple[bool, Optional[str]]:
        required = ["base_win", "base_draw", "base_loss", "bonus_max"]
        for field in required:
            if field not in self.config:
                return False, f"Missing required field: {field}"

        return True, None

    def calculate_points(self, player_score: int, opponent_score: int) -> int:
        # Determine base
        if player_score > opponent_score:
            base = self.config["base_win"]
        elif player_score == opponent_score:
            base = self.config["base_draw"]
        else:
            base = self.config["base_loss"]

        # Calculate bonus
        diff = player_score - opponent_score
        bonus = diff + self.config["bonus_offset"]
        bonus = max(self.config["bonus_min"], min(self.config["bonus_max"], bonus))

        return base + bonus

    def get_match_outcome(self, player_score: int, opponent_score: int) -> str:
        if player_score > opponent_score:
            return "win"
        elif player_score == opponent_score:
            return "draw"
        else:
            return "loss"

    def get_display_format(self) -> Dict[str, Any]:
        return {
            "type": "differential",
            "labels": {
                "points_column": "Points",
                "description": f"Win: {self.config['base_win']}+bonus, Draw: {self.config['base_draw']}+bonus, Loss: {self.config['base_loss']}+bonus"
            },
            "max_points": self.config["base_win"] + self.config["bonus_max"]
        }
```

### 4.4 Factory Pattern

**File:** `league/services/factory.py` (new file)

```python
from typing import Optional
from league.services.base import BaseFormatHandler, BaseScoringSystem
from league.services.formats.group_playoff import GroupPlayoffHandler
from league.services.scoring.aos_differential import AOSDifferentialScoring

class FormatHandlerFactory:
    """Factory for creating format handlers"""

    _handlers = {
        "group_playoff": GroupPlayoffHandler,
        # Future: "swiss": SwissHandler,
    }

    @classmethod
    def create(cls, season: dict) -> BaseFormatHandler:
        handler_class = cls._handlers.get(season['league_format'])

        if not handler_class:
            raise ValueError(f"Unknown league format: {season['league_format']}")

        handler = handler_class(season)

        is_valid, error = handler.validate_config()
        if not is_valid:
            raise ValueError(f"Invalid format config: {error}")

        return handler

class ScoringSystemFactory:
    """Factory for creating scoring systems"""

    _systems = {
        "aos_differential": AOSDifferentialScoring,
        # Future: "win_draw_loss": WinDrawLossScoring,
    }

    @classmethod
    def create(cls, season: dict) -> BaseScoringSystem:
        system_class = cls._systems.get(season['scoring_system'])

        if not system_class:
            raise ValueError(f"Unknown scoring system: {season['scoring_system']}")

        system = system_class(season['scoring_config'])

        is_valid, error = system.validate_config()
        if not is_valid:
            raise ValueError(f"Invalid scoring config: {error}")

        return system
```

### 4.5 ELO Service

**File:** `league/services/elo.py` (new file)

```python
import math
from typing import Tuple

class EloService:
    """ELO rating calculation service"""

    @staticmethod
    def calculate_expected_score(rating_a: int, rating_b: int) -> float:
        """Calculate expected score for player A against player B"""
        return 1 / (1 + math.pow(10, (rating_b - rating_a) / 400))

    @staticmethod
    def calculate_new_ratings(
        rating_a: int,
        rating_b: int,
        score_a: float,  # 1.0 for win, 0.5 for draw, 0.0 for loss
        k_factor: int = 32
    ) -> Tuple[int, int, int, int]:
        """
        Calculate new ELO ratings

        Returns:
            (new_rating_a, new_rating_b, change_a, change_b)
        """
        expected_a = EloService.calculate_expected_score(rating_a, rating_b)
        expected_b = 1 - expected_a

        change_a = round(k_factor * (score_a - expected_a))
        change_b = round(k_factor * ((1 - score_a) - expected_b))

        new_rating_a = rating_a + change_a
        new_rating_b = rating_b + change_b

        return new_rating_a, new_rating_b, change_a, change_b
```

---

## Phase 5: Backend - API Endpoints

### 5.1 Main API Router

**File:** `league/main.py` (new file)

Following Herald's pattern with FastAPI.

```python
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
import logging
from datetime import datetime

import league.database as db
from league.models import (
    SeasonCreateRequest,
    SeasonResponse,
    PlayerRegisterRequest,
    MatchSubmitRequest,
    MatchResponse,
    StandingsResponse
)
from league.services.factory import FormatHandlerFactory, ScoringSystemFactory
from league.services.elo import EloService

logger = logging.getLogger(__name__)

app = FastAPI(
    title="League API - Squig League",
    description="Tournament and league management",
    version="0.1.0"
)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# ═══════════════════════════════════════════════
# SEASON ENDPOINTS
# ═══════════════════════════════════════════════

@app.post("/api/league/seasons/create")
@limiter.limit("5/hour")
async def create_season(request: Request, data: SeasonCreateRequest):
    """Create a new league season"""
    try:
        season_id = db.create_season(
            name=data.name,
            season_number=data.season_number,
            start_date=data.start_date,
            league_format=data.league_format.value,
            format_config=data.format_config,
            scoring_system=data.scoring_system.value,
            scoring_config=data.scoring_config,
            elo_k_factor=data.elo_k_factor,
            competition_class=data.competition_class.value,
            registration_deadline=data.registration_deadline
        )

        if not season_id:
            raise HTTPException(500, "Failed to create season")

        return {"season_id": season_id, "message": "Season created successfully"}

    except Exception as e:
        logger.error(f"Error creating season: {e}")
        raise HTTPException(500, "Internal server error")

@app.get("/api/league/seasons")
async def list_seasons():
    """List all seasons"""
    seasons = db.list_seasons()
    return {"seasons": seasons}

@app.get("/api/league/seasons/{season_id}")
async def get_season(season_id: int):
    """Get season details"""
    season = db.get_season(season_id)
    if not season:
        raise HTTPException(404, "Season not found")
    return season

# ═══════════════════════════════════════════════
# MATCH ENDPOINTS
# ═══════════════════════════════════════════════

@app.post("/api/league/matches/submit", response_model=MatchResponse)
@limiter.limit("20/hour")
async def submit_match(request: Request, data: MatchSubmitRequest):
    """
    Submit match result - universal for all formats
    """

    # Get season
    season = db.get_season(data.season_id)
    if not season:
        raise HTTPException(404, "Season not found")

    # Get players
    p1 = db.get_player_by_discord_id(data.player1_discord_id)
    p2 = db.get_player_by_discord_id(data.player2_discord_id)

    if not p1 or not p2:
        raise HTTPException(404, "Player not found")

    # Create handler and scoring system
    format_handler = FormatHandlerFactory.create(season)
    scoring_system = ScoringSystemFactory.create(season)

    # Calculate points
    p1_points = scoring_system.calculate_points(data.player1_score, data.player2_score)
    p2_points = scoring_system.calculate_points(data.player2_score, data.player1_score)

    # Determine winner
    outcome = scoring_system.get_match_outcome(data.player1_score, data.player2_score)
    winner_id = p1['id'] if outcome == 'win' else (p2['id'] if outcome == 'loss' else None)

    # Calculate ELO if applicable
    elo_change_p1 = None
    elo_change_p2 = None

    if season['counts_for_elo']:
        score_p1 = 1.0 if outcome == 'win' else (0.5 if outcome == 'draw' else 0.0)
        new_elo_p1, new_elo_p2, elo_change_p1, elo_change_p2 = EloService.calculate_new_ratings(
            p1['global_elo'],
            p2['global_elo'],
            score_p1,
            season['elo_k_factor']
        )

        # Update player ELOs
        db.update_player_elo(p1['id'], new_elo_p1, elo_change_p1)
        db.update_player_elo(p2['id'], new_elo_p2, elo_change_p2)

    # Create match record
    match_id = db.create_match(
        season_id=data.season_id,
        phase=data.phase,
        player1_id=p1['id'],
        player2_id=p2['id'],
        player1_score=data.player1_score,
        player2_score=data.player2_score,
        player1_points=p1_points,
        player2_points=p2_points,
        winner_id=winner_id,
        elo_change_p1=elo_change_p1,
        elo_change_p2=elo_change_p2,
        mission=data.mission,
        submitted_by=data.submitted_by
    )

    if not match_id:
        raise HTTPException(500, "Failed to create match")

    # Update participant standings (format-specific)
    part1 = db.get_participant(p1['id'], data.season_id)
    part2 = db.get_participant(p2['id'], data.season_id)

    match_data = db.get_match(match_id)
    format_handler.record_match_result(match_data, part1, part2)

    # Update player stats
    db.update_player_stats(p1['id'], outcome == 'win', outcome == 'draw')
    db.update_player_stats(p2['id'], outcome == 'loss', outcome == 'draw')

    return MatchResponse(
        id=match_id,
        phase=data.phase,
        player1_name=p1['discord_name'],
        player2_name=p2['discord_name'],
        player1_score=data.player1_score,
        player2_score=data.player2_score,
        player1_points=p1_points,
        player2_points=p2_points,
        winner_name=(p1['discord_name'] if outcome == 'win' else
                    (p2['discord_name'] if outcome == 'loss' else 'Draw')),
        elo_change_p1=elo_change_p1,
        elo_change_p2=elo_change_p2,
        match_date=datetime.now()
    )

@app.get("/api/league/seasons/{season_id}/standings", response_model=StandingsResponse)
async def get_standings(season_id: int):
    """Get season standings - universal, returns format-specific data"""
    season = db.get_season(season_id)
    if not season:
        raise HTTPException(404, "Season not found")

    format_handler = FormatHandlerFactory.create(season)
    standings = format_handler.get_standings()

    scoring_system = ScoringSystemFactory.create(season)
    display_format = scoring_system.get_display_format()

    return StandingsResponse(
        season_id=season_id,
        season_name=season['name'],
        league_format=season['league_format'],
        standings=standings,
        display_format=display_format
    )
```

---

## Phase 6: Frontend - Alpine.js Components

### 6.1 Season List Page

**File:** `frontend/public/modules/league/seasons.js` (new file)

```javascript
function leagueSeasonsPage() {
    return {
        seasons: [],
        loading: true,
        error: null,

        async init() {
            await this.loadSeasons();
        },

        async loadSeasons() {
            this.loading = true;
            try {
                const res = await fetch('/api/league/seasons');
                if (res.ok) {
                    const data = await res.json();
                    this.seasons = data.seasons;
                } else {
                    this.error = 'Failed to load seasons';
                }
            } catch (err) {
                this.error = 'Network error';
            } finally {
                this.loading = false;
            }
        },

        getStatusBadge(status) {
            const badges = {
                'registration': 'bg-blue-500',
                'group_phase': 'bg-green-500',
                'playoffs': 'bg-yellow-500',
                'completed': 'bg-gray-500'
            };
            return badges[status] || 'bg-gray-500';
        }
    };
}

// HTML template (inline for simplicity, can be external)
window.leagueSeasonsPage = function() {
    return `
        <div x-data="leagueSeasonsPage()" x-init="init()" class="container mx-auto px-4 py-8">
            <h1 class="text-4xl font-bold mb-8">League Seasons</h1>

            <template x-if="loading">
                <p>Loading seasons...</p>
            </template>

            <template x-if="error">
                <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
                    <span x-text="error"></span>
                </div>
            </template>

            <template x-if="!loading && !error">
                <div class="grid gap-4">
                    <template x-for="season in seasons" :key="season.id">
                        <div class="bg-white border rounded-lg p-6 hover:shadow-lg transition">
                            <div class="flex justify-between items-start">
                                <div>
                                    <h3 class="text-2xl font-semibold" x-text="season.name"></h3>
                                    <p class="text-gray-600">
                                        Format: <span x-text="season.league_format"></span> |
                                        Scoring: <span x-text="season.scoring_system"></span>
                                    </p>
                                    <p class="text-gray-500">
                                        Participants: <span x-text="season.participant_count"></span>
                                    </p>
                                </div>
                                <span
                                    class="px-3 py-1 rounded-full text-white text-sm"
                                    :class="getStatusBadge(season.status)"
                                    x-text="season.status"
                                ></span>
                            </div>
                            <div class="mt-4">
                                <a
                                    :href="'/league/season/' + season.id"
                                    class="text-blue-600 hover:underline"
                                >
                                    View Details →
                                </a>
                            </div>
                        </div>
                    </template>
                </div>
            </template>
        </div>
    `;
};
```

### 6.2 Standings Component (Universal)

**File:** `frontend/public/modules/league/standings.js` (new file)

```javascript
function leagueStandingsComponent(seasonId) {
    return {
        seasonId: seasonId,
        standings: null,
        displayFormat: null,
        loading: true,

        async init() {
            await this.loadStandings();
        },

        async loadStandings() {
            this.loading = true;
            try {
                const res = await fetch(`/api/league/seasons/${this.seasonId}/standings`);
                if (res.ok) {
                    const data = await res.json();
                    this.standings = data.standings;
                    this.displayFormat = data.display_format;
                    this.leagueFormat = data.league_format;
                }
            } catch (err) {
                console.error('Error loading standings:', err);
            } finally {
                this.loading = false;
            }
        },

        renderStandings() {
            if (!this.standings) return '';

            // Dispatch to format-specific renderer
            switch (this.standings.type) {
                case 'group_standings':
                    return this.renderGroupStandings();
                default:
                    return '<p>Unknown standings format</p>';
            }
        },

        renderGroupStandings() {
            let html = '<div class="grid grid-cols-1 md:grid-cols-2 gap-6">';

            for (const [groupKey, players] of Object.entries(this.standings.groups)) {
                html += `
                    <div class="bg-white border rounded-lg p-4">
                        <h3 class="text-xl font-semibold mb-4">${groupKey.replace('group_', 'Group ')}</h3>
                        <table class="w-full">
                            <thead class="bg-gray-100">
                                <tr>
                                    <th class="p-2 text-left">#</th>
                                    <th class="p-2 text-left">Player</th>
                                    <th class="p-2 text-right">Points</th>
                                    <th class="p-2 text-right">GP</th>
                                    <th class="p-2 text-right">ELO</th>
                                </tr>
                            </thead>
                            <tbody>
                `;

                players.forEach(player => {
                    html += `
                        <tr class="border-t hover:bg-gray-50">
                            <td class="p-2">${player.position}</td>
                            <td class="p-2">${player.player_name}</td>
                            <td class="p-2 text-right font-semibold">${player.points}</td>
                            <td class="p-2 text-right">${player.games_played}</td>
                            <td class="p-2 text-right">${player.current_elo}</td>
                        </tr>
                    `;
                });

                html += `
                            </tbody>
                        </table>
                    </div>
                `;
            }

            html += '</div>';
            return html;
        }
    };
}
```

### 6.3 Additional Frontend Pages (Summary)

Following the same pattern as above, create these additional pages:

#### **Season Detail Page**
**File:** `frontend/public/modules/league/season-detail.js`

- Tabbed interface: Standings, Matches, Participants, Info
- Displays season header (name, status, dates)
- Integrates standings component from 6.2
- Match history table
- Player roster grid

**APIs used:**
- `/api/league/seasons/{id}`
- `/api/league/seasons/{id}/standings`
- `/api/league/seasons/{id}/matches`
- `/api/league/seasons/{id}/participants`

#### **Match Submission Form**
**File:** `frontend/public/modules/league/submit-match.js`

- Form with fields: season dropdown, player names, scores, mission
- Real-time validation (scores 0-100)
- Result preview (calculated points, ELO changes)
- POST to `/api/league/matches/submit`

#### **Player Profile Page**
**File:** `frontend/public/modules/league/player.js`

- Player card (avatar, name, ELO)
- Career statistics table
- Match history list
- Season participation badges

**API:** `/api/league/players/{discord_id}`

#### **Global Leaderboard**
**File:** `frontend/public/modules/league/leaderboard.js`

- ELO rankings table
- Filters (all-time, current season, min games)
- Sortable columns

**API:** `/api/league/leaderboard`

#### **League Home/Dashboard**
**File:** `frontend/public/modules/league/home.js`

- Hero section
- Quick stats (seasons, players, matches)
- Recent match results
- Call-to-action buttons

**API:** `/api/league/stats`

### 6.4 Routing Integration

**Update:** `frontend/public/src/main.js`

Add league routes to the `parseRoute()` method and corresponding page loading logic in `loadPage()` method. Follow the existing Herald pattern for URL parsing and dynamic page loading.

**Routes to add:**
- `/league` or `/league/` → League home page
- `/league/seasons` → Season list
- `/league/season/{id}` → Season detail
- `/league/player/{discord_id}` → Player profile
- `/league/submit-match` → Match submission form
- `/league/leaderboard` → Global leaderboard

### 6.5 Navigation Menu Updates

**Update:** `frontend/public/index.html`

Add league navigation link in header (around line 84) alongside existing Herald link.

Add script tags for all league module JavaScript files before closing body tag (around line 118):
- `home.js`
- `seasons.js`
- `season-detail.js`
- `standings.js`
- `submit-match.js`
- `player.js`
- `leaderboard.js`
- `components.js`

### 6.6 Reusable Components

**File:** `frontend/public/modules/league/components.js` (helper functions)

Create utility functions for common UI elements:

```javascript
// Status badge helper
function leagueStatusBadge(status) {
    const badges = {
        'registration': 'bg-blue-500',
        'group_phase': 'bg-green-500',
        'playoffs': 'bg-yellow-500',
        'completed': 'bg-gray-500'
    };
    const color = badges[status] || 'bg-gray-500';
    return `<span class="px-3 py-1 rounded-full text-white text-sm ${color}">${status}</span>`;
}

// ELO change indicator
function eloChangeIndicator(change) {
    if (change === null || change === undefined) return '';
    const color = change > 0 ? 'text-green-500' : 'text-red-500';
    const sign = change > 0 ? '+' : '';
    return `<span class="${color} font-semibold">${sign}${change}</span>`;
}

// Format badge
function formatBadge(format) {
    const labels = {
        'group_playoff': 'Groups + Playoff',
        'swiss': 'Swiss',
        'pure_playoff': 'Single Elimination'
    };
    return labels[format] || format;
}

// Scoring system label
function scoringLabel(system) {
    const labels = {
        'aos_differential': 'AoS Differential',
        'win_draw_loss': 'W/D/L (3/1/0)',
        'twenty_zero': '20-0 System'
    };
    return labels[system] || system;
}
```

### 6.7 Frontend File Structure

Complete frontend module structure:

```
frontend/public/modules/league/
├── components.js           # Reusable helper functions
├── home.js                 # League home/dashboard
├── seasons.js              # Season list page
├── season-detail.js        # Season detail with tabs
├── standings.js            # Standings component (universal)
├── submit-match.js         # Match submission form
├── player.js               # Player profile page
└── leaderboard.js          # Global leaderboard
```

**Total:** 8 new JavaScript files

### 6.8 Mobile Responsiveness

All pages should use Tailwind responsive utilities:

- **Grid layouts:** `grid-cols-1 md:grid-cols-2 lg:grid-cols-3`
- **Padding:** `px-4 sm:px-6 lg:px-8`
- **Text sizes:** `text-xl sm:text-2xl lg:text-3xl`
- **Hide on mobile:** `hidden md:block`
- **Tabs:** Stack vertically on mobile, horizontal on desktop

### 6.9 Frontend Implementation Priority

**Phase 1 (MVP):**
1. Routing integration (main.js updates)
2. Navigation menu
3. Components.js helpers
4. League home page (simple)
5. Season list page
6. Standings component

**Phase 2 (Core Features):**
7. Season detail page with tabs
8. Match submission form
9. Player profile page

**Phase 3 (Enhanced):**
10. Leaderboard
11. Admin panel (if needed)
12. ELO graphs/charts

---

## Phase 7: Integration & Testing

### 7.1 Test Checklist

**Database Tests:**
- [ ] All tables created successfully
- [ ] Indexes working correctly
- [ ] JSONB columns storing/retrieving data
- [ ] Foreign key constraints working

**Backend Tests:**
- [ ] Season CRUD operations
- [ ] Player registration
- [ ] Match submission
- [ ] ELO calculation accuracy
- [ ] Factory pattern creates correct handlers
- [ ] Group assignment logic

**API Tests:**
- [ ] All endpoints return correct status codes
- [ ] Pydantic validation working
- [ ] Rate limiting functional
- [ ] Error responses formatted correctly

**Frontend Tests:**
- [ ] Season list loads
- [ ] Standings display correctly
- [ ] Routing works
- [ ] Alpine.js reactivity functioning

### 7.2 Manual Testing Steps

```bash
# 1. Initialize database
docker-compose down -v
docker-compose up -d postgres
# Wait for PostgreSQL to initialize with schema

# 2. Start backend
docker-compose up -d app

# 3. Test API endpoints
curl http://localhost:8000/api/league/seasons

# 4. Create test season
curl -X POST http://localhost:8000/api/league/seasons/create \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Season 1",
    "season_number": 1,
    "start_date": "2025-01-01",
    "league_format": "group_playoff",
    "format_config": {"num_groups": 4},
    "scoring_system": "aos_differential",
    "elo_k_factor": 32,
    "competition_class": "local"
  }'

# 5. Test frontend
# Open browser: http://localhost:3000/league/
```

---

## Phase 8: Deployment Considerations

### 8.1 Docker Configuration

**Update:** `docker-compose.yml`

```yaml
services:
  app:
    # ... existing config
    volumes:
      - ./herald:/app/herald
      - ./league:/app/league  # Add league module
    environment:
      - DATABASE_URL=postgresql://squig:password@postgres:5432/squigleague
```

### 8.2 Nginx Configuration

**Update:** `nginx/nginx.conf`

```nginx
# Add league API routes
location /api/league/ {
    proxy_pass http://app:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

### 8.3 Environment Variables

**Add to `.env.prod`:**

```env
# League module settings
LEAGUE_ADMIN_DISCORD_ID=your_discord_id_here
LEAGUE_MAX_PLAYERS_PER_SEASON=32
LEAGUE_DEFAULT_K_FACTOR=32
```

---

## Phase 9: Future Extensibility

### 9.1 Adding Swiss Format (Example)

**File:** `league/services/formats/swiss.py`

```python
from league.services.base import BaseFormatHandler

class SwissHandler(BaseFormatHandler):
    """Swiss pairing format"""

    def validate_config(self):
        if "num_rounds" not in self.config:
            return False, "num_rounds required"
        return True, None

    def initialize_season(self, participants):
        # No initial grouping needed
        return True

    def get_next_matches(self):
        # Swiss pairing algorithm
        pass

    # ... implement all abstract methods
```

**Register in factory:**

```python
# league/services/factory.py
from league.services.formats.swiss import SwissHandler

FormatHandlerFactory._handlers["swiss"] = SwissHandler
```

### 9.2 Adding W/D/L Scoring (Example)

**File:** `league/services/scoring/win_draw_loss.py`

```python
from league.services.base import BaseScoringSystem

class WinDrawLossScoring(BaseScoringSystem):
    """3 points for win, 1 for draw, 0 for loss"""

    DEFAULT_CONFIG = {"win_points": 3, "draw_points": 1, "loss_points": 0}

    def calculate_points(self, player_score, opponent_score):
        if player_score > opponent_score:
            return self.config["win_points"]
        elif player_score == opponent_score:
            return self.config["draw_points"]
        else:
            return self.config["loss_points"]

    # ... implement other methods
```

**Register in factory:**

```python
ScoringSystemFactory._systems["win_draw_loss"] = WinDrawLossScoring
```

---

## Implementation Order

### Week 1: Foundation
1. Create database schema (`init.sql`)
2. Create Pydantic models (`league/models.py`)
3. Create database functions (`league/database.py`)
4. Test database operations

### Week 2: Service Layer
5. Create abstract base classes (`league/services/base.py`)
6. Implement AoS Differential scoring
7. Implement Group Playoff format handler
8. Create factories
9. Implement ELO service

### Week 3: API Layer
10. Create FastAPI routes (`league/main.py`)
11. Integrate with factories
12. Add rate limiting
13. Test all endpoints

### Week 4: Frontend
14. Create Alpine.js components
15. Implement routing
16. Build standings display
17. Add match submission form

### Week 5: Polish & Testing
18. End-to-end testing
19. Bug fixes
20. Documentation
21. Deployment

---

## Success Criteria

✅ **Database:**
- All tables created and indexed
- JSONB configs working
- Foreign keys enforced

✅ **Backend:**
- All CRUD operations functional
- Strategy pattern working
- ELO calculations accurate
- Factory creates correct instances

✅ **API:**
- All endpoints return correct data
- Rate limiting prevents abuse
- Error handling robust

✅ **Frontend:**
- Standings display correctly
- Routing works smoothly
- Forms submit successfully
- Loading states visible

✅ **Integration:**
- Full match flow works end-to-end
- ELO updates properly
- Standings refresh after matches
- Phase transitions work

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Database schema changes | Use ALTER TABLE carefully; test on staging first |
| ELO calculation bugs | Unit tests with known values; cross-check with online calculators |
| Factory pattern complexity | Start with 1 format + 1 scoring, add more later |
| Frontend state management | Keep Alpine.js components simple; use explicit data flow |
| Performance issues | Add database indexes; use connection pooling |
| Discord integration | Mock Discord API for local testing |

---

## Conclusion

This plan adapts the original league system design to Squig League's FastAPI + functional architecture. The Strategy Pattern enables future extensibility while keeping the current implementation simple and focused on Group + Playoff format with AoS Differential scoring.

The modular structure allows adding new formats and scoring systems without modifying core code - just create a new handler class and register it in the factory.
