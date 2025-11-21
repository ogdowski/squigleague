-- Initialize test database with Herald schema
-- This is a simplified version of database/init.sql for testing

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Herald exchanges table
CREATE TABLE IF NOT EXISTS herald_exchanges (
    id TEXT PRIMARY KEY,
    list_a TEXT NOT NULL,
    hash_a TEXT NOT NULL,
    timestamp_a TIMESTAMPTZ NOT NULL,
    list_b TEXT,
    hash_b TEXT,
    timestamp_b TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Herald request logging
CREATE TABLE IF NOT EXISTS herald_request_log (
    id SERIAL PRIMARY KEY,
    ip TEXT,
    endpoint TEXT NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    user_agent TEXT
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_herald_created_at ON herald_exchanges(created_at);
CREATE INDEX IF NOT EXISTS idx_herald_list_b_null ON herald_exchanges(list_b) WHERE list_b IS NULL;
CREATE INDEX IF NOT EXISTS idx_herald_log_ip_time ON herald_request_log(ip, timestamp);
CREATE INDEX IF NOT EXISTS idx_herald_log_timestamp ON herald_request_log(timestamp);
