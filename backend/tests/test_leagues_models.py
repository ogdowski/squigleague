"""
Model tests for League, LeagueParticipant, LeagueMatch, LeagueStandings.
Covers defaults, relationships, and simple validations.
"""

import pytest
from datetime import date
from sqlmodel import Session, create_engine, SQLModel, select
from sqlmodel.pool import StaticPool

from app.leagues.models import League, LeagueParticipant, LeagueMatch, LeagueStandings


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def test_league_defaults(session: Session):
    league = League(
        name="Test League",
        season="2025",
        organizer_id=1,
        format_type="round_robin",
        config={"num_groups": 2},
        start_date=date(2025, 1, 1),
        registration_deadline=date(2024, 12, 31)
    )
    session.add(league)
    session.commit()
    session.refresh(league)

    assert league.id is not None
    assert league.status == "draft"
    assert league.config == {"num_groups": 2}
    assert league.created_at is not None
    assert league.updated_at is not None


def test_participant_relationship(session: Session):
    league = League(
        name="Test League",
        season="2025",
        organizer_id=1,
        format_type="round_robin",
        config={},
        start_date=date(2025, 1, 1),
        registration_deadline=date(2024, 12, 31)
    )
    session.add(league)
    session.commit()
    session.refresh(league)

    participant = LeagueParticipant(league_id=league.id, user_id=10, group_number=1)
    session.add(participant)
    session.commit()
    session.refresh(participant)

    fetched = session.exec(select(LeagueParticipant).where(LeagueParticipant.league_id == league.id)).first()
    assert fetched is not None
    assert fetched.user_id == 10
    assert fetched.group_number == 1


def test_match_defaults(session: Session):
    match = LeagueMatch(
        league_id=1,
        player1_id=1,
        player2_id=2,
        phase="group",
        round=1
    )
    session.add(match)
    session.commit()
    session.refresh(match)

    assert match.played is False
    assert match.player1_points is None
    assert match.player2_points is None
    assert match.deadline is None


def test_standings_defaults(session: Session):
    standing = LeagueStandings(
        league_id=1,
        user_id=1,
        phase="group",
        matches_total=3
    )
    session.add(standing)
    session.commit()
    session.refresh(standing)

    assert standing.total_points == 0
    assert standing.matches_played == 0
    assert standing.wins == 0
    assert standing.draws == 0
    assert standing.losses == 0
    assert standing.position is None


def test_standings_update_counters(session: Session):
    standing = LeagueStandings(
        league_id=1,
        user_id=1,
        phase="group",
        matches_total=3,
        total_points=100,
        matches_played=1,
        wins=1,
        draws=0,
        losses=0
    )
    session.add(standing)
    session.commit()

    standing.total_points += 50
    standing.matches_played += 1
    standing.wins += 0
    standing.draws += 1
    standing.losses += 0
    session.add(standing)
    session.commit()

    refreshed = session.get(LeagueStandings, standing.id)
    assert refreshed.total_points == 150
    assert refreshed.matches_played == 2
    assert refreshed.wins == 1
    assert refreshed.draws == 1
    assert refreshed.losses == 0


def test_phase_and_round_required(session: Session):
    match = LeagueMatch(league_id=1, player1_id=1, player2_id=2, phase="group", round=1)
    session.add(match)
    session.commit()
    assert match.phase == "group"
    assert match.round == 1
