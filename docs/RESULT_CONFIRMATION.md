# Result Confirmation Workflow - User Manual

## Overview
The dual-user result confirmation system ensures both players agree on the outcome of their matchup. Combined with geolocation verification, this creates a trustworthy record of game results.

---

## For Players: How to Submit & Confirm Results

### Step 1: Complete Your Battle
- Play your game using the generated battle plan
- Track Victory Points throughout the game
- Determine the winner at the end
- **Important**: Both players must still be at the venue for result submission

---

### Step 2: Player 1 Submits Result

**Navigate to Matchup Page**:
- Go to your matchup from history or share link
- Battle plan and army lists are displayed

**Click "Submit Result"**:
- System requests your current location
- Grant location permission when prompted

**Enter Result Data**:
```
Winner: [Player 1 ▼] [Player 2] [Draw]

Victory Points:
  Your Score:     [___] VP
  Opponent Score: [___] VP

Battle Notes (optional):
[Text area for notes about the game]

Major Events (optional):
☐ Tabled (all units destroyed)
☐ Conceded early
☐ Time limit reached
```

**Submit**:
- System verifies your location matches battle start location
- Result stored, waiting for opponent confirmation
- You see: "Result submitted. Waiting for opponent to confirm..."

---

### Step 3: Player 2 Confirms Result

**Receive Notification**:
- Matchup page updates: "Your opponent has submitted the result"
- Click "Review & Confirm Result"

**Review Submitted Result**:
```
Result Submitted by Alice
━━━━━━━━━━━━━━━━━━━━━━━
Winner: Alice
Victory Points: Alice 85 - Bob 72

Battle Notes:
"Close game, came down to last turn. Bob's Kruleboyz 
fought well but Stormcast held objectives."

Please verify this result and submit your confirmation.
```

**Confirm or Dispute**:

**Option A - Results Match**:
- Select same winner
- Enter same (or very close) victory points
- Click "Confirm Result"
- Location verified
- Matchup marked `completed`
- Both players see final result

**Option B - Results Don't Match**:
- Enter different winner or significantly different scores
- Click "Submit My Result"
- System detects mismatch
- Matchup marked `disputed`
- Admin notified for review

---

## Result Matching Rules

### Automatic Confirmation
Results automatically match if:
- Winner selection is identical
- Victory Points within ±5 VP tolerance
- Both locations verified within 150m of start location
- Both submissions within 30 minutes of each other

### Dispute Triggers
Results flagged for dispute if:
- Different winner selected
- Victory Points differ by > 5 VP
- Location verification failed (too far from venue)
- Submissions > 6 hours after battle start
- Submissions > 30 minutes apart

---

## Location Verification During Result Submission

### Success State
```
Location Verified ✓
━━━━━━━━━━━━━━━━━━━━━━━
You are at the same venue where the battle started.
Distance from start: 45 meters
Accuracy: ±12 meters

You can now submit your result.
```

### Failure State
```
Location Verification Failed ✗
━━━━━━━━━━━━━━━━━━━━━━━
You are too far from the battle venue.
Distance from start: 2.3 km
Maximum allowed: 150 meters

Please return to the venue to submit results.
```

### Accuracy Warning
```
GPS Signal Weak ⚠
━━━━━━━━━━━━━━━━━━━━━━━
Location accuracy: ±85 meters
Required accuracy: ±50 meters

Move closer to a window or outdoors for better signal.
```

---

## Dispute Resolution Process

### When Results Don't Match

**Player View**:
```
Result Disputed
━━━━━━━━━━━━━━━━━━━━━━━
Your result and your opponent's result do not match.
An administrator will review and make a final determination.

Your Submission:
  Winner: You (Alice)
  Score: 85 - 72

Opponent's Submission:
  Winner: Opponent (Bob)
  Score: 80 - 75

Status: Under Review
Estimated resolution: 24-48 hours
```

**Admin Receives**:
- Notification of disputed matchup
- Both players' submissions side-by-side
- Location verification data
- Timestamps of submissions
- IP addresses (fraud detection)
- Contact info for both players

**Admin Actions**:
1. **Accept Player 1 Result**: Marks Player 1 as winner with their submitted VPs
2. **Accept Player 2 Result**: Marks Player 2 as winner with their submitted VPs
3. **Accept Draw**: Marks game as draw with averaged VPs
4. **Void Matchup**: Removes matchup from history, no result recorded
5. **Request Clarification**: Sends message to both players asking for more info

**Resolution Notification**:
Both players receive notification with final result and admin notes.

---

## Matchup Lifecycle States

### State Diagram
```
created
  ↓
awaiting_player2
  ↓
ready (both lists submitted)
  ↓
awaiting_start_verification
  ↓
in_progress (battle happening)
  ↓
pending_confirmation (P1 submitted result)
  ↓
completed (both confirmed) OR disputed (mismatch detected)
```

### State Descriptions

**`created`**: Matchup created, share link generated

