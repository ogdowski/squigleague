# Security Guide for SquigLeague

## ⚠️ CRITICAL: Never Commit Sensitive Data

This is a **public repository**. The following must NEVER be committed:

### 🔐 Secrets That Must Stay Private

1. **Environment Files**
   - `.env`
   - `.env.local`
   - `.env.prod`
   - Any file containing actual credentials

2. **Credentials**
   - Database passwords
   - Secret keys
   - OAuth client secrets
   - API keys
   - Admin passwords

3. **Infrastructure Details**
   - VPS IP addresses
   - SSH keys
   - SSL private keys
   - Database connection strings with passwords

4. **Personal Information**
   - Email addresses (except placeholder examples)
   - Admin IP addresses
   - User data

## ✅ What's Safe to Commit

1. **Template Files**
   - `.env.*.example` files with placeholder values
   - Documentation with `YOUR_IP_HERE` placeholders

2. **Public Information**
   - Domain names (squigleague.com)
   - Docker Hub usernames (if public)
   - Application structure
   - Code and configuration templates

3. **Test Data**
   - Test passwords in `docker-compose.test.yml` (for local testing only)
   - Example configurations

## 🛡️ Current Security Setup

### .gitignore Protection

The following patterns are ignored:
```
.env
.env.local
.env.prod
.env.*.local
backend/.env
frontend/.env
*.pem
*.key
*.crt
secrets/
*.secret
```

### Environment Variable Management

**Production secrets** are loaded from `.env.prod`:
```bash
# VPS Configuration
VPS_IP=your.actual.ip.address      # NEVER commit!
DB_PASSWORD=strong_password_here    # NEVER commit!
SECRET_KEY=generated_secret_key     # NEVER commit!
```

**Template files** use placeholders:
```bash
# .env.prod.example (safe to commit)
VPS_IP=your.vps.ip.address
DB_PASSWORD=your_secure_database_password_here
SECRET_KEY=generate_with_openssl_rand_hex_32
```

## 🔒 Setting Up Secrets for Deployment

### First-Time Setup

```bash
# 1. Copy example files
cp .env.local.example .env.local
cp .env.prod.example .env.prod

# 2. Generate secure secrets
openssl rand -hex 32  # Use this for SECRET_KEY

# 3. Edit .env.prod with real values
nano .env.prod  # or vim, code, etc.

# 4. Verify .env.prod is gitignored
git status --ignored | grep .env.prod
# Should show: .env.prod

# 5. NEVER add it to git!
```

### Required Secrets

You need to obtain and configure:

1. **Database Password**
   ```bash
   # Generate strong password
   openssl rand -base64 32
   ```

2. **Backend Secret Key**
   ```bash
   # Generate secret key
   openssl rand -hex 32
   ```

3. **OAuth Credentials**
   - Google: https://console.cloud.google.com/
   - Discord: https://discord.com/developers/applications

4. **VPS Configuration**
   - IP address from your VPS provider
   - SSH access configured

5. **SSL Email**
   - Valid email for Let's Encrypt notifications

## 🚨 Security Checklist Before Each Commit

```bash
# 1. Check what's staged
git status

# 2. Review changes
git diff --cached

# 3. Ensure no secrets in changed files
git diff --cached | grep -i "password\|secret\|key" | grep -v "example\|placeholder"

# 4. Verify .env files are ignored
git status --ignored | grep .env
```

## 🔍 Audit Your Repository

### Check for Accidentally Committed Secrets

```bash
# Search for potential secrets in git history
git log --all --full-history --source --pickaxe-all -S "password"
git log --all --full-history --source --pickaxe-all -S "secret"

# Search current files
grep -r "password\|secret" . --include="*.yml" --include="*.conf" | grep -v "example\|placeholder"
```

### If You Accidentally Committed Secrets

**DO NOT just delete and commit again!** Secrets remain in git history.

1. **Immediately rotate the compromised credentials**
2. **Remove from git history** (requires force push):
   ```bash
   # Use BFG Repo Cleaner or git filter-branch
   # WARNING: This rewrites history!
   git filter-branch --force --index-filter \
     'git rm --cached --ignore-unmatch .env.prod' \
     --prune-empty --tag-name-filter cat -- --all
   ```
3. **Change ALL compromised credentials**
4. **Force push** (coordinate with team first):
   ```bash
   git push --force --all
   ```

## 🔐 Best Practices

### 1. Use Environment Variables

Never hardcode secrets in code:
```python
# ❌ BAD
password = "mypassword123"

# ✅ GOOD
password = os.environ["DB_PASSWORD"]
```

### 2. Keep .env Files Out of Docker Images

Never `COPY .env` in Dockerfiles:
```dockerfile
# ❌ BAD
COPY .env /app/.env

# ✅ GOOD
# Pass env vars at runtime via docker-compose
```

### 3. Use Separate Credentials Per Environment

```bash
# Development
DB_PASSWORD=dev_password_ok_to_be_weak

# Production
DB_PASSWORD=Str0ng!R@nd0m!Pr0d!P@ssw0rd
```

### 4. Regular Security Audits

```bash
# Monthly audit
just security-audit  # (if you add this command)

# Check for exposed secrets
git secrets --scan  # (requires git-secrets tool)
```

## 🛠️ Recommended Tools

### Git Secrets Prevention

Install git-secrets:
```bash
# macOS
brew install git-secrets

# Setup for repo
cd /path/to/squig_league
git secrets --install
git secrets --register-aws  # Catches AWS keys
git secrets --add 'password.*=.*'
git secrets --add 'secret.*=.*'
```

### Pre-commit Hooks

Create `.git/hooks/pre-commit`:
```bash
#!/bin/bash
# Prevent committing .env files
if git diff --cached --name-only | grep -E '^\.env$|^\.env\.local$|^\.env\.prod$'; then
    echo "ERROR: Attempting to commit .env file!"
    echo "These files should never be committed."
    exit 1
fi
```

## 📞 What to Do If Secrets Are Exposed

1. **Immediately rotate ALL credentials**
2. **Check access logs** for unauthorized usage
3. **Review git history** to confirm secrets are removed
4. **Force push** cleaned history
5. **Monitor** for suspicious activity
6. **Document** the incident and lessons learned

## 🎯 Quick Reference

**Safe to commit:**
- `*.example` files
- Documentation with placeholders
- Code and configuration templates

**NEVER commit:**
- `.env*` files (except `.example`)
- Files with real passwords/keys/secrets
- IP addresses, connection strings
- Private SSL certificates

**When in doubt:** Ask before committing!
