"""API endpoints for player profiles."""

from collections import Counter

from app.core.deps import get_current_user_optional
from app.db import get_session
from app.league.models import ArmyStats, League, LeaguePlayer, Match, PlayerElo
from app.league.schemas import (
    ArmyStatEntry,
    PlayerProfileResponse,
    ProfileLeagueResponse,
    ProfileMatchResponse,
)
from app.users.models import User
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlmodel import Session, func, select

router = APIRouter()


@router.get("/ranking")
async def get_player_ranking(
    session: Session = Depends(get_session),
    search: str = Query(default=None, min_length=1),
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0, ge=0),
):
    """Get player ranking by ELO with optional search and global stats."""
    # Build query for ranking (players with games)
    query = (
        select(PlayerElo, User)
        .join(User, PlayerElo.user_id == User.id)
        .where(PlayerElo.games_played > 0)
        .order_by(PlayerElo.elo.desc(), PlayerElo.games_played.desc())
    )

    # Apply search filter if provided
    if search:
        query = query.where(User.username.ilike(f"%{search}%"))

    # Get total count before pagination
    count_query = select(func.count(PlayerElo.id)).where(PlayerElo.games_played > 0)
    if search:
        count_query = count_query.join(User, PlayerElo.user_id == User.id).where(
            User.username.ilike(f"%{search}%")
        )
    total_count = session.execute(count_query).scalar_one()

    # Apply pagination
    query = query.offset(offset).limit(limit)
    results = session.execute(query).all()

    # Get user IDs for the current page
    user_ids = [user.id for _, user in results]

    # Aggregate stats per user from LeaguePlayer (1 query instead of loading all)
    user_stats = {}
    if user_ids:
        stats_query = (
            select(
                LeaguePlayer.user_id,
                func.coalesce(func.sum(LeaguePlayer.games_won), 0).label("wins"),
                func.coalesce(func.sum(LeaguePlayer.games_drawn), 0).label("draws"),
                func.coalesce(func.sum(LeaguePlayer.games_lost), 0).label("losses"),
            )
            .where(LeaguePlayer.user_id.in_(user_ids))
            .group_by(LeaguePlayer.user_id)
        )
        stats_results = session.execute(stats_query).all()
        for user_id, wins, draws, losses in stats_results:
            user_stats[user_id] = {"wins": wins, "draws": draws, "losses": losses}

        # Get most used army per user (separate query for simplicity)
        army_query = select(
            LeaguePlayer.user_id, LeaguePlayer.group_army_faction
        ).where(
            LeaguePlayer.user_id.in_(user_ids),
            LeaguePlayer.group_army_faction.is_not(None),
        )
        army_results = session.execute(army_query).all()

        # Also get knockout armies
        knockout_army_query = select(
            LeaguePlayer.user_id, LeaguePlayer.knockout_army_faction
        ).where(
            LeaguePlayer.user_id.in_(user_ids),
            LeaguePlayer.knockout_army_faction.is_not(None),
        )
        knockout_results = session.execute(knockout_army_query).all()

        # Count armies per user
        user_armies = {}
        for user_id, faction in army_results:
            if user_id not in user_armies:
                user_armies[user_id] = Counter()
            user_armies[user_id][faction] += 1
        for user_id, faction in knockout_results:
            if user_id not in user_armies:
                user_armies[user_id] = Counter()
            user_armies[user_id][faction] += 1

    # Build ranking list
    ranking = []
    for idx, (elo_record, user) in enumerate(results):
        stats_data = user_stats.get(user.id, {"wins": 0, "draws": 0, "losses": 0})
        armies = user_armies.get(user.id, Counter()) if user_ids else Counter()
        main_army = armies.most_common(1)[0][0] if armies else None
        ranking.append(
            {
                "rank": offset + idx + 1,
                "user_id": user.id,
                "username": user.username,
                "avatar_url": user.avatar_url,
                "elo": elo_record.elo,
                "games_played": elo_record.games_played,
                "wins": stats_data["wins"],
                "draws": stats_data["draws"],
                "losses": stats_data["losses"],
                "main_army": main_army,
            }
        )

    # Get players without games
    new_players = []
    if not search or offset == 0:
        # Get users without ELO record or with 0 games
        users_with_elo = session.scalars(
            select(PlayerElo.user_id).where(PlayerElo.games_played > 0)
        ).all()

        new_players_query = select(User).where(User.id.not_in(users_with_elo))
        if search:
            new_players_query = new_players_query.where(
                User.username.ilike(f"%{search}%")
            )
        new_players_query = new_players_query.order_by(User.username).limit(50)

        new_users = session.scalars(new_players_query).all()
        for user in new_users:
            new_players.append(
                {
                    "user_id": user.id,
                    "username": user.username,
                    "avatar_url": user.avatar_url,
                }
            )

    # Get global stats (only when not searching, for efficiency)
    stats = None
    if not search:
        # Total registered users
        total_users = session.execute(select(func.count(User.id))).scalar_one()

        # Total players with games
        total_active = session.execute(
            select(func.count(PlayerElo.id)).where(PlayerElo.games_played > 0)
        ).scalar_one()

        # Total games from all players
        total_games = (
            session.execute(select(func.sum(PlayerElo.games_played))).scalar_one() or 0
        )
        # Divide by 2 because each game is counted for both players
        total_games = total_games // 2

        # Most popular armies - get from cached ArmyStats
        army_stats_records = session.scalars(
            select(ArmyStats).order_by(ArmyStats.games_played.desc()).limit(5)
        ).all()

        top_armies = [
            {
                "faction": s.faction,
                "count": s.games_played,
                "wins": s.wins,
                "draws": s.draws,
                "losses": s.losses,
                "win_rate": (
                    round(s.wins / s.games_played * 100, 1) if s.games_played > 0 else 0
                ),
            }
            for s in army_stats_records
        ]

        stats = {
            "total_players": total_active,
            "total_users": total_users,
            "total_games": total_games,
            "top_armies": top_armies,
        }

    return {
        "ranking": ranking,
        "new_players": new_players,
        "total_count": total_count,
        "stats": stats,
    }