**`awaiting_player2`**: Waiting for second player to join

**`ready`**: Both players submitted lists, battle plan generated

**`awaiting_start_verification`**: Both players must verify location to start

**`in_progress`**: Battle started, location verified, timer running

**`pending_confirmation`**: Player 1 submitted result, waiting for Player 2

**`completed`**: Both players confirmed, result verified, matchup finalized

**`disputed`**: Results don't match, admin review required

---

## User Manual: Complete Matchup Flow

### 1. Create Matchup (Player 1)
- Log in to SquigLeague
- Click "New Matchup"
- Select game system
- Select your faction
- Enter or select army list
- Click "Create" → Share link generated

### 2. Join Matchup (Player 2)
- Receive share link from opponent
- Log in (or register if new)
- Click share link
- See opponent's name and faction
- Select your faction
- Enter your army list
- Click "Submit" → Battle plan generated

### 3. Review Battle Plan (Both Players)
- Both see complete matchup details:
  - Battle plan with deployment and objectives
  - Both army lists revealed
  - Both factions displayed
- Meet at agreed venue with devices

### 4. Start Battle (Both Players)
- Both navigate to matchup page at venue
- Click "Start Battle"
- Grant location permission
- Wait for both verifications
- System confirms: "Battle started!"
- Play the game

### 5. Submit Result (Player 1)
- After game ends, click "Submit Result"
- Grant location permission
- Select winner
- Enter Victory Points for both players
- Add optional notes
- Click "Submit"
- See: "Waiting for opponent confirmation..."

### 6. Confirm Result (Player 2)
- See notification: "Opponent submitted result"
- Review submitted result
- Grant location permission
- Enter your result data
- **If you agree**: Click "Confirm Result" → Matchup complete
- **If you disagree**: Enter correct data → Dispute created

### 7. View Result (Both Players)
- Final result displayed on matchup page
- Added to matchup history
- Stats updated (win/loss record, faction performance)

---

## Tournament Mode vs Casual Mode

### Tournament Mode (Default)
- ✅ User authentication required
- ✅ Geolocation verification required
- ✅ Dual result confirmation required
- ✅ Results count toward standings
- ✅ Admin dispute resolution available

### Casual Mode (Future Feature)
- ⚠️ Optional authentication
- ⚠️ No geolocation requirement
- ⚠️ Single-player result submission
- ⚠️ Results stored but not ranked
- ⚠️ For friendly games and practice

**Enable Casual Mode**:
- Matchup creator toggles "Casual Game" checkbox
- Share link indicates casual mode
- Simpler flow, fewer validations

---

## Troubleshooting

### "I can't submit results - location keeps failing"
**Cause**: You left the venue or GPS signal is poor

**Solutions**:
- Return to the venue where you started the battle
- Ensure location services enabled on your device
- Move near a window for better GPS signal
- Wait 30 seconds for GPS to acquire accurate signal
- If venue is indoors with no signal, contact admin for manual verification

---

### "My opponent submitted wrong results"
**Cause**: Score discrepancy or wrong winner

**Solution**:
- Enter the correct results from your perspective
- System will detect mismatch and create dispute
- Admin will review within 24-48 hours
- Keep photos of score sheets as evidence if available

---

### "Battle took longer than 6 hours"
**Cause**: Multi-day game or very long battle

**Solution**:
- For legitimate long games, contact admin before submitting
- Admin can extend time limit for specific matchup
- Otherwise, submit results within 6 hours of start

---

### "I accidentally submitted wrong result"
**Cause**: User error in data entry

**Solution**:
- Contact opponent immediately
- Both agree to wait for dispute resolution
- Contact admin explaining the error
- Admin can void and allow re-submission
- In future: 5-minute edit window for result changes

---

## Best Practices

### For Players
1. **Verify your list before creating matchup** - No edits after submission
2. **Test your location permissions** before going to venue
3. **Keep battle notes** - Helps with accurate result submission
4. **Submit results immediately** after game - Don't wait days
5. **Be honest** - Disputed results are reviewed and patterns tracked

### For Tournament Organizers
1. **Announce matchup system** before event starts
2. **Ensure venue has good GPS signal** or plan for QR code verification
3. **Have backup plan** - Manual result submission if tech fails
4. **Monitor disputes** - Quick resolution keeps players happy
5. **Review fraud patterns** - Use admin tools to maintain integrity

---

## Future Enhancements

### Result Evidence Upload
- Upload photo of score sheets
- Attach battle report
- Link to video recording
- Helps resolve disputes with visual proof

### Live Score Updates
- Players update VPs during battle
- Opponent sees running score
- Reduces end-of-game disputes
- Creates engaging spectator experience

### Spectator Mode
- Share read-only link with friends
- View live score updates
- See battle plan and armies
- Cannot influence result submission

### Result Statistics
- Average game duration by system
- Common victory point ranges
- Most-played battle plans
- Faction win rates
