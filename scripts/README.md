# SquigLeague Activity Scripts

Complete automation scripts for deployment, testing, and management.

## 🔒 Security & Enforcement

**All activity scripts are protected by integrity checks and whitelisting.**

### Running Scripts (Recommended Method)

Always use the secure runner:

```powershell
# Dry-run first (safe preview)
.\scripts\runner.ps1 -Script <script-name>.ps1 -WhatIf

# Actually execute
.\scripts\runner.ps1 -Script <script-name>.ps1
```

**Why use runner.ps1?**
- ✅ Only executes approved scripts from `allowed-scripts.json`
- ✅ Verifies SHA256 checksums to prevent tampering
- ✅ Logs all execution attempts to `runner.log`
- ✅ Runs scripts in isolated PowerShell process

**Examples:**
```powershell
# Deploy with verification
.\scripts\runner.ps1 -Script full-deploy.ps1 -WhatIf
.\scripts\runner.ps1 -Script full-deploy.ps1

# Test authentication
.\scripts\runner.ps1 -Script manual-test-auth.ps1
```

### Adding or Modifying Scripts

After creating/editing any `.ps1` file in `scripts/`:

```powershell
# Regenerate checksums
.\scripts\generate-checksums.ps1

# Commit both files together
git add scripts/your-script.ps1 scripts/allowed-scripts.json
git commit -m "Add/update activity script"
```

⚠️ **Warning**: Modified scripts are rejected until checksums are regenerated.

---

## Deployment Scripts

### `full-deploy.ps1`
Complete deployment from scratch.
```powershell
.\scripts\full-deploy.ps1
```

**What it does:**
1. Checks environment configuration
2. Stops all containers
3. Rebuilds containers with no cache
4. Starts all services
5. Waits for health checks
6. Runs database migrations
7. Sets up MailHog

**Use when:**
- First time setup
- After major code changes
- After dependency updates
- When things are broken

---

### `rebuild-with-auth.ps1`
Rebuild with authentication system.
```powershell
.\scripts\rebuild-with-auth.ps1
```

**What it does:**
1. Creates .env.local if needed
2. Rebuilds containers
3. Runs database migrations
4. Sets up MailHog
5. Shows service URLs

**Use when:**
- Deploying authentication features
- Initial Phase 2.1 deployment

---

### `quick-restart.ps1`
Fast restart without rebuild.
```powershell
.\scripts\quick-restart.ps1           # Restart all
.\scripts\quick-restart.ps1 squig     # Restart backend only
```

**What it does:**
- Restarts specified service(s)
- Waits for health check
- No rebuild, just restart

**Use when:**
- Testing code changes (if mounted)
- Service crashed
- Quick fixes

---

## Database Scripts

### `setup-database.ps1`
Run database migrations.
```powershell
.\scripts\setup-database.ps1
```

**What it does:**
1. Checks PostgreSQL is running
2. Waits for database to be ready
3. Runs Alembic migrations
4. Shows database tables

**Use when:**
- After creating new migrations
- Database schema needs updating
- First time setup

---

## Email Testing Scripts

### `setup-mailhog.ps1`
Set up MailHog for email testing.
```powershell
.\scripts\setup-mailhog.ps1
```

**What it does:**
1. Starts MailHog container
2. Updates .env.local with MailHog settings
3. Shows MailHog web UI URL

**Use when:**
- First time setup
- MailHog container stopped
- Need to test emails

**MailHog URLs:**
- Web UI: http://localhost:8025
- SMTP: localhost:1025 (from host) or mailhog:1025 (from containers)

---

## Testing Scripts

### `test-auth-api.ps1`
Quick authentication API test.
```powershell
.\scripts\test-auth-api.ps1
```

**What it does:**
- Tests backend health
- Tests registration endpoint
- Shows success/failure

**Use when:**
- After deployment
- Verifying auth works
- Quick sanity check

---

### `test-auth-flow.ps1`
Complete authentication flow test.
```powershell
.\scripts\test-auth-flow.ps1
```

