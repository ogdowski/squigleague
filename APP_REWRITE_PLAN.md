# SquigLeague - Complete Rewrite Plan

> **Original Plan Document** - Stored for reference during migration
> **Date:** 2025-12-24
> **Branch:** feature/app-rewrite

---

## 1. Stack Technologiczny

### Backend
- **FastAPI** - framework API
- **SQLModel** - ORM + Pydantic schemas
- **FastAPI Users** - autoryzacja + SSO
- **FastAPI Permissions** - system uprawnień
- **PostgreSQL** - baza danych
- **Alembic** - migracje
- **HTTPX** - async HTTP client (BSData)
- **Nginx** - routing/reverse proxy
- **Docker + Docker Compose** - konteneryzacja

### Frontend
- **Vue 3** (Composition API)
- **Vue Router** - routing
- **Pinia** - state management
- **Vite** - bundler
- **Axios/ofetch** - API calls
- **TailwindCSS** - styling (dark/light mode)
- Kolory: czarno-żółte, minimalistyczny design

---

## 2. Struktura Projektu

```
squigleague/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── db.py
│   │   ├── core/           # Wspólne rzeczy
│   │   │   ├── __init__.py
│   │   │   ├── security.py
│   │   │   ├── deps.py
│   │   │   └── permissions.py
│   │   ├── users/          # Moduł użytkowników
│   │   │   ├── __init__.py
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   ├── routes.py
│   │   │   └── auth.py     # FastAPI Users config
│   │   ├── matchup/        # Moduł matchup
│   │   │   ├── __init__.py
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   ├── routes.py
│   │   │   └── service.py
│   │   ├── elo/            # Moduł ELO (osobny)
│   │   │   ├── __init__.py
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   ├── routes.py
│   │   │   ├── service.py
│   │   │   └── calculator.py
│   │   ├── leagues/        # Moduł lig
│   │   │   ├── __init__.py
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   ├── routes.py
│   │   │   ├── scoring.py  # Logika punktacji
│   │   │   └── formats.py  # Różne formaty lig
│   │   ├── data_importer/  # BSData importer (TODO: później)
│   │   │   ├── __init__.py
│   │   │   ├── models.py
│   │   │   ├── routes.py
│   │   │   └── bsdata.py   # Logika importu
│   │   ├── tournaments/    # Moduł turniejów (TODO: osobny moduł)
│   │   │   ├── __init__.py
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   └── routes.py
│   │   ├── list_builder/   # List builder (TODO: osobny moduł)
│   │   │   ├── __init__.py
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   └── routes.py
│   │   └── collections/    # Zarządzanie kolekcjami figurek (TODO: osobny moduł)
│   │       ├── __init__.py
│   │       ├── models.py
│   │       ├── schemas.py
│   │       └── routes.py
│   ├── alembic/
│   ├── nginx/
│   │   └── nginx.conf
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── main.js
│   │   ├── App.vue
│   │   ├── router/
│   │   │   └── index.js
│   │   ├── stores/
│   │   │   ├── auth.js
│   │   │   └── theme.js
│   │   ├── views/
│   │   │   ├── Matchup.vue
│   │   │   ├── MatchupView.vue
│   │   │   ├── Leagues.vue
│   │   │   ├── LeagueDetail.vue
│   │   │   ├── Leaderboard.vue
│   │   │   ├── Admin/          # Custom admin panel (dla adminów/organizatorów)
│   │   │   │   ├── Dashboard.vue
│   │   │   │   ├── Users.vue
│   │   │   │   ├── ELOSettings.vue
│   │   │   │   └── LeagueManagement.vue
│   │   │   ├── Tournaments.vue  # TODO: później
│   │   │   ├── ListBuilder.vue  # TODO: później
│   │   │   ├── Collections.vue  # TODO: dużo później - zarządzanie kolekcją figurek
│   │   │   ├── Rules.vue
│   │   │   ├── Login.vue
│   │   │   ├── Register.vue
│   │   │   └── Settings.vue
│   │   ├── components/
│   │   │   ├── Sidebar.vue
│   │   │   ├── ThemeToggle.vue
│   │   │   ├── LeagueTable.vue
│   │   │   ├── PlayoffBracket.vue
│   │   │   └── UserELOStats.vue
│   │   ├── assets/
│   │   └── styles/
│   │       └── main.css     # TailwindCSS + custom
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── Dockerfile
├── docker-compose.yml
└── justfile
```

