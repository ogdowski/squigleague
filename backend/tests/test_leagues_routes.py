"""
API tests for Leagues routes.
Uses real SQLModel DB (sqlite in-memory) and dependency overrides for session/auth.
No mocking of core business logic or ELO updates.
"""

import pytest
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel, select
from sqlmodel.pool import StaticPool

from app.main import app
from app.core.deps import get_session, get_current_user
from app.users.models import User
from app.leagues.models import League, LeagueParticipant, LeagueMatch, LeagueStandings
from app.elo.models import ELORating, ELOConfig


@pytest.fixture(name="session")
def session_fixture():
    """Create in-memory DB with all tables and seed users/ELO."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        # Seed ELO configs
        for name in ["league", "global", "tournament"]:
            session.add(ELOConfig(name=name, k_factor=50, is_active=True))

        # Seed users
        users = [
            User(id=1, username="user1", email="u1@test.com", display_name="User 1", hashed_password="h1"),
            User(id=2, username="user2", email="u2@test.com", display_name="User 2", hashed_password="h2"),
            User(id=3, username="user3", email="u3@test.com", display_name="User 3", hashed_password="h3"),
            User(id=4, username="user4", email="u4@test.com", display_name="User 4", hashed_password="h4"),
        ]
        for user in users:
            session.add(user)

        # Seed ELO ratings
        for user_id in [1, 2, 3, 4]:
            for rating_type in ["league", "global", "tournament"]:
                session.add(ELORating(user_id=user_id, rating_type=rating_type, rating=1000))

        session.commit()
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """FastAPI TestClient with dependency overrides for DB and auth."""
    auth_state = {"user_id": 1}

    def get_session_override():
        return session

    def get_current_user_override():
        return session.get(User, auth_state["user_id"])

    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[get_current_user] = get_current_user_override

    test_client = TestClient(app)
    test_client.auth_state = auth_state
    yield test_client
    app.dependency_overrides.clear()


def _iso(days_from_now: int) -> str:
    return (datetime.now(timezone.utc).date() + timedelta(days=days_from_now)).isoformat()


def test_create_league_success(client: TestClient):
    payload = {
        "name": "League A",
        "season": "2025",
        "format_type": "round_robin",
        "config": {"num_groups": 2},
        "start_date": _iso(7),
        "registration_deadline": _iso(5)
    }
    resp = client.post("/api/leagues", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "League A"
    assert data["organizer_id"] == 1
    assert data["status"] == "draft"


def test_list_leagues_filter_status(client: TestClient, session: Session):
    # Create two leagues
    l1 = League(name="L1", season="S1", organizer_id=1, format_type="rr", config={}, status="registration", start_date=datetime.now(timezone.utc).date(), registration_deadline=datetime.now(timezone.utc).date())
    l2 = League(name="L2", season="S2", organizer_id=1, format_type="rr", config={}, status="completed", start_date=datetime.now(timezone.utc).date(), registration_deadline=datetime.now(timezone.utc).date())
    session.add(l1)
    session.add(l2)
    session.commit()

    resp = client.get("/api/leagues", params={"status": "completed"})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["name"] == "L2"


def test_get_league_success(client: TestClient, session: Session):
    league = League(name="Test League", season="S1", organizer_id=1, format_type="rr", config={}, start_date=datetime.now(timezone.utc).date(), registration_deadline=datetime.now(timezone.utc).date())
    session.add(league)
    session.commit()
    session.refresh(league)
    
    resp = client.get(f"/api/leagues/{league.id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Test League"
    assert data["season"] == "S1"


def test_get_league_not_found(client: TestClient):
    resp = client.get("/api/leagues/9999")
    assert resp.status_code == 404


def test_update_league_success(client: TestClient, session: Session):
    league = League(name="Old", season="S", organizer_id=1, format_type="rr", config={}, start_date=datetime.now(timezone.utc).date(), registration_deadline=datetime.now(timezone.utc).date())
    session.add(league)
    session.commit()
    session.refresh(league)

    payload = {"name": "New Name"}
    resp = client.patch(f"/api/leagues/{league.id}", json=payload)
    assert resp.status_code == 200
    assert resp.json()["name"] == "New Name"


def test_update_league_forbidden(client: TestClient, session: Session):
    league = League(name="Old", season="S", organizer_id=1, format_type="rr", config={}, start_date=datetime.now(timezone.utc).date(), registration_deadline=datetime.now(timezone.utc).date())
    session.add(league)
    session.commit()
    session.refresh(league)

    client.auth_state["user_id"] = 2
    resp = client.patch(f"/api/leagues/{league.id}", json={"name": "Nope"})
    assert resp.status_code == 403


def test_delete_league_success(client: TestClient, session: Session):
    league = League(name="Delete", season="S", organizer_id=1, format_type="rr", config={}, start_date=datetime.now(timezone.utc).date(), registration_deadline=datetime.now(timezone.utc).date())
    session.add(league)
    session.commit()
    session.refresh(league)

    resp = client.delete(f"/api/leagues/{league.id}")
    assert resp.status_code == 200
    assert resp.json()["status"] == "deleted"
    assert session.get(League, league.id) is None


def test_delete_league_forbidden(client: TestClient, session: Session):
    league = League(name="Delete", season="S", organizer_id=1, format_type="rr", config={}, start_date=datetime.now(timezone.utc).date(), registration_deadline=datetime.now(timezone.utc).date())
    session.add(league)
    session.commit()
    session.refresh(league)

    client.auth_state["user_id"] = 2
    resp = client.delete(f"/api/leagues/{league.id}")
    assert resp.status_code == 403


def test_join_league_success(client: TestClient, session: Session):
    league = League(name="Join", season="S", organizer_id=1, format_type="rr", config={}, status="registration", start_date=datetime.now(timezone.utc).date(), registration_deadline=datetime.now(timezone.utc).date())
    session.add(league)
    session.commit()

    client.auth_state["user_id"] = 2
    resp = client.post(f"/api/leagues/{league.id}/join")
    assert resp.status_code == 200
    assert resp.json()["status"] == "registered"


def test_start_league_success(client: TestClient, session: Session):
    league = League(name="Start", season="S", organizer_id=1, format_type="rr", config={"num_groups": 2}, status="registration", start_date=datetime.now(timezone.utc).date(), registration_deadline=datetime.now(timezone.utc).date())
    session.add(league)
    session.commit()
    session.refresh(league)

    for uid in [1, 2, 3, 4]:
        session.add(LeagueParticipant(league_id=league.id, user_id=uid))
    session.commit()

    resp = client.post(f"/api/leagues/{league.id}/start")
    assert resp.status_code == 200
    assert resp.json()["status"] == "group_phase_started"

    league_db = session.get(League, league.id)
    assert league_db.status == "group_phase"

    standings = session.exec(select(LeagueStandings).where(LeagueStandings.league_id == league.id)).all()
    assert len(standings) == 4


def test_start_league_forbidden(client: TestClient, session: Session):
    league = League(name="Start", season="S", organizer_id=1, format_type="rr", config={"num_groups": 2}, status="registration", start_date=datetime.now(timezone.utc).date(), registration_deadline=datetime.now(timezone.utc).date())
    session.add(league)
    session.commit()
    session.refresh(league)

    for uid in [1, 2, 3, 4]:
        session.add(LeagueParticipant(league_id=league.id, user_id=uid))
    session.commit()

    client.auth_state["user_id"] = 2
    resp = client.post(f"/api/leagues/{league.id}/start")
    assert resp.status_code == 403


def test_submit_match_result_success(client: TestClient, session: Session):
    league = League(name="Play", season="S", organizer_id=1, format_type="rr", config={}, status="group_phase", start_date=datetime.now(timezone.utc).date(), registration_deadline=datetime.now(timezone.utc).date())
    session.add(league)
    session.commit()
    session.refresh(league)

    # standings and match
    session.add(LeagueStandings(league_id=league.id, user_id=1, phase="group", matches_total=1))
    session.add(LeagueStandings(league_id=league.id, user_id=2, phase="group", matches_total=1))
    match = LeagueMatch(league_id=league.id, player1_id=1, player2_id=2, phase="group", round=1)
    session.add(match)
    session.commit()
    session.refresh(match)

    resp = client.post(f"/api/leagues/{league.id}/matches/{match.id}/result", json={"player1_score": 70, "player2_score": 30})
    assert resp.status_code == 200
    assert resp.json()["status"] == "result_submitted"

    updated = session.get(LeagueMatch, match.id)
    assert updated.played is True
    assert updated.player1_points == 1100
    assert updated.player2_points == 210

    standing1 = session.exec(select(LeagueStandings).where(LeagueStandings.user_id == 1)).first()
    standing2 = session.exec(select(LeagueStandings).where(LeagueStandings.user_id == 2)).first()
    assert standing1.total_points == 1100
    assert standing1.wins == 1
    assert standing2.total_points == 210
    assert standing2.losses == 1


def test_get_standings(client: TestClient, session: Session):
    league = League(name="Standings", season="S", organizer_id=1, format_type="rr", config={}, status="group_phase", start_date=datetime.now(timezone.utc).date(), registration_deadline=datetime.now(timezone.utc).date())
    session.add(league)
    session.commit()
    session.refresh(league)

    session.add(LeagueStandings(league_id=league.id, user_id=1, phase="group", total_points=2000, wins=2, matches_total=1))
    session.add(LeagueStandings(league_id=league.id, user_id=2, phase="group", total_points=1000, wins=1, matches_total=1))
    session.add(LeagueMatch(league_id=league.id, player1_id=1, player2_id=2, phase="group", round=1, played=True, player1_score=60, player2_score=40))
    session.commit()

    resp = client.get(f"/api/leagues/{league.id}/standings")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    assert data[0]["user_id"] == 1
    assert data[0]["position"] == 1
    assert data[1]["user_id"] == 2
    assert data[1]["position"] == 2
    assert data[0]["goal_difference"] == 20
    assert data[1]["goal_difference"] == -20


def test_update_league_not_found(client: TestClient):
    """Test update endpoint returns 404 for missing league"""
    client.auth_state["user_id"] = 1
    resp = client.patch("/api/leagues/999999", json={"name": "Updated"})
    assert resp.status_code == 404


def test_delete_league_not_found(client: TestClient):
    """Test delete endpoint returns 404 for missing league"""
    client.auth_state["user_id"] = 1
    resp = client.delete("/api/leagues/999999")
    assert resp.status_code == 404
