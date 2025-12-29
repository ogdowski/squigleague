# Squig League - justfile
# Modern command runner for building, deploying, and managing Herald

# Load environment variables from .env files
set dotenv-load := true
set dotenv-filename := ".env.local"

# VPS Configuration (loaded from .env files)
VPS_IP := env_var_or_default('VPS_IP', '')
VPS_USER := env_var_or_default('VPS_USER', 'root')
VPS_HOST := VPS_USER + "@" + VPS_IP

# Docker Registry Configuration
IMAGE_PREFIX := env_var_or_default('IMAGE_PREFIX', 'ogdowski')
IMAGE_NAME := env_var_or_default('IMAGE_NAME', 'private')
SQUIG_VERSION := env_var_or_default('SQUIG_VERSION', '0.1')
SL_IMAGE := IMAGE_PREFIX + "/" + IMAGE_NAME
BACKEND_TAG := "squigleague-" + SQUIG_VERSION
FRONTEND_TAG := "squigleague-frontend-" + SQUIG_VERSION

# Default recipe (shows help)
default:
    @just --list

# Show detailed help
help:
    @echo "Squig League - Available Commands"
    @echo "======================================"
    @echo ""
    @echo "Quick Start:"
    @echo "  just dev              - Start development environment"
    @echo "  just logs             - View logs"
    @echo "  just down             - Stop services"
    @echo ""
    @echo "Development:"
    @echo "  just dev              - Start development environment (no SSL)"
    @echo "  just up               - Start dev services in background"
    @echo "  just prod             - Start production environment (with SSL)"
    @echo "  just down             - Stop all services"
    @echo "  just restart          - Restart all services"
    @echo "  just logs             - Show logs (all services)"
    @echo "  just logs-squig       - Show Squig logs only"
    @echo "  just logs-db          - Show PostgreSQL logs only"
    @echo ""
    @echo "Shell Access:"
    @echo "  just shell            - Open shell in local Squig container"
    @echo "  just shell-prod       - Open shell in prod Squig container"
    @echo "  just env-local        - Check local environment variables"
    @echo "  just env-prod         - Check prod environment variables"
    @echo ""
    @echo "Environment:"
    @echo "  just env-check        - Check environment configuration"
    @echo "  just env-create-local - Create .env.local from template"
    @echo "  just env-create-prod  - Create .env.prod from template"
    @echo "  just version          - Show current version"
    @echo ""
    @echo "Releases:"
    @echo "  just release VERSION    - Full release: version bump, commit, tag, build, push"
    @echo "  just gh-release VERSION - Create GitHub release (requires gh CLI)"
    @echo ""
    @echo "Database:"
    @echo "  just db-connect       - Connect to PostgreSQL shell"
    @echo "  just db-backup        - Backup database"
    @echo "  just db-restore FILE  - Restore database from backup"
    @echo "  just db-reset         - Reset database (DANGER!)"
    @echo ""
    @echo "VPS Management:"
    @echo "  just ssh-prod         - SSH into production VPS"
    @echo "  just vps-logs         - View logs on VPS"
    @echo "  just vps-status       - Check services status on VPS"
    @echo "  just vps-update       - Update services on VPS (syncs .env.prod)"
    @echo "  just vps-sync-compose - Sync docker-compose files to VPS"
    @echo "  just vps-sync-nginx   - Sync nginx configs to VPS"
    @echo "  just vps-sync-all     - Sync all configs to VPS"
    @echo ""
    @echo "SSL/Certificates:"
    @echo "  just ssl-cert DOMAIN EMAIL - Obtain SSL certificate"
    @echo "  just ssl-cert-all EMAIL    - Obtain SSL for all domains"
    @echo "  just ssl-renew            - Renew SSL certificates"
    @echo ""
    @echo "Docker Images:"
    @echo "  just build            - Build all images"
    @echo "  just push             - Push multi-arch image to registry"
    @echo "  just pull             - Pull image from registry"
    @echo "  just inspect-image    - Inspect image manifest (verify multi-arch)"
    @echo ""
    @echo "Monitoring:"
    @echo "  just stats            - Show container resource usage"
    @echo "  just health           - Check Squig health"
    @echo "  just ps               - Show running containers"
    @echo ""
    @echo "Admin:"
    @echo "  just admin-resources  - Check server resources (requires admin key)"
    @echo "  just admin-abuse      - Check for abusive IPs (requires admin key)"
    @echo ""
    @echo "Cleanup:"
    @echo "  just clean            - Stop and remove containers"
    @echo "  just clean-all        - Remove containers, volumes, and images"
    @echo ""

