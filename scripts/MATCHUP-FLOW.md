# Matchup System - User Flow

## Complete Flow

### Step 1: Player 1 Creates Matchup
1. Visit http://localhost/squire/matchup
2. Select game system (Age of Sigmar, 40k, or Old World)
3. Click "Create Matchup"
4. **System generates shareable link**: `http://localhost/squire/matchup/{matchup_id}`

### Step 2: Player 1 Submits Their List
1. Copy the share link to send to opponent
2. Enter your name
3. Paste your army list
4. Click "Submit My List"
5. See "Waiting for opponent..." message

### Step 3: Player 2 Joins via Share Link
1. **Player 1 shares link** (via Discord, email, etc.)
2. Player 2 visits: `http://localhost/squire/matchup/{matchup_id}`
3. System loads matchup showing:
   - Opponent's name (Player 1)
   - "Waiting for you to submit your army list"

### Step 4: Player 2 Submits Their List
1. Enter your name
2. Paste your army list
3. Click "Submit My List"
4. **Battle plan automatically generated!**

### Step 5: Both Players See Results
- **Battle Plan** with full mission details
- **Both army lists** revealed
- Ability to print matchup summary

## What Makes It Work

### The Share Link
- Format: `http://localhost/squire/matchup/{matchup_id}`
- Anyone with link can join (first 2 players only)
- No authentication required
- Unique ID prevents conflicts

### The Waiting Game
- Frontend polls every 5 seconds
- Updates automatically when opponent submits
- Battle plan only appears when BOTH players submit

### Key Features
✅ Shareable link - send via any method
✅ Auto-reveal when both players ready
✅ Clean UI showing status
✅ Printable summary for reference

## Testing in Browser

1. Open first tab: http://localhost/squire/matchup
2. Create matchup, copy link
3. Submit your list as Player 1
4. Open second tab (or incognito): paste the link
5. Submit as Player 2
6. Battle plan appears in both tabs!
