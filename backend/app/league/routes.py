"""API endpoints for the league module."""

import random
from datetime import datetime, timedelta

from app.core.deps import get_current_user, get_current_user_optional, require_role
from app.db import get_session
from app.league.constants import MISSION_MAPS
from app.league.models import (
    Group,
    League,
    LeaguePlayer,
    Match,
    PlayerElo,
    Vote,
    VoteCategory,
)
from app.league.schemas import (
    ArmyListResponse,
    ArmyListSubmit,
    ChangeGroupResponse,
    ChangePlayerGroupRequest,
    GroupResponse,
    GroupStandings,
    GroupUpdate,
    KnockoutBracket,
    KnockoutListResponse,
    KnockoutListSubmit,
    LeagueCreate,
    LeagueListResponse,
    LeaguePlayerCreate,
    LeaguePlayerResponse,
    LeagueResponse,
    LeagueUpdate,
    MatchArmyListSubmit,
    MatchDetailResponse,
    MatchMapSet,
    MatchResponse,
    MatchResultSubmit,
    PlayerEloResponse,
    PlayerRemovalResponse,
    StandingsEntry,
    TieBreakerRequest,
    VoteCategoryCreate,
    VoteCategoryResponse,
    VoteCreate,
    VoteResponse,
    VoteResultEntry,
    VotingResultsResponse,
)
from app.league.service import (
    advance_to_next_knockout_round,
    all_round_matches_confirmed,
    break_tie_random,
    calculate_knockout_size,
    calculate_phase_dates,
    cast_vote,
    change_player_group,
    close_voting,
    confirm_match_result,
    create_vote_category,
    draw_groups,
    enable_voting_for_league,
    generate_group_matches,
    generate_knockout_matches,
    get_allowed_knockout_sizes,
    get_group_standings,
    get_knockout_constraints,
    get_knockout_round_names,
    get_league_player_count,
    get_next_knockout_round,
    get_player_vote,
    get_qualified_players,
    get_qualifying_info,
    get_voting_results,
    remove_player_from_league,
    submit_match_result,
    update_match_deadlines,
)
from app.users.models import User
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
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
        city=data.city,
        country=data.country,
        organizer_id=current_user.id,
        registration_end=data.registration_end,
        min_players=data.min_players,
        max_players=data.max_players,
        min_group_size=data.min_group_size,
        max_group_size=data.max_group_size,
        days_per_match=data.days_per_match,
        has_knockout_phase=data.has_knockout_phase,
        knockout_size=data.knockout_size,
        has_group_phase_lists=data.has_group_phase_lists,
        has_knockout_phase_lists=data.has_knockout_phase_lists,
        voting_enabled=data.voting_enabled,
    )

    # Add city/country to shared locations pool
    from app.users.routes import add_location_if_new

    if data.city:
        add_location_if_new(session, city=data.city)
    if data.country:
        add_location_if_new(session, country=data.country)

    session.add(league)
    session.commit()
    session.refresh(league)

    # Auto-create default voting category if voting is enabled
    if data.voting_enabled:
        default_category = VoteCategory(
            league_id=league.id,
            name="best_sport",
            description=None,
        )
        session.add(default_category)
        session.commit()

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
    current_user: User = Depends(get_current_user_optional),
):
    """Lists all leagues with user participation info (excludes cancelled)."""
    statement = (
        select(League)
        .where(League.status != "cancelled")
        .order_by(League.created_at.desc())
    )
    leagues = list(session.scalars(statement).all())

    if not leagues:
        return []

    league_ids = [l.id for l in leagues]
    organizer_ids = list({l.organizer_id for l in leagues})

    # Bulk fetch player counts (1 query instead of N)
    player_counts = session.execute(
        select(LeaguePlayer.league_id, func.count(LeaguePlayer.id))
        .where(LeaguePlayer.league_id.in_(league_ids))
        .group_by(LeaguePlayer.league_id)
    ).all()
    count_map = {league_id: count for league_id, count in player_counts}

    # Bulk fetch organizers (1 query instead of N)
    organizers = session.scalars(select(User).where(User.id.in_(organizer_ids))).all()
    organizer_map = {u.id: u for u in organizers}

    # Bulk fetch user's league memberships (1 query instead of N)
    user_league_ids = set()
    if current_user:
        user_memberships = session.scalars(
            select(LeaguePlayer.league_id).where(
                LeaguePlayer.league_id.in_(league_ids),
                LeaguePlayer.user_id == current_user.id,
            )
        ).all()
        user_league_ids = set(user_memberships)

    result = []
    for league in leagues:
        organizer = organizer_map.get(league.organizer_id)
        is_organizer = bool(current_user and league.organizer_id == current_user.id)
        is_player = league.id in user_league_ids

        result.append(
            LeagueListResponse(
                id=league.id,
                name=league.name,
                city=league.city,
                country=league.country,
                status=league.status,
                registration_end=league.registration_end,
                group_phase_end=league.group_phase_end,
                knockout_phase_end=league.knockout_phase_end,
                finished_at=league.finished_at,
                player_count=count_map.get(league.id, 0),
                organizer_name=organizer.username if organizer else None,
                is_organizer=is_organizer,
                is_player=is_player,
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

    # Get organizer name
    organizer = session.scalars(
        select(User).where(User.id == league.organizer_id)
    ).first()

    return LeagueResponse(
        **league.__dict__,
        player_count=player_count,
        is_registration_open=league.is_registration_open,
        qualifying_spots_per_group=spots_per_group if spots_per_group > 0 else None,
        total_qualifying_spots=total_spots if total_spots > 0 else None,
        organizer_name=organizer.username if organizer else None,
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

    # Add city/country to shared locations pool
    from app.users.routes import add_location_if_new

    if data.city:
        add_location_if_new(session, city=data.city)
    if data.country:
        add_location_if_new(session, country=data.country)

    # Set finished_at when status changes to finished
    if update_data.get("status") == "finished" and league.finished_at is None:
        league.finished_at = datetime.utcnow()

    # Update match deadlines when phase end dates change
    phase_dates_changed = (
        "group_phase_end" in update_data or "knockout_phase_end" in update_data
    )
    session.add(league)
    session.commit()

    if phase_dates_changed:
        update_match_deadlines(session, league)

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

    # Check max_players limit
    if league.max_players is not None:
        current_count = get_league_player_count(session, league_id)
        if current_count >= league.max_players:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="League is full",
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


@router.post("/{league_id}/leave", response_model=PlayerRemovalResponse)
async def leave_league(
    league_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Leaves a league (player drops out).

    - During registration: simply removes the player
    - During group/knockout phase: removes player and awards walkovers (25:0, 1175 pts)
    - After finished: not allowed
    """
    statement = select(League).where(League.id == league_id)
    league = session.scalars(statement).first()

    if not league:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="League not found",
        )

    if league.status == "finished":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="League has already finished",
        )

    statement = select(LeaguePlayer).where(
        LeaguePlayer.league_id == league_id,
        LeaguePlayer.user_id == current_user.id,
    )
    player = session.scalars(statement).first()

    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You are not in this league",
        )

    # Award walkovers during active phases (group or knockout)
    award_walkovers = league.status in ("group_phase", "knockout_phase")

    result = remove_player_from_league(session, player, award_walkovers=award_walkovers)

    return PlayerRemovalResponse(
        message="Successfully left the league",
        deleted_matches=result["deleted_matches"],
        walkover_matches=result["walkover_matches"],
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

    # Check max_players limit
    if league.max_players is not None:
        current_count = get_league_player_count(session, league_id)
        if current_count >= league.max_players:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="League is full",
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
    # Get league to check list visibility
    league = session.scalars(select(League).where(League.id == league_id)).first()

    players = list(
        session.scalars(
            select(LeaguePlayer).where(LeaguePlayer.league_id == league_id)
        ).all()
    )

    if not players:
        return []

    # Collect IDs for bulk fetching
    user_ids = {p.user_id for p in players if p.user_id}
    group_ids = {p.group_id for p in players if p.group_id}

    # Bulk fetch users (1 query instead of N)
    users = (
        session.scalars(select(User).where(User.id.in_(user_ids))).all()
        if user_ids
        else []
    )
    user_map = {u.id: u for u in users}

    # Bulk fetch groups (1 query instead of N)
    groups = (
        session.scalars(select(Group).where(Group.id.in_(group_ids))).all()
        if group_ids
        else []
    )
    group_map = {g.id: g for g in groups}

    result = []
    for player in players:
        # Get user from cache
        username = None
        avatar_url = None
        if player.user_id and player.user_id in user_map:
            user = user_map[player.user_id]
            username = user.username
            avatar_url = user.avatar_url

        # Get group from cache
        group_name = None
        if player.group_id and player.group_id in group_map:
            group_name = group_map[player.group_id].name

        # Include army lists only if visible
        group_army_list = None
        knockout_army_list = None
        if league:
            if league.group_lists_visible:
                group_army_list = player.group_army_list
            if league.knockout_lists_visible:
                knockout_army_list = player.knockout_army_list

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
                avatar_url=avatar_url,
                joined_at=player.joined_at,
                group_army_faction=player.group_army_faction,
                group_army_list=group_army_list,
                group_list_submitted=player.group_army_list is not None,
                knockout_army_faction=player.knockout_army_faction,
                knockout_army_list=knockout_army_list,
                knockout_list_submitted=player.knockout_army_list is not None,
            )
        )

    return result


@router.delete("/{league_id}/player/{player_id}", response_model=PlayerRemovalResponse)
async def remove_player(
    league_id: int,
    player_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_organizer),
):
    """
    Removes a player from a league (organizer).

    - During registration: simply removes the player
    - During group/knockout phase: removes player and awards walkovers (25:0, 1175 pts)
    - After finished: not allowed
    """
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

    if league.status == "finished":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="League has already finished",
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

    # Award walkovers during active phases (group or knockout)
    award_walkovers = league.status in ("group_phase", "knockout_phase")

    result = remove_player_from_league(session, player, award_walkovers=award_walkovers)

    return PlayerRemovalResponse(
        message="Player removed from league",
        deleted_matches=result["deleted_matches"],
        walkover_matches=result["walkover_matches"],
    )


@router.patch(
    "/{league_id}/player/{player_id}/group", response_model=ChangeGroupResponse
)
async def change_player_group_endpoint(
    league_id: int,
    player_id: int,
    data: ChangePlayerGroupRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_organizer),
):
    """
    Moves a player to a different group (organizer).

    Only available during group phase. Deletes old matches and creates new ones.
    """
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
            detail="Can only change groups during group phase",
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

    statement = select(Group).where(
        Group.id == data.group_id,
        Group.league_id == league_id,
    )
    new_group = session.scalars(statement).first()

    if not new_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target group not found",
        )

    if player.group_id == new_group.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Player is already in this group",
        )

    result = change_player_group(session, player, new_group)

    return ChangeGroupResponse(
        message=f"Player moved to {new_group.name}",
        deleted_matches=result["deleted_matches"],
        created_matches=result["created_matches"],
        new_group_id=new_group.id,
        new_group_name=new_group.name,
    )


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

    # Set match deadlines to phase end dates
    update_match_deadlines(session, league)

    return {
        "message": f"Created {len(groups)} groups with {len(matches)} matches",
        "groups": [{"id": g.id, "name": g.name} for g in groups],
        "group_phase_end": group_end.isoformat() if group_end else None,
        "knockout_phase_end": knockout_end.isoformat() if knockout_end else None,
    }


@router.patch("/{league_id}/groups/{group_id}", response_model=GroupResponse)
async def update_group(
    league_id: int,
    group_id: int,
    group_update: GroupUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Update group name (organizer only)."""
    league = session.scalars(select(League).where(League.id == league_id)).first()
    if not league:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="League not found",
        )

    if league.organizer_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the organizer can edit groups",
        )

    group = session.scalars(
        select(Group).where(Group.id == group_id, Group.league_id == league_id)
    ).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found",
        )

    group.name = group_update.name
    session.add(group)
    session.commit()
    session.refresh(group)

    return group


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

    # Sync match deadlines with new phase dates
    update_match_deadlines(session, league)

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
    """Gets standings for all groups with qualification info."""
    league = session.scalars(select(League).where(League.id == league_id)).first()
    if not league:
        return []

    statement = select(Group).where(Group.league_id == league_id)
    groups = list(session.scalars(statement).all())
    num_groups = len(groups)

    if num_groups == 0:
        return []

    # Calculate knockout qualification rules
    player_count = get_league_player_count(session, league_id)
    knockout_size = league.knockout_size
    if knockout_size is None:
        knockout_size = calculate_knockout_size(player_count)
    knockout_size = min(knockout_size, player_count)

    guaranteed_per_group = knockout_size // num_groups
    extra_spots = knockout_size % num_groups

    # First pass: collect all runners-up and all user_ids
    runners_up = []  # (player_id, total_points, games_played, average_points, group_id)
    group_standings_data = {}
    all_user_ids = set()

    for group in groups:
        players = get_group_standings(session, group.id)
        group_standings_data[group.id] = players

        # Collect user_ids for bulk fetching
        for player in players:
            if player.user_id:
                all_user_ids.add(player.user_id)

        # Collect runner-up (position after guaranteed spots)
        if extra_spots > 0 and len(players) > guaranteed_per_group:
            runner_up = players[guaranteed_per_group]
            runners_up.append(
                (
                    runner_up.id,
                    runner_up.total_points,
                    runner_up.games_played,
                    runner_up.average_points,
                    group.id,
                )
            )

    # Bulk fetch all users (1 query instead of N)
    users = (
        session.scalars(select(User).where(User.id.in_(all_user_ids))).all()
        if all_user_ids
        else []
    )
    user_map = {u.id: u for u in users}

    # Sort runners-up and find which ones qualify
    runners_up.sort(
        key=lambda r: (-r[1], r[2], -r[3])
    )  # points desc, games asc, avg desc
    qualifying_runner_up_ids = {r[0] for r in runners_up[:extra_spots]}

    # Second pass: build response with qualification flags
    result = []
    for group in groups:
        players = group_standings_data[group.id]

        standings = []
        for position, player in enumerate(players, 1):
            # Get user from cache
            username = None
            avatar_url = None
            if player.user_id and player.user_id in user_map:
                user = user_map[player.user_id]
                username = user.username
                avatar_url = user.avatar_url

            qualifies = position <= guaranteed_per_group
            qualifies_as_runner_up = (
                not qualifies and player.id in qualifying_runner_up_ids
            )

            # Show army faction and list based on phase
            army_faction = None
            army_list = None
            list_submitted = False
            if league.status == "knockout_phase":
                army_faction = player.knockout_army_faction
                list_submitted = player.knockout_army_list is not None
                if league.knockout_lists_visible:
                    army_list = player.knockout_army_list
            else:
                army_faction = player.group_army_faction
                list_submitted = player.group_army_list is not None
                if league.group_lists_visible:
                    army_list = player.group_army_list

            standings.append(
                StandingsEntry(
                    position=position,
                    player_id=player.id,
                    user_id=player.user_id,
                    username=username,
                    discord_username=player.discord_username,
                    avatar_url=avatar_url,
                    army_faction=army_faction,
                    army_list=army_list,
                    list_submitted=list_submitted,
                    games_played=player.games_played,
                    games_won=player.games_won,
                    games_drawn=player.games_drawn,
                    games_lost=player.games_lost,
                    total_points=player.total_points,
                    average_points=player.average_points,
                    qualifies=qualifies,
                    qualifies_as_runner_up=qualifies_as_runner_up,
                )
            )

        result.append(
            GroupStandings(
                group_id=group.id,
                group_name=group.name,
                standings=standings,
                qualifying_spots=guaranteed_per_group,
                runner_up_spots=extra_spots,
            )
        )

    return result


# ============ Matches ============


@router.get("/{league_id}/matches", response_model=list[MatchResponse])
async def list_matches(
    league_id: int,
    phase: str = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user_optional),
):
    """Lists matches in a league with army lists (if visible)."""
    # Get league for list visibility settings
    league = session.scalars(select(League).where(League.id == league_id)).first()

    # Auto-confirm matches pending for more than 24 hours
    if league and league.status not in ("finished",):
        auto_confirm_cutoff = datetime.utcnow() - timedelta(hours=24)
        pending_old = session.scalars(
            select(Match).where(
                Match.league_id == league_id,
                Match.status == "pending_confirmation",
                Match.submitted_at < auto_confirm_cutoff,
            )
        ).all()

        for match in pending_old:
            confirm_match_result(session, match, match.submitted_by_id)

    statement = select(Match).where(Match.league_id == league_id)
    if phase:
        statement = statement.where(Match.phase == phase)
    statement = statement.order_by(Match.created_at)

    matches = list(session.scalars(statement).all())

    if not matches:
        return []

    # Collect all player IDs needed
    player_ids = set()
    for match in matches:
        if match.player1_id:
            player_ids.add(match.player1_id)
        if match.player2_id:
            player_ids.add(match.player2_id)

    # Bulk fetch all LeaguePlayers (1 query instead of 2N)
    players = session.scalars(
        select(LeaguePlayer).where(LeaguePlayer.id.in_(player_ids))
    ).all()
    player_map = {p.id: p for p in players}

    # Collect user IDs and group IDs
    user_ids = {p.user_id for p in players if p.user_id}
    group_ids = {p.group_id for p in players if p.group_id}

    # Bulk fetch all Users (1 query instead of 2N)
    users = (
        session.scalars(select(User).where(User.id.in_(user_ids))).all()
        if user_ids
        else []
    )
    user_map = {u.id: u for u in users}

    # Bulk fetch all Groups (1 query instead of N)
    groups = (
        session.scalars(select(Group).where(Group.id.in_(group_ids))).all()
        if group_ids
        else []
    )
    group_map = {g.id: g for g in groups}

    result = []
    for match in matches:
        p1 = player_map.get(match.player1_id)
        p2 = player_map.get(match.player2_id)

        # Get usernames and avatars from cached data
        p1_username = None
        p1_avatar = None
        if p1:
            if p1.user_id and p1.user_id in user_map:
                user1 = user_map[p1.user_id]
                p1_username = user1.username
                p1_avatar = user1.avatar_url
            else:
                p1_username = p1.discord_username

        p2_username = None
        p2_avatar = None
        if p2:
            if p2.user_id and p2.user_id in user_map:
                user2 = user_map[p2.user_id]
                p2_username = user2.username
                p2_avatar = user2.avatar_url
            else:
                p2_username = p2.discord_username

        # Get army faction based on match phase
        if match.phase == "group":
            p1_army_faction = p1.group_army_faction if p1 else None
            p2_army_faction = p2.group_army_faction if p2 else None
        else:
            p1_army_faction = p1.knockout_army_faction if p1 else None
            p2_army_faction = p2.knockout_army_faction if p2 else None

        # Determine army list visibility (only when revealed)
        p1_army_list = None
        p2_army_list = None
        if league:
            if match.phase == "group" and league.group_lists_visible:
                p1_army_list = p1.group_army_list if p1 else None
                p2_army_list = p2.group_army_list if p2 else None
            elif match.phase == "knockout" and league.knockout_lists_visible:
                p1_army_list = p1.knockout_army_list if p1 else None
                p2_army_list = p2.knockout_army_list if p2 else None

        # Get group info from cached data
        group_id = None
        group_name = None
        if p1 and p1.group_id and p1.group_id in group_map:
            group_id = p1.group_id
            group_name = group_map[p1.group_id].name

        # Per-match army lists (blind exchange)
        match_p1_list = None
        match_p2_list = None
        match_p1_faction = None
        match_p2_faction = None
        if match.lists_revealed:
            match_p1_list = match.player1_army_list
            match_p2_list = match.player2_army_list
            match_p1_faction = match.player1_army_faction
            match_p2_faction = match.player2_army_faction

        final_p1_list = match_p1_list if match_p1_list else p1_army_list
        final_p2_list = match_p2_list if match_p2_list else p2_army_list
        final_p1_faction = match_p1_faction if match_p1_faction else p1_army_faction
        final_p2_faction = match_p2_faction if match_p2_faction else p2_army_faction

        # Determine if player has submitted a list
        if match.phase == "knockout":
            p1_has_league_list = (
                league
                and league.has_knockout_phase_lists
                and p1
                and p1.knockout_army_list
            )
            p2_has_league_list = (
                league
                and league.has_knockout_phase_lists
                and p2
                and p2.knockout_army_list
            )
        else:
            p1_has_league_list = (
                league and league.has_group_phase_lists and p1 and p1.group_army_list
            )
            p2_has_league_list = (
                league and league.has_group_phase_lists and p2 and p2.group_army_list
            )

        p1_list_submitted = bool(match.player1_army_list) or bool(p1_has_league_list)
        p2_list_submitted = bool(match.player2_army_list) or bool(p2_has_league_list)

        lists_are_revealed = match.lists_revealed
        if not lists_are_revealed and league:
            if match.phase == "knockout" and league.knockout_lists_visible:
                lists_are_revealed = True
            elif match.phase == "group" and league.group_lists_visible:
                lists_are_revealed = True

        result.append(
            MatchResponse(
                id=match.id,
                league_id=match.league_id,
                player1_id=match.player1_id,
                player2_id=match.player2_id,
                player1_user_id=p1.user_id if p1 else None,
                player2_user_id=p2.user_id if p2 else None,
                player1_username=p1_username,
                player2_username=p2_username,
                player1_avatar=p1_avatar,
                player2_avatar=p2_avatar,
                player1_army_faction=final_p1_faction,
                player2_army_faction=final_p2_faction,
                group_id=group_id,
                group_name=group_name,
                phase=match.phase,
                knockout_round=match.knockout_round,
                player1_score=match.player1_score,
                player2_score=match.player2_score,
                player1_league_points=match.player1_league_points,
                player2_league_points=match.player2_league_points,
                status=match.status,
                deadline=match.deadline,
                map_name=match.map_name,
                submitted_by_id=match.submitted_by_id,
                created_at=match.created_at,
                is_completed=match.is_completed,
                player1_army_list=final_p1_list,
                player2_army_list=final_p2_list,
                player1_list_submitted=p1_list_submitted,
                player2_list_submitted=p2_list_submitted,
                lists_revealed=lists_are_revealed,
                lists_revealed_at=match.lists_revealed_at,
            )
        )

    return result


