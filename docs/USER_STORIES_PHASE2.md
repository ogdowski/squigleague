# Phase 2 User Stories: Authentication & Validated Results

## Epic 1: User Authentication

### US-2.1: User Registration
**As a** player  
**I want to** create an account  
**So that** I can participate in verified matchups and track my game history

**Acceptance Criteria**:
- [ ] User can register with username, email, and password
- [ ] Username must be unique (3-20 characters, alphanumeric + underscore)
- [ ] Email must be valid and unique
- [ ] Password must be at least 8 characters with complexity requirements
- [ ] Password is hashed (bcrypt) before storage
- [ ] Registration creates unverified account
- [ ] Verification email sent with unique link
- [ ] Email expires after 24 hours
- [ ] User cannot login until email verified
- [ ] Invalid inputs show clear error messages
- [ ] Resend verification email option available

**API**: `POST /auth/register`
```json
{
  "username": "string",
  "email": "string",
  "password": "string"
}
```

**Response**: 
```json
{
  "user_id": "uuid",
  "username": "string",
  "email": "string",
  "message": "Registration successful. Please check your email to verify your account."
}
```

---

### US-2.1b: Email Verification
**As a** newly registered player  
**I want to** verify my email address  
**So that** I can activate my account and start playing

**Acceptance Criteria**:
- [ ] Verification email sent within 1 minute of registration
- [ ] Email contains unique verification link valid for 24 hours
- [ ] Clicking link verifies account and shows success message
- [ ] User can now login after verification
- [ ] Expired links show clear error with resend option
- [ ] Already-verified accounts show "already verified" message
- [ ] Invalid tokens show error message

**API**: `GET /auth/verify-email?token={verification_token}`

**Response** (success):
```json
{
  "verified": true,
  "message": "Email verified! You can now log in.",
  "redirect_url": "/login"
}
```

---

### US-2.1c: Resend Verification Email
**As a** unverified user  
**I want to** resend my verification email  
**So that** I can verify my account if the original email was lost

**Acceptance Criteria**:
- [ ] "Resend verification email" link on login page
- [ ] Enter email address
- [ ] New verification email sent if account exists and unverified
- [ ] Rate limited: max 3 resends per hour
- [ ] Shows message: "Email sent. Check your inbox."
- [ ] No error if email doesn't exist (security: don't leak user existence)

**API**: `POST /auth/resend-verification`
```json
{
  "email": "string"
}
```

**Response**:
```json
{
  "message": "If that email is registered and unverified, a verification email has been sent."
}
```

---

### US-2.2: User Login
**As a** registered player  
**I want to** log into my account  
**So that** I can access my matchups and create new verified games

**Acceptance Criteria**:
- [ ] User can log in with username/email and password
- [ ] Successful login returns JWT token
- [ ] Token expires after 24 hours
- [ ] Invalid credentials show clear error message
- [ ] Token stored in localStorage
- [ ] User redirected to home page after login
- [ ] Login state persists across browser sessions

**API**: `POST /auth/login`
```json
{
  "username_or_email": "string",
  "password": "string"
}
```

**Response**:
```json
{
  "user_id": "uuid",
  "username": "string",
  "email": "string",
  "token": "jwt_string",
  "expires_at": "iso8601_timestamp"
}
```

---

### US-2.3: User Logout
**As a** logged-in player  
**I want to** log out of my account  
**So that** I can secure my account on shared devices

**Acceptance Criteria**:
- [ ] User can click logout button
- [ ] JWT token removed from localStorage
- [ ] User redirected to login page
- [ ] All protected routes redirect to login after logout

**Implementation**: Client-side only (clear localStorage)

---

### US-2.4: Protected Matchup Creation
**As a** logged-in player  
**I want to** create matchups tied to my account  
**So that** my games are tracked in my history

**Acceptance Criteria**:
- [ ] Only authenticated users can create matchups
- [ ] Matchup creator's user_id stored with matchup
- [ ] Creator's username displayed as Player 1
- [ ] Unauthenticated users see "Login to create matchup" message
- [ ] JWT token sent with matchup creation request

**API**: `POST /matchup/create` (now requires Authentication header)
```json
Headers: {
  "Authorization": "Bearer {jwt_token}"
}
```

---

## Epic 2: Faction Selection

### US-2.5: View Available Factions
**As a** player creating a matchup  
**I want to** see all available factions for my chosen game system  
**So that** I can select the faction I'm playing

