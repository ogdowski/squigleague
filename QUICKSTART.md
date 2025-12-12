# Quickstart Guide - v0.3.0 Development

## For Reviewers/Testers

This branch contains the full v0.3.0 matchup system + battle plan gallery.

### Prerequisites
- Python 3.11+ installed
- Git Bash or PowerShell

### 1. Clone and Setup

```bash
# Clone the repo
git clone https://github.com/ogdowski/squigleague.git
cd squigleague

# Checkout this branch
git checkout release/v0.3.0-aos-matchups

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

### 2. Start Servers

**Option A: Activity Script (Recommended)**
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

Open browser to:
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

### What Changed in This Release

**New Features:**
- ✅ Battle Plan Gallery with 12 AoS GH 2025-26 deployment maps
- ✅ Battle plan data corrected to official Wahapedia source
- ✅ Matchup system for list exchange + battle plan generation
- ✅ API endpoints for battle plans and matchups
- ✅ Frontend gallery components with Alpine.js

**Files Changed:**
- 109 files modified
- 10,987 lines added
- Battle plan images, gallery components, matchup system, tests

**Testing:**
- 4 gallery integration tests passing
- Matchup system tests included
- Manual GUI testing documented in docs/RELEASE_v0.3.0_GUI_TEST.md