@router.get("/{league_id}/matches/{match_id}", response_model=MatchDetailResponse)
async def get_match_detail(
    league_id: int,
    match_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user_optional),
):
    """Gets detailed match information including ELO changes."""
    match = session.scalars(
        select(Match).where(Match.id == match_id, Match.league_id == league_id)
    ).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    league = session.scalars(select(League).where(League.id == league_id)).first()

    # Get player info
    player1 = session.scalars(
        select(LeaguePlayer).where(LeaguePlayer.id == match.player1_id)
    ).first()
    player2 = session.scalars(
        select(LeaguePlayer).where(LeaguePlayer.id == match.player2_id)
    ).first()

    # Get usernames and avatars
    p1_username = None
    p2_username = None
    p1_avatar = None
    p2_avatar = None
    u1 = None
    u2 = None
    if player1 and player1.user_id:
        u1 = session.scalars(select(User).where(User.id == player1.user_id)).first()
        if u1:
            p1_username = u1.username
            p1_avatar = u1.avatar_url
        else:
            p1_username = player1.discord_username
    elif player1:
        p1_username = player1.discord_username
    if player2 and player2.user_id:
        u2 = session.scalars(select(User).where(User.id == player2.user_id)).first()
        if u2:
            p2_username = u2.username
            p2_avatar = u2.avatar_url
        else:
            p2_username = player2.discord_username
    elif player2:
        p2_username = player2.discord_username

    # Get group name
    group_name = None
    if player1 and player1.group_id:
        group = session.scalars(
            select(Group).where(Group.id == player1.group_id)
        ).first()
        if group:
            group_name = group.name

    # Determine army faction and list based on phase
    p1_army_faction = None
    p2_army_faction = None
    p1_army_list = None
    p2_army_list = None
    if player1 and player2:
        if match.phase == "knockout":
            p1_army_faction = player1.knockout_army_faction
            p2_army_faction = player2.knockout_army_faction
            # Show lists if visible or user is participant/org
            if league.knockout_lists_visible or (
                current_user
                and (
                    current_user.id == player1.user_id
                    or current_user.id == player2.user_id
                    or current_user.id == league.organizer_id
                    or current_user.role == "admin"
                )
            ):
                p1_army_list = player1.knockout_army_list
                p2_army_list = player2.knockout_army_list
        else:
            p1_army_faction = player1.group_army_faction
            p2_army_faction = player2.group_army_faction
            if league.group_lists_visible or (
                current_user
                and (
                    current_user.id == player1.user_id
                    or current_user.id == player2.user_id
                    or current_user.id == league.organizer_id
                    or current_user.role == "admin"
                )
            ):
                p1_army_list = player1.group_army_list
                p2_army_list = player2.group_army_list

    # Determine permissions
    is_participant = bool(
        current_user
        and player1
        and player2
        and (current_user.id == player1.user_id or current_user.id == player2.user_id)
    )
    is_org_or_admin = bool(
        current_user
        and (current_user.id == league.organizer_id or current_user.role == "admin")
    )
    can_edit = (is_participant or is_org_or_admin) and match.status != "confirmed"
    # Only organizer can CHANGE map after it's been auto-assigned (for corrections)
    # Map is auto-assigned when both players submit their lists - no manual selection allowed
    can_set_map = (
        is_org_or_admin and match.map_name is not None and match.status != "confirmed"
    )

    # Per-match army lists allowed only if league doesn't require them for this phase
    # If lists are required, they come from player profile, not per-match submission
    if match.phase == "knockout":
        lists_required_for_phase = league.has_knockout_phase_lists
        p1_has_league_list = (
            lists_required_for_phase and player1 and player1.knockout_army_list
        )
        p2_has_league_list = (
            lists_required_for_phase and player2 and player2.knockout_army_list
        )
    else:
        lists_required_for_phase = league.has_group_phase_lists
        p1_has_league_list = (
            lists_required_for_phase and player1 and player1.group_army_list
        )
        p2_has_league_list = (
            lists_required_for_phase and player2 and player2.group_army_list
        )
    can_submit_army_list = not lists_required_for_phase

    # Player has list if per-match submitted OR league-required list exists
    p1_list_submitted = bool(match.player1_army_list) or bool(p1_has_league_list)
    p2_list_submitted = bool(match.player2_army_list) or bool(p2_has_league_list)

    # Lists are revealed if per-match lists revealed OR if league lists are visible
    lists_are_revealed = match.lists_revealed
    if not lists_are_revealed:
        if match.phase == "knockout" and league.knockout_lists_visible:
            lists_are_revealed = True
        elif match.phase == "group" and league.group_lists_visible:
            lists_are_revealed = True

    # Per-match lists - use them if revealed, otherwise use league lists
    final_p1_list = match.player1_army_list if match.lists_revealed else p1_army_list
    final_p2_list = match.player2_army_list if match.lists_revealed else p2_army_list
    final_p1_faction = (
        match.player1_army_faction
        if match.lists_revealed and match.player1_army_faction
        else p1_army_faction
    )
    final_p2_faction = (
        match.player2_army_faction
        if match.lists_revealed and match.player2_army_faction
        else p2_army_faction
    )

    return MatchDetailResponse(
        id=match.id,
        league_id=match.league_id,
        league_name=league.name,
        player1_id=match.player1_id,
        player2_id=match.player2_id,
        player1_user_id=player1.user_id if player1 else None,
        player2_user_id=player2.user_id if player2 else None,
        player1_username=p1_username,
        player2_username=p2_username,
        player1_avatar=p1_avatar,
        player2_avatar=p2_avatar,
        player1_army_faction=final_p1_faction,
        player2_army_faction=final_p2_faction,
        player1_army_list=final_p1_list,
        player2_army_list=final_p2_list,
        player1_list_submitted=p1_list_submitted,
        player2_list_submitted=p2_list_submitted,
        lists_revealed=lists_are_revealed,
        lists_revealed_at=match.lists_revealed_at,
        phase=match.phase,
        knockout_round=match.knockout_round,
        group_name=group_name,
        player1_score=match.player1_score,
        player2_score=match.player2_score,
        player1_league_points=match.player1_league_points,
        player2_league_points=match.player2_league_points,
        status=match.status,
        map_name=match.map_name,
        deadline=match.deadline,
        player1_elo_before=match.player1_elo_before,
        player1_elo_after=match.player1_elo_after,
        player2_elo_before=match.player2_elo_before,
        player2_elo_after=match.player2_elo_after,
        submitted_by_id=match.submitted_by_id,
        submitted_at=match.submitted_at,
        confirmed_by_id=match.confirmed_by_id,
        confirmed_at=match.confirmed_at,
        created_at=match.created_at,
        can_edit=can_edit,
        can_set_map=can_set_map,
        can_submit_army_list=can_submit_army_list,
        points_per_win=league.points_per_win,
        points_per_draw=league.points_per_draw,
        points_per_loss=league.points_per_loss,
    )


