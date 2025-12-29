# Knowledge Base Index - Squig League

Central documentation hub for the Squig League platform.

---

## Documentation Structure

```
docs/
├── INDEX.md (this file)              # Central navigation hub
├── README.md                         # Project overview and quick start
├── ARCHITECTURE.md                   # System architecture and design decisions
├── API.md                            # API endpoint documentation
├── DATABASE.md                       # Database schema and migrations
├── DEPLOYMENT.md                     # Deployment and infrastructure
├── CONTRIBUTING.md                   # Contribution guidelines
├── CHANGELOG.md                      # Version history and changes
│
├── testing/
│   ├── TESTING_POLICY.md            # Mandatory testing requirements (100% coverage)
│   ├── TESTING_GUIDE.md             # How to write and run tests
│   ├── FIXTURES.md                  # Test fixture documentation
│   └── CI_CD.md                     # Continuous integration setup
│
├── modules/
│   ├── HERALD.md                    # Herald module (blind list exchange)
│   ├── SQUIRE.md                    # Squire module (battle tracking) - FUTURE
│   ├── SCRIBE.md                    # Scribe module (record keeping) - FUTURE
│   └── SENESCHAL.md                 # Seneschal module (tournament management) - FUTURE
│
├── development/
│   ├── SETUP.md                     # Local development environment setup
│   ├── WORKFLOWS.md                 # Git workflows and branching strategy
│   ├── CODE_STYLE.md                # Code style and conventions
│   └── DEBUGGING.md                 # Debugging tips and tools
│
├── operations/
│   ├── SSL_SETUP.md                 # SSL certificate configuration
│   ├── MONITORING.md                # Application monitoring - FUTURE
│   └── BACKUP_RESTORE.md            # Database backup procedures - FUTURE
│
└── guides/
    ├── MISSION_DATA_GUIDE.md        # Collecting and maintaining mission data
    ├── USER_GUIDE.md                # End-user documentation - FUTURE
    └── ADMIN_GUIDE.md               # Administrator documentation - FUTURE
```

---

## Quick Navigation

### For New Contributors

**Start Here:**
1. [README.md](../README.md) - Project overview
2. [CONTRIBUTING.md](../CONTRIBUTING.md) - How to contribute
3. [development/SETUP.md](development/SETUP.md) - Set up development environment
4. [TESTING_POLICY.md](TESTING_POLICY.md) - Testing requirements (mandatory reading)
5. [ARCHITECTURE.md](ARCHITECTURE.md) - Understand system design

**Then Read:**
- [development/CODE_STYLE.md](development/CODE_STYLE.md) - Code conventions
- [development/WORKFLOWS.md](development/WORKFLOWS.md) - Git workflow
- [TESTING_GUIDE.md](TESTING_GUIDE.md) - How to write tests

### For Developers

**Backend Development:**
- [API.md](API.md) - API endpoint specifications
- [DATABASE.md](DATABASE.md) - Database schema and queries
- [modules/HERALD.md](modules/HERALD.md) - Herald module internals
- [TESTING_GUIDE.md](TESTING_GUIDE.md) - Writing tests

**Frontend Development:**
- [ARCHITECTURE.md](ARCHITECTURE.md) - Alpine.js patterns
- [development/CODE_STYLE.md](development/CODE_STYLE.md) - Frontend conventions
- [API.md](API.md) - API integration

**Testing:**
- [TESTING_POLICY.md](TESTING_POLICY.md) - Testing policy (100% coverage, no mocking)
- [TESTING_GUIDE.md](TESTING_GUIDE.md) - Writing and running tests
- [testing/FIXTURES.md](testing/FIXTURES.md) - Test fixture reference
- [testing/CI_CD.md](testing/CI_CD.md) - CI/CD pipeline

### For DevOps

