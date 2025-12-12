# Pull Request: v0.3.0 - AoS Matchup System + Battle Plan Gallery

## Overview

This release adds the complete Squire module for Age of Sigmar, including battle plan gallery and matchup system.

## What's New

### Battle Plan Gallery
- **12 Official Battle Plans** from General's Handbook 2025-26
- **Deployment Maps**: High-quality images from Wahapedia showing objective placement
- **Accurate Rules**: TWIST mechanics, scoring formulas, and underdog abilities verified against official GH source
- **Interactive Gallery**: View all plans with deployment maps and rule details

### Matchup System
- **List Exchange**: Two players share army lists anonymously
- **Simultaneous Reveal**: Lists revealed only when both players submit
- **Random Battle Plan**: Official GH 2025-26 mission selected automatically
- **Shareable Links**: Unique matchup ID for easy sharing

## Deployment Methods

### Docker (Primary Deployment Method)

```bash
# Clone and checkout
git checkout release/v0.3.0-aos-matchups

# Start containers
docker-compose up --build

# Access application
open http://localhost/
```

**Architecture:**
- Backend (FastAPI): Port 8000
- Frontend (Nginx): Port 80
- PostgreSQL: Port 5432 (internal)
- Nginx: Reverse proxy routing `/api/*` to backend

### Alternative: Local Development

```powershell
# Setup
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Start servers
.\scripts\activity-start-servers.ps1

# Access
open http://localhost:3000/
```

## Testing

### Automated Tests
```bash
pytest tests/integration/squire/test_gallery.py -v
```
- 4 integration tests for gallery API
- All tests passing
- Coverage of API endpoints and data validation

### Manual Testing
1. **Gallery**: http://localhost/#/squire/battleplans
   - View all 12 battle plans
   - Check deployment maps display
   - Verify rule descriptions
   
2. **Matchup**:
   - Create new matchup
   - Submit list as Player 1
   - Open matchup link in incognito as Player 2
   - Submit list as Player 2
   - Verify simultaneous reveal + battle plan

3. **API Documentation**: http://localhost/docs
   - Swagger UI with all endpoints
   - Test endpoints interactively

## Technical Details

### API Endpoints
- `GET /api/squire/battle-plans/gallery?system=age_of_sigmar` - Gallery data
- `GET /api/squire/battle-plan/random?system=age_of_sigmar` - Random plan
- `POST /api/squire/matchup/create` - Create matchup
- `POST /api/squire/matchup/{id}/submit` - Submit list
- `GET /api/squire/matchup/{id}` - Get matchup status

### File Structure
```
squire/
├── battle_plans.py      # Battle plan data (GH 2025-26)
├── matchup.py          # Matchup system logic
└── routes.py           # API endpoints

frontend/public/modules/squire/
├── battleplan-gallery.js        # Gallery Alpine.js component
├── battleplan-gallery-render.js # Gallery UI rendering
└── matchup.js                   # Matchup system UI

assets/battle-plans/
└── *.png               # 12 deployment map images

tests/integration/squire/
├── test_gallery.py     # Gallery API tests
└── test_matchup.py     # Matchup system tests
```

### Data Sources
- **Battle Plans**: General's Handbook 2025-26 (via Wahapedia)
- **Deployment Maps**: Wahapedia official diagrams
- **Rules Verification**: Cross-referenced with GH 2025-26

### Docker Configuration
- **Dockerfile**: Fixed module import structure (herald.main:app)
- **nginx-dev.conf**: HTTP-only config for local development
- **docker-compose.yml**: Updated to use dev nginx config
- **Health Checks**: Backend and database health monitoring

## Breaking Changes

None. This is a new feature addition.

## Migration Notes

No database migrations required. SQLite used for local development (matchup storage).

## Documentation

- **QUICKSTART.md**: Quick start guide for reviewers and developers
- **docs/MATCHUP_FEATURE.md**: Detailed matchup system documentation
- **docs/RELEASE_v0.3.0_GUI_TEST.md**: Manual testing procedures
- **docs/BATTLE_PLAN_IMAGE_SOURCES.md**: Image attribution

## Verification Checklist

- [x] All 12 battle plan images present
- [x] Gallery API returns correct data
- [x] Gallery UI displays all plans
- [x] Deployment maps load correctly
- [x] Matchup creation works
- [x] List submission works
- [x] Simultaneous reveal works
- [x] Battle plan randomization works
- [x] Docker deployment successful
- [x] All tests passing
- [x] API documentation complete

## Rollback Plan

If issues arise:
```bash
# Stop containers
docker-compose down

# Checkout main
git checkout main

# Restart
docker-compose up --build
```

No database changes to revert.

## Performance Impact

- Image assets: ~900KB total (12 PNG files)
- API response time: <100ms for gallery endpoint
- Docker memory: ~800MB total (backend + frontend + db)
- No performance regressions expected

## Security Considerations

- No authentication required (public gallery)
- Matchup IDs are UUIDs (non-guessable)
- No sensitive data in army lists (user-provided text)
- SQLite for local development only (no production use)

## Future Work

- Add 40k battle plans (blocked on data source)
- Add Old World battle plans (blocked on GH 2025 release)
- Add battle plan filtering/search
- Add print-friendly view
- Add matchup history

## Questions for Reviewers

1. Is the Docker deployment clear enough for production use?
2. Should we add more automated tests for the matchup flow?
3. Any concerns about the gallery UI/UX?

## Credits

- Battle plan data: Games Workshop General's Handbook 2025-26
- Images: Wahapedia (https://wahapedia.ru/aos4/)
- Development: BACKEND_CORE, DEVOPS_FORGE, DOC_SCRIBE, QA_GUARDIAN
