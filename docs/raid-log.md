# RAID Log

## Purpose
This document tracks Risks, Assumptions, Issues, and Dependencies for the SquigLeague platform.

---

## Risks

### R-001: Docker Desktop Licensing
**Status**: Active  
**Severity**: Medium  
**Date Identified**: 2025-11-25  
**Description**: Docker Desktop requires paid license for organizations over certain size.  
**Impact**: Could require migration to Podman or alternative containerization.  
**Mitigation**: Monitor team size, evaluate alternatives proactively.  
**Owner**: DevOps

### R-002: Third-Party API Availability
**Status**: Active  
**Severity**: Low  
**Date Identified**: 2025-11-25  
**Description**: Currently self-contained, but future features may depend on external APIs (e.g., Warhammer Community data).  
**Impact**: Features could break if external services go down.  
**Mitigation**: Cache data locally, implement graceful degradation.  
**Owner**: Backend Team

---

## Assumptions

### A-001: Users Have Modern Browsers
**Status**: Valid  
**Date**: 2025-11-25  
**Description**: Platform assumes users have browsers supporting ES6+, CSS Grid, Alpine.js (Chrome 60+, Firefox 60+, Safari 11+).  
**Validation**: Monitor browser analytics, provide graceful degradation message.  
**Owner**: Frontend Team

### A-002: Tournament Formats Follow GW Standards
**Status**: Valid  
**Date**: 2025-11-25  
**Description**: Battle plans and tournament structures follow Games Workshop official formats (General's Handbook, etc.).  
**Validation**: Review GW published tournament packs annually.  
**Owner**: Product Owner

### A-003: Users Understand Warhammer Terminology
**Status**: Valid  
**Date**: 2025-11-25  
**Description**: UI uses game-specific terms (deployment, objectives, etc.) without extensive explanation.  
**Validation**: User testing with new players, add tooltips if needed.  
**Owner**: UX Design

### A-004: Single Database Sufficient for MVP
**Status**: Valid  
**Date**: 2025-11-25  
**Description**: Single PostgreSQL instance can handle expected load for initial release.  
**Validation**: Monitor performance metrics, plan for read replicas if needed.  
**Owner**: Backend Team

---

## Issues

### I-001: /api/squire/systems Endpoint Broken
**Status**: Open  
**Severity**: Low  
**Date Identified**: 2025-11-25  
**Description**: ImportError when calling /api/squire/systems - tries to import non-existent AOS_DEPLOYMENTS constant.  
**Impact**: Systems listing endpoint fails, but core battle plan generation works.  
**Resolution**: Remove or fix the systems endpoint - not currently used by frontend.  
**Owner**: Backend Team  
**Target Date**: 2025-12-01

### I-002: No User Authentication
**Status**: Open  
**Severity**: High  
**Date Identified**: 2025-11-25  
**Description**: Platform has no authentication system - all features are public.  
**Impact**: Cannot track user data, lists, or tournament registrations.  
**Resolution**: Implement OAuth2 or similar auth system in next sprint.  
**Owner**: Backend Team  
**Target Date**: 2025-12-15

---

## Dependencies

### D-001: PostgreSQL 16
**Type**: Technical  
**Status**: Active  
**Date**: 2025-11-25  
**Description**: Database requires PostgreSQL 16+ for specific features.  
**Risk**: Migration complexity if version changes.  
**Owner**: Backend Team

### D-002: Games Workshop IP
**Type**: Legal/Business  
**Status**: Active  
**Date**: 2025-11-25  
**Description**: Battle plans and mission data are based on GW published content.  
**Risk**: Potential IP concerns if we reproduce too much official content.  
**Mitigation**: Use generic descriptions, reference official sources, don't reproduce full text.  
**Owner**: Product Owner

### D-003: TailwindCSS CDN
**Type**: Technical  
**Status**: Active  
**Date**: 2025-11-25  
**Description**: Frontend uses TailwindCSS via CDN (not built).  
**Risk**: CDN downtime or deprecation.  
**Mitigation**: Consider moving to built version for production.  
**Owner**: Frontend Team

### D-004: Alpine.js CDN
**Type**: Technical  
**Status**: Active  
**Date**: 2025-11-25  
**Description**: Frontend uses Alpine.js via CDN.  
**Risk**: CDN downtime or version changes breaking compatibility.  
**Mitigation**: Pin specific version, consider self-hosting for production.  
**Owner**: Frontend Team

---

## Log Update Process

1. **Adding New Items**: Include all required fields (ID, Status, Date, Description, etc.)
2. **Status Updates**: Change status and add update date in item description
3. **Review Cadence**: Review this log in weekly team meetings
4. **Archival**: Move resolved issues and invalid assumptions to archive section quarterly

---

## Archive

### Resolved Issues
*None yet*

### Deprecated Assumptions
*None yet*

### Closed Risks
*None yet*
