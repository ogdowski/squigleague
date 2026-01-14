# SquigLeague Production Deployment Guide

## Prerequisites

1. VPS with Docker and Docker Compose installed
2. Domain name (squigleague.com) pointing to VPS IP
3. `.env.prod` file configured with production values

## First-Time Deployment with HTTPS

### Step 1: Prepare for deployment

```bash
# Ensure you're on the correct branch
git checkout from_scratch

# Run the release command to build and push images
just release 0.3.0
```

### Step 2: Deploy to VPS (HTTP-only initially)

```bash
# Copy HTTP-only nginx config for initial setup
cp nginx/nginx.http-only.conf nginx/nginx.conf

# Deploy to VPS
just vps-update
```

### Step 3: Setup SSL Certificates on VPS

SSH into your VPS and run:

```bash
cd ~/squig_league

# Run the SSL setup command (replace with your email)
just ssl-setup your-email@example.com
```

This will:
1. ✅ Start services with HTTP-only config
2. ✅ Obtain SSL certificates from Let's Encrypt
3. ✅ Switch to HTTPS config automatically
4. ✅ Restart nginx with SSL enabled

### Step 4: Verify HTTPS is working

```bash
# Check that SSL is active
curl -I https://squigleague.com

# Should return 200 OK with SSL headers
```

## Updating Deployment

For subsequent deployments (after SSL is already setup):

```bash
# 1. Build new version
just release 0.3.1

# 2. Deploy to VPS (will use existing SSL certs)
just vps-update
```

## SSL Certificate Management

### Auto-Renewal

The certbot container automatically renews certificates every 12 hours. No manual intervention needed.

### Manual Renewal

If you need to manually renew:

```bash
just ssl-renew
```

### Adding New Domains

To add a new subdomain to the certificate:

```bash
just ssl-cert-all your-email@example.com
```

Then update `nginx/nginx.prod.conf` to include the new domain.

## Troubleshooting

### Nginx fails to start with SSL errors

**Problem:** Nginx can't find SSL certificate files

**Solution:**
```bash
# Switch back to HTTP-only config
cp nginx/nginx.http-only.conf nginx/nginx.conf
docker-compose restart nginx

# Re-run SSL setup
just ssl-setup your-email@example.com
```

### Certificate validation fails

**Problem:** Let's Encrypt can't validate domain ownership

**Check:**
1. Domain DNS points to correct IP
2. Port 80 is accessible (firewall rules)
3. Nginx is running and serving `.well-known/acme-challenge/`

```bash
# Test ACME challenge endpoint
curl http://squigleague.com/.well-known/acme-challenge/test
```

### Viewing logs

```bash
# All logs
just vps-logs

# Specific service
just vps-logs nginx
just vps-logs certbot
```

## Migration from Herald

If migrating from the old Herald system with existing exchanges:

```bash
# After deployment, run the migration
just vps-migrate-herald
```

This will copy the 2 active herald exchanges to the new matchups table.

## Architecture

```
┌─────────────────────────────────────────┐
│            Internet                     │
└──────────────┬──────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│  Nginx (Port 80/443)                     │
│  - SSL Termination                       │
│  - Reverse Proxy                         │
└──┬───────────────────────┬───────────────┘
   │                       │
   ▼                       ▼
┌──────────┐        ┌─────────────┐
│ Backend  │        │  Frontend   │
│ (FastAPI)│        │  (Vue/Nginx)│
└────┬─────┘        └─────────────┘
     │
     ▼
┌──────────┐
│PostgreSQL│
└──────────┘
```

## Security Notes

- SSL certificates auto-renew every 12 hours
- Admin routes are IP-restricted (see nginx.prod.conf)
- Database passwords stored in .env.prod (never commit!)
- HTTPS redirects all HTTP traffic automatically

## Monitoring

Check service health:
```bash
just vps-status
just health
```

View resource usage:
```bash
just stats
```
