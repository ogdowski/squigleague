-- Migration script: Herald exchanges → Matchups
-- Copies active herald_exchanges to new matchups table
-- Run this ONCE after deploying new version

-- Copy herald_exchanges to matchups table
INSERT INTO matchups (
    name,                    -- Use old exchange ID as name
    player1_id,             -- NULL (anonymous)
    player2_id,             -- NULL (anonymous)
    player1_list,           -- Copy list_a
    player2_list,           -- Copy list_b
    player1_submitted,      -- Always true (list_a exists)
    player2_submitted,      -- True if list_b exists
    map_name,               -- NULL (not used in old system)
    created_at,             -- Use timestamp_a
    expires_at,             -- created_at + 90 days
    revealed_at             -- Use timestamp_b if both lists submitted
)
SELECT
    id AS name,
    NULL AS player1_id,
    NULL AS player2_id,
    list_a AS player1_list,
    list_b AS player2_list,
    TRUE AS player1_submitted,
    CASE WHEN list_b IS NOT NULL THEN TRUE ELSE FALSE END AS player2_submitted,
    NULL AS map_name,
    timestamp_a AS created_at,
    timestamp_a + INTERVAL '90 days' AS expires_at,
    CASE WHEN list_b IS NOT NULL THEN timestamp_b ELSE NULL END AS revealed_at
FROM herald_exchanges
WHERE timestamp_a > NOW() - INTERVAL '90 days'  -- Only migrate recent exchanges
  AND NOT EXISTS (
      SELECT 1 FROM matchups WHERE name = herald_exchanges.id
  );  -- Skip if already migrated

-- Verify migration
SELECT
    'Migrated exchanges:' AS info,
    COUNT(*) AS count
FROM matchups
WHERE name IN (SELECT id FROM herald_exchanges);
