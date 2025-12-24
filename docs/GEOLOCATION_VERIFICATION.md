# Geolocation Verification System

## Overview
The geolocation verification system ensures both players are physically present at the same location during matchup execution. This prevents remote result manipulation and verifies legitimate in-person games.

## User Story

**As a** tournament organizer or competitive player  
**I want** both players' locations verified at battle start and result submission  
**So that** I can ensure games are played legitimately in person

## User Flow

### 1. Battle Start Location Verification

**Trigger**: Both players have submitted army lists and are ready to start

**Steps**:
1. Matchup status transitions from `ready` to `awaiting_start_verification`
2. Both players navigate to matchup page
3. System prompts: "Ready to start battle? Both players must verify location."
4. Each player clicks "Verify Location & Start Battle"
5. Browser requests geolocation permission
6. Player grants permission → location captured
7. Location sent to backend: POST /matchup/{id}/verify-start-location
8. Backend checks: Are both players within acceptable radius?
9. **Success**: Status → `in_progress`, battle timer starts
10. **Failure**: Show error, retry option

**UI Display**:
```
Battle Start Verification
━━━━━━━━━━━━━━━━━━━━━━━
Player 1 (Alice): ✓ Location verified
Player 2 (Bob):   ⏳ Waiting for verification...

Both players must be within 100 meters to start.
```

---

### 2. Result Submission Location Verification

**Trigger**: Battle completed, players ready to submit results

**Steps**:
1. Player 1 navigates to matchup → clicks "Submit Result"
2. Enters result data: winner, victory points, notes
3. Browser captures current geolocation
4. Submits: POST /matchup/{id}/submit-result
5. Backend stores: result + location + timestamp
6. Status → `pending_confirmation`
7. Player 2 receives notification to confirm
8. Player 2 clicks "Confirm Result"
9. Enters their result data (must match Player 1)
10. Browser captures Player 2 location
11. Submits: POST /matchup/{id}/confirm-result
12. Backend validates:
    - Both players within radius of start location
    - Results match (winner, score within tolerance)
    - Time elapsed reasonable for game type
13. **Success**: Status → `completed`, result recorded
14. **Mismatch**: Status → `disputed`, admin intervention required

---

## Geolocation Data Model

### Location Capture Schema
```python
@dataclass
class LocationVerification:
    matchup_id: str
    user_id: str
    event_type: str  # "start_battle" | "submit_result"
    latitude: float
    longitude: float
    accuracy: float  # meters
    timestamp: datetime
    ip_address: str  # additional fraud detection
```

### Storage
**Table**: `matchup_locations`
- id (UUID, primary key)
- matchup_id (foreign key → matchups.id)
- user_id (foreign key → users.id)
- event_type (enum: start_battle, submit_result)
- latitude (decimal 10,8)
- longitude (decimal 11,8)
- accuracy (float, meters)
- timestamp (timestamptz)
- ip_address (varchar)
- created_at (timestamptz)

---

## Validation Rules

### Distance Calculation
Uses Haversine formula to calculate distance between two GPS coordinates:

```python
def calculate_distance(lat1, lon1, lat2, lon2) -> float:
    """Returns distance in meters between two coordinates"""
    R = 6371000  # Earth radius in meters
    φ1 = radians(lat1)
    φ2 = radians(lat2)
    Δφ = radians(lat2 - lat1)
    Δλ = radians(lon2 - lon1)
    
    a = sin(Δφ/2)**2 + cos(φ1) * cos(φ2) * sin(Δλ/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    return R * c
```

### Verification Rules

**Battle Start**:
- Both players must verify within 10 minutes of each other
- Distance between players: ≤ 100 meters (configurable)
- Accuracy must be ≤ 50 meters (GPS quality check)
- If either fails, status remains `awaiting_start_verification`

**Result Submission**:
- Both players must be within 150 meters of start location
- Both players must verify within 30 minutes of each other
- Allows for venue movement (e.g., different tables in same game store)
- Time elapsed: 1-6 hours (reasonable game duration)

**Configurable Settings** (admin panel, future):
- max_player_distance_meters (default: 100)
- max_venue_drift_meters (default: 150)
- max_verification_delay_minutes (default: 10 start, 30 result)
- min_game_duration_minutes (default: 60)
- max_game_duration_minutes (default: 360)

---

## Privacy & Security

### User Privacy
- **Location data retention**: 90 days, then purged
- **Display granularity**: Never show exact coordinates to users
- **UI Display**: "Verified in Birmingham, UK" (city-level only)
- **Consent**: Explicit permission request before each capture
- **Opt-out**: Tournament organizers can disable for casual games

### Security Considerations
- **Spoofing Prevention**: 
  - Compare IP address geolocation with GPS coordinates
  - Flag mismatches > 50km for manual review
  - Rate limit location submissions (max 5 per matchup)
  
- **Replay Attacks**:
  - Each verification has unique timestamp
  - Cannot reuse previous location data
  
- **Collusion**:
  - Store both players' locations separately
  - Admin can review location history for suspicious patterns

---

## Error Handling

### Location Permission Denied
```
Unable to verify location

Your browser denied location access. To verify your 
location and start the battle:

1. Enable location services in your browser settings
2. Refresh this page
3. Click "Allow" when prompted

Without location verification, this matchup cannot proceed
in tournament mode.
```

### Players Too Far Apart
```
Location Verification Failed

You and your opponent are too far apart:
- Distance: 2.3 km
- Maximum allowed: 100 m

Please ensure both players are at the same venue and 
try again.
```

