from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    # Database
    DATABASE_URL: str

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # OAuth (optional - will be empty for initial development)
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    DISCORD_CLIENT_ID: Optional[str] = None
    DISCORD_CLIENT_SECRET: Optional[str] = None

    # Application
    SQUIG_VERSION: str = "0.4.21"
    APP_NAME: str = "SquigLeague"

    # Admin
    ADMIN_IP: Optional[str] = None

    # Monitoring
    SENTRY_DSN: Optional[str] = None

    # Base URL for OAuth callbacks (set to production domain in prod)
    BASE_URL: str = "https://"

    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost",
        "http://localhost:5173",
        "http://localhost:80",
        "https://squigleague.com",
        "https://www.squigleague.com",
    ]

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT == "production"

    @property
    def oauth_enabled(self) -> bool:
        """Check if OAuth is configured."""
        return bool(
            self.GOOGLE_CLIENT_ID
            and self.GOOGLE_CLIENT_SECRET
            or self.DISCORD_CLIENT_ID
            and self.DISCORD_CLIENT_SECRET
        )


settings = Settings()
