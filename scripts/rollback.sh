#!/bin/bash

# ==========================================
# Rollback Script for Failed Deployments
# ==========================================

set -e

echo "🔄 Rolling back to previous deployment..."

# Get previous Docker image tag
PREVIOUS_TAG=$(docker images --format "{{.Repository}}:{{.Tag}}" | grep agenticai | sed -n '2p')

if [ -z "$PREVIOUS_TAG" ]; then
    echo "❌ No previous image found"
    exit 1
fi

echo "   Rolling back to: $PREVIOUS_TAG"

# Update docker-compose to use previous image
sed -i "s|image:.*agenticai.*|image: $PREVIOUS_TAG|" docker-compose.yml

# Restart services
docker-compose up -d --no-deps api worker

# Wait for health check
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Check health
if curl -f http://localhost/health > /dev/null 2>&1; then
    echo "✅ Rollback successful"
else
    echo "❌ Rollback failed - services not healthy"
    exit 1
fi

echo "✅ Rollback completed"
