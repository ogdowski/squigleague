# SquigLeague - Plan Przepisania Aplikacji

## IMPLEMENTATION STATUS (Updated: 2025-12-29)

### ✅ COMPLETED (Phase 1 & 2)

#### Infrastructure
- ✅ Docker Compose setup (postgres, backend, frontend, nginx, certbot)
- ✅ Nginx reverse proxy configured (local: HTTP only, production: HTTPS ready)
- ✅ Environment files (.env, .env.local.example, .env.prod.example)
- ✅ Multi-stage Docker builds for both backend and frontend
- ✅ Health checks for all services

#### Backend (FastAPI + SQLModel)
- ✅ Project structure created
- ✅ FastAPI app with lifespan manager
- ✅ SQLModel engine with connection pooling
- ✅ Pydantic Settings for configuration
- ✅ CORS middleware configured
- ✅ **Users module**: Registration, Login, JWT authentication
  - ✅ bcrypt password hashing (direct, not via passlib)
  - ✅ OAuth models prepared (Google/Discord - not configured yet)
  - ✅ Role-based access control (anonymous, player, organizer, admin)
- ✅ **Matchup module** (Herald logic): FULLY FUNCTIONAL
  - ✅ Friendly matchup IDs (e.g., "mighty-dragon-3x7a") using Age of Sigmar themed words
  - ✅ Anonymous matchup creation
  - ✅ Blind list submission
  - ✅ Auto-reveal when both lists submitted
  - ✅ Random map assignment from hardcoded list
  - ✅ 7-day expiration
  - ✅ All endpoints tested and working

#### Frontend (Vue 3 + Vite + Tailwind)
- ✅ Vue 3 project with Composition API (`<script setup>`)
- ✅ Vite build configuration
- ✅ Tailwind CSS with custom theme (squig-green, dark mode)
- ✅ Vue Router with lazy-loaded routes
- ✅ Pinia store for authentication (localStorage + JWT)
- ✅ Axios configured with auth headers
- ✅ **Views implemented**:
  - ✅ Home (landing page)
  - ✅ Login/Register
  - ✅ MatchupCreate (with copy link button)
  - ✅ Matchup (submit lists + reveal)
- ✅ Responsive navbar with auth state

#### Testing & Verification
- ✅ Backend API fully tested via curl
- ✅ End-to-end matchup flow tested successfully
- ✅ Frontend build working correctly
- ✅ Full stack integration verified

### 🎯 CURRENT STATE

**Working Features:**
- Complete matchup flow (create → submit → reveal)
- User authentication (registration, login, JWT)
- Anonymous matchup support
- Friendly matchup IDs with Age of Sigmar theming
- Auto map randomization
- Frontend/backend integration via nginx

**Known Issues Resolved:**
- ✅ bcrypt/passlib compatibility → Switched to direct bcrypt
- ✅ Frontend white screen → Cleaned old files from public/ directory
- ✅ Nginx SSL errors → Separated nginx.conf (local) vs nginx.prod.conf (production)
- ✅ Environment variables → Removed ${ADMIN_IP} variable, using hardcoded IPs

**Not Yet Implemented (Future Phases):**
- [ ] OAuth providers (Google, Discord)
- [ ] Alembic migrations (currently using SQLModel.create_all())
- [ ] BSData integration for maps
- [ ] ELO system
- [ ] Leagues module
- [ ] Tournaments module
- [ ] List builder
- [ ] Collections

### 📁 ACTUAL PROJECT STRUCTURE

```
squig_league/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app
│   │   ├── config.py            # Pydantic settings
│   │   ├── db.py                # SQLModel engine
│   │   ├── core/
│   │   │   ├── security.py      # JWT + bcrypt (direct)
│   │   │   ├── deps.py          # Auth dependencies
│   │   │   └── permissions.py   # Role permissions map
│   │   ├── users/
│   │   │   ├── models.py        # User, OAuthAccount
│   │   │   ├── schemas.py       # Pydantic schemas
│   │   │   └── routes.py        # /auth/* endpoints
│   │   └── matchup/
│   │       ├── models.py        # Matchup model
│   │       ├── schemas.py       # Pydantic schemas
│   │       ├── routes.py        # /matchup/* endpoints
│   │       ├── service.py       # Business logic + map list
│   │       └── words.py         # Friendly ID generation
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── main.js
│   │   ├── App.vue              # Main app with navbar
│   │   ├── style.css            # Tailwind + custom classes
│   │   ├── router/
│   │   │   └── index.js         # Vue Router config
│   │   ├── stores/
│   │   │   └── auth.js          # Pinia auth store
│   │   └── views/
│   │       ├── Home.vue
│   │       ├── Login.vue
│   │       ├── Register.vue
│   │       ├── MatchupCreate.vue
│   │       └── Matchup.vue
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── nginx.conf               # Frontend nginx config
│   ├── Dockerfile
│   └── .env
├── nginx/
│   ├── nginx.conf               # Local (HTTP only)
│   └── nginx.prod.conf          # Production (HTTPS)
├── docker-compose.yml
├── docker-compose.prod.yml
├── justfile                     # Deployment commands
├── .env                         # Root env file
├── .env.prod                    # Production env
└── README.md
```

### 🔧 IMPORTANT IMPLEMENTATION DETAILS

#### Matchup ID Generation
- Uses `words.py` with Age of Sigmar themed adjectives + nouns + 4-char code
- Example: "mighty-dragon-3x7a", "exalted-seraphon-isfm"
- Stored in `Matchup.uuid` field (unique, indexed)
- DB still has `Matchup.id` as primary key

#### Password Hashing
- **Using bcrypt directly** (not via passlib) to avoid compatibility issues
- `bcrypt.hashpw()` for hashing, `bcrypt.checkpw()` for verification
- passlib removed from direct dependencies (fastapi-users still depends on it)

#### Frontend Build
- **CRITICAL**: `public/` directory must be empty or contain only static assets
- Old files in `public/` will overwrite built files during Vite build
- Built assets go to `dist/` which is copied to nginx container

#### Nginx Configuration
- **Local**: `nginx/nginx.conf` - HTTP only, no SSL
- **Production**: `nginx/nginx.prod.conf` - HTTPS with Let's Encrypt certs
- Routes: `/api/*` → backend, `/` → frontend
- Admin routes at `/admin/*` (IP restricted: 127.0.0.1, 172.16.0.0/12)

#### Database
- Using SQLModel's `create_all()` for now (auto-creates tables on startup)
- Alembic configured but not actively used yet
- PostgreSQL 16 with connection pooling (pool_size=5, max_overflow=10)

### 📝 DEPLOYMENT NOTES

**Local Development:**
```bash
docker-compose up -d
# Access: http://localhost
```

**Production Deployment:**
```bash
# Copy production nginx config
cp nginx/nginx.prod.conf nginx/nginx.conf

# Deploy using existing justfile commands
just release v2.0.0
```

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

## 4. Moduły - Szczegółowy Plan

### 4.1 Users (Priorytet 1)

