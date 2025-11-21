# herald/main.py
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import hashlib
import os
import logging
import psutil
import sys

# Add parent directory to path for squire module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import local modules
import database
import words
from models import (
    CreateExchangeRequest,
    RespondExchangeRequest,
    CreateExchangeResponse,
    ExchangeStatusResponse,
    HealthCheckResponse,
    ResourcesResponse,
)

# Import Squire routes
from squire.routes import router as squire_router

# Application version (from environment or default)
APP_VERSION = os.getenv("SQUIG_VERSION", "0.1.0")

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Herald API - Squig League",
    description="API for fair and secure army list exchange",
    version=APP_VERSION,
)

# Include Squire router for battle plan randomization
app.include_router(squire_router)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Get admin key from environment
ADMIN_KEY = os.getenv("ADMIN_KEY", "change-this-key")

# ═══════════════════════════════════════════════
# MIDDLEWARE
# ═══════════════════════════════════════════════

# User-Agent filtering
BLOCKED_USER_AGENTS = ["wget", "scrapy", "python-requests", "beautifulsoup", "scraper"]
ALLOWED_BOTS = [
    "googlebot",
    "bingbot",
    "mozilla",
    "chrome",
    "safari",
    "edge",
    "firefox",
]


@app.middleware("http")
async def filter_bots_and_log_requests(request: Request, call_next):
    """Filter bad bots and log all requests"""
    user_agent = request.headers.get("user-agent", "").lower()
    client_ip = request.client.host

    # Allow health check endpoints (for Docker healthcheck and monitoring)
    if request.url.path in ["/health", "/docs", "/openapi.json"]:
        response = await call_next(request)
        return response

    # Allow browser traffic (check first for performance)
    if any(browser in user_agent for browser in ALLOWED_BOTS):
        response = await call_next(request)
        return response

    # Check for blocked user agents
    for blocked in BLOCKED_USER_AGENTS:
        if blocked in user_agent:
            logger.warning(f"Blocked bot: {user_agent} from {client_ip}")
            raise HTTPException(403, "Bot traffic not allowed")

    # Log request (async to not block request)
    try:
        database.log_request(
            ip=client_ip, endpoint=request.url.path, user_agent=user_agent
        )
    except Exception as e:
        logger.error(f"Failed to log request: {e}")

    response = await call_next(request)
    return response


@app.middleware("http")
async def add_template_context(request: Request, call_next):
    """Add global context to all templates"""
    request.state.current_year = datetime.now().year
    request.state.app_version = APP_VERSION
    response = await call_next(request)
    return response


# ═══════════════════════════════════════════════
# SCHEDULER - Auto cleanup
# ═══════════════════════════════════════════════


def cleanup_old_data():
    """Delete exchanges and logs older than 30 days"""
    try:
        deleted_exchanges = database.delete_old_exchanges(days=30)
        deleted_logs = database.delete_old_logs(days=30)
        logger.info(
            f"Cleanup completed: {deleted_exchanges} exchanges, {deleted_logs} deleted"
        )
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")


scheduler = BackgroundScheduler()

# ═══════════════════════════════════════════════
# STARTUP / SHUTDOWN
# ═══════════════════════════════════════════════


@app.on_event("startup")
async def startup_event():
    """Initialize app on startup"""
    logger.info("🚀 Herald starting up...")

    # Start background scheduler (skip in test environment)
    if os.environ.get("TESTING") != "true":
        scheduler.add_job(
            cleanup_old_data,
            "interval",
            hours=24,
            next_run_time=datetime.now(),  # Run immediately on startup
        )
        scheduler.start()
        logger.info("Background scheduler started")

    # Check database connection
    if not database.check_database_health():
        logger.error("❌ Database connection failed!")
        raise Exception("Cannot connect to PostgreSQL")

    logger.info("✅ Database connection successful")

    # Run initial cleanup
    cleanup_old_data()

    logger.info("🎯 Herald ready!")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    scheduler.shutdown()
    logger.info("👋 Herald shutting down...")


# ═══════════════════════════════════════════════
# ROUTES
# ═══════════════════════════════════════════════


@app.get("/api/herald/health")
async def api_health():
    """API health check"""
    return {"status": "healthy", "module": "herald", "version": APP_VERSION}


@app.post("/api/herald/exchange/create")
@limiter.limit("10/hour")
async def create_exchange(request: Request, data: CreateExchangeRequest):
    """Create new exchange"""
    try:
        # Generate unique exchange ID
        exchange_id = words.generate_exchange_id(
            check_exists_callback=database.exchange_exists
        )

        # Calculate SHA-256 hash
        hash_value = hashlib.sha256(data.list_content.encode()).hexdigest()

        # Create exchange in database
        success = database.create_exchange(
            exchange_id=exchange_id,
            list_a=data.list_content,
            hash_a=hash_value,
            timestamp_a=datetime.now(),
        )

        if not success:
            raise HTTPException(500, "Failed to create exchange")

        logger.info(f"Created exchange: {exchange_id}")

        return JSONResponse({"exchange_id": exchange_id, "hash_a": hash_value})

    except Exception as e:
        logger.error(f"Error creating exchange: {e}")
        raise HTTPException(500, "Internal server error")