**What it does:**
1. Registers new user
2. Tests login before verification (should fail)
3. Retrieves verification email from MailHog
4. Verifies email
5. Tests login after verification
6. Gets user info with JWT
7. Tests unauthorized access

**Use when:**
- Full integration testing
- Verifying entire auth flow
- Before release

---

### `create-test-user.ps1`
Create and verify test user.
```powershell
.\scripts\create-test-user.ps1
```

**What it does:**
- Creates test user with timestamp
- Auto-verifies email via MailHog
- Shows credentials

**Use when:**
- Need test account
- Manual frontend testing
- Demo purposes

---

## Monitoring Scripts

### `check-services.ps1`
Verify all services are running.
```powershell
.\scripts\check-services.ps1
```

**What it does:**
- Lists Docker container status
- Tests all service endpoints
- Checks database connection
- Verifies migrations applied

**Use when:**
- After deployment
- Troubleshooting
- Health check

---

### `view-logs.ps1`
View container logs.
```powershell
.\scripts\view-logs.ps1                  # All containers
.\scripts\view-logs.ps1 -Container squig  # Specific container
.\scripts\view-logs.ps1 -Lines 100        # More lines
```

**What it does:**
- Shows recent logs from containers
- Can filter by container
- Shows available containers

**Use when:**
- Debugging errors
- Checking startup issues
- Monitoring activity

---

## Utility Scripts

### `run-tests.ps1`
Run API test suite.
```powershell
.\scripts\run-tests.ps1
```

**What it does:**
- Runs all API tests
- Shows pass/fail results
- Generates test report

---

### `export-battleplans.ps1`
Export battle plan reference.
```powershell
.\scripts\export-battleplans.ps1
```

**What it does:**
- Exports battle plans to JSON
- Creates backup
- Shows export location

---

### `prepare-release.ps1`
Prepare release artifacts.
```powershell
.\scripts\prepare-release.ps1
```

**What it does:**
- Creates release directory
- Exports battle plans
- Copies documentation
- Generates changelog

---

## Common Workflows

### Fresh Deployment
```powershell
.\scripts\full-deploy.ps1
.\scripts\check-services.ps1
.\scripts\test-auth-api.ps1
```

### After Code Changes
```powershell
.\scripts\full-deploy.ps1        # If dependencies changed
# OR
.\scripts\quick-restart.ps1      # If just code changed
```

### Testing Authentication
```powershell
.\scripts\test-auth-api.ps1      # Quick test
.\scripts\test-auth-flow.ps1     # Full test
.\scripts\create-test-user.ps1   # Manual testing
```

### Troubleshooting
```powershell
.\scripts\check-services.ps1
.\scripts\view-logs.ps1
docker-compose ps
```

### Database Management
```powershell
.\scripts\setup-database.ps1     # Run migrations
docker exec squig alembic current  # Check current version
docker exec squig-postgres psql -U squig -d squigleague  # SQL console
```

---

## Environment Files

- `.env` - Used by docker-compose (auto-created from .env.local)
- `.env.local` - Local development settings
- `.env.local.example` - Template for new setups

**Important:** Never commit `.env` or `.env.local` to git!

---

## Service URLs

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost:8080 | Web application |
| Backend API | http://localhost:8000 | REST API |
| MailHog UI | http://localhost:8025 | Email testing |
| PostgreSQL | localhost:5432 | Database (internal) |

---

## Tips

1. **Always check services after deployment:**
   ```powershell
   .\scripts\check-services.ps1
   ```

2. **View logs when things fail:**
   ```powershell
   .\scripts\view-logs.ps1 -Container squig
   ```

3. **Create test users for manual testing:**
   ```powershell
   .\scripts\create-test-user.ps1
   ```

4. **Run full test suite before committing:**
   ```powershell
   .\scripts\test-auth-flow.ps1
   .\scripts\run-tests.ps1
   ```

5. **Use MailHog for all email testing:**
   - Open http://localhost:8025
   - View verification emails
   - No real emails sent

---

## Script Dependencies

All scripts require:
- Docker and Docker Compose
- PowerShell 5.1 or higher
- .env or .env.local file

Optional:
- curl (for API testing)
- git (for release scripts)
