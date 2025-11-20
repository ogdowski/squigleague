# SSL Certificate Setup Guide

## Prerequisites

Before getting SSL certificates, ensure:
1. Your VPS is running and accessible
2. Application is deployed and running on HTTP (`just prod`)
3. `.env.prod` is configured with your VPS_IP
4. DNS records are configured and propagated

## Step 1: Configure DNS Records

At your domain registrar (where you bought squigleague.com), add these A records:

**Get your VPS IP:**
```bash
# Check your .env.prod file
grep VPS_IP .env.prod
```

**Add DNS A records:**

| Type | Name/Host | Value | TTL |
|------|-----------|-------|-----|
| A | @ | YOUR_VPS_IP | 3600 |
| A | www | YOUR_VPS_IP | 3600 |
| A | herald | YOUR_VPS_IP | 3600 |

**What this does:**
- `squigleague.com` → points to VPS
- `www.squigleague.com` → points to VPS
- `herald.squigleague.com` → points to VPS

## Step 2: Wait for DNS Propagation

DNS changes can take 5-30 minutes to propagate globally.

**Check if DNS is ready:**

```bash
# From your local machine or VPS
nslookup squigleague.com
nslookup www.squigleague.com
nslookup herald.squigleague.com
```

All three should return your VPS IP address.

**Alternative check:**
```bash
# Test HTTP access works (replace with your domain)
curl http://squigleague.com/health
curl http://herald.squigleague.com/health
```

Both should return: `{"status":"healthy","module":"herald","database":"connected"}`

## Step 3: Get SSL Certificates

SSH into your VPS:

```bash
# Uses VPS_IP from .env.prod
just ssh-prod
cd ~/squig_league
```

### Option A: Using just (Recommended)

```bash
# Get certificates for all domains
just ssl-cert-all your@email.com
```

### Option B: Manual Commands

```bash
# Get certificate for squigleague.com and www.squigleague.com
docker-compose run --rm certbot certonly --webroot \
  --webroot-path=/var/www/certbot \
  -d squigleague.com \
  -d www.squigleague.com \
  --email your@email.com \
  --agree-tos \
  --no-eff-email

# Get certificate for herald.squigleague.com
docker-compose run --rm certbot certonly --webroot \
  --webroot-path=/var/www/certbot \
  -d herald.squigleague.com \
  --email your@email.com \
  --agree-tos \
  --no-eff-email
```

**Expected output:**
```
Successfully received certificate.
Certificate is saved at: /etc/letsencrypt/live/squigleague.com/fullchain.pem
Key is saved at:         /etc/letsencrypt/live/squigleague.com/privkey.pem
```

## Step 4: Enable SSL in Nginx

Currently you're using `nginx/nginx.http-only.conf`. Switch to full SSL config:

```bash
# Restore original nginx config with SSL
cp nginx/nginx.conf.backup nginx/nginx.conf

# Restart nginx to load SSL config
docker-compose restart nginx

# Check nginx logs
docker-compose logs nginx
```

**What this does:**
- Enables HTTPS on port 443
- Redirects all HTTP traffic to HTTPS
- Redirects `squigleague.com` → `herald.squigleague.com`

## Step 5: Verify SSL is Working

```bash
# Test HTTPS
curl https://herald.squigleague.com/health

# Test HTTP redirect
curl -I http://herald.squigleague.com/health

# Test from browser
# Open: https://herald.squigleague.com
```

Expected result:
- HTTPS works with valid certificate (green lock icon)
- HTTP automatically redirects to HTTPS
- `squigleague.com` redirects to `herald.squigleague.com`

## Step 6: Auto-Renewal Setup

Let's Encrypt certificates expire after 90 days. Auto-renewal is already configured.

**Test renewal (dry run):**
```bash
docker-compose run --rm certbot renew --dry-run
```

**Manual renewal (if needed):**
```bash
just ssl-renew
# Or:
docker-compose run --rm certbot renew
docker-compose restart nginx
```

