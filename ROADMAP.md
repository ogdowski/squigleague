# Squig League - Development Roadmap

**Last Updated**: November 20, 2025  
**Current Version**: 0.2.1  
**Active Module**: Herald

---

## Overview

Squig League is being developed in phases, with each phase adding new modules or capabilities. This document outlines the development roadmap, priorities, and feature specifications.

## Phase Status

| Phase | Module | Status | Priority | Target |
|-------|--------|--------|----------|--------|
| Phase 1 | Herald | ✅ Complete | - | Live |
| Phase 2 | Squire | 🔨 In Planning | HIGH | Q1 2026 |
| Phase 3 | Core Auth | 📋 Planned | HIGH | Q2 2026 |
| Phase 4 | Archivist | 📋 Planned | MEDIUM | Q3 2026 |
| Phase 5 | Marshal | 📋 Planned | MEDIUM | Q4 2026 |
| Phase 6 | Keeper | 📋 Planned | LOW | 2027 |
| Phase 7 | Patron | 📋 Planned | MEDIUM | 2027 |

---

## Phase 1: Herald ✅ COMPLETE

**Purpose**: Blind army list exchange for fair play

### Completed Features (v0.2.1)
- ✅ Cryptographic list hashing (SHA-256)
- ✅ Anonymous exchanges (no authentication required)
- ✅ Human-readable exchange IDs
- ✅ Rate limiting and abuse detection
- ✅ Frontend/backend separation
- ✅ Admin monitoring endpoints
- ✅ Auto-cleanup (30-day retention)
- ✅ Multi-arch Docker deployment
- ✅ Production SSL deployment

### Planned Enhancements
- [ ] Mission randomizer (hardcoded AoS/40k missions)
- [ ] PDF export of exchanges
- [ ] Email notifications (optional, pre-auth)
- [ ] QR code generation for URLs
- [ ] List templates and formatting

---

## Phase 2: Squire 🔨 IN PLANNING

**Purpose**: Battle score tracking, matchup history, and player statistics

**Priority**: HIGH - Requested by community  
**Target**: Q1 2026  
**Dependencies**: None (can start immediately)

### Core Features

#### 1. Battle Plan Randomization
- **Multi-System Support**
  - Game system dropdown selector:
    - Warhammer Age of Sigmar (4th Edition)
    - Warhammer 40,000 (10th Edition)
    - Warhammer: The Old World
    - *Extensible for future systems*
  - System-specific mission pools
  - System-specific point categories
  - Mission versioning (track current season)

- **AoS 4th Edition Missions**
  - Current season mission pool (2024-2025)
  - Random mission selection
  - Mission details display (objectives, deployment, etc.)
  - Filter by game size (1000, 2000, 3000 points)
  
- **Warhammer 40k 10th Edition Missions**
  - Current season mission pool (Leviathan)
  - Random mission selection
  - Mission details display
  - Filter by game type (Combat Patrol, Incursion, Strike Force, Onslaught)

- **Warhammer: The Old World Missions**
  - Current edition mission pool
  - Random mission selection
  - Mission details display
  - Filter by game size (1000, 2000, 3000 points)

- **Mission Selection UI**
  - Game system dropdown (AoS / 40k / Old World)
  - Point value selector (system-dependent)
  - "Roll Mission" button
  - Display mission card with objectives
  - Shareable mission URL
  - Link mission to battle (optional)

#### 2. Battle Tracking & Self-Reporting

- **Battle Creation**
  - Player A creates battle
  - Select game system (AoS / 40k)
  - Select point value
  - Optional: Link Herald exchange
  - Optional: Link randomized mission
  - Generates battle ID and URL

- **Player Registration**
  - Both players enter basic info:
    - Player name/nickname
    - Faction (dropdown per game system)
    - Points value
    - Optional: Army list notes
  
- **Battle Execution**
  - Round-by-round score entry
  - Each player reports their own score
  - VP tracking per round
  - Final score submission
  - Battle duration tracking
  - Optional: Notes per round

