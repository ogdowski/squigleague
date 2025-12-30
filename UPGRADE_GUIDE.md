# Upgrade from Main Branch to from_scratch (v0.3.0)

## Current State on VPS
- ✅ SSL certificates exist and are valid
- ⚠️ Nginx config uses old service names (squig → backend)
- ⚠️ Old Herald app running instead of new backend/frontend

## Safe Upgrade Process

### Step 1: Backup current state (on VPS)

```bash
ssh root@YOUR_VPS_IP
cd ~/squig_league

# Backup current working config
cp nginx/nginx.conf nginx/nginx.conf.pre-upgrade-backup
cp .env.prod .env.prod.backup

# Note current containers
docker-compose ps > containers-before-upgrade.txt
```

### Step 2: Prepare new nginx config

```bash
# On your local machine
cd ~/Projects/squig_league

# Copy the production HTTPS nginx config
# (this already has SSL configured for squigleague.com)
cp nginx/nginx.prod.conf nginx/nginx.conf.new
```

### Step 3: Deploy new version (automatic!)

```bash
# On your local machine

# 1. Release new version (builds and pushes ALL images including nginx)
just release 0.3.0

# 2. Deploy to VPS (pulls new backend, frontend, AND nginx)
just vps-update
```

This will:
- ✅ Pull new backend image (version 0.3.0)
- ✅ Pull new frontend image (version 0.3.0)
- ✅ Pull new nginx image (version 0.3.0 with updated config!)
- ✅ Keep existing SSL certificates (in volumes)
- ✅ Automatically restart all services

### Step 4: Verify everything works

```bash
# Test HTTPS
curl -I https://squigleague.com

# Should return 200 OK, not redirect to herald

# Test API
curl https://squigleague.com/api/health

# Test stats endpoint
curl https://squigleague.com/api/matchup/stats
```

### Step 5: Migrate Herald data (optional)

If you want to preserve the 2 active herald exchanges:

```bash
# On VPS
just vps-migrate-herald
```

## What Changed

### Service Names
- `squig:8000` → `backend:8000`
- Herald app → Backend (FastAPI) + Frontend (Vue)

### Routing
**Old (Herald):**
- squigleague.com → redirects to herald.squigleague.com
- herald.squigleague.com → Herald app

**New (v0.3.0):**
- squigleague.com → Main app
- /api/* → Backend API
- /* → Frontend SPA

### SSL Configuration
- ✅ No changes needed
- ✅ Certificates already exist
- ✅ Auto-renewal continues to work

## Rollback Plan (if needed)

If something goes wrong:

```bash
ssh root@YOUR_VPS_IP
cd ~/squig_league

# Restore old nginx config
cp nginx/nginx.conf.pre-upgrade-backup nginx/nginx.conf
docker-compose restart nginx

# Restore old .env.prod (if needed)
cp .env.prod.backup .env.prod

# Pull old version (check what version was running)
docker-compose down
docker-compose up -d
```

## One-Command Upgrade

It's really just two commands:

```bash
# 1. Build and push all images (backend, frontend, nginx)
just release 0.3.0

# 2. Deploy to VPS
just vps-update
```

That's it! The nginx config is now versioned with the image.

## Post-Upgrade Verification

```bash
# Check all services are healthy
just vps-status

# Check logs for errors
just vps-logs

# Test the app
curl https://squigleague.com/api/matchup/stats
# Should return: {"exchanges_completed": X, "exchanges_expired": Y, "version": "0.3.0"}
```
