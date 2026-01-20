-- Add battle plan support to Herald exchanges
-- Migration: Add battle_plan_slug column
-- Date: 2026-01-19

ALTER TABLE herald_exchanges 
ADD COLUMN IF NOT EXISTS battle_plan_slug TEXT;

COMMENT ON COLUMN herald_exchanges.battle_plan_slug IS 'Slug of the selected battle plan (e.g., aos-passing-seasons)';

-- Optional: Add index if we want to query by battle plan
CREATE INDEX IF NOT EXISTS idx_herald_battle_plan ON herald_exchanges(battle_plan_slug) WHERE battle_plan_slug IS NOT NULL;