# ═══════════════════════════════════════════════
# DEVELOPMENT
# ═══════════════════════════════════════════════

# Start development environment
dev:
    @echo "🚀 Starting development environment..."
    @if [ ! -f .env.local ]; then \
        echo "⚠️  .env.local not found, copying from .env.local.example"; \
        cp .env.local.example .env.local; \
        echo "✅ .env.local created with development defaults"; \
    fi
    @echo "📝 Using .env.local for configuration"
    docker-compose --env-file .env.local -f docker-compose.yml -f docker-compose.dev.yml up

# Start services in background
up:
    @echo "🚀 Starting services in background..."
    @if [ ! -f .env.local ]; then \
        echo "⚠️  .env.local not found, copying from .env.local.example"; \
        cp .env.local.example .env.local; \
        echo "✅ .env.local created with development defaults"; \
    fi
    @echo "📝 Using .env.local for configuration"
    docker-compose --env-file .env.local -f docker-compose.yml -f docker-compose.dev.yml up -d
    @echo "✅ Services started!"
    @echo "📊 Run 'just logs' to view logs"

# Start production environment (with SSL)
prod:
    @echo "🚀 Starting PRODUCTION environment..."
    @if [ ! -f .env.prod ]; then \
        echo "❌ .env.prod file required for production!"; \
        echo "📝 Create it from template: just env-create-prod"; \
        echo "⚙️  Then edit .env.prod and set VPS_IP, passwords, and domains"; \
        exit 1; \
    fi
    @echo "📝 Using .env.prod for configuration"
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env.prod up -d --build
    @echo "✅ Production services started!"
    @echo "ℹ️  Note: Currently running in HTTP-only mode."
    @echo "ℹ️  To enable SSL, edit docker-compose.prod.yml and run 'just vps-update'"

# Stop all services
down:
    @echo "🛑 Stopping all services..."
    docker-compose down
    @echo "✅ Services stopped"

# Restart all services
restart:
    @echo "🔄 Restarting all services..."
    docker-compose restart
    @echo "✅ Services restarted"

# Show logs (all services)
logs:
    @echo "📋 Showing logs (Ctrl+C to exit)..."
    docker-compose logs -f

# Show backend logs only
logs-backend:
    @echo "📋 Showing backend logs..."
    docker-compose logs -f backend

# Legacy command (kept for compatibility)
logs-squig: logs-backend
logs-herald: logs-backend

# Show PostgreSQL logs only
logs-db:
    @echo "📋 Showing PostgreSQL logs..."
    docker-compose logs -f postgres

# ═══════════════════════════════════════════════
# ENVIRONMENT
# ═══════════════════════════════════════════════

# Check environment configuration
env-check:
    @echo "🔍 Checking environment configuration..."
    @echo ""
    @echo "Local Development (.env.local):"
    @if [ ! -f .env.local ]; then \
        echo "  ❌ .env.local not found - run 'just dev' to create it"; \
    else \
        echo "  ✅ .env.local exists"; \
        echo "  Variables (values hidden):"; \
        grep -v '^#' .env.local | grep -v '^$$' | sed 's/^/    /' | sed 's/=.*/=***/' || true; \
    fi
    @echo ""
    @echo "Production (.env.prod):"
    @if [ ! -f .env.prod ]; then \
        echo "  ⚠️  .env.prod not found - run 'just env-create-prod'"; \
    else \
        echo "  ✅ .env.prod exists"; \
        echo "  Variables (values hidden):"; \
        grep -v '^#' .env.prod | grep -v '^$$' | sed 's/^/    /' | sed 's/=.*/=***/' || true; \
    fi

# Create .env.local from template
env-create-local:
    @if [ -f .env.local ]; then \
        echo "⚠️  .env.local already exists. Delete it first if you want to recreate."; \
        exit 1; \
    fi
    cp .env.local.example .env.local
    @echo "✅ Created .env.local with development defaults"

