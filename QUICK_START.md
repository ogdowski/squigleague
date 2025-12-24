# Quick Start Guide - App Rewrite Implementation

> **Branch:** `feature/app-rewrite`  
> **Current Status:** Planning Complete  
> **Next Phase:** Backend Foundation (Phase 1)

---

## What Has Been Done

✅ Analyzed current codebase structure  
✅ Created `feature/app-rewrite` branch  
✅ Documented comprehensive rewrite plan ([APP_REWRITE_PLAN.md](APP_REWRITE_PLAN.md))  
✅ Created detailed migration strategy ([MIGRATION_PLAN.md](MIGRATION_PLAN.md))  
✅ Committed planning documents  

---

## What to Do Next

### Immediate Next Steps (Phase 1.1 - Backend Structure)

#### Step 1: Create Backend Directory Structure

```powershell
# Run from: c:\repos\SquigLeague\squigleague\

# Create backend directory structure
New-Item -Path "backend\app\core" -ItemType Directory -Force
New-Item -Path "backend\app\users" -ItemType Directory -Force
New-Item -Path "backend\app\matchup" -ItemType Directory -Force
New-Item -Path "backend\app\elo" -ItemType Directory -Force
New-Item -Path "backend\app\leagues" -ItemType Directory -Force
New-Item -Path "backend\alembic" -ItemType Directory -Force

# Create __init__.py files
New-Item -Path "backend\app\__init__.py" -ItemType File
New-Item -Path "backend\app\core\__init__.py" -ItemType File
New-Item -Path "backend\app\users\__init__.py" -ItemType File
New-Item -Path "backend\app\matchup\__init__.py" -ItemType File
New-Item -Path "backend\app\elo\__init__.py" -ItemType File
New-Item -Path "backend\app\leagues\__init__.py" -ItemType File
```

#### Step 2: Create Core Backend Files

1. **backend/app/config.py** - Application settings
2. **backend/app/db.py** - Database session management
3. **backend/app/main.py** - FastAPI application entry point
4. **backend/app/core/security.py** - Password hashing, JWT helpers
5. **backend/app/core/deps.py** - Dependency injection functions
6. **backend/requirements.txt** - Python dependencies

#### Step 3: Set Up Database Connection

- Copy current `squire/database.py` Session logic → `backend/app/db.py`
- Update `DATABASE_URL` in `.env`
- Test database connection

#### Step 4: Migrate Alembic

```powershell
# Copy alembic configuration
Copy-Item -Path "alembic" -Destination "backend\alembic" -Recurse
Copy-Item -Path "alembic.ini" -Destination "backend\alembic.ini"

# Update alembic.ini to point to new app structure
```

---

## Phase 1 Checklist (Week 1)

### Backend Foundation
- [ ] Create directory structure
- [ ] Create `backend/app/config.py` with Pydantic settings
- [ ] Create `backend/app/db.py` with SQLModel session
- [ ] Create `backend/app/main.py` with FastAPI app
- [ ] Create `backend/app/core/security.py` (password hashing)
- [ ] Create `backend/app/core/deps.py` (get_session)
- [ ] Create `backend/requirements.txt`
- [ ] Create `backend/Dockerfile`
- [ ] Update `docker-compose.yml` for new backend path
- [ ] Test: Backend starts successfully
- [ ] Test: Database connection works
- [ ] Test: Alembic migrations work

### Environment Setup
- [ ] Create `backend/.env.example` with OAuth placeholders
- [ ] Update main `.env` with new structure
- [ ] Document OAuth setup process

---

## Phase 2 Checklist (Week 1-2)

### Users Module + OAuth
- [ ] Create `backend/app/users/models.py` (SQLModel User)
- [ ] Create `backend/app/users/schemas.py` (Pydantic schemas)
- [ ] Create `backend/app/users/auth.py` (FastAPI Users setup)
- [ ] Configure Google OAuth client
- [ ] Configure Discord OAuth client
- [ ] Create `backend/app/users/routes.py` (auth endpoints)
- [ ] Add user router to main.py
- [ ] Create Alembic migration for users table
- [ ] Test: Google OAuth login works
- [ ] Test: Discord OAuth login works
- [ ] Test: User role assignment works
- [ ] Update `backend/app/core/deps.py` (get_current_user)
- [ ] Create `backend/app/core/permissions.py` (require_role)

---

## Code Reuse Checklist

### Files to Migrate (in order)

#### Phase 1 (Foundation)
- [x] None - all new code

#### Phase 2 (Users)
- [ ] `squire/database.py` (User model) → `backend/app/users/models.py`
- [ ] `squire/auth.py` (password hashing) → `backend/app/core/security.py`

#### Phase 3 (Matchup)
- [ ] `squire/matchup.py` → `backend/app/matchup/service.py`
- [ ] `squire/battle_plans.py` → `backend/app/matchup/battle_plans.py`
- [ ] `squire/database.py` (Matchup model) → `backend/app/matchup/models.py`

