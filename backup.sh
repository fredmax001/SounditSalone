#!/bin/bash
# ============================================================
# Sound It Platform - Database Backup Script
# ============================================================

set -e

# Configuration
BACKUP_DIR="./backups"
DB_CONTAINER="soundit-db"
RETENTION_DAYS=30
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="soundit_backup_${DATE}.sql.gz"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Perform backup
log_info "Starting database backup..."

if docker ps | grep -q "$DB_CONTAINER"; then
    docker exec "$DB_CONTAINER" pg_dumpall -U soundit_user | gzip > "$BACKUP_DIR/$BACKUP_FILE"
    log_info "Backup completed: $BACKUP_FILE"
else
    log_error "Database container not running"
    exit 1
fi

# Cleanup old backups
log_info "Cleaning up old backups (retention: $RETENTION_DAYS days)..."
find "$BACKUP_DIR" -name "soundit_backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete

# List recent backups
log_info "Recent backups:"
ls -lh "$BACKUP_DIR"/*.sql.gz 2>/dev/null | tail -5

log_info "Backup process completed"