# Create .env.prod from template
env-create-prod:
    @if [ -f .env.prod ]; then \
        echo "⚠️  .env.prod already exists. Delete it first if you want to recreate."; \
        exit 1; \
    fi
    cp .env.prod.example .env.prod
    @echo "✅ Created .env.prod from template"
    @echo "⚙️  Edit .env.prod and set VPS_IP, passwords, and domains"

# Show current version
version:
    @echo "📦 Current Squig League version: {{SQUIG_VERSION}}"
    @echo "Backend: {{SL_IMAGE}}:{{BACKEND_TAG}}"
    @echo "Frontend: {{SL_IMAGE}}:{{FRONTEND_TAG}}"

# Full release workflow - updates versions, commits, tags, builds, and pushes
release VERSION:
    @echo "🚀 Starting full release workflow for v{{VERSION}}..."
    @echo ""
    @echo "📋 Step 1/7: Checking for uncommitted changes..."
    @if ! git diff-index --quiet HEAD --; then \
        echo "❌ You have uncommitted changes. Commit or stash them first."; \
        exit 1; \
    fi
    @echo "✅ Working directory clean"
    @echo ""
    @echo "📋 Step 2/7: Updating package.json version..."
    @sed -i '' 's/"version": "[^"]*"/"version": "{{VERSION}}"/' frontend/package.json
    @echo "✅ Updated frontend/package.json to v{{VERSION}}"
    @echo ""
    @echo "📋 Step 3/7: Updating backend version..."
    @sed -i '' 's/"version": "[^"]*"/"version": "{{VERSION}}"/' backend/app/matchup/routes.py
    @echo "✅ Updated backend/app/matchup/routes.py to v{{VERSION}}"
    @echo ""
    @echo "📋 Step 4/7: Updating environment files..."
    @sed -i '' 's/SQUIG_VERSION=.*/SQUIG_VERSION={{VERSION}}/' .env.local || true
    @sed -i '' 's/SQUIG_VERSION=.*/SQUIG_VERSION={{VERSION}}/' .env.local.example || true
    @sed -i '' 's/SQUIG_VERSION=.*/SQUIG_VERSION={{VERSION}}/' .env.prod || true
    @sed -i '' 's/SQUIG_VERSION=.*/SQUIG_VERSION={{VERSION}}/' .env.prod.example || true
    @echo "✅ Updated env files to v{{VERSION}}"
    @echo ""
    @echo "📋 Step 5/7: Committing changes..."
    git add frontend/package.json backend/app/matchup/routes.py .env.local .env.local.example .env.prod .env.prod.example
    git commit -m "Release v{{VERSION}}"
    @echo "✅ Changes committed"
    @echo ""
    @echo "📋 Step 6/7: Creating and pushing git tag..."
    git tag -a v{{VERSION}} -m "Release v{{VERSION}}"
    git push origin main
    git push origin v{{VERSION}}
    @echo "✅ Tag v{{VERSION}} created and pushed"
    @echo ""
    @echo "📋 Step 7/7: Building and pushing Docker images..."
    @echo "🏗️  This will build multi-arch images and push to registry..."
    just push
    @echo ""
    @echo "✅ Release v{{VERSION}} complete!"
    @echo ""
    @echo "📦 Next steps:"
    @echo "  • Deploy to VPS: just vps-update"
    @echo "  • Create GitHub release: gh release create v{{VERSION}} --generate-notes"

# Create GitHub release with notes (requires gh CLI)
gh-release VERSION:
    @echo "🚀 Creating GitHub release v{{VERSION}}..."
    @if ! command -v gh >/dev/null 2>&1; then \
        echo "❌ GitHub CLI (gh) not installed."; \
        echo "Install: brew install gh"; \
        exit 1; \
    fi
    gh release create v{{VERSION}} --generate-notes --title "v{{VERSION}}"
    @echo "✅ GitHub release v{{VERSION}} created!"
    @echo "View at: https://github.com/ogdowski/squigleague/releases/tag/v{{VERSION}}"

# ═══════════════════════════════════════════════
# BUILDING
# ═══════════════════════════════════════════════

# Build all Docker images (uses default driver for fast local builds)
build:
    @echo "🔨 Building all images..."
    docker buildx use default
    docker-compose build
    @echo "✅ Build complete"

