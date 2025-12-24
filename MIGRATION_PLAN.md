# SquigLeague App Rewrite - Migration Action Plan

**Branch:** `feature/app-rewrite`  
**Created:** 2025-12-24  
**Status:** Phase 3 Complete ✅

---

## Executive Summary

This document outlines the systematic migration from the current SquigLeague structure to the new modular architecture described in the comprehensive plan. The migration focuses on **reusing existing code** where possible while implementing the new structure.

**Progress:**
- ✅ Phase 1: Backend Foundation (Complete)
- ✅ Phase 2: Users Module with OAuth (Complete)
- ✅ Phase 3: Matchup Module (Complete)
- ✅ Phase 4: ELO Module (Complete)
- ✅ Phase 5: Leagues Module (Complete)
- ✅ Phase 6: Frontend Vue 3 Rewrite (Complete)
- 🔄 Phase 7: Integration & Testing (Next)

---

## Current State Analysis

### Existing Components (Reusable)

#### Backend (`squire/`)
- ✅ **auth.py** - User registration, login, JWT, email verification
- ✅ **database.py** - SQLAlchemy models (User, EmailVerificationToken, Faction, Matchup)
- ✅ **matchup.py** - Matchup logic (in-memory, needs DB persistence)
- ✅ **battle_plans.py** - Battle plan generation (AoS, 40k, TOW)
- ✅ **email_service.py** - Email sending (needs removal per new plan)
- ✅ **admin.py** - Admin functions (user management, factions)
- ✅ **routes.py** - FastAPI routes (needs restructuring)

#### Frontend (`frontend/public/`)
- ✅ **login.js** - Login functionality
- ✅ **Static HTML** - Basic UI structure
- ⚠️ **No Vue.js yet** - needs complete rewrite

#### Infrastructure
- ✅ **Docker Compose** - Already configured
- ✅ **Nginx** - Reverse proxy setup
- ✅ **Alembic** - Database migrations
- ✅ **PostgreSQL** - Database setup
- ✅ **Justfile** - Command automation

### What Needs to Change

