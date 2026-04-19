#!/bin/bash

# Sound It Platform Backup Script

set -e

BACKUP_DIR=${BACKUP_DIR:-"./backups"}
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="soundit_backup_$DATE.sql"

mkdir -p "$BACKUP_DIR"

echo "🗄️  Creating database backup..."

if [ -f "soundit_local.db" ]; then
    # SQLite backup
    echo "SQLite database detected"
    cp soundit_local.db "$BACKUP_DIR/soundit_backup_$DATE.db"
    echo "✅ SQLite backup created: $BACKUP_DIR/soundit_backup_$DATE.db"
else
    # PostgreSQL backup via Docker
    echo "PostgreSQL database detected"
    docker-compose exec -T db pg_dump -U soundit soundit > "$BACKUP_DIR/$BACKUP_FILE"
    echo "✅ PostgreSQL backup created: $BACKUP_DIR/$BACKUP_FILE"
fi

# Cleanup old backups (keep last 7 days)
echo "🧹 Cleaning up old backups..."
find "$BACKUP_DIR" -name "soundit_backup_*" -mtime +7 -delete

echo "🎉 Backup complete!"