### Accuracy Too Low
```
GPS Signal Too Weak

Your location accuracy is 250m. We require ≤50m for 
verification.

Try:
- Moving closer to a window
- Waiting a few moments for better GPS signal
- Enabling high-accuracy mode in device settings
```

### Time Validation Failed
```
Result Timing Issue

This battle took 8 hours, which exceeds the maximum 
allowed duration of 6 hours.

If this was a legitimate game, contact an admin for 
manual verification.
```

---

## API Endpoints

### POST /matchup/{id}/verify-start-location
**Purpose**: Capture player location at battle start

**Request**:
```json
{
  "latitude": 52.4862,
  "longitude": -1.8904,
  "accuracy": 15.0
}
```

**Response**:
```json
{
  "verified": true,
  "waiting_for": "player2",
  "message": "Location verified. Waiting for opponent..."
}
```

**When both verified**:
```json
{
  "verified": true,
  "battle_started": true,
  "started_at": "2025-11-25T14:30:00Z",
  "message": "Battle started! Good luck!"
}
```

---

### POST /matchup/{id}/submit-result
**Purpose**: Submit result with location verification

**Request**:
```json
{
  "winner": "player1" | "player2" | "draw",
  "player1_vp": 85,
  "player2_vp": 72,
  "notes": "Close game, came down to last turn",
  "latitude": 52.4865,
  "longitude": -1.8907,
  "accuracy": 12.0
}
```

**Response**:
```json
{
  "result_submitted": true,
  "waiting_for_confirmation": true,
  "message": "Result submitted. Waiting for opponent confirmation..."
}
```

---

### POST /matchup/{id}/confirm-result
**Purpose**: Second player confirms result with location

**Request**:
```json
{
  "winner": "player1",
  "player1_vp": 85,
  "player2_vp": 72,
  "latitude": 52.4863,
  "longitude": -1.8905,
  "accuracy": 18.0
}
```

**Success Response**:
```json
{
  "confirmed": true,
  "status": "completed",
  "message": "Result confirmed! Matchup complete."
}
```

**Mismatch Response**:
```json
{
  "confirmed": false,
  "status": "disputed",
  "discrepancies": [
    {
      "field": "player2_vp",
      "player1_submitted": 72,
      "player2_submitted": 75,
      "message": "Victory point totals do not match"
    }
  ],
  "message": "Results do not match. An admin will review."
}
```

---

## Admin Tools

### Dispute Resolution
**Admin View**: `/admin/disputes`

Shows all matchups with status `disputed`:
- Both players' submitted results
- Location verification data
- Time elapsed
- IP addresses
- Option to: Accept Player 1 result | Accept Player 2 result | Void matchup

### Location Audit Log
**Admin View**: `/admin/location-audit`

Filter suspicious patterns:
- Multiple matchups from impossible locations (teleportation)
- Consistently perfect accuracy (possible spoofing)
- IP/GPS mismatches
- Flagged for manual review

---

## Implementation Phases

### Phase 2.2.1: Basic Location Capture (Week 1)
- Browser geolocation API integration
- Location storage in database
- Simple distance validation
- No UI indicators yet

### Phase 2.2.2: Start Verification (Week 2)
- POST /verify-start-location endpoint
- Distance validation between players
- UI status indicators
- Error handling for permission denied

### Phase 2.2.3: Result Verification (Week 3)
- POST /submit-result with location
- POST /confirm-result with location
- Venue drift validation (150m from start)
- Dispute detection

### Phase 2.2.4: Admin Tools (Week 4)
- Dispute resolution UI
- Location audit log
- Manual override capabilities
- Fraud detection reports

---

## Testing Requirements

### Unit Tests
- [ ] Haversine distance calculation accuracy
- [ ] Validation rules (all pass/fail scenarios)
- [ ] Time window validation
- [ ] Result matching logic

### Integration Tests
- [ ] Complete flow: start verification → result submission → confirmation
- [ ] Location permission denied handling
- [ ] Disputed result creation
- [ ] Admin dispute resolution

### Manual UAT
- [ ] Two devices at same location can verify
- [ ] Two devices at different locations fail verification
- [ ] Matching results confirm successfully
- [ ] Mismatched results create dispute
- [ ] Admin can resolve disputes

---

## Mobile Considerations

### iOS Safari
- Requires HTTPS for geolocation API
- May require user to enable location in Settings → Safari
- Accuracy typically 10-50m in urban areas

### Android Chrome
- Works on HTTP for localhost, requires HTTPS for production
- Prompts for high-accuracy mode
- Accuracy typically 5-30m with GPS enabled

### Progressive Web App (Future)
- Install as PWA for better location permissions
- Background location updates during battle
- Push notifications for opponent verification

---

## Privacy Compliance

### GDPR Requirements
- [ ] Explicit consent before capturing location
- [ ] Clear explanation of why location is needed
- [ ] Right to request location data deletion
- [ ] Data retention policy: 90 days
- [ ] Privacy policy updated

### User Control
- [ ] Tournament mode (location required) vs Casual mode (optional)
- [ ] Can disable location features in profile settings
- [ ] Export all stored location data on request
- [ ] Delete account removes all location history

---

## Alternative: QR Code Verification (Future Option)

For venues without reliable GPS (indoor locations):

1. Venue generates unique QR code for the day
2. Both players scan QR code at battle start
3. QR code contains: venue_id, date, unique_token
4. Backend validates both players scanned same code
5. Result submission requires same QR code

**Benefits**:
- Works indoors (no GPS required)
- Venue verification instead of exact location
- Simpler privacy model (venue-level, not coordinate-level)

**Implementation**: Phase 3, after core geolocation working
