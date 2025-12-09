# SquigLeague Documentation

## Overview
SquigLeague is a tournament management platform for Warhammer gaming communities, consisting of two main modules:
- **Herald**: Tournament administration and matchmaking
- **Squire**: Player utilities and tools

---

## Documentation Index

### Project Management
- [User Stories](user-stories.md) - All user stories (implemented and planned)
- [RAID Log](raid-log.md) - Risks, Assumptions, Issues, Dependencies
- [Design Decisions](design-decisions.md) - Architectural and design decision records

### Technical Documentation
- [API Documentation](http://localhost:8000/docs) - FastAPI auto-generated docs (when running)
- [Development Setup](#development-setup) - Getting started guide
- [Architecture](#architecture) - System architecture overview

---

## Development Setup

### Prerequisites
- Docker Desktop
- Git
- PowerShell (Windows) or Bash (Linux/Mac)

### Quick Start
```bash
# Clone repository
git clone https://github.com/ogdowski/squigleague.git
cd squigleague

# Create environment file
cp .env.local.example .env.local

# Build and start services
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build -d

# Access the application
# Frontend: http://localhost/
# Backend API: http://localhost:8000/docs
# Squire Tools: http://localhost/squire/battle-plan
```

### Running Tests
```powershell
# UAT test suite
.\run-uat-tests.ps1

# Full deployment + UAT tests
.\scripts\activity-uat.ps1

# Validate all systems
.\scripts\validate-all.ps1
```

---

## Architecture

### Services
1. **squig-postgres** - PostgreSQL 16 database
2. **squig** - FastAPI backend (Python 3.11)
3. **squig-frontend** - Alpine.js SPA
4. **squig-nginx** - Reverse proxy and routing

### Request Flow
```
User → nginx:80 → Frontend (Alpine.js SPA)
                → Backend API (FastAPI) :8000
                           → PostgreSQL :5432
```

### Module Structure
```
/herald     - Tournament administration (planned)
/squire     - Player utilities (battle plans implemented)
```

---

## Current Feature Status

### Implemented Features
- ✅ Battle Plan Randomizer (Squire)
  - Age of Sigmar (12 missions, GH 2025-2026)
  - Warhammer 40k (placeholder)
  - The Old World (placeholder)
  - UI: http://localhost/squire/battle-plan
  - API: GET /api/squire/battle-plan/random?system=age_of_sigmar

### Planned Features
See [User Stories](user-stories.md) for complete list:
- Herald tournament management
- Battle plan integration with matchups
- User authentication
- List submission and validation
- Automated pairing generation

---

## Design Principles

### No Emoji Policy
All UI elements must use text labels, SVG icons, or icon fonts. Emoji characters are prohibited in user-facing content. See [DD-001](design-decisions.md#dd-001-no-emoji-icons-in-ui).

### User Story Driven Development
All new features must have defined user stories with acceptance criteria before implementation begins. See [User Stories](user-stories.md).

---

## Contributing

### Adding New Features
1. Create user story in [user-stories.md](user-stories.md)
2. Get story approved by product owner
3. Update RAID log if new risks/dependencies identified
4. Implement feature with tests
5. Document any design decisions in [design-decisions.md](design-decisions.md)
6. Update user story status to "Implemented"

### Testing Requirements
- All API endpoints must have UAT tests
- All UI components must have manual test checklist
- No features merged without passing tests

---

## Support & Contact

- Repository: https://github.com/ogdowski/squigleague
- Issues: https://github.com/ogdowski/squigleague/issues

---

## License
[To be determined]