# Build backend only (legacy - use 'build' instead)
build-backend:
    @echo "🔨 Building backend..."
    docker-compose build backend
    @echo "✅ Backend build complete"

# Legacy commands (kept for compatibility)
build-squig: build-backend
build-herald: build-backend

# Force rebuild all images (no cache)
rebuild:
    @echo "🔨 Force rebuilding all images (no cache)..."
    docker-compose build --no-cache
    @echo "✅ Rebuild complete"

# ═══════════════════════════════════════════════
# DOCKER REGISTRY
# ═══════════════════════════════════════════════

# Login to Docker registry
registry-login:
    @echo "🔐 Logging into Docker Hub..."
    docker login
    @echo "✅ Login successful"

# Build and push Squig League images to registry (multi-arch: amd64 + arm64)
push:
    @echo "📦 Building and pushing Squig League images (multi-arch)..."
    @echo "Image: {{SL_IMAGE}}"
    @echo "Backend tag: {{BACKEND_TAG}}"
    @echo "Frontend tag: {{FRONTEND_TAG}}"
    @echo "🔧 Setting up buildx..."
    docker buildx create --name squig-builder --use 2>/dev/null || docker buildx use squig-builder
    @echo "🏗️  Building backend for linux/amd64 and linux/arm64..."
    cd herald && docker buildx build \
        --platform linux/amd64,linux/arm64 \
        -t {{SL_IMAGE}}:{{BACKEND_TAG}} \
        -t {{SL_IMAGE}}:latest \
        --push \
        .
    @echo "✅ Backend image pushed!"
    @echo "🏗️  Building frontend for linux/amd64 and linux/arm64..."
    cd frontend && docker buildx build \
        --platform linux/amd64,linux/arm64 \
        -t {{SL_IMAGE}}:{{FRONTEND_TAG}} \
        --push \
        .
    @echo "✅ Frontend image pushed!"
    @echo "✅ All images pushed successfully!"
    @echo "Backend: {{SL_IMAGE}}:{{BACKEND_TAG}}"
    @echo "Frontend: {{SL_IMAGE}}:{{FRONTEND_TAG}}"
    @echo "Platforms: linux/amd64, linux/arm64"

# Pull Squig League images from registry
pull:
    @echo "📥 Pulling Squig League images from registry..."
    @echo "Backend: {{SL_IMAGE}}:{{BACKEND_TAG}}"
    docker pull {{SL_IMAGE}}:{{BACKEND_TAG}}
    docker tag {{SL_IMAGE}}:{{BACKEND_TAG}} squig_league-squig:latest
    @echo "✅ Backend image pulled and tagged"
    @echo "Frontend: {{SL_IMAGE}}:{{FRONTEND_TAG}}"
    docker pull {{SL_IMAGE}}:{{FRONTEND_TAG}}
    docker tag {{SL_IMAGE}}:{{FRONTEND_TAG}} squig_league-frontend:latest
    @echo "✅ Frontend image pulled and tagged"
    @echo "✅ All images pulled successfully!"

# Inspect image manifests (verify multi-arch)
inspect-image:
    @echo "🔍 Inspecting backend manifest..."
    docker buildx imagetools inspect {{SL_IMAGE}}:{{BACKEND_TAG}}
    @echo ""
    @echo "🔍 Inspecting frontend manifest..."
    docker buildx imagetools inspect {{SL_IMAGE}}:{{FRONTEND_TAG}}

# Legacy commands (kept for compatibility)
push-herald: push
pull-herald: pull

# ═══════════════════════════════════════════════
# SHELL ACCESS
# ═══════════════════════════════════════════════

# Shell into local Squig container
shell:
    @echo "🐚 Opening shell in backend container..."
    docker-compose exec backend /bin/sh

# Check local environment variables
env-local:
    @echo "🔍 Local backend environment variables:"
    @docker-compose exec backend env | grep -E 'DATABASE_URL|SECRET_KEY' || echo "❌ Container not running"
    @echo ""
    @echo "🔍 Local Postgres environment variables:"
    @docker-compose exec postgres env | grep -E 'POSTGRES_PASSWORD|POSTGRES_USER|POSTGRES_DB' || echo "❌ Container not running"

