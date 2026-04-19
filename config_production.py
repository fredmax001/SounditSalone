"""
Sound It Platform - Production Configuration
=============================================
Hardened production settings with:
- Environment-based secrets
- No hardcoded credentials
- Strict validation
"""

import os
import secrets
from typing import List, Optional
from pydantic_settings import BaseSettings
from functools import lru_cache
from pydantic import field_validator

# Load environment variables from .env.production file
try:
    from dotenv import load_dotenv
    env_path = os.path.join(os.path.dirname(__file__), '.env.production')
    if os.path.exists(env_path):
        load_dotenv(env_path, override=True)
except ImportError:
    pass  # python-dotenv not installed, rely on system env vars


class ProductionSettings(BaseSettings):
    """Production settings - all sensitive values from environment"""
    
    # ============================================
    # App Settings
    # ============================================
    APP_NAME: str = "Sound It API"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    
    # Generate a strong secret key if not provided (will change on restart)
    # In production, always set SECRET_KEY in environment
    SECRET_KEY: str = os.getenv("SECRET_KEY", secrets.token_hex(32))
    
    # Base URL for the application
    BASE_URL: str = os.getenv("BASE_URL", "http://localhost:8000")
    API_URL: str = os.getenv("API_URL", "http://localhost:8000/api/v1")
    
    # ============================================
    # Database - PostgreSQL (Production)
    # ============================================
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    
    # Database connection pool settings
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "10"))
    DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "20"))
    DB_POOL_TIMEOUT: int = int(os.getenv("DB_POOL_TIMEOUT", "30"))
    
    # ============================================
    # Redis (Caching & Sessions)
    # ============================================
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    REDIS_ENABLED: bool = os.getenv("REDIS_ENABLED", "false").lower() == "true"
    
    # Cache TTL settings (in seconds)
    CACHE_TTL_SHORT: int = 60  # 1 minute
    CACHE_TTL_MEDIUM: int = 300  # 5 minutes
    CACHE_TTL_LONG: int = 3600  # 1 hour
    
    # ============================================
    # JWT Authentication
    # ============================================
    # MUST be set in environment for production
    JWT_SECRET: str = os.getenv("JWT_SECRET", "")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))
    JWT_REFRESH_EXPIRATION_DAYS: int = int(os.getenv("JWT_REFRESH_EXPIRATION_DAYS", "7"))
    
    # ============================================
    # OTP Settings
    # ============================================
    OTP_EXPIRATION_MINUTES: int = int(os.getenv("OTP_EXPIRATION_MINUTES", "5"))
    OTP_MAX_ATTEMPTS: int = int(os.getenv("OTP_MAX_ATTEMPTS", "3"))
    OTP_COOLDOWN_MINUTES: int = int(os.getenv("OTP_COOLDOWN_MINUTES", "15"))
    
    # ============================================
    # SendGrid (Email)
    # ============================================
    SENDGRID_API_KEY: str = os.getenv("SENDGRID_API_KEY", "")
    SENDGRID_FROM_EMAIL: str = os.getenv("SENDGRID_FROM_EMAIL", "noreply@sounditentsl.com")
    SENDGRID_ENABLED: bool = os.getenv("SENDGRID_API_KEY", "") != ""
    
    # ============================================
    # Orange Money (Sierra Leone)
    # ============================================
    ORANGE_MONEY_CLIENT_ID: str = os.getenv("ORANGE_MONEY_CLIENT_ID", "")
    ORANGE_MONEY_CLIENT_SECRET: str = os.getenv("ORANGE_MONEY_CLIENT_SECRET", "")
    ORANGE_MONEY_BASE_URL: str = os.getenv("ORANGE_MONEY_BASE_URL", "https://api.orange.com")
    ORANGE_MONEY_MERCHANT_ID: str = os.getenv("ORANGE_MONEY_MERCHANT_ID", "")
    ORANGE_MONEY_AUTHORIZATION_HEADER: str = os.getenv("ORANGE_MONEY_AUTHORIZATION_HEADER", "")
    ORANGE_MONEY_ENABLED: bool = all([
        os.getenv("ORANGE_MONEY_CLIENT_ID", ""),
        os.getenv("ORANGE_MONEY_CLIENT_SECRET", "")
    ])
    
    # ============================================
    # Twilio (SMS & Verify)
    # ============================================
    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_PHONE_NUMBER: str = os.getenv("TWILIO_PHONE_NUMBER", "")
    TWILIO_VERIFY_SERVICE_SID: str = os.getenv("TWILIO_VERIFY_SERVICE_SID", "")
    TWILIO_ENABLED: bool = all([
        os.getenv("TWILIO_ACCOUNT_SID", ""),
        os.getenv("TWILIO_AUTH_TOKEN", "")
    ])
    
    # ============================================
    # Stripe (International Payments)
    # ============================================
    STRIPE_SECRET_KEY: str = os.getenv("STRIPE_SECRET_KEY", "")
    STRIPE_WEBHOOK_SECRET: str = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    STRIPE_PUBLISHABLE_KEY: str = os.getenv("STRIPE_PUBLISHABLE_KEY", "")
    STRIPE_ENABLED: bool = os.getenv("STRIPE_SECRET_KEY", "") != ""
    
    # ============================================
    # AWS S3 (File Storage)
    # ============================================
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    AWS_S3_BUCKET: str = os.getenv("AWS_S3_BUCKET", "sound-it-uploads")
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    AWS_S3_ENDPOINT: str = os.getenv("AWS_S3_ENDPOINT", "")
    AWS_CLOUDFRONT_URL: str = os.getenv("AWS_CLOUDFRONT_URL", "")
    AWS_ENABLED: bool = all([
        os.getenv("AWS_ACCESS_KEY_ID", ""),
        os.getenv("AWS_SECRET_ACCESS_KEY", "")
    ])
    
    # ============================================
    # hearthis.at (DJ Mixes)
    # ============================================
    HEARTHIS_API_KEY: str = os.getenv("HEARTHIS_API_KEY", "")
    HEARTHIS_API_URL: str = os.getenv("HEARTHIS_API_URL", "https://hearthis.at/api/v1/")
    
    # ============================================
    # Google OAuth
    # ============================================
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URI: str = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/api/v1/auth/google/callback")
    
    # ============================================
    # Security Settings
    # ============================================
    # Allowed hosts for CORS (comma-separated string, use get_allowed_hosts() to get list)
    ALLOWED_HOSTS: str = "localhost,127.0.0.1"
    
    # CORS origins (comma-separated string, use get_cors_origins() to get list)
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    
    # Rate limiting
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))  # seconds
    
    # File upload limits
    MAX_UPLOAD_SIZE: int = int(os.getenv("MAX_UPLOAD_SIZE", "10485760"))  # 10MB
    ALLOWED_UPLOAD_TYPES: List[str] = [
        "image/jpeg", "image/png", "image/gif", "image/webp",
        "video/mp4", "video/quicktime",
        "audio/mpeg", "audio/wav", "audio/mp3"
    ]
    
    # ============================================
    # Monitoring & Logging
    # ============================================
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/production.log")
    ERROR_WEBHOOK_URL: str = os.getenv("ERROR_WEBHOOK_URL", "")
    
    # Sentry (Error Tracking)
    SENTRY_DSN: str = os.getenv("SENTRY_DSN", "")
    SENTRY_ENABLED: bool = os.getenv("SENTRY_DSN", "") != ""
    
    # ============================================
    # Platform Settings
    # ============================================
    # Commission rate (10%)
    PLATFORM_COMMISSION_RATE: float = float(os.getenv("PLATFORM_COMMISSION_RATE", "0.10"))
    
    # Minimum payout amount
    MIN_PAYOUT_AMOUNT: float = float(os.getenv("MIN_PAYOUT_AMOUNT", "100.00"))
    
    # Currency
    DEFAULT_CURRENCY: str = os.getenv("DEFAULT_CURRENCY", "SLE")
    
    # Timezone
    TIMEZONE: str = os.getenv("TIMEZONE", "Africa/Freetown")
    
    class Config:
        env_file = ".env.production"
        env_file_encoding = "utf-8"
        extra = "ignore"
        case_sensitive = False
    
    def validate_production_settings(self):
        """Validate critical production settings"""
        errors = []
        
        if not self.JWT_SECRET or self.JWT_SECRET == "jwt-secret-key":
            errors.append("JWT_SECRET must be set to a secure value in production")
        
        if not self.SECRET_KEY or "change" in self.SECRET_KEY.lower():
            errors.append("SECRET_KEY must be set to a secure value in production")
        
        if "sqlite" in self.DATABASE_URL.lower():
            errors.append("SQLite should not be used in production. Use PostgreSQL.")
        
        if errors:
            raise ValueError("Production validation failed:\n" + "\n".join(f"  - {e}" for e in errors))
        
        return True
    
    def get_allowed_hosts(self) -> List[str]:
        """Get ALLOWED_HOSTS as a list"""
        return [host.strip() for host in self.ALLOWED_HOSTS.split(",") if host.strip()]
    
    def get_cors_origins(self) -> List[str]:
        """Get CORS_ORIGINS as a list"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


@lru_cache()
def get_settings() -> ProductionSettings:
    """Get cached settings instance"""
    settings = ProductionSettings()
    
    # Validate in production
    if not settings.DEBUG:
        settings.validate_production_settings()
    
    return settings


# Export for backward compatibility
Settings = ProductionSettings