**Deployment:**
- [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment procedures
- [operations/SSL_SETUP.md](operations/SSL_SETUP.md) - SSL configuration
- [operations/MONITORING.md](operations/MONITORING.md) - Monitoring setup (future)
- [operations/BACKUP_RESTORE.md](operations/BACKUP_RESTORE.md) - Backup procedures (future)

### For Project Managers

**Planning:**
- [ROADMAP.md](../ROADMAP.md) - Development roadmap (7 phases)
- [BACKLOG.md](../BACKLOG.md) - Task backlog (45+ tasks)
- [CHANGELOG.md](../CHANGELOG.md) - Version history

**Quality Assurance:**
- [TESTING_POLICY.md](TESTING_POLICY.md) - QA requirements
- [testing/CI_CD.md](testing/CI_CD.md) - Automated quality gates

---

## Knowledge Domains

### System Architecture

**What**: High-level system design, technology choices, patterns

**Key Documents:**
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
- [API.md](API.md) - API design patterns
- [DATABASE.md](DATABASE.md) - Database design

**Knowledge Graph:**
```
System Architecture
├── Backend (FastAPI)
│   ├── Herald Module (blind list exchange)
│   ├── Squire Module (battle tracking) - FUTURE
│   └── Rate Limiting (SlowAPI)
│
├── Frontend (Alpine.js SPA)
│   ├── No build step (CDN)
│   └── Tailwind CSS
│
├── Database (PostgreSQL)
│   ├── Herald schema
│   └── Squire schema - FUTURE
│
└── Infrastructure
    ├── Docker multi-arch
    ├── Nginx reverse proxy
    └── Hetzner VPS with SSL
```

### Testing Infrastructure

**What**: Testing frameworks, policies, practices

**Key Documents:**
- [TESTING_POLICY.md](TESTING_POLICY.md) - Mandatory testing requirements
- [TESTING_GUIDE.md](TESTING_GUIDE.md) - How to write tests
- [testing/FIXTURES.md](testing/FIXTURES.md) - Test fixtures
- [testing/CI_CD.md](testing/CI_CD.md) - CI/CD pipeline

**Requirements:**
- ✅ 100% test coverage (enforced)
- ✅ No mocking internal logic (real PostgreSQL containers)
- ✅ Transaction rollback for clean tests
- ✅ pytest + pytest-asyncio + pytest-cov
- ✅ GitHub Actions CI/CD
- ✅ Merge blocked on test failures

**Knowledge Graph:**
```
Testing Infrastructure
├── Unit Tests
│   ├── Herald (test_database.py, test_main.py, test_models.py, test_words.py)
│   └── Squire - FUTURE
│
├── Integration Tests
│   ├── Herald (test_exchange_flow.py, test_api_endpoints.py, test_rate_limiting.py)
│   └── Squire - FUTURE
│
├── Test Fixtures (conftest.py)
│   ├── test_engine (PostgreSQL connection)
│   ├── test_db (transaction rollback)
│   ├── test_client (FastAPI TestClient)
│   └── sample_data (factories)
│
└── CI/CD Pipeline
    ├── GitHub Actions
    ├── PostgreSQL service container
    ├── Coverage enforcement (100%)
    └── Merge blocking
```

### Herald Module

**What**: Blind army list exchange for Warhammer games

**Key Documents:**
- [modules/HERALD.md](modules/HERALD.md) - Herald internals
- [API.md](API.md) - API endpoints

**Features:**
- Create exchange → Generate exchange ID → Share ID
- Respond to exchange → Submit list B
- View exchange → Both lists revealed after both submitted
- Admin endpoints (stats, recent exchanges, logs)

**Knowledge Graph:**
```
Herald Module
├── API Endpoints
│   ├── POST /api/herald/exchange/create (create exchange)
│   ├── GET /api/herald/exchange/{id} (view exchange)
│   ├── POST /api/herald/exchange/{id}/respond (submit response)
│   ├── GET /api/herald/stats (admin stats)
│   └── GET /api/herald/admin/recent (admin recent exchanges)
│
├── Database Schema
│   ├── herald_exchanges (id, list_a, list_b, hash_a, hash_b, timestamps)
│   └── herald_request_log (id, exchange_id, endpoint, ip, timestamp)
│
└── Business Logic
    ├── Exchange ID generation (memorable words + hash)
    ├── List hashing (SHA256)
    ├── Rate limiting (10 creates/hour, 20 views/hour)
    └── Request logging
```

### Squire Module (Future)

**What**: Battle tracking, mission randomization, player stats

**Key Documents:**
- [ROADMAP.md](../ROADMAP.md) - Squire Phase 2 specification
- [BACKLOG.md](../BACKLOG.md) - Squire tasks (SQUIRE-001 to SQUIRE-045)
- [guides/MISSION_DATA_GUIDE.md](guides/MISSION_DATA_GUIDE.md) - Mission data collection

**Planned Features:**
- Multi-system support (AoS, 40k, Old World)
- Mission randomization (official mission data)
- Battle result tracking (self-reported by both players)
- Player stats (win/loss, faction usage, matchup history)
- Faction analytics (win rates, popularity)
- Time-period filtering (season, month, all-time)

**Knowledge Graph:**
```
Squire Module (FUTURE)
├── Game Systems
│   ├── Warhammer Age of Sigmar
│   ├── Warhammer 40,000
│   ├── Warhammer: The Old World
│   └── Future expansions (extensible)
│
├── Mission Data
│   ├── Official missions (Games Workshop publications)
│   ├── Versioning (season tracking)
│   ├── Source URLs (GW PDFs)
│   └── Validation scripts
│
├── Battle Tracking
│   ├── Battle creation (system, mission, players)
│   ├── Round tracking (turn-by-turn)
│   ├── Result submission (self-reported)
│   └── Matchup history
│
└── Analytics
    ├── Player stats (W/L, faction usage)
    ├── Faction stats (win rates, popularity)
    ├── Matchup analysis (faction vs faction)
    └── Time-period filtering
```

### Database Schema

**What**: PostgreSQL database structure

**Key Documents:**
- [DATABASE.md](DATABASE.md) - Complete schema documentation

**Herald Tables:**
- `herald_exchanges` - Exchange data (lists, hashes, timestamps)
- `herald_request_log` - API request logging

**Squire Tables (Future):**
- `squire_game_systems` - Extensible system registry
- `squire_missions` - Official mission data with versioning
- `squire_battles` - Battle records
- `squire_players` - Player profiles
- `squire_battle_rounds` - Turn-by-turn tracking
- `squire_battle_results` - Self-reported results
- `squire_player_stats` - Player statistics
- `squire_faction_stats` - Faction statistics

---

## Development Phases

### Phase 1: Herald (Complete - v0.2.1)

**Status**: ✅ Production  
**Documentation**: [modules/HERALD.md](modules/HERALD.md)

**Completed:**
- Blind list exchange
- Memorable exchange IDs
- Hash verification
- Rate limiting
- Admin endpoints
- Frontend/backend separation
- Docker deployment
- SSL configuration

**Missing:**
- ❌ Automated tests (0% coverage)
- ❌ CI/CD pipeline

### Phase 2: Squire (Planned - Q1 2026)

**Status**: 📋 Planning  
**Documentation**: [ROADMAP.md](../ROADMAP.md), [BACKLOG.md](../BACKLOG.md)

**Sprints:**
1. Testing Infrastructure (2 weeks) - CRITICAL BLOCKER
2. Multi-System Support (2 weeks)
3. Mission Randomization (2 weeks)
4. Battle Tracking (2 weeks)
5. Player Stats & Analytics (2 weeks)

**Prerequisites:**
- ✅ Testing infrastructure (100% coverage)
- ✅ Mission data collection
- ✅ Database migrations
- ✅ CI/CD pipeline

### Phase 3-7: Future Modules

**Status**: 🔮 Future  
**Documentation**: [ROADMAP.md](../ROADMAP.md)

**Modules:**
- Phase 3: Scribe (record keeping)
- Phase 4: Seneschal (tournament management)
- Phase 5: Loremaster (battle reports)
- Phase 6: Artificer (model tracking)
- Phase 7: Chronicler (campaign tracking)

---

## Development Workflows

### Setting Up Development Environment

1. **Clone repository**
   ```bash
   git clone https://github.com/ogdowski/squigleague.git
   cd squigleague
   ```

2. **Read documentation**
   - [development/SETUP.md](development/SETUP.md)
   - [TESTING_POLICY.md](TESTING_POLICY.md)

3. **Install dependencies**
   ```bash
   # Backend
   cd herald
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Test dependencies
   
   # Database
   docker-compose up -d postgres
   ```

4. **Run tests**
   ```bash
   pytest --cov=herald --cov-report=html
   ```

5. **Start development server**
   ```bash
   uvicorn main:app --reload
   ```

### Contributing Code

1. **Create feature branch**
   ```bash
   git checkout -b feature/SQUIRE-001-database-schema
   ```

2. **Write tests first (TDD)**
   - See [TESTING_GUIDE.md](TESTING_GUIDE.md)
   - Ensure 100% coverage

3. **Implement feature**
   - Follow [development/CODE_STYLE.md](development/CODE_STYLE.md)
   - Write meaningful commit messages

4. **Run tests locally**
   ```bash
   pytest --cov=herald --cov=squire --cov-report=html
   black .
   isort .
   flake8
   ```

5. **Submit PR**
   - Reference task ID (SQUIRE-001)
   - Ensure CI passes
   - Request review

### Testing Workflow

**Before every commit:**
```bash
# Run tests
pytest

# Check coverage
pytest --cov --cov-report=term

# Format code
black .
isort .

# Lint
flake8
```

**CI will check:**
- All tests pass
- Coverage = 100%
- No linting errors
- No type errors (mypy)

---

## Common Tasks

### Adding a New API Endpoint

1. Read [API.md](API.md) for patterns
2. Write integration test in `tests/integration/herald/test_api_endpoints.py`
3. Implement endpoint in `herald/main.py`
4. Write unit tests for business logic
5. Run tests: `pytest --cov`
6. Update [API.md](API.md) documentation

### Adding a Database Table

1. Read [DATABASE.md](DATABASE.md) for schema conventions
2. Create migration script (Alembic)
3. Write test fixtures in `tests/conftest.py`
4. Write database operation tests
5. Run tests: `pytest --cov`
6. Update [DATABASE.md](DATABASE.md) documentation

### Adding a New Test

1. Read [TESTING_GUIDE.md](TESTING_GUIDE.md)
2. Identify test category (unit/integration)
3. Write test in appropriate directory
4. Use existing fixtures from `conftest.py`
5. Run test: `pytest tests/path/to/test_file.py -v`
6. Verify coverage: `pytest --cov --cov-report=html`

---

## Troubleshooting

### Tests Failing

**Check:**
1. [TESTING_GUIDE.md](TESTING_GUIDE.md) - Common issues section
2. [testing/CI_CD.md](testing/CI_CD.md) - CI-specific problems
3. CI logs (GitHub Actions)
4. Coverage report (`htmlcov/index.html`)

### Database Issues

**Check:**
1. [DATABASE.md](DATABASE.md) - Schema documentation
2. [development/DEBUGGING.md](development/DEBUGGING.md) - Debug tips
3. Migration status: `alembic current`
4. Test database connection: `pytest tests/integration/ -v`

### Deployment Issues

**Check:**
1. [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment procedures
2. [operations/SSL_SETUP.md](operations/SSL_SETUP.md) - SSL configuration
3. Docker logs: `docker-compose logs -f`
4. Nginx logs: `docker-compose logs nginx`

---

## External Resources

### Documentation
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [pytest Documentation](https://docs.pytest.org/)
- [Alpine.js Documentation](https://alpinejs.dev/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Docker Documentation](https://docs.docker.com/)

### Tools
- [GitHub Repository](https://github.com/ogdowski/squigleague)
- [CI/CD Pipeline](https://github.com/ogdowski/squigleague/actions)
- [Issue Tracker](https://github.com/ogdowski/squigleague/issues)

### Community
- Slack: #squigleague
- Email: team@squigleague.com

---

## Document Maintenance

**Owner**: Documentation Team  
**Last Updated**: November 20, 2025  
**Review Schedule**: Monthly

**Update Process:**
1. Identify outdated documentation
2. Create issue with `documentation` label
3. Submit PR with updates
4. Update this index if structure changes

**Quality Standards:**
- All code examples must be tested
- All links must be valid
- All diagrams must be current
- All API docs must match implementation

---

## Quick Reference

**Starting Development:**
1. [development/SETUP.md](development/SETUP.md)
2. [CONTRIBUTING.md](../CONTRIBUTING.md)
3. [TESTING_POLICY.md](TESTING_POLICY.md)

**Writing Code:**
1. [TESTING_GUIDE.md](TESTING_GUIDE.md) - Write tests first
2. [development/CODE_STYLE.md](development/CODE_STYLE.md) - Code style
3. [API.md](API.md) - API patterns

**Deploying:**
1. [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment
2. [operations/SSL_SETUP.md](operations/SSL_SETUP.md) - SSL

**Getting Help:**
- #testing - Testing questions
- #development - Dev questions
- #devops - Deployment questions

---

**This is a living document. Keep it updated as the project evolves.**