**Funkcjonalność:**
- **Logowanie przez Google OAuth + Discord OAuth** (obydwa od początku)
- Profile użytkownika (username, email z OAuth, avatar)
- Role: player, organizer, admin
- **Brak wysyłania emaili z aplikacji** (no email notifications, no password reset emails)

**Modele:**
```python
from fastapi_users.db import SQLAlchemyBaseUserTable
from sqlmodel import Field, SQLModel
from typing import Optional
from datetime import datetime

class User(SQLAlchemyBaseUserTable[int], SQLModel, table=True):
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    username: str = Field(max_length=100, unique=True, index=True)
    hashed_password: str
    role: str = Field(default="player")  # player, organizer, admin
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False
    
    # OAuth fields (FastAPI Users automatic)
    oauth_accounts: list = []
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**SSO Setup:**
```python
# app/users/auth.py
from httpx_oauth.clients.google import GoogleOAuth2
from httpx_oauth.clients.discord import DiscordOAuth2

google_oauth_client = GoogleOAuth2(
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
)

discord_oauth_client = DiscordOAuth2(
    client_id=settings.DISCORD_CLIENT_ID,
    client_secret=settings.DISCORD_CLIENT_SECRET,
    scopes=["identify", "email"],
)
```

**Endpoints:**
- `GET /auth/me`
- `GET /auth/google/authorize` (redirect to Google)
- `GET /auth/google/callback`
- `GET /auth/discord/authorize` (redirect to Discord)
- `GET /auth/discord/callback`
- `POST /auth/jwt/logout`
- `PATCH /users/me`

---

### 4.2 Matchup (Priorytet 2) ✅ IMPLEMENTED

**Funkcjonalność:**
- Gracz 1 tworzy matchup, dostaje unikalny link
- Gracz 1 przesyła swoją listę (tekst lub plik)
- Gracz 2 używa linku, dodaje swoją listę
- Po dodaniu obu list: losowanie mapy (hardcoded na start, później z BSData)
- Obaj widzą listy przeciwnika + wylosowaną mapę
- Działa dla anonymous i zalogowanych
- **Anonymous matchupy NIE liczą się do ELO**
- Opcjonalnie: zapisywanie historii matchupów dla zalogowanych

**Przyszłe rozszerzenia (dużo później):**
- **Score Tracker** - live tracking wyników podczas gry
- **Unit Statistics** - statystyki unitów (średni dmg, survival rate, etc.)
- Integracja z Collections (używanie własnych figurek w matchup)

**Modele (ACTUAL IMPLEMENTATION):**
```python
from datetime import datetime, timedelta
from app.matchup.words import generate_matchup_id  # Age of Sigmar themed IDs

class Matchup(SQLModel, table=True):
    __tablename__ = "matchups"

    id: Optional[int] = Field(default=None, primary_key=True)
    # ⚠️ CHANGED: Using friendly IDs instead of UUID
    uuid: str = Field(
        default_factory=generate_matchup_id,  # e.g., "mighty-dragon-3x7a"
        unique=True,
        index=True,
        max_length=50
    )
    
    # Gracze (nullable dla anonymous)
    player1_id: Optional[int] = Field(default=None, foreign_key="users.id")
    player2_id: Optional[int] = Field(default=None, foreign_key="users.id")
    
    # Listy
    player1_list: Optional[str] = None
    player2_list: Optional[str] = None
    
    # Status
    player1_submitted: bool = False
    player2_submitted: bool = False
    
    # Mapa
    map_name: Optional[str] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime = Field(default_factory=lambda: datetime.utcnow() + timedelta(days=7))
    revealed_at: Optional[datetime] = None
```

**Endpoints:**
- `POST /matchup` - tworzy matchup, zwraca UUID
- `GET /matchup/{uuid}` - sprawdza status matchup
- `POST /matchup/{uuid}/submit` - dodaje listę (player1 lub player2)
- `GET /matchup/{uuid}/reveal` - zwraca obie listy + mapę (gdy oba submitted=True)
- `GET /matchup/history` - historia dla zalogowanego usera (optional)

**Flow:**
1. Player1: `POST /matchup` → otrzymuje link `https://squigleague.com/matchup/{uuid}`
2. Player1: `POST /matchup/{uuid}/submit` (body: {list: "..."})
3. Player1 wysyła link do Player2
4. Player2: otwiera link, widzi że Player1 już submitted
5. Player2: `POST /matchup/{uuid}/submit` (body: {list: "..."})
6. Backend: losuje mapę z hardcoded listy (później z BSData)
7. Obaj: `GET /matchup/{uuid}/reveal` → widzą obie listy + mapę

**Hardcoded mapy (na start):**
```python
# app/matchup/service.py
MAPS = [
    "Tectonic Interference",
    "Prove Your Mettle",
    "Negotiation",
    "Battle of the Pass",
    "The Vice",
    "Contest of Generals",
    # ... więcej map z GHB 2025/2026
]

import random

def draw_random_map() -> str:
    return random.choice(MAPS)
```

---

### 4.3 ELO System (Priorytet 3 - Osobny Moduł)

**Funkcjonalność:**
- 3 typy ELO: League, Tournament, Global
- Start: 1000 punktów
- **Nowi gracze: K=50 przez pierwsze 5 gier**
- **Po 5 grach: K wg globalnej konfiguracji (domyślnie 50, admin może zmienić)**
- **ELO jest publiczne - każdy może zobaczyć**
- **Bilans widoczny od pierwszej gry**
- **Anonymous matchupy NIE liczą się do ELO**
- League ELO: tylko mecze ligowe
- Tournament ELO: tylko mecze turniejowe
- Global ELO: wszystkie mecze (league + tournament)

**Modele:**

```python
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON
from typing import Optional
from datetime import datetime

class ELOConfig(SQLModel, table=True):
    """Konfiguracja systemu ELO - admin może zmieniać K-factor."""
    __tablename__ = "elo_configs"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)  # "league", "tournament", "global"
    k_factor: int = Field(default=50)  # 50, 40, 32, etc.
    is_active: bool = Field(default=True)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ELORating(SQLModel, table=True):
    """Rating gracza w danym systemie (League/Tournament/Global)."""
    __tablename__ = "elo_ratings"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    rating_type: str = Field(index=True)  # "league", "tournament", "global"
    
    # Current rating
    rating: int = Field(default=1000)
    
    # Stats
    games_played: int = Field(default=0)
    wins: int = Field(default=0)
    losses: int = Field(default=0)
    draws: int = Field(default=0)
    
    # Peak rating
    peak_rating: int = Field(default=1000)
    peak_date: Optional[datetime] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ELOHistory(SQLModel, table=True):
    """Historia zmian ELO - każda gra zapisuje zmianę."""
    __tablename__ = "elo_history"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    opponent_id: int = Field(foreign_key="users.id")
    rating_type: str = Field(index=True)  # "league", "tournament", "global"
    
    # Ratings before match
    old_rating: int
    opponent_old_rating: int
    
    # Match result
    result: str  # "win", "loss", "draw"
    
    # Ratings after match
    new_rating: int
    rating_change: int  # +/- delta
    
    # K-factor used
    k_factor: int
    
    # Optional: link do meczu
    match_id: Optional[int] = None
    match_type: Optional[str] = None  # "league" lub "tournament"
    
    # Timestamp
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

**Calculator (app/elo/calculator.py):**

```python
import math

