# Setup Guide

Complete guide to setting up Squig League for local development.

## Prerequisites

### Required Software

1. **Docker & Docker Compose**
   - [Install Docker Desktop](https://www.docker.com/products/docker-desktop/)
   - Verify: `docker --version` and `docker-compose --version`

2. **just** command runner

**macOS:**
```bash
brew install just
```

**Linux:**
```bash
# Ubuntu/Debian
sudo apt install just

# Arch Linux
sudo pacman -S just

# Fedora
sudo dnf install just

# Or use pre-built binary (all distros)
curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh | bash -s -- --to /usr/local/bin
```

**Verify installation:**
```bash
just --version
```

See [JUST_INSTALL.md](JUST_INSTALL.md) for detailed installation instructions.

## Quick Start

```bash
# Clone repository
git clone https://github.com/arielogdowski/squig_league.git
cd squig_league

# Start development environment
# (automatically creates .env.local with safe defaults)
just dev
```

That's it! The application is now running at http://localhost:8000

## Step-by-Step Setup

### 1. Clone Repository

```bash
git clone https://github.com/arielogdowski/squig_league.git
cd squig_league
```

### 2. Environment Configuration

**Automatic (recommended):**
```bash
# Just run dev - it auto-creates .env.local
just dev
```

**Manual (if needed):**
```bash
# Create environment file
cp .env.local.example .env.local

# View configuration
cat .env.local
```

The `.env.local` file contains safe defaults for local development:
- `DB_PASSWORD`: Local PostgreSQL password
- `HERALD_ADMIN_KEY`: Development admin key
- `SQUIG_VERSION`: Application version

**No changes needed** for local development.

### 3. Start Services

**Foreground (with logs):**
```bash
just dev
```

**Background:**
```bash
just up

# View logs
just logs

# View specific service logs
just logs-herald
just logs-db
```

### 4. Verify Installation

**Check health:**
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "module": "herald",
  "database": "connected"
}
```

**Access the application:**
- Open browser: http://localhost:8000
- You should see the Herald home page (served by frontend service)
- Backend API available at: http://localhost:8000/api/herald/*

### 5. Stop Services

```bash
just down
```

## Available Commands

View all available commands:
```bash
just --list
```

**Common commands:**
```bash
# Development
just dev              # Start dev environment
just up               # Start in background
just down             # Stop services
just restart          # Restart services
just logs             # View all logs
just logs-squig       # Backend logs only
just logs-db          # Database logs only

# Environment
just env-check        # Check configuration
just env-create-local # Create .env.local

# Database
just db-connect       # Connect to PostgreSQL
just db-backup        # Backup database
just db-reset         # Reset database

# Monitoring
just ps               # Show running containers
just stats            # Container resource usage
just health           # Check Herald health

# Cleanup
just clean            # Stop and remove containers
just prune            # Remove unused Docker resources
```

## Manual Docker Compose (Without just)

If you prefer not to use `just`:

```bash
# Create environment file
cp .env.local.example .env.local

# Start services
docker-compose --env-file .env.local \
  -f docker-compose.yml \
  -f docker-compose.dev.yml \
  up -d --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Troubleshooting

### Port Already in Use

**Problem:** Error about port 8000 or 5432 already in use

**Solution:**
```bash
# Check what's using the port
lsof -i :8000
lsof -i :5432

# Stop the service or change ports in docker-compose.dev.yml
```

### Docker Not Running

**Problem:** Cannot connect to Docker daemon

**Solution:**
- Start Docker Desktop
- Verify: `docker ps`

### Database Connection Failed

**Problem:** Backend can't connect to PostgreSQL

**Solution:**
```bash
# Check database is running
just ps

# Check database logs
just logs-db

# Reset database if needed
just down
just up
```

### Environment Variables Not Working

**Problem:** Configuration not applied

**Solution:**
```bash
# Check .env.local exists
ls -la .env.local

# Check configuration
just env-check

# Common issue: no spaces around = in .env files
# ✅ Correct: DB_PASSWORD=mypassword
# ❌ Wrong:   DB_PASSWORD = mypassword

# Recreate .env.local
rm .env.local
just dev
```

### Permission Denied (Linux)

**Problem:** Permission errors with Docker

**Solution:**
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Log out and back in, then:
docker ps
```

## Development Workflow

### Making Changes

1. **Edit code** in your editor
2. **Restart service** to apply changes:
   ```bash
   just restart
   ```
3. **View logs** for errors:
   ```bash
   just logs-squig  # Backend logs
   just logs        # All services
   ```

### Database Changes

**Connect to database:**
```bash
just db-connect
```

**Backup before making changes:**
```bash
just db-backup
```

**Reset to clean state:**
```bash
just db-reset
```

## Architecture

Squig League uses a **frontend/backend separation** architecture:

```
┌─────────────┐
│   Nginx     │  Routes: /api/* → backend, /* → frontend
└──────┬──────┘
       │
   ┌───┴────┐
   │        │
   ▼        ▼
Backend  Frontend
(API)    (Alpine.js SPA)
   │
   ▼
PostgreSQL
```

### Services

1. **Backend (squig)**: FastAPI JSON API at `/api/herald/*`
2. **Frontend**: Alpine.js SPA serving static HTML/JS/CSS
3. **Nginx**: Reverse proxy and static file server
4. **PostgreSQL**: Shared database for all modules

### Benefits

- Independent scaling of frontend and backend
- Clean API contracts with JSON-only backend
- Easier testing and development
- Static frontend can be cached/CDN'd
- Backend can serve multiple frontends

## Project Structure

```
squig_league/
├── herald/              # Backend (JSON API)
│   ├── main.py         # FastAPI application
│   ├── database.py     # Database operations
│   └── models.py       # Pydantic models
├── frontend/           # Frontend (Alpine.js SPA)
│   ├── index.html      # Main page
│   ├── view.html       # Exchange view
│   ├── style.css       # Global styles
│   └── Dockerfile      # Frontend container
├── database/           # PostgreSQL initialization
│   └── init.sql        # Database schema
├── nginx/              # Nginx configuration
│   └── nginx.conf      # Routing and proxy config
├── .env.local.example  # Environment template
├── docker-compose.yml  # Base Docker config
├── docker-compose.dev.yml  # Dev overrides
└── justfile            # Command definitions
```

## Next Steps

- **Read the code**: Start with `herald/main.py`
- **Check issues**: [GitHub Issues](https://github.com/arielogdowski/squig_league/issues)
- **Make changes**: See [CONTRIBUTING.md](CONTRIBUTING.md)
- **Test changes**: Run the app and verify it works

## Getting Help

- **Documentation**: See [README.md](README.md#documentation)
- **Issues**: Create an issue on GitHub
- **Email**: squigleague@proton.me

## Environment Variables Reference

All variables in `.env.local`:

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_PASSWORD` | `dev_password_123` | PostgreSQL password |
| `HERALD_ADMIN_KEY` | `dev_admin_key_change_in_production` | Admin API key |
| `VPS_IP` | `localhost` | VPS IP (not used in dev) |
| `VPS_USER` | `root` | VPS user (not used in dev) |
| `REGISTRY` | `docker.io` | Docker registry |
| `IMAGE_PREFIX` | `ogdowski` | Docker image prefix |
| `IMAGE_NAME` | `private` | Docker image name |
| `SQUIG_VERSION` | `0.1.0` | Application version |
| `DOMAIN` | `localhost` | Domain name |
| `EMAIL` | `dev@localhost` | Email for SSL |

**For development:** Defaults work fine, no changes needed.

**For production:** See deployment documentation (private).