- **Self-Reporting System**
  - Both players must confirm final scores
  - Discrepancy detection (if scores don't match)
  - Resolution workflow for mismatches
  - Timestamp all score entries

#### 3. Player Tracking

- **Anonymous Player Profiles** (Phase 2 - No Auth)
  - Player identified by unique code/URL
  - Claim URL to view your stats
  - No password required (bookmark system)

- **Player Statistics**
  - Total games played
  - Win/Loss/Draw record
  - Factions played (with counts)
  - Average VP scored
  - Average game duration
  - Most played against (opponents)
  - Favorite missions

- **Authenticated Player Profiles** (Phase 3 - After Auth)
  - Link all anonymous battles to account
  - Public profile pages
  - Achievement badges
  - Rating/ELO system

#### 4. Matchup History

- **Battle History View**
  - List of all battles for a player
  - Filter by:
    - Date range
    - Game system (AoS / 40k)
    - Faction (yours)
    - Opponent faction
    - Mission type
    - Result (W/L/D)
  - Sort by date, VP difference, duration

- **Head-to-Head Records**
  - Player A vs Player B history
  - Record between specific players
  - Faction matchup analysis
  - Common missions played

- **Matchup Matrix**
  - Your faction vs all opponent factions
  - Win rate per matchup
  - Sample size per matchup
  - Average VP differential

#### 5. Faction Statistics

- **Per-Faction Stats**
  - Games played with faction
  - Win rate
  - Average VP scored
  - Average VP against
  - Most common opponent factions
  - Best/worst matchups

- **Community Faction Stats**
  - Most played factions (global)
  - Faction win rates (global)
  - Meta analysis
  - Trending factions over time

#### 6. Time-Period Analytics

- **Date Range Filters**
  - Last 7 days
  - Last 30 days
  - Last 90 days
  - Custom date range
  - By tournament/event

- **Statistical Tables**
  - Games per period
  - Faction usage per period
  - Win rates per period
  - VP trends over time
  - Activity heatmap (calendar view)

### Database Schema

```sql
-- SQUIRE: Battle tracking and statistics

-- Players (anonymous in Phase 2, linked to core_users in Phase 3)
CREATE TABLE squire_players (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    claim_code TEXT UNIQUE NOT NULL,           -- For anonymous claiming
    display_name TEXT NOT NULL,
    user_id UUID REFERENCES core_users(id),    -- NULL until Phase 3
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_battle_at TIMESTAMPTZ
);

-- Battles
CREATE TABLE squire_battles (
    id TEXT PRIMARY KEY,                        -- Format: adjective-noun-XXXX
    game_system_id TEXT REFERENCES squire_game_systems(id) NOT NULL,
    points_value INTEGER NOT NULL,              -- 1000, 2000, etc.
    mission_id TEXT REFERENCES squire_missions(id),  -- Link to mission if randomized
    herald_exchange_id TEXT,                    -- Link to Herald exchange if used
    
    player_a_id UUID REFERENCES squire_players(id) NOT NULL,
    player_a_faction TEXT NOT NULL,
    player_a_list_notes TEXT,
    
    player_b_id UUID REFERENCES squire_players(id) NOT NULL,
    player_b_faction TEXT NOT NULL,
    player_b_list_notes TEXT,
    
    status TEXT NOT NULL DEFAULT 'setup',       -- 'setup', 'in_progress', 'completed', 'disputed'
    
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Battle rounds (score tracking per round)
CREATE TABLE squire_battle_rounds (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    battle_id TEXT REFERENCES squire_battles(id) ON DELETE CASCADE,
    round_number INTEGER NOT NULL,
    
    player_a_vp INTEGER,
    player_a_reported_at TIMESTAMPTZ,
    
    player_b_vp INTEGER,
    player_b_reported_at TIMESTAMPTZ,
    
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(battle_id, round_number)
);

-- Final battle results
CREATE TABLE squire_battle_results (
    battle_id TEXT PRIMARY KEY REFERENCES squire_battles(id) ON DELETE CASCADE,
    
    player_a_total_vp INTEGER NOT NULL,
    player_a_confirmed_at TIMESTAMPTZ,
    
    player_b_total_vp INTEGER NOT NULL,
    player_b_confirmed_at TIMESTAMPTZ,
    
    result TEXT NOT NULL,                       -- 'player_a_win', 'player_b_win', 'draw'
    vp_difference INTEGER NOT NULL,
    
    disputed BOOLEAN DEFAULT FALSE,
    disputed_reason TEXT,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Game systems (extensible list)
CREATE TABLE squire_game_systems (
    id TEXT PRIMARY KEY,                        -- 'aos', '40k', 'old_world'
    display_name TEXT NOT NULL,                 -- 'Age of Sigmar', 'Warhammer 40,000'
    current_edition TEXT NOT NULL,              -- '4th', '10th', '1st'
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Missions (data from official sources)
CREATE TABLE squire_missions (
    id TEXT PRIMARY KEY,
    game_system_id TEXT REFERENCES squire_game_systems(id) NOT NULL,
    edition TEXT NOT NULL,                      -- '4th', '10th', '1st' etc.
    season TEXT,                                -- 'leviathan', '2024-2025', NULL
    mission_name TEXT NOT NULL,
    points_category TEXT,                       -- '1000', '2000', 'any'
    game_type TEXT,                             -- 'combat_patrol', 'strike_force', etc.
    deployment_type TEXT,
    objectives TEXT,
    special_rules TEXT,
    deployment_map_url TEXT,                    -- Link to deployment map image
    is_active BOOLEAN DEFAULT TRUE,             -- Enable/disable missions
    source_url TEXT,                            -- Reference to official source
    version INTEGER DEFAULT 1,                  -- Track updates to mission
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Player statistics cache (updated via triggers/scheduled jobs)
CREATE TABLE squire_player_stats (
    player_id UUID PRIMARY KEY REFERENCES squire_players(id) ON DELETE CASCADE,
    
    total_games INTEGER DEFAULT 0,
    total_wins INTEGER DEFAULT 0,
    total_losses INTEGER DEFAULT 0,
    total_draws INTEGER DEFAULT 0,
    
    total_vp_scored INTEGER DEFAULT 0,
    total_vp_conceded INTEGER DEFAULT 0,
    
    factions_played JSONB DEFAULT '[]'::jsonb,  -- [{"faction": "Orks", "games": 5}]
    
    last_updated TIMESTAMPTZ DEFAULT NOW()
);

-- Faction matchup statistics (global stats)
CREATE TABLE squire_faction_stats (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    game_system_id TEXT REFERENCES squire_game_systems(id) NOT NULL,
    faction_a TEXT NOT NULL,
    faction_b TEXT NOT NULL,
    
    games_played INTEGER DEFAULT 0,
    faction_a_wins INTEGER DEFAULT 0,
    faction_b_wins INTEGER DEFAULT 0,
    draws INTEGER DEFAULT 0,
    
    avg_vp_difference DECIMAL(5,2),
    
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(game_system_id, faction_a, faction_b)
);

-- Indexes
CREATE INDEX idx_battles_player_a ON squire_battles(player_a_id);
CREATE INDEX idx_battles_player_b ON squire_battles(player_b_id);
CREATE INDEX idx_battles_system ON squire_battles(game_system_id);
CREATE INDEX idx_battles_created ON squire_battles(created_at);
CREATE INDEX idx_battles_completed ON squire_battles(completed_at);
CREATE INDEX idx_battles_status ON squire_battles(status);

CREATE INDEX idx_rounds_battle ON squire_battle_rounds(battle_id);
CREATE INDEX idx_results_battle ON squire_battle_results(battle_id);

CREATE INDEX idx_missions_system ON squire_missions(game_system_id);
CREATE INDEX idx_missions_active ON squire_missions(is_active) WHERE is_active = TRUE;

CREATE INDEX idx_faction_stats_system ON squire_faction_stats(game_system_id);
CREATE INDEX idx_faction_stats_factions ON squire_faction_stats(faction_a, faction_b);
```

### API Endpoints

**Mission Randomization**
- `GET /api/squire/missions?system={aos|40k}&points={value}` - List missions
- `GET /api/squire/missions/random?system={aos|40k}&points={value}` - Random mission

**Battle Management**
- `POST /api/squire/battles/create` - Create new battle
- `GET /api/squire/battles/{id}` - Get battle details
- `POST /api/squire/battles/{id}/register-player` - Register player to battle
- `POST /api/squire/battles/{id}/start` - Start battle
- `POST /api/squire/battles/{id}/round` - Submit round scores
- `POST /api/squire/battles/{id}/complete` - Submit final scores
- `POST /api/squire/battles/{id}/confirm` - Confirm final scores
- `GET /api/squire/battles/{id}/status` - Check battle status

**Player Stats**
- `GET /api/squire/players/{claim_code}` - Get player profile
- `GET /api/squire/players/{claim_code}/battles` - Get battle history
- `GET /api/squire/players/{claim_code}/stats` - Get player statistics
- `GET /api/squire/players/{claim_code}/matchups` - Get matchup matrix

**Analytics**
- `GET /api/squire/stats/factions?system={aos|40k}` - Global faction stats
- `GET /api/squire/stats/matchups?faction={name}` - Faction matchup table
- `GET /api/squire/stats/trends?period={7d|30d|90d}` - Activity trends
- `GET /api/squire/stats/leaderboard` - Top players (by games/wins)

### Frontend Pages

**Mission Randomizer**
- `/squire/missions` - Mission randomizer tool

**Battle Flow**
- `/squire/battle/create` - Create new battle
- `/squire/battle/{id}` - Battle detail/tracking page
- `/squire/battle/{id}/round/{n}` - Round score entry

**Player Stats**
- `/squire/player/{claim_code}` - Player profile
- `/squire/player/{claim_code}/battles` - Battle history

**Analytics**
- `/squire/stats` - Global statistics dashboard
- `/squire/stats/factions` - Faction statistics tables
- `/squire/stats/matchups` - Matchup matrix tool

### Technical Implementation

**Backend** (`squire/`)
- FastAPI module (similar to Herald)
- PostgreSQL database access
- JSON API endpoints
- Rate limiting
- Data validation

**Frontend** (`frontend/public/modules/squire/`)
- Alpine.js components
- Battle tracking UI
- Score entry forms
- Statistics dashboards
- Charts (Chart.js via CDN)

**Data Population**
- Python script to seed missions table
- AoS 4th edition missions (JSON file)
- 40k 10th edition missions (JSON file)

### Development Stages

**Stage 1: Core Battle Tracking** (2 weeks)
- Database schema implementation
- Battle creation API
- Player registration
- Round score tracking
- Basic UI for battle flow

**Stage 2: Mission Data Collection & Randomizer** (2 weeks)
- Research and collect official missions from current seasons:
  - AoS 4th Edition (current season)
  - 40k 10th Edition (Leviathan season)
  - Old World (current edition)
- Create mission JSON data files
- Verify mission data accuracy (official sources)
- Implement mission versioning system
- Mission update workflow documentation
- Missions table seeding
- Mission randomization API
- Mission display UI
- Link mission to battle

**Stage 3: Player Statistics** (2 weeks)
- Player profile system
- Stats calculation
- Battle history views
- Claim code system

**Stage 4: Analytics & Matchups** (2 weeks)
- Faction statistics
- Matchup matrix
- Time-period filtering
- Dashboard UI

**Stage 5: Polish & Testing** (1 week)
- UI/UX refinements
- Mobile responsiveness
- Performance optimization
- End-to-end testing

**Total Estimated Time**: 8 weeks

### Quality Control Requirements

**CRITICAL - ZERO TOLERANCE**

- ✅ **100% Unit Test Coverage**
  - All functions must have unit tests
  - All edge cases covered
  - No untested code paths
  - Coverage reports generated on CI

- ✅ **100% Truthfulness (No Mocking)**
  - Integration tests use real database (test containers)
  - API tests call actual endpoints
  - No mocked responses in critical paths
  - Use test fixtures, not mocks
  - Database transactions rolled back in tests

- ✅ **Automated Testing**
  - All tests run on every commit
  - CI pipeline blocks merge if tests fail
  - No manual testing required for regression
  - Performance benchmarks tracked

- ✅ **Code Review Requirements**
  - All PRs require passing tests
  - Coverage cannot decrease
  - New features include tests
  - Test quality reviewed alongside code

### Success Metrics

- 100+ battles tracked in first month
- <500ms average API response time
- 50+ active players in first quarter
- 90%+ score confirmation rate (both players agree)
- 95%+ mobile usability score
- 100% test coverage maintained
- 0 production bugs from untested code

---

## Phase 3: Core Authentication

**Purpose**: Shared user authentication and account management

**Priority**: HIGH  
**Target**: Q2 2026  
**Dependencies**: None (but unlocks features in other modules)

### Features

- User registration and login
- Email verification
- Password reset
- Session management
- OAuth providers (Google, Discord)
- User profiles
- Privacy settings

### Impact on Existing Modules

**Herald**
- Link exchanges to user accounts
- Exchange history
- Private exchanges
- Email notifications
- Export to PDF

**Squire**
- Link anonymous player profiles to accounts
- Persistent player identity
- Friend system
- Challenge system
- Achievement badges
- Public/private profile toggle

---

## Phase 4: Archivist

**Purpose**: BSData integration for Warhammer unit/rules data

**Priority**: MEDIUM  
**Target**: Q3 2026  
**Dependencies**: None

### Features

- BSData repository integration
- Unit/weapon stat viewer
- Rules lookup
- Army faction browser
- Search functionality
- Data caching and updates

### Benefits

- Powers mission randomizer (dynamic missions)
- Enables smart army builder (Marshal)
- Provides rule references during battles

---

## Phase 5: Marshal

**Purpose**: Army list builder

**Priority**: MEDIUM  
**Target**: Q4 2026  
**Dependencies**: Archivist (for unit data)

### Features

- Visual army list creator
- Points auto-calculation
- Rule validation
- Faction-specific rules
- List templates
- Export to PDF
- Share lists publicly
- Direct integration with Herald

---

## Phase 6: Keeper

**Purpose**: Personal miniature collection tracker

**Priority**: LOW  
**Target**: 2027  
**Dependencies**: Core Auth

### Features

- Track owned miniatures
- Painting progress tracking
- Photo uploads
- Collection statistics
- Wishlist management
- Barcode scanning (for boxes)

---

## Phase 7: Patron

**Purpose**: Tournament and league management

**Priority**: MEDIUM  
**Target**: 2027  
**Dependencies**: Core Auth, Squire

### Features

- Tournament creation
- Player registration
- Swiss pairing system
- Automated rounds
- Standings and rankings
- Prize tracking
- Integration with Squire for battle reporting
- Batch Herald exchange creation

---

## Quick Wins & Enhancements

### Herald Improvements
- [ ] Mission randomizer (hardcoded) - 1 week
- [ ] PDF export - 1 week
- [ ] QR code generation - 2 days
- [ ] Dark/light theme toggle - 3 days
- [ ] List character counter - 1 day

### Infrastructure
- [ ] CI/CD pipeline (GitHub Actions) - 1 week
- [ ] Automated testing framework - 1 week
- [ ] Monitoring (Prometheus + Grafana) - 1 week
- [ ] CDN setup (CloudFlare) - 2 days

### Developer Experience
- [ ] API documentation (auto-generated) - 2 days
- [ ] Docker development improvements - 3 days
- [ ] Contribution guide enhancements - 1 day

---

## Contributing to Roadmap

Have ideas or want to contribute? See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Propose new features**: Open an issue using the [feature request template](.github/ISSUE_TEMPLATE/feature_request.md)

**Vote on priorities**: Comment on existing feature requests with 👍 reactions

**Contribute code**: Submit PRs for features marked as "Help Wanted"

---

## Version Naming

- **0.x.x** - Pre-1.0 (Phase 1-3 development)
- **1.0.0** - Full Herald + Squire + Core Auth release
- **2.0.0** - Archivist + Marshal integration
- **3.0.0** - Keeper + Patron completion

---

## License

Copyright © 2025 Ariel Ogdowski  
Licensed under AGPL-3.0 - see [LICENSE](LICENSE)