def calculate_expected_score(rating_a: int, rating_b: int) -> float:
    """
    Oblicza oczekiwany wynik dla gracza A vs B.
    Zwraca wartość 0.0 - 1.0 (prawdopodobieństwo wygranej A).
    """
    return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))


def calculate_new_rating(
    current_rating: int,
    opponent_rating: int,
    actual_score: float,  # 1.0 = win, 0.5 = draw, 0.0 = loss
    k_factor: int = 50,
) -> int:
    """
    Oblicza nowy rating po meczu.
    
    Args:
        current_rating: Aktualny rating gracza
        opponent_rating: Rating przeciwnika
        actual_score: Faktyczny wynik (1.0, 0.5, 0.0)
        k_factor: K-factor
    
    Returns:
        Nowy rating (int)
    """
    expected = calculate_expected_score(current_rating, opponent_rating)
    change = k_factor * (actual_score - expected)
    new_rating = current_rating + round(change)
    
    # Rating nie może być < 0
    return max(0, new_rating)


def calculate_rating_change(
    current_rating: int,
    opponent_rating: int,
    actual_score: float,
    k_factor: int = 50,
) -> int:
    """
    Zwraca tylko zmianę ratingu (+/- delta).
    """
    new_rating = calculate_new_rating(current_rating, opponent_rating, actual_score, k_factor)
    return new_rating - current_rating
```

**Service (app/elo/service.py):**

```python
from sqlmodel import Session, select
from app.elo.models import ELORating, ELOHistory, ELOConfig
from app.elo.calculator import calculate_new_rating
from typing import Literal

ResultType = Literal["win", "draw", "loss"]

# KLUCZOWA REGUŁA: Nowi gracze mają K=50 przez pierwsze 5 gier
NEW_PLAYER_K_FACTOR = 50
NEW_PLAYER_GAMES_THRESHOLD = 5


def get_or_create_rating(
    session: Session,
    user_id: int,
    rating_type: str,
) -> ELORating:
    """Pobiera lub tworzy rating dla gracza."""
    statement = select(ELORating).where(
        ELORating.user_id == user_id,
        ELORating.rating_type == rating_type,
    )
    rating = session.exec(statement).first()
    
    if not rating:
        rating = ELORating(
            user_id=user_id,
            rating_type=rating_type,
            rating=1000,
        )
        session.add(rating)
        session.commit()
        session.refresh(rating)
    
    return rating


def get_k_factor(session: Session, rating_type: str, games_played: int) -> int:
    """
    Pobiera K-factor dla gracza.
    
    REGUŁA: Przez pierwsze 5 gier zawsze K=50, potem wg globalnej konfiguracji.
    """
    if games_played < NEW_PLAYER_GAMES_THRESHOLD:
        return NEW_PLAYER_K_FACTOR
    
    # Po 5 grach: używamy globalnej konfiguracji
    statement = select(ELOConfig).where(
        ELOConfig.name == rating_type,
        ELOConfig.is_active == True,
    )
    config = session.exec(statement).first()
    
    return config.k_factor if config else 50


def update_elo_after_match(
    session: Session,
    player1_id: int,
    player2_id: int,
    result: ResultType,  # z perspektywy player1
    rating_type: str,
    match_id: int | None = None,
    match_type: str | None = None,
) -> tuple[int, int]:
    """
    Aktualizuje ELO obu graczy po meczu.
    
    Args:
        session: DB session
        player1_id: ID gracza 1
        player2_id: ID gracza 2
        result: "win", "draw", "loss" (z perspektywy player1)
        rating_type: "league", "tournament", "global"
        match_id: Opcjonalne ID meczu
        match_type: Opcjonalnie typ meczu
    
    Returns:
        (player1_new_rating, player2_new_rating)
    """
    # Get current ratings
    p1_rating = get_or_create_rating(session, player1_id, rating_type)
    p2_rating = get_or_create_rating(session, player2_id, rating_type)
    
    # Get K-factors (uwzględniając pierwsze 5 gier)
    p1_k_factor = get_k_factor(session, rating_type, p1_rating.games_played)
    p2_k_factor = get_k_factor(session, rating_type, p2_rating.games_played)
    
    # Map result to scores
    score_map = {
        "win": (1.0, 0.0),
        "draw": (0.5, 0.5),
        "loss": (0.0, 1.0),
    }
    p1_score, p2_score = score_map[result]
    
    # Calculate new ratings
    p1_new = calculate_new_rating(
        p1_rating.rating,
        p2_rating.rating,
        p1_score,
        p1_k_factor,
    )
    p2_new = calculate_new_rating(
        p2_rating.rating,
        p1_rating.rating,
        p2_score,
        p2_k_factor,
    )
    
    # Update ratings
    p1_old = p1_rating.rating
    p2_old = p2_rating.rating
    
    p1_rating.rating = p1_new
    p2_rating.rating = p2_new
    
    # Update stats
    p1_rating.games_played += 1
    p2_rating.games_played += 1
    
    if result == "win":
        p1_rating.wins += 1
        p2_rating.losses += 1
    elif result == "loss":
        p1_rating.losses += 1
        p2_rating.wins += 1
    else:
        p1_rating.draws += 1
        p2_rating.draws += 1
    
    # Update peak rating
    if p1_new > p1_rating.peak_rating:
        p1_rating.peak_rating = p1_new
        p1_rating.peak_date = datetime.utcnow()
    
    if p2_new > p2_rating.peak_rating:
        p2_rating.peak_rating = p2_new
        p2_rating.peak_date = datetime.utcnow()
    
    # Save history
    p1_history = ELOHistory(
        user_id=player1_id,
        opponent_id=player2_id,
        rating_type=rating_type,
        old_rating=p1_old,
        opponent_old_rating=p2_old,
        result=result,
        new_rating=p1_new,
        rating_change=p1_new - p1_old,
        k_factor=p1_k_factor,
        match_id=match_id,
        match_type=match_type,
    )
    
    p2_result = "loss" if result == "win" else ("win" if result == "loss" else "draw")
    p2_history = ELOHistory(
        user_id=player2_id,
        opponent_id=player1_id,
        rating_type=rating_type,
        old_rating=p2_old,
        opponent_old_rating=p1_old,
        result=p2_result,
        new_rating=p2_new,
        rating_change=p2_new - p2_old,
        k_factor=p2_k_factor,
        match_id=match_id,
        match_type=match_type,
    )
    
    session.add(p1_history)
    session.add(p2_history)
    session.commit()
    
    return p1_new, p2_new


def get_leaderboard(
    session: Session,
    rating_type: str,
    limit: int = 100,
    min_games: int = 1,  # Pokazujemy od 1. gry
) -> list[ELORating]:
    """
    Zwraca ranking graczy.
    
    REGUŁA: Bilans widoczny od pierwszej gry (min_games=1).
    """
    statement = (
        select(ELORating)
        .where(
            ELORating.rating_type == rating_type,
            ELORating.games_played >= min_games,
        )
        .order_by(ELORating.rating.desc())
        .limit(limit)
    )
    return list(session.exec(statement).all())
