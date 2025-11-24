# herald/database.py
import logging
import os
from contextlib import contextmanager
from datetime import datetime, timedelta

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)

# Database URL from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://squig:password@postgres:5432/squigleague"
)

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,  # Verify connections before using
    echo=False,  # Set to True for SQL query debugging
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextmanager
def get_db():
    """Context manager for database sessions with automatic rollback on error"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        db.close()


# ═══════════════════════════════════════════════
# EXCHANGE OPERATIONS
# ═══════════════════════════════════════════════


def create_exchange(
    exchange_id: str, list_a: str, hash_a: str, timestamp_a: datetime
) -> bool:
    """
    Create new exchange

    Args:
        exchange_id: Unique exchange identifier
        list_a: Player A's army list
        hash_a: SHA-256 hash of list_a
        timestamp_a: When exchange was created

    Returns:
        bool: True if created successfully
    """
    try:
        with get_db() as db:
            query = text(
                """
                INSERT INTO herald_exchanges (id, list_a, hash_a, timestamp_a)
                VALUES (:id, :list_a, :hash_a, :timestamp_a)
            """
            )
            db.execute(
                query,
                {
                    "id": exchange_id,
                    "list_a": list_a,
                    "hash_a": hash_a,
                    "timestamp_a": timestamp_a,
                },
            )
        return True
    except Exception as e:
        logger.error(f"Error creating exchange: {e}")
        return False


def exchange_exists(exchange_id: str) -> bool:
    """
    Check if exchange ID already exists

    Args:
        exchange_id: Exchange ID to check

    Returns:
        bool: True if exists
    """
    try:
        with get_db() as db:
            query = text("SELECT 1 FROM herald_exchanges WHERE id = :id")
            result = db.execute(query, {"id": exchange_id}).fetchone()
            return result is not None
    except Exception:
        return False


def get_exchange(exchange_id: str) -> dict:
    """
    Get exchange by ID

    Args:
        exchange_id: Exchange ID to retrieve

    Returns:
        dict: Exchange data or None if not found
    """
    try:
        with get_db() as db:
            query = text(
                """
                SELECT id, list_a, hash_a, timestamp_a, list_b, hash_b, timestamp_b, created_at
                FROM herald_exchanges
                WHERE id = :id
            """
            )
            result = db.execute(query, {"id": exchange_id}).fetchone()

            if not result:
                return None

            return {
                "id": result[0],
                "list_a": result[1],
                "hash_a": result[2],
                "timestamp_a": result[3],
                "list_b": result[4],
                "hash_b": result[5],
                "timestamp_b": result[6],
                "created_at": result[7],
            }
    except Exception as e:
        logger.error(f"Error getting exchange: {e}")
        return None


def update_exchange_with_list_b(
    exchange_id: str, list_b: str, hash_b: str, timestamp_b: datetime
) -> bool:
    """
    Add Player B's list to exchange

    Args:
        exchange_id: Exchange ID to update
        list_b: Player B's army list
        hash_b: SHA-256 hash of list_b
        timestamp_b: When Player B responded

    Returns:
        bool: True if updated successfully (and list_b was NULL before)
    """
    try:
        with get_db() as db:
            query = text(
                """
                UPDATE herald_exchanges
                SET list_b = :list_b, hash_b = :hash_b, timestamp_b = :timestamp_b
                WHERE id = :id AND list_b IS NULL
                RETURNING id
            """
            )
            result = db.execute(
                query,
                {
                    "id": exchange_id,
                    "list_b": list_b,
                    "hash_b": hash_b,
                    "timestamp_b": timestamp_b,
                },
            ).fetchone()

            return result is not None
    except Exception as e:
        logger.error(f"Error updating exchange: {e}")
        return False


def exchange_is_complete(exchange_id: str) -> bool:
    """
    Check if exchange has both lists submitted

    Args:
        exchange_id: Exchange ID to check

    Returns:
        bool: True if both lists are present
    """
    try:
        with get_db() as db:
            query = text(
                """
                SELECT list_b IS NOT NULL as complete
                FROM herald_exchanges
                WHERE id = :id
            """
            )
            result = db.execute(query, {"id": exchange_id}).fetchone()
            return result[0] if result else False
    except Exception:
        return False


# ═══════════════════════════════════════════════
# REQUEST LOGGING
# ═══════════════════════════════════════════════


def log_request(ip: str, endpoint: str, user_agent: str):
    """
    Log HTTP request for abuse detection

    Args:
        ip: Client IP address
        endpoint: Request endpoint
        user_agent: User agent string
    """
    try:
        with get_db() as db:
            query = text(
                """
                INSERT INTO herald_request_log (ip, endpoint, user_agent)
                VALUES (:ip, :endpoint, :user_agent)
            """
            )
            db.execute(
                query, {"ip": ip, "endpoint": endpoint, "user_agent": user_agent}
            )
    except Exception as e:
        logger.error(f"Error logging request: {e}")


def get_abusive_ips(min_requests: int = 100, hours: int = 1) -> list:
    """
    Find IPs with excessive request counts

    Args:
        min_requests: Minimum request count to be considered abusive
        hours: Time window to check

    Returns:
        list: List of dicts with ip and count
    """
    try:
        with get_db() as db:
            query = text(
                """
                SELECT ip, COUNT(*) as request_count
                FROM herald_request_log
                WHERE timestamp > NOW() - INTERVAL '1 hour' * :hours
                GROUP BY ip
                HAVING COUNT(*) > :min_requests
                ORDER BY request_count DESC
            """
            )
            results = db.execute(
                query, {"hours": hours, "min_requests": min_requests}
            ).fetchall()

            return [{"ip": str(row[0]), "count": row[1]} for row in results]
    except Exception as e:
        logger.error(f"Error getting abusive IPs: {e}")
        return []


# ═══════════════════════════════════════════════
# CLEANUP OPERATIONS
# ═══════════════════════════════════════════════


def delete_old_exchanges(days: int = 7) -> int:
    """
    Delete exchanges older than specified days

    Args:
        days: Age threshold in days

    Returns:
        int: Number of exchanges deleted
    """
    try:
        with get_db() as db:
            cutoff = datetime.now() - timedelta(days=days)
            query = text(
                """
                DELETE FROM herald_exchanges
                WHERE created_at < :cutoff
            """
            )
            result = db.execute(query, {"cutoff": cutoff})
            count = result.rowcount
            logger.info(f"Deleted {count} old exchanges")
            return count
    except Exception as e:
        logger.error(f"Error deleting old exchanges: {e}")
        return 0


def delete_old_logs(days: int = 7) -> int:
    """
    Delete request logs older than specified days

    Args:
        days: Age threshold in days

    Returns:
        int: Number of logs deleted
    """
    try:
        with get_db() as db:
            cutoff = datetime.now() - timedelta(days=days)
            query = text(
                """
                DELETE FROM herald_request_log
                WHERE timestamp < :cutoff
            """
            )
            result = db.execute(query, {"cutoff": cutoff})
            count = result.rowcount
            logger.info(f"Deleted {count} old log entries")
            return count
    except Exception as e:
        logger.error(f"Error deleting old logs: {e}")
        return 0


# ═══════════════════════════════════════════════
# HEALTH & MONITORING
# ═══════════════════════════════════════════════


def check_database_health() -> bool:
    """
    Check if database connection is working

    Returns:
        bool: True if database is accessible
    """
    try:
        with get_db() as db:
            db.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False


def get_stats() -> dict:
    """
    Get database statistics

    Returns:
        dict: Statistics about exchanges and logs
    """
    try:
        with get_db() as db:
            # Count total exchanges
            total = db.execute(
                text("SELECT COUNT(*) FROM herald_exchanges")
            ).fetchone()[0]

            # Count complete exchanges (both lists submitted)
            complete = db.execute(
                text(
                    """
                SELECT COUNT(*) FROM herald_exchanges WHERE list_b IS NOT NULL
            """
                )
            ).fetchone()[0]

            # Count pending exchanges (waiting for Player B)
            pending = db.execute(
                text(
                    """
                SELECT COUNT(*) FROM herald_exchanges WHERE list_b IS NULL
            """
                )
            ).fetchone()[0]

            return {
                "total_exchanges": total,
                "complete_exchanges": complete,
                "pending_exchanges": pending,
            }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return {}