@router.post("/{league_id}/matches/{match_id}/map")
async def set_match_map(
    league_id: int,
    match_id: int,
    data: MatchMapSet,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Sets or randomizes the map for a match (participants or organizer)."""
    match = session.scalars(
        select(Match).where(Match.id == match_id, Match.league_id == league_id)
    ).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    league = session.scalars(select(League).where(League.id == league_id)).first()

    # Get players
    player1 = session.scalars(
        select(LeaguePlayer).where(LeaguePlayer.id == match.player1_id)
    ).first()
    player2 = session.scalars(
        select(LeaguePlayer).where(LeaguePlayer.id == match.player2_id)
    ).first()

    # Check permissions
    is_participant = (
        player1
        and player2
        and (current_user.id == player1.user_id or current_user.id == player2.user_id)
    )
    is_org_or_admin = (
        current_user.id == league.organizer_id or current_user.role == "admin"
    )

    if not is_participant and not is_org_or_admin:
        raise HTTPException(
            status_code=403, detail="Only participants or organizer can set the map"
        )

    # Cannot change map if match is confirmed
    if match.status == "confirmed":
        raise HTTPException(
            status_code=400, detail="Cannot change map for confirmed match"
        )

    # Cannot change map if league is finished
    if league.status == "finished":
        raise HTTPException(
            status_code=400, detail="Cannot modify matches in a finished league"
        )

    # Set map
    if data.random:
        match.map_name = random.choice(MISSION_MAPS)
    elif data.map_name:
        match.map_name = data.map_name
    else:
        raise HTTPException(
            status_code=400, detail="Provide map_name or set random=true"
        )

    session.add(match)
    session.commit()

    return {"map_name": match.map_name}


@router.post("/{league_id}/matches/{match_id}/army-list")
async def submit_match_army_list(
    league_id: int,
    match_id: int,
    data: MatchArmyListSubmit,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Submit army list for a match (blind exchange like matchups)."""
    # Get match
    statement = select(Match).where(
        Match.id == match_id,
        Match.league_id == league_id,
    )
    match = session.scalars(statement).first()

    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    # Get league to check list settings
    league = session.get(League, league_id)
    if not league:
        raise HTTPException(status_code=404, detail="League not found")

    # Get player info
    player1 = session.get(LeaguePlayer, match.player1_id)
    player2 = session.get(LeaguePlayer, match.player2_id)

    # Check if current user is one of the players
    is_player1 = player1 and player1.user_id == current_user.id
    is_player2 = player2 and player2.user_id == current_user.id

    if not is_player1 and not is_player2:
        raise HTTPException(
            status_code=403, detail="You are not a participant in this match"
        )

    # Check if match is completed - can't submit lists after
    if match.status == "confirmed":
        raise HTTPException(
            status_code=400, detail="Cannot submit list for completed match"
        )

    # Auto-detect faction if not provided
    army_faction = data.army_faction
    if not army_faction:
        from app.matchup.constants import detect_army_faction

        army_faction = detect_army_faction(data.army_list)

    # Determine which player's list to update
    if is_player1:
        if match.player1_army_list is not None:
            raise HTTPException(
                status_code=400, detail="You have already submitted your list"
            )
        match.player1_army_list = data.army_list
        match.player1_army_faction = army_faction
        match.player1_list_submitted_at = datetime.utcnow()
    else:
        if match.player2_army_list is not None:
            raise HTTPException(
                status_code=400, detail="You have already submitted your list"
            )
        match.player2_army_list = data.army_list
        match.player2_army_faction = army_faction
        match.player2_list_submitted_at = datetime.utcnow()

    # Check if both lists are now submitted - reveal and assign map
    if match.both_lists_submitted and not match.lists_revealed_at:
        match.lists_revealed_at = datetime.utcnow()
        # Assign random map if not already set
        if not match.map_name:
            import random

            from app.league.constants import MISSION_MAPS

            match.map_name = random.choice(MISSION_MAPS)

    session.add(match)
    session.commit()
    session.refresh(match)

    return {
        "message": "Army list submitted",
        "lists_revealed": match.lists_revealed,
        "map_name": match.map_name if match.lists_revealed else None,
    }


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

    # Check league status
    league_stmt = select(League).where(League.id == league_id)
    league_check = session.scalars(league_stmt).first()
    if league_check and league_check.status == "finished":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot modify results in a finished league",
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
    """Confirms a match result. Only organizer or admin can confirm."""
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
            detail="Match is already confirmed",
        )

    if match.player1_score is None or match.player2_score is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot confirm match without scores",
        )

    stmt = select(League).where(League.id == league_id)
    league = session.scalars(stmt).first()

    # Check league status
    if league and league.status == "finished":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot modify results in a finished league",
        )

    # Get players to check if current user is the opponent
    stmt = select(LeaguePlayer).where(LeaguePlayer.id == match.player1_id)
    p1 = session.scalars(stmt).first()
    stmt = select(LeaguePlayer).where(LeaguePlayer.id == match.player2_id)
    p2 = session.scalars(stmt).first()

    is_organizer = league and league.organizer_id == current_user.id
    is_admin = current_user.role == "admin"

    # Check if current user is the opponent (not the one who submitted)
    is_opponent = False
    if match.submitted_by_id:
        if (
            p1
            and p1.user_id == match.submitted_by_id
            and p2
            and p2.user_id == current_user.id
        ):
            is_opponent = True
        elif (
            p2
            and p2.user_id == match.submitted_by_id
            and p1
            and p1.user_id == current_user.id
        ):
            is_opponent = True

    if not (is_opponent or is_organizer or is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only opponent, organizer or admin can confirm matches",
        )

    confirm_match_result(session, match, current_user.id)

    return {"message": "Result confirmed"}


