# Activity Scripts - Quick Reference Card

## ✅ DO THIS (Enforced & Secure)

```powershell
# Run any activity script via runner
.\scripts\runner.ps1 -Script <name>.ps1 -WhatIf   # Preview first
.\scripts\runner.ps1 -Script <name>.ps1           # Then execute
```

## ❌ DON'T DO THIS (Will Fail)

```powershell
# Direct execution (bypasses enforcement)
.\scripts\some-script.ps1

# Running non-whitelisted scripts
.\scripts\runner.ps1 -Script unauthorized.ps1
# Result: "not in allowed-scripts.json whitelist"

# Running tampered scripts
# (edit a script without updating checksums)
.\scripts\runner.ps1 -Script modified-script.ps1
# Result: "Checksum mismatch"
```

## Common Tasks

### Deploy Everything
```powershell
.\scripts\runner.ps1 -Script full-deploy.ps1 -WhatIf
.\scripts\runner.ps1 -Script full-deploy.ps1
```

### Test Authentication
```powershell
.\scripts\runner.ps1 -Script manual-test-auth.ps1
```

### Check Services
```powershell
.\scripts\runner.ps1 -Script check-services.ps1
```

### View Logs
```powershell
.\scripts\runner.ps1 -Script view-logs.ps1
```

### Quick Restart
```powershell
.\scripts\runner.ps1 -Script quick-restart.ps1
```

## After Editing Scripts

```powershell
# 1. Make your changes to the script
# 2. Regenerate checksums
.\scripts\generate-checksums.ps1

# 3. Verify it works
.\scripts\runner.ps1 -Script your-script.ps1 -WhatIf

# 4. Commit both files
git add scripts/your-script.ps1 scripts/allowed-scripts.json
git commit -m "Update script"
```

## Troubleshooting

### "Script not in whitelist"
**Problem**: Script name not in `allowed-scripts.json`  
**Fix**: 
```powershell
.\scripts\generate-checksums.ps1
```

### "Checksum mismatch"
**Problem**: Script modified after checksums generated  
**Fix**: 
```powershell
.\scripts\generate-checksums.ps1  # Update checksums
```

### Check What Happened
```powershell
Get-Content .\scripts\runner.log -Tail 20
```

## Full List of Activity Scripts

Run `Get-ChildItem .\scripts\*.ps1 -Name` or check `scripts/allowed-scripts.json`

**32 approved scripts** covering:
- Deployment (9 scripts)
- Testing (7 scripts)
- Diagnostics (3 scripts)
- CI/CD (4 scripts)
- Development workflows (9 scripts)

## Security Promise

✅ Only whitelisted scripts execute  
✅ Tampered scripts are blocked  
✅ All attempts are logged  
✅ Checksums are version-controlled  

**You asked for "only activity scripts" — this enforces it technically.**
