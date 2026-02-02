#!/bin/bash

# ==========================================
# Database Restore Script
# ==========================================

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <backup_file>"
    echo ""
    echo "Available PostgreSQL backups:"
    ls -lh /opt/agenticai/backups/postgres/*.sql.gz 2>/dev/null || echo "No backups found"
    exit 1
fi

BACKUP_FILE="$1"
POSTGRES_USER="${POSTGRES_USER:-agenticai}"
POSTGRES_DB="${POSTGRES_DB:-agenticai_db}"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ Backup file not found: $BACKUP_FILE"
    exit 1
fi

echo "⚠️  WARNING: This will restore the database from backup"
echo "   Backup file: $BACKUP_FILE"
echo "   Database: $POSTGRES_DB"
echo ""
read -p "Continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Restore cancelled"
    exit 0
fi

# ==========================================
# PostgreSQL Restore
# ==========================================
echo "📦 Restoring PostgreSQL database..."

# Drop existing database
docker-compose exec -T postgres psql -U "$POSTGRES_USER" -c "DROP DATABASE IF EXISTS ${POSTGRES_DB}_temp;"
docker-compose exec -T postgres psql -U "$POSTGRES_USER" -c "CREATE DATABASE ${POSTGRES_DB}_temp;"

# Restore backup to temp database
gunzip -c "$BACKUP_FILE" | docker-compose exec -T postgres psql -U "$POSTGRES_USER" -d "${POSTGRES_DB}_temp"

if [ $? -eq 0 ]; then
    echo "✅ Backup restored to temporary database"
    
    # Swap databases
    echo "🔄 Swapping databases..."
    docker-compose exec -T postgres psql -U "$POSTGRES_USER" -c "ALTER DATABASE $POSTGRES_DB RENAME TO ${POSTGRES_DB}_old;"
    docker-compose exec -T postgres psql -U "$POSTGRES_USER" -c "ALTER DATABASE ${POSTGRES_DB}_temp RENAME TO $POSTGRES_DB;"
    
    echo "✅ Database restore completed"
    echo ""
    echo "⚠️  Old database backed up as: ${POSTGRES_DB}_old"
    echo "   To drop it: docker-compose exec postgres psql -U $POSTGRES_USER -c 'DROP DATABASE ${POSTGRES_DB}_old;'"
else
    echo "❌ Restore failed"
    docker-compose exec -T postgres psql -U "$POSTGRES_USER" -c "DROP DATABASE IF EXISTS ${POSTGRES_DB}_temp;"
    exit 1
fi

# Restart API to reconnect
echo "🔄 Restarting API service..."
docker-compose restart api

echo "✅ Restore process completed!"
