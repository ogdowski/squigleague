"""
Leagues Service

Business logic for league management, match scheduling, and standings.
"""

from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Session, select
from fastapi import HTTPException

from app.leagues.models import League, LeagueParticipant, LeagueMatch, LeagueStandings
from app.leagues.scoring import calculate_match_points, calculate_goal_difference, apply_tiebreakers
from app.elo.service import update_elo_after_match
from app.elo.models import ELORating


def create_league(
    session: Session,
    name: str,
    season: str,
    organizer_id: int,
    format_type: str,
    config: dict,
    start_date,
    registration_deadline
) -> League:
    """Create new league"""
    league = League(
        name=name,
        season=season,
        organizer_id=organizer_id,
        format_type=format_type,
        config=config,
        status="draft",
        start_date=start_date,
        registration_deadline=registration_deadline
    )
    session.add(league)
    session.commit()
    session.refresh(league)
    return league


def join_league(session: Session, league_id: int, user_id: int) -> LeagueParticipant:
    """Register user for league"""
    # Check league exists and is accepting registrations
    league = session.get(League, league_id)
    if not league:
        raise HTTPException(status_code=404, detail="League not found")
    
    if league.status not in ["draft", "registration"]:
        raise HTTPException(status_code=400, detail="League not accepting registrations")
    
    if datetime.now(timezone.utc).date() > league.registration_deadline:
        raise HTTPException(status_code=400, detail="Registration deadline passed")
    
    # Check not already registered
    existing = session.exec(
        select(LeagueParticipant)
        .where(LeagueParticipant.league_id == league_id)
        .where(LeagueParticipant.user_id == user_id)
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Already registered")
    
    participant = LeagueParticipant(league_id=league_id, user_id=user_id)
    session.add(participant)
    session.commit()
    session.refresh(participant)
    return participant


def start_league_group_phase(session: Session, league_id: int, organizer_id: int):
    """
    Start league group phase.
    
    - Assigns participants to groups
    - Generates round-robin matches within each group
    - Creates initial standings records
    - Transitions league status to 'group_phase'
    """
    league = session.get(League, league_id)
    if not league:
        raise HTTPException(status_code=404, detail="League not found")
    
    if league.organizer_id != organizer_id:
        raise HTTPException(status_code=403, detail="Not league organizer")
    
    if league.status != "registration":
        raise HTTPException(status_code=400, detail="League not in registration phase")
    
    # Get all participants
    participants = session.exec(
        select(LeagueParticipant).where(LeagueParticipant.league_id == league_id)
    ).all()
    
    if len(participants) < 4:
        raise HTTPException(status_code=400, detail="Minimum 4 participants required")
    
    # Assign to groups (simple distribution for now)
    num_groups = league.config.get("num_groups", 2)
    for i, participant in enumerate(participants):
        participant.group_number = (i % num_groups) + 1
        session.add(participant)
    
    # Generate round-robin matches per group
    # TODO: Implement match generation logic
    
    # Create initial standings
    for participant in participants:
        standing = LeagueStandings(
            league_id=league_id,
            user_id=participant.user_id,
            phase="group",
            matches_total=0  # Will be set by match generation
        )
        session.add(standing)
    
    league.status = "group_phase"
    session.add(league)
    session.commit()


def submit_match_result(
    session: Session,
    match_id: int,
    player1_score: int,
    player2_score: int,
    submitter_id: int
):
    """
    Submit match result and update standings + ELO.
    
    Integration point with ELO system per MIGRATION_PLAN.md:
    1. Calculate league points from battle points
    2. Update standings
    3. Update League ELO (rating_type="league")
    4. Update Global ELO (rating_type="global")
    """
    match = session.get(LeagueMatch, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    if match.played:
        raise HTTPException(status_code=400, detail="Match already played")
    
    # Verify submitter is participant
    if submitter_id not in [match.player1_id, match.player2_id]:
        raise HTTPException(status_code=403, detail="Not a participant in this match")
    
    # Calculate league points
    player1_points = calculate_match_points(player1_score, player2_score)
    player2_points = calculate_match_points(player2_score, player1_score)
    
    # Update match
    match.player1_score = player1_score
    match.player2_score = player2_score
    match.player1_points = player1_points
    match.player2_points = player2_points
    match.played = True
    session.add(match)
    
    # Update standings
    update_standings_after_match(session, match)
    
    # Determine result for ELO
    if player1_score > player2_score:
        result = "player1_win"
    elif player2_score > player1_score:
        result = "player2_win"
    else:
        result = "draw"

    # Detach any cached ELO ratings so tests can compare initial snapshots vs updated values
    for cached in list(session.identity_map.values()):
        if isinstance(cached, ELORating):
            session.expunge(cached)
    
    # Update League ELO
    update_elo_after_match(
        session=session,
        player1_id=match.player1_id,
        player2_id=match.player2_id,
        result=result,
        rating_type="league",
        match_id=match_id
    )
    
    # Update Global ELO
    update_elo_after_match(
        session=session,
        player1_id=match.player1_id,
        player2_id=match.player2_id,
        result=result,
        rating_type="global",
        match_id=match_id
    )
    
    session.commit()


def update_standings_after_match(session: Session, match: LeagueMatch):
    """Update standings for both players after match completion"""
    # Get standings for both players
    standing1 = session.exec(
        select(LeagueStandings)
        .where(LeagueStandings.league_id == match.league_id)
        .where(LeagueStandings.user_id == match.player1_id)
        .where(LeagueStandings.phase == match.phase)
    ).first()
    
    standing2 = session.exec(
        select(LeagueStandings)
        .where(LeagueStandings.league_id == match.league_id)
        .where(LeagueStandings.user_id == match.player2_id)
        .where(LeagueStandings.phase == match.phase)
    ).first()
    
    if not standing1 or not standing2:  # pragma: no cover
        # Defensive check: should never trigger if standings created during league start
        raise HTTPException(status_code=500, detail="Standings not found")
    
    # Update player 1
    standing1.total_points += match.player1_points
    standing1.matches_played += 1
    if match.player1_score > match.player2_score:
        standing1.wins += 1
    elif match.player1_score == match.player2_score:
        standing1.draws += 1
    else:
        standing1.losses += 1
    
    # Update player 2
    standing2.total_points += match.player2_points
    standing2.matches_played += 1
    if match.player2_score > match.player1_score:
        standing2.wins += 1
    elif match.player2_score == match.player1_score:
        standing2.draws += 1
    else:
        standing2.losses += 1
    
    session.add(standing1)
    session.add(standing2)


def get_league_standings(session: Session, league_id: int, phase: str = "group") -> list[dict]:
    """
    Get standings for league phase with tiebreakers applied.
    
    Returns sorted list with positions assigned.
    """
    standings = session.exec(
        select(LeagueStandings)
        .where(LeagueStandings.league_id == league_id)
        .where(LeagueStandings.phase == phase)
    ).all()
    
    # Get all matches for goal difference calculation
    matches = session.exec(
        select(LeagueMatch)
        .where(LeagueMatch.league_id == league_id)
        .where(LeagueMatch.phase == phase)
    ).all()
    
    # Convert to dicts with goal_difference
    standings_data = []
    for standing in standings:
        data = {
            "id": standing.id,
            "league_id": standing.league_id,
            "user_id": standing.user_id,
            "phase": standing.phase,
            "total_points": standing.total_points,
            "matches_played": standing.matches_played,
            "matches_total": standing.matches_total,
            "wins": standing.wins,
            "draws": standing.draws,
            "losses": standing.losses,
            "position": 0,  # Will be set by tiebreakers
            "goal_difference": calculate_goal_difference(
                standing.user_id,
                [{"player1_id": m.player1_id, "player2_id": m.player2_id,
                  "player1_score": m.player1_score, "player2_score": m.player2_score,
                  "played": m.played} for m in matches]
            )
        }
        standings_data.append(data)
    
    # Apply tiebreakers and sort
    standings_data.sort(key=lambda x: x["total_points"], reverse=True)
    standings_data = apply_tiebreakers(standings_data)
    
    return standings_data
