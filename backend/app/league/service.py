"""Business logic for the league module."""

import math
import random
from datetime import datetime, timedelta
from typing import Optional

from app.league.elo import get_or_create_player_elo, update_elo_after_match
from app.league.models import (
    ArmyMatchupStats,
    ArmyStats,
    Group,
    League,
    LeaguePlayer,
    Match,
    PlayerElo,
    Vote,
    VoteCategory,
)
from app.league.scoring import calculate_match_points
from sqlmodel import Session, select


def recalculate_all_army_stats(session: Session) -> dict:
    """Recalculates all army stats from confirmed matches. Run once to populate cache."""
    # Clear existing stats
    session.query(ArmyStats).delete()
    session.query(ArmyMatchupStats).delete()

    # Get all confirmed matches
    matches = session.scalars(select(Match).where(Match.status == "confirmed")).all()

    stats_count = 0
    matchup_count = 0

    for match in matches:
        # Get players
        player1 = session.scalars(
            select(LeaguePlayer).where(LeaguePlayer.id == match.player1_id)
        ).first()
        player2 = session.scalars(
            select(LeaguePlayer).where(LeaguePlayer.id == match.player2_id)
        ).first()

        if not player1 or not player2:
            continue

        # Get factions
        if match.phase == "knockout":
            p1_faction = player1.knockout_army_faction
            p2_faction = player2.knockout_army_faction
        else:
            p1_faction = player1.group_army_faction
            p2_faction = player2.group_army_faction

        if not p1_faction and not p2_faction:
            continue

        # Determine results
        if match.player1_score > match.player2_score:
            p1_result, p2_result = "win", "loss"
        elif match.player1_score < match.player2_score:
            p1_result, p2_result = "loss", "win"
        else:
            p1_result, p2_result = "draw", "draw"

        is_mirror = p1_faction and p2_faction and p1_faction == p2_faction

        # Update global stats
        for faction, result in [(p1_faction, p1_result), (p2_faction, p2_result)]:
            if not faction:
                continue

            stats = session.scalars(
                select(ArmyStats).where(ArmyStats.faction == faction)
            ).first()

            if not stats:
                stats = ArmyStats(faction=faction)
                session.add(stats)
                stats_count += 1

            stats.games_played += 1
            if result == "win":
                stats.wins += 1
            elif result == "draw":
                stats.draws += 1
            else:
                stats.losses += 1
            stats.updated_at = datetime.utcnow()

        # Update matchup stats (skip mirrors)
        if not is_mirror and p1_faction and p2_faction:
            # p1 vs p2
            matchup1 = session.scalars(
                select(ArmyMatchupStats).where(
                    ArmyMatchupStats.faction == p1_faction,
                    ArmyMatchupStats.opponent_faction == p2_faction,
                )
            ).first()

            if not matchup1:
                matchup1 = ArmyMatchupStats(
                    faction=p1_faction, opponent_faction=p2_faction
                )
                session.add(matchup1)
                matchup_count += 1

            matchup1.games_played += 1
            if p1_result == "win":
                matchup1.wins += 1
            elif p1_result == "draw":
                matchup1.draws += 1
            else:
                matchup1.losses += 1
            matchup1.updated_at = datetime.utcnow()

            # p2 vs p1
            matchup2 = session.scalars(
                select(ArmyMatchupStats).where(
                    ArmyMatchupStats.faction == p2_faction,
                    ArmyMatchupStats.opponent_faction == p1_faction,
                )
            ).first()

            if not matchup2:
                matchup2 = ArmyMatchupStats(
                    faction=p2_faction, opponent_faction=p1_faction
                )
                session.add(matchup2)
                matchup_count += 1

            matchup2.games_played += 1
            if p2_result == "win":
                matchup2.wins += 1
            elif p2_result == "draw":
                matchup2.draws += 1
            else:
                matchup2.losses += 1
            matchup2.updated_at = datetime.utcnow()

    session.commit()

    return {
        "matches_processed": len(matches),
        "factions_tracked": stats_count,
        "matchups_tracked": matchup_count,
    }


