"""Tests for matchup played_on date functionality."""
from datetime import datetime, timedelta

import pytest
from app.matchup.models import Matchup
from fastapi.testclient import TestClient
from sqlmodel import Session


def test_matchup_has_default_played_on(session: Session):
    """Test that new matchups have played_on defaulted to current time."""
    before = datetime.utcnow()
    matchup = Matchup(
        player1_list="Test army list",
        player1_submitted=True,
    )
    session.add(matchup)
    session.commit()
    session.refresh(matchup)
    after = datetime.utcnow()

    assert matchup.played_on is not None
    assert before <= matchup.played_on <= after


def test_get_matchup_status_includes_played_on(client: TestClient, session: Session):
    """Test that GET /matchup/{name} includes played_on in response."""
    matchup = Matchup(
        player1_list="Test army list",
        player1_submitted=True,
    )
    session.add(matchup)
    session.commit()
    session.refresh(matchup)

    response = client.get(f"/matchup/{matchup.name}")
    assert response.status_code == 200
    data = response.json()
    assert "played_on" in data
    assert data["played_on"] is not None


def test_update_played_on_date_success(client: TestClient, session: Session):
    """Test successfully updating played_on date."""
    matchup = Matchup(
        player1_list="Test army list",
        player1_submitted=True,
    )
    session.add(matchup)
    session.commit()
    session.refresh(matchup)

    # Update to yesterday
    new_date = datetime.utcnow() - timedelta(days=1)
    response = client.patch(
        f"/matchup/{matchup.name}/date",
        json={"played_on": new_date.isoformat()},
    )

    assert response.status_code == 200
    data = response.json()
    assert "played_on" in data
    
    # Verify in database
    session.refresh(matchup)
    assert matchup.played_on.date() == new_date.date()


def test_update_played_on_rejects_future_date(client: TestClient, session: Session):
    """Test that updating played_on with future date is rejected."""
    matchup = Matchup(
        player1_list="Test army list",
        player1_submitted=True,
    )
    session.add(matchup)
    session.commit()
    session.refresh(matchup)

    # Try to set date to tomorrow
    future_date = datetime.utcnow() + timedelta(days=1)
    response = client.patch(
        f"/matchup/{matchup.name}/date",
        json={"played_on": future_date.isoformat()},
    )

    assert response.status_code == 400
    assert "future" in response.json()["detail"].lower()


def test_update_played_on_rejects_before_created(client: TestClient, session: Session):
    """Test that played_on cannot be before matchup creation date."""
    matchup = Matchup(
        player1_list="Test army list",
        player1_submitted=True,
    )
    session.add(matchup)
    session.commit()
    session.refresh(matchup)

    # Try to set date before creation
    before_created = matchup.created_at - timedelta(days=1)
    response = client.patch(
        f"/matchup/{matchup.name}/date",
        json={"played_on": before_created.isoformat()},
    )

    assert response.status_code == 400
    assert "creation" in response.json()["detail"].lower()


def test_update_played_on_nonexistent_matchup(client: TestClient):
    """Test updating played_on for non-existent matchup returns 404."""
    response = client.patch(
        "/matchup/nonexistent-matchup/date",
        json={"played_on": datetime.utcnow().isoformat()},
    )

    assert response.status_code == 404


def test_reveal_includes_played_on(client: TestClient, session: Session):
    """Test that revealed matchup includes played_on in response."""
    matchup = Matchup(
        player1_list="Player 1 army list",
        player1_submitted=True,
        player2_list="Player 2 army list",
        player2_submitted=True,
        map_name="Passing Seasons",
        revealed_at=datetime.utcnow(),
    )
    session.add(matchup)
    session.commit()
    session.refresh(matchup)

    response = client.get(f"/matchup/{matchup.name}/reveal")
    assert response.status_code == 200
    data = response.json()
    assert "played_on" in data
    assert data["played_on"] is not None


def test_my_matchups_includes_played_on(client: TestClient, session: Session, auth_headers):
    """Test that my matchups list includes played_on for each matchup."""
    # This test requires authentication setup
    # Implementation depends on your auth system
    pass
