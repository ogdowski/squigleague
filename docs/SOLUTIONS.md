# Solutions

This document tracks solutions to known issues and how to maintain them.

---

## [SOLUTION-001] Complete nginx Configuration for Auth Routes

**Solves:** ISSUE-001, ISSUE-002  
**Type:** Configuration + Process  
**Implementation:**

### 1. nginx Configuration Fix

File: `nginx/nginx.http-only.conf`

```nginx
# Auth routes go to backend
location /auth/ {
    proxy_pass http://backend/auth/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

**Location:** Add AFTER `/api/` block, BEFORE `/health` block

### 2. Validation Script

Run before declaring deployment successful:
```powershell
.\scripts\validate-deployment.ps1
```

Exit code 0 = PASS, 1 = FAIL

### 3. Deployment Process

**MANDATORY STEPS:**
1. Stop containers: `docker-compose down`
2. Rebuild frontend (no cache): `docker-compose -f docker-compose.yml -f docker-compose.dev.yml build --no-cache frontend`
3. Start with dev config: `docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d`
4. Wait 10 seconds for health checks
5. Run validation: `.\scripts\validate-deployment.ps1`
6. If validation fails: Check logs, fix issues, restart from step 1
7. Only open browser AFTER validation passes

**Maintenance:**
- Review nginx config whenever adding new API route prefixes
- Add new route tests to validate-deployment.ps1
- Keep KNOWN_ISSUES.md updated when patterns emerge

**Validation:**
Test registration manually after deployment:
1. Open http://localhost/register
2. Create account with unique email
3. Verify successful registration (redirects to /)
4. Check backend logs for successful POST to /auth/register

---

## [SOLUTION-003] Frontend Build with Correct Vite Environment Variables

**Solves:** ISSUE-003  
**Type:** Process + Code + Validation  
**Implementation:**

### 1. Dockerfile Fix

File: `frontend/Dockerfile`

**WRONG (Doesn't work):**
```dockerfile
ARG VITE_API_URL=/api
ENV VITE_API_URL=$VITE_API_URL  # ENV doesn't work for Vite
RUN npm run build
```

**CORRECT:**
```dockerfile
ARG VITE_API_URL=/api
RUN VITE_API_URL=$VITE_API_URL npm run build  # Shell variable works
```

**Why:** Vite reads `import.meta.env.VITE_API_URL` from shell environment during build, NOT from Docker ENV.

### 2. Build Command

**MANDATORY:**
```powershell
docker-compose -f docker-compose.yml -f docker-compose.dev.yml build --no-cache --build-arg VITE_API_URL=/api frontend
```

**REQUIRED FLAGS:**
- `--no-cache`: Prevents stale builds
- `--build-arg VITE_API_URL=/api`: Passes variable to build

### 3. Validation Script

**BEFORE declaring build success, run:**
```powershell
.\scripts\validate-frontend-build.ps1
```

**Exit codes:**
- 0 = API_URL is "/api" (SUCCESS)
- 1 = API_URL is "http://localhost:8000" or missing (FAILED)

**What it does:**
1. Extracts all API_URL definitions from built JavaScript
2. Verifies ACTUAL value is "/api"
3. Fails if localhost:8000 found
4. Never relies on absence of error - validates presence of correct value

### 4. Complete Rebuild Process

**MANDATORY SEQUENCE:**
```powershell
# Stop frontend
docker-compose -f docker-compose.yml -f docker-compose.dev.yml down frontend

# Rebuild with VITE_API_URL
docker-compose -f docker-compose.yml -f docker-compose.dev.yml build --no-cache --build-arg VITE_API_URL=/api frontend

# Start frontend
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d frontend

# Wait for container
Start-Sleep -Seconds 3

# VALIDATE (MANDATORY - DO NOT SKIP)
.\scripts\validate-frontend-build.ps1

# If validation passes (exit 0), THEN test browser functionality
.\scripts\test-browser-functionality-fixed.ps1
```

**Validation:**
- Run validation script: `.\scripts\validate-frontend-build.ps1`
- Check browser console: No requests to localhost:8000
- Test login: Should work with alakhaine@dundrafts.com / FinFan11
- Network tab: All requests go to /api/* not http://localhost:8000/*

**Maintenance:**
- Never rebuild frontend without running validate-frontend-build.ps1 after
- Update validation script if API_URL pattern changes
- Keep instruction file updated with this process
- Add to pre-deployment checklist

---

## Template for New Solutions

```markdown
## [SOLUTION-XXX] Brief Description

**Solves:** [ISSUE-IDs]  
**Type:** Process | Test | Documentation | Code  
**Implementation:** [What was added/changed]  
**Validation:** [How to verify it works]  
**Maintenance:** [How to keep it working]
```