@router.post("/{league_id}/matches/{match_id}/unlock")
async def unlock_result(
    league_id: int,
    match_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Unlocks a confirmed match result (organizer or admin only)."""
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

    if match.status != "confirmed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Match is not confirmed",
        )

    stmt = select(League).where(League.id == league_id)
    league = session.scalars(stmt).first()

    is_organizer = league and league.organizer_id == current_user.id
    is_admin = current_user.role == "admin"

    if not (is_organizer or is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organizer or admin can unlock matches",
        )

    match.status = "pending_confirmation"
    match.confirmed_by_id = None
    match.confirmed_at = None
    session.add(match)
    session.commit()

    return {"message": "Match unlocked for editing"}


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

    # Determine the first round based on knockout size
    player_count = get_league_player_count(session, league_id)
    knockout_size = league.knockout_size or len(matches) * 2
    rounds = get_knockout_round_names(knockout_size)
    first_round = rounds[0] if rounds else "final"

    league.status = "knockout_phase"
    league.current_knockout_round = first_round
    league.group_phase_end = datetime.utcnow()
    league.knockout_phase_start = datetime.utcnow()
    session.add(league)
    session.commit()

    return {
        "message": f"Started knockout phase with {len(matches)} matches",
        "qualified_count": len(matches) * 2,
        "current_round": first_round,
    }


@router.post("/{league_id}/advance-knockout")
async def advance_knockout(
    league_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_organizer),
):
    """Advances to the next knockout round (organizer). All current round matches must be confirmed."""
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

    if league.status != "knockout_phase":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="League is not in knockout phase",
        )

    if not league.current_knockout_round:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No current knockout round set",
        )

    # Check if all matches in current round are confirmed
    if not all_round_matches_confirmed(
        session, league.id, league.current_knockout_round
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="All matches in current round must be confirmed before advancing",
        )

    # Check if we're at the final
    next_round = get_next_knockout_round(league.current_knockout_round)
    if not next_round:
        # Final is complete, finish league
        league.status = "finished"
        league.knockout_phase_end = datetime.utcnow()
        league.finished_at = datetime.utcnow()
        session.add(league)
        session.commit()
        return {
            "message": "Knockout phase complete! League finished.",
            "finished": True,
        }

    # Advance to next round
    new_round, matches = advance_to_next_knockout_round(session, league)

    if not new_round:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to advance to next round",
        )

    return {
        "message": f"Advanced to {new_round}",
        "current_round": new_round,
        "matches_created": len(matches),
        "finished": False,
    }


# ============ Group Phase Lists ============


@router.post("/{league_id}/group-list")
async def submit_group_list(
    league_id: int,
    data: ArmyListSubmit,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Submits army list for group phase (before league starts)."""
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

    league = session.scalars(select(League).where(League.id == league_id)).first()

    if not league or not league.has_group_phase_lists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This league does not have group phase lists",
        )

    if league.group_lists_frozen:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Group lists are frozen, cannot submit or edit",
        )

    # Lists must be submitted before league starts (during registration)
    if league.status != "registration":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Group lists can only be submitted during registration",
        )

    player.group_army_faction = data.army_faction
    player.group_army_list = data.army_list
    player.group_list_submitted_at = datetime.utcnow()
    session.add(player)
    session.commit()

    return {"message": "Group list submitted"}


