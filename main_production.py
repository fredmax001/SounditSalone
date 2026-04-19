"""
Production entry point for Sound It platform.
Uses production configuration and database settings.
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from starlette.middleware.sessions import SessionMiddleware
from contextlib import asynccontextmanager
from datetime import datetime
import os
import sys
import logging

# Import configuration
from config import get_settings
from database import init_db, get_db

# Import all API routers
from api import auth_password
from api import google_auth
from api import events
from api import payments
from api import admin
from api import bookings
from api import dashboard_stats
from api import media
from api import contact
from api import notifications
from api import recaps
from api import cart
from api import city_guide
from api import organizer
from api import venue_dashboard
from api import sports_dashboard
from api import user_dashboard
from api import tickets
from api import sports
from api import orange_money

# Get settings
settings = get_settings()

# Configure structured logging for production
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("=" * 60)
    logger.info(f"Starting {settings.APP_NAME} in PRODUCTION mode")
    logger.info("=" * 60)
    
    # Validate critical settings
    if not settings.SECRET_KEY:
        logger.error("CRITICAL: SECRET_KEY is not set! Cannot start in production.")
        raise ValueError("SECRET_KEY environment variable is required for production")
    
    if len(settings.SECRET_KEY) < 32:
        logger.warning("WARNING: SECRET_KEY should be at least 32 characters for security")
    
    # Initialize database
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    
    # Ensure static directories exist
    os.makedirs("static/uploads", exist_ok=True)
    os.makedirs("static/uploads/avatars", exist_ok=True)
    os.makedirs("static/uploads/events", exist_ok=True)
    os.makedirs("static/uploads/venues", exist_ok=True)
    logger.info("Static directories ready")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="Sound It - Music Events & Nightlife Platform API (Production)",
    version="1.0.0",
    lifespan=lifespan,
    # Disable docs in production unless explicitly enabled
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
)

# CORS Configuration - Use environment-based origins (REQUIRED in production)
_env_origins = os.getenv("CORS_ORIGINS", "")
if _env_origins:
    ALLOWED_ORIGINS = [o.strip() for o in _env_origins.split(",")]
    logger.info(f"CORS configured with {len(ALLOWED_ORIGINS)} origins from environment")
else:
    raise RuntimeError("CORS_ORIGINS environment variable is REQUIRED in production")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With", "X-Request-ID"],
    expose_headers=["X-Total-Count", "X-Request-ID"]
)

# Session middleware for OAuth
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    session_cookie="soundit_session",
    max_age=3600,
    same_site="lax",
    https_only=True,  # Only send over HTTPS in production
)

# GZip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Request logging middleware
@app.middleware("http")
async def log_requests(request, call_next):
    import time
    start_time = time.time()
    
    # Log request
    client_host = request.client.host if request.client else "unknown"
    logger.info(f"Request started: {request.method} {request.url.path} - Client: {client_host}")
    
    response = await call_next(request)
    
    # Calculate duration
    duration = time.time() - start_time
    
    # Log response
    logger.info(
        f"Request completed: {request.method} {request.url.path} - "
        f"Status: {response.status_code} - Duration: {duration:.3f}s"
    )
    
    return response


# Security headers middleware
@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self'; connect-src 'self'"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    return response

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include API routers
app.include_router(auth_password.router, prefix="/api/v1")
app.include_router(google_auth.router, prefix="/api/v1")
app.include_router(events.router, prefix="/api/v1")
app.include_router(payments.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")
app.include_router(bookings.router, prefix="/api/v1")
app.include_router(dashboard_stats.router, prefix="/api/v1")
app.include_router(media.router, prefix="/api/v1")
app.include_router(contact.router, prefix="/api/v1")
app.include_router(notifications.router, prefix="/api/v1")
app.include_router(recaps.router, prefix="/api/v1")
app.include_router(cart.router, prefix="/api/v1")
app.include_router(city_guide.router, prefix="/api/v1")
app.include_router(organizer.router, prefix="/api/v1")
app.include_router(venue_dashboard.router, prefix="/api/v1")
app.include_router(sports_dashboard.router, prefix="/api/v1")
app.include_router(user_dashboard.router, prefix="/api/v1")
app.include_router(tickets.router, prefix="/api/v1")
app.include_router(sports.router, prefix="/api/v1")
app.include_router(orange_money.router, prefix="/api/v1")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for production"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    # Don't expose internal details in production
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred"}
    )


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": "1.0.0",
        "environment": "production",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health")
def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/v1/health")
def api_health_check():
    """API health check endpoint with database verification"""
    import psutil
    
    # Check database
    try:
        db = next(get_db())
        db.execute("SELECT 1")
        db_status = "connected"
        db_healthy = True
    except Exception as e:
        db_status = f"error: {str(e)}"
        db_healthy = False
        logger.error(f"Health check database error: {e}")
    
    # Check system resources
    try:
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        memory_status = "healthy" if memory.percent < 90 else "warning"
        disk_status = "healthy" if disk.percent < 90 else "warning"
        
        system_healthy = memory_status == "healthy" and disk_status == "healthy"
    except Exception as e:
        memory_status = "unknown"
        disk_status = "unknown"
        system_healthy = True  # Don't fail if we can't check
    
    overall_status = "healthy" if (db_healthy and system_healthy) else "degraded"
    
    return {
        "status": overall_status,
        "api_version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {
            "database": {
                "status": db_status,
                "healthy": db_healthy
            },
            "system": {
                "memory": memory_status,
                "disk": disk_status,
                "healthy": system_healthy
            }
        }
    }


@app.get("/metrics")
def metrics():
    """Basic metrics endpoint for monitoring"""
    import psutil
    import os
    
    try:
        # System metrics
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        cpu_percent = psutil.cpu_percent(interval=0.1)
        
        # Get database stats
        try:
            from sqlalchemy import func
            db = next(get_db())
            
            from models import User, Event, Order, Ticket
            
            user_count = db.query(User).count()
            event_count = db.query(Event).count()
            order_count = db.query(Order).count()
            ticket_count = db.query(Ticket).count()
            
            db_stats = {
                "users": user_count,
                "events": event_count,
                "orders": order_count,
                "tickets": ticket_count
            }
        except Exception as e:
            logger.error(f"Failed to get DB stats: {e}")
            db_stats = {"error": "Failed to retrieve"}
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "system": {
                "cpu_percent": cpu_percent,
                "memory": {
                    "total_gb": round(memory.total / (1024**3), 2),
                    "used_gb": round(memory.used / (1024**3), 2),
                    "percent": memory.percent
                },
                "disk": {
                    "total_gb": round(disk.total / (1024**3), 2),
                    "used_gb": round(disk.used / (1024**3), 2),
                    "percent": disk.percent
                }
            },
            "database": db_stats
        }
    except Exception as e:
        logger.error(f"Metrics error: {e}")
        return {"error": "Failed to gather metrics"}


# SPA catch-all route - serve index.html for non-API routes
@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    """Serve the SPA for client-side routing"""
    # Don't interfere with API or static routes
    if full_path.startswith("api/") or full_path.startswith("static/"):
        raise HTTPException(status_code=404)
    
    # Try to serve the built frontend
    index_path = os.path.join("app", "dist", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    
    # Fallback if frontend not built
    raise HTTPException(status_code=404, detail="Frontend not built")


if __name__ == "__main__":
    import uvicorn
    
    # Production server configuration
    uvicorn.run(
        "main_production:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        workers=int(os.getenv("WORKERS", "4")),
        log_level="info",
        access_log=True,
        proxy_headers=True,
        forwarded_allow_ips="*",
    )
