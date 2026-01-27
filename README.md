# Squig League

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0.html)
[![Docker Ready](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)

Open-source competitive league and matchup platform for Age of Sigmar.

**Live:** [squigleague.com](https://squigleague.com)

## Features

### Matchup System
Blind army list exchange for casual 1v1 games:

- **Blind Exchange**: Both players submit lists secretly, revealed simultaneously
- **Battle Plan Integration**: GHB 2025/2026 missions with objectives and underdog abilities
- **Auto Map Assignment**: Random mission assigned on reveal
- **Result Tracking**: Submit scores with opponent confirmation (24h auto-confirm)
- **Share Results**: Generate shareable images (1080x1080) with avatars, scores, and mission for social media
- **Friendly IDs**: AoS-themed IDs (e.g., "mighty-dragon-3x7a")
- **Anonymous Play**: Create matchups without registration

### League System
Full tournament management with group and knockout phases:

- **Group Phase**: Automatic group drawing, round-robin match generation
- **Knockout Phase**: Bracket generation (4/8/16/32 players) from qualifiers
- **Scoring System**: Points per match with margin bonus
- **Army Lists**: Per-phase lists with freeze/visible controls
- **ELO Integration**: Rating changes tracked per match
- **Organizer Tools**: Player management, match editing, phase controls
- **Voting System**: Post-league awards voting (e.g., Best Sportsmanship)
  - Anonymous voting until organizer closes
  - Automatic tie detection with random tie-breaker option
  - Winner displayed alongside tournament champion

### ELO Rating System
Global skill ratings for competitive players:

- **Standard ELO**: K=32 for experienced, K=50 for new players (first 5 games)
- **Match Tracking**: ELO before/after stored per match
- **Global Rankings**: Leaderboard sorted by rating
- **Configurable**: Admin can adjust K-factors via settings

### User System
- **Authentication**: Email/password with JWT, Discord OAuth
- **Profiles**: Avatar, location, language preference
- **Roles**: Player, Organizer, Admin

### UI/UX
- **Dark Theme**: Gradient background with consistent styling
- **Mobile-First**: Responsive design optimized for mobile play
- **Social Sharing**: Generate branded images for X, Facebook, Instagram

## Scoring System

League matches use a base + bonus point system:

| Result | Base Points | Bonus |
|--------|-------------|-------|
| Win    | 1000        | 0-100 |
| Draw   | 600         | 0-100 |
| Loss   | 200         | 0-100 |

**Bonus calculation**: `min(100, max(0, score_margin + 50))`

Example: Win 72-68 = 1000 + min(100, 4+50) = **1054 points**

## Battle Plans

12 GHB 2025/2026 missions supported:
- Passing Seasons, Paths of the Fey, Roiling Roots, Cyclic Shifts
- Surge of Slaughter, Linked Ley Lines, Noxious Nexus, The Liferoots
- Bountiful Equinox, Lifecycle, Creeping Corruption, Grasp of Thorns

Each includes deployment type, objectives, scoring rules, and underdog abilities.

## Army Factions

25 Age of Sigmar 4th Edition factions with auto-detection from army lists:

**Order** (9): Cities of Sigmar, Daughters of Khaine, Fyreslayers, Idoneth Deepkin, Kharadron Overlords, Lumineth Realm-lords, Seraphon, Stormcast Eternals, Sylvaneth

**Chaos** (7): Blades of Khorne, Disciples of Tzeentch, Hedonites of Slaanesh, Helsmiths of Hashut, Maggotkin of Nurgle, Skaven, Slaves to Darkness

**Death** (4): Flesh-eater Courts, Nighthaunt, Ossiarch Bonereapers, Soulblight Gravelords

**Destruction** (5): Gloomspite Gitz, Ironjawz, Kruleboyz, Ogor Mawtribes, Sons of Behemat

## Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.11)
- **ORM**: SQLModel (SQLAlchemy + Pydantic)
- **Database**: PostgreSQL
- **Migrations**: Alembic
- **Authentication**: JWT tokens, OAuth2

### Frontend
- **Framework**: Vue 3 (Composition API)
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **State**: Pinia
- **i18n**: English, Polish
- **Image Generation**: html2canvas for shareable result graphics

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Reverse Proxy**: Nginx
- **Task Runner**: Just (justfile)

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Just (optional, `brew install just`)

### Local Development

```bash
# Clone and enter
git clone https://github.com/ogdowski/squigleague.git
cd squigleague

# Start services
just up

# Seed test data (optional)
just seed

# Access
open http://localhost
```

### Test Credentials (after `just seed`)
- **Admin**: org1@t.co / test
- **Players**: p1@t.co - p30@t.co / test

### Commands

```bash
just up              # Start services
just down            # Stop services
just logs            # View all logs
just logs-backend    # View backend logs only
just seed            # Seed test data
just test            # Run tests
just test-k PATTERN  # Run specific test by name
just build           # Build images
just migrate         # Run migrations
just db-connect      # PostgreSQL shell
just db-reset        # Reset database (DANGER!)
just make-admin EMAIL    # Make user admin
just health          # Check service health
just stats           # Container resource usage
```

## Project Structure

```
squig_league/
├── backend/
│   ├── app/
│   │   ├── core/        # Auth, config, dependencies
│   │   ├── users/       # User management & auth
│   │   ├── matchup/     # Blind list exchange
│   │   ├── league/      # Tournament management
│   │   ├── player/      # Player profiles & ELO
│   │   ├── admin/       # Admin endpoints
│   │   └── data/        # Maps, armies data
│   ├── migrations/      # Alembic migrations
│   ├── tests/           # Pytest tests
│   └── seed_*.py        # Database seeders
├── frontend/
│   ├── src/
│   │   ├── views/       # Page components
│   │   ├── components/  # Reusable UI
│   │   ├── stores/      # Pinia state
│   │   └── locales/     # i18n translations
│   └── public/assets/   # Battle plan images
├── nginx/               # Proxy configs
├── docker-compose.yml   # Development
├── docker-compose.prod.yml
└── justfile             # Task runner
```

## API Endpoints

### Matchup
```
POST   /api/matchup                    Create matchup
GET    /api/matchup/{name}             Get matchup status
POST   /api/matchup/{name}/submit      Submit army list
GET    /api/matchup/{name}/reveal      Get revealed matchup with lists
POST   /api/matchup/{name}/result      Submit result
POST   /api/matchup/{name}/result/confirm  Confirm result
POST   /api/matchup/{name}/result/edit     Edit pending result
POST   /api/matchup/{name}/cancel      Cancel matchup
PATCH  /api/matchup/{name}/title       Update title
PATCH  /api/matchup/{name}/public      Toggle public visibility
GET    /api/matchup/my-matchups        List user's matchups
GET    /api/matchup/public             List public matchups
GET    /api/matchup/maps               List battle plans
GET    /api/matchup/armies             List army factions
```

### League
```
GET    /api/league                     List leagues
POST   /api/league                     Create league
GET    /api/league/{id}                League details
GET    /api/league/{id}/standings      Group standings
GET    /api/league/{id}/matches        List matches
POST   /api/league/{id}/matches/{id}/submit  Submit result
POST   /api/league/{id}/groups/draw    Draw groups
POST   /api/league/{id}/advance-knockout    Advance phase

# Voting
POST   /api/league/{id}/enable-voting  Enable voting for league
GET    /api/league/{id}/vote-categories      List vote categories
POST   /api/league/{id}/vote-categories/{cid}/vote    Cast vote
GET    /api/league/{id}/vote-categories/{cid}/results Get results
POST   /api/league/{id}/close-voting   Close voting & reveal results
POST   /api/league/{id}/vote-categories/{cid}/break-tie  Random tie-breaker
```

### Users
```
POST   /api/auth/register              Register
POST   /api/auth/login                 Login
GET    /api/auth/me                    Current user
GET    /api/player/{id}                Player profile
GET    /api/ranking                    ELO leaderboard
```

### Admin
```
GET    /api/admin/users                List users
PATCH  /api/admin/users/{id}/role      Change role
PATCH  /api/admin/elo-settings         Update ELO config
POST   /api/admin/recalculate-army-stats  Rebuild stats
```

## Environment Variables

### Backend (.env)
```env
DATABASE_URL=postgresql://squig:password@postgres:5432/squigleague
SECRET_KEY=your-secret-key
DISCORD_CLIENT_ID=xxx
DISCORD_CLIENT_SECRET=xxx
```

### Frontend
```env
VITE_API_URL=/api
```

## Database Models

| Model | Purpose |
|-------|---------|
| `users` | Accounts with auth |
| `oauth_accounts` | Discord/Google OAuth |
| `player_elo` | Global ELO ratings |
| `leagues` | Tournament records |
| `groups` | Group phase divisions |
| `league_players` | Participants with stats |
| `matches` | League matches |
| `matchups` | Blind list exchanges |
| `vote_categories` | Voting categories per league |
| `votes` | Individual player votes |
| `army_stats` | Faction win rates |
| `app_settings` | Global config |

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## License

AGPL-3.0 - See [LICENSE](LICENSE) for details.
