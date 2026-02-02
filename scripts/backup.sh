#!/bin/bash

# ==========================================
# Database Backup Script
# ==========================================

set -e

# Configuration
BACKUP_DIR="/opt/agenticai/backups"
POSTGRES_USER="${POSTGRES_USER:-agenticai}"
POSTGRES_DB="${POSTGRES_DB:-agenticai_db}"
RETENTION_DAYS=30
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p "$BACKUP_DIR/postgres"
mkdir -p "$BACKUP_DIR/chromadb"
mkdir -p "$BACKUP_DIR/redis"

echo "🗄️  Starting backup at $(date)"

# ==========================================
# PostgreSQL Backup
# ==========================================
echo "📦 Backing up PostgreSQL database..."

POSTGRES_BACKUP="$BACKUP_DIR/postgres/postgres_${TIMESTAMP}.sql.gz"

docker-compose exec -T postgres pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" | gzip > "$POSTGRES_BACKUP"

if [ $? -eq 0 ]; then
    echo "✅ PostgreSQL backup completed: $POSTGRES_BACKUP"
    SIZE=$(du -h "$POSTGRES_BACKUP" | cut -f1)
    echo "   Size: $SIZE"
else
    echo "❌ PostgreSQL backup failed"
    exit 1
fi

# ==========================================
# ChromaDB Backup
# ==========================================
echo "📦 Backing up ChromaDB..."

CHROMA_BACKUP="$BACKUP_DIR/chromadb/chromadb_${TIMESTAMP}.tar.gz"

docker run --rm \
    -v agenticai_chroma_data:/data \
    -v "$BACKUP_DIR/chromadb:/backup" \
    alpine tar czf "/backup/chromadb_${TIMESTAMP}.tar.gz" -C /data .

if [ $? -eq 0 ]; then
    echo "✅ ChromaDB backup completed: $CHROMA_BACKUP"
    SIZE=$(du -h "$CHROMA_BACKUP" | cut -f1)
    echo "   Size: $SIZE"
else
    echo "❌ ChromaDB backup failed"
fi

# ==========================================
# Redis Backup
# ==========================================
echo "📦 Backing up Redis..."

REDIS_BACKUP="$BACKUP_DIR/redis/redis_${TIMESTAMP}.rdb"

docker-compose exec -T redis redis-cli BGSAVE
sleep 2

docker cp agenticai-redis:/data/dump.rdb "$REDIS_BACKUP"

if [ $? -eq 0 ]; then
    echo "✅ Redis backup completed: $REDIS_BACKUP"
    SIZE=$(du -h "$REDIS_BACKUP" | cut -f1)
    echo "   Size: $SIZE"
else
    echo "❌ Redis backup failed"
fi

# ==========================================
# Cleanup Old Backups
# ==========================================
echo "🧹 Cleaning up backups older than $RETENTION_DAYS days..."

find "$BACKUP_DIR/postgres" -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR/chromadb" -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR/redis" -name "*.rdb" -mtime +$RETENTION_DAYS -delete

echo "✅ Cleanup completed"

# ==========================================
# Summary
# ==========================================
echo ""
echo "=========================================="
echo "✅ Backup completed at $(date)"
echo "=========================================="
echo "Backup location: $BACKUP_DIR"
echo ""
echo "PostgreSQL backups:"
ls -lh "$BACKUP_DIR/postgres" | tail -n 5
echo ""
echo "ChromaDB backups:"
ls -lh "$BACKUP_DIR/chromadb" | tail -n 5
echo ""

# Optional: Upload to S3 or cloud storage
# aws s3 sync "$BACKUP_DIR" s3://your-bucket/backups/