@router.get("/{league_id}/group-list/{player_id}", response_model=ArmyListResponse)
async def get_group_list(
    league_id: int,
    player_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user_optional),
):
    """Gets player's group phase army list (if visible)."""
    league = session.scalars(select(League).where(League.id == league_id)).first()

    if not league:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="League not found",
        )

    player = session.scalars(
        select(LeaguePlayer).where(LeaguePlayer.id == player_id)
    ).first()

    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found",
        )

    # Check visibility - only own list or when revealed
    is_own = current_user and player.user_id == current_user.id

    if not is_own and not league.group_lists_visible:
        return ArmyListResponse(
            player_id=player.id,
            username=None,
            army_faction=None,
            army_list=None,
            submitted_at=None,
        )

    username = None
    if player.user_id:
        user = session.scalars(select(User).where(User.id == player.user_id)).first()
        username = user.username if user else player.discord_username
    else:
        username = player.discord_username

    return ArmyListResponse(
        player_id=player.id,
        username=username,
        army_faction=player.group_army_faction,
        army_list=player.group_army_list,
        submitted_at=player.group_list_submitted_at,
    )


@router.post("/{league_id}/freeze-group-lists")
async def freeze_group_lists(
    league_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_organizer),
):
    """Freezes group phase army lists (organizer). No more player edits."""
    league = session.scalars(select(League).where(League.id == league_id)).first()

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

    league.group_lists_frozen = True
    session.add(league)
    session.commit()

    return {"message": "Group lists are now frozen"}


