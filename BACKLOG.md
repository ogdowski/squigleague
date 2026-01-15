# Squig League - Development Backlog

**Last Updated**: November 20, 2025  
**Format**: GitHub-style task tracking

This backlog tracks specific tasks, bugs, and technical debt. For high-level features and roadmap, see [ROADMAP.md](ROADMAP.md).

---

## Priority Levels

- 🔴 **CRITICAL** - Blocking issues, security vulnerabilities
- 🟠 **HIGH** - Important features, major bugs
- 🟡 **MEDIUM** - Nice-to-have features, minor bugs
- 🟢 **LOW** - Future enhancements, polish

---

## Sprint 1: Squire Phase 2 - Foundation (Weeks 1-2)

### Database & Backend Core

- [ ] 🟠 **SQUIRE-001**: Create Squire database schema
  - Tables: squire_players, squire_battles, squire_battle_rounds, squire_battle_results, squire_missions, squire_player_stats, squire_faction_stats
  - Indexes for performance
  - Foreign key constraints
  - Migration script
  - **Estimated**: 2 days

- [ ] 🟠 **SQUIRE-002**: Collect and seed missions data
  - Research official missions from current seasons:
    - AoS 4th Edition (General's Handbook 2024-2025)
    - 40k 10th Edition (Leviathan season missions)
    - Warhammer: The Old World (current edition)
  - Create mission JSON files with complete data:
    - Mission name, objectives, deployment type
    - Special rules, victory conditions
    - Points categories, game types
    - Source URLs for verification
  - Verify accuracy against official sources
  - Create game_systems seed data
  - Python seeding script for missions
  - Mission data validation (schema validation)
  - Documentation for adding new systems/missions
  - **Estimated**: 4 days

- [ ] 🟠 **SQUIRE-002A**: Mission update and versioning system
  - Track mission versions in database
  - Mark old missions as inactive when updated
  - Migration script for season updates
  - Admin UI for mission management (Phase 3)
  - Changelog for mission updates
  - Process documentation:
    - How to update missions for new season
    - How to add new game system
    - How to verify mission accuracy
  - **Estimated**: 2 daysWorld (current edition)
  - Create mission JSON files with complete data:
    - Mission name, objectives, deployment type
    - Special rules, victory conditions
    - Points categories, game types
    - Source URLs for verification
  - Verify accuracy against official sources
  - Create game_systems seed data
  - Python seeding script for missions
  - Mission data validation (schema validation)
  - Documentation for adding new systems/missions
  - **Estimated**: 4 days

- [ ] 🟠 **SQUIRE-003**: Setup Squire backend module structure
  - `squire/` directory with FastAPI app
  - `squire/main.py` - FastAPI routes
  - `squire/database.py` - Database operations
  - `squire/models.py` - Pydantic models
  - `squire/missions.py` - Mission logic
  - `squire/game_systems.py` - Game system management
  - Dockerfile for Squire service
  - **Estimated**: 1 day

- [ ] 🟠 **SQUIRE-004**: Implement battle creation API
  - `POST /api/squire/battles/create`
  - Generate battle ID (similar to Herald)
  - Validate game_system_id against game_systems table
  - Validate points value
  - Return battle URL
  - Rate limiting (10 battles/hour per IP)
  - **Estimated**: 1 day

- [ ] 🟠 **SQUIRE-005**: Implement player registration API
  - `POST /api/squire/battles/{id}/register-player`
  - Create player with claim code
  - Link player to battle (player_a or player_b)
  - Validation (both slots filled)
  - **Estimated**: 1 day

- [ ] 🟠 **SQUIRE-006**: Implement battle flow APIs
  - `POST /api/squire/battles/{id}/start` - Start battle timer
  - `POST /api/squire/battles/{id}/round` - Submit round scores
  - `GET /api/squire/battles/{id}` - Get battle details
  - `GET /api/squire/battles/{id}/status` - Check status
  - **Estimated**: 2 days

- [ ] 🟠 **SQUIRE-007**: Implement battle completion API
  - `POST /api/squire/battles/{id}/complete` - Submit final scores
  - `POST /api/squire/battles/{id}/confirm` - Confirm scores
  - Dispute detection (score mismatch)
  - Calculate result (win/loss/draw)
  - Update player stats
  - **Estimated**: 2 days

### Frontend Core

- [ ] 🟠 **SQUIRE-008**: Create Squire frontend structure
  - `frontend/public/modules/squire/` directory
  - `battle-create.js` - Battle creation form
  - `battle-track.js` - Battle tracking UI
  - `battle-complete.js` - Final score submission
  - Routing updates in main.js
  - **Estimated**: 1 day

- [ ] 🟠 **SQUIRE-009**: Build battle creation UI
  - Game system selector (AoS / 40k)
  - Points value input
  - Optional Herald exchange link
  - Create battle button
  - Display battle URL and player links
  - **Estimated**: 2 days

- [ ] 🟠 **SQUIRE-010**: Build player registration UI
  - Player name input
  - Faction dropdown (system-specific)
  - Optional list notes textarea
  - Register button
  - Waiting indicator (until both players registered)
  - **Estimated**: 2 days

- [ ] 🟠 **SQUIRE-011**: Build battle tracking UI
  - Round-by-round score entry
  - Current scores display
  - Battle timer
  - Add round button
  - Notes per round
  - Real-time updates (polling)
  - **Estimated**: 3 days

- [ ] 🟠 **SQUIRE-012**: Build final score submission UI
  - Total VP entry (both players)
  - Confirm scores workflow
  - Discrepancy warning
  - Final result display
  - Link to battle summary
  - **Estimated**: 2 days

---

## Sprint 2: Squire Phase 2 - Mission Randomizer (Week 3)

### Backend

- [ ] 🟠 **SQUIRE-013**: Mission randomization API
  - `GET /api/squire/game-systems` - List available game systems
  - `GET /api/squire/missions?system_id={id}&points={value}` - List missions
  - `GET /api/squire/missions/random?system_id={id}&points={value}` - Random mission
  - Filter by game system, points, and active status
  - Return mission details (objectives, deployment, rules, source)
  - Track mission version used in battle
  - **Estimated**: 1.5 days

- [ ] 🟠 **SQUIRE-014**: Link mission to battle
  - Update battle creation to accept optional mission_id
  - Store mission_id in squire_battles table
  - Include mission details in battle response
  - **Estimated**: 0.5 days

### Frontend

- [ ] 🟠 **SQUIRE-015**: Mission randomizer UI
  - `/squire/missions` page
  - Game system dropdown (fetch from API)
    - Age of Sigmar (4th Edition)
    - Warhammer 40,000 (10th Edition)
    - Warhammer: The Old World
  - Points value selector (system-dependent options)
  - "Roll Mission" button with animation
  - Mission card display (objectives, deployment, special rules)
  - Display source URL for verification
  - Shareable mission URL
  - "Start Battle with This Mission" button
  - **Estimated**: 2.5 days

- [ ] 🟠 **SQUIRE-016**: Mission display in battle view
  - Show linked mission in battle tracking UI
  - Mission objectives reference
  - Collapsible mission details
  - **Estimated**: 1 day

### Data

- [ ] 🟠 **SQUIRE-017**: AoS 4th Edition missions data
  - Research General's Handbook 2024-2025
  - Compile complete mission list
  - Create JSON file with mission details:
    - Objectives, deployment maps, special rules
    - Points categories (1000, 2000, 3000)
    - Battle tactics, grand strategies
  - Include source URLs
  - Verify against official publications
  - **Estimated**: 2 days

- [ ] 🟠 **SQUIRE-018**: 40k 10th Edition missions data
  - Research Leviathan season missions
  - Compile complete mission list
  - Create JSON file with mission details:
    - Primary objectives, secondary objectives
    - Deployment maps, special rules
    - Game types (Combat Patrol, Incursion, Strike Force, Onslaught)
  - Include source URLs
  - Verify against official publications
  - **Estimated**: 2 days

- [ ] 🟠 **SQUIRE-018A**: Old World missions data
  - Research Warhammer: The Old World rulebook
  - Compile complete mission list
  - Create JSON file with mission details:
    - Objectives, deployment maps, special rules
    - Points categories (1000, 2000, 3000)
  - Include source URLs
  - Verify against official publications
  - **Estimated**: 2 days

---

## Sprint 3: Squire Phase 2 - Player Stats (Weeks 4-5)

### Backend

- [ ] 🟠 **SQUIRE-019**: Player profile API
  - `GET /api/squire/players/{claim_code}` - Get player profile
  - Return player info and basic stats
  - Generate claim code on player creation
  - **Estimated**: 1 day

- [ ] 🟠 **SQUIRE-020**: Player statistics calculation
  - Calculate stats after each battle completion
  - Total games, wins, losses, draws
  - Total VP scored and conceded
  - Factions played (JSON array)
  - Update squire_player_stats table
  - **Estimated**: 2 days

- [ ] 🟠 **SQUIRE-021**: Battle history API
  - `GET /api/squire/players/{claim_code}/battles` - Get battle history
  - Pagination support
  - Filter by date range, game system, faction, result
  - Sort by date, VP difference
  - **Estimated**: 2 days

- [ ] 🟠 **SQUIRE-022**: Player stats API
  - `GET /api/squire/players/{claim_code}/stats` - Detailed statistics
  - Win rate calculations
  - Average VP scored/conceded
  - Faction breakdown
  - Best/worst matchups
  - **Estimated**: 2 days

- [ ] 🟠 **SQUIRE-023**: Matchup matrix API
  - `GET /api/squire/players/{claim_code}/matchups` - Matchup matrix
  - Your factions vs opponent factions
  - Win rate per matchup
  - Sample size
  - Average VP differential
  - **Estimated**: 2 days

### Frontend

- [ ] 🟠 **SQUIRE-024**: Player profile page
  - `/squire/player/{claim_code}` route
  - Display player name and stats
  - Total games, W/L/D record
  - Win rate percentage
  - Factions played pie chart
  - Average VP scored
  - **Estimated**: 2 days

- [ ] 🟠 **SQUIRE-025**: Battle history view
  - List of battles with filters
  - Date range picker
  - Filter by system, faction, result
  - Sort controls
  - Battle cards with key info
  - Link to full battle details
  - **Estimated**: 2 days

- [ ] 🟠 **SQUIRE-026**: Matchup matrix table
  - Grid view of your faction vs opponents
  - Color-coded win rates (green/yellow/red)
  - Click for detailed matchup stats
  - Sample size indicators
  - **Estimated**: 2 days

- [ ] 🟠 **SQUIRE-027**: Player claim system
  - Bookmark prompt on first battle
  - "Save your player URL" modal
  - QR code for mobile
  - Email link (optional, no account)
  - **Estimated**: 1 day

---

## Sprint 4: Squire Phase 2 - Analytics (Weeks 6-7)

### Backend

- [ ] 🟠 **SQUIRE-028**: Global faction statistics
  - `GET /api/squire/stats/factions?system={aos|40k}` - Faction stats
  - Calculate from squire_faction_stats table
  - Games played per faction
  - Win rates
  - Most/least played
  - **Estimated**: 2 days

- [ ] 🟠 **SQUIRE-029**: Faction matchup statistics
  - `GET /api/squire/stats/matchups?faction={name}&system={aos|40k}` - Matchup data
  - Faction vs all opponents
  - Win rates per matchup
  - Average VP differentials
  - Sample sizes
  - **Estimated**: 2 days

- [ ] 🟠 **SQUIRE-030**: Activity trends API
  - `GET /api/squire/stats/trends?period={7d|30d|90d}` - Trend data
  - Games per day/week
  - Active players count
  - Popular factions over time
  - **Estimated**: 2 days

- [ ] 🟠 **SQUIRE-031**: Leaderboard API
  - `GET /api/squire/stats/leaderboard?metric={games|wins|winrate}` - Top players
  - Top 100 players by metric
  - Pagination
  - Minimum game threshold
  - **Estimated**: 1 day

- [ ] 🟠 **SQUIRE-032**: Statistics cache job
  - Background job to update faction stats
  - Scheduled daily
  - Update squire_faction_stats table
  - Recalculate global metrics
  - **Estimated**: 2 days

### Frontend

- [ ] 🟠 **SQUIRE-033**: Analytics dashboard
  - `/squire/stats` route
  - Overview cards (total games, players, factions)
  - Activity chart (games over time)
  - Most played factions (bar chart)
  - Recent battles feed
  - **Estimated**: 3 days

- [ ] 🟠 **SQUIRE-034**: Faction statistics page
  - `/squire/stats/factions` route
  - Table of all factions
  - Sortable columns (games, win rate, avg VP)
  - Filter by game system
  - Click faction for detailed view
  - **Estimated**: 2 days

- [ ] 🟠 **SQUIRE-035**: Matchup matrix tool
  - `/squire/stats/matchups` route
  - Select your faction
  - Display matchup matrix
  - Color-coded cells
  - Tooltips with detailed stats
  - Export to CSV/image
  - **Estimated**: 3 days

- [ ] 🟠 **SQUIRE-036**: Charts and visualizations
  - Integrate Chart.js via CDN
  - Pie charts for faction distribution
  - Line charts for trends
  - Bar charts for comparisons
  - Responsive design
  - **Estimated**: 2 days

---

## Quality Assurance Requirements

**MANDATORY FOR ALL SQUIRE TASKS**

### Test Coverage Standards

- ✅ **100% Unit Test Coverage** - No exceptions
  - Every function must have unit tests
  - All branches and edge cases covered
  - Tests written alongside implementation (TDD encouraged)
  - Coverage report generated: `pytest --cov=squire --cov-report=html`

- ✅ **100% Truthfulness - No Mocking**
  - Integration tests use real PostgreSQL (Docker test containers)
  - API tests call actual endpoints (TestClient in FastAPI)
  - Database transactions rolled back after tests
  - Use fixtures and factories, not mocks
  - Only mock external services (email, third-party APIs)

### Testing Requirements Per Task

Each task must include:

1. **Unit Tests** (`tests/unit/squire/`)
   - Test individual functions in isolation
   - Test data validation (Pydantic models)
   - Test business logic (calculations, rules)
   - Test error handling

2. **Integration Tests** (`tests/integration/squire/`)
   - Test database operations with real DB
   - Test API endpoints end-to-end
   - Test multi-step workflows
   - Test concurrent operations

3. **Test Data** (`tests/fixtures/squire/`)
   - Fixture factories for test data generation
   - Sample mission data
   - Sample player/battle data
   - Reusable across tests

### CI/CD Pipeline Requirements

- All tests run on every commit
- PR merge blocked if:
  - Any test fails
  - Coverage drops below 100%
  - Linting errors exist
- Test execution time target: <5 minutes

### Example Test Structure

```python
# tests/unit/squire/test_missions.py
def test_random_mission_selection():
    """Test mission randomizer returns valid mission"""
    # Real database query, no mocks
    mission = get_random_mission(game_system_id="aos", points=2000)
    assert mission is not None
    assert mission.game_system_id == "aos"
    assert mission.is_active is True

# tests/integration/squire/test_battle_flow.py
def test_full_battle_workflow(test_db, test_client):
    """Test complete battle creation to completion flow"""
    # Uses real test database container
    # No mocks - actual API calls
    battle = test_client.post("/api/squire/battles/create", json={...})
    assert battle.status_code == 200
    # ... continue full workflow
```

---

## Sprint 5: Squire Phase 2 - Polish & Testing (Week 8)

### Testing

- [ ] 🔴 **SQUIRE-037**: Backend unit tests (100% coverage)
  - Test battle creation logic (all edge cases)
  - Test score validation (discrepancy detection)
  - Test statistics calculations (VP averages, win rates)
  - Test mission randomization (distribution, filtering)
  - Test game system validation
  - Test all database operations
  - NO MOCKING - use test database containers
  - Target: 100% coverage (enforced by CI)
  - **Estimated**: 4 days

- [ ] 🔴 **SQUIRE-038**: Integration tests (full workflows)
  - Full battle flow (create → register → track → complete)
  - Player stats updates (verify calculations)
  - Mission randomizer flow (link to battle)
  - Multi-system support (all three systems)
  - Concurrent battles (race conditions)
  - API rate limiting (verify enforcement)
  - Database constraints (foreign keys, uniqueness)
  - Real PostgreSQL test container
  - **Estimated**: 3 days

- [ ] 🔴 **SQUIRE-038A**: Test data fixtures and factories
  - Battle factory (generate test battles)
  - Player factory (generate test players)
  - Mission factory (generate test missions)
  - Score entry factory (round data)
  - Reusable across all tests
  - Randomized but deterministic (seeded)
  - **Estimated**: 2 daysests
  - Randomized but deterministic (seeded)
  - **Estimated**: 2 days

- [ ] 🔴 **SQUIRE-038B**: Test infrastructure setup
  - Docker test containers (PostgreSQL)
  - Test database auto-creation and teardown
  - Pytest configuration and plugins
  - Coverage reporting setup
  - CI integration (GitHub Actions)
  - Pre-commit hooks for tests
  - **Estimated**: 2 days

- [ ] 🟠 **SQUIRE-039**: Frontend testing
  - Manual testing on Chrome, Firefox, Safari
  - Mobile responsive testing
  - Cross-browser compatibility
  - Accessibility testing (WCAG)
  - **Estimated**: 2 days

### Polish

- [ ] 🟡 **SQUIRE-040**: UI/UX improvements
  - Loading states for API calls
  - Error handling and messages
  - Success animations
  - Form validation feedback
  - **Estimated**: 2 days

- [ ] 🟡 **SQUIRE-041**: Mobile optimization
  - Touch-friendly controls
  - Responsive tables
  - Mobile-first score entry
  - Progressive Web App features
  - **Estimated**: 2 days

- [ ] 🟡 **SQUIRE-042**: Performance optimization
  - Database query optimization
  - API response caching
  - Frontend bundle optimization
  - Lazy loading for charts
  - **Estimated**: 2 days

### Documentation

- [ ] 🟠 **SQUIRE-043**: API documentation
  - OpenAPI/Swagger docs
  - Example requests/responses
  - Authentication notes (for Phase 3)
  - Rate limiting info
  - **Estimated**: 1 day

- [ ] 🟠 **SQUIRE-044**: User guide
  - How to create a battle
  - How to track scores
  - How to view stats
  - FAQ section
  - Screenshots/GIFs
  - **Estimated**: 2 days

- [ ] 🟠 **SQUIRE-045**: Developer documentation
  - Setup instructions
  - Database schema docs
  - Architecture overview
  - Contributing guide
  - **Estimated**: 1 day

---

## Matchup/Herald Enhancements Backlog

### High Priority

- [ ] 🟠 **MATCHUP-001**: Faction extraction and tracking
  - Parse army lists to extract faction information
  - Store faction in matchups table (player1_faction, player2_faction)
  - Display factions on matchup view
  - Display all factions used by user on their profile
  - Support multiple game systems (AoS, 40k, TOW)
  - **Dependencies**: Faction parsing logic, database migration
  - **Estimated**: 3 days

- [ ] 🟠 **MATCHUP-002**: Battle tactics extraction and storage
  - Parse army lists to extract battle tactics (2 per list)
  - Create battle_tactics table (matchup_id, player, tactic_name)
  - Display tactics on matchup view
  - Show tactics alongside army lists when revealed
  - **Dependencies**: Tactics parsing logic, database migration
  - **Estimated**: 2 days

- [ ] 🟠 **MATCHUP-003**: Monthly statistics page
  - Stats page showing matchups per month
  - Breakdown by faction
  - Total matchups counter
  - Faction popularity chart
  - Filter by date range
  - **Dependencies**: MATCHUP-001, MATCHUP-002
  - **Estimated**: 3 days

- [ ] 🟠 **MATCHUP-004**: Battle status tracking system
  - Add status field to matchups: Planned → Battle Completed → Results Reported
  - "Planned" status when matchup is created and revealed
  - "Battle Completed" when result is entered by either player
  - "Results Reported" when both players confirm result
  - Optional battle date field (defaults to result entry time)
  - Result submission UI with VP scores
  - Dispute resolution for mismatched results
  - **Dependencies**: Database migration, new routes, UI updates
  - **Estimated**: 4 days

- [ ] 🟠 **MATCHUP-005**: Tactics statistics integration
  - Add tactics column to stats page
  - Show most popular tactics by month
  - Tactics usage frequency chart
  - Filter stats by faction and tactics
  - **Dependencies**: MATCHUP-002, MATCHUP-003
  - **Estimated**: 2 days

- [ ] 🟠 **HERALD-001**: Mission randomizer integration
  - Add "Roll Mission" button to Herald exchange
  - Link randomized mission to exchange
  - Display mission in exchange view
  - **Estimated**: 2 days

- [ ] 🟠 **HERALD-002**: PDF export
  - Generate PDF of exchange
  - Include both lists, hashes, timestamps
  - Downloadable from exchange page
  - Library: ReportLab or WeasyPrint
  - **Estimated**: 3 days

- [ ] 🟠 **HERALD-003**: Email notifications (pre-auth)
  - Optional email input on exchange creation
  - Send notification when opponent responds
  - No account required
  - Include exchange URL
  - **Estimated**: 2 days

### Medium Priority

- [ ] 🟡 **HERALD-004**: QR code generation
  - Generate QR code for exchange URL
  - Display on creation confirmation
  - Scannable on mobile
  - **Estimated**: 1 day

- [ ] 🟡 **HERALD-005**: List templates
  - Pre-fill common list formats
  - AoS list template
  - 40k list template
  - Custom template storage
  - **Estimated**: 2 days

- [ ] 🟡 **HERALD-006**: Character counter
  - Real-time character count
  - Warn at 45,000 chars (90% of limit)
  - Format indicator (plain text vs formatted)
  - **Estimated**: 0.5 days

- [ ] 🟡 **HERALD-007**: Dark/light theme toggle
  - Theme switcher in header
  - Persist preference (localStorage)
  - Light theme design
  - Smooth transition
  - **Estimated**: 2 days

---

## Infrastructure Backlog

### High Priority

- [ ] 🟠 **ADMIN-001**: Admin panel for matchup management
  - Admin dashboard with matchup list view
  - Filter matchups by: status, date range, player ID, usernames, anonymous/registered
  - Search by: matchup name, player username, army list content
  - Sort by: created date, expiration, revealed status
  - View full matchup details (both lists, players, timestamps)
  - Edit matchup player assignment (player1_id, player2_id)
  - Use case: Assign anonymous matchups to user accounts retroactively
  - Admin role-based access control
  - Audit log for admin actions
  - **Dependencies**: User authentication, admin role system
  - **Estimated**: 5 days

- [ ] 🟠 **INFRA-001**: CI/CD pipeline
  - GitHub Actions workflow
  - Automated testing on PR
  - Automated Docker builds
  - Deploy to staging on merge
  - **Estimated**: 3 days

- [ ] 🟠 **INFRA-002**: Monitoring setup
  - Prometheus metrics collection
  - Grafana dashboards
  - Key metrics: response time, error rate, active users
  - Alerts via email/Discord
  - **Estimated**: 3 days

- [ ] 🟠 **INFRA-003**: Backup automation
  - Daily database backups
  - Backup to cloud storage (S3/B2)
  - 30-day retention
  - Restore testing
  - **Estimated**: 2 days

### Medium Priority

- [ ] 🟡 **INFRA-004**: CDN setup
  - CloudFlare free tier
  - Static asset caching
  - DDoS protection
  - Analytics integration
  - **Estimated**: 1 day

- [ ] 🟡 **INFRA-005**: Logging improvements
  - Structured logging (JSON)
  - Log aggregation (Loki or ELK)
  - Log search interface
  - Error tracking (Sentry)
  - **Estimated**: 2 days

- [ ] 🟡 **INFRA-006**: Load testing
  - k6 or Locust setup
  - Test battle creation load
  - Test concurrent battles
  - Identify bottlenecks
  - **Estimated**: 2 days

---

## Technical Debt

- [ ] 🟡 **TECH-001**: Database migration system
  - Alembic or similar migration tool
  - Version-controlled schema changes
  - Rollback capability
  - **Estimated**: 2 days

- [ ] 🟡 **TECH-002**: API versioning
  - `/api/v1/` prefix for all endpoints
  - Version negotiation strategy
  - Deprecation warnings
  - **Estimated**: 1 day

- [ ] 🟡 **TECH-003**: Environment variable validation
  - Validate required env vars on startup
  - Clear error messages
  - Default value documentation
  - **Estimated**: 1 day

- [ ] 🟡 **TECH-004**: Error handling standardization
  - Consistent error response format
  - Error codes for client handling
  - User-friendly error messages
  - **Estimated**: 2 days

- [ ] 🟢 **TECH-005**: Code linting and formatting
  - Black for Python
  - isort for imports
  - Prettier for JavaScript
  - Pre-commit hooks
  - **Estimated**: 1 day

---

## Bugs

### Critical

*(None currently)*

### High

*(None currently)*

### Medium

*(None currently)*

### Low

*(None currently)*

---

## Feature Requests from Community

*(Track community requests here)*

---

## Notes

- Tasks are estimated in days (8-hour workdays)
- Priority can change based on community feedback
- Dependencies are noted in task descriptions
- Update this file as tasks are completed
- Use GitHub issues to track detailed discussions

---

## Contributing

Want to work on a task?

1. Comment on the related GitHub issue (or create one referencing the task ID)
2. Assign yourself to the issue
3. Create a feature branch: `git checkout -b feature/SQUIRE-001`
4. Submit a PR when ready
5. Update this backlog to mark task as complete

See [CONTRIBUTING.md](CONTRIBUTING.md) for full guidelines.

---

**Last Review**: January 15, 2026  
**Recent Additions**: MATCHUP-001 through MATCHUP-005 (Faction tracking, battle status, tactics, statistics)
