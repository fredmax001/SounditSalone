#!/bin/bash

# Sound It Platform Deployment Script

set -e

ENVIRONMENT=${1:-production}
COMPOSE_FILE="docker-compose.yml"

if [ "$ENVIRONMENT" == "production" ]; then
    COMPOSE_FILE="docker-compose.yml:docker-compose.prod.yml"
    echo "🚀 Deploying to PRODUCTION environment"
else
    echo "🔧 Deploying to DEVELOPMENT environment"
fi

# Check Docker
echo "📋 Checking Docker..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose not found. Please install Docker Compose."
    exit 1
fi

# Pull latest changes
echo "📥 Pulling latest changes..."
git pull origin main || echo "⚠️  Could not pull changes (may not be a git repo)"

# Build and start services
echo "🔨 Building and starting services..."
docker-compose -f $COMPOSE_FILE up -d --build

# Wait for database
echo "⏳ Waiting for database..."
sleep 5

# Run migrations
echo "🗃️  Running database migrations..."
docker-compose exec -T app alembic upgrade head || echo "⚠️  Migration may have failed, continuing..."

# Health check
echo "🏥 Performing health check..."
sleep 2
if docker-compose exec -T app curl -sf http://localhost:8000/api/v1/health > /dev/null; then
    echo "✅ Health check passed!"
else
    echo "❌ Health check failed!"
    docker-compose logs app --tail=20
    exit 1
fi

echo ""
echo "🎉 Deployment complete!"
echo "📊 Services status:"
docker-compose ps
echo ""
echo "📜 View logs: docker-compose logs -f"
