# SquigLeague Backend

FastAPI backend with OAuth authentication (Google + Discord).

## Features

- ✅ **FastAPI Users** - Complete user management system
- ✅ **OAuth 2.0** - Google and Discord authentication
- ✅ **SQLModel** - Type-safe ORM with Pydantic integration
- ✅ **JWT Authentication** - Secure token-based auth
- ✅ **Role-based Access Control** - player, organizer, admin roles
- ✅ **PostgreSQL** - Production-ready database
- ✅ **Alembic** - Database migrations
- ✅ **Modular Architecture** - Separated concerns (users, matchup, elo, leagues)

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 16+
- Google OAuth credentials
- Discord OAuth credentials

### Installation

1. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your values
   ```

4. **Set up database:**
   ```bash
   # Make sure PostgreSQL is running
   # Database will be created automatically on first run
   ```

5. **Run the application:**
   ```bash
   uvicorn app.main:app --reload
   ```

   Or with custom settings:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

6. **Open API docs:**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## Configuration

### Environment Variables

Create a `.env` file in the `backend/` directory:

```bash
# Application
APP_NAME=SquigLeague
ENVIRONMENT=development
DEBUG=True

# Database
DATABASE_URL=postgresql://squigleague:changeme@localhost:5432/squigleague

# Security
SECRET_KEY=your-super-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Discord OAuth
DISCORD_CLIENT_ID=your-discord-application-id
DISCORD_CLIENT_SECRET=your-discord-client-secret

# URLs
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:5173
```

### OAuth Setup

#### Google OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google+ API
4. Go to **Credentials** → **Create Credentials** → **OAuth 2.0 Client ID**
5. Add authorized redirect URIs:
   - `http://localhost:8000/api/auth/google/callback`
   - `https://yourdomain.com/api/auth/google/callback` (production)
6. Copy Client ID and Client Secret to `.env`

#### Discord OAuth

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to **OAuth2** settings
4. Add redirect URIs:
   - `http://localhost:8000/api/auth/discord/callback`
   - `https://yourdomain.com/api/auth/discord/callback` (production)
5. Copy Client ID and Client Secret to `.env`

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Settings management
│   ├── db.py                # Database session
│   ├── core/                # Core utilities
│   │   ├── security.py      # Password hashing, JWT
│   │   ├── deps.py          # Dependencies
│   │   └── permissions.py   # RBAC
│   ├── users/               # Users module
│   │   ├── models.py        # User, OAuthAccount models
│   │   ├── schemas.py       # Pydantic schemas
│   │   ├── auth.py          # FastAPI Users config
│   │   └── routes.py        # Auth & user routes
│   ├── matchup/             # Matchup module (TODO)
│   ├── elo/                 # ELO module (TODO)
│   └── leagues/             # Leagues module (TODO)
├── alembic/                 # Database migrations
├── requirements.txt
├── Dockerfile
└── .env.example
```

## API Endpoints

### Authentication

- `POST /api/auth/jwt/login` - JWT login (for testing)
- `POST /api/auth/jwt/logout` - Logout
- `GET /api/auth/google/authorize` - Google OAuth login
- `GET /api/auth/google/callback` - Google OAuth callback
- `GET /api/auth/discord/authorize` - Discord OAuth login
- `GET /api/auth/discord/callback` - Discord OAuth callback

### Users

- `GET /api/users/me` - Get current user
- `PATCH /api/users/me` - Update current user
- `GET /api/users/me/profile` - Get profile with stats
- `GET /api/users/{user_id}/profile` - Get public profile (no auth required)

### Admin (Requires admin role)

- `GET /api/admin/users` - List all users
- `PATCH /api/admin/users/{user_id}/role` - Update user role

## Database Migrations

### Create migration

```bash
alembic revision --autogenerate -m "Description of changes"
```

### Run migrations

```bash
alembic upgrade head
```

### Rollback migration

```bash
alembic downgrade -1
```

## Development

### Testing imports

```bash
python test_startup.py
```

### Code formatting

```bash
black app/
isort app/
```

### Run tests

```bash
pytest
```

## Docker

### Build image

```bash
docker build -t squigleague-backend .
```

### Run container

```bash
docker run -p 8000:8000 --env-file .env squigleague-backend
```

### Docker Compose

See main `docker-compose.yml` in project root.

## Roles & Permissions

### User Roles

- **player** (default) - Can play in leagues, use matchup, has ELO
- **organizer** - Can create and manage leagues
- **admin** - Full access to all features

### Permission System

Permissions are defined in `app/core/permissions.py`:

```python
PERMISSIONS = {
    "matchup.create": ["anonymous", "player", "organizer", "admin"],
    "league.create": ["organizer", "admin"],
    "users.manage": ["admin"],
    "elo.config": ["admin"],
    # ... more permissions
}
```

### Using permissions in routes

```python
from app.core.permissions import require_role

@router.post("/leagues", dependencies=[Depends(require_role("organizer", "admin"))])
def create_league():
    ...
```

## Troubleshooting

### Database connection fails

- Ensure PostgreSQL is running
- Check `DATABASE_URL` in `.env`
- Verify database exists: `psql -U postgres -c "CREATE DATABASE squigleague;"`

### OAuth redirect fails

- Check redirect URIs in Google/Discord console match `.env` URLs
- Ensure `FRONTEND_URL` is correct
- Check CORS settings in `app/main.py`

### Import errors

- Activate virtual environment
- Install dependencies: `pip install -r requirements.txt`
- Check Python version: `python --version` (should be 3.11+)

## Next Steps

- [ ] Implement Matchup module (Phase 3)
- [ ] Implement ELO system (Phase 4)
- [ ] Implement Leagues module (Phase 5)
- [ ] Create Alembic migrations
- [ ] Add comprehensive tests
- [ ] Set up CI/CD

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [FastAPI Users](https://fastapi-users.github.io/fastapi-users/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)

---

**Status:** Phase 2 Complete - Users module with OAuth ✅  
**Next:** Phase 3 - Matchup module
