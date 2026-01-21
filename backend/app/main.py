from contextlib import asynccontextmanager
from pathlib import Path

import sentry_sdk
from app.config import settings
from app.db import create_db_and_tables
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware

# Initialize Sentry (before FastAPI app creation)
if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,
        release=f"squigleague@{settings.SQUIG_VERSION}",
        traces_sample_rate=0.1,  # 10% of requests for performance monitoring
        profiles_sample_rate=0.1,
    )


class SentryHttpMiddleware(BaseHTTPMiddleware):
    """Middleware to log 4xx errors to Sentry."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        if 400 <= response.status_code < 500 and settings.SENTRY_DSN:
            with sentry_sdk.push_scope() as scope:
                scope.set_tag("http.status_code", response.status_code)
                scope.set_tag("http.method", request.method)
                scope.set_tag("http.path", request.url.path)
                scope.set_level("warning")
                sentry_sdk.capture_message(
                    f"{response.status_code} {request.method} {request.url.path}",
                    level="warning",
                )

        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for startup and shutdown events."""
    # Startup
    create_db_and_tables()
    yield
    # Shutdown (if needed)


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.SQUIG_VERSION,
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Log 4xx errors to Sentry
if settings.SENTRY_DSN:
    app.add_middleware(SentryHttpMiddleware)


@app.get("/health")
async def health_check():
    """Health check endpoint for Docker and monitoring."""
    return {
        "status": "healthy",
        "version": settings.SQUIG_VERSION,
        "environment": settings.ENVIRONMENT,
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "app": settings.APP_NAME,
        "version": settings.SQUIG_VERSION,
        "docs": "/docs" if settings.DEBUG else "disabled",
    }


# Import and include routers
from app.admin.routes import router as admin_router
from app.league.routes import router as league_router
from app.matchup.routes import router as matchup_router
from app.player.routes import router as player_router
from app.users.routes import router as users_router

app.include_router(users_router, prefix="/auth", tags=["Authentication"])
app.include_router(matchup_router, prefix="/matchup", tags=["Matchup"])
app.include_router(league_router, prefix="/league", tags=["League"])
app.include_router(player_router, prefix="/player", tags=["Player"])
app.include_router(admin_router, prefix="/admin", tags=["Admin"])

# Serve uploaded files (directory created by Dockerfile)
try:
    Path("/app/uploads/avatars").mkdir(parents=True, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory="/app/uploads"), name="uploads")
except PermissionError:
    # Running in environment without write access, skip static mount
    pass