@router.get("/{user_id}/profile", response_model=PlayerProfileResponse)
async def get_player_profile(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user_optional),
):
    """Gets player profile with matches grouped by league, ELO, and army lists."""
    # Get user
    user = session.scalars(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Get ELO
    elo_record = session.scalars(
        select(PlayerElo).where(PlayerElo.user_id == user_id)
    ).first()
    elo = elo_record.elo if elo_record else 1000
    elo_games = elo_record.games_played if elo_record else 0

    # Get all LeaguePlayer records for this user
    league_players = list(
        session.scalars(
            select(LeaguePlayer).where(LeaguePlayer.user_id == user_id)
        ).all()
    )

    if not league_players:
        # No league participation - return basic profile
        email = user.email if (user.show_email or user.role == "organizer") else None
        return PlayerProfileResponse(
            user_id=user.id,
            username=user.username,
            avatar_url=user.avatar_url,
            city=user.city,
            country=user.country,
            email=email,
            discord_username=user.discord_username,
            elo=elo,
            elo_games_played=elo_games,
            total_games=0,
            total_wins=0,
            total_draws=0,
            total_losses=0,
            win_rate=0.0,
            most_played_army=None,
            army_stats=[],
            leagues=[],
        )

    # Build player_id -> LeaguePlayer mapping
    player_ids = [lp.id for lp in league_players]
    league_ids = [lp.league_id for lp in league_players]

    # Bulk fetch all leagues (1 query instead of N)
    leagues = session.scalars(select(League).where(League.id.in_(league_ids))).all()
    league_map = {l.id: l for l in leagues}

    # Bulk fetch all matches for this player (1 query instead of N)
    all_matches = list(
        session.scalars(
            select(Match)
            .where(
                or_(
                    Match.player1_id.in_(player_ids),
                    Match.player2_id.in_(player_ids),
                )
            )
            .order_by(Match.created_at.desc())
        ).all()
    )

    # Collect all opponent player IDs
    opponent_ids = set()
    for match in all_matches:
        if match.player1_id in player_ids:
            opponent_ids.add(match.player2_id)
        else:
            opponent_ids.add(match.player1_id)

    # Bulk fetch all opponent LeaguePlayers (1 query instead of N)
    opponent_players = (
        session.scalars(
            select(LeaguePlayer).where(LeaguePlayer.id.in_(opponent_ids))
        ).all()
        if opponent_ids
        else []
    )
    opponent_player_map = {op.id: op for op in opponent_players}

    # Collect opponent user IDs and bulk fetch users
    opponent_user_ids = {op.user_id for op in opponent_players if op.user_id}
    opponent_users = (
        session.scalars(select(User).where(User.id.in_(opponent_user_ids))).all()
        if opponent_user_ids
        else []
    )
    opponent_user_map = {u.id: u for u in opponent_users}

    # Group matches by league_id for the player
    matches_by_league = {}
    for match in all_matches:
        # Find which league_player this match belongs to
        if match.player1_id in player_ids:
            lp_id = match.player1_id
        else:
            lp_id = match.player2_id
        # Get the league_id for this player
        for lp in league_players:
            if lp.id == lp_id:
                lid = lp.league_id
                if lid not in matches_by_league:
                    matches_by_league[lid] = []
                matches_by_league[lid].append((match, lp))
                break

    # Track army stats
    army_stats_dict: dict[str, dict] = {}

    def add_army_result(faction: str, result: str):
        if not faction:
            return
        if faction not in army_stats_dict:
            army_stats_dict[faction] = {"games": 0, "wins": 0, "draws": 0, "losses": 0}
        army_stats_dict[faction]["games"] += 1
        if result == "win":
            army_stats_dict[faction]["wins"] += 1
        elif result == "draw":
            army_stats_dict[faction]["draws"] += 1
        elif result == "loss":
            army_stats_dict[faction]["losses"] += 1

    total_wins = 0
    total_draws = 0
    total_losses = 0
    leagues_data = []

    for league_player in league_players:
        league = league_map.get(league_player.league_id)
        if not league:
            continue

        league_matches_data = matches_by_league.get(league.id, [])
        matches = []

        for match, lp in league_matches_data:
            is_player1 = match.player1_id == lp.id
            opponent_lp_id = match.player2_id if is_player1 else match.player1_id

            player_score = match.player1_score if is_player1 else match.player2_score
            opponent_score = match.player2_score if is_player1 else match.player1_score
            player_points = (
                match.player1_league_points
                if is_player1
                else match.player2_league_points
            )

            result = None
            if match.status == "confirmed" and player_score is not None:
                if player_score > opponent_score:
                    result = "win"
                    total_wins += 1
                elif player_score < opponent_score:
                    result = "loss"
                    total_losses += 1
                else:
                    result = "draw"
                    total_draws += 1

                army_faction = (
                    lp.knockout_army_faction
                    if match.phase == "knockout"
                    else lp.group_army_faction
                )
                add_army_result(army_faction, result)

            # Get opponent info from cache
            opponent_lp = opponent_player_map.get(opponent_lp_id)
            opponent_username = None
            if opponent_lp:
                if opponent_lp.user_id and opponent_lp.user_id in opponent_user_map:
                    opponent_username = opponent_user_map[opponent_lp.user_id].username
                else:
                    opponent_username = opponent_lp.discord_username

            # Army lists for knockout
            player_army_list = None
            opponent_army_list = None
            if match.phase == "knockout":
                is_own_profile = current_user and current_user.id == user_id
                can_see_own = league.knockout_lists_visible or is_own_profile
                can_see_opponent = league.knockout_lists_visible

                if can_see_own:
                    player_army_list = lp.knockout_army_list
                if can_see_opponent and opponent_lp:
                    opponent_army_list = opponent_lp.knockout_army_list

            matches.append(
                ProfileMatchResponse(
                    match_id=match.id,
                    phase=match.phase,
                    knockout_round=match.knockout_round,
                    opponent_id=opponent_lp_id,
                    opponent_username=opponent_username,
                    player_score=player_score,
                    opponent_score=opponent_score,
                    player_league_points=player_points,
                    result=result,
                    status=match.status,
                    played_at=match.confirmed_at,
                    player_army_list=player_army_list,
                    opponent_army_list=opponent_army_list,
                )
            )

        is_own_profile = current_user and current_user.id == user_id
        show_knockout_list = league.knockout_lists_visible or is_own_profile
        knockout_list = league_player.knockout_army_list if show_knockout_list else None

        leagues_data.append(
            ProfileLeagueResponse(
                league_id=league.id,
                league_name=league.name,
                league_status=league.status,
                games_played=league_player.games_played,
                games_won=league_player.games_won,
                games_drawn=league_player.games_drawn,
                games_lost=league_player.games_lost,
                total_points=league_player.total_points,
                average_points=league_player.average_points,
                knockout_army_list=knockout_list,
                knockout_list_submitted=league_player.knockout_army_list is not None,
                knockout_placement=league_player.knockout_placement,
                matches=matches,
            )
        )

    total_games = total_wins + total_draws + total_losses
    win_rate = (total_wins / total_games * 100) if total_games > 0 else 0.0

    # Calculate army stats
    total_army_uses = sum(stats["games"] for stats in army_stats_dict.values())
    most_played_army = None
    army_stats = []
    if army_stats_dict:
        most_played_army = max(
            army_stats_dict, key=lambda x: army_stats_dict[x]["games"]
        )
        army_stats = [
            ArmyStatEntry(
                army_faction=faction,
                games_played=stats["games"],
                wins=stats["wins"],
                draws=stats["draws"],
                losses=stats["losses"],
                percentage=round(stats["games"] / total_army_uses * 100, 1),
            )
            for faction, stats in sorted(
                army_stats_dict.items(), key=lambda x: x[1]["games"], reverse=True
            )
        ]

    # Contact info - email visible if user allows it OR is organizer
    email = user.email if (user.show_email or user.role == "organizer") else None

    return PlayerProfileResponse(
        user_id=user.id,
        username=user.username,
        avatar_url=user.avatar_url,
        city=user.city,
        country=user.country,
        email=email,
        discord_username=user.discord_username,
        elo=elo,
        elo_games_played=elo_games,
        total_games=total_games,
        total_wins=total_wins,
        total_draws=total_draws,
        total_losses=total_losses,
        win_rate=round(win_rate, 1),
        most_played_army=most_played_army,
        army_stats=army_stats,
        leagues=leagues_data,
    )
