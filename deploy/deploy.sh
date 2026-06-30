#!/bin/bash

# Sound It Platform Deployment Script

set -e

ENVIRONMENT=${1:-production}

if [ "$ENVIRONMENT" == "production" ]; then
    COMPOSE_FILE="docker-compose.prod.yml"
    echo "🚀 Deploying to PRODUCTION environment"
else
    COMPOSE_FILE="docker-compose.yml"
    echo "🔧 Deploying to DEVELOPMENT environment"
fi

# Check Docker
echo "📋 Checking Docker..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker."
    exit 1
fi

if ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose v2 not found. Please install Docker Compose."
    exit 1
fi

# Pull latest changes
echo "📥 Pulling latest changes..."
git pull origin main || echo "⚠️  Could not pull changes (may not be a git repo)"

# Build and start services
echo "🔨 Building and starting services..."
docker compose -f $COMPOSE_FILE up -d --build

# Wait for database
echo "⏳ Waiting for database..."
sleep 5

# Run migrations
echo "🗃️  Running database migrations..."
docker compose -f $COMPOSE_FILE exec -T app alembic upgrade head

# Health check
echo "🏥 Performing health check..."
sleep 2
if docker compose -f $COMPOSE_FILE exec -T app curl -sf http://localhost:8000/api/v1/health > /dev/null; then
    echo "✅ Health check passed!"
else
    echo "❌ Health check failed!"
    docker compose -f $COMPOSE_FILE logs app --tail=20
    exit 1
fi

echo ""
echo "🎉 Deployment complete!"
echo "📊 Services status:"
docker-compose ps
echo ""
echo "📜 View logs: docker-compose logs -f"