#### Phase 4 (ELO)
- [ ] None - new module

#### Phase 5 (Leagues)
- [ ] None - new module

---

## Testing Strategy

### After Phase 1
```powershell
cd backend
pytest tests/test_config.py
pytest tests/test_db.py
```

### After Phase 2
```powershell
pytest tests/test_users.py
# Manual: Test OAuth flow in browser
```

### After Phase 3
```powershell
pytest tests/test_matchup.py
# Manual: Create matchup via API
```

---

## Development Workflow

### Daily Workflow
1. Pull latest from `feature/app-rewrite`
2. Work on current phase checklist
3. Write tests for new code
4. Run tests before committing
5. Commit with descriptive messages
6. Push to `feature/app-rewrite`

### Commit Message Format
```
type(scope): description

Examples:
feat(users): Add Google OAuth integration
fix(matchup): Fix UUID generation
refactor(elo): Extract calculator logic
test(leagues): Add scoring system tests
docs(readme): Update setup instructions
```

### Branch Protection
- **DO NOT** merge to `main` until all phases complete
- Keep `main` as fallback to old system
- All work in `feature/app-rewrite`

---

## Resources

### Documentation
- [APP_REWRITE_PLAN.md](APP_REWRITE_PLAN.md) - Complete plan
- [MIGRATION_PLAN.md](MIGRATION_PLAN.md) - Detailed migration strategy
- [FastAPI Users Docs](https://fastapi-users.github.io/fastapi-users/)
- [SQLModel Docs](https://sqlmodel.tiangolo.com/)
- [Vue 3 Docs](https://vuejs.org/)

### Current Codebase Reference
- `squire/` - Current backend code
- `frontend/public/` - Current frontend code
- `database/` - Database schemas
- `docs/` - Project documentation

---

## Key Decisions Reference

### Architecture
- **Backend:** Modular structure (users, matchup, elo, leagues)
- **Frontend:** Vue 3 + Composition API + TailwindCSS
- **Auth:** Google + Discord OAuth (NO email/password)
- **Database:** PostgreSQL with SQLModel ORM
- **Styling:** Dark mode default, black/yellow theme

### Business Rules
- **ELO:** K=50 for first 5 games, then configurable
- **Anonymous:** Can use matchup, NO ELO tracking
- **Roles:** player (default), organizer, admin
- **Leagues:** Group phase → Playoff
- **Scoring:** Win=1000, Draw=600, Loss=200 + bonus

---

## Troubleshooting

### Issue: Docker won't start
- Check `docker-compose.yml` paths
- Verify `.env` has required variables
- Run `docker-compose down -v` and retry

### Issue: Database connection fails
- Check `DATABASE_URL` in `.env`
- Verify PostgreSQL container is running
- Check `backend/app/db.py` Session config

### Issue: OAuth redirect fails
- Verify OAuth credentials in `.env`
- Check callback URLs in Google/Discord console
- Ensure `FRONTEND_URL` matches actual URL

### Issue: Alembic migration fails
- Check `alembic.ini` database URL
- Verify `backend/app/db.py` imports all models
- Run `alembic downgrade -1` and retry

---

## Progress Tracking

### Phase Status
- [x] Phase 0: Preparation (Complete)
- [ ] Phase 1: Backend Foundation (In Progress)
- [ ] Phase 2: Users + OAuth (Not Started)
- [ ] Phase 3: Matchup (Not Started)
- [ ] Phase 4: ELO (Not Started)
- [ ] Phase 5: Leagues (Not Started)
- [ ] Phase 6: Frontend (Not Started)
- [ ] Phase 7-8: Polish (Not Started)

### Current Sprint Focus
**Week 1 Goal:** Complete Phase 1 + Phase 2
- Backend structure functional
- OAuth login working
- User roles implemented

---

## Getting Help

### When Stuck
1. Check [MIGRATION_PLAN.md](MIGRATION_PLAN.md) for detailed guidance
2. Review current code in `squire/` for reference
3. Consult FastAPI Users documentation
4. Check existing tests for patterns

### Before Asking for Review
- [ ] All tests passing
- [ ] Code follows existing patterns
- [ ] Documentation updated
- [ ] `.env.example` updated if needed
- [ ] Migrations created and tested

---

## Success Metrics

### Phase 1 Success
- Backend starts without errors
- Database connection works
- Health check endpoint responds
- Alembic migrations run successfully

### Phase 2 Success
- Can login with Google OAuth
- Can login with Discord OAuth
- User gets correct role (player default)
- Protected routes require authentication
- Admin can promote users to organizer

### Overall Success
- All features from original plan implemented
- All tests passing
- Production deployment successful
- No critical bugs
- Admin panel functional

---

**Ready to begin implementation!**

**Next Command:**
```powershell
# Create backend structure
New-Item -Path "backend\app\core" -ItemType Directory -Force
```

**Then:** Start implementing `backend/app/config.py`