```

**Endpoints:**
- `GET /elo/leaderboard/{rating_type}` - ranking (publiczny)
- `GET /elo/user/{user_id}` - ELO użytkownika (publiczne)
- `GET /elo/history/{user_id}` - historia zmian (publiczne)
- `GET /elo/config/{rating_type}` - konfiguracja (publiczne)
- `PATCH /elo/config/{rating_type}` - zmiana K-factor (admin only)

---

### 4.4 Leagues (Priorytet 4)

**Funkcjonalność:**
- Tworzenie lig przez organizatora
- Format: grupy + faza pucharowa (extensible dla innych formatów)
- Dynamiczna punktacja (configurable)
- Tiebreakers (w kolejności: unplayed matches, avg points, ELO)
- Zapisywanie wyników meczy
- **Po każdym meczu: update League ELO + Global ELO**
- Tabele grupowe + bracket pucharowy
- Historia lig
- Tylko ty (admin) możesz tworzyć ligi na start

**Modele:**
```python
from datetime import date

class League(SQLModel, table=True):
    __tablename__ = "leagues"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=200)
    season: str = Field(max_length=50)
    description: str
    
    # Organizator
    organizer_id: int = Field(foreign_key="users.id")
    
    # Format i config
    format_type: str = Field(default="group_playoff")  # extensible
    config: dict = Field(default={}, sa_column=Column(JSON))  # punktacja, tiebreakers, etc.
    
    # Status
    status: str = Field(default="draft")  # draft, registration, group_phase, playoff, finished
    
    # Daty
    start_date: date
    registration_deadline: date
    group_phase_end: Optional[date] = None
    end_date: Optional[date] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class LeagueParticipant(SQLModel, table=True):
    __tablename__ = "league_participants"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    league_id: int = Field(foreign_key="leagues.id")
    user_id: int = Field(foreign_key="users.id")
    
    # Grupy
    group_number: Optional[int] = None
    
    # Playoff
    eliminated: bool = False
    playoff_position: Optional[int] = None
    
    # Lista dla playoff (locked)
    playoff_list: Optional[str] = None
    
    # Metadata
    joined_at: datetime = Field(default_factory=datetime.utcnow)

class LeagueMatch(SQLModel, table=True):
    __tablename__ = "league_matches"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    league_id: int = Field(foreign_key="leagues.id")
    
    # Gracze
    player1_id: int = Field(foreign_key="users.id")
    player2_id: int = Field(foreign_key="users.id")
    
    # Faza
    phase: str  # "group", "playoff"
    round_number: int
    
    # Wyniki
    player1_score: Optional[int] = None  # Battle points (0-100)
    player2_score: Optional[int] = None
    player1_points: Optional[int] = None  # Punkty ligowe (wg systemu)
    player2_points: Optional[int] = None
    
    # Status
    played: bool = False
    played_at: Optional[datetime] = None
    deadline: datetime
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)

class LeagueStandings(SQLModel, table=True):
    __tablename__ = "league_standings"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    league_id: int = Field(foreign_key="leagues.id")
    user_id: int = Field(foreign_key="users.id")
    
    # Faza
    phase: str  # "group", "overall"
    group_number: Optional[int] = None
    
    # Statystyki
    total_points: int = 0
    matches_played: int = 0
    matches_total: int = 0  # Do obliczania niezagranych
    wins: int = 0
    draws: int = 0
    losses: int = 0
    
    # Ranking
    position: int = 0
    
    # Metadata
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Scoring System:**
```python
# app/leagues/scoring.py
def calculate_match_points(player_score: int, opponent_score: int) -> int:
    """
    Wylicza punkty ligowe dla gracza.
    
    - Wygrana: 1000 pkt
    - Remis: 600 pkt
    - Przegrana: 200 pkt
    - Bonus: (player_score - opponent_score + 50), max 100, min 0
    
    Przykład:
    - Wynik 72-68: 1000 + 54 = 1054 pkt
    - Wynik 68-72: 200 + 46 = 246 pkt
    """
    if player_score > opponent_score:
        base = 1000
    elif player_score == opponent_score:
        base = 600
    else:
        base = 200
    
    bonus = min(100, max(0, (player_score - opponent_score) + 50))
    return base + bonus

def calculate_tiebreakers(league_id: int, user_id: int, session: Session) -> dict:
    """
    Tiebreakers (w kolejności):
    1. Mniej niezagranych meczy
    2. Wyższa średnia punktów
    3. Wyższe ELO
    """
    from app.elo.service import get_or_create_rating
    
    # Get standings
    statement = select(LeagueStandings).where(
        LeagueStandings.league_id == league_id,
        LeagueStandings.user_id == user_id,
    )
    standing = session.exec(statement).first()
    
    unplayed = standing.matches_total - standing.matches_played
    avg_points = standing.total_points / standing.matches_played if standing.matches_played > 0 else 0
    
    # Get ELO
    elo_rating = get_or_create_rating(session, user_id, "league")
    
    return {
        "unplayed_matches": unplayed,
        "avg_points": avg_points,
        "elo": elo_rating.rating,
    }
```

**Format ligi:**
```python
# app/leagues/formats.py
from typing import Tuple

LEAGUE_FORMATS: dict[Tuple[int, int], dict] = {
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

def determine_format(num_players: int) -> dict:
    """Zwraca format ligi na podstawie liczby graczy."""
    for (min_p, max_p), config in LEAGUE_FORMATS.items():
        if min_p <= num_players <= max_p:
            return config
    raise ValueError(f"Unsupported number of players: {num_players}")
```

**Integracja z ELO:**
```python
# app/leagues/routes.py (fragment)
from app.elo.service import update_elo_after_match

@router.post("/leagues/{league_id}/matches/{match_id}/result")
def submit_match_result(
    league_id: int,
    match_id: int,
    result: MatchResultSubmit,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    """Wpisanie wyniku meczu ligowego."""
    match = session.get(LeagueMatch, match_id)
    
    # ... validation ...
    
    # Update match
    match.player1_score = result.player1_score
    match.player2_score = result.player2_score
    match.played = True
    match.played_at = datetime.utcnow()
    
    # Calculate league points
    from app.leagues.scoring import calculate_match_points
    match.player1_points = calculate_match_points(result.player1_score, result.player2_score)
    match.player2_points = calculate_match_points(result.player2_score, result.player1_score)
    
    # ... update standings ...
    
    # ===== UPDATE ELO =====
    # Determine result from player1 perspective
    if result.player1_score > result.player2_score:
        elo_result = "win"
    elif result.player1_score < result.player2_score:
        elo_result = "loss"
    else:
        elo_result = "draw"
    
    # Update League ELO
    update_elo_after_match(
        session=session,
        player1_id=match.player1_id,
        player2_id=match.player2_id,
        result=elo_result,
        rating_type="league",
        match_id=match_id,
        match_type="league",
    )
    
    # Update Global ELO (każda gra liczy się do Global)
    update_elo_after_match(
        session=session,
        player1_id=match.player1_id,
        player2_id=match.player2_id,
        result=elo_result,
        rating_type="global",
        match_id=match_id,
        match_type="league",
    )
    
    session.commit()
    
    return {"message": "Match result submitted and ELO updated"}
```

