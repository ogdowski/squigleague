-- database/init.sql
-- Initial database schema for Squig League
-- Runs automatically when PostgreSQL container first starts
-- Created: 2025-01-13

-- Enable PostgreSQL extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ═══════════════════════════════════════════════
-- CORE SCHEMA (Phase 3 - Prepared but not used yet)
-- ═══════════════════════════════════════════════
-- This table is created now but will only be used when
-- authentication is implemented in Phase 3

CREATE TABLE IF NOT EXISTS core_users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    email_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_core_users_email ON core_users(email);
CREATE INDEX idx_core_users_username ON core_users(username);

COMMENT ON TABLE core_users IS 'User accounts - will be used in Phase 3 when authentication is added';

-- ═══════════════════════════════════════════════
-- HERALD SCHEMA (Phase 1 - Active now)
-- ═══════════════════════════════════════════════

-- Exchanges table - stores blind list exchanges
CREATE TABLE herald_exchanges (
    id TEXT PRIMARY KEY,                          -- Format: adjective-noun-verb-XXXX
    list_a TEXT NOT NULL,                         -- Player A's army list
    hash_a TEXT NOT NULL,                         -- SHA-256 hash of list_a
    timestamp_a TIMESTAMPTZ NOT NULL,             -- When Player A created the exchange
    list_b TEXT,                                  -- Player B's list (NULL until they respond)
    hash_b TEXT,                                  -- SHA-256 hash of list_b
    timestamp_b TIMESTAMPTZ,                      -- When Player B responded
    created_at TIMESTAMPTZ DEFAULT NOW(),         -- Record creation timestamp

    -- Phase 3: These foreign keys will be used when auth is added
    -- For now, they remain NULL (anonymous exchanges)
    user_id_a UUID REFERENCES core_users(id) ON DELETE SET NULL,
    user_id_b UUID REFERENCES core_users(id) ON DELETE SET NULL
);

-- Indexes for Herald exchanges
CREATE INDEX idx_herald_created_at ON herald_exchanges(created_at);
CREATE INDEX idx_herald_list_b_null ON herald_exchanges(list_b) WHERE list_b IS NULL;
CREATE INDEX idx_herald_user_a ON herald_exchanges(user_id_a) WHERE user_id_a IS NOT NULL;
CREATE INDEX idx_herald_user_b ON herald_exchanges(user_id_b) WHERE user_id_b IS NOT NULL;

COMMENT ON TABLE herald_exchanges IS 'Blind army list exchanges - Phase 1 active';
COMMENT ON COLUMN herald_exchanges.user_id_a IS 'Phase 3: Will link to user account';
COMMENT ON COLUMN herald_exchanges.user_id_b IS 'Phase 3: Will link to user account';

-- Request logging for security and rate limiting
CREATE TABLE herald_request_log (
    id SERIAL PRIMARY KEY,
    ip INET NOT NULL,                             -- Client IP address
    endpoint TEXT NOT NULL,                       -- Request endpoint
    timestamp TIMESTAMPTZ DEFAULT NOW(),          -- Request timestamp
    user_agent TEXT                               -- User agent string
);

-- Indexes for Herald request logging
CREATE INDEX idx_herald_log_ip_time ON herald_request_log(ip, timestamp);
CREATE INDEX idx_herald_log_timestamp ON herald_request_log(timestamp);

COMMENT ON TABLE herald_request_log IS 'HTTP request logging for abuse detection';

-- ═══════════════════════════════════════════════
-- FUTURE MODULE SCHEMAS (Placeholders for documentation)
-- ═══════════════════════════════════════════════

-- SCRIBE (Phase 2): Army list builder
-- Tables will be added when Scribe module is implemented
-- Planned tables: scribe_lists, scribe_templates

-- PATRON (Phase 4): Tournament and league management
-- Tables will be added when Patron module is implemented
-- Planned tables: patron_tournaments, patron_participants, patron_matches

-- KEEPER (Phase 5): Miniature collection manager
-- Tables will be added when Keeper module is implemented
-- Planned tables: keeper_collections, keeper_miniatures, keeper_photos

-- SQUIRE (Phase 6): Battle score tracker
-- Tables will be added when Squire module is implemented
-- Planned tables: squire_battles, squire_rounds, squire_scores

-- ═══════════════════════════════════════════════
-- LEAGUE SCHEMA (Phase 2 - Active now)
-- ═══════════════════════════════════════════════