@router.post("/{league_id}/unfreeze-group-lists")
async def unfreeze_group_lists(
    league_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_organizer),
):
    """Unfreezes group phase army lists (organizer). Players can edit again, lists hidden."""
    league = session.scalars(select(League).where(League.id == league_id)).first()

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

    league.group_lists_frozen = False
    league.group_lists_visible = False  # Hide lists when unfreezing
    session.add(league)
    session.commit()

    return {"message": "Group lists are now unfrozen and hidden"}


@router.post("/{league_id}/reveal-group-lists")
async def reveal_group_lists(
    league_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_organizer),
):
    """Reveals group phase army lists (organizer). Also freezes them."""
    league = session.scalars(select(League).where(League.id == league_id)).first()

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

    league.group_lists_visible = True
    league.group_lists_frozen = True
    session.add(league)
    session.commit()

    return {"message": "Group lists are now visible"}


@router.put("/{league_id}/group-list/{player_id}")
async def edit_group_list_organizer(
    league_id: int,
    player_id: int,
    data: ArmyListSubmit,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_organizer),
):
    """Edits player's group list (organizer only, even after freeze)."""
    league = session.scalars(select(League).where(League.id == league_id)).first()

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

    player = session.scalars(
        select(LeaguePlayer).where(
            LeaguePlayer.id == player_id, LeaguePlayer.league_id == league_id
        )
    ).first()

    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found",
        )

    player.group_army_faction = data.army_faction
    player.group_army_list = data.army_list
    player.group_list_submitted_at = datetime.utcnow()
    session.add(player)
    session.commit()

    return {"message": "Group list updated"}


