# Release v0.3.0 - AoS Matchup Generation

## Features

### Squire Module - Battle Plan & Matchup System
- **Battle Plan Randomizer**: Generate random battle plans for Age of Sigmar (12 official missions from GH 2025-2026)
- **Matchup System**: Players can exchange army lists and get a randomized battle plan
  - Create matchup with unique ID
  - Both players submit lists anonymously
  - Lists revealed simultaneously with battle plan when both submitted

### API Endpoints

#### Battle Plan Generation
- `GET /api/squire/battle-plan/random` - Get single random battle plan
- `GET /api/squire/battle-plan/multiple` - Generate multiple battle plans (1-10)
- `GET /api/squire/systems` - List supported systems and deployments

#### Matchup System
- `POST /api/squire/matchup/create` - Create new matchup
- `POST /api/squire/matchup/{id}/submit` - Submit army list to matchup
- `GET /api/squire/matchup/{id}` - Get matchup status

## Deployment Steps

### Prerequisites
- Python 3.11+
- PostgreSQL 15+ (for Herald module)
- Docker (optional, for containerized deployment)

### Local Deployment
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

2. Set environment variables:
   ```bash
   DATABASE_URL=postgresql://user:password@localhost/squigleague
   ADMIN_API_KEY=your-secret-key
   ```

3. Start server:
   ```bash
   uvicorn herald.main:app --reload --port 8000
   ```

4. Access API docs:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Docker Deployment
```bash
docker-compose up -d
```

## Testing

### Manual Testing Checklist
- [ ] Battle plan randomizer returns valid AoS mission
- [ ] Can generate multiple battle plans
- [ ] Systems endpoint lists Age of Sigmar with 12 deployments
- [ ] Can create matchup and get unique ID
- [ ] First player submission returns waiting status
- [ ] Second player submission reveals both lists + battle plan
- [ ] Accessing matchup before both submissions hides lists

### Test Battle Plan Generation
```bash
curl http://localhost:8000/api/squire/battle-plan/random?system=age_of_sigmar
```

### Test Matchup Flow
1. Create matchup:
   ```bash
   curl -X POST http://localhost:8000/api/squire/matchup/create \
     -H "Content-Type: application/json" \
     -d '{"game_system": "age_of_sigmar"}'
   ```

2. Submit first list:
   ```bash
   curl -X POST http://localhost:8000/api/squire/matchup/{ID}/submit \
     -H "Content-Type: application/json" \
     -d '{"player_name": "Player 1", "army_list": "My army list..."}'
   ```

3. Submit second list:
   ```bash
   curl -X POST http://localhost:8000/api/squire/matchup/{ID}/submit \
     -H "Content-Type: application/json" \
     -d '{"player_name": "Player 2", "army_list": "My army list..."}'
   ```

4. Get matchup (should show both lists + battle plan):
   ```bash
   curl http://localhost:8000/api/squire/matchup/{ID}
   ```

## Version Info
- **Version**: 0.3.0
- **Release Date**: December 9, 2025
- **Branch**: release/v0.3.0-aos-matchups
- **Game Systems**: Age of Sigmar only
- **Missions**: 12 official GH 2025-2026 battle plans

## Known Limitations
- AoS only (40k and Old World missions coming in future releases)
- In-memory matchup storage (resets on server restart)
- No persistence for battle plans (generated on-demand)
- No authentication for matchup access (anyone with ID can view)

## Next Steps
- Add frontend UI for matchup system
- Implement persistent storage for matchups
- Add 40k and Old World battle plans
- Add matchup history and statistics
