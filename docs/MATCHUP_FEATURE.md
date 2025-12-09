# Matchup System - Feature Documentation

**Date**: 2025-11-25  
**Status**: ✅ Implemented  
**Version**: 0.2.0

---

## Overview

The Matchup System allows two players to:
1. Select a game system (AoS, 40k, Old World)
2. Exchange army lists
3. Receive a randomized battle plan for their game

**This is NOT a tournament feature.** It's a standalone tool for casual matchups.

---

## User Flow

```
Player 1                          Player 2
   |                                 |
   | 1. Create matchup              |
   |    (select system)              |
   v                                 |
[Matchup Created]                    |
   |                                 |
   | 2. Share link ----------------> |
   |                                 |
   | 3. Submit list                  | 4. Open link
   v                                 v
[Waiting for opponent]         [Submit list form]
   |                                 |
   |                                 | 5. Submit list
   |                                 v
   | <------ Battle plan generated ----
   v                                 v
[Matchup Summary]              [Matchup Summary]
   |                                 |
   | • Both lists visible            |
   | • Battle plan details           |
   | • Can print                     |
```

---

## API Endpoints

### POST `/api/squire/matchup/create`

Create a new matchup.

**Request**:
```json
{
  "game_system": "age_of_sigmar"
}
```

**Response**:
```json
{
  "matchup_id": "XyZ123AbC456",
  "game_system": "age_of_sigmar",
  "share_url": "/squire/matchup/XyZ123AbC456"
}
```

---

### POST `/api/squire/matchup/{matchup_id}/submit`

Submit army list to matchup.

**Request**:
```json
{
  "player_name": "John Doe",
  "army_list": "Stormcast Eternals - 2000pts\n\nLord-Imperatant...\n"
}
```

**Response** (first player):
```json
{
  "matchup_id": "XyZ123AbC456",
  "game_system": "age_of_sigmar",
  "is_complete": false,
  "waiting_count": 1,
  "player1": null,
  "player2": null,
  "battle_plan": null
}
```

**Response** (second player - triggers battle plan):
```json
{
  "matchup_id": "XyZ123AbC456",
  "game_system": "age_of_sigmar",
  "is_complete": true,
  "waiting_count": 2,
  "player1": {
    "name": "John Doe",
    "army_list": "...",
    "submitted_at": "2025-11-25T12:34:56"
  },
  "player2": {
    "name": "Jane Smith",
    "army_list": "...",
    "submitted_at": "2025-11-25T12:35:12"
  },
  "battle_plan": {
    "name": "Grasp of Thorns",
    "game_system": "age_of_sigmar",
    "deployment": "frontal_assault",
    "deployment_description": "...",
    "primary_objective": "...",
    "secondary_objectives": [...],
    "victory_conditions": "...",
    "turn_limit": 5,
    "special_rules": [...],
    "battle_tactics": [...]
  }
}
```

---

### GET `/api/squire/matchup/{matchup_id}`

Get matchup details. Returns same structure as submit endpoint.

**Note**: Lists and battle plan are only visible when `is_complete` is `true`.

---

## Frontend Routes

### `/squire/matchup`

Main matchup page. Shows:
- Create new matchup form (if no matchup ID in URL)
- Submit list form (if matchup created but not submitted)
- Waiting screen (if submitted, waiting for opponent)
- Matchup summary (if both players submitted)

### `/squire/matchup/{matchup_id}`

Direct link to specific matchup. Automatically loads matchup data.

---

## Key Features

✅ **List Privacy**: Lists are hidden until BOTH players submit  
✅ **Automatic Battle Plan**: Generated when second player submits  
✅ **Real-time Updates**: Frontend polls every 5 seconds  
✅ **Copy Share Link**: One-click copy of matchup URL  
✅ **Print Summary**: Clean print view of matchup + battle plan  
✅ **No Authentication Required**: Anonymous matchups  

---

## Technical Implementation

### Backend (`squire/matchup.py`)

