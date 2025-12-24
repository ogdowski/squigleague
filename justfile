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
    @echo "Testing:"
    @echo "  just test-all         - Run all pre-deployment checks"
    @echo "  just test-unit        - Run unit tests with 100% coverage"
    @echo "  just test-integration - Run integration tests"
    @echo "  just test-uat         - Run UAT acceptance tests"
    @echo "  just build-test       - Build Docker images (test)"
    @echo "  just build-validate   - Validate docker-compose configs"
    @echo "  just test-db-up       - Start test database"
    @echo "  just test-db-down     - Stop test database"
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
    @echo "  just bump VERSION     - Bump version (e.g., just bump 0.2)"
    @echo ""
    @echo "Releases:"
    @echo "  just tag VERSION      - Create git tag for version"
    @echo "  just release VERSION  - Create and push git tag"
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
    docker-compose --env-file .env.local -f docker-compose.yml -f docker-compose.dev.yml up --build

# Start services in background
up:
    @echo "🚀 Starting services in background..."
    @if [ ! -f .env.local ]; then \
        echo "⚠️  .env.local not found, copying from .env.local.example"; \
        cp .env.local.example .env.local; \
        echo "✅ .env.local created with development defaults"; \
    fi
    @echo "📝 Using .env.local for configuration"
    docker-compose --env-file .env.local -f docker-compose.yml -f docker-compose.dev.yml up -d --build
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

# Show Squig logs only
logs-squig:
    @echo "📋 Showing Squig logs..."
    docker-compose logs -f squig

# Legacy command (kept for compatibility)
logs-herald: logs-squig

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

# Bump version in all env files
bump VERSION:
    @echo "📦 Bumping version to {{VERSION}}..."
    @sed -i '' 's/SQUIG_VERSION=.*/SQUIG_VERSION={{VERSION}}/' .env.local
    @sed -i '' 's/SQUIG_VERSION=.*/SQUIG_VERSION={{VERSION}}/' .env.local.example
    @sed -i '' 's/SQUIG_VERSION=.*/SQUIG_VERSION={{VERSION}}/' .env.prod
    @sed -i '' 's/SQUIG_VERSION=.*/SQUIG_VERSION={{VERSION}}/' .env.prod.example
    @echo "✅ Version bumped to {{VERSION}} in all env files"
    @echo ""
    @echo "Next steps:"
    @echo "  1. Update CHANGELOG.md with release notes"
    @echo "  2. git add -A && git commit -m 'Bump version to {{VERSION}}'"
    @echo "  3. just release {{VERSION}}  - Create git tag and GitHub release"
    @echo "  4. just push                 - Build and push new version"
    @echo "  5. just vps-update           - Deploy to VPS"

# Create git tag for version
tag VERSION:
    @echo "🏷️  Creating git tag v{{VERSION}}..."
    git tag -a v{{VERSION}} -m "Release v{{VERSION}}"
    @echo "✅ Tag v{{VERSION}} created"
    @echo "Push tag with: git push origin v{{VERSION}}"

# Create and push git tag
release VERSION:
    @echo "🚀 Creating release v{{VERSION}}..."
    @if ! git diff-index --quiet HEAD --; then \
        echo "❌ You have uncommitted changes. Commit them first."; \
        exit 1; \
    fi
    @echo "📝 Creating git tag..."
    git tag -a v{{VERSION}} -m "Release v{{VERSION}}"
    @echo "📤 Pushing tag to GitHub..."
    git push origin v{{VERSION}}
    @echo "✅ Release v{{VERSION}} created and pushed!"
    @echo ""
    @echo "🌐 Create GitHub release at:"
    @echo "   https://github.com/ogdowski/squigleague/releases/new?tag=v{{VERSION}}"
    @echo ""
    @echo "Or use GitHub CLI: gh release create v{{VERSION}} --generate-notes"

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

# Build all Docker images
build:
    @echo "🔨 Building all images..."
    docker-compose build
    @echo "✅ Build complete"

# Build Squig module only (legacy - use 'build' instead)
build-squig:
    @echo "🔨 Building Squig module..."
    docker-compose build squig
    @echo "✅ Squig module build complete"

# Legacy command (kept for compatibility)
build-herald: build-squig

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
    @echo "🐚 Opening shell in Squig container..."
    docker-compose exec squig /bin/sh

# Check local environment variables
env-local:
    @echo "🔍 Local Squig environment variables:"
    @docker-compose exec squig env | grep -E 'DATABASE_URL|ADMIN_KEY' || echo "❌ Container not running"
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
    echo "🐳 Squig container environment:"
    ssh ${VPS_USER}@${VPS_IP} "cd ~/squig_league && docker-compose exec -T squig env | grep -E 'DATABASE_URL|ADMIN_KEY' || echo '❌ Container not running'"
    echo ""
    echo "🐳 Postgres container environment:"
    ssh ${VPS_USER}@${VPS_IP} "cd ~/squig_league && docker-compose exec -T postgres env | grep -E 'POSTGRES_PASSWORD|POSTGRES_USER|POSTGRES_DB' || echo '❌ Container not running'"

# Shell into production Squig container
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
    echo "🐚 Opening shell in production Squig container..."
    ssh -t ${VPS_USER}@${VPS_IP} "cd ~/squig_league && docker-compose exec squig /bin/sh"

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
    @curl -s http://localhost:8000/health | python3 -m json.tool || echo "❌ Squig is not responding"

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

# Run all pre-deployment checks
test-all:
    @echo "🧪 Running comprehensive pre-deployment checks..."
    pwsh scripts/pre-deployment-check.ps1

# Run unit tests with coverage
test-unit:
    @echo "🧪 Running unit tests with coverage..."
    pwsh -Command ".\.venv\Scripts\python.exe squigleague\run_coverage.py"

# Run integration tests (requires services running)
test-integration:
    @echo "🧪 Running integration tests..."
    pwsh scripts/integration-test-runner.ps1

# Run integration tests and keep services running
test-integration-debug:
    @echo "🧪 Running integration tests (debug mode)..."
    pwsh scripts/integration-test-runner.ps1 -KeepRunning

# Run UAT tests against running instance
test-uat:
    @echo "🧪 Running UAT tests..."
    pwsh run-uat-tests.ps1

# Start test database
test-db-up:
    @echo "🗄️  Starting test database..."
    docker-compose -f docker-compose.test.yml up -d postgres-test
    @echo "✅ Test database ready on port 5433"

# Stop test database
test-db-down:
    @echo "🗄️  Stopping test database..."
    docker-compose -f docker-compose.test.yml down
    @echo "✅ Test database stopped"

# Build all Docker images (for testing builds)
build-test:
    @echo "🏗️  Building Docker images..."
    @echo "Building backend..."
    docker build -t squigleague-backend:test -f backend/Dockerfile backend/
    @echo "Building herald..."
    docker build -t squigleague-herald:test -f herald/Dockerfile herald/
    @echo "Building frontend..."
    docker build -t squigleague-frontend:test -f frontend/Dockerfile frontend/
    @echo "✅ All images built successfully"

# Validate docker-compose configurations
build-validate:
    @echo "🔍 Validating docker-compose configurations..."
    @echo "Testing dev config..."
    docker-compose -f docker-compose.yml -f docker-compose.dev.yml config > /dev/null
    @echo "Testing prod config..."
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml config > /dev/null
    @echo "Testing test config..."
    docker-compose -f docker-compose.test.yml config > /dev/null
    @echo "✅ All configurations valid"

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
