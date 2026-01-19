# Deployment Checklist

**MANDATORY:** Complete ALL steps before declaring deployment successful.

---

## Pre-Deployment

- [ ] All commits pushed to current branch
- [ ] Branch name matches feature (e.g., feature/display-player-names)
- [ ] No uncommitted changes: `git status` is clean
- [ ] Battle plan images present: `Get-ChildItem assets/battle-plans-matplotlib/*.png` shows 12+ files

---

## Docker Deployment

### Stop Existing Containers
```powershell
docker-compose down
```

### Rebuild (Development)
```powershell
# Use dev config to avoid SSL cert issues
docker-compose -f docker-compose.yml -f docker-compose.dev.yml build --no-cache frontend
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

### Wait for Health Checks
```powershell
Start-Sleep -Seconds 10
```

---

## Validation (MANDATORY)

### Run Automated Validation
```powershell
.\scripts\validate-deployment.ps1
```

**If validation FAILS:**
- Check errors in output
- Review docker logs: `docker logs squig-backend --tail 50`
- Fix issues
- Return to "Docker Deployment" section

**Only proceed if validation PASSES (exit code 0)**

---

## Manual Verification

### Test Critical User Flows

#### 1. Registration Flow
- [ ] Navigate to http://localhost/register
- [ ] Enter unique email, username, password (8+ chars)
- [ ] Click "Register" button
- [ ] Verify: Redirects to / (home page)
- [ ] Verify: No error message shown
- [ ] Check backend logs: `docker logs squig-backend --tail 10` shows POST to /auth/register with 201

#### 2. Login Flow
- [ ] Navigate to http://localhost/login
- [ ] Enter credentials from registration test
- [ ] Click "Login" button  
- [ ] Verify: Redirects to / (home page)
- [ ] Verify: Username shown in nav bar
- [ ] Verify: "Logout" button present

#### 3. Matchup Creation (Feature-Specific)
- [ ] Navigate to http://localhost/matchup/create (or click "Create Matchup")
- [ ] Select game system (Age of Sigmar)
- [ ] Submit two army lists
- [ ] Verify: Battle plan generates successfully
- [ ] Verify: Battle plan image displays (matplotlib diagram)
- [ ] Verify: Image loads without 404 errors (check browser console F12)

---

## Browser Console Check

- [ ] Open browser DevTools (F12)
- [ ] Check Console tab for errors
- [ ] Check Network tab for failed requests (red items)
- [ ] All critical API calls return 200/201 (not 404/405/500)

---

## Commit Configuration Changes

If nginx config was modified:
```powershell
git add nginx/nginx.http-only.conf
git commit -m "Fix nginx auth routes configuration"
```

---

## Post-Deployment

- [ ] Update docs/SESSION_REVIVAL.md with deployment notes
- [ ] Document any new issues in docs/KNOWN_ISSUES.md
- [ ] Document solutions in docs/SOLUTIONS.md
- [ ] Update this checklist if new steps were needed

---

## Emergency Rollback

If deployment fails and cannot be fixed quickly:

```powershell
# Stop broken deployment
docker-compose down

# Checkout last known good commit
git log --oneline -10  # Find last working commit
git checkout <commit-hash>

# Rebuild
docker-compose -f docker-compose.yml -f docker-compose.dev.yml build --no-cache frontend
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Validate
.\scripts\validate-deployment.ps1
```

---

## Common Issues

### nginx 405 on /auth/ routes
**Symptom:** Registration fails with generic error  
**Fix:** Verify nginx.http-only.conf has /auth/ location block  
**Validate:** `.\scripts\validate-deployment.ps1` should test this

### Stale frontend build
**Symptom:** Changes not reflected in browser  
**Fix:** Rebuild with --no-cache flag  
**Validate:** Check build timestamp in validation script

### Database connection errors
**Symptom:** Backend fails to start, "connection refused"  
**Fix:** Verify squig-postgres container is healthy  
**Check:** `docker logs squig-postgres --tail 50`
