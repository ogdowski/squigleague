"""Endpointy API dla modulu league."""

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
    confirm_match_result,
    draw_groups,
    generate_group_matches,
    generate_knockout_matches,
    get_group_standings,
    get_league_player_count,
    get_qualified_players,
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
    """Tworzy nowa lige (tylko organizer+)."""
    league = League(
        name=data.name,
        description=data.description,
        organizer_id=current_user.id,
        registration_start=data.registration_start,
        registration_end=data.registration_end,
        points_per_win=data.points_per_win,
        points_per_draw=data.points_per_draw,
        points_per_loss=data.points_per_loss,
    )
    session.add(league)
    session.commit()
    session.refresh(league)

    return LeagueResponse(
        **league.__dict__,
        player_count=0,
        is_registration_open=league.is_registration_open,
    )


@router.get("", response_model=list[LeagueListResponse])
async def list_leagues(
    session: Session = Depends(get_session),
):
    """Lista wszystkich lig."""
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
    """Pobiera szczegoly ligi."""
    statement = select(League).where(League.id == league_id)
    league = session.scalars(statement).first()

    if not league:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="League not found",
        )

    player_count = get_league_player_count(session, league_id)

    return LeagueResponse(
        **league.__dict__,
        player_count=player_count,
        is_registration_open=league.is_registration_open,
    )


@router.patch("/{league_id}", response_model=LeagueResponse)
async def update_league(
    league_id: int,
    data: LeagueUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_organizer),
):
    """Aktualizuje lige (tylko organizer ligi lub admin)."""
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

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(league, key, value)

    session.add(league)
    session.commit()
    session.refresh(league)

    player_count = get_league_player_count(session, league_id)

    return LeagueResponse(
        **league.__dict__,
        player_count=player_count,
        is_registration_open=league.is_registration_open,
    )


@router.delete("/{league_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_league(
    league_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_admin),
):
    """Usuwa lige (tylko admin)."""
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
    """Dolacza do ligi (przed rozpoczeciem)."""
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
    """Dodaje gracza recznie (organizer)."""
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
    """Lista graczy w lidze."""
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
    """Usuwa gracza z ligi (organizer)."""
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
    """Losuje grupy (organizer)."""
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
    if player_count < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Need at least 8 players to draw groups",
        )

    groups = draw_groups(session, league)
    matches = generate_group_matches(session, league)

    league.status = "group_phase"
    league.group_phase_start = datetime.utcnow()
    session.add(league)
    session.commit()

    return {
        "message": f"Created {len(groups)} groups with {len(matches)} matches",
        "groups": [{"id": g.id, "name": g.name} for g in groups],
    }


@router.get("/{league_id}/standings", response_model=list[GroupStandings])
async def get_standings(
    league_id: int,
    session: Session = Depends(get_session),
):
    """Pobiera tabele wszystkich grup."""
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
                )
            )

        result.append(
            GroupStandings(
                group_id=group.id,
                group_name=group.name,
                standings=standings,
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
    """Lista meczow w lidze."""
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
    """Zglasza wynik meczu."""
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
    """Potwierdza wynik meczu."""
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
    """Rozpoczyna faze pucharowa (organizer)."""
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
    """Odkrywa listy armii fazy pucharowej (organizer)."""
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
    """Przesyla liste armii na faze pucharowa."""
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
    """Pobiera liste armii gracza (jesli widoczna)."""
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
    """Pobiera ranking ELO."""
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
    """Pobiera ELO gracza."""
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
