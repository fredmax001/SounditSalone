# Sound It Platform - Deployment Guide

## Overview

This guide covers deploying the Sound It Platform to production using Docker Compose.

## Architecture

```
┌─────────────┐
│    Nginx    │ ← Reverse Proxy, SSL, Static Files
│   (Port 80  │
│    & 443)   │
└──────┬──────┘
       │
┌──────▼──────┐
│   FastAPI   │ ← Main Application (Port 8000)
│   Backend   │
└──────┬──────┘
       │
┌──────▼──────┐     ┌─────────────┐
│ PostgreSQL  │     │    Redis    │
│  Database   │     │   Cache/    │
│  (Port 5432)│     │  Rate Limit │
└─────────────┘     └─────────────┘
```

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- Domain name with DNS configured
- SSL certificates (Let's Encrypt or custom)

## Environment Setup

1. Copy environment template:
```bash
cp .env.production .env.production.local
```

2. Edit `.env.production.local` with your values:
```bash
# Security
SECRET_KEY=your-super-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# Database
DATABASE_URL=postgresql://user:password@db:5432/soundit
POSTGRES_USER=soundit
POSTGRES_PASSWORD=secure-password-here
POSTGRES_DB=soundit

# Email (SendGrid)
SENDGRID_API_KEY=SG.xxx
FROM_EMAIL=noreply@soundit.com

# SMS (Twilio)
TWILIO_ACCOUNT_SID=ACxxx
TWILIO_AUTH_TOKEN=xxx
TWILIO_PHONE_NUMBER=+1234567890

# Redis
REDIS_URL=redis://redis:6379/0

# CORS
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Monitoring
SENTRY_DSN=https://xxx@xxx.ingest.sentry.io/xxx
LOG_LEVEL=INFO
```

## Deployment Steps

### 1. Initial Setup

```bash
# Clone repository
git clone <repo-url>
cd sound-it-platform

# Create data directories
mkdir -p postgres_data redis_data

# Set permissions
chmod +x deploy/deploy.sh
```

### 2. SSL Certificates

**Option A: Let's Encrypt (Recommended)**
```bash
# Install certbot
sudo apt-get install certbot

# Obtain certificates
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Copy to project
cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/
cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/
```

**Option B: Custom Certificates**
```bash
# Place your certificates in nginx/ssl/
cp your-cert.pem nginx/ssl/fullchain.pem
cp your-key.pem nginx/ssl/privkey.pem
```

### 3. Build and Deploy

```bash
# Production deployment
deploy/deploy.sh production

# Or manually:
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

### 4. Database Migrations

```bash
# Run migrations
docker-compose exec api alembic upgrade head

# Verify migration status
docker-compose exec api alembic current
```

### 5. Verify Deployment

```bash
# Check health
curl https://yourdomain.com/api/v1/health

# Check detailed health
curl https://yourdomain.com/api/v1/health/detailed

# View logs
docker-compose logs -f api
```

## Maintenance

### Backup Database

```bash
# Create backup
docker-compose exec db pg_dump -U soundit soundit > backup_$(date +%Y%m%d).sql

# Restore backup
docker-compose exec -T db psql -U soundit soundit < backup_20240101.sql
```

### Update Application

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
deploy/deploy.sh production

# Run migrations if needed
docker-compose exec api alembic upgrade head
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f db
docker-compose logs -f redis

# Last 100 lines
docker-compose logs --tail=100 api
```

### Monitoring

```bash
# Resource usage
docker stats

# Disk usage
docker system df

# Clean up unused data
docker system prune -a
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs api

# Check for port conflicts
sudo netstat -tlnp | grep 8000

# Restart service
docker-compose restart api
```

### Database Connection Issues

```bash
# Verify database is running
docker-compose ps db

# Check database logs
docker-compose logs db

# Test connection
docker-compose exec db psql -U soundit -d soundit -c "SELECT 1"
```

### Migration Failures

```bash
# Check migration status
docker-compose exec api alembic history

# Rollback if needed
docker-compose exec api alembic downgrade -1

# Mark as applied (careful!)
docker-compose exec api alembic stamp head
```

### SSL Issues

```bash
# Test SSL configuration
openssl s_client -connect yourdomain.com:443

# Verify certificate expiry
echo | openssl s_client -servername yourdomain.com -connect yourdomain.com:443 2>/dev/null | openssl x509 -noout -dates
```

## Security Checklist

- [ ] Strong `SECRET_KEY` (32+ random characters)
- [ ] Database password changed from default
- [ ] SSL certificates installed and valid
- [ ] CORS origins restricted to production domains
- [ ] Rate limiting enabled
- [ ] Sentry configured for error tracking
- [ ] Database backups scheduled
- [ ] Log rotation configured
- [ ] Firewall rules in place
- [ ] Regular security updates

## Rollback Procedure

```bash
# Rollback to previous version
git log --oneline -10
git checkout <previous-commit>
deploy/deploy.sh production

# Restore database if needed
docker-compose exec -T db psql -U soundit soundit < backup_before_upgrade.sql
```

## Support

For issues or questions:
1. Check logs: `docker-compose logs -f`
2. Review monitoring dashboard
3. Contact: support@soundit.com
