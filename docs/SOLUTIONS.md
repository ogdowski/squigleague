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

## Template for New Solutions

```markdown
## [SOLUTION-XXX] Brief Description

**Solves:** [ISSUE-IDs]  
**Type:** Process | Test | Documentation | Code  
**Implementation:** [What was added/changed]  
**Validation:** [How to verify it works]  
**Maintenance:** [How to keep it working]
```