-- Seasons table - represents a league season
CREATE TABLE IF NOT EXISTS league_seasons (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    season_number INTEGER NOT NULL,
    start_date DATE NOT NULL,
    registration_deadline DATE,

    -- Format configuration (Strategy Pattern via JSONB)
    league_format TEXT NOT NULL DEFAULT 'group_playoff',
    format_config JSONB DEFAULT '{}',

    -- Scoring system configuration
    scoring_system TEXT NOT NULL DEFAULT 'aos_differential',
    scoring_config JSONB DEFAULT '{}',

    -- ELO configuration
    elo_k_factor INTEGER NOT NULL DEFAULT 32,
    counts_for_elo BOOLEAN DEFAULT FALSE,
    competition_class TEXT DEFAULT 'local',

    -- Status tracking
    status TEXT NOT NULL DEFAULT 'registration',

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_league_seasons_status ON league_seasons(status);
CREATE INDEX idx_league_seasons_number ON league_seasons(season_number);

COMMENT ON TABLE league_seasons IS 'League seasons with extensible format and scoring configs';
COMMENT ON COLUMN league_seasons.format_config IS 'Format-specific config as JSON, e.g. {"num_groups": 4}';
COMMENT ON COLUMN league_seasons.scoring_config IS 'Scoring-specific config as JSON';

-- Players table - represents individual players
CREATE TABLE IF NOT EXISTS league_players (
    id SERIAL PRIMARY KEY,
    discord_id TEXT UNIQUE NOT NULL,
    discord_name TEXT NOT NULL,
    discord_avatar TEXT,

    -- Global ELO rating
    global_elo INTEGER NOT NULL DEFAULT 1500,
    peak_elo INTEGER NOT NULL DEFAULT 1500,

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

    -- Group assignment (format-specific)
    group_number INTEGER,

    -- Group phase statistics
    group_points INTEGER DEFAULT 0,
    group_games_played INTEGER DEFAULT 0,
    group_avg_score NUMERIC(6,2),

    -- Playoff tracking
    qualified_for_playoffs BOOLEAN DEFAULT FALSE,
    playoff_position INTEGER,

    -- ELO tracking for this season
    starting_elo INTEGER NOT NULL,
    current_season_elo INTEGER NOT NULL,

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

    -- Match phase
    phase TEXT NOT NULL,

    -- Players
    player1_id INTEGER NOT NULL REFERENCES league_players(id) ON DELETE CASCADE,
    player2_id INTEGER NOT NULL REFERENCES league_players(id) ON DELETE CASCADE,

    -- Battle scores
    player1_score INTEGER NOT NULL,
    player2_score INTEGER NOT NULL,

    -- Ranking points
    player1_points INTEGER NOT NULL,
    player2_points INTEGER NOT NULL,

    -- Match outcome
    winner_id INTEGER REFERENCES league_players(id),

    -- ELO changes
    elo_change_p1 INTEGER,
    elo_change_p2 INTEGER,
    k_factor_p1 INTEGER,
    k_factor_p2 INTEGER,
    counted_for_elo BOOLEAN DEFAULT FALSE,

    -- Match metadata
    mission TEXT,
    match_date TIMESTAMPTZ DEFAULT NOW(),
    status TEXT DEFAULT 'confirmed',

    -- Submission tracking
    submitted_by TEXT,
    submitted_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_league_matches_season ON league_matches(season_id);
CREATE INDEX idx_league_matches_players ON league_matches(player1_id, player2_id);
CREATE INDEX idx_league_matches_date ON league_matches(match_date DESC);

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
    change INTEGER NOT NULL,
    k_factor INTEGER NOT NULL,

    -- Match context
    opponent_id INTEGER REFERENCES league_players(id) ON DELETE SET NULL,
    match_result TEXT,

    timestamp TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_league_elo_player ON league_elo_history(player_id, timestamp DESC);
CREATE INDEX idx_league_elo_season ON league_elo_history(season_id);

COMMENT ON TABLE league_elo_history IS 'Historical ELO rating changes';

-- ═══════════════════════════════════════════════
-- INITIAL DATA (Optional)
-- ═══════════════════════════════════════════════

-- Example season for testing (optional)
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
    '{"num_groups": 4, "max_unplayed_games": 1, "use_elo_for_grouping": false}'::jsonb,
    'aos_differential',
    '{"base_win": 1000, "base_draw": 600, "base_loss": 200, "bonus_offset": 50, "bonus_max": 100}'::jsonb,
    32,
    false,
    'registration'
) ON CONFLICT DO NOTHING;
