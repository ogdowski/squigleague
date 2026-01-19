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

## [ISSUE-003] Frontend Build Uses Wrong API_URL (Hardcoded localhost:8000)

**Date Discovered:** 2026-01-19  
**Severity:** CRITICAL  
**Root Cause:** Vite environment variables must be shell variables during `npm run build`, not Docker ENV. Using `ENV VITE_API_URL` doesn't make variable available to Vite build process.  
**Symptoms:**
- User login fails in browser with "Login failed. Please try again."
- Backend API endpoints work when tested with PowerShell/curl
- Frontend JavaScript contains `"http://localhost:8000"` instead of `"/api"`
- Browser tries to reach backend directly (unreachable) instead of via nginx proxy
- All frontend API calls bypass nginx routing

**Process Gap:**
- No validation of ACTUAL API_URL value in built JavaScript
- Validation only checked absence of localhost:8000, not presence of correct value
- No understanding of Vite environment variable mechanics (build-time vs runtime)
- Test script validated backend API but not frontend code
- Premature success declaration without comprehensive validation

**Prevention Added:**
- [x] Updated instruction file with "FRONTEND BUILD VALIDATION PROTOCOL"
- [x] Created scripts/validate-frontend-build.ps1 to extract and verify API_URL
- [x] Fixed Dockerfile: `RUN VITE_API_URL=$VITE_API_URL npm run build`
- [x] Documented in KNOWN_ISSUES.md
- [x] Added MANDATORY validation before declaring build success

**Correct Dockerfile:**
```dockerfile
ARG VITE_API_URL=/api
RUN VITE_API_URL=$VITE_API_URL npm run build
```

**MANDATORY Validation After Build:**
```powershell
.\scripts\validate-frontend-build.ps1
# Must exit 0 before declaring success
```

**Related Issues:** ISSUE-002  
**Related Solutions:** SOLUTION-003

---

## [ISSUE-010] Enhanced Images Destroyed Without Recovery
**Date Discovered:** 2026-01-19  
**Severity:** CRITICAL  
**Root Cause:** Agent destroyed work-in-progress files that were never committed to git  
**Symptoms:**
- 11 enhanced battleplan images (frontend/public/assets/battle-plans-enhanced/*.png) were created 2026-01-19 20:39
- Agent overwrote them with wrong matplotlib diagrams 2026-01-19 21:28
- Agent then deleted all files
- Files were NEVER committed to git - permanently lost
- No documentation exists explaining what they were or how they were created

**Process Gap:**
- No enforcement of "commit before modifying" rule
- No documentation of what enhanced images were
- No backup/verification before destructive operations
- Agent created files without user permission

**Prevention Added:**
- [x] Documented in BATTLE_PLANS_GENERATION.md
- [x] Created KNOWN_ISSUES.md entry
- [ ] Add pre-commit hook requiring documentation for new image assets
- [ ] Add validation preventing file deletion without git backup

**Related Issues:** [ISSUE-011], [ISSUE-012]  
**Related Solutions:** None - data permanently lost

---

## [ISSUE-011] No Process Documentation for Image Generation
**Date Discovered:** 2026-01-19  
**Severity:** CRITICAL  
**Root Cause:** Work completed yesterday (2026-01-18) with zero documentation  
**Symptoms:**
- Matplotlib battle plan images generated and committed
- Scripts created and committed
- No README, no docs, no comments explaining process
- 90 minutes wasted re-discovering what was done yesterday
- Agent made assumptions instead of reading non-existent docs

**Process Gap:**
- PROCESS-FIRST PROTOCOL not followed
- No documentation requirement before committing generated assets
- No session summary documenting deliverables
- No handoff documentation between sessions

**Prevention Added:**
- [x] Created BATTLE_PLANS_GENERATION.md documenting full process
- [x] Created KNOWN_ISSUES.md entry
- [ ] Add pre-commit hook requiring docs/ entry for new assets
- [ ] Add session summary template requirement
- [ ] Add documentation validation to approval process

**Related Issues:** [ISSUE-010], [ISSUE-012]  
**Related Solutions:** [SOLUTION-010]

---

## [ISSUE-012] Agent Used Wrong Data Source Repeatedly
**Date Discovered:** 2026-01-19  
**Severity:** HIGH  
**Root Cause:** Agent assumed objectives_corrected.json was correct data source without verification  
**Symptoms:**
- Created 4 different Python scripts all reading objectives_corrected.json
- User repeatedly said "WRONG SOURCE"
- Agent didn't stop and verify correct source
- Agent didn't read existing scripts to understand data flow

**Process Gap:**
- No verification step before creating scripts
- No requirement to check existing code for data sources
- Agent proceeded with assumptions instead of investigation
- No "read before write" protocol

**Prevention Added:**
- [x] Documented FORBIDDEN data sources in BATTLE_PLANS_GENERATION.md
- [x] Created KNOWN_ISSUES.md entry
- [ ] Add validation script checking for objectives_corrected.json usage
- [ ] Add pre-script-creation checklist: "What data source? Verify it exists and is correct"
- [ ] Add "read existing code" step before creating new scripts

**Related Issues:** [ISSUE-010], [ISSUE-011]  
**Related Solutions:** [SOLUTION-011]

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