**Acceptance Criteria**:
- [ ] Faction dropdown appears after selecting game system
- [ ] Factions filtered by selected game system
- [ ] Factions displayed with name and optional icon
- [ ] Default selection is first faction alphabetically
- [ ] AoS shows ~15 factions (Stormcast, Kruleboyz, Seraphon, etc.)
- [ ] 40k shows ~20 factions (Space Marines, Orks, Necrons, etc.)
- [ ] Old World shows ~12 factions (Empire, Orcs & Goblins, Dwarfs, etc.)

**API**: `GET /game-systems/{system}/factions`

**Response**:
```json
{
  "game_system": "age_of_sigmar",
  "factions": [
    {
      "id": "uuid",
      "name": "Stormcast Eternals",
      "abbreviation": "SCE"
    }
  ]
}
```

---

### US-2.6: Select Faction for Army List
**As a** player submitting my army list  
**I want to** specify which faction I'm playing  
**So that** the matchup records my faction choice

**Acceptance Criteria**:
- [ ] Faction selection required before submitting list
- [ ] Selected faction validated against game system
- [ ] Faction name displayed in matchup summary
- [ ] Opponent's faction revealed when matchup completes
- [ ] Faction recorded in matchup history

**API**: `POST /matchup/{id}/submit` (updated)
```json
{
  "player_name": "string",
  "army_list": "string",
  "faction_id": "uuid"
}
```

---

## Epic 3: Matchup History

### US-2.7: View My Matchup History
**As a** logged-in player  
**I want to** see all my past matchups  
**So that** I can review my games and results

**Acceptance Criteria**:
- [ ] History page shows all user's matchups (newest first)
- [ ] Each entry shows: date, opponent, game system, factions, battle plan
- [ ] Pagination: 20 matchups per page
- [ ] Filter by game system (All / AoS / 40k / Old World)
- [ ] Filter by completion status (All / Completed / In Progress)
- [ ] Click matchup to view full details
- [ ] Empty state message if no matchups

**API**: `GET /matchup/history?page=1&limit=20&system=all&status=all`

**Response**:
```json
{
  "matchups": [
    {
      "id": "string",
      "created_at": "iso8601",
      "game_system": "age_of_sigmar",
      "opponent_username": "string",
      "my_faction": "Stormcast Eternals",
      "opponent_faction": "Kruleboyz",
      "battle_plan": "The Liferoots",
      "status": "completed"
    }
  ],
  "total": 150,
  "page": 1,
  "pages": 8
}
```

---

### US-2.8: View Faction Usage Statistics
**As a** logged-in player  
**I want to** see which factions I've played most  
**So that** I can track my army diversity

**Acceptance Criteria**:
- [ ] History page shows faction breakdown
- [ ] Displays count and percentage for each faction played
- [ ] Grouped by game system
- [ ] Shows win rate per faction (when results implemented)

**UI Display**:
```
Age of Sigmar:
- Stormcast Eternals: 12 games (40%)
- Kruleboyz: 8 games (27%)
- Seraphon: 6 games (20%)

Warhammer 40k:
- Space Marines: 5 games (100%)
```

---

## Epic 4: Army List Management

### US-2.9: Save Army Lists
**As a** player  
**I want to** save my army lists to my account  
**So that** I can reuse them in future matchups

**Acceptance Criteria**:
- [ ] Option to save list after matchup creation
- [ ] List saved with name, faction, points value, game system
- [ ] Saved lists appear in dropdown when creating new matchup
- [ ] Can edit/delete saved lists
- [ ] Maximum 50 saved lists per user

**API**: 
- `POST /lists` - Create saved list
- `GET /lists?system={system}` - Get user's lists
- `PUT /lists/{id}` - Update list
- `DELETE /lists/{id}` - Delete list

---

### US-2.10: List Currency Validation
**As a** player  
**I want** my army list validated against current rules  
**So that** I know my list is legal for the game

**Acceptance Criteria**:
- [ ] Points value validation (e.g., 2000 points for matched play)
- [ ] Ally restrictions enforced
- [ ] Duplicate unit limits checked
- [ ] Mandatory units validated (e.g., Battleline requirements)
- [ ] List format structured (JSON schema)
- [ ] Validation errors shown clearly
- [ ] Optional: Integration with Warhammer app / Battlescribe

**Validation Response**:
```json
{
  "valid": false,
  "errors": [
    {
      "field": "points",
      "message": "List exceeds 2000 points (2150 total)"
    },
    {
      "field": "battleline",
      "message": "Minimum 3 Battleline units required (found 2)"
    }
  ]
}
```