# ═══════════════════════════════════════════════
# VPS MANAGEMENT
# ═══════════════════════════════════════════════

# SSH into production VPS
ssh-prod:
    #!/usr/bin/env bash
    set -a
    if [ -f .env.prod ]; then
        source .env.prod
    fi
    set +a
    if [ -z "$VPS_IP" ]; then
        echo "❌ VPS_IP not set. Create .env.prod and set VPS_IP"
        exit 1
    fi
    echo "🔐 Connecting to production VPS (${VPS_IP})..."
    ssh ${VPS_USER}@${VPS_IP}

# Check production environment variables
env-prod:
    #!/usr/bin/env bash
    set -a
    if [ -f .env.prod ]; then
        source .env.prod
    fi
    set +a
    if [ -z "$VPS_IP" ]; then
        echo "❌ VPS_IP not set. Create .env.prod and set VPS_IP"
        exit 1
    fi
    echo "🔍 Production environment variables on ${VPS_USER}@${VPS_IP}:"
    echo ""
    echo "📄 .env.prod file:"
    ssh ${VPS_USER}@${VPS_IP} "cd ~/squig_league && cat .env.prod 2>/dev/null || echo '❌ .env.prod not found'"
    echo ""
    echo "🐳 Backend container environment:"
    ssh ${VPS_USER}@${VPS_IP} "cd ~/squig_league && docker-compose exec -T backend env | grep -E 'DATABASE_URL|SECRET_KEY' || echo '❌ Container not running'"
    echo ""
    echo "🐳 Postgres container environment:"
    ssh ${VPS_USER}@${VPS_IP} "cd ~/squig_league && docker-compose exec -T postgres env | grep -E 'POSTGRES_PASSWORD|POSTGRES_USER|POSTGRES_DB' || echo '❌ Container not running'"

# Shell into production backend container
shell-prod:
    #!/usr/bin/env bash
    set -a
    if [ -f .env.prod ]; then
        source .env.prod
    fi
    set +a
    if [ -z "$VPS_IP" ]; then
        echo "❌ VPS_IP not set. Create .env.prod and set VPS_IP"
        exit 1
    fi
    echo "🐚 Opening shell in production backend container..."
    ssh -t ${VPS_USER}@${VPS_IP} "cd ~/squig_league && docker-compose exec backend /bin/sh"

# View logs on VPS
vps-logs:
    #!/usr/bin/env bash
    set -a
    if [ -f .env.prod ]; then
        source .env.prod
    fi
    set +a
    if [ -z "$VPS_IP" ]; then
        echo "❌ VPS_IP not set. Create .env.prod and set VPS_IP"
        exit 1
    fi
    echo "📋 Viewing logs on ${VPS_USER}@${VPS_IP}..."
    ssh ${VPS_USER}@${VPS_IP} "cd ~/squig_league && docker-compose logs -f --tail=100"

# Check services status on VPS
vps-status:
    #!/usr/bin/env bash
    set -a
    if [ -f .env.prod ]; then
        source .env.prod
    fi
    set +a
    if [ -z "$VPS_IP" ]; then
        echo "❌ VPS_IP not set. Create .env.prod and set VPS_IP"
        exit 1
    fi
    echo "📊 Checking status on ${VPS_USER}@${VPS_IP}..."
    ssh ${VPS_USER}@${VPS_IP} "cd ~/squig_league && docker-compose ps"

# Update services on VPS (pulls latest version from .env.prod)
vps-update:
    #!/usr/bin/env bash
    set -a
    if [ -f .env.prod ]; then
        source .env.prod
    fi
    set +a
    if [ -z "$VPS_IP" ]; then
        echo "❌ VPS_IP not set. Create .env.prod and set VPS_IP"
        exit 1
    fi
    echo "🔄 Updating services on ${VPS_USER}@${VPS_IP} to version squigleague-${SQUIG_VERSION}..."
    echo "📦 Syncing .env.prod to VPS..."
    scp .env.prod ${VPS_USER}@${VPS_IP}:~/squig_league/.env.prod
    echo "🐳 Pulling and restarting services..."
    ssh ${VPS_USER}@${VPS_IP} "cd ~/squig_league && docker-compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env.prod pull && docker-compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env.prod up -d"
    echo "✅ Update complete! Running version: squigleague-${SQUIG_VERSION}"

