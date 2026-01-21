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
    # Get all league players for W/D/L stats and army info
    all_league_players = session.scalars(select(LeaguePlayer)).all()

    # Build user stats map
    user_stats = {}  # user_id -> {wins, draws, losses, armies: Counter}
    for lp in all_league_players:
        if not lp.user_id:
            continue
        if lp.user_id not in user_stats:
            user_stats[lp.user_id] = {
                "wins": 0,
                "draws": 0,
                "losses": 0,
                "armies": Counter(),
            }
        user_stats[lp.user_id]["wins"] += lp.games_won or 0
        user_stats[lp.user_id]["draws"] += lp.games_drawn or 0
        user_stats[lp.user_id]["losses"] += lp.games_lost or 0
        if lp.group_army_faction:
            user_stats[lp.user_id]["armies"][lp.group_army_faction] += 1
        if lp.knockout_army_faction:
            user_stats[lp.user_id]["armies"][lp.knockout_army_faction] += 1

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

    # Build ranking list
    ranking = []
    for idx, (elo_record, user) in enumerate(results):
        stats_data = user_stats.get(
            user.id, {"wins": 0, "draws": 0, "losses": 0, "armies": Counter()}
        )
        main_army = (
            stats_data["armies"].most_common(1)[0][0] if stats_data["armies"] else None
        )
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
    league_players = session.scalars(
        select(LeaguePlayer).where(LeaguePlayer.user_id == user_id)
    ).all()

    # Build player_id -> LeaguePlayer mapping
    player_map = {lp.id: lp for lp in league_players}

    # Track army stats (games, wins, draws, losses per army)
    army_stats_dict: dict[str, dict] = {}  # faction -> {games, wins, draws, losses}

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

    # Global stats
    total_wins = 0
    total_draws = 0
    total_losses = 0

    # Group by league
    leagues_data = []

    for league_player in league_players:
        league = session.scalars(
            select(League).where(League.id == league_player.league_id)
        ).first()
        if not league:
            continue

        # Get matches for this league
        statement = (
            select(Match)
            .where(
                Match.league_id == league.id,
                (Match.player1_id == league_player.id)
                | (Match.player2_id == league_player.id),
            )
            .order_by(Match.created_at.desc())
        )
        league_matches = session.scalars(statement).all()

        matches = []
        for match in league_matches:
            # Determine if user is player1 or player2
            is_player1 = match.player1_id == league_player.id
            opponent_lp_id = match.player2_id if is_player1 else match.player1_id

            player_score = match.player1_score if is_player1 else match.player2_score
            opponent_score = match.player2_score if is_player1 else match.player1_score
            player_points = (
                match.player1_league_points
                if is_player1
                else match.player2_league_points
            )

            # Determine result and track army stats
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

                # Track army faction for this match
                army_faction = (
                    league_player.knockout_army_faction
                    if match.phase == "knockout"
                    else league_player.group_army_faction
                )
                add_army_result(army_faction, result)

            # Get opponent info
            opponent_lp = session.scalars(
                select(LeaguePlayer).where(LeaguePlayer.id == opponent_lp_id)
            ).first()
            opponent_username = None
            if opponent_lp:
                if opponent_lp.user_id:
                    opp_user = session.scalars(
                        select(User).where(User.id == opponent_lp.user_id)
                    ).first()
                    opponent_username = (
                        opp_user.username if opp_user else opponent_lp.discord_username
                    )
                else:
                    opponent_username = opponent_lp.discord_username

            # Get army lists for knockout matches
            player_army_list = None
            opponent_army_list = None
            if match.phase == "knockout":
                is_own_profile = current_user and current_user.id == user_id
                can_see_own = league.knockout_lists_visible or is_own_profile
                can_see_opponent = league.knockout_lists_visible

                if can_see_own:
                    player_army_list = league_player.knockout_army_list
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

        # Knockout list visibility for profile
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
