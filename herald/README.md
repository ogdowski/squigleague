# 📯 Herald Backend - JSON API

Backend service for the Herald blind list exchange system.

## What is Herald Backend?

The Herald backend is a **pure JSON API** built with FastAPI. It handles all business logic, database operations, and cryptographic hash generation for the Herald list exchange system.

## Architecture

Herald uses a **frontend/backend separation**:

- **Backend (this service)**: FastAPI JSON API at `/api/herald/*`
- **Frontend**: Separate Alpine.js SPA (see `../frontend/`)
- **Communication**: Frontend calls backend via JSON API
- **Nginx**: Routes `/api/*` to backend, everything else to frontend

## Features

- **Pure JSON API**: No HTML rendering, only JSON responses
- **Cryptographic Security**: SHA-256 hashing for list integrity
- **Database**: PostgreSQL for persistent storage
- **Rate Limiting**: Prevents abuse
- **Health Checks**: `/health` endpoint for monitoring
- **Stats Endpoint**: `/api/herald/stats` provides system statistics

## Tech Stack

- **Framework**: FastAPI (Python 3.11)
- **Database**: PostgreSQL (shared with other modules)
- **Deployment**: Docker container

## API Endpoints

All endpoints are JSON-only. The frontend (separate service) handles HTML rendering.

### Public Endpoints

- `POST /api/herald/exchange/create` - Create new exchange
  - Returns: `{"id": "...", "hash_a": "...", "url": "..."}`
- `GET /api/herald/exchange/{id}` - Get exchange data
  - Returns: Exchange object with lists (if both submitted)
- `POST /api/herald/exchange/{id}/respond` - Submit Player B's list
  - Returns: Complete exchange with both lists
- `GET /api/herald/exchange/{id}/status` - Check if complete
  - Returns: `{"complete": true/false}`
- `GET /api/herald/stats` - System statistics
  - Returns: `{"version": "...", "exchanges": {...}, "uptime": ...}`
- `GET /health` - Health check
  - Returns: `{"status": "healthy", "module": "herald", "database": "connected"}`

### Admin Endpoints

- `GET /admin/resources?admin_key=KEY` - Server resources
- `GET /admin/abuse-report?admin_key=KEY` - Abuse detection

## Environment Variables

```bash
DATABASE_URL=postgresql://squig:password@postgres:5432/squigleague
ADMIN_KEY=your_admin_key_here
MODULE_NAME=herald
```

## Development

The backend is typically run via Docker Compose alongside the frontend:

```bash
# From project root
just dev              # Starts both backend and frontend

# Backend logs
just logs-squig

# Backend-only development (if needed)
cd herald
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```

**Note**: The backend expects requests at `/api/herald/*` paths when behind nginx. For local development without nginx, use the full path or adjust your frontend to call `http://localhost:8001/exchange/create` instead of `/api/herald/exchange/create`.

## Database Schema

Herald uses these tables:
- `herald_exchanges` - Exchange records
- `herald_request_log` - Request logging for abuse detection

## Security Features

- Rate limiting on all endpoints
- Bot detection and blocking
- Request logging with IP tracking
- Input validation and sanitization
- Automatic cleanup of old data

## Rate Limits

- Home page: 60 requests/minute
- Create exchange: 10 requests/hour
- View exchange: 30 requests/minute
- Submit response: 20 requests/hour
- Status check: 120 requests/minute

## Automatic Cleanup

Runs daily:
- Deletes exchanges older than 7 days
- Deletes request logs older than 7 days

## Word Lists

Exchange IDs format: `{adjective}-{noun}-{verb}-{hash}`

Example: `crimson-captain-charges-7a2f`

- 50 adjectives (colors, traits, war terms)
- 50 Warhammer nouns (units, races, characters)
- 50 verbs (battle actions)
- 4-character hex hash

Total combinations: 8,192,000,000

## Production Configuration

Runs on Hetzner CX23:
- 1 Uvicorn worker
- 512MB memory limit
- PostgreSQL connection pooling
- Nginx reverse proxy (routes `/api/*` to this service)
- Separate frontend service for static files

## Docker Images

Built as multi-arch images (amd64/arm64):
- Backend: `ogdowski/private:squigleague-VERSION`
- Frontend: `ogdowski/private:squigleague-frontend-VERSION`

Both images are built and pushed together:
```bash
just push  # Builds and pushes both backend and frontend
```

## Monitoring

Check server health:
```bash
curl https://squigleague.com/health
```

View system stats:
```bash
curl https://squigleague.com/api/herald/stats
```

View resources (requires admin key):
```bash
curl "https://squigleague.com/admin/resources?admin_key=YOUR_KEY"
```

Check for abusive IPs:
```bash
curl "https://squigleague.com/admin/abuse-report?admin_key=YOUR_KEY&min_requests=100"
```

## Future Enhancements (Phase 3)

When authentication is added:
- User accounts with login
- Exchange history
- Private exchanges
- Notifications when opponent responds
- Export to PDF

Database already prepared with `user_id_a` and `user_id_b` foreign keys.

## License

Part of Squig League ecosystem.
Copyright © 2025 Ariel Ogdowski. All Rights Reserved.
