"""API endpoints for player profiles."""

from app.core.deps import get_current_user_optional
from app.db import get_session
from app.league.models import League, LeaguePlayer, Match, PlayerElo
from app.league.schemas import (
    ArmyStatEntry,
    PlayerProfileResponse,
    ProfileLeagueResponse,
    ProfileMatchResponse,
)
from app.users.models import User
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

router = APIRouter()


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

    # Collect army faction usage
    army_counts: dict[str, int] = {}
    for lp in league_players:
        if lp.group_army_faction:
            army_counts[lp.group_army_faction] = (
                army_counts.get(lp.group_army_faction, 0) + 1
            )
        if lp.knockout_army_faction:
            army_counts[lp.knockout_army_faction] = (
                army_counts.get(lp.knockout_army_faction, 0) + 1
            )

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

            # Determine result
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
    total_army_uses = sum(army_counts.values())
    most_played_army = None
    army_stats = []
    if army_counts:
        most_played_army = max(army_counts, key=army_counts.get)
        army_stats = [
            ArmyStatEntry(
                army_faction=faction,
                games_played=count,
                percentage=round(count / total_army_uses * 100, 1),
            )
            for faction, count in sorted(
                army_counts.items(), key=lambda x: x[1], reverse=True
            )
        ]

    return PlayerProfileResponse(
        user_id=user.id,
        username=user.username,
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
