# 📯 Herald - Fair Army List Exchange

Fair and secure blind army list exchange for Warhammer and other tabletop wargames.

## What is Herald?

Herald prevents list tailoring by using cryptographic hashing to ensure both players commit to their army lists simultaneously. Neither player can see the opponent's list until both have been submitted and locked.

## Features

- **Cryptographic Security**: SHA-256 hashing ensures lists cannot be modified after submission
- **No Registration**: Completely anonymous, no accounts required
- **Auto-Delete**: Exchanges automatically deleted after 7 days
- **Client-Side Verification**: Hash verification happens in the browser
- **Real-Time Updates**: Auto-refresh when opponent submits
- **Rate Limiting**: Prevents abuse

## How It Works

1. **Player A Creates**: Paste army list → Get unique URL → Hash locked
2. **Player B Responds**: Opens URL → Sees hash proof → Submits their list
3. **Both Revealed**: Lists instantly revealed to both players with timestamps

## Tech Stack

- **Backend**: FastAPI (Python 3.11)
- **Database**: PostgreSQL (shared with other modules)
- **Frontend**: TailwindCSS + Alpine.js
- **Deployment**: Docker containers

## API Endpoints

### Public Endpoints

- `GET /` - Home page
- `POST /exchange/create` - Create new exchange
- `GET /exchange/{id}` - View exchange (adaptive UI)
- `POST /exchange/{id}/respond` - Submit Player B's list
- `GET /exchange/{id}/status` - Check if complete (polling)
- `GET /health` - Health check

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

```bash
cd herald
pip install -r requirements.txt
uvicorn main:app --reload
```

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
- Nginx reverse proxy

## Monitoring

Check server health:
```bash
curl https://herald.squigleague.com/health
```

View resources (requires admin key):
```bash
curl "https://herald.squigleague.com/admin/resources?admin_key=YOUR_KEY"
```

Check for abusive IPs:
```bash
curl "https://herald.squigleague.com/admin/abuse-report?admin_key=YOUR_KEY&min_requests=100"
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
