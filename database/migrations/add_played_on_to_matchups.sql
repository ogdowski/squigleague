-- Add played_on column to matchups table
-- This field tracks when the matchup was actually played
-- Defaults to current timestamp, cannot be in the future

ALTER TABLE matchups 
ADD COLUMN played_on TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP;

-- Add constraint to prevent future dates
ALTER TABLE matchups
ADD CONSTRAINT chk_played_on_not_future 
CHECK (played_on <= CURRENT_TIMESTAMP);

-- Add constraint to ensure played_on is not before created_at
ALTER TABLE matchups
ADD CONSTRAINT chk_played_on_after_created 
CHECK (played_on >= created_at);
