# Quickstart Guide - v0.3.0 Development

## For Reviewers/Testers

This branch contains the full v0.3.0 matchup system + battle plan gallery.

### Prerequisites

**Primary Method (Docker - Recommended):**
- Docker Desktop installed ([Download](https://www.docker.com/products/docker-desktop/))
- `just` command runner ([Install Guide](SETUP.md#prerequisites))

**Alternative (Local Development):**
- Python 3.11+ installed
- Git Bash or PowerShell

### 1. Clone and Setup

```bash
# Clone repository
git clone https://github.com/ogdowski/squigleague.git
cd squigleague

# Checkout this branch
git checkout release/v0.3.0-aos-matchups
```

**If using local development (skip if using Docker):**
```bash
# Create Python virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# On Git Bash:
source .venv/Scripts/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Start Application

**Method A: Docker (Recommended for Testing)**

```bash
# Start with just
just dev

# OR manually with docker-compose
docker-compose up --build
```

This starts:
- Backend API on http://localhost:8000
- Frontend on http://localhost (port 80)
- PostgreSQL database
- Nginx reverse proxy

**Method B: Local Development Servers**

**Option 1: Activity Script**
```powershell
.\scripts\activity-start-servers.ps1
```

This opens two PowerShell windows:
- Backend on http://localhost:8000
- Frontend on http://localhost:3000

**Option B: Manual**
```powershell
# Terminal 1 - Backend
$env:DATABASE_URL="sqlite:///./squigleague.db"
.\.venv\Scripts\python.exe -m uvicorn herald.main:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend\public
python spa-server.py
```

### 3. Access Application

**Docker Deployment:**
- **Main App**: http://localhost/
- **Battle Plan Gallery**: http://localhost/#/squire/battleplans
- **Create Matchup**: http://localhost/#/squire/matchup
- **API Docs**: http://localhost/docs (proxied through nginx)

**Local Development:**
- **Main App**: http://localhost:3000/
- **Battle Plan Gallery**: http://localhost:3000/#/squire/battleplans
- **Create Matchup**: http://localhost:3000/#/squire/matchup
- **API Docs**: http://localhost:8000/docs

### 4. Test Features

#### Battle Plan Gallery
1. Navigate to http://localhost:3000/#/squire/battleplans
2. View all 12 AoS GH 2025-26 battle plans with deployment maps
3. Click cards to see details (objectives, scoring, TWIST mechanics)

#### Matchup System
1. Navigate to http://localhost:3000/#/squire/matchup
2. Click "Create Matchup"
3. Copy the matchup URL
4. Submit army list as Player 1
5. Open matchup URL in incognito/different browser as Player 2
6. Submit army list as Player 2
7. Both players see lists revealed + random battle plan

### Troubleshooting

**Docker Issues:**

**Containers won't start:**
```bash
# Stop all containers
just down
# OR
docker-compose down

# Rebuild and start
just dev
# OR
docker-compose up --build
```

**Check container status:**
```bash
docker ps -a
```

**View container logs:**
```bash
# All services
just logs

# Specific service
docker logs squig
docker logs squig-frontend
docker logs squig-nginx
```

**Port conflicts:**
- Docker uses port 80 (frontend/nginx) and 8000 (backend API)
- Stop services using these ports or modify docker-compose.yml

**Local Development Issues:**

**"Failed to fetch" error:**
- Check both servers are running (ports 8000 and 3000)
- Run: `Test-NetConnection -ComputerName localhost -Port 8000 -InformationLevel Quiet`
- Run: `Test-NetConnection -ComputerName localhost -Port 3000 -InformationLevel Quiet`
- Both should return `True`

**Server won't start:**
- Kill existing Python processes: `Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force`
- Restart activity script

**Port already in use:**
- Change ports in commands or kill processes using those ports

## What Changed in This Release

See [PR_DETAILS.md](PR_DETAILS.md) for complete release notes.

**Quick Summary:**
- ✅ Battle Plan Gallery: 12 AoS GH 2025-26 plans with deployment maps
- ✅ Matchup System: Anonymous list exchange + battle plan randomization
- ✅ Docker Deployment: Full containerization with nginx reverse proxy
- ✅ Verified Data: All battle plans sourced from official Wahapedia GH 2025-26
- ✅ 4 integration tests passing
- ✅ 109 files changed, 10,987+ lines added

**Key Files:**
- `squire/battle_plans.py` - Battle plan data
- `squire/matchup.py` - Matchup system
- `frontend/public/modules/squire/battleplan-gallery.js` - Gallery UI
- `assets/battle-plans/*.png` - 12 deployment map images
- `herald/Dockerfile` - Fixed module imports
- `nginx/nginx-dev.conf` - Local development proxy config
