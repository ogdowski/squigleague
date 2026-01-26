#!/bin/bash
# Database backup script with remote upload
# Run via cron: 0 2 * * * /root/squig_league/scripts/backup-db-remote.sh >> /var/log/squig-backup.log 2>&1
#
# Prerequisites:
# 1. Install rclone: curl https://rclone.org/install.sh | sudo bash
# 2. Configure remote: rclone config
#    - For Backblaze B2: rclone config -> n -> squig-backup -> b2 -> key_id -> app_key
#    - For S3: rclone config -> n -> squig-backup -> s3 -> aws_access_key -> aws_secret_key
# 3. Test: rclone lsd squig-backup:

set -e

# Configuration
BACKUP_DIR="/root/squig_league/backups"
CONTAINER_NAME="squig-postgres"
DB_USER="squig"
DB_NAME="squigleague"
KEEP_LAST_LOCAL=5
KEEP_LAST_REMOTE=30

# Remote configuration (change these)
RCLONE_REMOTE="squig-backup"        # Name from rclone config
REMOTE_BUCKET="squig-league-backups" # Bucket/folder name

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

# Upload to remote storage
echo "[$(date)] Uploading to remote storage..."
if command -v rclone &> /dev/null; then
    if rclone copy "$BACKUP_FILE" "${RCLONE_REMOTE}:${REMOTE_BUCKET}/" --progress; then
        echo "[$(date)] Upload successful"

        # Clean up old remote backups (keep last N by age - rclone doesn't support count-based)
        echo "[$(date)] Cleaning old remote backups (older than 30 days)..."
        rclone delete "${RCLONE_REMOTE}:${REMOTE_BUCKET}/" --min-age "30d" 2>/dev/null || true
    else
        echo "[$(date)] WARNING: Remote upload failed, backup kept locally"
    fi
else
    echo "[$(date)] WARNING: rclone not installed, skipping remote upload"
fi

# Delete old local backups (keep fewer since we have remote)
echo "[$(date)] Cleaning up old local backups (keeping last $KEEP_LAST_LOCAL)..."
cd "$BACKUP_DIR" && ls -t backup_*.sql.gz 2>/dev/null | tail -n +$((KEEP_LAST_LOCAL + 1)) | xargs -r rm -f

echo "[$(date)] Backup completed successfully"