1. **Backend Structure:** Flat `squire/` → Modular `backend/app/{users,matchup,elo,leagues,core}/`
2. **Auth System:** Email/password → Google + Discord OAuth (FastAPI Users)
3. **Frontend:** Static HTML/JS → Vue 3 + Composition API + TailwindCSS
4. **Matchup:** In-memory → PostgreSQL persistence
5. **ELO System:** NEW module (doesn't exist yet)
6. **Leagues:** NEW module (doesn't exist yet)
7. **Email Service:** Remove completely (no email notifications)

---

## Migration Strategy

### Phase 0: Preparation (Current)
- [x] Create `feature/app-rewrite` branch
- [x] Analyze existing codebase
- [x] Document migration plan
- [ ] Back up current working state

### Phase 1: Backend Foundation (Priority 1)
**Goal:** New directory structure + Core module + Database setup

#### 1.1 Directory Structure
```bash
backend/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI app entry point
│   ├── config.py        # Settings (Pydantic BaseSettings)
│   ├── db.py            # Database session management
│   └── core/            # NEW - Common utilities
│       ├── __init__.py
│       ├── security.py  # JWT, password hashing
│       ├── deps.py      # Dependency injection
│       └── permissions.py  # Role-based access
├── alembic/
├── requirements.txt
├── Dockerfile
└── .env
```

#### 1.2 Reuse Plan
- **FROM:** `squire/database.py` → **TO:** `backend/app/db.py` + individual module models
- **FROM:** `squire/auth.py` (JWT/hashing) → **TO:** `backend/app/core/security.py`
- **FROM:** `alembic/` → **TO:** `backend/alembic/` (copy as-is)

#### 1.3 New Components
- `backend/app/config.py` - Settings with OAuth credentials
- `backend/app/core/deps.py` - `get_session()`, `get_current_user()`
- `backend/app/core/permissions.py` - `require_role()` decorator

**Deliverable:** Backend structure ready, database connects, migrations work

---

### Phase 2: Users Module (Priority 2)
**Goal:** FastAPI Users + Google + Discord OAuth

#### 2.1 Users Module Structure
```bash
backend/app/users/
├── __init__.py
├── models.py      # SQLModel User (FastAPI Users compatible)
├── schemas.py     # Pydantic schemas
├── routes.py      # Auth endpoints
└── auth.py        # FastAPI Users config + OAuth clients
```

#### 2.2 Reuse Plan
- **FROM:** `squire/database.py` (User model) → **TO:** `backend/app/users/models.py`
  - Keep: username, email, is_admin
  - **REMOVE:** password_hash (OAuth only)
  - **REMOVE:** email_verified (no email verification)
  - **ADD:** role (player/organizer/admin)
  - **ADD:** FastAPI Users fields (is_active, is_superuser, is_verified)
  
- **FROM:** `squire/auth.py` (password hashing) → **TO:** `backend/app/core/security.py`
  - Keep: `hash_password()`, `verify_password()` (for admin if needed)
  - **REMOVE:** JWT creation (FastAPI Users handles this)
  - **REMOVE:** Email verification logic

#### 2.3 New Components
- `backend/app/users/auth.py` - FastAPI Users setup:
  ```python
  from fastapi_users import FastAPIUsers
  from httpx_oauth.clients.google import GoogleOAuth2
  from httpx_oauth.clients.discord import DiscordOAuth2
  
  google_oauth_client = GoogleOAuth2(...)
  discord_oauth_client = DiscordOAuth2(...)
  
  fastapi_users = FastAPIUsers[User, int](
      get_user_manager,
      [cookie_authentication],
  )
  ```

- OAuth routes:
  - `GET /api/auth/google/authorize`
  - `GET /api/auth/google/callback`
  - `GET /api/auth/discord/authorize`
  - `GET /api/auth/discord/callback`
  - `POST /api/auth/logout`
  - `GET /api/auth/me`

**Deliverable:** Working OAuth login with Google + Discord

---

### Phase 3: Matchup Module (Priority 3)
**Goal:** Persistent matchup with PostgreSQL

#### 3.1 Matchup Module Structure
```bash
backend/app/matchup/
├── __init__.py
├── models.py      # SQLModel Matchup
├── schemas.py     # Pydantic request/response
├── routes.py      # Matchup endpoints
└── service.py     # Business logic (create, submit, reveal)
```

#### 3.2 Reuse Plan
- **FROM:** `squire/matchup.py` → **TO:** `backend/app/matchup/service.py`
  - Keep: Core logic (create, submit, reveal, is_complete)
  - **CHANGE:** In-memory dict → SQLModel + database
  - Keep: `generate_battle_plan()` call
  
- **FROM:** `squire/battle_plans.py` → **TO:** `backend/app/matchup/battle_plans.py`
  - Keep: Entire module (works perfectly as-is)
  - Maps are hardcoded for now (Phase 7 will integrate BSData)

- **FROM:** `squire/database.py` (Matchup model) → **TO:** `backend/app/matchup/models.py`
  - Keep: UUID, player IDs, lists, timestamps
  - **ADD:** expires_at (7 days)
  - **ADD:** map_name (from battle plan)

#### 3.3 Endpoints
```python
POST /api/matchup           # Create new matchup
GET /api/matchup/{uuid}     # Get status
POST /api/matchup/{uuid}/submit  # Submit list
GET /api/matchup/{uuid}/reveal   # Reveal lists + map
GET /api/matchup/history    # User's matchup history (if logged in)
```

#### 3.4 Key Changes
- **Anonymous support:** `player1_id` and `player2_id` are optional
- **ELO exclusion:** Anonymous matchups do NOT update ELO
- **Expiry:** Cron job or manual cleanup of matchups > 7 days old

**Deliverable:** Matchup works end-to-end with database persistence

---

### Phase 4: ELO Module (Priority 4)
**Goal:** Complete ELO system (League, Tournament, Global)

#### 4.1 ELO Module Structure
```bash
backend/app/elo/
├── __init__.py
├── models.py        # ELORating, ELOHistory, ELOConfig
├── schemas.py       # Response schemas
├── routes.py        # ELO endpoints
├── service.py       # update_elo_after_match(), get_leaderboard()
└── calculator.py    # ELO math (expected score, new rating)
```

#### 4.2 Reuse Plan
- **FROM:** None (new module)
- **INSPIRATION:** Plan's detailed ELO design

#### 4.3 Models
```python
# models.py
class ELOConfig(SQLModel, table=True):
    name: str  # "league", "tournament", "global"
    k_factor: int = 50
    is_active: bool = True

class ELORating(SQLModel, table=True):
    user_id: int
    rating_type: str  # "league", "tournament", "global"
    rating: int = 1000
    games_played: int = 0
    wins: int = 0
    losses: int = 0
    draws: int = 0
    peak_rating: int = 1000
    peak_date: Optional[datetime] = None

class ELOHistory(SQLModel, table=True):
    user_id: int
    opponent_id: int
    rating_type: str
    old_rating: int
    new_rating: int
    rating_change: int
    result: str  # "win", "draw", "loss"
    k_factor: int
    match_id: Optional[int] = None
    match_type: Optional[str] = None  # "league", "tournament"
```

#### 4.4 Service Logic
```python
# service.py
def get_k_factor(games_played: int, global_k: int) -> int:
    """K=50 for first 5 games, then global K"""
    return 50 if games_played < 5 else global_k

def update_elo_after_match(
    player1_id, player2_id, result, rating_type, match_id=None
):
    """Update ELO for both players"""
    # Get current ratings
    # Calculate K-factors (new player rule)
    # Calculate new ratings
    # Update ELORating models
    # Create ELOHistory records
    # Update peak ratings
```

#### 4.5 Endpoints
```python
GET /api/elo/leaderboard/{rating_type}  # Public
GET /api/elo/user/{user_id}             # Public
GET /api/elo/history/{user_id}          # Public
GET /api/elo/config/{rating_type}       # Public
PATCH /api/elo/config/{rating_type}     # Admin only (change K-factor)
```

#### 4.6 Database Seeding
```python
# Alembic migration: seed default configs
INSERT INTO elo_configs (name, k_factor, is_active)
VALUES 
    ('league', 50, true),
    ('tournament', 50, true),
    ('global', 50, true);
```

**Deliverable:** ELO system works, leaderboards public, admin can configure K-factor

---

### Phase 5: Leagues Module (Priority 5)
**Goal:** Create leagues, play group phase, update ELO

#### 5.1 Leagues Module Structure
```bash
backend/app/leagues/
├── __init__.py
├── models.py        # League, Participant, Match, Standings
├── schemas.py       # Request/response models
├── routes.py        # League endpoints
├── service.py       # League management logic
├── scoring.py       # Point calculation + tiebreakers
└── formats.py       # Group/playoff format definitions
```

#### 5.2 Reuse Plan
- **FROM:** None (new module)
- **INSPIRATION:** Plan's detailed league design

#### 5.3 Models
```python
# models.py
class League(SQLModel, table=True):
    name: str
    season: str
    organizer_id: int
    format_type: str = "group_playoff"
    config: dict = {}  # JSON column
    status: str = "draft"  # draft, registration, group_phase, playoff, finished
    start_date: date
    registration_deadline: date

class LeagueParticipant(SQLModel, table=True):
    league_id: int
    user_id: int
    group_number: Optional[int] = None
    playoff_list: Optional[str] = None

class LeagueMatch(SQLModel, table=True):
    league_id: int
    player1_id: int
    player2_id: int
    phase: str  # "group", "playoff"
    round_number: int
    player1_score: Optional[int] = None  # Battle points (0-100)
    player2_score: Optional[int] = None
    player1_points: Optional[int] = None  # League points
    player2_points: Optional[int] = None
    played: bool = False
    deadline: datetime

class LeagueStandings(SQLModel, table=True):
    league_id: int
    user_id: int
    phase: str
    total_points: int = 0
    matches_played: int = 0
    matches_total: int = 0
    wins: int = 0
    draws: int = 0
    losses: int = 0
    position: int = 0
```

#### 5.4 Scoring System
```python
# scoring.py (from plan)
def calculate_match_points(player_score: int, opponent_score: int) -> int:
    """
    - Win: 1000 + bonus
    - Draw: 600 + bonus
    - Loss: 200 + bonus
    - Bonus: (player - opponent + 50), max 100, min 0
    """
    if player_score > opponent_score:
        base = 1000
    elif player_score == opponent_score:
        base = 600
    else:
        base = 200
    
    bonus = min(100, max(0, (player_score - opponent_score) + 50))
    return base + bonus
```

#### 5.5 ELO Integration
When match result is submitted:
1. Calculate league points
2. Update standings
3. **Update League ELO** (call `update_elo_after_match(rating_type="league")`)
4. **Update Global ELO** (call `update_elo_after_match(rating_type="global")`)

#### 5.6 Endpoints
```python
POST /api/leagues                       # Create league (organizer)
GET /api/leagues                        # List leagues
GET /api/leagues/{id}                   # League details
POST /api/leagues/{id}/join             # Join league
POST /api/leagues/{id}/start            # Start (generate groups)
POST /api/leagues/{id}/matches/{mid}/result  # Submit result + update ELO
GET /api/leagues/{id}/standings         # Group/overall standings
PATCH /api/leagues/{id}                 # Edit (organizer)
DELETE /api/leagues/{id}                # Delete (admin)
```

**Deliverable:** Leagues work through group phase, ELO updates automatically

---

### Phase 6: Frontend Rewrite (Priority 6)
**Goal:** Vue 3 + TailwindCSS + Dark mode

#### 6.1 Frontend Structure
```bash
frontend/
├── src/
│   ├── main.js
│   ├── App.vue
│   ├── router/
│   │   └── index.js
│   ├── stores/
│   │   ├── auth.js      # Pinia store for auth
│   │   └── theme.js     # Dark/light mode
│   ├── views/
│   │   ├── Matchup.vue
│   │   ├── MatchupView.vue
│   │   ├── Leagues.vue
│   │   ├── LeagueDetail.vue
│   │   ├── Leaderboard.vue
│   │   ├── Login.vue
│   │   ├── Settings.vue
│   │   └── Admin/
│   │       ├── Dashboard.vue
│   │       ├── Users.vue
│   │       └── ELOSettings.vue
│   ├── components/
│   │   ├── Sidebar.vue
│   │   ├── ThemeToggle.vue
│   │   ├── LeagueTable.vue
│   │   └── UserELOStats.vue
│   ├── assets/
│   └── styles/
│       └── main.css     # TailwindCSS
├── public/
├── package.json
├── vite.config.js
├── tailwind.config.js
└── Dockerfile
```

#### 6.2 Reuse Plan
- **FROM:** `frontend/public/modules/squire/login.js` → **TO:** `frontend/src/stores/auth.js` (logic only)
- **FROM:** `frontend/public/static/` → **TO:** `frontend/public/` (static assets)
- **DISCARD:** All HTML/vanilla JS → Replace with Vue components

#### 6.3 Tech Stack
```json
{
  "dependencies": {
    "vue": "^3.4.0",
    "vue-router": "^4.2.0",
    "pinia": "^2.1.0",
    "axios": "^1.6.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "vite": "^5.0.0",
    "tailwindcss": "^3.4.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0"
  }
}
```

#### 6.4 Theme (TailwindCSS)
```js
// tailwind.config.js
module.exports = {
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#FFD700',  // Gold/Yellow
          dark: '#FFA500',
        },
        background: {
          dark: '#0A0A0A',
        },
        surface: {
          dark: '#1A1A1A',
        }
      }
    }
  }
}
```

#### 6.5 Key Views

**Login.vue**
```vue
<template>
  <div class="login-container">
    <h1>Login to SquigLeague</h1>
    <button @click="loginWithGoogle">Continue with Google</button>
    <button @click="loginWithDiscord">Continue with Discord</button>
  </div>
</template>

<script setup>
const loginWithGoogle = () => {
  window.location.href = '/api/auth/google/authorize'
}
const loginWithDiscord = () => {
  window.location.href = '/api/auth/discord/authorize'
}
</script>
```

**Leaderboard.vue**
- 3 tabs: League ELO, Tournament ELO, Global ELO
- Table: Rank, Player, Rating, Games, W-D-L, Win Rate
- Public (no auth required)

**Matchup.vue**
- Create matchup button
- Anonymous support
- Share link
- Submit list form

**Leagues.vue**
- List all leagues
- Filter: upcoming, ongoing, finished
- "Join League" button

**Admin/Dashboard.vue**
- User count, matchup count, league count
- Recent activity
- Quick actions (create league, manage users)

**Admin/ELOSettings.vue**
- Change K-factor per rating type
- View current configs

**Deliverable:** Full Vue 3 frontend with dark mode, OAuth login, all main views

---

### Phase 7: Playoff System (Priority 7)
**Goal:** Complete league lifecycle (groups → playoff)

#### 7.1 Playoff Features
- Seeding from group standings (tiebreakers)
- Bracket generation (top 4, top 8, top 16)
- Locked lists
- Single elimination
- Winner announcement

#### 7.2 Frontend
- `PlayoffBracket.vue` component
- Visual bracket display
- Match results submission

**Deliverable:** Leagues finish with playoff winners

---

### Phase 8: Admin Panel & Polish (Priority 8)
**Goal:** Production-ready application

#### 8.1 Admin Features
- User management (promote to organizer, ban)
- ELO config management
- League management (edit, delete, force results)
- System stats dashboard

#### 8.2 Production Setup
- SSL certificates
- Environment-specific configs
- Error handling & logging
- Rate limiting
- CORS configuration

#### 8.3 Testing
```bash
backend/tests/
├── test_users.py
├── test_matchup.py
├── test_elo.py
└── test_leagues.py

frontend/tests/
└── e2e/
    └── login.spec.js
```

**Deliverable:** Stable production deployment

---

### Phase 9: Data Importer (TODO - Later)
**Goal:** BSData integration for maps

#### 9.1 Features
- Fetch BSData JSON from GitHub
- Parse maps & scenarios
- Store in database
- Replace hardcoded maps in matchup

#### 9.2 Module Structure
```bash
backend/app/data_importer/
├── __init__.py
├── models.py       # GameMap
├── routes.py       # /sync endpoint (admin)
└── bsdata.py       # GitHub API + parser
```

**Deliverable:** Matchup uses real BSData maps

---

### Phase 10: Tournaments (TODO - Future)
**Goal:** Tournament system with Tournament ELO

#### 10.1 Features
- Single elimination / Swiss
- Tournament ELO tracking
- Global ELO update

**Deliverable:** Tournament module operational

---

### Phase 11: List Builder (TODO - Future)
**Goal:** Army list creation tool

**Deliverable:** List builder module

---

### Phase 12: Collections (TODO - Far Future)
**Goal:** Miniature collection management

**Deliverable:** Collections module

---

## Code Reuse Matrix

| Current File | New Location | Reuse % | Notes |
|--------------|--------------|---------|-------|
| `squire/auth.py` | `backend/app/core/security.py` | 30% | Keep hashing, remove JWT/email |
| `squire/database.py` | Multiple modules | 50% | Split models across modules |
| `squire/matchup.py` | `backend/app/matchup/service.py` | 70% | Keep logic, add DB |
| `squire/battle_plans.py` | `backend/app/matchup/battle_plans.py` | 95% | Nearly unchanged |
| `squire/admin.py` | `backend/app/users/routes.py` (admin) | 40% | Refactor for FastAPI Users |
| `squire/routes.py` | Multiple routers | 20% | Split by module |
| `squire/email_service.py` | **REMOVED** | 0% | No email in new plan |
| `alembic/` | `backend/alembic/` | 80% | Keep structure, new migrations |
| `docker-compose.yml` | `docker-compose.yml` | 90% | Minor updates |
| `nginx/nginx.conf` | `nginx/nginx.conf` | 95% | Nearly unchanged |
| `justfile` | `justfile` | 80% | Update paths |
| `frontend/public/` | **REPLACED** | 0% | Complete Vue rewrite |

---

## Dependencies Changes

### Backend Requirements
```txt
# NEW ADDITIONS
fastapi-users[sqlalchemy]==12.1.3
httpx-oauth==0.13.0
sqlmodel==0.0.14

# KEEP
fastapi==0.109.0
uvicorn[standard]==0.27.0
psycopg2-binary==2.9.9
alembic==1.13.1
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
pydantic[email]==2.5.3
httpx==0.26.0

# REMOVE
sendgrid (no email)
```

### Frontend Dependencies
```json
{
  "dependencies": {
    "vue": "^3.4.0",
    "vue-router": "^4.2.0",
    "pinia": "^2.1.0",
    "axios": "^1.6.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "vite": "^5.0.0",
    "tailwindcss": "^3.4.0"
  }
}
```

---

## Testing Strategy

### Backend Tests
```python
# Priority tests for each phase
pytest backend/tests/test_users.py          # OAuth, roles
pytest backend/tests/test_matchup.py        # Create, submit, reveal
pytest backend/tests/test_elo.py            # K-factor, rating calculation
pytest backend/tests/test_leagues.py        # Scoring, standings, ELO update
```

### Frontend Tests
```js
// E2E critical paths
cy.test('OAuth login flow')
cy.test('Create matchup anonymous')
cy.test('Join league and submit result')
cy.test('View leaderboard')
```

---

## Rollout Plan

### Week 1-2: Foundation (Phases 1-2)
- [ ] Backend structure
- [ ] Users module + OAuth
- [ ] Database migrations
- [ ] Docker setup
- **Checkpoint:** Can login with Google/Discord

### Week 3: Matchup (Phase 3)
- [ ] Matchup models
- [ ] Matchup service
- [ ] Battle plans integration
- **Checkpoint:** Matchup works with DB

### Week 4: ELO (Phase 4)
- [ ] ELO models
- [ ] ELO calculator
- [ ] Leaderboards
- [ ] Admin K-factor config
- **Checkpoint:** ELO system operational

### Week 5-6: Leagues (Phase 5)
- [ ] League models
- [ ] Group phase logic
- [ ] Scoring system
- [ ] ELO integration
- **Checkpoint:** Can create and play leagues

### Week 7: Frontend (Phase 6)
- [ ] Vue 3 setup
- [ ] TailwindCSS dark mode
- [ ] All main views
- [ ] OAuth integration
- **Checkpoint:** Full UI working

### Week 8: Playoff & Polish (Phases 7-8)
- [ ] Playoff bracket
- [ ] Admin panel
- [ ] Production deploy
- **Checkpoint:** Production ready

---

## Risk Mitigation

### High Risk Items
1. **OAuth Configuration**
   - Risk: Google/Discord OAuth setup issues
   - Mitigation: Test in dev first, clear documentation
   
2. **Database Migration**
   - Risk: Data loss during migration
   - Mitigation: Full backup before starting, test migrations in dev
   
3. **Frontend Rewrite**
   - Risk: Loss of current functionality
   - Mitigation: Keep old frontend accessible until new one is complete

### Rollback Strategy
- Keep `main` branch untouched
- All work in `feature/app-rewrite`
- Can revert to old system anytime before merge

---

## Success Criteria

### Phase 1-2 Success
- [x] Backend runs on Docker
- [x] Can login with Google OAuth
- [x] Can login with Discord OAuth
- [x] User roles work (player/organizer/admin)

### Phase 3 Success
- [ ] Anonymous users can create matchup
- [ ] Logged users can create matchup
- [ ] Lists persist in database
- [ ] Battle plan generated correctly

### Phase 4 Success
- [ ] ELO updates after matches
- [ ] K=50 for first 5 games works
- [ ] Leaderboards display correctly
- [ ] Admin can change K-factor

### Phase 5 Success
- [ ] Organizer can create league
- [ ] Players can join and play
- [ ] Standings calculate correctly
- [ ] League ELO + Global ELO update

### Phase 6 Success
- [ ] Vue app loads
- [ ] Dark mode works
- [ ] All views accessible
- [ ] OAuth login from frontend works

### Final Success
- [ ] Production deployment successful
- [ ] All tests passing
- [ ] No critical bugs
- [ ] Admin panel functional
- [ ] Documentation complete

---

## Next Steps

1. **Immediate:** Create backend directory structure
2. **Day 1:** Migrate database models to SQLModel
3. **Day 2-3:** Implement Users module with OAuth
4. **Week 1:** Complete Phases 1-2
5. **Weekly:** Review progress against plan

---

## Notes

- **Preserve Git History:** Keep old code in separate commits before deletion
- **Documentation:** Update README.md with new structure
- **Environment Variables:** New `.env.example` with OAuth keys
- **Database:** Create new migrations, don't modify old ones

---

**Status:** Ready to begin implementation  
**Next Action:** Create backend directory structure (Phase 1.1)
