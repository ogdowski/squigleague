"""API endpoints for the league module."""

from datetime import datetime, timedelta

from app.core.deps import get_current_user, get_current_user_optional, require_role
from app.db import get_session
from app.league.models import Group, League, LeaguePlayer, Match, PlayerElo
from app.league.schemas import (
    GroupStandings,
    KnockoutBracket,
    KnockoutListResponse,
    KnockoutListSubmit,
    LeagueCreate,
    LeagueListResponse,
    LeaguePlayerCreate,
    LeaguePlayerResponse,
    LeagueResponse,
    LeagueUpdate,
    MatchResponse,
    MatchResultSubmit,
    PlayerEloResponse,
    StandingsEntry,
)
from app.league.service import (
    calculate_phase_dates,
    confirm_match_result,
    draw_groups,
    generate_group_matches,
    generate_knockout_matches,
    get_allowed_knockout_sizes,
    get_group_standings,
    get_knockout_constraints,
    get_league_player_count,
    get_qualified_players,
    get_qualifying_info,
    submit_match_result,
)
from app.users.models import User
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

router = APIRouter()

get_organizer = require_role("organizer", "admin")
get_admin = require_role("admin")


# ============ League CRUD ============


@router.post("", response_model=LeagueResponse, status_code=status.HTTP_201_CREATED)
async def create_league(
    data: LeagueCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_organizer),
):
    """Creates a new league (organizer+ only)."""
    if data.min_group_size > data.max_group_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="min_group_size cannot be greater than max_group_size",
        )

    if data.max_players is not None and data.min_players > data.max_players:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="min_players cannot be greater than max_players",
        )

    # Validate knockout_size against min_players constraints
    if data.knockout_size is not None:
        if data.knockout_size not in [2, 4, 8, 16, 32]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="knockout_size must be 2, 4, 8, 16, or 32",
            )
        _, _, max_knockout = get_knockout_constraints(data.min_players)
        if data.knockout_size > max_knockout:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"knockout_size ({data.knockout_size}) exceeds maximum ({max_knockout}) for {data.min_players} players",
            )

    league = League(
        name=data.name,
        description=data.description,
        organizer_id=current_user.id,
        registration_end=data.registration_end,
        min_players=data.min_players,
        max_players=data.max_players,
        min_group_size=data.min_group_size,
        max_group_size=data.max_group_size,
        days_per_match=data.days_per_match,
        has_knockout_phase=data.has_knockout_phase,
        knockout_size=data.knockout_size,
    )
    session.add(league)
    session.commit()
    session.refresh(league)

    return LeagueResponse(
        **league.__dict__,
        player_count=0,
        is_registration_open=league.is_registration_open,
        qualifying_spots_per_group=None,
        total_qualifying_spots=None,
    )


@router.get("", response_model=list[LeagueListResponse])
async def list_leagues(
    session: Session = Depends(get_session),
):
    """Lists all leagues."""
    statement = select(League).order_by(League.created_at.desc())
    leagues = session.scalars(statement).all()

    result = []
    for league in leagues:
        player_count = get_league_player_count(session, league.id)

        statement = select(User).where(User.id == league.organizer_id)
        organizer = session.scalars(statement).first()

        result.append(
            LeagueListResponse(
                id=league.id,
                name=league.name,
                status=league.status,
                registration_end=league.registration_end,
                player_count=player_count,
                organizer_name=organizer.username if organizer else None,
            )
        )

    return result


@router.get("/{league_id}", response_model=LeagueResponse)
async def get_league(
    league_id: int,
    session: Session = Depends(get_session),
):
    """Gets league details."""
    statement = select(League).where(League.id == league_id)
    league = session.scalars(statement).first()

    if not league:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="League not found",
        )

    player_count = get_league_player_count(session, league_id)
    spots_per_group, total_spots = get_qualifying_info(session, league)

    return LeagueResponse(
        **league.__dict__,
        player_count=player_count,
        is_registration_open=league.is_registration_open,
        qualifying_spots_per_group=spots_per_group if spots_per_group > 0 else None,
        total_qualifying_spots=total_spots if total_spots > 0 else None,
    )


