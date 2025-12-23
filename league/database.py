import json
from sqlalchemy import text
from datetime import datetime, timedelta, date
from typing import Optional, List, Dict, Any
import logging
from core.database import get_db

logger = logging.getLogger(__name__)

def create_season(
    name: str,
    season_number: int,
    start_date: date,
    league_format: str,
    format_config: dict,
    scoring_system: str,
    scoring_config: dict,
    elo_k_factor: int,
    competition_class: str,
    registration_deadline: Optional[date] = None
) -> Optional[int]:
    """Create a new season"""
    try:
        with get_db() as db:
            query = text("""
                INSERT INTO league_seasons (
                    name, season_number, start_date, registration_deadline,
                    league_format, format_config, scoring_system, scoring_config,
                    elo_k_factor, competition_class
                )
                VALUES (
                    :name, :season_number, :start_date, :registration_deadline,
                    :league_format, :format_config::jsonb, :scoring_system, :scoring_config::jsonb,
                    :elo_k_factor, :competition_class
                )
                RETURNING id
            """)
            result = db.execute(query, {
                "name": name,
                "season_number": season_number,
                "start_date": start_date,
                "registration_deadline": registration_deadline,
                "league_format": league_format,
                "format_config": json.dumps(format_config),
                "scoring_system": scoring_system,
                "scoring_config": json.dumps(scoring_config),
                "elo_k_factor": elo_k_factor,
                "competition_class": competition_class
            }).fetchone()
            return result[0] if result else None
    except Exception as e:
        logger.error(f"Error creating season: {e}")
        return None

def get_season(season_id: int) -> Optional[dict]:
    """Get season by ID"""
    try:
        with get_db() as db:
            query = text("""
                SELECT id, name, season_number, start_date, registration_deadline,
                       league_format, format_config, scoring_system, scoring_config,
                       elo_k_factor, competition_class, status, created_at
                FROM league_seasons
                WHERE id = :id
            """)
            result = db.execute(query, {"id": season_id}).fetchone()

            if not result:
                return None

            return {
                "id": result[0],
                "name": result[1],
                "season_number": result[2],
                "start_date": result[3],
                "registration_deadline": result[4],
                "league_format": result[5],
                "format_config": result[6],
                "scoring_system": result[7],
                "scoring_config": result[8],
                "elo_k_factor": result[9],
                "competition_class": result[10],
                "status": result[11],
                "created_at": result[12]
            }
    except Exception as e:
        logger.error(f"Error getting season: {e}")
        return None

def list_seasons(limit: int = 20) -> List[dict]:
    """List all seasons (most recent first)"""
    try:
        with get_db() as db:
            query = text("""
                SELECT s.id, s.name, s.season_number, s.start_date,
                       s.league_format, s.scoring_system, s.status,
                       COUNT(p.id) as participant_count
                FROM league_seasons s
                LEFT JOIN league_participants p ON s.id = p.season_id
                GROUP BY s.id
                ORDER BY s.season_number DESC
                LIMIT :limit
            """)
            results = db.execute(query, {"limit": limit}).fetchall()

            return [
                {
                    "id": row[0],
                    "name": row[1],
                    "season_number": row[2],
                    "start_date": row[3],
                    "league_format": row[4],
                    "scoring_system": row[5],
                    "status": row[6],
                    "participant_count": row[7]
                }
                for row in results
            ]
    except Exception as e:
        logger.error(f"Error listing seasons: {e}")
        return []

def get_or_create_player(discord_id: str, discord_name: str, discord_avatar: Optional[str] = None) -> Optional[int]:
    """Get existing player or create new one"""
    try:
        with get_db() as db:
            query = text("SELECT id FROM league_players WHERE discord_id = :discord_id")
            result = db.execute(query, {"discord_id": discord_id}).fetchone()

            if result:
                return result[0]

            insert_query = text("""
                INSERT INTO league_players (discord_id, discord_name, discord_avatar)
                VALUES (:discord_id, :discord_name, :discord_avatar)
                RETURNING id
            """)
            result = db.execute(insert_query, {
                "discord_id": discord_id,
                "discord_name": discord_name,
                "discord_avatar": discord_avatar
            }).fetchone()

            return result[0] if result else None
    except Exception as e:
        logger.error(f"Error getting/creating player: {e}")
        return None