**Endpoints:**
- `POST /leagues` - tworzy ligę (organizer only)
- `GET /leagues` - lista lig (publiczne + własne)
- `GET /leagues/{id}` - szczegóły ligi
- `POST /leagues/{id}/join` - dołączanie gracza
- `POST /leagues/{id}/start` - rozpoczęcie ligi, generuje grupy (organizer)
- `POST /leagues/{id}/start-playoff` - start playoff, generuje bracket (organizer)
- `POST /leagues/{id}/matches/{match_id}/result` - wpisanie wyniku
- `GET /leagues/{id}/standings` - tabela (grupowa lub playoff)
- `GET /leagues/{id}/bracket` - drabinka playoff
- `PATCH /leagues/{id}` - edycja ligi (organizer)
- `DELETE /leagues/{id}` - usunięcie ligi (admin only)

---

### 4.5 Data Importer (Priorytet 5 - TODO później)

**Funkcjonalność:**
- Pobiera dane JSON z BSData repository (GitHub)
- Parsuje mapy, scenariusze
- Zapisuje w bazie
- Endpoint do manualnego triggera (tylko admin)
- Opcjonalnie: cron job co tydzień

**Modele:**
```python
class GameMap(SQLModel, table=True):
    __tablename__ = "game_maps"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=200)
    source: str = Field(default="BSData")
    map_data: dict = Field(default={}, sa_column=Column(JSON))
    imported_at: datetime = Field(default_factory=datetime.utcnow)
```

**Endpoints:**
- `POST /data-importer/sync` (admin only) - trigger sync
- `GET /data-importer/maps` - lista map
- `GET /data-importer/status` - ostatni sync info

**BSData:**
- Repository: https://github.com/BSData/age-of-sigmar-4th
- TODO: określić strukturę danych po analizie repo

---

### 4.6 Tournaments (TODO - osobny moduł)

**Funkcjonalność:**
- Single-elimination lub Swiss
- Brak fazy grupowej
- Krótsza forma niż ligi
- Pairing w Swiss
- **Tournament ELO tracking**
- **Global ELO update po każdej grze**

**Modele:**
```python
# TODO: Design later
class Tournament(SQLModel, table=True):
    pass

class TournamentMatch(SQLModel, table=True):
    pass
```

---

### 4.7 List Builder (TODO - osobny moduł)

**Funkcjonalność:**
- Tworzenie list armijnych dla zalogowanych
- Walidacja punktów
- Zapisywanie/edycja list
- Eksport do PDF/text

**Modele:**
```python
# TODO: Design later
class ArmyList(SQLModel, table=True):
    pass

class ListUnit(SQLModel, table=True):
    pass
```

---

### 4.8 Collections (TODO - dużo później, osobny moduł)

**Funkcjonalność:**
- Zarządzanie kolekcją figurek użytkownika
- Katalog modeli (painted/unpainted)
- Tracking co masz vs co potrzebujesz
- Integracja z List Builder (zaznaczanie co już masz)
- Gallery (zdjęcia malowanych armii)
- Wishlist

**Modele:**
```python
# TODO: Design later
class Collection(SQLModel, table=True):
    """Kolekcja użytkownika."""
    id: Optional[int]
    user_id: int
    name: str  # np. "My Seraphon Army"

class CollectionUnit(SQLModel, table=True):
    """Unit w kolekcji."""
    id: Optional[int]
    collection_id: int
    unit_name: str
    quantity: int
    painted: bool
    image_url: Optional[str]
```

---

### 4.9 Matchup Extensions (TODO - dużo później)

**Score Tracker:**
- Live tracking wyników podczas gry
- Round-by-round VP tracking
- Battle tactics completion
- Real-time synchronizacja między graczami

**Unit Statistics:**
- Tracking performance unitów w meczach
- Średni damage dealt/received
- Survival rate
- Kill count
- Heat maps (gdzie unit był najbardziej efektywny)

**Modele:**
```python
# TODO: Design later
class MatchupScoreTracker(SQLModel, table=True):
    """Live tracking wyników."""
    id: Optional[int]
    matchup_id: int
    round_number: int
    player1_vp: int
    player2_vp: int
    timestamp: datetime

class UnitStatistics(SQLModel, table=True):
    """Statystyki jednostki w meczach."""
    id: Optional[int]
    user_id: int
    unit_name: str
    games_played: int
    avg_damage_dealt: float
    avg_damage_received: float
    survival_rate: float  # % gier gdzie przeżył
    kills: int
```

---

### 4.10 Core (Utilities)

**Funkcjonalność:**
- Dependency injection (get_session, get_current_user)
- Permissions helpers
- Security utilities
- Response models
- Exceptions

```python
# app/core/deps.py
from fastapi import Depends, HTTPException, status
from sqlmodel import Session
from app.db import get_session
from app.users.models import User
import fastapi_users

def get_current_active_user(
    current_user: User = Depends(fastapi_users.current_user())
) -> User:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

def require_role(*allowed_roles: str):
    """
    Dependency do sprawdzania roli użytkownika.
    
    Usage:
        @app.get("/admin", dependencies=[Depends(require_role("admin"))])
    """
    def role_checker(user: User = Depends(get_current_active_user)):
        if user.role not in allowed_roles and user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return user
    return role_checker

def get_current_organizer(user: User = Depends(require_role("organizer", "admin"))):
    return user

def get_current_admin(user: User = Depends(require_role("admin"))):
    return user
```

---

## 5. Frontend - Szczegóły

### Layout
```
┌──────────────────────────────────────────┐
│ Sidebar (pionowy, lewy, czarno-żółty)    │
├────────────┬─────────────────────────────┤
│            │                             │
│  Logo      │                             │
│  (Yellow)  │    Main Content             │
│            │    (Dark bg)                │
│ ────────── │                             │
│            │                             │
│ Matchup    │                             │
│ Leagues    │                             │
│ Leaderboard│                             │
│ Rules      │                             │
│ (Collections - later)                    │
│            │                             │
│ ────────── │                             │
│            │                             │
│ Login      │                             │
│ Settings   │                             │
│            │                             │
└────────────┴─────────────────────────────┘
```

