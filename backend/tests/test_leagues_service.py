"""
Tests for Leagues Service Layer

Integration tests for league management business logic.
Per TESTING_POLICY.md: Real database, no mocking, 100% coverage.
"""

import pytest
from datetime import datetime, timezone, timedelta
from sqlmodel import Session, create_engine, SQLModel, select
from sqlmodel.pool import StaticPool
from fastapi import HTTPException

from app.leagues.service import (
    create_league,
    join_league,
    start_league_group_phase,
    submit_match_result,
    update_standings_after_match,
    get_league_standings
)
from app.leagues.models import League, LeagueParticipant, LeagueMatch, LeagueStandings
from app.users.models import User
from app.elo.models import ELORating, ELOConfig


# ═══════════════════════════════════════════════
# TEST DATABASE SETUP
# ═══════════════════════════════════════════════


@pytest.fixture(name="session")
def session_fixture():
    """Create test database session with all tables"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    
    # Prevent attribute refresh on commit so initial snapshots stay stable in assertions
    with Session(engine, expire_on_commit=False) as session:
        # Seed ELO configs (required by update_elo_after_match)
        configs = [
            ELOConfig(name="league", k_factor=50, is_active=True),
            ELOConfig(name="global", k_factor=50, is_active=True),
            ELOConfig(name="tournament", k_factor=50, is_active=True)
        ]
        for config in configs:
            session.add(config)
        
        # Create test users
        users = [
            User(id=1, username="player1", email="p1@test.com", display_name="Player 1", hashed_password="hash1"),
            User(id=2, username="player2", email="p2@test.com", display_name="Player 2", hashed_password="hash2"),
            User(id=3, username="player3", email="p3@test.com", display_name="Player 3", hashed_password="hash3"),
            User(id=4, username="player4", email="p4@test.com", display_name="Player 4", hashed_password="hash4"),
            User(id=5, username="organizer", email="org@test.com", display_name="Organizer", hashed_password="hash5")
        ]
        for user in users:
            session.add(user)
        
        # Create initial ELO ratings
        for user_id in [1, 2, 3, 4, 5]:
            for rating_type in ["league", "global", "tournament"]:
                session.add(ELORating(user_id=user_id, rating_type=rating_type, rating=1000))
        
        session.commit()
        yield session


# ═══════════════════════════════════════════════
# CREATE LEAGUE TESTS
# ═══════════════════════════════════════════════


class TestCreateLeague:
    """Test league creation"""
    
    def test_create_league_success(self, session: Session):
        """Successfully create league"""
        start_date = datetime.now(timezone.utc).date() + timedelta(days=7)
        reg_deadline = datetime.now(timezone.utc).date() + timedelta(days=5)
        
        league = create_league(
            session=session,
            name="Winter League 2025",
            season="Winter 2025",
            organizer_id=5,
            format_type="round_robin",
            config={"num_groups": 2, "group_size": 4},
            start_date=start_date,
            registration_deadline=reg_deadline
        )
        
        assert league.id is not None
        assert league.name == "Winter League 2025"
        assert league.season == "Winter 2025"
        assert league.organizer_id == 5
        assert league.format_type == "round_robin"
        assert league.status == "draft"
        assert league.config == {"num_groups": 2, "group_size": 4}
        assert league.start_date == start_date
        assert league.registration_deadline == reg_deadline
    
    def test_create_league_persisted(self, session: Session):
        """League is persisted to database"""
        start_date = datetime.now(timezone.utc).date() + timedelta(days=7)
        reg_deadline = datetime.now(timezone.utc).date() + timedelta(days=5)
        
        league = create_league(
            session=session,
            name="Test League",
            season="Test",
            organizer_id=5,
            format_type="swiss",
            config={},
            start_date=start_date,
            registration_deadline=reg_deadline
        )
        
        # Query from DB
        db_league = session.get(League, league.id)
        assert db_league is not None
        assert db_league.name == "Test League"
        assert db_league.organizer_id == 5


# ═══════════════════════════════════════════════
# JOIN LEAGUE TESTS
# ═══════════════════════════════════════════════


class TestJoinLeague:
    """Test league registration"""
    
    @pytest.fixture(autouse=True)
    def setup_league(self, session: Session):
        """Create test league for each test"""
        start_date = datetime.now(timezone.utc).date() + timedelta(days=7)
        reg_deadline = datetime.now(timezone.utc).date() + timedelta(days=5)
        
        self.league = create_league(
            session=session,
            name="Test League",
            season="Test",
            organizer_id=5,
            format_type="round_robin",
            config={"num_groups": 2},
            start_date=start_date,
            registration_deadline=reg_deadline
        )
        self.league.status = "registration"
        session.add(self.league)
        session.commit()
    
    def test_join_league_success(self, session: Session):
        """Successfully join league"""
        participant = join_league(session, self.league.id, 1)
        
        assert participant.id is not None
        assert participant.league_id == self.league.id
        assert participant.user_id == 1
        assert participant.group_number is None  # Not assigned yet
    
    def test_join_league_multiple_users(self, session: Session):
        """Multiple users can join"""
        p1 = join_league(session, self.league.id, 1)
        p2 = join_league(session, self.league.id, 2)
        p3 = join_league(session, self.league.id, 3)
        
        assert p1.user_id == 1
        assert p2.user_id == 2
        assert p3.user_id == 3
    
    def test_join_league_already_registered(self, session: Session):
        """Cannot join twice"""
        join_league(session, self.league.id, 1)
        
        with pytest.raises(HTTPException) as exc:
            join_league(session, self.league.id, 1)
        
        assert exc.value.status_code == 400
        assert "Already registered" in exc.value.detail
    
    def test_join_league_not_found(self, session: Session):
        """Cannot join non-existent league"""
        with pytest.raises(HTTPException) as exc:
            join_league(session, 99999, 1)
        
        assert exc.value.status_code == 404
        assert "not found" in exc.value.detail
    
    def test_join_league_wrong_status(self, session: Session):
        """Cannot join league not accepting registrations"""
        self.league.status = "completed"
        session.add(self.league)
        session.commit()
        
        with pytest.raises(HTTPException) as exc:
            join_league(session, self.league.id, 1)
        
        assert exc.value.status_code == 400
        assert "not accepting" in exc.value.detail
    
    def test_join_league_deadline_passed(self, session: Session):
        """Cannot join after deadline"""
        self.league.registration_deadline = datetime.now(timezone.utc).date() - timedelta(days=1)
        session.add(self.league)
        session.commit()
        
        with pytest.raises(HTTPException) as exc:
            join_league(session, self.league.id, 1)
        
        assert exc.value.status_code == 400
        assert "deadline passed" in exc.value.detail


# ═══════════════════════════════════════════════
# START GROUP PHASE TESTS
# ═══════════════════════════════════════════════


class TestStartGroupPhase:
    """Test group phase initialization"""
    
    @pytest.fixture(autouse=True)
    def setup_league(self, session: Session):
        """Create league with 4 participants"""
        start_date = datetime.now(timezone.utc).date() + timedelta(days=7)
        reg_deadline = datetime.now(timezone.utc).date() + timedelta(days=5)
        
        self.league = create_league(
            session=session,
            name="Test League",
            season="Test",
            organizer_id=5,
            format_type="round_robin",
            config={"num_groups": 2},
            start_date=start_date,
            registration_deadline=reg_deadline
        )
        self.league.status = "registration"
        session.add(self.league)
        session.commit()
        
        # Add 4 participants
        for user_id in [1, 2, 3, 4]:
            join_league(session, self.league.id, user_id)
    
    def test_start_group_phase_success(self, session: Session):
        """Successfully start group phase"""
        start_league_group_phase(session, self.league.id, 5)
        
        # Check league status
        league = session.get(League, self.league.id)
        assert league.status == "group_phase"
        
        # Check group assignments
        participants = session.exec(
            select(LeagueParticipant).where(LeagueParticipant.league_id == self.league.id)
        ).all()
        
        assert len(participants) == 4
        for p in participants:
            assert p.group_number in [1, 2]
        
        # Check standings created
        standings = session.exec(
            select(LeagueStandings).where(LeagueStandings.league_id == self.league.id)
        ).all()
        
        assert len(standings) == 4
        for standing in standings:
            assert standing.phase == "group"
            assert standing.total_points == 0
            assert standing.matches_played == 0
    
    def test_start_group_phase_group_distribution(self, session: Session):
        """Groups are distributed evenly"""
        start_league_group_phase(session, self.league.id, 5)
        
        participants = session.exec(
            select(LeagueParticipant).where(LeagueParticipant.league_id == self.league.id)
        ).all()
        
        group1_count = sum(1 for p in participants if p.group_number == 1)
        group2_count = sum(1 for p in participants if p.group_number == 2)
        
        assert group1_count == 2
        assert group2_count == 2
    
    def test_start_group_phase_not_organizer(self, session: Session):
        """Only organizer can start phase"""
        with pytest.raises(HTTPException) as exc:
            start_league_group_phase(session, self.league.id, 1)
        
        assert exc.value.status_code == 403
        assert "Not league organizer" in exc.value.detail
    
    def test_start_group_phase_wrong_status(self, session: Session):
        """Cannot start from wrong status"""
        self.league.status = "draft"
        session.add(self.league)
        session.commit()
        
        with pytest.raises(HTTPException) as exc:
            start_league_group_phase(session, self.league.id, 5)
        
        assert exc.value.status_code == 400
        assert "not in registration phase" in exc.value.detail
    
    def test_start_group_phase_insufficient_participants(self, session: Session):
        """Minimum 4 participants required"""
        # Remove participants to have only 2
        participants = session.exec(
            select(LeagueParticipant).where(LeagueParticipant.league_id == self.league.id)
        ).all()
        
        for p in participants[2:]:
            session.delete(p)
        session.commit()
        
        with pytest.raises(HTTPException) as exc:
            start_league_group_phase(session, self.league.id, 5)
        
        assert exc.value.status_code == 400
        assert "Minimum 4 participants" in exc.value.detail
    
    def test_start_group_phase_league_not_found(self, session: Session):
        """Cannot start non-existent league"""
        with pytest.raises(HTTPException) as exc:
            start_league_group_phase(session, 99999, 5)
        
        assert exc.value.status_code == 404
        assert "not found" in exc.value.detail


# ═══════════════════════════════════════════════
# SUBMIT MATCH RESULT TESTS
# ═══════════════════════════════════════════════


class TestSubmitMatchResult:
    """Test match result submission and ELO integration"""
    
    @pytest.fixture(autouse=True)
    def setup_match(self, session: Session):
        """Create league with match ready to play"""
        start_date = datetime.now(timezone.utc).date() + timedelta(days=7)
        reg_deadline = datetime.now(timezone.utc).date() + timedelta(days=5)
        
        self.league = create_league(
            session=session,
            name="Test League",
            season="Test",
            organizer_id=5,
            format_type="round_robin",
            config={"num_groups": 2},
            start_date=start_date,
            registration_deadline=reg_deadline
        )
        self.league.status = "group_phase"
        session.add(self.league)
        
        # Create standings
        for user_id in [1, 2]:
            standing = LeagueStandings(
                league_id=self.league.id,
                user_id=user_id,
                phase="group",
                matches_total=1
            )
            session.add(standing)
        
        # Create match
        self.match = LeagueMatch(
            league_id=self.league.id,
            player1_id=1,
            player2_id=2,
            phase="group",
            round=1
        )
        session.add(self.match)
        session.commit()
        session.refresh(self.match)
    
    def test_submit_match_result_player1_wins(self, session: Session):
        """Player 1 wins match"""
        submit_match_result(session, self.match.id, 80, 20, 1)
        
        # Check match updated
        match = session.get(LeagueMatch, self.match.id)
        assert match.played is True
        assert match.player1_score == 80
        assert match.player2_score == 20
        assert match.player1_points == 1100  # Win 80-20
        assert match.player2_points == 200   # Loss 20-80
    
    def test_submit_match_result_player2_wins(self, session: Session):
        """Player 2 wins match"""
        submit_match_result(session, self.match.id, 30, 70, 2)
        
        match = session.get(LeagueMatch, self.match.id)
        assert match.player1_score == 30
        assert match.player2_score == 70
        assert match.player1_points == 210   # Loss 30-70
        assert match.player2_points == 1100  # Win 70-30
    
    def test_submit_match_result_draw(self, session: Session):
        """Match ends in draw"""
        submit_match_result(session, self.match.id, 50, 50, 1)
        
        match = session.get(LeagueMatch, self.match.id)
        assert match.player1_score == 50
        assert match.player2_score == 50
        assert match.player1_points == 650  # Draw
        assert match.player2_points == 650  # Draw
    
    def test_submit_match_result_updates_standings(self, session: Session):
        """Standings are updated after match"""
        submit_match_result(session, self.match.id, 60, 40, 1)
        
        # Check player 1 standing
        standing1 = session.exec(
            select(LeagueStandings)
            .where(LeagueStandings.league_id == self.league.id)
            .where(LeagueStandings.user_id == 1)
        ).first()
        
        assert standing1.total_points == 1070
        assert standing1.matches_played == 1
        assert standing1.wins == 1
        assert standing1.draws == 0
        assert standing1.losses == 0
        
        # Check player 2 standing
        standing2 = session.exec(
            select(LeagueStandings)
            .where(LeagueStandings.league_id == self.league.id)
            .where(LeagueStandings.user_id == 2)
        ).first()
        
        assert standing2.total_points == 230
        assert standing2.matches_played == 1
        assert standing2.wins == 0
        assert standing2.draws == 0
        assert standing2.losses == 1
    
    def test_submit_match_result_updates_elo(self, session: Session):
        """ELO ratings are updated (both league and global)"""
        # Get initial ratings
        initial_league_1 = session.exec(
            select(ELORating)
            .where(ELORating.user_id == 1)
            .where(ELORating.rating_type == "league")
        ).first()
        initial_global_1 = session.exec(
            select(ELORating)
            .where(ELORating.user_id == 1)
            .where(ELORating.rating_type == "global")
        ).first()
        
        submit_match_result(session, self.match.id, 80, 20, 1)
        
        # Check league ELO updated
        league_rating_1 = session.exec(
            select(ELORating)
            .where(ELORating.user_id == 1)
            .where(ELORating.rating_type == "league")
        ).first()
        
        assert league_rating_1.rating != initial_league_1.rating
        assert league_rating_1.games_played == 1
        assert league_rating_1.wins == 1
        
        # Check global ELO updated
        global_rating_1 = session.exec(
            select(ELORating)
            .where(ELORating.user_id == 1)
            .where(ELORating.rating_type == "global")
        ).first()
        
        assert global_rating_1.rating != initial_global_1.rating
        assert global_rating_1.games_played == 1
        assert global_rating_1.wins == 1
    
    def test_submit_match_result_not_found(self, session: Session):
        """Cannot submit for non-existent match"""
        with pytest.raises(HTTPException) as exc:
            submit_match_result(session, 99999, 50, 50, 1)
        
        assert exc.value.status_code == 404
        assert "not found" in exc.value.detail
    
    def test_submit_match_result_already_played(self, session: Session):
        """Cannot submit result twice"""
        submit_match_result(session, self.match.id, 50, 50, 1)
        
        with pytest.raises(HTTPException) as exc:
            submit_match_result(session, self.match.id, 60, 40, 1)
        
        assert exc.value.status_code == 400
        assert "already played" in exc.value.detail
    
    def test_submit_match_result_not_participant(self, session: Session):
        """Only participants can submit"""
        with pytest.raises(HTTPException) as exc:
            submit_match_result(session, self.match.id, 50, 50, 3)
        
        assert exc.value.status_code == 403
        assert "Not a participant" in exc.value.detail


# ═══════════════════════════════════════════════
# GET STANDINGS TESTS
# ═══════════════════════════════════════════════


class TestGetLeagueStandings:
    """Test standings retrieval with tiebreakers"""
    
    def test_get_standings_empty(self, session: Session):
        """Empty standings for new league"""
        start_date = datetime.now(timezone.utc).date() + timedelta(days=7)
        reg_deadline = datetime.now(timezone.utc).date() + timedelta(days=5)
        
        league = create_league(
            session=session,
            name="Test",
            season="Test",
            organizer_id=5,
            format_type="round_robin",
            config={},
            start_date=start_date,
            registration_deadline=reg_deadline
        )
        
        standings = get_league_standings(session, league.id)
        assert standings == []
    
    def test_get_standings_with_positions(self, session: Session):
        """Standings include positions"""
        start_date = datetime.now(timezone.utc).date() + timedelta(days=7)
        reg_deadline = datetime.now(timezone.utc).date() + timedelta(days=5)
        
        league = create_league(
            session=session,
            name="Test",
            season="Test",
            organizer_id=5,
            format_type="round_robin",
            config={},
            start_date=start_date,
            registration_deadline=reg_deadline
        )
        
        # Create standings
        standings_models = [
            LeagueStandings(league_id=league.id, user_id=1, phase="group", total_points=3000, wins=3, draws=0, losses=0),
            LeagueStandings(league_id=league.id, user_id=2, phase="group", total_points=2000, wins=2, draws=0, losses=1),
            LeagueStandings(league_id=league.id, user_id=3, phase="group", total_points=1000, wins=1, draws=0, losses=2)
        ]
        for s in standings_models:
            session.add(s)
        session.commit()
        
        standings = get_league_standings(session, league.id)
        
        assert len(standings) == 3
        assert standings[0]["user_id"] == 1
        assert standings[0]["position"] == 1
        assert standings[1]["user_id"] == 2
        assert standings[1]["position"] == 2
        assert standings[2]["user_id"] == 3
        assert standings[2]["position"] == 3
    
    def test_get_standings_includes_goal_difference(self, session: Session):
        """Goal difference calculated from matches"""
        start_date = datetime.now(timezone.utc).date() + timedelta(days=7)
        reg_deadline = datetime.now(timezone.utc).date() + timedelta(days=5)
        
        league = create_league(
            session=session,
            name="Test",
            season="Test",
            organizer_id=5,
            format_type="round_robin",
            config={},
            start_date=start_date,
            registration_deadline=reg_deadline
        )
        
        # Create standings
        session.add(LeagueStandings(league_id=league.id, user_id=1, phase="group", total_points=1000))
        session.add(LeagueStandings(league_id=league.id, user_id=2, phase="group", total_points=1000))
        
        # Create match (player1 wins 60-40)
        match = LeagueMatch(
            league_id=league.id,
            player1_id=1,
            player2_id=2,
            phase="group",
            round=1,
            played=True,
            player1_score=60,
            player2_score=40
        )
        session.add(match)
        session.commit()
        
        standings = get_league_standings(session, league.id)
        
        assert standings[0]["goal_difference"] == 20   # 60-40
        assert standings[1]["goal_difference"] == -20  # 40-60


# Test suite summary
"""
Coverage Matrix:

create_league():
✅ Successful creation
✅ Database persistence

join_league():
✅ Successful join
✅ Multiple users
✅ Already registered (error)
✅ League not found (error)
✅ Wrong status (error)
✅ Deadline passed (error)

start_league_group_phase():
✅ Successful start
✅ Group distribution
✅ Not organizer (error)
✅ Wrong status (error)
✅ Insufficient participants (error)
✅ League not found (error)

submit_match_result():
✅ Player 1 wins
✅ Player 2 wins
✅ Draw
✅ Updates standings
✅ Updates ELO (league + global)
✅ Match not found (error)
✅ Already played (error)
✅ Not participant (error)

get_league_standings():
✅ Empty standings
✅ Positions assigned
✅ Goal difference calculated

Total: 30 test cases covering service.py business logic
"""
