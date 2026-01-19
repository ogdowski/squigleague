# Known Issues

This document tracks recurring issues, their root causes, and prevention strategies.

---

## [ISSUE-001] Registration Fails - nginx Missing /auth/ Routes

**Date Discovered:** 2026-01-19  
**Severity:** HIGH  
**Root Cause:** nginx configuration lacks `/auth/` location block to proxy authentication endpoints  
**Symptoms:**
- Registration returns "Registration failed. Please try again." (generic error)
- Browser shows HTTP 405 Method Not Allowed
- Backend logs show no POST requests to /auth/register
- curl/Postman tests to http://localhost/auth/register fail with 405

**Process Gap:** 
- No validation script to verify all critical API routes are proxied through nginx
- No end-to-end testing of user registration flow before deployment
- Stale Docker builds not detected

**Prevention Added:**
- [x] Updated nginx.http-only.conf with /auth/ location block
- [x] Created scripts/validate-deployment.ps1 to test auth routes
- [x] Added frontend build currency check
- [x] Documented in KNOWN_ISSUES.md

**Related Issues:** ISSUE-002  
**Related Solutions:** SOLUTION-001

---

## [ISSUE-002] Stale Frontend Docker Build

**Date Discovered:** 2026-01-19  
**Severity:** HIGH  
**Root Cause:** Docker build cache prevents frontend from rebuilding when source changes  
**Symptoms:**
- Frontend serves old JavaScript bundles (4+ days old)
- User authentication features missing or broken
- API calls use wrong endpoint paths or data structures
- Source code changes not reflected in running application

**Process Gap:**
- No check for frontend build currency during deployment
- No automatic cache-busting on deployment
- Docker layer caching too aggressive for development

**Prevention Added:**
- [x] Added build date check to validate-deployment.ps1
- [x] Documented cache-clearing rebuild command
- [x] Added to deployment checklist

**Fix:**
```powershell
# Force rebuild without cache
docker-compose -f docker-compose.yml -f docker-compose.dev.yml build --no-cache frontend
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d --no-deps frontend
```

**Related Issues:** ISSUE-001  
**Related Solutions:** SOLUTION-001

---

## Template for New Issues

```markdown
## [ISSUE-XXX] Brief Description

**Date Discovered:** YYYY-MM-DD  
**Severity:** CRITICAL | HIGH | MEDIUM | LOW  
**Root Cause:** [What actually caused this]  
**Symptoms:** [How it manifested]  
**Process Gap:** [What was missing from process]

**Prevention Added:**
- [ ] Updated instructions
- [ ] Created validation script
- [ ] Added to pipeline
- [ ] Tested prevention

**Related Issues:** [ISSUE-IDs]  
**Related Solutions:** [SOLUTION-IDs]
```
