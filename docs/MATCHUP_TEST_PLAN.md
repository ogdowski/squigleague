# Matchup Feature - Manual Test Script

## Test Flow

This script validates the matchup system end-to-end.

### Prerequisites
- Services running: `docker-compose ps`
- Frontend accessible: http://localhost/squire/matchup
- API accessible: http://localhost:8000/api/squire/health

---

## Test Case 1: Create Matchup

**Steps**:
1. Open http://localhost/squire/matchup
2. Select "Age of Sigmar"
3. Click "Create Matchup"

**Expected**:
- ✓ Matchup ID generated
- ✓ Share URL displayed
- ✓ Player submission form appears
- ✓ URL changes to `/squire/matchup/{id}`

---

## Test Case 2: Submit First List

**Steps**:
1. Enter player name: "Player 1"
2. Paste army list:
   ```
   Stormcast Eternals - 2000pts
   
   Lord-Imperatant (General)
   3x Vindictors
   5x Liberators
   ```
3. Click "Submit My List"

**Expected**:
- ✓ "List Submitted" message appears
- ✓ "Waiting for opponent..." displayed
- ✓ Polling starts (check every 5 seconds)
- ✓ Lists NOT visible yet

---

## Test Case 3: Second Player Joins

**Steps**:
1. Copy share URL
2. Open in new browser window/incognito
3. Enter player name: "Player 2"
4. Paste army list:
   ```
   Lumineth Realm-lords - 2000pts
   
   Scinari Cathallar (General)
   10x Vanari Auralan Wardens
   5x Vanari Dawnriders
   ```
5. Click "Submit My List"

**Expected**:
- ✓ Matchup summary appears immediately
- ✓ Battle plan generated
- ✓ Both army lists visible
- ✓ Both player names shown
- ✓ Battle plan includes deployment, objectives, victory conditions

---

## Test Case 4: View from First Player

**Steps**:
1. Return to first browser window
2. Wait for polling to detect update

**Expected**:
- ✓ Matchup summary appears
- ✓ Same battle plan shown
- ✓ Both lists visible
- ✓ No waiting message

---

## Test Case 5: Print Summary

**Steps**:
1. Click "Print Matchup Summary"

**Expected**:
- ✓ Print dialog opens
- ✓ All content visible in print preview
- ✓ Battle plan details included
- ✓ Both lists formatted correctly

---

## Test Case 6: API Direct Test

### Create Matchup
```bash
curl -X POST http://localhost:8000/api/squire/matchup/create \
  -H "Content-Type: application/json" \
  -d '{"game_system": "age_of_sigmar"}'
```

**Expected Response**:
```json
{
  "matchup_id": "abc123...",
  "game_system": "age_of_sigmar",
  "share_url": "/squire/matchup/abc123..."
}
```

### Submit First List
```bash
curl -X POST http://localhost:8000/api/squire/matchup/{MATCHUP_ID}/submit \
  -H "Content-Type: application/json" \
  -d '{
    "player_name": "API Player 1",
    "army_list": "Test list 1"
  }'
```

**Expected Response**:
```json
{
  "matchup_id": "abc123...",
  "game_system": "age_of_sigmar",
  "is_complete": false,
  "waiting_count": 1,
  "player1": null,
  "player2": null,
  "battle_plan": null
}
```

### Submit Second List
```bash
curl -X POST http://localhost:8000/api/squire/matchup/{MATCHUP_ID}/submit \
  -H "Content-Type: application/json" \
  -d '{
    "player_name": "API Player 2",
    "army_list": "Test list 2"
  }'
```

**Expected Response**:
```json
{
  "matchup_id": "abc123...",
  "game_system": "age_of_sigmar",
  "is_complete": true,
  "waiting_count": 2,
  "player1": {
    "name": "API Player 1",
    "army_list": "Test list 1",
    "submitted_at": "2025-11-25T..."
  },
  "player2": {
    "name": "API Player 2",
    "army_list": "Test list 2",
    "submitted_at": "2025-11-25T..."
  },
  "battle_plan": {
    "name": "...",
    "game_system": "age_of_sigmar",
    "deployment": "...",
    ...
  }
}
```

### Get Matchup
```bash
curl http://localhost:8000/api/squire/matchup/{MATCHUP_ID}
```

**Expected**: Same as submit second list response

---

## Error Cases

### Test: Invalid Game System
```bash
curl -X POST http://localhost:8000/api/squire/matchup/create \
  -H "Content-Type: application/json" \
  -d '{"game_system": "invalid"}'
```

**Expected**: HTTP 400 with error message

### Test: Submit to Full Matchup
```bash
# After both players submitted, try to submit third
curl -X POST http://localhost:8000/api/squire/matchup/{MATCHUP_ID}/submit \
  -H "Content-Type: application/json" \
  -d '{
    "player_name": "Player 3",
    "army_list": "Test list 3"
  }'
```

**Expected**: HTTP 404 with "Matchup already has two players"

### Test: Matchup Not Found
```bash
curl http://localhost:8000/api/squire/matchup/nonexistent
```

**Expected**: HTTP 404 with "Matchup nonexistent not found"

---

## Success Criteria

All tests pass:
- [x] Can create matchup
- [x] Can submit first list (hidden)
- [x] Can submit second list (triggers reveal)
- [x] Battle plan generated automatically
- [x] Both lists visible when complete
- [x] Polling works for real-time updates
- [x] Print functionality works
- [x] API returns correct responses
- [x] Error handling works

---

## Known Limitations

- Matchups stored in memory (lost on restart)
- No authentication (anyone can submit to matchup)
- No edit/delete functionality
- No matchup expiration
- No list validation

These are acceptable for MVP. Future enhancements in Phase 2.
