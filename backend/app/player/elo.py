"""ELO rating system for players."""

from datetime import datetime

from app.league.models import AppSettings
from app.player.models import PlayerElo
from sqlmodel import Session, select

# Default values
DEFAULT_K_FACTOR = 32
DEFAULT_NEW_PLAYER_K = 50
DEFAULT_NEW_PLAYER_GAMES = 5


def get_setting(session: Session, key: str, default: str = "") -> str:
    """Get a setting value from AppSettings."""
    statement = select(AppSettings).where(AppSettings.key == key)
    setting = session.scalars(statement).first()
    return setting.value if setting else default


def set_setting(session: Session, key: str, value: str) -> AppSettings:
    """Set a setting value in AppSettings."""
    statement = select(AppSettings).where(AppSettings.key == key)
    setting = session.scalars(statement).first()

    if setting:
        setting.value = value
        setting.updated_at = datetime.utcnow()
    else:
        setting = AppSettings(key=key, value=value)

    session.add(setting)
    session.commit()
    session.refresh(setting)
    return setting


def get_global_k_factor(session: Session) -> int:
    """Get global K-factor from settings."""
    value = get_setting(session, "elo_k_factor", str(DEFAULT_K_FACTOR))
    return int(value)


def get_new_player_k_factor(session: Session) -> int:
    """Get K-factor for new players."""
    value = get_setting(session, "elo_new_player_k", str(DEFAULT_NEW_PLAYER_K))
    return int(value)


def get_new_player_games_threshold(session: Session) -> int:
    """Get number of games before player uses global K."""
    value = get_setting(session, "elo_new_player_games", str(DEFAULT_NEW_PLAYER_GAMES))
    return int(value)


def get_k_factor(session: Session, player: PlayerElo) -> int:
    """
    Get K-factor for a player.

    New players use higher K for first N games.
    """
    threshold = get_new_player_games_threshold(session)

    if player.k_factor_games < threshold:
        return get_new_player_k_factor(session)

    return get_global_k_factor(session)


def calculate_expected_score(player_elo: int, opponent_elo: int) -> float:
    """Calculate expected score for player (0.0 - 1.0)."""
    return 1 / (1 + 10 ** ((opponent_elo - player_elo) / 400))


def calculate_elo_change(
    player_elo: int, opponent_elo: int, result: float, k_factor: int
) -> int:
    """
    Calculate ELO change.

    Args:
        player_elo: Current player ELO
        opponent_elo: Opponent ELO
        result: 1.0 = win, 0.5 = draw, 0.0 = loss
        k_factor: K coefficient

    Returns:
        ELO change (can be negative)
    """
    expected = calculate_expected_score(player_elo, opponent_elo)
    return round(k_factor * (result - expected))


def get_or_create_player_elo(session: Session, user_id: int) -> PlayerElo:
    """Get or create ELO record for a player."""
    statement = select(PlayerElo).where(PlayerElo.user_id == user_id)
    player_elo = session.scalars(statement).first()

    if not player_elo:
        player_elo = PlayerElo(
            user_id=user_id, elo=1000, games_played=0, k_factor_games=0
        )
        session.add(player_elo)
        session.commit()
        session.refresh(player_elo)

    return player_elo


def update_elo_after_match(
    session: Session,
    player1_user_id: int,
    player2_user_id: int,
    player1_score: int,
    player2_score: int,
) -> tuple[int, int]:
    """
    Update ELO for both players after a match.

    Returns:
        Tuple (player1 ELO change, player2 ELO change)
    """
    player1_elo = get_or_create_player_elo(session, player1_user_id)
    player2_elo = get_or_create_player_elo(session, player2_user_id)

    if player1_score > player2_score:
        result1, result2 = 1.0, 0.0
    elif player1_score < player2_score:
        result1, result2 = 0.0, 1.0
    else:
        result1, result2 = 0.5, 0.5

    k1 = get_k_factor(session, player1_elo)
    k2 = get_k_factor(session, player2_elo)

    change1 = calculate_elo_change(player1_elo.elo, player2_elo.elo, result1, k1)
    change2 = calculate_elo_change(player2_elo.elo, player1_elo.elo, result2, k2)

    player1_elo.elo += change1
    player1_elo.games_played += 1
    player1_elo.k_factor_games += 1
    player1_elo.updated_at = datetime.utcnow()

    player2_elo.elo += change2
    player2_elo.games_played += 1
    player2_elo.k_factor_games += 1
    player2_elo.updated_at = datetime.utcnow()

    session.add(player1_elo)
    session.add(player2_elo)
    session.commit()

    return change1, change2
