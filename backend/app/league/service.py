"""Logika biznesowa modulu league."""

import random
from datetime import datetime, timedelta
from typing import Optional

from app.league.elo import update_elo_after_match
from app.league.models import Group, League, LeaguePlayer, Match, PlayerElo
from app.league.scoring import calculate_match_points
from sqlmodel import Session, select

# ============ League Operations ============


def get_league_player_count(session: Session, league_id: int) -> int:
    """Pobiera liczbe graczy w lidze."""
    statement = select(LeaguePlayer).where(LeaguePlayer.league_id == league_id)
    return len(session.scalars(statement).all())


def calculate_num_groups(player_count: int) -> int:
    """
    Oblicza liczbe grup na podstawie liczby graczy.

    8-11: 2 grupy
    12-15: 3 grupy
    16-19: 4 grupy
    20-23: 5 grup
    24-27: 6 grup
    28-31: 7 grup
    32-48: 8 grup
    """
    if player_count < 8:
        return 1
    elif player_count <= 11:
        return 2
    elif player_count <= 15:
        return 3
    elif player_count <= 19:
        return 4
    elif player_count <= 23:
        return 5
    elif player_count <= 27:
        return 6
    elif player_count <= 31:
        return 7
    else:
        return 8


def calculate_knockout_size(player_count: int) -> int:
    """
    Oblicza rozmiar fazy pucharowej.

    8-15: Top 4
    16-31: Top 8
    32+: Top 16
    """
    if player_count < 16:
        return 4
    elif player_count < 32:
        return 8
    else:
        return 16


# ============ Group Drawing ============


def draw_groups(
    session: Session,
    league: League,
    baskets: Optional[list[list[int]]] = None,
) -> list[Group]:
    """
    Losuje grupy dla ligi.

    Args:
        session: Sesja bazy danych
        league: Liga
        baskets: Opcjonalne koszyki z player_id dla losowania seeded
                 Jesli None - losowanie calkowicie losowe

    Returns:
        Lista utworzonych grup
    """
    statement = select(LeaguePlayer).where(LeaguePlayer.league_id == league.id)
    players = list(session.scalars(statement).all())

    num_groups = calculate_num_groups(len(players))

    created_groups = []
    for i in range(num_groups):
        group = Group(
            league_id=league.id,
            name=f"Grupa {chr(65 + i)}",
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
    Generuje mecze fazy grupowej (kazdy z kazdym w grupie).

    Args:
        session: Sesja bazy danych
        league: Liga
        weeks_per_match: Tygodnie na rozegranie meczu (dla deadline)

    Returns:
        Lista utworzonych meczow
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
    """Zglasza wynik meczu."""
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
    """Potwierdza wynik meczu i aktualizuje statystyki."""
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
    Pobiera tabele grupy posortowana wg punktow.

    Sortowanie:
    1. Total points (malejaco)
    2. Games played (rosnaco - mniej niezagranych = lepiej)
    3. Average points (malejaco)
    """
    statement = select(LeaguePlayer).where(LeaguePlayer.group_id == group_id)
    players = list(session.scalars(statement).all())

    players.sort(key=lambda p: (-p.total_points, p.games_played, -p.average_points))

    return players


# ============ Knockout Phase ============


def get_advancement_rules(player_count: int) -> tuple[int, int, int]:
    """
    Zwraca zasady awansu na podstawie liczby graczy.

    Returns:
        (num_groups, direct_qualifiers_per_group, best_runners_up)

    8-11: 2 grupy, 1+2 miejsca -> Top 4
    12-15: 3 grupy, 1 miejsca + najlepsze 2 miejsce -> Top 4
    16-19: 4 grupy, 1+2 miejsca -> Top 8
    20-23: 5 grup, 1 miejsca + 3 najlepsze 2 miejsca -> Top 8
    24-27: 6 grup, 1 miejsca + 2 najlepsze 2 miejsca -> Top 8
    28-31: 7 grup, 1 miejsca + najlepsze 2 miejsce -> Top 8
    32-48: 8 grup, 1+2 miejsca -> Top 16
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
    Pobiera graczy ktorzy awansowali do fazy pucharowej.

    Returns:
        Lista graczy posortowana wg wynikow (najlepszy pierwszy)
    """
    statement = select(Group).where(Group.league_id == league.id)
    groups = list(session.scalars(statement).all())

    player_count = get_league_player_count(session, league.id)
    _, direct_qualifiers, best_runners_up = get_advancement_rules(player_count)

    qualified = []
    runners_up = []

    for group in groups:
        standings = get_group_standings(session, group.id)

        for i, player in enumerate(standings[:direct_qualifiers]):
            qualified.append(player)

        if best_runners_up > 0 and len(standings) > direct_qualifiers:
            runners_up.append(standings[direct_qualifiers])

    runners_up.sort(key=lambda p: (-p.total_points, -p.average_points))
    qualified.extend(runners_up[:best_runners_up])

    qualified.sort(key=lambda p: (-p.total_points, -p.average_points))

    return qualified


def generate_knockout_matches(
    session: Session,
    league: League,
    weeks_per_match: int = 2,
) -> list[Match]:
    """
    Generuje mecze fazy pucharowej.

    Najlepszy gra z najgorszym, drugi z przedostatnim itd.
    """
    qualified = get_qualified_players(session, league)
    knockout_size = len(qualified)

    if knockout_size not in [4, 8, 16]:
        raise ValueError(f"Invalid knockout size: {knockout_size}")

    round_names = {
        4: ["semi", "final"],
        8: ["quarter", "semi", "final"],
        16: ["round_of_16", "quarter", "semi", "final"],
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
    Tworzy mecz nastepnej rundy dla zwyciezcy.

    Returns:
        Nowy mecz jesli utworzony, None jesli to byl final
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
    Porownuje graczy dla tiebreakera w fazie pucharowej.

    Returns:
        -1 jesli player1 wygrywa, 1 jesli player2, 0 jesli remis
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
