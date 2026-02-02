#!/bin/bash

# ==========================================
# Production Startup Script for Agentic AI
# ==========================================

set -e  # Exit on error

echo "🚀 Starting Agentic AI Production Deployment..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your configuration before proceeding!"
    exit 1
fi

# Load environment variables
source .env

# Check required environment variables
required_vars=("SECRET_KEY" "JWT_SECRET_KEY" "POSTGRES_PASSWORD")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Error: $var is not set in .env file"
        exit 1
    fi
done

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running"
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Error: docker-compose is not installed"
    exit 1
fi

echo "✅ Prerequisites check passed"

# Build images
echo "📦 Building Docker images..."
docker-compose build --no-cache

# Start services
echo "🐳 Starting Docker services..."
docker-compose up -d

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
until docker-compose exec -T postgres pg_isready -U ${POSTGRES_USER:-agenticai} > /dev/null 2>&1; do
    echo "   Waiting..."
    sleep 2
done

echo "✅ PostgreSQL is ready"

# Initialize database
echo "🗄️  Initializing database..."
docker-compose exec -T postgres psql -U ${POSTGRES_USER:-agenticai} -d ${POSTGRES_DB:-agenticai_db} -f /docker-entrypoint-initdb.d/init-db.sql

# Run migrations (if using Alembic)
echo "📝 Running database migrations..."
docker-compose exec -T api alembic upgrade head || echo "⚠️  Migrations not configured yet"

# Check service health
echo "🏥 Checking service health..."
sleep 5

services=("api" "postgres" "redis" "rabbitmq")
for service in "${services[@]}"; do
    if docker-compose ps | grep $service | grep -q "Up"; then
        echo "✅ $service is running"
    else
        echo "❌ $service is not running"
        docker-compose logs $service
    fi
done

# Test API health endpoint
echo "🔍 Testing API health endpoint..."
sleep 3
if curl -f http://localhost/health > /dev/null 2>&1; then
    echo "✅ API is healthy"
else
    echo "❌ API health check failed"
    docker-compose logs api
fi

echo ""
echo "=========================================="
echo "✅ Agentic AI is now running!"
echo "=========================================="
echo ""
echo "🌐 API URL: http://localhost"
echo "📚 API Docs: http://localhost/docs"
echo "📊 Grafana: http://localhost:3000 (admin/admin)"
echo "📈 Prometheus: http://localhost:9090"
echo "🐰 RabbitMQ: http://localhost:15672 (guest/guest)"
echo ""
echo "📋 Useful commands:"
echo "   View logs:    docker-compose logs -f"
echo "   Stop:         docker-compose down"
echo "   Restart:      docker-compose restart"
echo "   Shell:        docker-compose exec api bash"
echo ""
