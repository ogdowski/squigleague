"""OAuth authentication configuration."""

from typing import Optional
from httpx_oauth.clients.google import GoogleOAuth2
from httpx_oauth.clients.discord import DiscordOAuth2

from app.config import settings


def get_google_oauth_client() -> Optional[GoogleOAuth2]:
    """Get Google OAuth client if credentials are configured."""
    if settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET:
        return GoogleOAuth2(
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
        )
    return None


def get_discord_oauth_client() -> Optional[DiscordOAuth2]:
    """Get Discord OAuth client if credentials are configured."""
    if settings.DISCORD_CLIENT_ID and settings.DISCORD_CLIENT_SECRET:
        return DiscordOAuth2(
            client_id=settings.DISCORD_CLIENT_ID,
            client_secret=settings.DISCORD_CLIENT_SECRET,
            scopes=["identify", "email"],
        )
    return None
