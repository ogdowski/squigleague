from contextlib import asynccontextmanager

from app.config import settings
from app.db import create_db_and_tables
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


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


from app.matchup.routes import router as matchup_router

# Import and include routers
from app.users.routes import router as users_router

app.include_router(users_router, prefix="/auth", tags=["Authentication"])
app.include_router(matchup_router, prefix="/matchup", tags=["Matchup"])