@router.patch("/{league_id}", response_model=LeagueResponse)
async def update_league(
    league_id: int,
    data: LeagueUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_organizer),
):
    """Updates a league (league organizer or admin only)."""
    statement = select(League).where(League.id == league_id)
    league = session.scalars(statement).first()

    if not league:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="League not found",
        )

    if league.organizer_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this league",
        )

    # Validate group size constraints
    min_group = (
        data.min_group_size
        if data.min_group_size is not None
        else league.min_group_size
    )
    max_group = (
        data.max_group_size
        if data.max_group_size is not None
        else league.max_group_size
    )
    if min_group > max_group:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="min_group_size cannot be greater than max_group_size",
        )

    # Validate player constraints
    min_players = (
        data.min_players if data.min_players is not None else league.min_players
    )
    max_players = (
        data.max_players if data.max_players is not None else league.max_players
    )
    if max_players is not None and min_players > max_players:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="min_players cannot be greater than max_players",
        )

    # Validate knockout_size
    player_count = get_league_player_count(session, league_id)
    if data.knockout_size is not None:
        if data.knockout_size not in [2, 4, 8, 16, 32]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="knockout_size must be 2, 4, 8, 16, or 32",
            )
        # Check against current player count
        if data.knockout_size > player_count:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"knockout_size ({data.knockout_size}) cannot be greater than player count ({player_count})",
            )
        # Check against max allowed for player count
        _, _, max_knockout = get_knockout_constraints(player_count)
        if data.knockout_size > max_knockout:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"knockout_size ({data.knockout_size}) exceeds maximum ({max_knockout}) for {player_count} players",
            )

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(league, key, value)

    session.add(league)
    session.commit()
    session.refresh(league)

    player_count = get_league_player_count(session, league_id)
    spots_per_group, total_spots = get_qualifying_info(session, league)

    return LeagueResponse(
        **league.__dict__,
        player_count=player_count,
        is_registration_open=league.is_registration_open,
        qualifying_spots_per_group=spots_per_group if spots_per_group > 0 else None,
        total_qualifying_spots=total_spots if total_spots > 0 else None,
    )


@router.delete("/{league_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_league(
    league_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_admin),
):
    """Deletes a league (admin only)."""
    statement = select(League).where(League.id == league_id)
    league = session.scalars(statement).first()

    if not league:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="League not found",
        )

    session.delete(league)
    session.commit()


# ============ Players ============


