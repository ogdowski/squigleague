"""
Leagues Routes

API endpoints for league management.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.core.deps import get_session, get_current_user
from app.users.models import User
from app.leagues.models import League, LeagueParticipant
from app.leagues.schemas import (
    LeagueCreate, LeagueUpdate, LeagueRead, LeagueListItem,
    MatchResultSubmit, MatchRead, StandingRead
)
from app.leagues import service


router = APIRouter(prefix="/api/leagues", tags=["leagues"])


@router.post("", response_model=LeagueRead)
def create_league(
    league_data: LeagueCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Create new league.
    
    Authenticated users can create leagues and become organizer.
    """
    league = service.create_league(
        session=session,
        name=league_data.name,
        season=league_data.season,
        organizer_id=current_user.id,
        format_type=league_data.format_type,
        config=league_data.config,
        start_date=league_data.start_date,
        registration_deadline=league_data.registration_deadline
    )
    return league


@router.get("", response_model=list[LeagueListItem])
def list_leagues(
    session: Session = Depends(get_session),
    status: str | None = None
):
    """
    List all leagues.
    
    Public endpoint. Optionally filter by status.
    """
    query = select(League)
    if status:
        query = query.where(League.status == status)
    
    leagues = session.exec(query).all()
    return leagues


@router.get("/{league_id}", response_model=LeagueRead)
def get_league(
    league_id: int,
    session: Session = Depends(get_session)
):
    """
    Get league details.
    
    Public endpoint.
    """
    league = session.get(League, league_id)
    if not league:
        raise HTTPException(status_code=404, detail="League not found")
    return league


@router.patch("/{league_id}", response_model=LeagueRead)
def update_league(
    league_id: int,
    updates: LeagueUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Update league settings.
    
    Organizer only.
    """
    league = session.get(League, league_id)
    if not league:
        raise HTTPException(status_code=404, detail="League not found")
    
    if league.organizer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not league organizer")
    
    # Apply updates
    if updates.name is not None:
        league.name = updates.name
    if updates.season is not None:
        league.season = updates.season
    if updates.registration_deadline is not None:
        league.registration_deadline = updates.registration_deadline
    if updates.config is not None:
        league.config = updates.config
    
    session.add(league)
    session.commit()
    session.refresh(league)
    return league


@router.delete("/{league_id}")
def delete_league(
    league_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Delete league.
    
    Admin only (require_admin dependency would be added from app.core.permissions).
    For now, restrict to organizer.
    """
    league = session.get(League, league_id)
    if not league:
        raise HTTPException(status_code=404, detail="League not found")
    
    if league.organizer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not league organizer")
    
    session.delete(league)
    session.commit()
    return {"status": "deleted"}


@router.post("/{league_id}/join")
def join_league(
    league_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Join league.
    
    Registers current user as participant.
    """
    participant = service.join_league(session, league_id, current_user.id)
    return {"status": "registered", "participant_id": participant.id}


@router.post("/{league_id}/start")
def start_league(
    league_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Start league group phase.
    
    - Assigns participants to groups
    - Generates round-robin matches
    - Creates standings
    
    Organizer only.
    """
    service.start_league_group_phase(session, league_id, current_user.id)
    return {"status": "group_phase_started"}


@router.post("/{league_id}/matches/{match_id}/result")
def submit_match_result(
    league_id: int,
    match_id: int,
    result: MatchResultSubmit,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Submit match result.
    
    Updates standings and ELO ratings (league + global).
    Participant only.
    """
    service.submit_match_result(
        session=session,
        match_id=match_id,
        player1_score=result.player1_score,
        player2_score=result.player2_score,
        submitter_id=current_user.id
    )
    return {"status": "result_submitted"}


@router.get("/{league_id}/standings", response_model=list[StandingRead])
def get_standings(
    league_id: int,
    phase: str = "group",
    session: Session = Depends(get_session)
):
    """
    Get league standings.
    
    Returns sorted standings with tiebreakers applied.
    Public endpoint.
    """
    standings = service.get_league_standings(session, league_id, phase)
    return standings