# ============ Knockout Phase Lists ============


@router.post("/{league_id}/freeze-lists")
async def freeze_knockout_lists(
    league_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_organizer),
):
    """Freezes knockout phase army lists (organizer). No more edits allowed."""
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

    if league.knockout_lists_frozen:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Lists are already frozen",
        )

    league.knockout_lists_frozen = True
    session.add(league)
    session.commit()

    return {"message": "Knockout lists are now frozen"}


@router.post("/{league_id}/unfreeze-lists")
async def unfreeze_knockout_lists(
    league_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_organizer),
):
    """Unfreezes knockout phase army lists (organizer). Players can edit again, lists hidden."""
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

    league.knockout_lists_frozen = False
    league.knockout_lists_visible = False  # Hide lists when unfreezing
    session.add(league)
    session.commit()

    return {"message": "Knockout lists are now unfrozen and hidden"}


@router.post("/{league_id}/reveal-lists")
async def reveal_knockout_lists(
    league_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_organizer),
):
    """Reveals knockout phase army lists (organizer). Also freezes them if not already."""
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
    league.knockout_lists_frozen = True  # Revealing also freezes
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

    if league and league.knockout_lists_frozen:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Lists are frozen, cannot submit or edit",
        )

    player.knockout_army_faction = data.army_faction
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

    # Only owner can see before reveal
    if not league.knockout_lists_visible and not is_owner:
        return KnockoutListResponse(
            player_id=player.id,
            username=None,
            army_faction=None,
            army_list=None,
            submitted_at=None,
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
        army_faction=player.knockout_army_faction,
        army_list=player.knockout_army_list,
        submitted_at=player.knockout_list_submitted_at,
    )


@router.put("/{league_id}/knockout-list/{player_id}")
async def edit_knockout_list_organizer(
    league_id: int,
    player_id: int,
    data: ArmyListSubmit,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_organizer),
):
    """Edits player's knockout list (organizer only, even after freeze)."""
    league = session.scalars(select(League).where(League.id == league_id)).first()

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

    player = session.scalars(
        select(LeaguePlayer).where(
            LeaguePlayer.id == player_id, LeaguePlayer.league_id == league_id
        )
    ).first()

    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found",
        )

    player.knockout_army_faction = data.army_faction
    player.knockout_army_list = data.army_list
    player.knockout_list_submitted_at = datetime.utcnow()
    session.add(player)
    session.commit()

    return {"message": "Knockout list updated"}


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


# ============ Voting ============


@router.post(
    "/{league_id}/vote-categories",
    response_model=VoteCategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_vote_category_endpoint(
    league_id: int,
    data: VoteCategoryCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_organizer),
):
    """Creates a vote category for a league (organizer only)."""
    league = session.scalars(select(League).where(League.id == league_id)).first()

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

    if not league.voting_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Voting is not enabled for this league",
        )

    category = create_vote_category(session, league_id, data.name, data.description)

    return VoteCategoryResponse(
        id=category.id,
        league_id=category.league_id,
        name=category.name,
        description=category.description,
        winner_id=category.winner_id,
        winner_username=None,
        created_at=category.created_at,
    )


@router.get("/{league_id}/vote-categories", response_model=list[VoteCategoryResponse])
async def list_vote_categories(
    league_id: int,
    session: Session = Depends(get_session),
):
    """Gets all vote categories for a league."""
    categories = session.scalars(
        select(VoteCategory).where(VoteCategory.league_id == league_id)
    ).all()

    result = []
    for category in categories:
        winner_username = None
        if category.winner_id:
            winner_player = session.get(LeaguePlayer, category.winner_id)
            if winner_player and winner_player.user_id:
                winner_user = session.get(User, winner_player.user_id)
                if winner_user:
                    winner_username = winner_user.username
            elif winner_player:
                winner_username = winner_player.discord_username

        result.append(
            VoteCategoryResponse(
                id=category.id,
                league_id=category.league_id,
                name=category.name,
                description=category.description,
                winner_id=category.winner_id,
                winner_username=winner_username,
                created_at=category.created_at,
            )
        )

    return result