@router.post("/{league_id}/join", response_model=LeaguePlayerResponse)
async def join_league(
    league_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Joins a league (before it starts)."""
    statement = select(League).where(League.id == league_id)
    league = session.scalars(statement).first()

    if not league:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="League not found",
        )

    if not league.is_registration_open:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration is closed",
        )

    statement = select(LeaguePlayer).where(
        LeaguePlayer.league_id == league_id,
        LeaguePlayer.user_id == current_user.id,
    )
    existing = session.scalars(statement).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already joined this league",
        )

    player = LeaguePlayer(
        league_id=league_id,
        user_id=current_user.id,
        is_claimed=True,
    )
    session.add(player)
    session.commit()
    session.refresh(player)

    return LeaguePlayerResponse(
        id=player.id,
        league_id=player.league_id,
        user_id=player.user_id,
        group_id=player.group_id,
        group_name=None,
        games_played=player.games_played,
        games_won=player.games_won,
        games_drawn=player.games_drawn,
        games_lost=player.games_lost,
        total_points=player.total_points,
        average_points=player.average_points,
        is_claimed=player.is_claimed,
        discord_username=player.discord_username,
        username=current_user.username,
        joined_at=player.joined_at,
        knockout_list_submitted=player.knockout_army_list is not None,
    )


@router.post("/{league_id}/add-player", response_model=LeaguePlayerResponse)
async def add_player(
    league_id: int,
    data: LeaguePlayerCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_organizer),
):
    """Adds a player manually (organizer)."""
    statement = select(League).where(League.id == league_id)
    league = session.scalars(statement).first()

    if not league:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="League not found",
        )

    if league.organizer_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized",
        )

    player = LeaguePlayer(
        league_id=league_id,
        user_id=None,
        discord_username=data.discord_username,
        is_claimed=False,
    )
    session.add(player)
    session.commit()
    session.refresh(player)

    return LeaguePlayerResponse(
        id=player.id,
        league_id=player.league_id,
        user_id=player.user_id,
        group_id=player.group_id,
        group_name=None,
        games_played=player.games_played,
        games_won=player.games_won,
        games_drawn=player.games_drawn,
        games_lost=player.games_lost,
        total_points=player.total_points,
        average_points=player.average_points,
        is_claimed=player.is_claimed,
        discord_username=player.discord_username,
        username=None,
        joined_at=player.joined_at,
        knockout_list_submitted=False,
    )


@router.get("/{league_id}/players", response_model=list[LeaguePlayerResponse])
async def list_players(
    league_id: int,
    session: Session = Depends(get_session),
):
    """Lists players in a league."""
    statement = select(LeaguePlayer).where(LeaguePlayer.league_id == league_id)
    players = session.scalars(statement).all()

    result = []
    for player in players:
        username = None
        if player.user_id:
            statement = select(User).where(User.id == player.user_id)
            user = session.scalars(statement).first()
            username = user.username if user else None

        group_name = None
        if player.group_id:
            statement = select(Group).where(Group.id == player.group_id)
            group = session.scalars(statement).first()
            group_name = group.name if group else None

        result.append(
            LeaguePlayerResponse(
                id=player.id,
                league_id=player.league_id,
                user_id=player.user_id,
                group_id=player.group_id,
                group_name=group_name,
                games_played=player.games_played,
                games_won=player.games_won,
                games_drawn=player.games_drawn,
                games_lost=player.games_lost,
                total_points=player.total_points,
                average_points=player.average_points,
                is_claimed=player.is_claimed,
                discord_username=player.discord_username,
                username=username,
                joined_at=player.joined_at,
                knockout_list_submitted=player.knockout_army_list is not None,
            )
        )

    return result


@router.delete(
    "/{league_id}/player/{player_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def remove_player(
    league_id: int,
    player_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_organizer),
):
    """Removes a player from a league (organizer)."""
    statement = select(League).where(League.id == league_id)
    league = session.scalars(statement).first()

    if not league:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="League not found",
        )

    if league.organizer_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized",
        )

    statement = select(LeaguePlayer).where(
        LeaguePlayer.id == player_id,
        LeaguePlayer.league_id == league_id,
    )
    player = session.scalars(statement).first()

    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found",
        )

    session.delete(player)
    session.commit()


# ============ Groups ============


@router.post("/{league_id}/draw-groups")
async def draw_groups_endpoint(
    league_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_organizer),
):
    """Draws groups (organizer)."""
    statement = select(League).where(League.id == league_id)
    league = session.scalars(statement).first()

    if not league:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="League not found",
        )

    if league.organizer_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized",
        )

    if league.status != "registration":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Groups can only be drawn during registration phase",
        )

    player_count = get_league_player_count(session, league_id)
    if player_count < league.min_players:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Need at least {league.min_players} players to draw groups (currently {player_count})",
        )

    groups = draw_groups(session, league)
    matches = generate_group_matches(session, league)

    # Calculate phase dates
    start_date = datetime.utcnow()
    group_start, group_end, knockout_start, knockout_end = calculate_phase_dates(
        session, league, start_date
    )

    league.status = "group_phase"
    league.group_phase_start = group_start
    league.group_phase_end = group_end
    league.knockout_phase_start = knockout_start
    league.knockout_phase_end = knockout_end
    session.add(league)
    session.commit()

    return {
        "message": f"Created {len(groups)} groups with {len(matches)} matches",
        "groups": [{"id": g.id, "name": g.name} for g in groups],
        "group_phase_end": group_end.isoformat() if group_end else None,
        "knockout_phase_end": knockout_end.isoformat() if knockout_end else None,
    }


@router.post("/{league_id}/recalculate-dates")
async def recalculate_dates_endpoint(
    league_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_organizer),
):
    """Recalculates phase dates based on current settings (organizer)."""
    statement = select(League).where(League.id == league_id)
    league = session.scalars(statement).first()

    if not league:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="League not found",
        )

    if league.organizer_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized",
        )

    if league.status == "registration":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot recalculate dates before groups are drawn",
        )

    # Use group_phase_start as the base, or now if not set
    start_date = league.group_phase_start or datetime.utcnow()
    group_start, group_end, knockout_start, knockout_end = calculate_phase_dates(
        session, league, start_date
    )

    league.group_phase_start = group_start
    league.group_phase_end = group_end
    league.knockout_phase_start = knockout_start
    league.knockout_phase_end = knockout_end
    session.add(league)
    session.commit()

    return {
        "message": "Dates recalculated",
        "group_phase_start": group_start.isoformat() if group_start else None,
        "group_phase_end": group_end.isoformat() if group_end else None,
        "knockout_phase_start": knockout_start.isoformat() if knockout_start else None,
        "knockout_phase_end": knockout_end.isoformat() if knockout_end else None,
    }


@router.post("/{league_id}/end-group-phase")
async def end_group_phase_endpoint(
    league_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_organizer),
):
    """Ends the group phase (organizer). Knockout can only start after this."""
    statement = select(League).where(League.id == league_id)
    league = session.scalars(statement).first()

    if not league:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="League not found",
        )

    if league.organizer_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized",
        )

    if league.status != "group_phase":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="League is not in group phase",
        )

    if league.group_phase_ended:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Group phase already ended",
        )

    league.group_phase_ended = True
    session.add(league)
    session.commit()

    return {"message": "Group phase ended"}


@router.get("/{league_id}/standings", response_model=list[GroupStandings])
async def get_standings(
    league_id: int,
    session: Session = Depends(get_session),
):
    """Gets standings for all groups."""
    # Get league for qualifying info
    league = session.scalars(select(League).where(League.id == league_id)).first()
    spots_per_group, _ = get_qualifying_info(session, league) if league else (0, 0)

    statement = select(Group).where(Group.league_id == league_id)
    groups = session.scalars(statement).all()

    result = []
    for group in groups:
        players = get_group_standings(session, group.id)

        standings = []
        for position, player in enumerate(players, 1):
            username = None
            if player.user_id:
                stmt = select(User).where(User.id == player.user_id)
                user = session.scalars(stmt).first()
                username = user.username if user else None

            standings.append(
                StandingsEntry(
                    position=position,
                    player_id=player.id,
                    username=username,
                    discord_username=player.discord_username,
                    games_played=player.games_played,
                    games_won=player.games_won,
                    games_drawn=player.games_drawn,
                    games_lost=player.games_lost,
                    total_points=player.total_points,
                    average_points=player.average_points,
                    qualifies=position <= spots_per_group,
                )
            )

        result.append(
            GroupStandings(
                group_id=group.id,
                group_name=group.name,
                standings=standings,
                qualifying_spots=spots_per_group,
            )
        )

    return result


# ============ Matches ============


@router.get("/{league_id}/matches", response_model=list[MatchResponse])
async def list_matches(
    league_id: int,
    phase: str = None,
    session: Session = Depends(get_session),
):
    """Lists matches in a league."""
    statement = select(Match).where(Match.league_id == league_id)
    if phase:
        statement = statement.where(Match.phase == phase)
    statement = statement.order_by(Match.created_at)

    matches = session.scalars(statement).all()

    result = []
    for match in matches:
        p1_username = None
        p2_username = None

        stmt = select(LeaguePlayer).where(LeaguePlayer.id == match.player1_id)
        p1 = session.scalars(stmt).first()
        if p1:
            if p1.user_id:
                stmt = select(User).where(User.id == p1.user_id)
                user = session.scalars(stmt).first()
                p1_username = user.username if user else p1.discord_username
            else:
                p1_username = p1.discord_username

        stmt = select(LeaguePlayer).where(LeaguePlayer.id == match.player2_id)
        p2 = session.scalars(stmt).first()
        if p2:
            if p2.user_id:
                stmt = select(User).where(User.id == p2.user_id)
                user = session.scalars(stmt).first()
                p2_username = user.username if user else p2.discord_username
            else:
                p2_username = p2.discord_username

        result.append(
            MatchResponse(
                id=match.id,
                league_id=match.league_id,
                player1_id=match.player1_id,
                player2_id=match.player2_id,
                player1_username=p1_username,
                player2_username=p2_username,
                phase=match.phase,
                knockout_round=match.knockout_round,
                player1_score=match.player1_score,
                player2_score=match.player2_score,
                player1_league_points=match.player1_league_points,
                player2_league_points=match.player2_league_points,
                status=match.status,
                deadline=match.deadline,
                map_name=match.map_name,
                created_at=match.created_at,
                is_completed=match.is_completed,
            )
        )

    return result


@router.post("/{league_id}/matches/{match_id}/result")
async def submit_result(
    league_id: int,
    match_id: int,
    data: MatchResultSubmit,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Submits a match result."""
    statement = select(Match).where(
        Match.id == match_id,
        Match.league_id == league_id,
    )
    match = session.scalars(statement).first()

    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found",
        )

    if match.status == "confirmed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Match result already confirmed",
        )

    stmt = select(LeaguePlayer).where(LeaguePlayer.id == match.player1_id)
    p1 = session.scalars(stmt).first()
    stmt = select(LeaguePlayer).where(LeaguePlayer.id == match.player2_id)
    p2 = session.scalars(stmt).first()

    stmt = select(League).where(League.id == league_id)
    league = session.scalars(stmt).first()

    is_player = (p1 and p1.user_id == current_user.id) or (
        p2 and p2.user_id == current_user.id
    )
    is_organizer = league and league.organizer_id == current_user.id
    is_admin = current_user.role == "admin"

    if not (is_player or is_organizer or is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to submit result for this match",
        )

    submit_match_result(
        session,
        match,
        data.player1_score,
        data.player2_score,
        current_user.id,
        data.map_name,
    )

    return {"message": "Result submitted, waiting for confirmation"}


