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
-- INITIAL DATA (Optional)
-- ═══════════════════════════════════════════════

-- No initial data needed for Phase 1