# Sync docker-compose.prod.yml to VPS
vps-sync-compose:
    #!/usr/bin/env bash
    set -a
    if [ -f .env.prod ]; then
        source .env.prod
    fi
    set +a
    if [ -z "$VPS_IP" ]; then
        echo "❌ VPS_IP not set. Create .env.prod and set VPS_IP"
        exit 1
    fi
    echo "📦 Syncing docker-compose files to VPS..."
    scp docker-compose.yml ${VPS_USER}@${VPS_IP}:~/squig_league/docker-compose.yml
    scp docker-compose.prod.yml ${VPS_USER}@${VPS_IP}:~/squig_league/docker-compose.prod.yml
    echo "✅ Sync complete!"

# Sync nginx configs to VPS
vps-sync-nginx:
    #!/usr/bin/env bash
    set -a
    if [ -f .env.prod ]; then
        source .env.prod
    fi
    set +a
    if [ -z "$VPS_IP" ]; then
        echo "❌ VPS_IP not set. Create .env.prod and set VPS_IP"
        exit 1
    fi
    if [ -z "$ADMIN_IP" ]; then
        echo "❌ ADMIN_IP not set in .env.prod"
        exit 1
    fi
    echo "📦 Syncing nginx configs to VPS..."
    echo "🔧 Substituting ADMIN_IP=${ADMIN_IP} in nginx.conf..."
    envsubst '${ADMIN_IP}' < nginx/nginx.conf | ssh ${VPS_USER}@${VPS_IP} "cat > ~/squig_league/nginx/nginx.conf"
    scp nginx/nginx.http-only.conf ${VPS_USER}@${VPS_IP}:~/squig_league/nginx/nginx.http-only.conf
    echo "✅ Sync complete!"
    echo "⚠️  Restart nginx: ssh ${VPS_USER}@${VPS_IP} 'cd ~/squig_league && docker-compose restart nginx'"

# Sync all VPS configs (compose + nginx)
vps-sync-all:
    @echo "📦 Syncing all configs to VPS..."
    just vps-sync-compose
    just vps-sync-nginx
    @echo "✅ All configs synced!"

# ═══════════════════════════════════════════════
# DATABASE
# ═══════════════════════════════════════════════

# Connect to PostgreSQL shell
db-connect:
    @echo "🗄️  Connecting to PostgreSQL..."
    @echo "Commands: \dt (list tables), \d tablename (describe table), \q (quit)"
    docker exec -it squig-postgres psql -U squig -d squigleague

# Backup database to file
db-backup:
    @echo "💾 Creating database backup..."
    @mkdir -p backups
    docker exec squig-postgres pg_dump -U squig squigleague > backups/backup_$(date +%Y%m%d_%H%M%S).sql
    @echo "✅ Backup created in backups/"
    @ls -lh backups/ | tail -1

# Restore database from backup file
db-restore FILE:
    @echo "⚠️  Restoring database from {{FILE}}"
    @echo "This will overwrite current data. Press Ctrl+C to cancel, or Enter to continue..."
    @read confirm
    docker exec -i squig-postgres psql -U squig squigleague < {{FILE}}
    @echo "✅ Database restored"

# Reset database (DANGER!)
db-reset:
    @echo "⚠️  WARNING: This will delete all data!"
    @echo "Press Ctrl+C to cancel, or Enter to continue..."
    @read confirm
    @echo "🗑️  Dropping and recreating database..."
    docker exec -i squig-postgres psql -U squig -c "DROP DATABASE IF EXISTS squigleague;"
    docker exec -i squig-postgres psql -U squig -c "CREATE DATABASE squigleague;"
    docker exec -i squig-postgres psql -U squig squigleague < database/init.sql
    @echo "✅ Database reset complete"

# ═══════════════════════════════════════════════
# SSL CERTIFICATES
# ═══════════════════════════════════════════════

