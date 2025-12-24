# Copilot Instructions Setup - Complete

**Date**: November 25, 2025  
**Location**: `.github/copilot-instructions.md`  
**Status**: ✅ Active

## What Was Created

A GitHub Copilot instruction file that enforces the "activity scripts only" policy.

### File Location
```
.github/copilot-instructions.md
```

This location is automatically detected by GitHub Copilot in VS Code and applies to all AI interactions in this repository.

### Key Rules Enforced

1. **✅ MUST use activity scripts via runner**
   ```powershell
   .\scripts\runner.ps1 -Script <name>.ps1
   ```

2. **❌ FORBIDDEN direct commands**
   - No `docker` commands
   - No `Invoke-WebRequest`
   - No `git` commands  
   - No database commands
   - No ad-hoc scripts

3. **📋 Lists all 32 approved scripts**
   - Deployment (6 scripts)
   - Testing (7 scripts)
   - Diagnostics (3 scripts)
   - Development workflows (16 scripts)

4. **🔒 Explains enforcement mechanism**
   - Whitelist validation
   - SHA256 integrity checks
   - Audit logging

### How It Works

GitHub Copilot reads `.github/copilot-instructions.md` automatically and:
- Uses it as context for all suggestions
- Follows the rules when generating code
- References approved scripts when suggesting commands
- Explains the policy when users ask

### Verification

The instruction file:
- ✅ Created in `.github/` directory
- ✅ Named `copilot-instructions.md` (GitHub standard)
- ✅ Contains complete list of activity scripts
- ✅ Explains runner.ps1 usage
- ✅ Provides examples of correct/wrong patterns
- ✅ Documents the enforcement mechanism

### What Happens Now

From now on, when you interact with GitHub Copilot in this repository:

1. **Copilot will suggest** using `.\scripts\runner.ps1 -Script <name>.ps1`
2. **Copilot will NOT suggest** direct docker/git/curl commands
3. **Copilot will reference** the approved scripts list
4. **Copilot will explain** why activity scripts are required

### Testing the Integration

You can verify Copilot is using these instructions by:

1. Opening VS Code in this repository
2. Asking Copilot: "How do I check if services are running?"
3. Expected response: Suggest `.\scripts\runner.ps1 -Script check-services.ps1`

### Updating Instructions

If you need to modify the instructions:

1. Edit `.github/copilot-instructions.md`
2. Commit changes
3. Reload VS Code window (Copilot re-reads the file)

### Integration with Existing Enforcement

This complements the technical enforcement:

| Layer | Mechanism | Purpose |
|-------|-----------|---------|
| **Technical** | `runner.ps1` + checksums | Blocks unauthorized execution |
| **AI Assistant** | `copilot-instructions.md` | Guides developers to use runner |
| **Documentation** | `scripts/README.md` | Explains the policy |
| **Audit** | `runner.log` | Tracks all attempts |

### Complete Enforcement Stack

```
┌─────────────────────────────────────┐
│  .github/copilot-instructions.md    │ ← AI guidance
│  (GitHub Copilot reads this)        │
└─────────────────┬───────────────────┘
                  │
                  ↓
┌─────────────────────────────────────┐
│  Developer asks Copilot             │
│  "How do I deploy?"                 │
└─────────────────┬───────────────────┘
                  │
                  ↓
┌─────────────────────────────────────┐
│  Copilot suggests:                  │
│  .\scripts\runner.ps1 -Script       │
│  full-deploy.ps1                    │
└─────────────────┬───────────────────┘
                  │
                  ↓
┌─────────────────────────────────────┐
│  runner.ps1 validates:              │
│  ✓ Script in whitelist              │
│  ✓ Checksum matches                 │
│  ✓ Logs to runner.log               │
└─────────────────┬───────────────────┘
                  │
                  ↓
┌─────────────────────────────────────┐
│  Script executes safely             │
│  Audit trail created                │
└─────────────────────────────────────┘
```

## Benefits

1. **Guidance at source**: AI assistant suggests correct patterns from the start
2. **Reduces errors**: Developers don't need to remember the policy
3. **Consistent workflow**: Everyone (human and AI) uses the same approach
4. **Self-documenting**: Instructions explain WHY the policy exists
5. **Version controlled**: Instructions tracked in git alongside code

## Compliance

✅ **AI layer**: Copilot instructions guide to activity scripts  
✅ **Execution layer**: runner.ps1 enforces whitelist + checksums  
✅ **Audit layer**: runner.log tracks all attempts  
✅ **Documentation layer**: READMEs explain the policy  

**The "activity scripts only" rule is now enforced at every level.**
