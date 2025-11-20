# Squig League Database

## Overview
PostgreSQL database shared by all Squig League modules.

## Connection
- **Host:** postgres (Docker service name)
- **Port:** 5432
- **Database:** squigleague
- **User:** squig
- **Password:** Set in `.env` as `DB_PASSWORD`

## Schema Organization
- `core_*` tables: Shared authentication and user management
- `herald_*` tables: List exchange module 
- `scribe_*` tables: List builder 
- `patron_*` tables: Tournament platform 
- `keeper_*` tables: Collection manager
- `squire_*` tables: Battle tracker

## Accessing Database
```bash
# Connect via Docker
docker exec -it squig-postgres psql -U squig -d squigleague

# List tables
\dt

# Describe table
\d herald_exchanges

# Exit
\q
```

## Backup & Restore
```bash
# Backup
docker exec squig-postgres pg_dump -U squig squigleague > backup.sql

# Restore
docker exec -i squig-postgres psql -U squig squigleague < backup.sql
```

## Phase 1 (Herald)
Active tables:
- `core_users` (prepared, not used yet)
- `herald_exchanges`
- `herald_request_log`