### Router
```javascript
// router/index.js
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', redirect: '/matchup' },
  { path: '/matchup', component: () => import('@/views/Matchup.vue') },
  { path: '/matchup/:uuid', component: () => import('@/views/MatchupView.vue') },
  { path: '/leagues', component: () => import('@/views/Leagues.vue') },
  { path: '/leagues/:id', component: () => import('@/views/LeagueDetail.vue') },
  { path: '/leaderboard', component: () => import('@/views/Leaderboard.vue') },
  { path: '/rules', component: () => import('@/views/Rules.vue') },
  { path: '/login', component: () => import('@/views/Login.vue') },
  { path: '/register', component: () => import('@/views/Register.vue') },
  { path: '/settings', component: () => import('@/views/Settings.vue'), meta: { requiresAuth: true } },
  
  // Collections (TODO: dużo później)
  // { path: '/collections', component: () => import('@/views/Collections.vue'), meta: { requiresAuth: true } },
  
  // Custom Admin Panel (tylko dla adminów/organizatorów)
  { 
    path: '/admin', 
    component: () => import('@/views/Admin/Dashboard.vue'), 
    meta: { requiresAuth: true, requiresRole: ['admin', 'organizer'] } 
  },
  { 
    path: '/admin/users', 
    component: () => import('@/views/Admin/Users.vue'), 
    meta: { requiresAuth: true, requiresRole: ['admin'] } 
  },
  { 
    path: '/admin/elo', 
    component: () => import('@/views/Admin/ELOSettings.vue'), 
    meta: { requiresAuth: true, requiresRole: ['admin'] } 
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Auth guard
router.beforeEach((to, from, next) => {
  const isAuthenticated = localStorage.getItem('token')
  
  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login')
  } else {
    next()
  }
})

export default router
```

### Theme (TailwindCSS)
```javascript
// tailwind.config.js
module.exports = {
  darkMode: 'class', // Default: dark
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#FFD700',  // Yellow/Gold
          dark: '#FFA500',     // Orange-yellow
          light: '#FFED4E',
        },
        background: {
          light: '#FFFFFF',
          dark: '#0A0A0A',     // Near black
        },
        surface: {
          light: '#F5F5F5',
          dark: '#1A1A1A',     // Dark gray
        },
        text: {
          light: '#0A0A0A',
          dark: '#F5F5F5',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      }
    }
  },
  plugins: [],
}
```

### Login View (Google + Discord OAuth)
```vue
<!-- views/Login.vue -->
<template>
  <div class="login-container">
    <h1>Login to SquigLeague</h1>
    
    <!-- SSO Buttons -->
    <button @click="loginWithGoogle" class="btn-google">
      <GoogleIcon /> Continue with Google
    </button>
    
    <button @click="loginWithDiscord" class="btn-discord">
      <DiscordIcon /> Continue with Discord
    </button>
  </div>
</template>

<script setup>
const loginWithGoogle = () => {
  window.location.href = '/api/auth/google/authorize'
}

const loginWithDiscord = () => {
  window.location.href = '/api/auth/discord/authorize'
}
</script>
```

### Leaderboard View
```vue
<!-- views/Leaderboard.vue -->
<template>
  <div class="leaderboard">
    <h1>ELO Rankings</h1>
    
    <div class="tabs">
      <button @click="selectedType = 'league'" :class="{ active: selectedType === 'league' }">
        League ELO
      </button>
      <button @click="selectedType = 'tournament'" :class="{ active: selectedType === 'tournament' }">
        Tournament ELO
      </button>
      <button @click="selectedType = 'global'" :class="{ active: selectedType === 'global' }">
        Global ELO
      </button>
    </div>
    
    <div class="leaderboard-table">
      <table>
        <thead>
          <tr>
            <th>Rank</th>
            <th>Player</th>
            <th>Rating</th>
            <th>Games</th>
            <th>W-D-L</th>
            <th>Win Rate</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(rating, index) in ratings" :key="rating.id">
            <td>{{ index + 1 }}</td>
            <td>{{ rating.user.username }}</td>
            <td class="rating">{{ rating.rating }}</td>
            <td>{{ rating.games_played }}</td>
            <td>{{ rating.wins }}-{{ rating.draws }}-{{ rating.losses }}</td>
            <td>{{ calculateWinRate(rating) }}%</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import axios from 'axios'

const selectedType = ref('league')
const ratings = ref([])

const fetchLeaderboard = async () => {
  const response = await axios.get(`/api/elo/leaderboard/${selectedType.value}`)
  ratings.value = response.data.ratings
}

const calculateWinRate = (rating) => {
  if (rating.games_played === 0) return 0
  return ((rating.wins / rating.games_played) * 100).toFixed(1)
}

watch(selectedType, fetchLeaderboard)
onMounted(fetchLeaderboard)
</script>
```

---

## 6. Requirements.txt

```txt
# FastAPI
fastapi==0.109.0
uvicorn[standard]==0.27.0

# Database
sqlmodel==0.0.14
psycopg2-binary==2.9.9
alembic==1.13.1

# Auth
fastapi-users[sqlalchemy]==12.1.3
httpx-oauth==0.13.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4

# Permissions
fastapi-permissions==0.2.7

# Utils
httpx==0.26.0
pydantic[email]==2.5.3
python-dotenv==1.0.0
python-multipart==0.0.6

# Dev
pytest==7.4.3
black==23.12.1
isort==5.13.2
```

---

## 7. Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: squigleague
      POSTGRES_PASSWORD: ${DB_PASSWORD:-changeme}
      POSTGRES_DB: squigleague
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U squigleague"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build: ./backend
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    volumes:
      - ./backend:/app
    environment:
      DATABASE_URL: postgresql://squigleague:${DB_PASSWORD:-changeme}@db:5432/squigleague
      SECRET_KEY: ${SECRET_KEY:-change-me-in-production}
      GOOGLE_CLIENT_ID: ${GOOGLE_CLIENT_ID}
      GOOGLE_CLIENT_SECRET: ${GOOGLE_CLIENT_SECRET}
      DISCORD_CLIENT_ID: ${DISCORD_CLIENT_ID}
      DISCORD_CLIENT_SECRET: ${DISCORD_CLIENT_SECRET}
      ENVIRONMENT: ${ENVIRONMENT:-development}
    depends_on:
      db:
        condition: service_healthy
    ports:
      - "8000:8000"

  frontend:
    build: ./frontend
    command: npm run dev -- --host 0.0.0.0
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      VITE_API_URL: http://localhost/api
    ports:
      - "5173:5173"

  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
    ports:
      - "80:80"
    depends_on:
      - backend
      - frontend

volumes:
  postgres_data:
```

---

## 8. Nginx Config

```nginx
# nginx/nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:5173;
    }

    server {
        listen 80;
        server_name localhost squigleague.com;

        # Backend API
        location /api/ {
            proxy_pass http://backend/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # FastAPI docs
        location /docs {
            proxy_pass http://backend/docs;
            proxy_set_header Host $host;
        }

        location /redoc {
            proxy_pass http://backend/redoc;
            proxy_set_header Host $host;
        }

        # Frontend SPA
        location / {
            proxy_pass http://frontend/;
            proxy_set_header Host $host;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }
    }
}
```

---

## 9. Justfile

```makefile
# justfile
set dotenv-load := true

# Default recipe
default:
    @just --list

# Development
dev:
    docker-compose up

dev-build:
    docker-compose up --build

down:
    docker-compose down

down-volumes:
    docker-compose down -v

# Database
migrate:
    docker-compose exec backend alembic upgrade head

