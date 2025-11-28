# Design Decisions

## Purpose
This document records all architectural and design decisions made for the SquigLeague platform.

## Decision Format
Each decision should include:
- **Decision ID**: Unique identifier (DD-###)
- **Date**: When the decision was made
- **Status**: Proposed | Accepted | Deprecated | Superseded
- **Context**: What prompted this decision
- **Decision**: What was decided
- **Consequences**: Impacts and trade-offs
- **Alternatives Considered**: Other options that were evaluated

---

## DD-001: No Emoji Icons in UI
**Date**: 2025-11-25  
**Status**: Accepted  
**Context**: User feedback indicated emoji icons are unprofessional and detract from the serious competitive gaming nature of the platform.

**Decision**: All UI components must use text labels, SVG icons, or icon fonts only. Emoji characters (Unicode emoji) are strictly prohibited in:
- User interface elements
- Navigation menus
- Buttons and controls
- Status indicators
- Notifications
- Any user-facing content

**Consequences**:
- More professional appearance
- Better accessibility (screen readers)
- Consistent cross-platform rendering
- Slightly longer development time for custom icons

**Alternatives Considered**:
- Using emoji with text fallbacks (rejected - still shows emoji)
- Allowing emoji in user-generated content only (rejected - inconsistent UX)

---

## DD-002: Docker-Based Architecture
**Date**: 2025-11-25  
**Status**: Accepted  
**Context**: Need for consistent development and deployment environments across team members and production.

**Decision**: Use Docker Compose for local development and production deployment with separate services:
- PostgreSQL database (squig-postgres)
- FastAPI backend (squig)
- Alpine.js frontend (squig-frontend)
- Nginx reverse proxy (squig-nginx)

**Consequences**:
- Consistent environments across dev/staging/prod
- Easy onboarding for new developers
- Requires Docker Desktop for development
- Slightly higher resource usage locally

**Alternatives Considered**:
- Monolithic Python application (rejected - harder to scale)
- Separate repos for frontend/backend (rejected - coordination overhead)

---

## DD-003: Alpine.js for Frontend Framework
**Date**: 2025-11-25  
**Status**: Accepted  
**Context**: Need lightweight, reactive frontend without heavy build processes.

**Decision**: Use Alpine.js for client-side interactivity with server-rendered HTML and client-side routing.

**Consequences**:
- Minimal build tooling required
- Fast page loads
- Easy to understand for Python developers
- Limited ecosystem compared to React/Vue
- Manual state management required

**Alternatives Considered**:
- React (rejected - too heavy, requires build process)
- Vue.js (rejected - similar overhead to React)
- Vanilla JavaScript (rejected - too much boilerplate)

---

## DD-004: Modular Backend Structure
**Date**: 2025-11-25  
**Status**: Accepted  
**Context**: Platform will have multiple distinct features (Herald for tournament admin, Squire for player tools).

**Decision**: Organize backend into modules with separate route files:
- `/herald/*` - Tournament administration
- `/squire/*` - Player utilities (battle plans, list tools)
- Each module has its own routes.py, models, and business logic

**Consequences**:
- Clear separation of concerns
- Easier to add new modules
- Potential for future microservices if needed
- Slightly more files to navigate

**Alternatives Considered**:
- Single monolithic routes file (rejected - would become unwieldy)
- Separate microservices from start (rejected - premature optimization)

---

## Template for Future Decisions

```markdown
## DD-###: [Decision Title]
**Date**: YYYY-MM-DD  
**Status**: Proposed | Accepted | Deprecated | Superseded  
**Context**: [Why is this decision needed?]

**Decision**: [What are we doing?]

**Consequences**:
- [Positive and negative impacts]

**Alternatives Considered**:
- [Other options and why they were rejected]
```
