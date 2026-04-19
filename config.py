import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Sound It API"
    DEBUG: bool = False
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    BASE_URL: str = os.getenv("BASE_URL", "http://localhost:8000")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Validate SECRET_KEY in production
        if not self.DEVELOPER_MODE:
            if not self.SECRET_KEY:
                raise ValueError(
                    "SECRET_KEY environment variable is REQUIRED for production. "
                    "Generate a secure key with: openssl rand -hex 32"
                )
            if len(self.SECRET_KEY) < 32:
                import warnings
                warnings.warn(
                    "SECURITY WARNING: SECRET_KEY should be at least 32 characters for production security",
                    RuntimeWarning
                )
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # JWT
    JWT_SECRET: str = os.getenv("JWT_SECRET") or os.getenv("SECRET_KEY", "")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = int(os.getenv("JWT_EXPIRATION_MINUTES", "15"))
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
    SENDGRID_FROM_EMAIL: str = ""  # e.g., noreply@soundit.com
    
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
    
    # Development Mode
    DEVELOPER_MODE: bool = True
    
    
    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
