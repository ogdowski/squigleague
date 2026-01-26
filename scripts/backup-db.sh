#!/bin/bash
# Database backup script for Squig League
# Run via cron: 0 2 * * * /root/squig_league/scripts/backup-db.sh >> /var/log/squig-backup.log 2>&1

set -e

# Configuration
BACKUP_DIR="/root/squig_league/backups"
CONTAINER_NAME="squig-postgres"
DB_USER="squig"
DB_NAME="squigleague"
KEEP_LAST=5

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Generate filename with timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_${TIMESTAMP}.sql.gz"

echo "[$(date)] Starting database backup..."

# Create compressed backup
docker exec "$CONTAINER_NAME" pg_dump -U "$DB_USER" "$DB_NAME" | gzip > "$BACKUP_FILE"

# Check if backup was successful
if [ -f "$BACKUP_FILE" ] && [ -s "$BACKUP_FILE" ]; then
    SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo "[$(date)] Backup created: $BACKUP_FILE ($SIZE)"
else
    echo "[$(date)] ERROR: Backup failed!"
    exit 1
fi

# Delete old backups (keep last N)
echo "[$(date)] Cleaning up old backups (keeping last $KEEP_LAST)..."
cd "$BACKUP_DIR" && ls -t backup_*.sql.gz 2>/dev/null | tail -n +$((KEEP_LAST + 1)) | xargs -r rm -f

# List current backups
echo "[$(date)] Current backups:"
ls -lh "$BACKUP_DIR"/backup_*.sql.gz 2>/dev/null || echo "No backups found"

echo "[$(date)] Backup completed successfully"