@router.post("/{league_id}/matches/{match_id}/confirm")
async def confirm_result(
    league_id: int,
    match_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Confirms a match result."""
    statement = select(Match).where(
        Match.id == match_id,
        Match.league_id == league_id,
    )
    match = session.scalars(statement).first()

    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found",
        )

    if match.status != "pending_confirmation":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Match is not pending confirmation",
        )

    stmt = select(LeaguePlayer).where(LeaguePlayer.id == match.player1_id)
    p1 = session.scalars(stmt).first()
    stmt = select(LeaguePlayer).where(LeaguePlayer.id == match.player2_id)
    p2 = session.scalars(stmt).first()

    stmt = select(League).where(League.id == league_id)
    league = session.scalars(stmt).first()

    submitter_is_p1 = p1 and p1.user_id == match.submitted_by_id
    is_opponent = (submitter_is_p1 and p2 and p2.user_id == current_user.id) or (
        not submitter_is_p1 and p1 and p1.user_id == current_user.id
    )
    is_organizer = league and league.organizer_id == current_user.id
    is_admin = current_user.role == "admin"

    if not (is_opponent or is_organizer or is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to confirm this match",
        )

    confirm_match_result(session, match, current_user.id)

    return {"message": "Result confirmed"}


# ============ Knockout Phase ============


@router.post("/{league_id}/start-knockout")
async def start_knockout(
    league_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_organizer),
):
    """Starts knockout phase (organizer)."""
    statement = select(League).where(League.id == league_id)
    league = session.scalars(statement).first()

    if not league:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="League not found",
        )

    if league.organizer_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized",
        )

    if league.status != "group_phase":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="League must be in group phase to start knockout",
        )

    if not league.group_phase_ended:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Group phase must be ended first before starting knockout",
        )

    matches = generate_knockout_matches(session, league)

    league.status = "knockout_phase"
    league.group_phase_end = datetime.utcnow()
    league.knockout_phase_start = datetime.utcnow()
    session.add(league)
    session.commit()

    return {
        "message": f"Started knockout phase with {len(matches)} matches",
        "qualified_count": len(matches) * 2,
    }


@router.post("/{league_id}/reveal-lists")
async def reveal_knockout_lists(
    league_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_organizer),
):
    """Reveals knockout phase army lists (organizer)."""
    statement = select(League).where(League.id == league_id)
    league = session.scalars(statement).first()

    if not league:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="League not found",
        )

    if league.organizer_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized",
        )

    league.knockout_lists_visible = True
    session.add(league)
    session.commit()

    return {"message": "Knockout lists are now visible"}


@router.post("/{league_id}/knockout-list")
async def submit_knockout_list(
    league_id: int,
    data: KnockoutListSubmit,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Submits army list for knockout phase."""
    statement = select(LeaguePlayer).where(
        LeaguePlayer.league_id == league_id,
        LeaguePlayer.user_id == current_user.id,
    )
    player = session.scalars(statement).first()

    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You are not a player in this league",
        )

    statement = select(League).where(League.id == league_id)
    league = session.scalars(statement).first()

    if league and league.knockout_lists_visible:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Lists are already revealed, cannot submit",
        )

    player.knockout_army_list = data.army_list
    player.knockout_list_submitted_at = datetime.utcnow()
    session.add(player)
    session.commit()

    return {"message": "Knockout list submitted"}


