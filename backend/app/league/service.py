"""Business logic for the league module."""

import math
import random
from datetime import datetime, timedelta
from typing import Optional

from app.league.elo import update_elo_after_match
from app.league.models import Group, League, LeaguePlayer, Match, PlayerElo
from app.league.scoring import calculate_match_points
from sqlmodel import Session, select

# ============ League Operations ============


def get_league_player_count(session: Session, league_id: int) -> int:
    """Gets the number of players in a league."""
    statement = select(LeaguePlayer).where(LeaguePlayer.league_id == league_id)
    return len(session.scalars(statement).all())


def round_up_to_hour(dt: datetime) -> datetime:
    """Round datetime up to the next complete hour."""
    if dt.minute == 0 and dt.second == 0 and dt.microsecond == 0:
        return dt
    return dt.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)


def get_qualifying_info(session: Session, league: League) -> tuple[int, int]:
    """
    Calculate qualifying spots for knockout phase.

    Returns:
        (spots_per_group, total_spots)
    """
    if not league.has_knockout_phase:
        return (0, 0)

    # Get groups
    groups = session.scalars(select(Group).where(Group.league_id == league.id)).all()

    if not groups:
        return (0, 0)

    num_groups = len(groups)
    player_count = get_league_player_count(session, league.id)

    # Calculate knockout size
    knockout_size = league.knockout_size
    if knockout_size is None:
        knockout_size = calculate_knockout_size(player_count)

    # Ensure knockout_size doesn't exceed player count
    knockout_size = min(knockout_size, player_count)

    # Calculate spots per group (evenly distributed)
    spots_per_group = knockout_size // num_groups

    return (spots_per_group, knockout_size)


def calculate_group_phase_rounds(session: Session, league: League) -> int:
    """
    Calculate the number of rounds needed for group phase (round-robin).
    This equals (max_group_size - 1) rounds.
    """
    groups = session.scalars(select(Group).where(Group.league_id == league.id)).all()

    if not groups:
        return 0

    # Find largest group
    max_size = 0
    for group in groups:
        players_in_group = session.scalars(
            select(LeaguePlayer).where(LeaguePlayer.group_id == group.id)
        ).all()
        max_size = max(max_size, len(players_in_group))

    # Round-robin needs (n-1) rounds for n players
    return max_size - 1 if max_size > 1 else 0


def calculate_knockout_rounds(knockout_size: int) -> int:
    """Calculate number of knockout rounds (log2 of size)."""
    if knockout_size <= 1:
        return 0
    return int(math.log2(knockout_size))


def calculate_phase_dates(
    session: Session, league: League, start_date: datetime
) -> tuple[datetime, datetime, datetime, datetime]:
    """
    Calculate phase start and end dates.

    Returns:
        (group_start, group_end, knockout_start, knockout_end)
    """
    group_rounds = calculate_group_phase_rounds(session, league)
    group_days = group_rounds * league.days_per_match

    group_start = round_up_to_hour(start_date)
    group_end = round_up_to_hour(group_start + timedelta(days=group_days))

    # Knockout phase
    if not league.has_knockout_phase:
        return (group_start, group_end, None, None)

    player_count = get_league_player_count(session, league.id)
    knockout_size = league.knockout_size or calculate_knockout_size(player_count)
    knockout_rounds = calculate_knockout_rounds(knockout_size)
    knockout_days = knockout_rounds * league.days_per_match

    knockout_start = group_end
    knockout_end = round_up_to_hour(knockout_start + timedelta(days=knockout_days))

    return (group_start, group_end, knockout_start, knockout_end)


def calculate_num_groups(
    player_count: int,
    min_group_size: int = 4,
    max_group_size: int = 6,
) -> int:
    """
    Calculates the optimal number of groups based on player count and constraints.
    Prefers smaller groups (more groups) within the allowed range.

    Algorithm:
    1. Minimum number of groups = ceil(player_count / max_group_size)
    2. Maximum number of groups = floor(player_count / min_group_size)
    3. Select the largest number of groups (smallest group sizes)

    Example:
    - 20 players, min=4, max=6: min_groups=4 (ceil(20/6)), max_groups=5 (20/4)
      -> 5 groups of 4 players each
    - 8 players, min=4, max=6: min_groups=2 (ceil(8/6)), max_groups=2 (8/4)
      -> 2 groups of 4 players each
    """
    import math

    if player_count < min_group_size:
        return 1

    min_groups = math.ceil(player_count / max_group_size)
    max_groups = player_count // min_group_size

    if min_groups > max_groups:
        return min_groups

    return max_groups


