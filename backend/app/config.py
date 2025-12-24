"""
Application Configuration

Uses Pydantic BaseSettings for environment variable management.
"""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = "SquigLeague"
    APP_VERSION: str = "2.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "postgresql://squigleague:changeme@db:5432/squigleague"
    
    # Security
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Google OAuth
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    
    # Discord OAuth
    DISCORD_CLIENT_ID: Optional[str] = None
    DISCORD_CLIENT_SECRET: Optional[str] = None
    
    # URLs
    BACKEND_URL: str = "http://localhost:8000"
    FRONTEND_URL: str = "http://localhost:5173"
    
    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost",
        "http://localhost:5173",
        "http://localhost:8000",
    ]
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


# Global settings instance
settings = Settings()