@router.post(
    "/{league_id}/vote-categories/{category_id}/vote",
    response_model=VoteResponse,
    status_code=status.HTTP_201_CREATED,
)
async def cast_vote_endpoint(
    league_id: int,
    category_id: int,
    data: VoteCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Casts a vote in a category (league player only, not for self)."""
    league = session.scalars(select(League).where(League.id == league_id)).first()

    if not league:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="League not found",
        )

    # Check voting is enabled
    if not league.voting_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Voting is not enabled for this league",
        )

    # Check league is finished
    if league.status != "finished":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Voting is only available after the league finishes",
        )

    # Check voting is still open
    if league.voting_closed_at is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Voting is closed",
        )

    # Check category exists and belongs to this league
    category = session.scalars(
        select(VoteCategory).where(
            VoteCategory.id == category_id,
            VoteCategory.league_id == league_id,
        )
    ).first()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vote category not found",
        )

    # Check current user is a league player
    voter_player = session.scalars(
        select(LeaguePlayer).where(
            LeaguePlayer.league_id == league_id,
            LeaguePlayer.user_id == current_user.id,
        )
    ).first()

    if not voter_player:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only league players can vote",
        )

    # Check not voting for self
    if voter_player.id == data.voted_for_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot vote for yourself",
        )

    # Check voted_for player exists in this league
    voted_for_player = session.scalars(
        select(LeaguePlayer).where(
            LeaguePlayer.id == data.voted_for_id,
            LeaguePlayer.league_id == league_id,
        )
    ).first()

    if not voted_for_player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player to vote for not found in this league",
        )

    # Check hasn't voted already
    existing_vote = get_player_vote(session, category_id, voter_player.id)
    if existing_vote:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already voted in this category",
        )

    vote = cast_vote(session, category_id, voter_player.id, data.voted_for_id)

    return VoteResponse(
        id=vote.id,
        category_id=vote.category_id,
        voter_id=vote.voter_id,
        voted_for_id=vote.voted_for_id,
        created_at=vote.created_at,
    )


@router.get(
    "/{league_id}/vote-categories/{category_id}/results",
    response_model=VotingResultsResponse,
)
async def get_voting_results_endpoint(
    league_id: int,
    category_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user_optional),
):
    """
    Gets voting results for a category.

    - If voting closed: shows full results with counts
    - If voting open and user is organizer: shows counts as preliminary
    - If voting open and user is player: only shows if they voted
    """
    league = session.scalars(select(League).where(League.id == league_id)).first()

    if not league:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="League not found",
        )

    category = session.scalars(
        select(VoteCategory).where(
            VoteCategory.id == category_id,
            VoteCategory.league_id == league_id,
        )
    ).first()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vote category not found",
        )

    # Get results
    results_data = get_voting_results(session, category_id)

    # Check if user can see results
    is_organizer = bool(
        current_user
        and (current_user.id == league.organizer_id or current_user.role == "admin")
    )
    voting_closed = league.voting_closed_at is not None

    # If voting not closed and not organizer, check if user voted
    if not voting_closed and not is_organizer:
        if current_user:
            player = session.scalars(
                select(LeaguePlayer).where(
                    LeaguePlayer.league_id == league_id,
                    LeaguePlayer.user_id == current_user.id,
                )
            ).first()

            if player:
                user_vote = get_player_vote(session, category_id, player.id)
                if not user_vote:
                    # User hasn't voted, hide detailed results but show vote count
                    return VotingResultsResponse(
                        category_id=category.id,
                        category_name=category.name,
                        results=[],
                        winner_id=None,
                        winner_username=None,
                        is_tied=False,
                        total_votes=results_data["total_votes"],
                    )
        else:
            # Anonymous user, hide detailed results but show vote count
            return VotingResultsResponse(
                category_id=category.id,
                category_name=category.name,
                results=[],
                winner_id=None,
                winner_username=None,
                is_tied=False,
                total_votes=results_data["total_votes"],
            )

    # Build full results with usernames
    results_with_info = []
    for entry in results_data["results"]:
        player = session.get(LeaguePlayer, entry["player_id"])
        username = None
        avatar_url = None
        if player:
            if player.user_id:
                user = session.get(User, player.user_id)
                if user:
                    username = user.username
                    avatar_url = user.avatar_url
            else:
                username = player.discord_username

        results_with_info.append(
            VoteResultEntry(
                player_id=entry["player_id"],
                username=username,
                avatar_url=avatar_url,
                vote_count=entry["vote_count"],
            )
        )

    # Get winner username
    winner_username = None
    if category.winner_id:
        winner_player = session.get(LeaguePlayer, category.winner_id)
        if winner_player and winner_player.user_id:
            winner_user = session.get(User, winner_player.user_id)
            if winner_user:
                winner_username = winner_user.username
        elif winner_player:
            winner_username = winner_player.discord_username

    return VotingResultsResponse(
        category_id=category.id,
        category_name=category.name,
        results=results_with_info,
        winner_id=category.winner_id,
        winner_username=winner_username,
        is_tied=results_data["is_tied"],
        total_votes=results_data["total_votes"],
    )


@router.post("/{league_id}/close-voting")
async def close_voting_endpoint(
    league_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_organizer),
):
    """Closes voting and determines winners (organizer only)."""
    league = session.scalars(select(League).where(League.id == league_id)).first()

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

    if not league.voting_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Voting is not enabled for this league",
        )

    if league.voting_closed_at is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Voting is already closed",
        )

    result = close_voting(session, league)

    return {
        "message": "Voting closed",
        "voting_closed_at": league.voting_closed_at.isoformat(),
        "categories": result["categories"],
    }


@router.post("/{league_id}/vote-categories/{category_id}/break-tie")
async def break_tie_endpoint(
    league_id: int,
    category_id: int,
    data: TieBreakerRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_organizer),
):
    """Randomly selects a winner from tied players (organizer only)."""
    league = session.scalars(select(League).where(League.id == league_id)).first()

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

    category = session.scalars(
        select(VoteCategory).where(
            VoteCategory.id == category_id,
            VoteCategory.league_id == league_id,
        )
    ).first()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vote category not found",
        )

    if category.winner_id is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Winner already selected for this category",
        )

    # Verify the players are actually tied
    results = get_voting_results(session, category_id)
    if not results["is_tied"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="There is no tie to break",
        )

    # Verify all provided player_ids are in the top tied positions
    top_vote_count = results["results"][0]["vote_count"] if results["results"] else 0
    tied_player_ids = {
        r["player_id"] for r in results["results"] if r["vote_count"] == top_vote_count
    }

    for pid in data.player_ids:
        if pid not in tied_player_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Player {pid} is not in the tie",
            )

    winner_id = break_tie_random(session, category, data.player_ids)

    # Get winner username
    winner_player = session.get(LeaguePlayer, winner_id)
    winner_username = None
    if winner_player and winner_player.user_id:
        winner_user = session.get(User, winner_player.user_id)
        if winner_user:
            winner_username = winner_user.username
    elif winner_player:
        winner_username = winner_player.discord_username

    return {
        "message": "Tie broken",
        "winner_id": winner_id,
        "winner_username": winner_username,
    }


@router.post("/{league_id}/enable-voting")
async def enable_voting_endpoint(
    league_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_organizer),
):
    """Enables voting for a league and creates the default category (organizer only)."""
    league = session.scalars(select(League).where(League.id == league_id)).first()

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

    if league.voting_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Voting is already enabled",
        )

    category = enable_voting_for_league(session, league)

    return {
        "message": "Voting enabled",
        "voting_enabled": True,
        "default_category": (
            {
                "id": category.id,
                "name": category.name,
                "description": category.description,
            }
            if category
            else None
        ),
    }
