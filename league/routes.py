from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
import logging
import os

from league import database
from league.models import (
    SeasonCreateRequest,
    SeasonResponse,
    PlayerRegisterRequest,
    MatchSubmitRequest,
    MatchResponse,
    StandingsResponse
)
from league.services.factory import FormatHandlerFactory, ScoringSystemFactory
from league.services.elo import EloService
from core.database import check_database_health

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/league", tags=["league"])

APP_VERSION = os.getenv("SQUIG_VERSION", "0.1.0")

@router.get("/health")
async def api_health():
    """API health check"""
    db_healthy = check_database_health()
    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "module": "league",
        "version": APP_VERSION,
        "database": "connected" if db_healthy else "disconnected"
    }

@router.get("/seasons")
async def list_seasons():
    """List all seasons"""
    seasons = database.list_seasons()
    return {"seasons": seasons}

@router.get("/seasons/{season_id}")
async def get_season(season_id: int):
    """Get season details"""
    season = database.get_season(season_id)
    if not season:
        raise HTTPException(404, "Season not found")
    return season

@router.get("/seasons/{season_id}/standings", response_model=StandingsResponse)
async def get_standings(season_id: int):
    """Get season standings - universal, returns format-specific data"""
    season = database.get_season(season_id)
    if not season:
        raise HTTPException(404, "Season not found")

    format_handler = FormatHandlerFactory.create(season)
    standings = format_handler.get_standings()

    scoring_system = ScoringSystemFactory.create(season)
    display_format = scoring_system.get_display_format()

    return StandingsResponse(
        season_id=season_id,
        season_name=season['name'],
        league_format=season['league_format'],
        standings=standings,
        display_format=display_format
    )

@router.get("/stats")
async def get_stats():
    """Get league statistics"""
    stats = database.get_stats()
    return {
        "total_seasons": stats.get("total_seasons", 0),
        "total_players": stats.get("total_players", 0),
        "total_matches": stats.get("total_matches", 0),
        "version": APP_VERSION
    }
