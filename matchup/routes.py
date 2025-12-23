from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime
import hashlib
import logging
import os

from matchup import database, words
from matchup.models import (
    CreateExchangeRequest,
    RespondExchangeRequest,
    ExchangeStatusResponse
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/matchup", tags=["matchup"])

APP_VERSION = os.getenv("SQUIG_VERSION", "0.1.0")

@router.get("/health")
async def api_health():
    """API health check"""
    return {
        "status": "healthy",
        "module": "matchup",
        "version": APP_VERSION
    }

@router.post("/exchange/create")
async def create_exchange(request: Request, data: CreateExchangeRequest):
    """Create new exchange"""
    try:
        exchange_id = words.generate_exchange_id(
            check_exists_callback=database.exchange_exists
        )

        hash_value = hashlib.sha256(data.list_content.encode()).hexdigest()

        success = database.create_exchange(
            exchange_id=exchange_id,
            list_a=data.list_content,
            hash_a=hash_value,
            timestamp_a=datetime.now()
        )

        if not success:
            raise HTTPException(500, "Failed to create exchange")

        logger.info(f"Created exchange: {exchange_id}")

        return JSONResponse({
            "exchange_id": exchange_id,
            "hash_a": hash_value
        })

    except Exception as e:
        logger.error(f"Error creating exchange: {e}")
        raise HTTPException(500, "Internal server error")

@router.get("/exchange/{exchange_id}")
async def get_exchange(request: Request, exchange_id: str):
    """Get exchange data"""
    if not words.validate_exchange_id(exchange_id):
        raise HTTPException(404, "Invalid exchange ID format")

    exchange = database.get_exchange(exchange_id)

    if not exchange:
        raise HTTPException(404, "Exchange not found")

    response_data = {
        "id": exchange["id"],
        "hash_a": exchange["hash_a"],
        "timestamp_a": exchange["timestamp_a"].strftime("%Y-%m-%d %H:%M UTC"),
        "status": "complete" if exchange["list_b"] is not None else "waiting"
    }

    if exchange["list_b"] is not None:
        response_data.update({
            "list_a": exchange["list_a"],
            "list_b": exchange["list_b"],
            "hash_b": exchange["hash_b"],
            "timestamp_b": exchange["timestamp_b"].strftime("%Y-%m-%d %H:%M UTC")
        })

    return response_data

@router.post("/exchange/{exchange_id}/respond")
async def respond_exchange(request: Request, exchange_id: str, data: RespondExchangeRequest):
    """Player B submits their list"""
    if not words.validate_exchange_id(exchange_id):
        raise HTTPException(404, "Invalid exchange ID")

    exchange = database.get_exchange(exchange_id)
    if not exchange:
        raise HTTPException(404, "Exchange not found")

    if exchange["list_b"] is not None:
        raise HTTPException(400, "Exchange already complete")

    hash_value = hashlib.sha256(data.list_content.encode()).hexdigest()

    success = database.update_exchange_with_list_b(
        exchange_id=exchange_id,
        list_b=data.list_content,
        hash_b=hash_value,
        timestamp_b=datetime.now()
    )

    if not success:
        raise HTTPException(500, "Failed to update exchange")

    logger.info(f"Exchange completed: {exchange_id}")

    return JSONResponse({"success": True, "exchange_id": exchange_id})

@router.get("/exchange/{exchange_id}/status", response_model=ExchangeStatusResponse)
async def check_status(request: Request, exchange_id: str):
    """Check if exchange is complete (for polling)"""
    ready = database.exchange_is_complete(exchange_id)
    return ExchangeStatusResponse(ready=ready)

@router.get("/stats")
async def get_stats():
    """Get public statistics"""
    stats = database.get_stats()
    return {
        "completed_exchanges": stats.get("complete_exchanges", 0),
        "version": APP_VERSION
    }