def get_player_by_discord_id(discord_id: str) -> Optional[dict]:
    """Get player by Discord ID"""
    try:
        with get_db() as db:
            query = text("""
                SELECT id, discord_id, discord_name, discord_avatar,
                       global_elo, peak_elo, total_games, total_wins, total_draws, total_losses
                FROM league_players
                WHERE discord_id = :discord_id
            """)
            result = db.execute(query, {"discord_id": discord_id}).fetchone()

            if not result:
                return None

            return {
                "id": result[0],
                "discord_id": result[1],
                "discord_name": result[2],
                "discord_avatar": result[3],
                "global_elo": result[4],
                "peak_elo": result[5],
                "total_games": result[6],
                "total_wins": result[7],
                "total_draws": result[8],
                "total_losses": result[9]
            }
    except Exception as e:
        logger.error(f"Error getting player: {e}")
        return None

def register_participant(season_id: int, player_id: int, starting_elo: int) -> Optional[int]:
    """Register a player for a season"""
    try:
        with get_db() as db:
            query = text("""
                INSERT INTO league_participants (season_id, player_id, starting_elo, current_season_elo)
                VALUES (:season_id, :player_id, :starting_elo, :current_season_elo)
                RETURNING id
            """)
            result = db.execute(query, {
                "season_id": season_id,
                "player_id": player_id,
                "starting_elo": starting_elo,
                "current_season_elo": starting_elo
            }).fetchone()
            return result[0] if result else None
    except Exception as e:
        logger.error(f"Error registering participant: {e}")
        return None

def get_participant(player_id: int, season_id: int) -> Optional[dict]:
    """Get participant record"""
    try:
        with get_db() as db:
            query = text("""
                SELECT p.id, p.season_id, p.player_id, p.group_number,
                       p.group_points, p.group_games_played, p.group_avg_score,
                       p.qualified_for_playoffs, p.playoff_position,
                       p.starting_elo, p.current_season_elo,
                       pl.discord_name
                FROM league_participants p
                JOIN league_players pl ON p.player_id = pl.id
                WHERE p.player_id = :player_id AND p.season_id = :season_id
            """)
            result = db.execute(query, {"player_id": player_id, "season_id": season_id}).fetchone()

            if not result:
                return None

            return {
                "id": result[0],
                "season_id": result[1],
                "player_id": result[2],
                "group_number": result[3],
                "group_points": result[4],
                "group_games_played": result[5],
                "group_avg_score": float(result[6]) if result[6] else 0,
                "qualified_for_playoffs": result[7],
                "playoff_position": result[8],
                "starting_elo": result[9],
                "current_season_elo": result[10],
                "player_name": result[11]
            }
    except Exception as e:
        logger.error(f"Error getting participant: {e}")
        return None

def get_group_participants(season_id: int, group_number: int) -> List[dict]:
    """Get all participants in a group"""
    try:
        with get_db() as db:
            query = text("""
                SELECT p.id, p.player_id, p.group_points, p.group_games_played,
                       p.group_avg_score, p.current_season_elo,
                       pl.discord_name
                FROM league_participants p
                JOIN league_players pl ON p.player_id = pl.id
                WHERE p.season_id = :season_id AND p.group_number = :group_number
                ORDER BY p.group_points DESC
            """)
            results = db.execute(query, {"season_id": season_id, "group_number": group_number}).fetchall()

            return [
                {
                    "id": row[0],
                    "player_id": row[1],
                    "group_points": row[2],
                    "group_games_played": row[3],
                    "group_avg_score": float(row[4]) if row[4] else 0,
                    "current_season_elo": row[5],
                    "player_name": row[6]
                }
                for row in results
            ]
    except Exception as e:
        logger.error(f"Error getting group participants: {e}")
        return []

def create_match(
    season_id: int,
    phase: str,
    player1_id: int,
    player2_id: int,
    player1_score: int,
    player2_score: int,
    player1_points: int,
    player2_points: int,
    winner_id: Optional[int],
    elo_change_p1: Optional[int],
    elo_change_p2: Optional[int],
    k_factor_p1: Optional[int],
    k_factor_p2: Optional[int],
    counted_for_elo: bool,
    mission: Optional[str],
    submitted_by: str
) -> Optional[int]:
    """Create a match record"""
    try:
        with get_db() as db:
            query = text("""
                INSERT INTO league_matches (
                    season_id, phase, player1_id, player2_id,
                    player1_score, player2_score, player1_points, player2_points,
                    winner_id, elo_change_p1, elo_change_p2,
                    k_factor_p1, k_factor_p2, counted_for_elo,
                    mission, submitted_by
                )
                VALUES (
                    :season_id, :phase, :player1_id, :player2_id,
                    :player1_score, :player2_score, :player1_points, :player2_points,
                    :winner_id, :elo_change_p1, :elo_change_p2,
                    :k_factor_p1, :k_factor_p2, :counted_for_elo,
                    :mission, :submitted_by
                )
                RETURNING id
            """)
            result = db.execute(query, {
                "season_id": season_id,
                "phase": phase,
                "player1_id": player1_id,
                "player2_id": player2_id,
                "player1_score": player1_score,
                "player2_score": player2_score,
                "player1_points": player1_points,
                "player2_points": player2_points,
                "winner_id": winner_id,
                "elo_change_p1": elo_change_p1,
                "elo_change_p2": elo_change_p2,
                "k_factor_p1": k_factor_p1,
                "k_factor_p2": k_factor_p2,
                "counted_for_elo": counted_for_elo,
                "mission": mission,
                "submitted_by": submitted_by
            }).fetchone()
            return result[0] if result else None
    except Exception as e:
        logger.error(f"Error creating match: {e}")
        return None