---

## 3. Role i Uprawnienia

### Role użytkowników:
1. **Anonymous** - może używać matchup bez logowania (nie liczy się do ELO)
2. **Player** (default po rejestracji) - może grać w ligach, używać matchup, ma ELO
3. **Organizer** - może tworzyć i zarządzać ligami
4. **Admin** - pełen dostęp

### Permissions:
```python
# app/core/permissions.py
permissions = {
    "matchup.create": ["anonymous", "player", "organizer", "admin"],
    "matchup.view": ["anonymous", "player", "organizer", "admin"],
    "league.view": ["anonymous", "player", "organizer", "admin"],
    "league.create": ["organizer", "admin"],
    "league.manage_own": ["organizer", "admin"],  # tylko swoje ligi
    "league.manage_all": ["admin"],
    "league.delete": ["admin"],
    "users.manage": ["admin"],
    "data_importer.sync": ["admin"],
    "elo.view": ["anonymous", "player", "organizer", "admin"],  # Publiczne
    "elo.config": ["admin"],
}
```

---

## 4. Detailed Module Specifications

See [MIGRATION_PLAN.md](MIGRATION_PLAN.md) for detailed implementation plan.

### Key Modules:

#### 4.1 Users Module
- Google OAuth + Discord OAuth (both from start)
- No email notifications
- Roles: player, organizer, admin
- FastAPI Users integration

#### 4.2 Matchup Module
- Anonymous + logged users
- UUID-based links
- 7-day expiry
- Hardcoded maps (BSData later)
- Anonymous matchups DON'T count for ELO

#### 4.3 ELO Module
- 3 types: League, Tournament, Global
- Starting: 1000 points
- **K=50 for first 5 games**
- **Then K per global config (admin adjustable)**
- Public visibility
- Balance visible from game 1

#### 4.4 Leagues Module
- Group + playoff format
- Dynamic scoring system
- Tiebreakers: unplayed matches → avg points → ELO
- Auto ELO update (League + Global)

---

## 5. Implementation Phases

### Faza 1: Fundament ⭐
- Backend setup (FastAPI + SQLModel + Alembic)
- Frontend setup (Vue 3 + Tailwind)
- Users module (Google + Discord OAuth)
- Core module (deps, security, permissions)

**Deliverable:** Working OAuth login

### Faza 2: Matchup ⭐
- Matchup models + endpoints
- Anonymous support
- Hardcoded maps
- Frontend UI

**Deliverable:** End-to-end matchup

### Faza 3: ELO System ⭐
- ELO models + calculator
- Service layer (K-factor rules)
- Public leaderboards
- Admin config management

**Deliverable:** Complete ELO system

### Faza 4: Leagues - Podstawy ⭐
- League CRUD
- Group phase
- Result submission
- ELO integration

**Deliverable:** Playable leagues with ELO

### Faza 5: Leagues - Playoff ⭐
- Playoff bracket generation
- Locked lists
- Winner announcement

**Deliverable:** Complete league lifecycle

### Faza 6: Polish & Deploy ⭐
- Admin panel
- Rules page
- Settings
- Production deployment

**Deliverable:** Production-ready app

### Faza 7-12: Future Features 🔜
- Data Importer (BSData)
- Tournaments
- List Builder
- Collections
- Matchup extensions (score tracker, unit stats)

---

## 6. Technical Specifications

### ELO Calculation

```python
def calculate_expected_score(rating_a: int, rating_b: int) -> float:
    return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))

def calculate_new_rating(
    current_rating: int,
    opponent_rating: int,
    actual_score: float,  # 1.0 = win, 0.5 = draw, 0.0 = loss
    k_factor: int = 50,
) -> int:
    expected = calculate_expected_score(current_rating, opponent_rating)
    change = k_factor * (actual_score - expected)
    new_rating = current_rating + round(change)
    return max(0, new_rating)
```