# Obtain SSL certificate for a domain
ssl-cert DOMAIN EMAIL:
    @echo "🔒 Obtaining SSL certificate for {{DOMAIN}}..."
    docker-compose run --rm certbot certonly \
        --webroot --webroot-path=/var/www/certbot \
        --email {{EMAIL}} --agree-tos --no-eff-email \
        -d {{DOMAIN}}
    @echo "✅ Certificate obtained"
    @echo "🔄 Restarting nginx..."
    docker-compose restart nginx
    @echo "✅ Done! Your site should now be accessible via HTTPS"

# Obtain SSL certificates for all domains
ssl-cert-all EMAIL:
    @echo "🔒 Obtaining SSL certificates for all domains..."
    docker-compose run --rm certbot certonly \
        --webroot --webroot-path=/var/www/certbot \
        --email {{EMAIL}} --agree-tos --no-eff-email \
        -d squigleague.com \
        -d www.squigleague.com \
        -d herald.squigleague.com
    @echo "✅ Certificates obtained for all domains"
    @echo "🔄 Restarting nginx..."
    docker-compose restart nginx
    @echo "✅ Done! All sites should now be accessible via HTTPS"

# Renew SSL certificates
ssl-renew:
    @echo "🔄 Renewing SSL certificates..."
    docker-compose run --rm certbot renew
    docker-compose restart nginx
    @echo "✅ Certificates renewed"

# ═══════════════════════════════════════════════
# MONITORING
# ═══════════════════════════════════════════════

# Show container resource usage
stats:
    @echo "📊 Container resource usage:"
    docker stats --no-stream

# Check Squig health
health:
    @echo "🏥 Checking Squig health..."
    @curl -s http://localhost/api/health | python3 -m json.tool || echo "❌ Squig is not responding"

# Show running containers
ps:
    @echo "📦 Running containers:"
    docker-compose ps

# ═══════════════════════════════════════════════
# CLEANUP
# ═══════════════════════════════════════════════

# Stop and remove containers
clean:
    @echo "🧹 Cleaning up containers..."
    docker-compose down
    @echo "✅ Cleanup complete"

# Remove containers, volumes, and images
clean-all:
    @echo "⚠️  WARNING: This will remove containers, volumes, and images!"
    @echo "Press Ctrl+C to cancel, or Enter to continue..."
    @read confirm
    docker-compose down -v --rmi all
    @echo "✅ Deep cleanup complete"

# Remove unused Docker resources
prune:
    @echo "🧹 Removing unused Docker resources..."
    docker system prune -f
    @echo "✅ Prune complete"

# ═══════════════════════════════════════════════
# TESTING
# ═══════════════════════════════════════════════

# Create test exchange
test-exchange:
    @echo "🧪 Creating test exchange..."
    @curl -X POST http://localhost:8000/exchange/create \
        -H "Content-Type: application/json" \
        -d '{"list_content":"Test Army List\n\nHQ:\n- Test Captain\n\nTroops:\n- 10x Test Marines"}' \
        | python3 -m json.tool

# ═══════════════════════════════════════════════
# ADMIN ENDPOINTS
# ═══════════════════════════════════════════════

# Get server resources (requires admin key from .env.prod)
admin-resources:
    #!/usr/bin/env bash
    set -a
    if [ -f .env.prod ]; then
        source .env.prod
    fi
    set +a
    if [ -z "$HERALD_ADMIN_KEY" ]; then
        echo "❌ HERALD_ADMIN_KEY not set in .env.prod"
        exit 1
    fi
    ENCODED_KEY=$(printf %s "$HERALD_ADMIN_KEY" | jq -sRr @uri)
    curl -s "https://herald.squigleague.com/admin/resources?admin_key=$ENCODED_KEY" | python3 -m json.tool

# Get abuse report (requires admin key from .env.prod)
admin-abuse MIN_REQUESTS="100" HOURS="1":
    #!/usr/bin/env bash
    set -a
    if [ -f .env.prod ]; then
        source .env.prod
    fi
    set +a
    if [ -z "$HERALD_ADMIN_KEY" ]; then
        echo "❌ HERALD_ADMIN_KEY not set in .env.prod"
        exit 1
    fi
    ENCODED_KEY=$(printf %s "$HERALD_ADMIN_KEY" | jq -sRr @uri)
    curl -s "https://herald.squigleague.com/admin/abuse-report?admin_key=$ENCODED_KEY&min_requests={{MIN_REQUESTS}}&hours={{HOURS}}" | python3 -m json.tool