@app.get("/api/herald/exchange/{exchange_id}")
@limiter.limit("30/minute")
async def get_exchange(request: Request, exchange_id: str):
    """Get exchange data"""
    # Validate exchange ID format
    if not words.validate_exchange_id(exchange_id):
        raise HTTPException(404, "Invalid exchange ID format")

    # Get exchange from database
    exchange = database.get_exchange(exchange_id)

    if not exchange:
        raise HTTPException(404, "Exchange not found")

    # Build response data
    response_data = {
        "id": exchange["id"],
        "hash_a": exchange["hash_a"],
        "timestamp_a": exchange["timestamp_a"].strftime("%Y-%m-%d %H:%M UTC"),
        "status": "complete" if exchange["list_b"] is not None else "waiting",
    }

    # If exchange is complete, include all data
    if exchange["list_b"] is not None:
        response_data.update(
            {
                "list_a": exchange["list_a"],
                "list_b": exchange["list_b"],
                "hash_b": exchange["hash_b"],
                "timestamp_b": exchange["timestamp_b"].strftime("%Y-%m-%d %H:%M UTC"),
            }
        )

    return response_data


@app.post("/api/herald/exchange/{exchange_id}/respond")
@limiter.limit("20/hour")
async def respond_exchange(
    request: Request, exchange_id: str, data: RespondExchangeRequest
):
    """Player B submits their list"""
    # Validate exchange ID
    if not words.validate_exchange_id(exchange_id):
        raise HTTPException(404, "Invalid exchange ID")

    # Check if exchange exists
    exchange = database.get_exchange(exchange_id)
    if not exchange:
        raise HTTPException(404, "Exchange not found")

    # Check if already responded
    if exchange["list_b"] is not None:
        raise HTTPException(400, "Exchange already complete")

    # Calculate hash
    hash_value = hashlib.sha256(data.list_content.encode()).hexdigest()

    # Update exchange
    success = database.update_exchange_with_list_b(
        exchange_id=exchange_id,
        list_b=data.list_content,
        hash_b=hash_value,
        timestamp_b=datetime.now(),
    )

    if not success:
        raise HTTPException(500, "Failed to update exchange")

    logger.info(f"Exchange completed: {exchange_id}")

    return JSONResponse({"success": True, "exchange_id": exchange_id})


@app.get(
    "/api/herald/exchange/{exchange_id}/status", response_model=ExchangeStatusResponse
)
@limiter.limit("120/minute")
async def check_status(request: Request, exchange_id: str):
    """Check if exchange is complete (for polling)"""
    ready = database.exchange_is_complete(exchange_id)
    return ExchangeStatusResponse(ready=ready)


# ═══════════════════════════════════════════════
# ADMIN / MONITORING ENDPOINTS
# ═══════════════════════════════════════════════


@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint"""
    db_healthy = database.check_database_health()

    return HealthCheckResponse(
        status="healthy" if db_healthy else "unhealthy",
        module="herald",
        database="connected" if db_healthy else "disconnected",
    )


@app.get("/api/herald/stats")
async def get_stats():
    """Get public statistics"""
    stats = database.get_stats()
    return {
        "completed_exchanges": stats.get("complete_exchanges", 0),
        "version": APP_VERSION,
    }


@app.get("/admin/resources", response_model=ResourcesResponse)
@limiter.limit("10/hour")
async def get_resources(request: Request, admin_key: str):
    """Get server resource usage (requires admin key)"""
    if admin_key != ADMIN_KEY:
        raise HTTPException(401, "Invalid admin key")

    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        return ResourcesResponse(
            cpu_percent=cpu_percent,
            memory={
                "used_mb": memory.used / 1024 / 1024,
                "available_mb": memory.available / 1024 / 1024,
                "percent": memory.percent,
            },
            disk={
                "used_gb": disk.used / 1024 / 1024 / 1024,
                "free_gb": disk.free / 1024 / 1024 / 1024,
                "percent": disk.percent,
            },
        )
    except Exception as e:
        logger.error(f"Error getting resources: {e}")
        raise HTTPException(500, "Failed to get resources")


@app.get("/admin/abuse-report")
@limiter.limit("10/hour")
async def abuse_report(
    request: Request, admin_key: str, min_requests: int = 100, hours: int = 1
):
    """Get list of potentially abusive IPs (requires admin key)"""
    if admin_key != ADMIN_KEY:
        raise HTTPException(401, "Invalid admin key")

    try:
        abusive_ips = database.get_abusive_ips(min_requests, hours)
        stats = database.get_stats()

        return {
            "abusive_ips": abusive_ips,
            "stats": stats,
            "threshold": {"min_requests": min_requests, "hours": hours},
        }
    except Exception as e:
        logger.error(f"Error generating abuse report: {e}")
        raise HTTPException(500, "Failed to generate report")


# ═══════════════════════════════════════════════
# ERROR HANDLERS
# ═══════════════════════════════════════════════


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Custom rate limit error response"""
    return JSONResponse(
        status_code=429,
        content={
            "error": "Rate limit exceeded",
            "message": "You're making requests too quickly. Please wait and try again.",
            "retry_after": 60,
        },
    )


@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """Custom 404 handler"""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not found",
            "message": (
                str(exc.detail) if hasattr(exc, "detail") else "Resource not found"
            ),
        },
    )
