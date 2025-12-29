from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, func
from datetime import datetime

from app.db import get_session
from app.core.deps import get_current_user_optional, get_current_user
from app.matchup.models import Matchup
from app.matchup.schemas import (
    MatchupCreate,
    MatchupCreateResponse,
    MatchupSubmit,
    MatchupStatus,
    MatchupReveal,
)
from app.matchup.service import submit_list

router = APIRouter()


@router.post("", response_model=MatchupCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_matchup(
    data: MatchupCreate,
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user_optional),
):
    """Create a new matchup with Player 1's army list and return the UUID link."""
    matchup = Matchup(
        player1_id=current_user.id if current_user else None,
        player1_list=data.army_list,
        player1_submitted=True,
    )

    session.add(matchup)
    session.commit()
    session.refresh(matchup)

    return MatchupCreateResponse(
        name=matchup.name,
        link=f"/matchup/{matchup.name}",
        expires_at=matchup.expires_at,
    )


@router.get("/my-matchups", response_model=list[MatchupStatus])
async def get_my_matchups(
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user),
):
    """Get all matchups for the current user."""
    from sqlalchemy import or_

    statement = select(Matchup).where(
        or_(
            Matchup.player1_id == current_user.id,
            Matchup.player2_id == current_user.id
        )
    ).order_by(Matchup.created_at.desc())

    matchups = session.exec(statement).all()

    return [
        MatchupStatus(
            name=m.name,
            player1_submitted=m.player1_submitted,
            player2_submitted=m.player2_submitted,
            is_revealed=m.is_revealed,
            created_at=m.created_at,
            expires_at=m.expires_at,
        )
        for m in matchups
    ]


@router.get("/{matchup_name}", response_model=MatchupStatus)
async def get_matchup_status(
    matchup_name: str,
    session: Session = Depends(get_session),
):
    """Get matchup status (without revealing lists)."""
    statement = select(Matchup).where(Matchup.name == matchup_name)
    matchup = session.exec(statement).first()

    if not matchup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Matchup not found",
        )

    if matchup.is_expired:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Matchup has expired",
        )

    return MatchupStatus(
        name=matchup.name,
        player1_submitted=matchup.player1_submitted,
        player2_submitted=matchup.player2_submitted,
        is_revealed=matchup.is_revealed,
        created_at=matchup.created_at,
        expires_at=matchup.expires_at,
    )


@router.post("/{matchup_name}/submit")
async def submit_army_list(
    matchup_name: str,
    submission: MatchupSubmit,
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user_optional),
):
    """Submit an army list to a matchup."""
    statement = select(Matchup).where(Matchup.name == matchup_name)
    matchup = session.exec(statement).first()

    if not matchup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Matchup not found",
        )

    if matchup.is_expired:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Matchup has expired",
        )

    # Determine if this is player1 or player2
    is_player1 = False
    if current_user and matchup.player1_id == current_user.id:
        is_player1 = True
    elif not matchup.player1_submitted:
        is_player1 = True

    try:
        matchup = submit_list(matchup, submission.army_list, is_player1, session)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    return {
        "message": "List submitted successfully",
        "is_revealed": matchup.is_revealed,
    }


@router.get("/{matchup_name}/reveal", response_model=MatchupReveal)
async def reveal_matchup(
    matchup_name: str,
    session: Session = Depends(get_session),
):
    """Reveal both army lists and the assigned map."""
    statement = select(Matchup).where(Matchup.name == matchup_name)
    matchup = session.exec(statement).first()

    if not matchup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Matchup not found",
        )

    if not matchup.is_revealed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Both players must submit their lists before revealing",
        )

    return MatchupReveal(
        name=matchup.name,
        player1_list=matchup.player1_list,
        player2_list=matchup.player2_list,
        map_name=matchup.map_name,
        revealed_at=matchup.revealed_at,
    )


@router.get("/stats")
async def get_stats(session: Session = Depends(get_session)):
    """Get platform statistics."""
    # Count completed matchups (both lists submitted)
    completed_statement = select(func.count(Matchup.id)).where(
        Matchup.player1_submitted == True,
        Matchup.player2_submitted == True,
    )
    completed_count = session.execute(completed_statement).scalar_one()

    # Count expired matchups
    now = datetime.utcnow()
    expired_statement = select(func.count(Matchup.id)).where(
        Matchup.expires_at < now
    )
    expired_count = session.execute(expired_statement).scalar_one()

    return {
        "exchanges_completed": completed_count,
        "exchanges_expired": expired_count,
        "version": "0.3.0"
    }