migrate-create MESSAGE:
    docker-compose exec backend alembic revision --autogenerate -m "{{MESSAGE}}"

migrate-rollback:
    docker-compose exec backend alembic downgrade -1

db-reset:
    docker-compose down -v
    docker-compose up -d db
    sleep 5
    just migrate

# Backend
backend-shell:
    docker-compose exec backend bash

backend-test:
    docker-compose exec backend pytest

backend-format:
    docker-compose exec backend black app/
    docker-compose exec backend isort app/

# Frontend
frontend-shell:
    docker-compose exec frontend sh

frontend-test:
    docker-compose exec frontend npm run test

frontend-lint:
    docker-compose exec frontend npm run lint

# Logs
logs SERVICE="":
    docker-compose logs -f {{SERVICE}}

# Production
prod-build:
    docker-compose -f docker-compose.prod.yml build

prod-up:
    docker-compose -f docker-compose.prod.yml up -d

prod-down:
    docker-compose -f docker-compose.prod.yml down

# Clean
clean:
    find . -type d -name __pycache__ -exec rm -rf {} +
    find . -type f -name "*.pyc" -delete
    docker-compose down -v --remove-orphans
```

---

## 10. Plan Implementacji (Fazy)

### **Faza 1: Fundament** (Tydzień 1-2) ⭐
**Cel:** Działające logowanie przez Google + Discord OAuth

1. Setup projektu (Docker, Git, .env)
2. Backend: FastAPI + SQLModel + Alembic
3. Frontend: Vue 3 + Router + Tailwind (dark mode default)
4. Database: PostgreSQL + migracje
5. Users module:
   - FastAPI Users integration
   - User model
   - **Google OAuth setup**
   - **Discord OAuth setup**
   - Auth endpoints
   - Role system (player, organizer, admin)
6. Core module:
   - Dependencies (get_session, get_current_user)
   - Permissions helpers
   - require_role decorators

**Deliverable:** 
✅ Działające logowanie przez Google OAuth + Discord OAuth
✅ Protected routes
✅ Role-based access control

---

### **Faza 2: Matchup** (Tydzień 3) ⭐
**Cel:** Działający matchup end-to-end

1. Backend: modele + endpoints
2. Frontend: UI (create, submit, reveal)
3. Flow implementation (UUID, submit, reveal)
4. Hardcoded mapy
5. Expiry mechanism (7 dni)
6. **Anonymous support (nie liczy się do ELO)**

**Deliverable:**
✅ Matchup działa dla anonymous i zalogowanych
✅ Anonymous nie ma ELO tracking

---

### **Faza 3: ELO System** (Tydzień 4) ⭐
**Cel:** Kompletny system ELO

1. ELO module models (ELORating, ELOHistory, ELOConfig)
2. Calculator (expected score, new rating)
3. Service layer:
   - **K=50 przez pierwsze 5 gier**
   - **Potem K wg globalnej konfiguracji**
   - Update after match
4. Endpoints (leaderboard, user stats, config)
5. Frontend:
   - Leaderboard view (3 tabs: League, Tournament, Global)
   - User ELO stats component
   - **Publiczny dostęp**
   - **Bilans od 1. gry**
6. Admin panel - K-factor management

**Deliverable:**
✅ Działający system ELO (3 typy)
✅ Publiczne leaderboardy
✅ Admin może zmieniać K-factor

---

### **Faza 4: Leagues - Podstawy** (Tydzień 5-6) ⭐
**Cel:** Można stworzyć ligę i rozegrać fazę grupową

1. League models (League, Participant, Match, Standings)
2. CRUD dla lig (tylko organizer może tworzyć)
3. Join league
4. Generowanie grup (losowo, wg formatu)
5. Faza grupowa (round-robin, deadline per match)
6. Wpisywanie wyników:
   - Scoring system
   - **Update League ELO**
   - **Update Global ELO**
   - Standings calculation
7. Frontend:
   - Leagues list
   - League detail
   - Group tables
   - Submit result form

**Deliverable:**
✅ Organizer może stworzyć ligę
✅ Gracze mogą dołączyć i grać
✅ Wyniki aktualizują standings + ELO

---

### **Faza 5: Leagues - Playoff** (Tydzień 7) ⭐
**Cel:** Pełny cykl ligi (grupy + playoff)

1. Logika awansu z grup (tiebreakers)
2. Generowanie drabinki playoff (seeding)
3. Playoff flow (locked lists, single elimination)
4. Frontend:
   - Playoff bracket visualization
   - Winner announcement

**Deliverable:**
✅ Liga kończy się z wynikami
✅ Playoff bracket działa

---

### **Faza 6: Polish & Deploy** (Tydzień 8) ⭐
**Cel:** Aplikacja w produkcji

1. Rules page (markdown renderer)
2. Settings (theme toggle, password change)
3. **Custom Admin Panel:**
   - Dashboard (stats overview)
   - Users management (promote to organizer, ban, etc.)
   - ELO config (K-factor settings)
   - League management
4. Error handling (global handlers)
5. Testing (pytest + vitest critical paths)
6. Justfile optimization
7. Production deploy (Docker, Nginx, SSL)

**Deliverable:**
✅ Stabilna aplikacja w produkcji
✅ Custom admin panel dla zarządzania

---

### **Faza 7: Data Importer** (Tydzień 9 - TODO) 🔜
**Cel:** Matchup używa prawdziwych map z BSData

1. BSData parser (analyze repo structure)
2. Import maps do DB
3. Admin endpoint (manual sync)
4. Integration z matchup (replace hardcoded)

**Deliverable:**
✅ Mapy z BSData w matchup

---

### **Faza 8: Tournaments** (TODO - osobny moduł) 🔜
- Swiss pairing
- Single elimination
- Tournament ELO tracking
- Global ELO update

---

### **Faza 9: List Builder** (TODO - osobny moduł) 🔜
- Army list creation
- Points validation
- Save/edit lists
- Export to PDF

---

### **Faza 10: Collections** (TODO - dużo później) 🔮
- Zarządzanie kolekcją figurek
- Painted/unpainted tracking
- Gallery zdjęć
- Wishlist
- Integracja z List Builder

---

### **Faza 11: Matchup Extensions** (TODO - dużo później) 🔮
- **Score Tracker:**
  - Live tracking VP round-by-round
  - Battle tactics completion
  - Real-time sync między graczami
- **Unit Statistics:**
  - Damage dealt/received tracking
  - Survival rates
  - Kill counts
  - Performance heat maps

---

## 11. Zasady Ligi (do Rules page)

### Pierwsza liga - Szczegóły

**Rozpoczęcie:** 2 lutego 2025

**Zasady:**
- Age of Sigmar 4. Edycja
- 2000 pkt
- GHB 2025/2026
- Stoły 60"x44"
- Dozwolone proxy i zamienniki modeli, o ile przeciwnik rozpozna co jest czym

**Format:**
- **Faza grupowa:**
  - 3-5 meczy zależnie od ilości graczy
  - 2 tygodnie per mecz, 6-8 tygodni na rozegranie
  - Gracze przydzieleni do grup losowo (od 2. sezonu: wg ELO)
  - Dowolna zmiana armii i listy z meczu na mecz
  - Gramy każdy z każdym w grupie w dowolnej kolejności
  - Gracz może nie zagrać 1 gry (więcej = niższy ranking)

- **Faza pucharowa:**
  - 2-3 mecze zależnie od ilości graczy
  - 2 tygodnie na mecz, 4-6 tygodni total
  - Najwyższy ranking gra z najniższym, itd.
  - Zwycięzca przechodzi dalej
  - W remisie: tiebreakery
  - Jedna lista (locked), podana przed startem fazy

**Tabela format (ilość graczy → grupy → awans):**
```
+---------+-------+-------------------------------------+-----------+
| Gracze  | Grupy | Zasady Awansu                       | Faza Puch.|
+---------+-------+-------------------------------------+-----------+
|  8-11   |   2   | 1. i 2. miejsca                     |   Top 4   |
| 12-15   |   3   | 1. miejsca + najlepsze 2. miejsce   |   Top 4   |
| 16-19   |   4   | 1. i 2. miejsca                     |   Top 8   |
| 20-23   |   5   | 1. miejsca + 3 najlepsze 2. miejsca |   Top 8   |
| 24-27   |   6   | 1. miejsca + 2 najlepsze 2. miejsca |   Top 8   |
| 28-31   |   7   | 1. miejsca + najlepsze 2. miejsce   |   Top 8   |
| 32-48   |   8   | 1. i 2. miejsca                     |   Top 16  |
+---------+-------+-------------------------------------+-----------+
```

**FAQ i Erraty:**
- Faza grupowa: dokumenty GW na dzień przed meczem
- Jeśli lista staje się nielegalna: obaj mogą zmienić
- Faza pucharowa: dokumenty GW na dzień przed deadline list

**Punktacja:**
- Wygrana: 1000 pkt
- Remis: 600 pkt
- Przegrana: 200 pkt
- Bonus: (twój_wynik - wynik_przeciwnika + 50), max 100, min 0

Przykład:
- Wynik 72-68: 1000 + 54 = 1054 pkt
- Wynik 68-72: 200 + 46 = 246 pkt

**Tiebreakery (w kolejności):**
1. Mniej niezagranych meczy grupowych (im mniej tym lepiej)
2. Wyższa średnia punktów w sezonie
3. Wyższe ELO gracza (od 2. sezonu)

---

## 12. ELO System - Szczegóły

### Reguły ELO:

1. **Typy ELO:**
   - **League ELO** - tylko mecze ligowe
   - **Tournament ELO** - tylko mecze turniejowe
   - **Global ELO** - wszystkie mecze (league + tournament)

2. **Punkty startowe:** 1000

3. **K-factor:**
   - **Nowi gracze:** K=50 przez pierwsze 5 gier (we wszystkich typach)
   - **Po 5 grach:** K wg globalnej konfiguracji (domyślnie 50)
   - **Admin może zmienić:** K=40, 32, 20, etc. (dla doświadczonych graczy)

4. **Widoczność:**
   - **ELO jest publiczne** - każdy może zobaczyć rankingi
   - **Bilans widoczny od 1. gry** - nie ma min. gier do leaderboardu

5. **Co się NIE liczy do ELO:**
   - **Anonymous matchupy** - brak weryfikacji tożsamości

6. **Aktualizacja ELO:**
   - Po każdym meczu ligowym: +League ELO, +Global ELO
   - Po każdym meczu turniejowym: +Tournament ELO, +Global ELO

### Przykład kalkulacji:

Gracz A (1200 ELO) vs Gracz B (1000 ELO):

**Expected score:**
- A: 1 / (1 + 10^((1000-1200)/400)) = 0.76
- B: 1 / (1 + 10^((1200-1000)/400)) = 0.24

**Jeśli A wygra (K=50):**
- A: 1200 + 50 * (1.0 - 0.76) = 1212 (+12)
- B: 1000 + 50 * (0.0 - 0.24) = 988 (-12)

**Jeśli B wygra (K=50):**
- A: 1200 + 50 * (0.0 - 0.76) = 1162 (-38)
- B: 1000 + 50 * (1.0 - 0.24) = 1038 (+38)

---

## 13. Environment Variables

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

## 14. Inicjalizacja Bazy Danych

### Alembic migration - ELO configs:

```python
# alembic/versions/xxx_init_elo_configs.py
def upgrade():
    # Insert default configs
    op.execute("""
        INSERT INTO elo_configs (name, k_factor, is_active, created_at, updated_at)
        VALUES 
            ('league', 50, true, NOW(), NOW()),
            ('tournament', 50, true, NOW(), NOW()),
            ('global', 50, true, NOW(), NOW())
        ON CONFLICT (name) DO NOTHING;
    """)

