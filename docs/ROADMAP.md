# SquigLeague Development Roadmap

## Phase 1: Matchup System (COMPLETED ✅)
- ✅ Matchup creation and player submission
- ✅ Share link functionality
- ✅ Battle plan randomizer (19 plans: AoS, 40k, Old World)
- ✅ Battle plan reference page
- ✅ Test suite and automation scripts

## Phase 2: Validated Results & User Authentication (NEXT)

### 2.1 User Authentication System
**Goal**: Two-player authentication for verified matchups

**Work Actions**:

**2.1.1 - Design Authentication Schema**
- Create `users` table: id (UUID), username (unique), email (unique), password_hash, email_verified (boolean), verification_token, verification_expires_at, created_at, updated_at
- Create `email_verification_tokens` table: id, user_id, token (UUID), expires_at, created_at
- JWT token structure: user_id, username, email, exp (24 hour expiry)
- Document in docs/DATABASE.md

**2.1.2 - Email Service Setup**
- Configure SMTP settings in .env (SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD)
- Create `squire/email_service.py` with send_email() function
- Email templates: verification email, password reset (future)
- Test email sending in development (use mailtrap.io or similar)

**2.1.3 - Registration Backend**
- Create `squire/auth.py` with User model
- Password hashing with bcrypt (cost factor: 12)
- POST /auth/register endpoint
- Validation: unique username, unique email, password strength (8+ chars, 1 number, 1 special char)
- Generate verification token (UUID), expires in 24 hours
- Send verification email with link: {BASE_URL}/auth/verify-email?token={token}
- Return success message (no JWT until verified)

**2.1.4 - Email Verification Endpoint**
- Create GET /auth/verify-email?token={token}
- Validate token exists and not expired
- Mark user.email_verified = true
- Delete verification token
- Return success with redirect to login
- Frontend: verify-email.js page showing success/error

