import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from datetime import datetime

from config import get_settings
from database import init_db
from api import auth_password
from api import google_auth
from api import events
from api import payments
from api import admin
from api import otp
from api import dashboard_stats
from api import bookings
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
from api import sports
from api import tickets
from api import orange_money

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting application...")
    init_db()
    print("Database initialized")
    
    # Ensure static directories exist
    import os
    os.makedirs("static/uploads", exist_ok=True)
    print("Static directories ready")
    
    yield
    # Shutdown
    print("Shutting down application...")


app = FastAPI(
    title=settings.APP_NAME,
    description="Sound It - Music Events & Nightlife Platform API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS - Use environment variable or default to localhost for development
_env_origins = os.getenv("CORS_ORIGINS", "")
_environment = os.getenv("ENVIRONMENT", "development").lower()
if _env_origins:
    ALLOWED_ORIGINS = [o.strip() for o in _env_origins.split(",")]
elif _environment == "production":
    raise RuntimeError("CORS_ORIGINS environment variable is required in production")
else:
    # Development defaults (includes Capacitor mobile app origins)
    ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "capacitor://localhost",  # iOS app
        "http://localhost",        # Android app
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
    expose_headers=["X-Total-Count"]
)

# Session middleware for Google OAuth
app.add_middleware(
    SessionMiddleware, 
    secret_key=settings.SECRET_KEY,
    session_cookie="soundit_session",
    max_age=3600 # 1 hour
)

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(auth_password.router, prefix="/api/v1")
app.include_router(google_auth.router, prefix="/api/v1")
app.include_router(events.router, prefix="/api/v1")
app.include_router(payments.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")
app.include_router(otp.router, prefix="/api/v1")
app.include_router(dashboard_stats.router, prefix="/api/v1")
app.include_router(bookings.router, prefix="/api/v1")
app.include_router(media.router, prefix="/api/v1")
app.include_router(contact.router, prefix="/api/v1")
app.include_router(notifications.router, prefix="/api/v1")
app.include_router(recaps.router, prefix="/api/v1")
app.include_router(cart.router, prefix="/api/v1")
app.include_router(city_guide.router, prefix="/api/v1")
app.include_router(organizer.router, prefix="/api/v1")
app.include_router(venue_dashboard.router, prefix="/api/v1")
app.include_router(sports_dashboard.router, prefix="/api/v1")
app.include_router(sports.router, prefix="/api/v1")
app.include_router(user_dashboard.router, prefix="/api/v1")
app.include_router(tickets.router, prefix="/api/v1")
app.include_router(orange_money.router, prefix="/api/v1")


@app.get("/")
def root():
    return {
        "name": settings.APP_NAME,
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "version": "1.0.0"
    }


@app.get("/api/v1/health")
def api_health_check():
    """API health check endpoint"""
    return {
        "status": "healthy",
        "api_version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    try:
        import socket
        import uvicorn

        # Try to show network-accessible URL
        try:
            local_ip = socket.gethostbyname(socket.gethostname())
        except Exception:
            local_ip = "127.0.0.1"

        port = 8000
        print(f"\n🚀 Starting Sound It API Server")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"   Local:       http://127.0.0.1:{port}")
        print(f"   Network:     http://{local_ip}:{port}")
        print(f"   CORS Origins: {ALLOWED_ORIGINS}")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

        uvicorn.run(app, host="0.0.0.0", port=port)
    except Exception as e:
        print(f"Server startup failed: {e}")
        import traceback
        traceback.print_exc()
