#!/bin/bash
# Sound It Platform - Home Server Deployment Script
# Run this ON your home server (192.168.2.14)

set -e

PROJECT_DIR="${PROJECT_DIR:-/opt/soundit}"
COMPOSE_FILE="docker-compose.homeserver-standalone.yml"

echo "🚀 Sound It Platform - Home Server Deploy"
echo "=========================================="

# 1. Ensure Docker is running
echo "📋 Checking Docker..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Install Docker first:"
    echo "   curl -fsSL https://get.docker.com | sh"
    exit 1
fi

if ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose v2 not found. Installing..."
    sudo apt-get update && sudo apt-get install -y docker-compose-plugin || true
fi

# 2. Create project directory
echo "📁 Setting up project directory: $PROJECT_DIR"
mkdir -p "$PROJECT_DIR"

# 3. Copy project files (do this manually or via rsync/scp first)
if [ ! -f "$PROJECT_DIR/$COMPOSE_FILE" ]; then
    echo "⚠️  Project files not found in $PROJECT_DIR"
    echo "   Copy the project files to $PROJECT_DIR first:"
    echo "   rsync -avz --exclude=node_modules --exclude=.venv --exclude=.git ./ server@192.168.2.14:$PROJECT_DIR"
    exit 1
fi

cd "$PROJECT_DIR"

# 4. Pull/build and start
echo "🔨 Building and starting services..."
docker compose -f "$COMPOSE_FILE" down 2>/dev/null || true
docker compose -f "$COMPOSE_FILE" up -d --build

# 5. Wait for DB and run migrations
echo "⏳ Waiting for database..."
sleep 8

echo "🗃️  Running migrations..."
docker compose -f "$COMPOSE_FILE" exec -T app alembic upgrade head

# 6. Health check
echo "🏥 Health check..."
sleep 2
if docker compose -f "$COMPOSE_FILE" exec -T app curl -sf http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ App is healthy!"
else
    echo "⚠️  Health check didn't pass immediately — checking logs..."
    docker compose -f "$COMPOSE_FILE" logs --tail=30 app
fi

echo ""
echo "🎉 Deployment complete!"
echo "📊 Services:"
docker compose -f "$COMPOSE_FILE" ps
echo ""
echo "🌐 Access the app at: http://192.168.2.14"
echo "📜 View logs: docker compose -f $COMPOSE_FILE logs -f app"