@router.get(
    "/{league_id}/knockout-list/{player_id}", response_model=KnockoutListResponse
)
async def get_knockout_list(
    league_id: int,
    player_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user_optional),
):
    """Gets player's army list (if visible)."""
    statement = select(League).where(League.id == league_id)
    league = session.scalars(statement).first()

    if not league:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="League not found",
        )

    statement = select(LeaguePlayer).where(
        LeaguePlayer.id == player_id,
        LeaguePlayer.league_id == league_id,
    )
    player = session.scalars(statement).first()

    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found",
        )

    is_owner = current_user and player.user_id == current_user.id
    is_organizer = current_user and league.organizer_id == current_user.id
    is_admin = current_user and current_user.role == "admin"

    if not league.knockout_lists_visible and not (is_owner or is_organizer or is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Knockout lists are not visible yet",
        )

    username = None
    if player.user_id:
        stmt = select(User).where(User.id == player.user_id)
        user = session.scalars(stmt).first()
        username = user.username if user else player.discord_username
    else:
        username = player.discord_username

    return KnockoutListResponse(
        player_id=player.id,
        username=username,
        army_list=player.knockout_army_list,
        submitted_at=player.knockout_list_submitted_at,
    )


# ============ ELO ============


@router.get("/elo/ranking", response_model=list[PlayerEloResponse])
async def get_elo_ranking(
    limit: int = 50,
    session: Session = Depends(get_session),
):
    """Gets ELO ranking."""
    statement = select(PlayerElo).order_by(PlayerElo.elo.desc()).limit(limit)
    rankings = session.scalars(statement).all()

    result = []
    for elo in rankings:
        stmt = select(User).where(User.id == elo.user_id)
        user = session.scalars(stmt).first()

        result.append(
            PlayerEloResponse(
                user_id=elo.user_id,
                username=user.username if user else None,
                elo=elo.elo,
                games_played=elo.games_played,
                updated_at=elo.updated_at,
            )
        )

    return result


@router.get("/elo/{user_id}", response_model=PlayerEloResponse)
async def get_player_elo(
    user_id: int,
    session: Session = Depends(get_session),
):
    """Gets player's ELO."""
    statement = select(PlayerElo).where(PlayerElo.user_id == user_id)
    elo = session.scalars(statement).first()

    if not elo:
        elo = PlayerElo(user_id=user_id, elo=1000, games_played=0)

    stmt = select(User).where(User.id == user_id)
    user = session.scalars(stmt).first()

    return PlayerEloResponse(
        user_id=elo.user_id,
        username=user.username if user else None,
        elo=elo.elo,
        games_played=elo.games_played,
        updated_at=elo.updated_at if elo.id else datetime.utcnow(),
    )