**Data Models**:
```python
@dataclass
class MatchupPlayer:
    name: str
    army_list: str
    submitted_at: datetime

@dataclass
class Matchup:
    matchup_id: str
    game_system: GameSystem
    player1: Optional[MatchupPlayer]
    player2: Optional[MatchupPlayer]
    battle_plan: Optional[BattlePlan]
```

**Functions**:
- `create_matchup(game_system)` - Create new matchup
- `get_matchup(matchup_id)` - Retrieve matchup
- `submit_list(matchup_id, name, list)` - Add player to matchup

### Frontend (`modules/squire/matchup.js`)

**Alpine.js Component**:
```javascript
function matchupManager() {
  return {
    selectedSystem: null,
    matchupId: null,
    matchup: null,
    
    createMatchup(),
    submitList(),
    loadMatchup(),
    startPolling(),  // Every 5 seconds
    getShareUrl(),
    copyShareLink()
  }
}
```

---

## Data Storage

**Current**: In-memory dictionary (lost on restart)

**Limitation**: 
- Matchups not persisted
- Lost when backend restarts
- No cleanup of old matchups

**Future Enhancement**: 
- PostgreSQL table
- TTL/expiration
- Matchup history

---

## Security Considerations

### Current Status
- ❌ No authentication
- ❌ No authorization
- ❌ Matchup IDs are random but predictable length
- ❌ Anyone with link can view matchup
- ❌ No rate limiting

### Acceptable for MVP Because:
- Not sensitive data (army lists are meant to be shared)
- No personal information collected
- Tool is for casual play, not competitive
- Matchup IDs use `secrets.token_urlsafe(12)` (cryptographically secure)

### Future Enhancements:
- Optional password protection
- Rate limiting on matchup creation
- TTL/expiration
- User accounts with matchup history

---

## User Stories Completed

- ✅ **US-006**: Create Matchup with System Selection
- ✅ **US-007**: Submit Army List to Matchup
- ✅ **US-008**: View Matchup Summary with Battle Plan

See `docs/user-stories.md` for full acceptance criteria.

---

## Testing

See `docs/MATCHUP_TEST_PLAN.md` for:
- Manual UI test cases
- API test examples
- Error case validation
- Success criteria

---

## Example Usage

### Scenario: Two Friends Want to Play

1. **Alex** opens http://localhost/squire/matchup
2. Selects "Age of Sigmar"
3. Clicks "Create Matchup"
4. Copies share link: `http://localhost/squire/matchup/XyZ123AbC456`
5. Sends link to **Beth** via Discord/WhatsApp
6. **Alex** enters name and pastes army list, clicks Submit
7. **Alex** sees "Waiting for opponent..."
8. **Beth** opens link Alex sent
9. **Beth** enters name and pastes army list, clicks Submit
10. **Both players** see matchup summary with:
    - Alex's list (left)
    - Beth's list (right)
    - Random battle plan (e.g., "Grasp of Thorns")
11. **Both players** can print the summary for reference during game

---

## Future Enhancements

### Phase 2
- [ ] Persist matchups to database
- [ ] Matchup expiration (24-48 hours)
- [ ] Optional password protection
- [ ] Email notifications when opponent submits

### Phase 3
- [ ] Matchup history (requires auth)
- [ ] Re-match button
- [ ] Share on social media
- [ ] QR code for mobile sharing

### Nice to Have
- [ ] List validation (points, format)
- [ ] Faction detection
- [ ] Predefined list templates
- [ ] Battle plan reroll (with opponent consent)

---

## Related Features

- **Battle Plan Reference** (`/squire/battle-plan`) - Browse missions for practice
- **Herald Exchange** (`/`) - Tournament-oriented list exchange with hashing

---

## Support

**Issues**: https://github.com/ogdowski/squigleague/issues  
**Documentation**: https://github.com/ogdowski/squigleague/tree/main/docs

---

## Changelog

### 2025-11-25 - v0.2.0
- ✅ Initial implementation
- ✅ Create matchup with system selection
- ✅ Submit army lists
- ✅ Auto-generate battle plan
- ✅ Real-time polling
- ✅ Print functionality
- ✅ Copy share link
- ✅ Full UI/UX implementation
- ✅ API endpoints
- ✅ Documentation
