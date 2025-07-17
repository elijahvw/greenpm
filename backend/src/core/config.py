"""
Green PM - Configuration Settings
"""
from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    # App settings
    APP_NAME: str = "Green PM"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "dev")
    PROJECT_ID: str = os.getenv("PROJECT_ID", "greenpm")
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    
    # Security
    JWT_SECRET: str = os.getenv("JWT_SECRET", "")
    APP_SECRET_KEY: str = os.getenv("APP_SECRET_KEY", "")
    ENCRYPTION_KEY: str = os.getenv("ENCRYPTION_KEY", "")
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "https://*.run.app",
        "https://*.googleusercontent.com"
    ]
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # External APIs
    STRIPE_SECRET_KEY: str = os.getenv("STRIPE_SECRET_KEY", "")
    STRIPE_PUBLISHABLE_KEY: str = os.getenv("STRIPE_PUBLISHABLE_KEY", "")
    STRIPE_WEBHOOK_SECRET: str = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    
    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_PHONE_NUMBER: str = os.getenv("TWILIO_PHONE_NUMBER", "")
    
    SENDGRID_API_KEY: str = os.getenv("SENDGRID_API_KEY", "")
    
    # Firebase
    FIREBASE_CONFIG: str = os.getenv("FIREBASE_CONFIG", "")
    
    # Storage
    DOCUMENTS_BUCKET: str = f"{PROJECT_ID}-{ENVIRONMENT}-documents"
    PROPERTY_IMAGES_BUCKET: str = f"{PROJECT_ID}-{ENVIRONMENT}-property-images"
    MAINTENANCE_IMAGES_BUCKET: str = f"{PROJECT_ID}-{ENVIRONMENT}-maintenance-images"
    BACKUPS_BUCKET: str = f"{PROJECT_ID}-{ENVIRONMENT}-backups"
    
    # Rate limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    # File upload
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: List[str] = [
        "image/jpeg", "image/png", "image/gif",
        "application/pdf", "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()