## Troubleshooting

### DNS Not Propagating

**Problem:** `nslookup` doesn't return `91.98.147.232`

**Solutions:**
- Wait longer (can take up to 24 hours in rare cases)
- Clear DNS cache: `sudo dscacheutil -flushcache` (Mac) or `ipconfig /flushdns` (Windows)
- Check with online tool: https://dnschecker.org

### Certificate Request Failed

**Problem:** Certbot fails with "Failed authorization procedure"

**Causes:**
1. DNS not pointing to VPS yet
2. Port 80 not accessible
3. Nginx not serving ACME challenge correctly

**Solutions:**
```bash
# Check DNS
nslookup herald.squigleague.com

# Check port 80 is open (use your VPS IP)
curl http://YOUR_VPS_IP/health

# Check nginx is running
docker-compose ps nginx

# Check nginx logs
docker-compose logs nginx

# Ensure you're using HTTP-only config during cert request
cp nginx/nginx.http-only.conf nginx/nginx.conf
docker-compose restart nginx
```

### Nginx Won't Start After Enabling SSL

**Problem:** Nginx keeps restarting, logs show certificate errors

**Cause:** Nginx config references SSL certs that don't exist yet

**Solution:**
```bash
# Switch back to HTTP-only
cp nginx/nginx.http-only.conf nginx/nginx.conf
docker-compose restart nginx

# Get certificates again
just ssl-cert-all your@email.com

# Verify certs exist
ls -la /var/lib/docker/volumes/squig_league_certbot-etc/_data/live/

# Then switch to SSL config
cp nginx/nginx.conf.backup nginx/nginx.conf
docker-compose restart nginx
```

### Mixed Content Warnings

**Problem:** Browser shows "mixed content" warnings even on HTTPS

**Cause:** Some resources loading via HTTP instead of HTTPS

**Solution:** Already handled - templates use dynamic protocol (`window.location.protocol`)

## Certificate Locations

Certificates are stored in Docker volume:

```bash
# On VPS - view certificates
docker-compose exec nginx ls -la /etc/letsencrypt/live/
```

**Certificates:**
- `/etc/letsencrypt/live/squigleague.com/fullchain.pem`
- `/etc/letsencrypt/live/squigleague.com/privkey.pem`
- `/etc/letsencrypt/live/herald.squigleague.com/fullchain.pem`
- `/etc/letsencrypt/live/herald.squigleague.com/privkey.pem`

## Quick Reference

```bash
# SSH to VPS
just ssh-prod

# Get certificates for all domains
just ssl-cert-all your@email.com

# Get certificate for single domain
just ssl-cert herald.squigleague.com your@email.com

# Test renewal
just ssl-renew
# Or test without actually renewing:
docker-compose run --rm certbot renew --dry-run

# Force renewal
docker-compose run --rm certbot renew --force-renewal

# Restart nginx after changes
docker-compose restart nginx

# Switch to HTTP-only (emergency)
cp nginx/nginx.http-only.conf nginx/nginx.conf
docker-compose restart nginx

# Switch to SSL (normal)
cp nginx/nginx.conf.backup nginx/nginx.conf
docker-compose restart nginx
```

## Summary

1. **Configure DNS** - Point domains to your VPS IP (from `.env.prod`)
2. **Wait for DNS** - Check with `nslookup`
3. **SSH to VPS** - `just ssh-prod`
4. **Get certificates** - `just ssl-cert-all your@email.com`
5. **Enable SSL** - `cp nginx/nginx.conf.backup nginx/nginx.conf`
6. **Restart nginx** - `docker-compose restart nginx`
7. **Test** - `curl https://herald.squigleague.com/health`

## Local Development vs Production

**Local Development:**
- No SSL needed
- Run `just dev`
- Access via `http://localhost:8000`

**Production:**
- SSL required for HTTPS
- Run `just prod` on VPS
- Get SSL certificates with `just ssl-cert-all`
- Access via `https://herald.squigleague.com`
