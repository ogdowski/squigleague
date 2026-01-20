# Squig League

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0.html)
[![Docker Ready](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)

Open-source competitive league and matchup platform for Age of Sigmar.

**Live:** [squigleague.com](https://squigleague.com)

## Features

### Matchup System (Herald)
- **Blind Army List Exchange**: Both players submit lists secretly, revealed simultaneously
- **Battle Plan Integration**: GHB 2025/2026 missions with objectives, scoring rules, and underdog abilities
- **Automatic Map Randomization**: Random map assignment on reveal
- **Friendly Matchup IDs**: AoS-themed IDs (e.g., "mighty-dragon-3x7a")
- **Anonymous Play**: Create matchups without registration
- **7-Day Expiration**: Matchups automatically expire

### League System
- **Full Tournament Management**: Create and manage competitive leagues
- **Group Phase**: Automatic group drawing, round-robin match generation
- **Knockout Phase**: Bracket generation from group qualifiers
- **Flexible Scoring**: Configurable points per win/draw/loss
- **Army List Management**: Per-phase lists with freeze/reveal controls
- **Standings & Qualification**: Automatic standings with qualification rules
- **Player Avatars**: Profile pictures throughout the app
- **Organizer Tools**: Player management, match editing, phase controls

### User System
- **Registration & Authentication**: Email/password with JWT tokens
- **OAuth Integration**: Discord login support
- **User Profiles**: Avatar upload, settings, match history
- **Role System**: Player, Organizer, Admin roles

## Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.11)
- **ORM**: SQLModel (SQLAlchemy + Pydantic)
- **Database**: PostgreSQL
- **Authentication**: JWT tokens, OAuth2

### Frontend
- **Framework**: Vue 3 (Composition API)
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **State Management**: Pinia
- **Routing**: Vue Router

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Reverse Proxy**: Nginx
- **Task Runner**: Just (justfile)

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Just (optional, for shortcuts)

### Local Development

```bash
# Clone the repository
git clone https://github.com/yourusername/squig_league.git
cd squig_league

# Copy environment files
cp .env.local.example .env

# Start all services
docker-compose up -d

# Or using Just
just up

# Access the application
open http://localhost
```

### Useful Commands

```bash
# View logs
just logs

# Rebuild containers
just build

# Stop services
just down

# Run backend tests
just test
```

## Project Structure

```
squig_league/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── core/           # Auth, dependencies, utilities
│   │   ├── users/          # User management & auth
│   │   ├── matchup/        # Blind list exchange system
│   │   ├── league/         # League/tournament management
│   │   ├── player/         # Player profiles
│   │   └── admin/          # Admin endpoints
│   ├── migrations/         # Alembic migrations
│   └── Dockerfile
├── frontend/               # Vue 3 frontend
│   ├── src/
│   │   ├── views/         # Page components
│   │   ├── components/    # Reusable components
│   │   ├── stores/        # Pinia state
│   │   ├── constants/     # App constants
│   │   └── router/        # Vue Router
│   ├── public/
│   │   └── assets/        # Battle plan images
│   └── Dockerfile
├── nginx/                  # Reverse proxy configs
├── assets/                 # Battle plan source images
├── docker-compose.yml      # Local development
├── docker-compose.prod.yml # Production
└── justfile               # Task runner commands
```

## Environment Variables

### Backend

```env
DATABASE_URL=postgresql://user:pass@postgres:5432/squig_league
SECRET_KEY=your-secret-key-here
DISCORD_CLIENT_ID=your-discord-client-id
DISCORD_CLIENT_SECRET=your-discord-client-secret
```

### Frontend

```env
VITE_API_URL=/api
```

## API Endpoints

### Matchup
- `POST /api/matchup/create` - Create new matchup
- `GET /api/matchup/{name}` - Get matchup status
- `POST /api/matchup/{name}/submit` - Submit army list
- `GET /api/matchup/{name}/reveal` - Get revealed matchup
- `GET /api/matchup/maps` - Get available battle plans

### League
- `GET /api/league` - List leagues
- `POST /api/league` - Create league
- `GET /api/league/{id}` - Get league details
- `GET /api/league/{id}/standings` - Get group standings
- `GET /api/league/{id}/matches` - List matches
- `GET /api/league/{id}/matches/{match_id}` - Match details

### Users
- `POST /api/users/register` - Register
- `POST /api/users/login` - Login
- `GET /api/users/me` - Current user
- `GET /api/player/{id}` - Player profile

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## License

AGPL-3.0 - See [LICENSE](LICENSE) for details.
