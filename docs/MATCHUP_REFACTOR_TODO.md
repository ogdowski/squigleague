# Matchup System Refactor - Ariel's Feedback

## Changes Required

### 1. Menu/Navigation
- [x] Identify current menu structure
- [ ] Move "List Exchange + Random Battle Plan" link to working state
- [ ] Rename to "Matchup"
- [ ] Move to first position (before Battle Plans Gallery)
- [ ] Rename "Battle Plans Gallery" to "Missions"
- [ ] Remove Wahapedia references, prepare for BSData integration

### 2. Matchup Flow Changes
- [ ] Home view: Show instructions for list exchange
- [ ] Show system choice (AoS 4th Ed GHB 25 etc)
- [ ] DO NOT show matchup link yet
- [ ] Require Player 1 to submit list FIRST
- [ ] Only after Player 1 submits, show link to Player 2
- [ ] After BOTH submit, show both lists
- [ ] Add button to randomize OR choose specific battleplan
- [ ] Allow either player to select battleplan (but only once total)
- [ ] Track selection: date, who selected (IP or matchup creator ID)
- [ ] Lock battleplan after selection

### 3. Link Generation
- [ ] Change from UUID style to Herald-style
- [ ] Format: `adjective-noun-4hex` (3 parts instead of 4)
- [ ] Keep AoS/fantasy themed words
- [ ] Examples: `brave-dragon-a3f2`, `mighty-squig-7b4d`

### 4. Notifications
- [ ] Change "list copied" notification back to old one
- [ ] Find what old notification text was

### 5. Images
- [ ] Remove battleplan images temporarily
- [ ] Keep image infrastructure for later BSData integration

### 6. Future Refactor Notes
- [ ] Document plan to merge herald + squire into "matchup" module
- [ ] Plan data structure: list exchange, mission randomization, score tracker
- [ ] Move missions/rules to data directory

## Files to Modify

### Frontend
- `frontend/public/index.html` - Update menu
- `frontend/public/modules/squire/matchup.js` - Update flow logic
- `frontend/public/modules/squire/battleplan-gallery.js` - Rename/update
- `frontend/public/src/main.js` - Update routing

### Backend
- `squire/matchups.py` - Update matchup ID generation
- `squire/battle_plans.py` - Prepare for BSData migration
- `main.py` - Update API routes if needed

## Implementation Order

1. Fix menu and navigation (cosmetic, no breaking changes)
2. Update matchup ID generation (backend, database compatible)
3. Update matchup flow (complex, requires careful testing)
4. Remove images (simple)
5. Document future refactor plans

## Testing Checklist

- [ ] Player 1 creates matchup
- [ ] Player 1 submits list
- [ ] Player 2 cannot access until Player 1 submits
- [ ] Player 2 submits list
- [ ] Both lists visible
- [ ] Either player can select battleplan
- [ ] Second selection attempt blocked
- [ ] Selection tracked (who + when)
- [ ] Link format matches adjective-noun-4hex

## BSData Integration Notes

BSData repo: https://github.com/BSData/age-of-sigmar-4th
- Contains battleplan data in XML/structured format
- Need to parse and convert to our JSON structure
- Can extract objective positions, terrain, deployment zones
- Future work: auto-update from BSData releases