**2.1.5 - Resend Verification Email**
- Create POST /auth/resend-verification
- Rate limiting: max 3 per hour per email
- Generate new token, invalidate old token
- Send new verification email
- Generic response (security: don't leak user existence)

**2.1.6 - Login Backend**
- Create POST /auth/login endpoint
- Accept username or email + password
- Check email_verified = true
- Validate password with bcrypt
- Generate JWT token (24 hour expiry)
- Return: user_id, username, email, token, expires_at
- Failed login: generic "Invalid credentials" (don't specify username vs password)

**2.1.7 - Current User Endpoint**
- Create GET /auth/me endpoint (requires JWT)
- Returns current user info from token
- Used for: maintaining login state, getting user profile
- Returns 401 if token invalid/expired

**2.1.8 - Authentication Middleware**
- Create decorator `@require_auth` in squire/auth.py
- Extract JWT from Authorization header
- Validate signature and expiration
- Inject user_id into request context
- Return 401 for missing/invalid token
- Return 403 for expired token

**2.1.9 - Registration Frontend**
- Create frontend/public/modules/squire/register.js
- Form: username, email, password, confirm password
- Client-side validation before submit
- Show loading state during registration
- Success: Show "Check your email" message with email address
- Error: Display validation errors inline
- Link to login page for existing users

**2.1.10 - Email Verification Frontend**
- Create frontend/public/modules/squire/verify-email.js
- Parse token from URL query parameter
- Auto-submit verification request on page load
- Success: Show checkmark, "Email verified!" message, redirect to login after 3 seconds
- Error: Show error message with "Resend verification email" button
- Loading state while verifying

**2.1.11 - Login Frontend**
- Create frontend/public/modules/squire/login.js
- Form: username/email, password
- "Remember me" checkbox (extend token to 30 days)
- Store JWT in localStorage on success
- Set global auth state
- Redirect to home or previous page
- Show "Email not verified" error with resend link
- Link to registration page for new users

**2.1.12 - Auth State Management**
- Create frontend/public/utils/auth.js helper
- Functions: isAuthenticated(), getToken(), getCurrentUser(), logout()
- Auto-redirect to login for protected routes
- Token refresh logic (future: refresh tokens)
- Global state for current user

**2.1.13 - Protected Route Handling**
- Update router in main.js to check auth before routing
- Redirect to login with return URL parameter
- After login, redirect back to intended page
- Show login required message for unauthenticated users

**2.1.14 - Update Matchup Endpoints for Auth**
- Add @require_auth to POST /matchup/create
- Add @require_auth to POST /matchup/{id}/submit
- Store user_id for both players in matchup
- Update matchup response to include usernames
- Frontend sends Authorization header with all requests

**2.1.15 - User Profile Page**
- Create frontend/public/modules/squire/profile.js
- Display: username, email, member since
- Edit profile: change email (requires re-verification), change password
- Account settings: notification preferences
- Danger zone: delete account (future)

**2.1.16 - Logout Functionality**
- Logout button in navigation
- Clear JWT from localStorage
- Clear auth state
- Redirect to home page
- Optional: Invalidate token on server (requires token blacklist)

**2.1.17 - Testing**
- Unit tests for password hashing, JWT generation/validation
- Integration tests: register → verify email → login → access protected endpoint
- Test email verification expiry
- Test rate limiting on resend verification
- Test authentication middleware edge cases
**Goal**: Confirm both players at same physical location

**Work Actions**:

**2.2.1 - Database Schema**
- Create `matchup_locations` table (matchup_id, user_id, event_type, lat, long, accuracy, timestamp, ip_address)
- Add indexes on matchup_id and user_id
- Migration script for location tracking
- Document in docs/DATABASE.md

**2.2.2 - Distance Calculation Utilities**
- Implement Haversine formula in `squire/geolocation.py`
- Function: `calculate_distance(lat1, lon1, lat2, lon2) -> float`
- Unit tests for distance calculation accuracy
- Edge cases: antipodal points, equator crossing, poles

**2.2.3 - Validation Rules Engine**
- Create `squire/location_validation.py`
- Function: `validate_start_location(player1_loc, player2_loc) -> ValidationResult`
- Function: `validate_result_location(result_loc, start_loc) -> ValidationResult`
- Configurable thresholds: player distance (100m), venue drift (150m), accuracy (50m)
- Time window validation: start (10 min), result (30 min)

**2.2.4 - Battle Start Verification Endpoint**
- Create POST /matchup/{id}/verify-start-location
- Requires authentication
- Captures: latitude, longitude, accuracy from browser
- Stores: user_id, timestamp, IP address
- Validates: both players within 100m, accuracy ≤50m
- Response: verification status, waiting for opponent or battle started
- Transitions matchup status: `ready` → `awaiting_start_verification` → `in_progress`

**2.2.5 - Result Submission with Location**
- Update POST /matchup/{id}/submit-result to include location
- Validate location within 150m of start location
- Store result + location + timestamp
- Status transition: `in_progress` → `pending_confirmation`
- Return: result summary, waiting for confirmation

**2.2.6 - Result Confirmation with Location**
- Create POST /matchup/{id}/confirm-result
- Validate Player 2 location within 150m of start
- Compare results: winner, VPs (±5 tolerance)
- Match → status: `completed`
- Mismatch → status: `disputed`, create dispute record
- Return: final result or dispute details

**2.2.7 - Frontend Location Capture**
- Create `frontend/public/utils/geolocation.js` helper
- Function: `requestLocation() -> Promise<{lat, lon, accuracy}>`
- Handle permission denied, timeout, low accuracy
- Error messages with troubleshooting steps

**2.2.8 - Battle Start UI**
- Add "Start Battle" button to matchup page when status=`ready`
- Request location permission
- Display verification status for both players
- Show distance between players if available
- Error handling for failed verification

**2.2.9 - Result Submission UI**
- Create result submission form with location capture
- Winner dropdown, VP inputs, notes textarea
- Location verification indicator
- Preview submitted result before final submit
- Waiting state for opponent confirmation

**2.2.10 - Dispute Handling UI**
- Display dispute status to both players
- Show both submitted results side-by-side
- Estimated resolution time
- Notification when admin resolves

### 2.3 Faction Selection & List Validation
**Goal**: Structured army list validation

**Work Actions**:
1. Design faction data model
   - Faction database per game system
   - AoS: Stormcast Eternals, Kruleboyz, etc.
   - 40k: Space Marines, Orks, etc.
   - Old World: Empire, Orcs & Goblins, etc.

2. Implement faction selection
   - GET /game-systems/{system}/factions
   - Update matchup creation to include faction
   - Validate faction belongs to selected system

3. Add list validation rules
   - Point value validation (e.g., 2000 points)
   - Unit count limits
   - Ally restrictions
   - Structured list format (JSON schema)
   - Optional: Integration with external list builders

### 2.4 Matchup Lifecycle Enhancement
**Goal**: Track matchup from creation to verified result

**Matchup States**:
- `created` → Matchup created, waiting for second player
- `awaiting_player2` → Share link distributed, waiting for join
- `ready` → Both players joined, battle plan generated
- `awaiting_start_verification` → Waiting for location verification
- `in_progress` → Battle started (location verified)
- `pending_confirmation` → One player submitted result
- `completed` → Both players confirmed result (locations verified)
- `disputed` → Results don't match (admin intervention needed)
- `voided` → Admin cancelled matchup (not counted)

**Work Actions**:

**2.4.1 - Extend Matchup Data Model**
- Add `status` field (enum of states above)
- Add `scheduled_time` (optional, for future scheduling)
- Add `location_name` (venue name, user-entered)
- Add `battle_started_at` (timestamp when in_progress)
- Add `battle_ended_at` (timestamp when result submitted)
- Add result fields: `winner_user_id`, `player1_vp`, `player2_vp`, `result_notes`
- Add `result_verified_at` (timestamp when completed)
- Add `disputed_at`, `dispute_reason`, `resolved_at`, `resolution_notes`
- Migration script for new fields

**2.4.2 - State Transition Logic**
- Create `squire/matchup_lifecycle.py`
- Function: `transition_state(matchup, new_state) -> bool`
- Validate legal state transitions (can't go from created → completed)
- State machine rules enforcement
- Audit log for state changes

**2.4.3 - Schedule Battle Endpoint (Optional)**
- Create POST /matchup/{id}/schedule
- Set scheduled_time and location_name
- Used for organized tournament scheduling
- Not required for immediate casual play

**2.4.4 - Battle Start Workflow**
- Combine faction selection with start verification
- UI shows "Ready to Start" when status=`ready`
- Both players click "Start Battle" → location capture
- When both verified → status: `in_progress`, timer starts
- Display battle timer in UI

**2.4.5 - Result Submission Workflow**
- Winner dropdown: Player 1 | Player 2 | Draw
- VP inputs for both players (0-200 range typical)
- Notes textarea (optional, max 500 chars)
- Location automatically captured on submit
- Status → `pending_confirmation`

**2.4.6 - Result Confirmation Workflow**
- Player 2 sees submitted result from Player 1
- Must enter own result data independently
- Location captured on confirmation
- Compare results: winner, VPs (±5 tolerance)
- Match → `completed` | Mismatch → `disputed`

**2.4.7 - Dispute Detection Logic**
- Create `squire/dispute_detection.py`
- Function: `detect_discrepancies(result1, result2) -> List[Discrepancy]`
- Check: winner mismatch, VP difference >5, suspicious timing
- Auto-flag for admin review
- Generate dispute summary for admin

**2.4.8 - Status Endpoint**
- Create GET /matchup/{id}/status
- Returns: current state, next action required, verification status
- Used by frontend for real-time status updates
- Polling interval: 5 seconds when in active states

**2.4.9 - Timeline View**
- Show matchup progression in UI
- Created → Lists Submitted → Battle Started → Result Submitted → Confirmed
- Display timestamps for each milestone
- Visual indicator of current state

### 2.5 Database Persistence
**Goal**: Replace in-memory storage with PostgreSQL

**Work Actions**:
1. Design database schema
   - users table (id, username, email, created_at)
   - matchups table (all matchup fields + foreign keys)
   - matchup_locations table (matchup_id, player_id, lat, long, timestamp, event_type)
   - factions table (id, game_system, name, description)

2. Implement database layer
   - SQLAlchemy models
   - Migration scripts (Alembic)
   - CRUD operations for all entities

3. Update all endpoints to use database
   - Replace in-memory dictionaries
   - Add transaction management
   - Implement proper error handling

## Phase 3: Admin & Reporting

### 3.1 Admin Dashboard
**Goal**: Centralized administration for disputes and system management

**Work Actions**:

**3.1.1 - Admin Authentication**
- Add `is_admin` boolean to users table
- Create admin-only middleware: @require_admin
- Admin login page with elevated permissions
- Session logging for admin actions

**3.1.2 - Dispute Management UI**
- Create `/admin/disputes` page
- List all matchups with status=`disputed`
- Sort by: oldest first, newest first, most critical
- Each dispute shows:
  - Both players' usernames (clickable to profile)
  - Battle plan used
  - Both submitted results side-by-side
  - VP discrepancy highlighted
  - Location verification status
  - Time elapsed between submissions
  - IP addresses (fraud detection)

**3.1.3 - Dispute Resolution Actions**
- Admin can: Accept P1 Result | Accept P2 Result | Set Draw | Void Matchup
- Add resolution notes (visible to both players)
- Send notification to both players with decision
- Log: admin_user_id, action, timestamp, notes
- Status transition: `disputed` → `completed` or `voided`

**3.1.4 - Manual Location Override**
- Admin can bypass location verification for specific matchup
- Use cases: Indoor venue, GPS failure, technical issues
- Requires justification note
- Flagged in matchup record: `location_manually_verified: true`

**3.1.5 - User Management**
- View all users, search by username/email
- Ban users (prevents matchup creation, login)
- Merge duplicate accounts
- Reset passwords
- View user's complete matchup history

**3.1.6 - System Configuration**
- Configure validation thresholds:
  - Max player distance (default 100m)
  - Max venue drift (default 150m)
  - VP tolerance (default ±5)
  - Time limits (default 1-6 hours)
- Enable/disable geolocation requirement globally
- Enable/disable faction requirement
- Maintenance mode toggle

**3.1.7 - Fraud Detection Dashboard**
- Flag suspicious patterns:
  - Same IP submitting both results
  - Impossible location jumps (>100km in <1 hour)
  - Repeated disputes from same user
  - Perfect GPS accuracy (possible spoofing)
- Auto-flag for review
- Admin can mark as: Legitimate | Fraudulent | Under Investigation

---

### 3.2 Player Statistics & Rankings
**Goal**: Track performance and create leaderboards

**Work Actions**:

**3.2.1 - Win/Loss Records**
- Calculate: total games, wins, losses, draws
- Win rate percentage
- Breakdown by game system
- Recent form (last 10 games)
- Display on user profile

**3.2.2 - Faction Performance Tracking**
- Games played per faction
- Win rate per faction
- Most-played faction per system
- Faction diversity score
- Display in history page

**3.2.3 - Battle Plan Statistics**
- Track which battle plans used most often
- Win rate per battle plan
- Player's experience with each plan
- "You've played The Liferoots 5 times (3-2 record)"

**3.2.4 - Leaderboards**
- Global leaderboard: most wins
- Per-system leaderboards
- Per-faction leaderboards
- Monthly/seasonal rankings
- Minimum games threshold (e.g., 10 games to rank)

**3.2.5 - Achievement System (Future)**
- Badges for milestones:
  - "First Win", "10 Wins", "50 Wins"
  - "Faction Master" (10 wins with single faction)
  - "System Explorer" (played all 3 systems)
  - "Battle Plan Expert" (played all plans in a system)
- Display on user profile
- Unlock special cosmetic features

**3.2.6 - Head-to-Head Records**
- Show record against specific opponents
- "vs Bob: 3-2 (W-L)"
- Factions used in each game
- Most common matchup
- Rivalry tracking

---

### 3.3 Dispute Resolution System
**Goal**: Fair and transparent conflict resolution

**Work Actions**:

**3.3.1 - Dispute Creation**
- Auto-detect result mismatches
- Create dispute record with:
  - Both submitted results
  - Discrepancy details
  - Location verification status
  - Timestamps
  - Automated severity scoring
- Notify both players and admins
- Status: `disputed`

**3.3.2 - Evidence Submission (Future)**
- Players can upload photos of score sheets
- Players can add text clarifications
- Time limit: 24 hours after dispute created
- Evidence attached to dispute record
- Visible to admin during review

**3.3.3 - Automated Dispute Checks**
- Check if VP discrepancy ≤ 5 → suggest average
- Check if one player clearly wrong (tabled vs close game)
- Check location data for fraud indicators
- Prioritize disputes: High (large discrepancy) | Medium | Low
- Auto-resolve simple cases (1 VP difference → take average)

**3.3.4 - Admin Resolution Workflow**
- Admin reviews all evidence
- Can message both players for clarification
- Makes decision with justification
- Options:
  - Accept Player 1 result
  - Accept Player 2 result  
  - Set custom result (draw with averaged VPs)
  - Void matchup (doesn't count)
  - Penalize player (ban for fraud)
- Both players notified with decision + reasoning

**3.3.5 - Appeal Process (Future)**
- Players can appeal admin decision (once)
- Different admin reviews appeal
- Final decision binding
- Repeated frivolous appeals → warning/ban

**3.3.6 - Dispute Analytics**
- Track dispute rate per player
- Flag players with >20% dispute rate
- Identify common dispute types
- System improvements based on patterns

---

### 3.4 Tournament Management
**Goal**: Support organized multi-round tournaments

**Work Actions**:

**3.4.1 - Tournament Creation**
- Admin creates tournament
- Set: name, game system, points limit, rounds, format
- Formats: Swiss, Single Elimination, Round Robin
- Registration deadline
- Publish tournament page

**3.4.2 - Player Registration**
- Players register with army list + faction
- List validation before acceptance
- Registration cap (e.g., 32 players)
- Waitlist for full tournaments

**3.4.3 - Pairing Algorithm**
- Swiss pairing: by record, avoid rematches
- Bracket generation for elimination
- Round Robin: all play all
- Auto-generate matchups for each round

**3.4.4 - Round Management**
- Admin starts each round → matchups created
- Players notified of pairings
- Time limit per round
- Admin can extend time or mark no-shows
- Auto-progress to next round when all games complete

**3.4.5 - Tournament Standings**
- Live leaderboard during tournament
- Tiebreakers: VP differential, strength of schedule
- Display remaining opponents
- Projections for final standings

---

### 3.5 Admin Audit & Monitoring Tools
**Goal**: System health and fraud prevention

**Work Actions**:

**3.5.1 - Activity Logs**
- Log all admin actions with timestamp and user
- Log all matchup state transitions
- Log all dispute resolutions
- Searchable, filterable logs
- Export logs for compliance

**3.5.2 - Location Audit Dashboard**
- Review all location captures
- Map view of matchup locations
- Flag impossible travel (teleportation detection)
- IP/GPS correlation analysis
- Repeated same-location usage (home address spoofing)

**3.5.3 - User Behavior Analytics**
- New user signups per day
- Active users per week
- Matchup creation rate
- Completion rate (created vs completed)
- Average time to complete matchup
- Identify drop-off points in flow

**3.5.4 - System Health Monitoring**
- API endpoint response times
- Error rate tracking
- Database query performance
- Active sessions count
- Storage usage
- Alert admins if thresholds exceeded

**3.5.5 - Fraud Detection Alerts**
- Auto-flag suspicious patterns:
  - Multiple accounts from same IP
  - Same location used for all games (GPS spoofing)
  - Unrealistic win rates (>95%)
  - Rapid matchup creation/completion
- Admin reviews flagged accounts
- Can: Investigate | Clear Flag | Ban User

---

### 3.6 Notification System
**Goal**: Keep players informed of matchup progress

**Work Actions**:

**3.6.1 - In-App Notifications**
- Notification center icon with count
- Types:
  - "Opponent joined your matchup"
  - "Opponent submitted result - confirm now"
  - "Dispute resolved by admin"
  - "Tournament round starting"
- Mark as read/unread
- Dismiss individual notifications

**3.6.2 - Email Notifications (Optional)**
- User preferences for email alerts
- Send for critical events:
  - Matchup completed
  - Result needs confirmation
  - Dispute resolved
- Unsubscribe option
- Email templates

**3.6.3 - Push Notifications (PWA, Future)**
- Service worker for push notifications
- Prompt user to enable on first login
- Real-time alerts on mobile
- Background sync for offline result submission

---

### 3.7 Tournament System (DEFERRED)
**Note**: Moved from Phase 3.3 - requires all Phase 2 features first

**Work Actions**: See 3.4 above for tournament management details

## Technical Debt & Infrastructure

### Immediate
- Add .gitignore for artifacts/ (should not be committed)
- Environment-based configuration (dev/staging/prod)
- API rate limiting
- CORS configuration for production

### Medium Priority
- Error logging and monitoring
- API documentation (OpenAPI/Swagger)
- Frontend error boundaries
- Mobile-responsive design

### Low Priority
- Caching layer (Redis)
- WebSocket for real-time updates (replace polling)
- Email notifications
- Push notifications for mobile

## Recommended Next Sprint

**Focus**: Phase 2.1 (User Authentication) + Phase 2.4 (Matchup Lifecycle)

**Rationale**: 
- Authentication is prerequisite for all validation features
- Lifecycle management provides structure for geolocation and results
- Can deliver incremental value: authenticated matchups without full geolocation first
- Faction selection can be added after core auth is stable

**Estimated Effort**: 
- User authentication: 2-3 days
- Matchup lifecycle: 2-3 days
- Integration & testing: 1-2 days
- **Total**: ~1 week for core validated matchup flow

**Deliverables**:
- Users can register/login
- Matchups linked to authenticated users
- Matchup state machine (created → ready → scheduled → in_progress → completed)
- Basic result submission (winner/score)
- Foundation for adding geolocation in next sprint