def downgrade():
    op.execute("DELETE FROM elo_configs WHERE name IN ('league', 'tournament', 'global');")
```

---

## 15. Pytania & Decyzje - FINALNE

### ✅ Resolved:
- **SSO:** Google OAuth + Discord OAuth (obydwa od początku)
- **Brak wysyłania emaili z aplikacji** (no email notifications)
- **Admin panel:** Custom (może być więcej adminów/organizatorów)
- **ELO:** Osobny moduł
- **ELO types:** League, Tournament, Global
- **Starting ELO:** 1000
- **K-factor:** K=50 przez pierwsze 5 gier, potem globalny (admin może zmienić)
- **ELO visibility:** Publiczne
- **Leaderboard min games:** 1 (bilans od pierwszej gry)
- **Anonymous matchup:** NIE liczy się do ELO
- **Global ELO:** Liczy się z każdej gry (league + tournament)

### Pozostałe do ustalenia później:
- ❓ Discord webhooks/bot integration (przyszłość - notyfikacje)
- ❓ Custom admin panel design details (może być więcej adminów/organizatorów)
- ❓ **Collections module** - zarządzanie kolekcją figurek (dużo później)
- ❓ **Matchup Score Tracker** - live VP tracking podczas gry (dużo później)
- ❓ **Unit Statistics** - performance tracking unitów (dużo później)

---

## 16. Getting Started

```bash
# 1. Clone repo
git clone https://github.com/ogdowski/squigleague
cd squigleague

# 2. Create .env
cp .env.example .env
# Edit .env with your OAuth credentials

# 3. Start containers
just dev-build

# 4. Run migrations
just migrate

# 5. Open browser
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000/docs
# Nginx proxy: http://localhost
```

---

## 17. References

- Old repo: https://github.com/ogdowski/squigleague
- FastAPI Users: https://fastapi-users.github.io/fastapi-users/
- SQLModel: https://sqlmodel.tiangolo.com/
- Vue 3: https://vuejs.org/
- TailwindCSS: https://tailwindcss.com/
- BSData Age of Sigmar: https://github.com/BSData/age-of-sigmar-4th

---

**Plan kompletny i gotowy do implementacji! 🎉**

**Następny krok:** Faza 1 - Setup projektu + Users + Auth (Google + Discord SSO)
