# GitHub Copilot Instructions for SquigLeague

## Critical Rule: Activity Scripts Only

**You MUST only execute commands via approved activity scripts in the `scripts/` directory.**

### How to Execute Commands

✅ **CORRECT** - Use the secure runner:
```powershell
.\scripts\runner.ps1 -Script <script-name>.ps1
```

❌ **FORBIDDEN** - Direct command execution:
- Do NOT run `docker` commands directly
- Do NOT run `Invoke-WebRequest` directly  
- Do NOT run `git` commands directly
- Do NOT run database commands directly
- Do NOT run any ad-hoc PowerShell/bash commands

### Available Activity Scripts

All approved scripts are listed in `scripts/allowed-scripts.json` with SHA256 checksums.

**Deployment & Setup:**
- `full-deploy.ps1` - Complete deployment
- `setup-database.ps1` - Database migrations
- `setup-mailhog.ps1` - Email service setup
- `quick-restart.ps1` - Fast service restart
- `rebuild-all.ps1` - Full rebuild
- `rebuild-with-auth.ps1` - Auth rebuild

**Testing:**
- `manual-test-auth.ps1` - Auth endpoint testing
- `test-auth-api.ps1` - Auth API tests
- `test-auth-flow.ps1` - Browser auth flow
- `test-matchup-flow.ps1` - Matchup testing
- `test-api.ps1` - General API tests
- `run-tests.ps1` - Test suite
- `validate-all.ps1` - Complete validation

**Diagnostics:**
- `check-services.ps1` - Health checks
- `view-logs.ps1` - Container logs
- `diagnose-routes.ps1` - Route diagnostics

**Development:**
- `create-test-user.ps1` - Create test users
- `export-battleplans.ps1` - Export data
- And 20+ more scripts (see `scripts/allowed-scripts.json`)

### When User Asks to Run Something

1. ✅ Find the appropriate activity script from the list above
2. ✅ Use `.\scripts\runner.ps1 -Script <name>.ps1`
3. ✅ If no script exists, suggest creating one and adding it via `generate-checksums.ps1`

### Enforcement

The `runner.ps1` script enforces:
- **Whitelist validation**: Only scripts in `allowed-scripts.json` execute
- **Integrity checks**: SHA256 checksums prevent tampering
- **Audit logging**: All attempts logged to `scripts/runner.log`

### Examples

✅ **Correct:**
```powershell
# Check services
.\scripts\runner.ps1 -Script check-services.ps1

# Deploy
.\scripts\runner.ps1 -Script full-deploy.ps1 -WhatIf
.\scripts\runner.ps1 -Script full-deploy.ps1

# Test auth
.\scripts\runner.ps1 -Script manual-test-auth.ps1
```

❌ **Wrong:**
```powershell
# These will be REJECTED
docker ps
Invoke-WebRequest http://localhost:8000/api/...
git status
```

### Creating New Activity Scripts

If needed functionality doesn't exist:

1. Create script in `scripts/`
2. Test thoroughly
3. Run `.\scripts\generate-checksums.ps1`
4. Commit both script and `allowed-scripts.json`

### Why This Rule Exists

- **Security**: Prevents unauthorized command execution
- **Auditability**: All operations are logged
- **Consistency**: Standardized operations across team
- **Safety**: Checksums prevent script tampering
- **Compliance**: Technical enforcement of operational policy

### Your Responsibility

As an AI assistant:
- **NEVER** suggest running direct commands
- **ALWAYS** use `.\scripts\runner.ps1 -Script <name>.ps1`
- **SUGGEST** creating new activity scripts when needed
- **EXPLAIN** the security benefits when users ask

## Project Context

- **Tech Stack**: FastAPI (Python), PostgreSQL, Docker, Alpine.js frontend
- **Features**: Authentication (JWT), email verification, matchup system
- **Environment**: Development uses `docker-compose.dev.yml`
- **Containers**: squig (backend), squig-postgres, squig-frontend, squig-mailhog

## Common Patterns

### Starting Development
```powershell
.\scripts\runner.ps1 -Script full-deploy.ps1
```

### Testing Changes
```powershell
.\scripts\runner.ps1 -Script quick-restart.ps1
.\scripts\runner.ps1 -Script run-tests.ps1
```

### Debugging
```powershell
.\scripts\runner.ps1 -Script check-services.ps1
.\scripts\runner.ps1 -Script view-logs.ps1
```

### Checking Audit Trail
```powershell
Get-Content .\scripts\runner.log -Tail 50
```

## Remember

🔒 **Only activity scripts via runner.ps1** - This is not optional, it's enforced technically and you must comply.