def get_match(match_id: int) -> Optional[dict]:
    """Get match by ID"""
    try:
        with get_db() as db:
            query = text("""
                SELECT id, season_id, phase, player1_id, player2_id,
                       player1_score, player2_score, player1_points, player2_points,
                       winner_id, match_date
                FROM league_matches
                WHERE id = :id
            """)
            result = db.execute(query, {"id": match_id}).fetchone()

            if not result:
                return None

            return {
                "id": result[0],
                "season_id": result[1],
                "phase": result[2],
                "player1_id": result[3],
                "player2_id": result[4],
                "player1_score": result[5],
                "player2_score": result[6],
                "player1_points": result[7],
                "player2_points": result[8],
                "winner_id": result[9],
                "match_date": result[10]
            }
    except Exception as e:
        logger.error(f"Error getting match: {e}")
        return None

def update_participant_group(participant_id: int, group_number: int) -> bool:
    """Update participant's group assignment"""
    try:
        with get_db() as db:
            query = text("""
                UPDATE league_participants
                SET group_number = :group_number
                WHERE id = :id
            """)
            db.execute(query, {"id": participant_id, "group_number": group_number})
            return True
    except Exception as e:
        logger.error(f"Error updating participant group: {e}")
        return False

def update_participant_stats(
    participant_id: int,
    group_points_delta: int,
    score: int
) -> bool:
    """Update participant statistics after a match"""
    try:
        with get_db() as db:
            query = text("""
                UPDATE league_participants
                SET group_points = group_points + :points_delta,
                    group_games_played = group_games_played + 1,
                    group_avg_score = (
                        (COALESCE(group_avg_score, 0) * group_games_played + :score) /
                        (group_games_played + 1)
                    )
                WHERE id = :id
            """)
            db.execute(query, {
                "id": participant_id,
                "points_delta": group_points_delta,
                "score": score
            })
            return True
    except Exception as e:
        logger.error(f"Error updating participant stats: {e}")
        return False

def update_player_elo(player_id: int, new_elo: int, change: int) -> bool:
    """Update player's global ELO"""
    try:
        with get_db() as db:
            query = text("""
                UPDATE league_players
                SET global_elo = :new_elo,
                    peak_elo = GREATEST(peak_elo, :new_elo),
                    last_active = NOW()
                WHERE id = :id
            """)
            db.execute(query, {"id": player_id, "new_elo": new_elo})
            return True
    except Exception as e:
        logger.error(f"Error updating player ELO: {e}")
        return False

def update_player_stats(player_id: int, won: bool, draw: bool) -> bool:
    """Update player career statistics"""
    try:
        with get_db() as db:
            query = text("""
                UPDATE league_players
                SET total_games = total_games + 1,
                    total_wins = total_wins + :wins,
                    total_draws = total_draws + :draws,
                    total_losses = total_losses + :losses
                WHERE id = :id
            """)
            wins = 1 if won else 0
            draws = 1 if draw else 0
            losses = 1 if not won and not draw else 0

            db.execute(query, {
                "id": player_id,
                "wins": wins,
                "draws": draws,
                "losses": losses
            })
            return True
    except Exception as e:
        logger.error(f"Error updating player stats: {e}")
        return False

def check_database_health() -> bool:
    """Check if database connection is working"""
    try:
        with get_db() as db:
            db.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False

def get_stats() -> dict:
    """Get league statistics"""
    try:
        with get_db() as db:
            total_seasons = db.execute(text("SELECT COUNT(*) FROM league_seasons")).fetchone()[0]
            total_players = db.execute(text("SELECT COUNT(*) FROM league_players")).fetchone()[0]
            total_matches = db.execute(text("SELECT COUNT(*) FROM league_matches")).fetchone()[0]

            return {
                "total_seasons": total_seasons,
                "total_players": total_players,
                "total_matches": total_matches
            }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return {}