def update_army_stats_after_match(
    session: Session,
    player1: LeaguePlayer,
    player2: LeaguePlayer,
    player1_score: int,
    player2_score: int,
    phase: str,
) -> None:
    """Updates cached army statistics after a match is confirmed."""
    # Determine factions based on match phase
    p1_faction = (
        player1.knockout_army_faction
        if phase == "knockout"
        else player1.group_army_faction
    )
    p2_faction = (
        player2.knockout_army_faction
        if phase == "knockout"
        else player2.group_army_faction
    )

    # Skip if no factions set
    if not p1_faction and not p2_faction:
        return

    # Check if mirror match
    is_mirror = p1_faction and p2_faction and p1_faction == p2_faction

    # Determine results
    if player1_score > player2_score:
        p1_result, p2_result = "win", "loss"
    elif player1_score < player2_score:
        p1_result, p2_result = "loss", "win"
    else:
        p1_result, p2_result = "draw", "draw"

    # Update global stats for each faction (including mirrors)
    for faction, result in [(p1_faction, p1_result), (p2_faction, p2_result)]:
        if not faction:
            continue

        stats = session.scalars(
            select(ArmyStats).where(ArmyStats.faction == faction)
        ).first()

        if not stats:
            stats = ArmyStats(faction=faction)
            session.add(stats)

        stats.games_played += 1
        if result == "win":
            stats.wins += 1
        elif result == "draw":
            stats.draws += 1
        else:
            stats.losses += 1
        stats.updated_at = datetime.utcnow()

    # Update matchup stats (skip mirrors)
    if not is_mirror and p1_faction and p2_faction:
        # Update p1 faction vs p2 faction
        matchup1 = session.scalars(
            select(ArmyMatchupStats).where(
                ArmyMatchupStats.faction == p1_faction,
                ArmyMatchupStats.opponent_faction == p2_faction,
            )
        ).first()

        if not matchup1:
            matchup1 = ArmyMatchupStats(faction=p1_faction, opponent_faction=p2_faction)
            session.add(matchup1)

        matchup1.games_played += 1
        if p1_result == "win":
            matchup1.wins += 1
        elif p1_result == "draw":
            matchup1.draws += 1
        else:
            matchup1.losses += 1
        matchup1.updated_at = datetime.utcnow()

        # Update p2 faction vs p1 faction
        matchup2 = session.scalars(
            select(ArmyMatchupStats).where(
                ArmyMatchupStats.faction == p2_faction,
                ArmyMatchupStats.opponent_faction == p1_faction,
            )
        ).first()

        if not matchup2:
            matchup2 = ArmyMatchupStats(faction=p2_faction, opponent_faction=p1_faction)
            session.add(matchup2)

        matchup2.games_played += 1
        if p2_result == "win":
            matchup2.wins += 1
        elif p2_result == "draw":
            matchup2.draws += 1
        else:
            matchup2.losses += 1
        matchup2.updated_at = datetime.utcnow()


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
    """Submits a match result and updates player statistics immediately."""
    statement = select(League).where(League.id == match.league_id)
    league = session.scalars(statement).first()

    statement = select(LeaguePlayer).where(LeaguePlayer.id == match.player1_id)
    player1 = session.scalars(statement).first()

    statement = select(LeaguePlayer).where(LeaguePlayer.id == match.player2_id)
    player2 = session.scalars(statement).first()

    # If match already had scores, reverse the previous stats first
    if match.player1_league_points is not None and player1 and player2:
        player1.games_played -= 1
        player1.total_points -= match.player1_league_points
        player2.games_played -= 1
        player2.total_points -= match.player2_league_points

        # Reverse win/draw/loss
        if match.player1_score > match.player2_score:
            player1.games_won -= 1
            player2.games_lost -= 1
        elif match.player1_score < match.player2_score:
            player1.games_lost -= 1
            player2.games_won -= 1
        else:
            player1.games_drawn -= 1
            player2.games_drawn -= 1

    # Set new scores
    match.player1_score = player1_score
    match.player2_score = player2_score
    match.submitted_by_id = submitted_by_id
    match.submitted_at = datetime.utcnow()
    match.status = "pending_confirmation"

    if map_name:
        match.map_name = map_name

    # Calculate and apply new stats
    if player1 and player2 and league:
        p1_points = calculate_match_points(
            player1_score,
            player2_score,
            league.points_per_win,
            league.points_per_draw,
            league.points_per_loss,
        )
        p2_points = calculate_match_points(
            player2_score,
            player1_score,
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

        if player1_score > player2_score:
            player1.games_won += 1
            player2.games_lost += 1
        elif player1_score < player2_score:
            player1.games_lost += 1
            player2.games_won += 1
        else:
            player1.games_drawn += 1
            player2.games_drawn += 1

        session.add(player1)
        session.add(player2)

    session.add(match)
    session.commit()
    session.refresh(match)
    return match


def confirm_match_result(
    session: Session,
    match: Match,
    confirmed_by_id: int,
) -> Match:
    """Confirms a match result (locks it from further edits) and updates ELO."""
    match.confirmed_by_id = confirmed_by_id
    match.confirmed_at = datetime.utcnow()
    match.status = "confirmed"

    # Update ELO only on confirmation
    statement = select(LeaguePlayer).where(LeaguePlayer.id == match.player1_id)
    player1 = session.scalars(statement).first()

    statement = select(LeaguePlayer).where(LeaguePlayer.id == match.player2_id)
    player2 = session.scalars(statement).first()

    if player1 and player2 and player1.user_id and player2.user_id:
        # Get ELO before update
        p1_elo = get_or_create_player_elo(session, player1.user_id)
        p2_elo = get_or_create_player_elo(session, player2.user_id)
        match.player1_elo_before = p1_elo.elo
        match.player2_elo_before = p2_elo.elo

        update_elo_after_match(
            session,
            player1.user_id,
            player2.user_id,
            match.player1_score,
            match.player2_score,
        )

        # Get ELO after update
        session.refresh(p1_elo)
        session.refresh(p2_elo)
        match.player1_elo_after = p1_elo.elo
        match.player2_elo_after = p2_elo.elo

    # Set knockout placement for loser (and winner if final)
    if match.phase == "knockout" and player1 and player2:
        # Determine winner and loser
        if match.player1_score > match.player2_score:
            winner, loser = player1, player2
        else:
            winner, loser = player2, player1

        # Map knockout round to placement
        placement_map = {
            "final": "2",
            "semi": "top_4",
            "quarter": "top_8",
            "round_of_16": "top_16",
            "round_of_32": "top_32",
        }
        loser_placement = placement_map.get(match.knockout_round, "top_32")
        loser.knockout_placement = loser_placement
        session.add(loser)

        # If final, also set winner placement
        if match.knockout_round == "final":
            winner.knockout_placement = "1"
            session.add(winner)

    # Update army statistics
    if player1 and player2:
        update_army_stats_after_match(
            session,
            player1,
            player2,
            match.player1_score,
            match.player2_score,
            match.phase,
        )

    session.add(match)
    session.commit()
    session.refresh(match)
    return match


# ============ Standings ============


def get_group_standings(session: Session, group_id: int) -> list[LeaguePlayer]:
    """
    Gets group standings sorted by points with minimum games requirement.

    In a group of N players, each player can play max N-1 games.
    Minimum required games = max_games - 1 (you can skip one match).
    E.g. in 4-player group: max=3, min required=2

    Sorting:
    1. Players who met minimum games requirement ranked above those who didn't
    2. Total points (descending)
    3. Games played (descending - more games played = better tiebreaker)
    4. Average points (descending)
    """
    statement = select(LeaguePlayer).where(LeaguePlayer.group_id == group_id)
    players = list(session.scalars(statement).all())

    group_size = len(players)
    max_games = group_size - 1  # In 4-player group, max 3 games
    min_required_games = max(
        1, max_games - 1
    )  # Can skip 1 match, so min = 2 for 4-player group

    def sorting_key(player):
        meets_minimum = player.games_played >= min_required_games
        return (
            not meets_minimum,  # Those who meet minimum first
            -player.total_points,
            -player.games_played,  # More games = better (descending)
            -player.average_points,
        )

    players.sort(key=sorting_key)

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

    Takes top X players from each group + best runners-up if needed.

    Examples:
    - 2 groups, top 4: 2 per group (evenly divides)
    - 3 groups, top 4: 1st places (3) + best 2nd place (1)
    - 5 groups, top 8: 1st places (5) + 3 best 2nd places
    - 6 groups, top 8: 1st places (6) + 2 best 2nd places

    Returns:
        List of qualified players sorted by results (best first for seeding)
    """
    # Get groups
    groups = session.scalars(select(Group).where(Group.league_id == league.id)).all()
    num_groups = len(groups)

    if num_groups == 0:
        return []

    # Calculate knockout size
    player_count = get_league_player_count(session, league.id)
    knockout_size = league.knockout_size
    if knockout_size is None:
        knockout_size = calculate_knockout_size(player_count)
    knockout_size = min(knockout_size, player_count)

    # Calculate guaranteed spots per group and extra spots for best runners-up
    guaranteed_per_group = knockout_size // num_groups
    extra_spots = knockout_size % num_groups

    if guaranteed_per_group == 0:
        # Edge case: more groups than knockout spots - just take best players globally
        guaranteed_per_group = 0
        extra_spots = knockout_size

    qualified = []
    runners_up = []

    for group in groups:
        group_players = get_group_standings(session, group.id)

        # Take guaranteed qualifiers from each group
        qualified.extend(group_players[:guaranteed_per_group])

        # Collect potential runners-up (next position after guaranteed spots)
        if extra_spots > 0 and len(group_players) > guaranteed_per_group:
            runners_up.append(group_players[guaranteed_per_group])

    # Sort runners-up by points and take the best ones
    if extra_spots > 0 and runners_up:
        runners_up.sort(
            key=lambda p: (-p.total_points, p.games_played, -p.average_points)
        )
        qualified.extend(runners_up[:extra_spots])

    # Sort all qualified players for seeding (best first)
    qualified.sort(key=lambda p: (-p.total_points, p.games_played, -p.average_points))

    return qualified


def get_knockout_round_names(knockout_size: int) -> list[str]:
    """Returns the list of knockout round names for a given bracket size."""
    round_names = {
        2: ["final"],
        4: ["semi", "final"],
        8: ["quarter", "semi", "final"],
        16: ["round_of_16", "quarter", "semi", "final"],
        32: ["round_of_32", "round_of_16", "quarter", "semi", "final"],
    }
    return round_names.get(knockout_size, ["final"])


def get_next_knockout_round(current_round: str) -> Optional[str]:
    """Returns the next knockout round, or None if current is final."""
    round_progression = {
        "round_of_32": "round_of_16",
        "round_of_16": "quarter",
        "quarter": "semi",
        "semi": "final",
        "final": None,
    }
    return round_progression.get(current_round)


def generate_knockout_matches(
    session: Session,
    league: League,
    weeks_per_match: int = 2,
) -> list[Match]:
    """
    Generates knockout phase matches for the FIRST ROUND only.

    Best plays worst, second plays second-to-last, etc.
    Uses league.knockout_size to determine the bracket size.
    """
    qualified = get_qualified_players(session, league)
    knockout_size = len(qualified)

    if knockout_size not in [2, 4, 8, 16, 32]:
        player_count = get_league_player_count(session, league.id)
        knockout_size = calculate_knockout_size(player_count, league.knockout_size)
        qualified = qualified[:knockout_size]

    rounds = get_knockout_round_names(knockout_size)
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
            deadline=base_deadline + timedelta(days=league.days_per_match),
        )
        session.add(match)
        created_matches.append(match)

    session.commit()
    return created_matches


def get_round_matches(
    session: Session, league_id: int, knockout_round: str
) -> list[Match]:
    """Gets all matches for a specific knockout round."""
    statement = select(Match).where(
        Match.league_id == league_id,
        Match.phase == "knockout",
        Match.knockout_round == knockout_round,
    )
    return list(session.scalars(statement).all())


def all_round_matches_confirmed(
    session: Session, league_id: int, knockout_round: str
) -> bool:
    """Checks if all matches in a knockout round are confirmed."""
    matches = get_round_matches(session, league_id, knockout_round)
    if not matches:
        return False
    return all(m.status == "confirmed" for m in matches)


def get_round_winners(
    session: Session, league_id: int, knockout_round: str
) -> list[int]:
    """
    Gets winner player IDs from a completed knockout round.
    Returns list of player IDs in seeding order (best seed first).
    """
    matches = get_round_matches(session, league_id, knockout_round)
    winners = []

    # Sort matches by their position (first match = top seeds, etc.)
    matches_sorted = sorted(matches, key=lambda m: m.id)

    for match in matches_sorted:
        if match.winner_id:
            winners.append(match.winner_id)

    return winners


def advance_to_next_knockout_round(
    session: Session,
    league: League,
) -> tuple[Optional[str], list[Match]]:
    """
    Advances the knockout to the next round.

    Returns:
        (new_round_name, created_matches) or (None, []) if already at final
    """
    current_round = league.current_knockout_round
    if not current_round:
        return (None, [])

    # Check all current round matches are confirmed
    if not all_round_matches_confirmed(session, league.id, current_round):
        return (None, [])

    next_round = get_next_knockout_round(current_round)
    if not next_round:
        # Already at final, finish league
        return (None, [])

    # Get winners from current round
    winners = get_round_winners(session, league.id, current_round)

    if len(winners) < 2:
        return (None, [])

    # Create matches for next round
    # Pair 1st with last, 2nd with second-to-last, etc. (bracket style)
    created_matches = []
    base_deadline = datetime.utcnow()
    half = len(winners) // 2

    for i in range(half):
        player1_id = winners[i]
        player2_id = winners[len(winners) - 1 - i]

        match = Match(
            league_id=league.id,
            player1_id=player1_id,
            player2_id=player2_id,
            phase="knockout",
            knockout_round=next_round,
            status="scheduled",
            deadline=base_deadline + timedelta(days=league.days_per_match),
        )
        session.add(match)
        created_matches.append(match)

    league.current_knockout_round = next_round
    session.add(league)
    session.commit()

    return (next_round, created_matches)


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


def remove_player_from_league(
    session: Session,
    player: LeaguePlayer,
    award_walkovers: bool = True,
) -> dict:
    """
    Removes a player from a league, handling their matches.

    For unplayed/pending matches: awards walkover (25:0, 1175 pts) to opponent
    For confirmed matches: keeps them (stats already counted)

    Walkover score is 25:0 with 1175 league points (max win + bonus).

    Args:
        session: Database session
        player: LeaguePlayer to remove
        award_walkovers: If True, unplayed matches become walkovers for opponent

    Returns:
        dict with counts of deleted/modified matches
    """
    # Walkover constants
    WALKOVER_WINNER_SCORE = 25
    WALKOVER_LOSER_SCORE = 0
    WALKOVER_WINNER_POINTS = 1075
    WALKOVER_LOSER_POINTS = 0

    statement = select(Match).where(
        Match.league_id == player.league_id,
        (Match.player1_id == player.id) | (Match.player2_id == player.id),
    )
    matches = list(session.scalars(statement).all())

    deleted_count = 0
    walkover_count = 0

    for match in matches:
        if match.status == "confirmed":
            # Keep confirmed matches - stats already counted
            continue

        if award_walkovers and match.status in ("scheduled", "pending_confirmation"):
            # Award walkover to opponent
            opponent_id = (
                match.player2_id if match.player1_id == player.id else match.player1_id
            )
            opponent = session.get(LeaguePlayer, opponent_id)

            if opponent:
                # Reverse any previous pending stats from this match
                if match.player1_league_points is not None:
                    other_points = (
                        match.player2_league_points
                        if match.player1_id == player.id
                        else match.player1_league_points
                    )
                    opponent.games_played -= 1
                    opponent.total_points -= other_points or 0
                    # Reverse win/loss/draw
                    if match.player1_score > match.player2_score:
                        if match.player1_id == player.id:
                            opponent.games_lost -= 1
                        else:
                            opponent.games_won -= 1
                    elif match.player1_score < match.player2_score:
                        if match.player1_id == player.id:
                            opponent.games_won -= 1
                        else:
                            opponent.games_lost -= 1
                    else:
                        opponent.games_drawn -= 1

                # Set walkover score (25:0, 1175 pts)
                if match.player1_id == player.id:
                    match.player1_score = WALKOVER_LOSER_SCORE
                    match.player2_score = WALKOVER_WINNER_SCORE
                    match.player1_league_points = WALKOVER_LOSER_POINTS
                    match.player2_league_points = WALKOVER_WINNER_POINTS
                else:
                    match.player1_score = WALKOVER_WINNER_SCORE
                    match.player2_score = WALKOVER_LOSER_SCORE
                    match.player1_league_points = WALKOVER_WINNER_POINTS
                    match.player2_league_points = WALKOVER_LOSER_POINTS

                # Update opponent stats with walkover win
                opponent.games_played += 1
                opponent.games_won += 1
                opponent.total_points += WALKOVER_WINNER_POINTS
                session.add(opponent)

                match.status = "confirmed"
                match.confirmed_at = datetime.utcnow()
                session.add(match)
                walkover_count += 1
                continue

        # Delete match if no walkover
        session.delete(match)
        deleted_count += 1

    # Remove player
    session.delete(player)
    session.commit()

    return {"deleted_matches": deleted_count, "walkover_matches": walkover_count}


def change_player_group(
    session: Session,
    player: LeaguePlayer,
    new_group: Group,
    regenerate_matches: bool = True,
) -> dict:
    """
    Moves a player from one group to another.

    Deletes old group matches and creates new ones if regenerate_matches=True.

    Args:
        session: Database session
        player: LeaguePlayer to move
        new_group: Target Group
        regenerate_matches: If True, regenerates matches for affected groups

    Returns:
        dict with counts of deleted/created matches
    """
    old_group_id = player.group_id
    league = session.get(League, player.league_id)

    if not league or old_group_id == new_group.id:
        return {"deleted_matches": 0, "created_matches": 0}

    deleted_count = 0
    created_count = 0

    if regenerate_matches:
        # Delete player's existing group matches (only unconfirmed ones)
        statement = select(Match).where(
            Match.league_id == player.league_id,
            Match.phase == "group",
            (Match.player1_id == player.id) | (Match.player2_id == player.id),
        )
        old_matches = list(session.scalars(statement).all())

        for match in old_matches:
            if match.status != "confirmed":
                # Reverse stats if match had pending results
                if match.player1_league_points is not None:
                    other_player_id = (
                        match.player2_id
                        if match.player1_id == player.id
                        else match.player1_id
                    )
                    other_player = session.get(LeaguePlayer, other_player_id)
                    if other_player:
                        other_points = (
                            match.player2_league_points
                            if match.player1_id == player.id
                            else match.player1_league_points
                        )
                        other_player.games_played -= 1
                        other_player.total_points -= other_points or 0
                        # Reverse win/loss/draw
                        if match.player1_score > match.player2_score:
                            if match.player1_id == player.id:
                                other_player.games_lost -= 1
                            else:
                                other_player.games_won -= 1
                        elif match.player1_score < match.player2_score:
                            if match.player1_id == player.id:
                                other_player.games_won -= 1
                            else:
                                other_player.games_lost -= 1
                        else:
                            other_player.games_drawn -= 1
                        session.add(other_player)

                session.delete(match)
                deleted_count += 1

    # Move player to new group
    player.group_id = new_group.id
    session.add(player)
    session.commit()

    if regenerate_matches:
        # Create new matches with players in the new group
        statement = select(LeaguePlayer).where(
            LeaguePlayer.group_id == new_group.id,
            LeaguePlayer.id != player.id,
        )
        new_groupmates = list(session.scalars(statement).all())

        base_deadline = datetime.utcnow()
        for groupmate in new_groupmates:
            match = Match(
                league_id=player.league_id,
                player1_id=player.id,
                player2_id=groupmate.id,
                phase="group",
                status="scheduled",
                deadline=base_deadline + timedelta(days=league.days_per_match),
            )
            session.add(match)
            created_count += 1

        session.commit()

    return {"deleted_matches": deleted_count, "created_matches": created_count}


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


# ============ Voting Operations ============


def enable_voting_for_league(
    session: Session,
    league: League,
    create_default_category: bool = True,
) -> Optional[VoteCategory]:
    """
    Enables voting for a league and optionally creates the default category.

    Args:
        session: Database session
        league: League to enable voting for
        create_default_category: If True, creates "Best Sport" category

    Returns:
        Created VoteCategory if create_default_category is True, else None
    """
    league.voting_enabled = True
    session.add(league)

    category = None
    if create_default_category:
        category = VoteCategory(
            league_id=league.id,
            name="best_sport",
            description=None,
        )
        session.add(category)

    session.commit()

    if category:
        session.refresh(category)

    return category


def create_vote_category(
    session: Session,
    league_id: int,
    name: str,
    description: Optional[str] = None,
) -> VoteCategory:
    """
    Creates a new vote category for a league.

    Args:
        session: Database session
        league_id: ID of the league
        name: Category name
        description: Optional description

    Returns:
        Created VoteCategory
    """
    category = VoteCategory(
        league_id=league_id,
        name=name,
        description=description,
    )
    session.add(category)
    session.commit()
    session.refresh(category)
    return category


def get_voting_results(
    session: Session,
    category_id: int,
) -> dict:
    """
    Gets voting results for a category.

    Args:
        session: Database session
        category_id: ID of the vote category

    Returns:
        Dict with results list, winner_id, is_tied, total_votes
    """
    votes = session.scalars(select(Vote).where(Vote.category_id == category_id)).all()

    if not votes:
        return {
            "results": [],
            "winner_id": None,
            "is_tied": False,
            "total_votes": 0,
        }

    # Count votes per player
    vote_counts: dict[int, int] = {}
    for vote in votes:
        vote_counts[vote.voted_for_id] = vote_counts.get(vote.voted_for_id, 0) + 1

    # Sort by count descending
    sorted_results = sorted(vote_counts.items(), key=lambda x: -x[1])

    # Check for tie at the top
    is_tied = False
    winner_id = None
    if len(sorted_results) >= 2:
        if sorted_results[0][1] == sorted_results[1][1]:
            is_tied = True
        else:
            winner_id = sorted_results[0][0]
    elif len(sorted_results) == 1:
        winner_id = sorted_results[0][0]

    results = [
        {"player_id": player_id, "vote_count": count}
        for player_id, count in sorted_results
    ]

    return {
        "results": results,
        "winner_id": winner_id,
        "is_tied": is_tied,
        "total_votes": len(votes),
    }


def close_voting(session: Session, league: League) -> dict:
    """
    Closes voting for a league and determines winners.

    Args:
        session: Database session
        league: League to close voting for

    Returns:
        Dict with categories and their winners/ties
    """
    league.voting_closed_at = datetime.utcnow()
    session.add(league)

    # Get all categories for this league
    categories = session.scalars(
        select(VoteCategory).where(VoteCategory.league_id == league.id)
    ).all()

    category_results = []
    for category in categories:
        results = get_voting_results(session, category.id)

        # Auto-set winner if no tie
        if not results["is_tied"] and results["winner_id"]:
            category.winner_id = results["winner_id"]
            session.add(category)

        category_results.append(
            {
                "category_id": category.id,
                "category_name": category.name,
                "winner_id": category.winner_id,
                "is_tied": results["is_tied"],
                "total_votes": results["total_votes"],
            }
        )

    session.commit()

    return {"categories": category_results}


def break_tie_random(
    session: Session,
    category: VoteCategory,
    tied_player_ids: list[int],
) -> int:
    """
    Randomly breaks a tie between players.

    Args:
        session: Database session
        category: VoteCategory to set winner for
        tied_player_ids: List of player IDs that are tied

    Returns:
        Winner player ID
    """
    winner_id = random.choice(tied_player_ids)
    category.winner_id = winner_id
    session.add(category)
    session.commit()
    return winner_id


def cast_vote(
    session: Session,
    category_id: int,
    voter_id: int,
    voted_for_id: int,
) -> Vote:
    """
    Casts a vote in a category.

    Args:
        session: Database session
        category_id: ID of the vote category
        voter_id: ID of the voter (league_player.id)
        voted_for_id: ID of the player being voted for (league_player.id)

    Returns:
        Created Vote
    """
    vote = Vote(
        category_id=category_id,
        voter_id=voter_id,
        voted_for_id=voted_for_id,
    )
    session.add(vote)
    session.commit()
    session.refresh(vote)
    return vote


def get_player_vote(
    session: Session,
    category_id: int,
    voter_id: int,
) -> Optional[Vote]:
    """
    Gets a player's vote in a category if it exists.

    Args:
        session: Database session
        category_id: ID of the vote category
        voter_id: ID of the voter (league_player.id)

    Returns:
        Vote if exists, None otherwise
    """
    return session.scalars(
        select(Vote).where(
            Vote.category_id == category_id,
            Vote.voter_id == voter_id,
        )
    ).first()
