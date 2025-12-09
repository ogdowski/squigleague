# Pull Request: Matchup System and Battle Plan Reference

## Summary
This PR adds a complete matchup system for Squig League, allowing two players to exchange army lists and receive a randomized battle plan. It also includes a battle plan reference page for verification and removes all emoji from the UI.

## Features Added

### 1. Matchup System
- **Create matchup**: Select game system (AoS, 40k, Old World)
- **Shareable link**: Each matchup gets unique URL to share with opponent
- **List submission**: Both players submit their army lists
- **Auto-reveal**: Battle plan appears when both players submit
- **Security**: Lists hidden until both players submit (prevents cheating)

### 2. Battle Plan Reference
- Browse all available battle plans for each game system
- Verify completeness and correctness of mission data
- Expandable cards showing full battle plan details
- Accessible at `/squire/battle-plan-reference`

### 3. UI Improvements
- Removed ALL emoji icons from UI (Herald and Squire modules)
- Clean, professional appearance
- Improved navigation with new "Reference" link

## Technical Changes

### Backend (`squire/`)
- **NEW**: `matchup.py` - Matchup data models and business logic
  - `MatchupPlayer` dataclass
  - `Matchup` dataclass with validation
  - `create_matchup()`, `submit_list()`, `get_matchup()` functions
  - In-memory storage (can be replaced with DB)

- **MODIFIED**: `routes.py` - Added matchup API endpoints
  - `POST /api/squire/matchup/create` - Create new matchup
  - `POST /api/squire/matchup/{id}/submit` - Submit army list
  - `GET /api/squire/matchup/{id}` - Retrieve matchup status
  - Validation: min 10 chars for army list, 1-100 chars for name

### Frontend (`frontend/public/`)
- **NEW**: `modules/squire/matchup.js` - Matchup UI component
  - Alpine.js component with polling (every 5 seconds)
  - System selection, list submission, status display
  - Automatic battle plan reveal when complete
  - Copy-to-clipboard for share links

- **NEW**: `modules/squire/battleplan-reference.js` - Reference page
  - Browse all battle plans by system
  - Expandable cards with full details
  - Automatic deduplication of battle plans

- **MODIFIED**: `modules/squire/battleplan.js` - Removed emoji (🎲🏰🚀🛡️⚔️⚠️✕📋🏆🎯⚡🖨️)
- **MODIFIED**: `modules/herald/waiting.js` - Removed emoji (✓⚠️)
- **MODIFIED**: `modules/herald/reveal.js` - Removed emoji (✓✗⚠️)
- **MODIFIED**: `modules/herald/home.js` - Removed emoji (⏱️)
- **MODIFIED**: `src/main.js` - Added routing for matchup and reference pages
- **MODIFIED**: `index.html` - Added navigation links and script tags

### Configuration
- **MODIFIED**: `nginx/nginx.conf` - Fixed syntax errors
  - Removed stray "just" text (line 53)
  - Fixed admin IP restriction for local dev

### Tests
- **NEW**: `tests/integration/squire/test_matchup.py` - Comprehensive test suite
  - 30+ test cases covering all functionality
  - Validation tests, edge cases, error handling
  - Tests for all three game systems

### Scripts
- **NEW**: `scripts/test-api.ps1` - API integration tests (15 tests, all passing)
- **NEW**: `scripts/test-matchup-flow.ps1` - End-to-end flow test
- **NEW**: `scripts/prepare-pr.ps1` - PR preparation automation
- **NEW**: `scripts/MATCHUP-FLOW.md` - User flow documentation

## Testing
All tests passing:
```
✅ 15/15 API integration tests
✅ End-to-end matchup flow test
✅ Frontend builds successfully
✅ All containers healthy
```

## User Flow
1. Player 1 creates matchup → gets shareable link
2. Player 1 submits their army list
3. Player 1 shares link with opponent (Discord, email, etc.)
4. Player 2 visits link → sees "waiting for you" message
5. Player 2 submits their army list
6. **Battle plan automatically appears for both players**
7. Both can view complete matchup summary with both lists

## Security & Privacy
- Lists are hidden until BOTH players submit (prevents last-second tailoring)
- Battle plan only revealed when matchup complete
- Unique, unguessable IDs for each matchup
- No authentication required (frictionless UX)

## Browser Testing
Manually tested in:
- Chrome (latest)
- Firefox (latest)
- Edge (latest)
- Mobile responsive design verified

## Breaking Changes
None - this is all new functionality

## Database Migration
Not required - uses in-memory storage (can be upgraded to persistent storage later)

## Deployment Notes
- Requires Docker rebuild (no-cache) for nginx fixes
- Frontend and backend both need rebuild
- Run: `docker-compose -f docker-compose.yml -f docker-compose.dev.yml build --no-cache`

## Screenshots
- Matchup creation page with system selection
- Share link and submission form
- Waiting screen with status
- Complete matchup with battle plan reveal
- Battle plan reference page with all missions

## Future Improvements
- Persistent database storage
- Email notifications when opponent submits
- Battle plan favorites/history
- Print-optimized layout
- Export to PDF

## Checklist
- [x] Code follows project style guidelines
- [x] All tests passing
- [x] No console errors
- [x] Responsive design verified
- [x] All emoji removed as requested
- [x] Documentation added
- [x] No breaking changes
