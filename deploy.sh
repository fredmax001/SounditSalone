#!/bin/bash
# ============================================================
# Sound It Platform - Production Deployment Script
# ============================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="soundit"
COMPOSE_FILE="docker-compose.prod.yml"
ENV_FILE=".env.production"

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if environment file exists
check_env() {
    if [ ! -f "$ENV_FILE" ]; then
        log_error "Environment file $ENV_FILE not found!"
        log_info "Copy .env.production.template to $ENV_FILE and configure it"
        exit 1
    fi
    log_info "Environment file found"
}

# Check Docker and Docker Compose
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    # Check for docker compose (v2) or docker-compose (v1 legacy)
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    if ! docker compose version &> /dev/null && ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed"
        log_error "Docker Compose is not installed"
        exit 1
    fi
    
    log_info "Docker and Docker Compose are available"
}

# Create required directories
create_directories() {
    log_info "Creating required directories..."
    mkdir -p nginx/ssl
    mkdir -p logs
    mkdir -p backups
    mkdir -p init-scripts
}

# Build and start services
deploy() {
    log_info "Building and starting services..."
    
    # Use docker compose v2 if available, fallback to docker-compose
    COMPOSE="docker compose"
    if ! docker compose version &> /dev/null; then
        COMPOSE="docker-compose"
    fi
    
    # Pull latest images
    $COMPOSE -f $COMPOSE_FILE pull
    
    # Build application
    $COMPOSE -f $COMPOSE_FILE build --no-cache
    
    # Start services
    $COMPOSE -f $COMPOSE_FILE up -d
    
    log_info "Services started successfully"
}

# Run database migrations
run_migrations() {
    log_info "Running database migrations..."
    
    # Wait for database to be ready
    sleep 5
    
    # Run migrations
    $COMPOSE -f $COMPOSE_FILE exec -T app alembic upgrade head
    
    log_info "Migrations completed"
}

# Health check
health_check() {
    log_info "Performing health check..."
    
    MAX_RETRIES=30
    RETRY_COUNT=0
    
    while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
        if $COMPOSE -f $COMPOSE_FILE exec -T app curl -sf http://localhost:8000/health > /dev/null; then
            log_info "Health check passed!"
            return 0
        fi
        
        RETRY_COUNT=$((RETRY_COUNT + 1))
        log_warn "Health check failed, retrying... ($RETRY_COUNT/$MAX_RETRIES)"
        sleep 2
    done
    
    log_error "Health check failed after $MAX_RETRIES attempts"
    return 1
}

# Display status
show_status() {
    log_info "Deployment Status:"
    echo ""
    $COMPOSE -f $COMPOSE_FILE ps
    echo ""
    log_info "Logs:"
    $COMPOSE -f $COMPOSE_FILE logs --tail=20 app
}

# Rollback function
rollback() {
    log_warn "Rolling back deployment..."
    $COMPOSE -f $COMPOSE_FILE down
    log_info "Rollback completed"
}

# Main deployment flow
main() {
    log_info "Starting Sound It Platform deployment..."
    
    check_env
    check_docker
    create_directories
    
    # Backup current state
    log_info "Creating backup..."
    if [ -f "backups/previous-deployment.tar" ]; then
        mv backups/previous-deployment.tar backups/previous-deployment-$(date +%Y%m%d-%H%M%S).tar
    fi
    $COMPOSE -f $COMPOSE_FILE down || true
    
    # Deploy
    if deploy; then
        if run_migrations; then
            if health_check; then
                show_status
                log_info "Deployment completed successfully!"
                log_info "Application is available at: https://api.sounditsl.com"
            else
                log_error "Health check failed"
                rollback
                exit 1
            fi
        else
            log_error "Migrations failed"
            rollback
            exit 1
        fi
    else
        log_error "Deployment failed"
        rollback
        exit 1
    fi
}

# Handle script interruption
trap 'log_warn "Deployment interrupted"; exit 1' INT TERM

# Run main function
main
