from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import logging

from matchup.routes import router as matchup_router
from league.routes import router as league_router
from core.database import check_database_health

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

APP_VERSION = os.getenv("SQUIG_VERSION", "0.2.0")

app = FastAPI(
    title="Squig League API",
    description="Unified API for Warhammer management platform",
    version=APP_VERSION
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(matchup_router)
app.include_router(league_router)

@app.on_event("startup")
async def startup_event():
    """Initialize app on startup"""
    logger.info(f"🚀 Squig League API v{APP_VERSION} starting up...")

    if not check_database_health():
        logger.error("❌ Database connection failed!")
        raise Exception("Cannot connect to PostgreSQL")

    logger.info("✅ Database connection successful")
    logger.info("🎯 Squig League API ready!")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("👋 Squig League API shutting down...")

@app.get("/health")
async def health_check():
    """Global health check"""
    db_healthy = check_database_health()
    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "version": APP_VERSION,
        "database": "connected" if db_healthy else "disconnected",
        "modules": {
            "matchup": "active",
            "league": "active"
        }
    }

@app.get("/")
async def root():
    """API root"""
    return {
        "name": "Squig League API",
        "version": APP_VERSION,
        "modules": ["matchup", "league"],
        "docs": "/docs"
    }
