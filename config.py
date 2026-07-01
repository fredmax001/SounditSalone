import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Sound It API"
    DEBUG: bool = False
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development").lower()
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    BASE_URL: str = os.getenv("BASE_URL", "http://localhost:8000")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Always require a non-empty SECRET_KEY so tokens/session cookies never use
        # an empty or default signing key, even during local development.
        if not self.SECRET_KEY:
            raise ValueError(
                "SECRET_KEY environment variable is REQUIRED. "
                "Generate a secure key with: openssl rand -hex 32"
            )
        if len(self.SECRET_KEY) < 32 and not self.DEVELOPER_MODE:
            raise ValueError(
                "SECURITY ERROR: SECRET_KEY must be at least 32 characters for production."
            )
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "10"))
    DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "20"))
    DB_POOL_TIMEOUT: int = int(os.getenv("DB_POOL_TIMEOUT", "30"))
    DB_POOL_RECYCLE: int = int(os.getenv("DB_POOL_RECYCLE", "3600"))
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    REDIS_ENABLED: bool = os.getenv("REDIS_ENABLED", "false").lower() == "true"
    
    # Celery Task Queue (defaults to REDIS_URL when not set)
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", os.getenv("REDIS_URL", "redis://localhost:6379/0"))
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", os.getenv("REDIS_URL", "redis://localhost:6379/0"))
    
    # JWT
    JWT_SECRET: str = os.getenv("JWT_SECRET") or os.getenv("SECRET_KEY", "")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))
    JWT_EXPIRATION_MINUTES: int = int(
        os.getenv("JWT_EXPIRATION_MINUTES", str(JWT_EXPIRATION_HOURS * 60))
    )
    JWT_REFRESH_EXPIRATION_DAYS: int = int(os.getenv("JWT_REFRESH_EXPIRATION_DAYS", "7"))
    
    # OTP
    OTP_EXPIRATION_MINUTES: int = 5
    
    # Twilio (SMS)
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = ""  # Your Twilio phone number
    TWILIO_VERIFY_SERVICE_SID: str = ""  # Twilio Verify Service SID
    
    # SendGrid (Email)
    SENDGRID_API_KEY: str = ""
    SENDGRID_FROM_EMAIL: str = ""  # e.g., noreply@sounditentsl.com
    
    # Hostinger SMTP (Email) - Primary email delivery
    SMTP_HOST: str = "smtp.hostinger.com"
    SMTP_PORT: int = 465
    SMTP_USER: str = ""  # e.g., otp@sounditentsl.com
    SMTP_PASS: str = ""  # Email password
    SMTP_FROM: str = ""  # e.g., "Sound It Salone <otp@sounditentsl.com>"
    
    # Stripe
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    
    # Sierra Leone Payment Gateways (Placeholders)
    # Orange Money API
    ORANGE_MONEY_API_KEY: str = ""
    ORANGE_MONEY_MERCHANT_ID: str = ""
    
    # Africell Money API
    AFRICELL_MONEY_API_KEY: str = ""
    AFRICELL_MONEY_MERCHANT_ID: str = ""
    
    # Monime Payment Platform (Sierra Leone)
    MONIME_API_TOKEN: str = ""
    MONIME_SPACE_ID: str = ""
    MONIME_WEBHOOK_SECRET: str = ""
    MONIME_API_VERSION: str = "caph.2025-08-23"
    MONIME_BASE_URL: str = "https://api.monime.io"
    
    # AWS S3 (for file uploads)
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_S3_BUCKET: str = "sound-it-uploads"
    AWS_REGION: str = "us-east-1"
    
    # hearthis.at
    HEARTHIS_API_KEY: str = ""
    HEARTHIS_API_URL: str = "https://hearthis.at/djfredmax/"
    
    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/google/callback"
    
    # Frontend URL (for OAuth callbacks)
    FRONTEND_BASE_URL: str = os.getenv("FRONTEND_BASE_URL", "http://localhost:5173")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # File uploads
    MAX_UPLOAD_SIZE: int = int(os.getenv("MAX_UPLOAD_SIZE", "10485760"))  # 10MB
    
    # Development Mode — default to False so production defaults are safe.
    DEVELOPER_MODE: bool = os.getenv("DEVELOPER_MODE", "false").lower() == "true"

    # Default admin credentials (only used on first startup if no admin exists)
    DEFAULT_ADMIN_EMAIL: str = os.getenv("DEFAULT_ADMIN_EMAIL", "admin")
    DEFAULT_ADMIN_PASSWORD: str = os.getenv("DEFAULT_ADMIN_PASSWORD", "")
    
    # Kimi AI Settings
    KIMI_API_KEY: str = ""
    KIMI_BASE_URL: str = "https://api.kimi.com/coding/v1"
    KIMI_AGENT_API_ID: str = ""
    
    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