### League Scoring

```python
def calculate_match_points(player_score: int, opponent_score: int) -> int:
    """
    - Wygrana: 1000 pkt
    - Remis: 600 pkt
    - Przegrana: 200 pkt
    - Bonus: (player_score - opponent_score + 50), max 100, min 0
    """
    if player_score > opponent_score:
        base = 1000
    elif player_score == opponent_score:
        base = 600
    else:
        base = 200
    
    bonus = min(100, max(0, (player_score - opponent_score) + 50))
    return base + bonus
```

### Tiebreakers (in order)
1. Fewer unplayed matches
2. Higher average points
3. Higher ELO

---

## 7. League Formats

```python
LEAGUE_FORMATS = {
    (8, 11): {
        "groups": 2,
        "advance_rule": "1st and 2nd from each group",
        "advance_count": 4,
        "playoff_name": "top4",
    },
    (12, 15): {
        "groups": 3,
        "advance_rule": "1st from each group + best 2nd",
        "advance_count": 4,
        "playoff_name": "top4",
    },
    (16, 19): {
        "groups": 4,
        "advance_rule": "1st and 2nd from each group",
        "advance_count": 8,
        "playoff_name": "top8",
    },
    (20, 23): {
        "groups": 5,
        "advance_rule": "1st from each group + 3 best 2nd places",
        "advance_count": 8,
        "playoff_name": "top8",
    },
    (24, 27): {
        "groups": 6,
        "advance_rule": "1st from each group + 2 best 2nd places",
        "advance_count": 8,
        "playoff_name": "top8",
    },
    (28, 31): {
        "groups": 7,
        "advance_rule": "1st from each group + best 2nd place",
        "advance_count": 8,
        "playoff_name": "top8",
    },
    (32, 48): {
        "groups": 8,
        "advance_rule": "1st and 2nd from each group",
        "advance_count": 16,
        "playoff_name": "top16",
    },
}
```

---

## 8. Environment Variables

```bash
# .env
# Database
DATABASE_URL=postgresql://squigleague:changeme@db:5432/squigleague
DB_PASSWORD=changeme

# JWT
SECRET_KEY=your-super-secret-key-change-in-production

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Discord OAuth
DISCORD_CLIENT_ID=your-discord-client-id
DISCORD_CLIENT_SECRET=your-discord-client-secret

# App
ENVIRONMENT=development
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:5173
```

---

## 9. Design Decisions

### ✅ Confirmed
- **SSO:** Google + Discord OAuth (both from start)
- **No emails:** No email notifications or verification
- **Admin:** Custom admin panel (multiple admins/organizers possible)
- **ELO:** Separate module, 3 types, public visibility
- **K-factor:** 50 for first 5 games, then configurable
- **Anonymous:** Matchup works, but NO ELO tracking
- **Global ELO:** Updated from all games (league + tournament)

### ❓ Future Decisions
- Discord bot/webhooks for notifications
- Collections module details
- Score tracker implementation
- Unit statistics tracking

---

## 10. References

- **Current repo:** https://github.com/ogdowski/squigleague
- **FastAPI Users:** https://fastapi-users.github.io/fastapi-users/
- **SQLModel:** https://sqlmodel.tiangolo.com/
- **Vue 3:** https://vuejs.org/
- **TailwindCSS:** https://tailwindcss.com/
- **BSData AoS:** https://github.com/BSData/age-of-sigmar-4th

---

## 11. Next Steps

See [MIGRATION_PLAN.md](MIGRATION_PLAN.md) for detailed action plan.

**Immediate:**
1. Create backend directory structure
2. Set up FastAPI + SQLModel foundation
3. Implement Users module with OAuth
4. Begin Matchup module migration

---

**Plan Version:** 1.0  
**Last Updated:** 2025-12-24  
**Status:** Ready for implementation