def get_knockout_constraints(player_count: int) -> tuple[int, int, int]:
    """
    Returns knockout size constraints based on player count.

    Returns:
        (default_size, min_size, max_size)

    Rules:
    - 4-7 players: always top 2 (final only)
    - 8-15 players: default top 4, max top 8
    - 16-47 players: default top 8, max top 16
    - 48+ players: default top 16, max top 32
    """
    if player_count < 8:
        return (2, 2, 2)
    elif player_count < 16:
        return (4, 2, 8)
    elif player_count < 48:
        return (8, 2, 16)
    else:
        return (16, 2, 32)


def get_allowed_knockout_sizes(player_count: int) -> list[int]:
    """
    Returns list of allowed knockout sizes for given player count.
    """
    _, _, max_size = get_knockout_constraints(player_count)
    all_sizes = [2, 4, 8, 16, 32]
    return [s for s in all_sizes if s <= max_size and s <= player_count]


def calculate_knockout_size(
    player_count: int, configured_size: Optional[int] = None
) -> int:
    """
    Calculates the knockout phase size.

    If configured_size is set, validates and uses it.
    Otherwise returns default based on player count.

    Rules:
    - 4-7 players: always top 2 (final only)
    - 8-15 players: default top 4, max top 8
    - 16-47 players: default top 8, max top 16
    - 48+ players: default top 16, max top 32
    """
    default_size, _, max_size = get_knockout_constraints(player_count)

    if configured_size is not None:
        # Validate configured size
        if configured_size <= player_count and configured_size <= max_size:
            return configured_size
        # Fall back to largest valid size
        allowed = get_allowed_knockout_sizes(player_count)
        return max(allowed) if allowed else default_size

    return default_size


# ============ Group Drawing ============


def draw_groups(
    session: Session,
    league: League,
    baskets: Optional[list[list[int]]] = None,
) -> list[Group]:
    """
    Draws groups for a league.

    Args:
        session: Database session
        league: League
        baskets: Optional baskets with player_id for seeded draw
                 If None - fully random draw

    Returns:
        List of created groups
    """
    statement = select(LeaguePlayer).where(LeaguePlayer.league_id == league.id)
    players = list(session.scalars(statement).all())

    num_groups = calculate_num_groups(
        len(players),
        league.min_group_size,
        league.max_group_size,
    )

    created_groups = []
    for i in range(num_groups):
        group = Group(
            league_id=league.id,
            name=f"Group {chr(65 + i)}",
        )
        session.add(group)
        created_groups.append(group)

    session.commit()

    for group in created_groups:
        session.refresh(group)

    if baskets:
        for basket in baskets:
            random.shuffle(basket)
            for i, player_id in enumerate(basket):
                group_index = i % num_groups
                statement = select(LeaguePlayer).where(LeaguePlayer.id == player_id)
                player = session.scalars(statement).first()
                if player:
                    player.group_id = created_groups[group_index].id
    else:
        random.shuffle(players)
        for i, player in enumerate(players):
            group_index = i % num_groups
            player.group_id = created_groups[group_index].id

    session.commit()

    return created_groups


