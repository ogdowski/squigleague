# Changelog

All notable changes to Squig League will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-11-20

### Herald - Frontend/Backend Separation

**Major Changes**
- **Added Frontend SPA**: New Alpine.js Single Page Application for user interface
  - Vanilla JavaScript with no build step required
  - Tailwind CSS via CDN for styling
  - Client-side routing with browser history API
  - Responsive dark theme design

**Architecture**
- Separated frontend and backend into independent services
- Backend (herald/) now serves pure JSON API at `/api/herald/*` endpoints
- Frontend (frontend/) is a standalone Alpine.js SPA
- Nginx routes `/api/*` to backend, everything else to frontend
- Two separate Docker images: `squigleague-VERSION` (backend) and `squigleague-frontend-VERSION` (frontend)

**Features**
- Dynamic version fetching from `/api/herald/stats` endpoint
- Footer version no longer hardcoded in frontend
- Multi-arch Docker images (amd64/arm64) for both services
- Independent scaling of frontend and backend services

**Developer Experience**
- `just dev` starts both backend and frontend services
- `just push` builds and pushes both images together
- Cleaner separation of concerns for testing and scaling

**Breaking Changes**
- Frontend templates moved from `herald/templates/` to `frontend/`
- Static files moved from `herald/static/` to `frontend/`
- Backend no longer serves HTML, only JSON
- New nginx routing configuration required

## [0.1.0] - 2025-01-20

### Herald Phase 1 - Initial Release

**Added**
- Herald - blind list exchange system for Warhammer battles

**Infrastructure**
- Docker containerization
- PostgreSQL database
- Production-ready deployment at herald.squigleague.com

---

