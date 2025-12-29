# Squig League

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0.html)
[![Docker Ready](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)

Open-source blind army list exchange platform for Age of Sigmar competitive play.

**Live:** [squigleague.com](https://squigleague.com)

## Features

- **Herald (Matchup System)**: Blind army list exchange with automatic map randomization
- **Friendly Matchup IDs**: Age of Sigmar themed IDs (e.g., "mighty-dragon-3x7a")
- **Anonymous Play**: Create matchups without registration
- **7-Day Expiration**: Matchups automatically expire after 7 days
- **OAuth Ready**: Google and Discord authentication (coming soon)

## Architecture

Modern full-stack web application:

- **Backend**: FastAPI + SQLModel + PostgreSQL
- **Frontend**: Vue 3 + Vite + Tailwind CSS
- **Reverse Proxy**: Nginx routes `/api/*` → backend, `/` → frontend
- **Deployment**: Docker Compose with multi-stage builds

## Quick Start

### Local Development

```bash
# Start all services
docker-compose up -d

# Access the application
open http://localhost
```

### Production Deployment

```bash
# Build and deploy
just release v2.0.0

# Or manually
docker-compose -f docker-compose.prod.yml up -d
```

## Development

### Backend (FastAPI)

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run dev server
uvicorn app.main:app --reload
```

### Frontend (Vue 3)

```bash
cd frontend

# Install dependencies
npm install

# Run dev server
npm run dev
```

## Project Structure

```
squig_league/
├── backend/           # FastAPI backend
│   ├── app/
│   │   ├── users/     # User authentication
│   │   ├── matchup/   # Herald matchup logic
│   │   └── core/      # Shared utilities
│   └── Dockerfile
├── frontend/          # Vue 3 frontend
│   ├── src/
│   │   ├── views/     # Page components
│   │   ├── stores/    # Pinia state management
│   │   └── router/    # Vue Router config
│   └── Dockerfile
├── nginx/             # Reverse proxy config
│   ├── nginx.conf         # Local (HTTP)
│   └── nginx.prod.conf    # Production (HTTPS)
└── docker-compose.yml
```

## Environment Variables

### Backend (.env)

```env
DATABASE_URL=postgresql://user:pass@postgres:5432/db
SECRET_KEY=your-secret-key
GOOGLE_CLIENT_ID=your-google-oauth-id
DISCORD_CLIENT_ID=your-discord-oauth-id
```

### Frontend (.env)

```env
VITE_API_URL=http://localhost:8000
```

## License

AGPL-3.0 - See [LICENSE](LICENSE) for details.

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.