def generate_group_matches(
    session: Session,
    league: League,
    weeks_per_match: int = 2,
) -> list[Match]:
    """
    Generates group phase matches (round-robin within each group).

    Args:
        session: Database session
        league: League
        weeks_per_match: Weeks per match (for deadline calculation)

    Returns:
        List of created matches
    """
    statement = select(Group).where(Group.league_id == league.id)
    groups = session.scalars(statement).all()

    created_matches = []
    base_deadline = datetime.utcnow()

    for group in groups:
        statement = select(LeaguePlayer).where(LeaguePlayer.group_id == group.id)
        players = list(session.scalars(statement).all())

        match_count = 0
        for i, player1 in enumerate(players):
            for player2 in players[i + 1 :]:
                deadline = base_deadline + timedelta(
                    weeks=weeks_per_match * (match_count // len(players) + 1)
                )

                match = Match(
                    league_id=league.id,
                    player1_id=player1.id,
                    player2_id=player2.id,
                    phase="group",
                    status="scheduled",
                    deadline=deadline,
                )
                session.add(match)
                created_matches.append(match)
                match_count += 1

    session.commit()
    return created_matches


# ============ Match Operations ============


def submit_match_result(
    session: Session,
    match: Match,
    player1_score: int,
    player2_score: int,
    submitted_by_id: int,
    map_name: Optional[str] = None,
) -> Match:
    """Submits a match result."""
    match.player1_score = player1_score
    match.player2_score = player2_score
    match.submitted_by_id = submitted_by_id
    match.submitted_at = datetime.utcnow()
    match.status = "pending_confirmation"

    if map_name:
        match.map_name = map_name

    session.add(match)
    session.commit()
    session.refresh(match)
    return match


def confirm_match_result(
    session: Session,
    match: Match,
    confirmed_by_id: int,
) -> Match:
    """Confirms a match result and updates statistics."""
    match.confirmed_by_id = confirmed_by_id
    match.confirmed_at = datetime.utcnow()
    match.status = "confirmed"

    statement = select(League).where(League.id == match.league_id)
    league = session.scalars(statement).first()

    statement = select(LeaguePlayer).where(LeaguePlayer.id == match.player1_id)
    player1 = session.scalars(statement).first()

    statement = select(LeaguePlayer).where(LeaguePlayer.id == match.player2_id)
    player2 = session.scalars(statement).first()

    if player1 and player2 and league:
        p1_points = calculate_match_points(
            match.player1_score,
            match.player2_score,
            league.points_per_win,
            league.points_per_draw,
            league.points_per_loss,
        )
        p2_points = calculate_match_points(
            match.player2_score,
            match.player1_score,
            league.points_per_win,
            league.points_per_draw,
            league.points_per_loss,
        )

        match.player1_league_points = p1_points
        match.player2_league_points = p2_points

        player1.games_played += 1
        player1.total_points += p1_points
        player2.games_played += 1
        player2.total_points += p2_points

        if match.player1_score > match.player2_score:
            player1.games_won += 1
            player2.games_lost += 1
        elif match.player1_score < match.player2_score:
            player1.games_lost += 1
            player2.games_won += 1
        else:
            player1.games_drawn += 1
            player2.games_drawn += 1

        if player1.user_id and player2.user_id:
            update_elo_after_match(
                session,
                player1.user_id,
                player2.user_id,
                match.player1_score,
                match.player2_score,
            )

        session.add(player1)
        session.add(player2)

    session.add(match)
    session.commit()
    session.refresh(match)
    return match


# ============ Standings ============


def get_group_standings(session: Session, group_id: int) -> list[LeaguePlayer]:
    """
    Gets group standings sorted by points.

    Sorting:
    1. Total points (descending)
    2. Games played (ascending - fewer unplayed = better)
    3. Average points (descending)
    """
    statement = select(LeaguePlayer).where(LeaguePlayer.group_id == group_id)
    players = list(session.scalars(statement).all())

    players.sort(key=lambda p: (-p.total_points, p.games_played, -p.average_points))

    return players


# ============ Knockout Phase ============


def get_advancement_rules(player_count: int) -> tuple[int, int, int]:
    """
    Returns advancement rules based on player count.

    Returns:
        (num_groups, direct_qualifiers_per_group, best_runners_up)

    8-11: 2 groups, 1st+2nd places -> Top 4
    12-15: 3 groups, 1st places + best 2nd place -> Top 4
    16-19: 4 groups, 1st+2nd places -> Top 8
    20-23: 5 groups, 1st places + 3 best 2nd places -> Top 8
    24-27: 6 groups, 1st places + 2 best 2nd places -> Top 8
    28-31: 7 groups, 1st places + best 2nd place -> Top 8
    32-48: 8 groups, 1st+2nd places -> Top 16
    """
    if player_count <= 11:
        return (2, 2, 0)
    elif player_count <= 15:
        return (3, 1, 1)
    elif player_count <= 19:
        return (4, 2, 0)
    elif player_count <= 23:
        return (5, 1, 3)
    elif player_count <= 27:
        return (6, 1, 2)
    elif player_count <= 31:
        return (7, 1, 1)
    else:
        return (8, 2, 0)


def get_qualified_players(session: Session, league: League) -> list[LeaguePlayer]:
    """
    Gets players who qualified for the knockout phase.

    Uses league.knockout_size to determine the number of qualifiers.
    If knockout_size is not set, calculates automatically.

    Returns:
        List of players sorted by results (best first), trimmed to knockout_size
    """
    player_count = get_league_player_count(session, league.id)
    knockout_size = calculate_knockout_size(player_count, league.knockout_size)

    statement = select(LeaguePlayer).where(LeaguePlayer.league_id == league.id)
    all_players = list(session.scalars(statement).all())

    all_players.sort(key=lambda p: (-p.total_points, p.games_played, -p.average_points))

    return all_players[:knockout_size]


def generate_knockout_matches(
    session: Session,
    league: League,
    weeks_per_match: int = 2,
) -> list[Match]:
    """
    Generates knockout phase matches.

    Best plays worst, second plays second-to-last, etc.
    Uses league.knockout_size to determine the bracket size.
    """
    qualified = get_qualified_players(session, league)
    knockout_size = len(qualified)

    if knockout_size not in [2, 4, 8, 16, 32]:
        player_count = get_league_player_count(session, league.id)
        knockout_size = calculate_knockout_size(player_count, league.knockout_size)
        qualified = qualified[:knockout_size]

    round_names = {
        2: ["final"],
        4: ["semi", "final"],
        8: ["quarter", "semi", "final"],
        16: ["round_of_16", "quarter", "semi", "final"],
        32: ["round_of_32", "round_of_16", "quarter", "semi", "final"],
    }

    rounds = round_names[knockout_size]
    first_round = rounds[0]

    created_matches = []
    base_deadline = datetime.utcnow()

    half = knockout_size // 2
    for i in range(half):
        player1 = qualified[i]
        player2 = qualified[knockout_size - 1 - i]

        match = Match(
            league_id=league.id,
            player1_id=player1.id,
            player2_id=player2.id,
            phase="knockout",
            knockout_round=first_round,
            status="scheduled",
            deadline=base_deadline + timedelta(weeks=weeks_per_match),
        )
        session.add(match)
        created_matches.append(match)

    session.commit()
    return created_matches


def advance_knockout_winner(session: Session, match: Match) -> Optional[Match]:
    """
    Creates next round match for the winner.

    Returns:
        New match if created, None if it was the final
    """
    if not match.is_completed or match.phase != "knockout":
        return None

    winner_id = match.winner_id
    if not winner_id:
        return None

    round_progression = {
        "round_of_16": "quarter",
        "quarter": "semi",
        "semi": "final",
        "final": None,
    }

    next_round = round_progression.get(match.knockout_round)
    if not next_round:
        return None

    return None


# ============ Tiebreakers ============


def compare_for_knockout_tiebreaker(
    session: Session,
    player1: LeaguePlayer,
    player2: LeaguePlayer,
) -> int:
    """
    Compares players for knockout tiebreaker.

    Returns:
        -1 if player1 wins, 1 if player2, 0 if tie
    """
    statement = select(Match).where(
        Match.league_id == player1.league_id,
        Match.phase == "group",
    )
    all_group_matches = session.scalars(statement).all()

    p1_unplayed = sum(
        1
        for m in all_group_matches
        if (m.player1_id == player1.id or m.player2_id == player1.id)
        and m.status != "confirmed"
    )
    p2_unplayed = sum(
        1
        for m in all_group_matches
        if (m.player1_id == player2.id or m.player2_id == player2.id)
        and m.status != "confirmed"
    )

    if p1_unplayed != p2_unplayed:
        return -1 if p1_unplayed < p2_unplayed else 1

    if player1.average_points != player2.average_points:
        return -1 if player1.average_points > player2.average_points else 1

    if player1.user_id and player2.user_id:
        stmt1 = select(PlayerElo).where(PlayerElo.user_id == player1.user_id)
        stmt2 = select(PlayerElo).where(PlayerElo.user_id == player2.user_id)
        elo1 = session.scalars(stmt1).first()
        elo2 = session.scalars(stmt2).first()

        if elo1 and elo2 and elo1.elo != elo2.elo:
            return -1 if elo1.elo < elo2.elo else 1

    return 0