---

## Epic 5: Authenticated Matchup Flow

### US-2.11: Create Authenticated Matchup
**As a** logged-in player  
**I want to** create a matchup with my account  
**So that** it appears in my history and is tied to my identity

**Acceptance Criteria**:
- [ ] Must be logged in to create matchup
- [ ] Creator automatically set as Player 1
- [ ] Creator's username auto-filled
- [ ] Can select from saved lists or enter new list
- [ ] Faction selection required
- [ ] Share link generated immediately

**Updated Flow**:
1. Login required to access /squire/matchup/create
2. Select game system → loads factions
3. Select faction → loads saved lists (optional)
4. Enter/select army list
5. Create matchup → auto-assigned as Player 1

---

### US-2.12: Join Matchup as Second Player
**As a** player with a share link  
**I want to** join a matchup  
**So that** I can compete against the creator

**Acceptance Criteria**:
- [ ] Must be logged in to join matchup
- [ ] Cannot join own matchup
- [ ] See creator's username (not army list yet)
- [ ] Select faction for same game system
- [ ] Enter army list
- [ ] Submit triggers battle plan generation
- [ ] Both players notified of completion

**Flow**:
1. Click share link → redirects to login if needed
2. After login → redirected to matchup join page
3. See opponent username, game system
4. Select faction + enter list
5. Submit → battle plan generated

---

## Epic 6: Matchup History & Statistics

### US-2.13: View Opponent's Profile
**As a** player viewing matchup history  
**I want to** see basic opponent statistics  
**So that** I can learn about players in my community

**Acceptance Criteria**:
- [ ] Click opponent username to view profile
- [ ] Profile shows: username, member since, total games
- [ ] Shows faction breakdown for each game system
- [ ] Shows most-played factions
- [ ] Privacy: No email or personal info exposed

---

## Technical Stories

### TS-2.1: Database Migration
**Technical Task**: Set up PostgreSQL persistence

**Acceptance Criteria**:
- [ ] Alembic configured for migrations
- [ ] Initial migration creates users, matchups, factions, army_lists tables
- [ ] Foreign key relationships established
- [ ] Indexes on frequently queried fields (user_id, created_at)
- [ ] Migration script documented in docs/DATABASE.md

**Tables**:
- `users`: id, username, email, password_hash, created_at, updated_at
- `matchups`: id, game_system, player1_id, player2_id, faction1_id, faction2_id, battle_plan_json, status, created_at, completed_at
- `factions`: id, game_system, name, abbreviation
- `army_lists`: id, user_id, faction_id, name, list_text, points_value, created_at

---

### TS-2.2: Authentication Middleware
**Technical Task**: JWT validation for protected routes

**Acceptance Criteria**:
- [ ] Decorator for protected endpoints: @require_auth
- [ ] Validates JWT signature and expiration
- [ ] Injects user_id into request context
- [ ] Returns 401 for invalid/missing tokens
- [ ] Returns 403 for expired tokens

---

### TS-2.3: Password Security
**Technical Task**: Secure password handling

**Acceptance Criteria**:
- [ ] bcrypt for password hashing (cost factor: 12)
- [ ] Passwords never logged or exposed in responses
- [ ] Password reset flow (future: requires email)
- [ ] Rate limiting on login attempts (max 5 per minute)

---

## Definition of Done

For each story to be considered complete:
- [ ] Backend implementation with validation
- [ ] Frontend implementation with error handling
- [ ] Unit tests (90%+ coverage)
- [ ] Integration tests for full flow
- [ ] Activity scripts updated if needed
- [ ] Manual UAT testing passed
- [ ] Documentation updated
- [ ] Code reviewed and merged to main

## Sprint Planning Recommendation

**Sprint 1 (Week 1)**: Authentication Foundation
- US-2.1, US-2.2, US-2.3 (Registration, Login, Logout)
- TS-2.1, TS-2.2, TS-2.3 (Database, Middleware, Security)

**Sprint 2 (Week 2)**: Factions & Lists
- US-2.5, US-2.6 (Faction selection)
- US-2.9 (Save army lists)
- US-2.11, US-2.12 (Authenticated matchup flow)

**Sprint 3 (Week 3)**: History & Validation
- US-2.7, US-2.8 (Matchup history)
- US-2.10 (List validation)
- US-2.13 (Opponent profiles)
