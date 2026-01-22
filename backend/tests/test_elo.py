"""Tests for ELO rating system."""

import pytest
from app.league.elo import (
    DEFAULT_K_FACTOR,
    DEFAULT_NEW_PLAYER_GAMES,
    DEFAULT_NEW_PLAYER_K,
    calculate_elo_change,
    calculate_expected_score,
    get_k_factor,
    get_or_create_player_elo,
    update_elo_after_match,
)
from app.league.models import AppSettings, PlayerElo
from sqlmodel import Session


class TestExpectedScore:
    """Test expected score calculations."""

    def test_equal_elo_gives_50_percent(self):
        """Equal ELO players should have 50% expected score."""
        expected = calculate_expected_score(1000, 1000)
        assert expected == pytest.approx(0.5, rel=0.001)

    def test_higher_elo_gives_higher_expected(self):
        """Higher ELO player should have >50% expected score."""
        expected = calculate_expected_score(1200, 1000)
        assert expected > 0.5
        assert expected < 1.0

    def test_lower_elo_gives_lower_expected(self):
        """Lower ELO player should have <50% expected score."""
        expected = calculate_expected_score(1000, 1200)
        assert expected < 0.5
        assert expected > 0.0

    def test_400_point_difference(self):
        """400 point difference should give ~91% expected for higher rated."""
        # ELO formula: E = 1 / (1 + 10^((Rb - Ra) / 400))
        # For 400 points: E = 1 / (1 + 10^(-1)) = 1 / 1.1 ≈ 0.909
        expected = calculate_expected_score(1400, 1000)
        assert expected == pytest.approx(0.909, rel=0.01)

    def test_symmetry(self):
        """Expected scores should sum to 1."""
        expected_higher = calculate_expected_score(1200, 1000)
        expected_lower = calculate_expected_score(1000, 1200)
        assert expected_higher + expected_lower == pytest.approx(1.0, rel=0.001)


class TestEloChange:
    """Test ELO change calculations."""

    def test_win_against_equal_opponent(self):
        """Win against equal opponent should give positive change."""
        change = calculate_elo_change(1000, 1000, result=1.0, k_factor=32)
        # Expected = 0.5, so change = 32 * (1.0 - 0.5) = 16
        assert change == 16

    def test_loss_against_equal_opponent(self):
        """Loss against equal opponent should give negative change."""
        change = calculate_elo_change(1000, 1000, result=0.0, k_factor=32)
        # Expected = 0.5, so change = 32 * (0.0 - 0.5) = -16
        assert change == -16

    def test_draw_against_equal_opponent(self):
        """Draw against equal opponent should give zero change."""
        change = calculate_elo_change(1000, 1000, result=0.5, k_factor=32)
        # Expected = 0.5, so change = 32 * (0.5 - 0.5) = 0
        assert change == 0

    def test_win_against_higher_rated(self):
        """Win against higher rated gives more points."""
        change_vs_equal = calculate_elo_change(1000, 1000, result=1.0, k_factor=32)
        change_vs_higher = calculate_elo_change(1000, 1200, result=1.0, k_factor=32)
        assert change_vs_higher > change_vs_equal

    def test_win_against_lower_rated(self):
        """Win against lower rated gives fewer points."""
        change_vs_equal = calculate_elo_change(1000, 1000, result=1.0, k_factor=32)
        change_vs_lower = calculate_elo_change(1000, 800, result=1.0, k_factor=32)
        assert change_vs_lower < change_vs_equal

    def test_higher_k_factor_gives_bigger_changes(self):
        """Higher K-factor results in bigger rating changes."""
        change_k32 = calculate_elo_change(1000, 1000, result=1.0, k_factor=32)
        change_k50 = calculate_elo_change(1000, 1000, result=1.0, k_factor=50)
        assert change_k50 > change_k32


class TestGetOrCreatePlayerElo:
    """Test player ELO record creation."""

    def test_creates_new_player_with_default_elo(self, session: Session):
        """New player should get default 1000 ELO."""
        # Use a user_id that doesn't exist yet
        player_elo = get_or_create_player_elo(session, user_id=999)

        assert player_elo.user_id == 999
        assert player_elo.elo == 1000
        assert player_elo.games_played == 0
        assert player_elo.k_factor_games == 0

    def test_returns_existing_player(self, session: Session):
        """Should return existing player record."""
        # Create player first
        existing = PlayerElo(user_id=888, elo=1150, games_played=10, k_factor_games=10)
        session.add(existing)
        session.commit()

        player_elo = get_or_create_player_elo(session, user_id=888)

        assert player_elo.user_id == 888
        assert player_elo.elo == 1150
        assert player_elo.games_played == 10


class TestGetKFactor:
    """Test K-factor selection logic."""

    def test_new_player_gets_higher_k(self, session: Session):
        """New player (fewer than threshold games) gets higher K."""
        player = PlayerElo(user_id=777, elo=1000, games_played=0, k_factor_games=2)
        session.add(player)
        session.commit()

        k_factor = get_k_factor(session, player)

        assert k_factor == DEFAULT_NEW_PLAYER_K  # 50

    def test_experienced_player_gets_global_k(self, session: Session):
        """Experienced player (at threshold games) gets global K."""
        player = PlayerElo(user_id=666, elo=1100, games_played=20, k_factor_games=10)
        session.add(player)
        session.commit()

        k_factor = get_k_factor(session, player)

        assert k_factor == DEFAULT_K_FACTOR  # 32


class TestUpdateEloAfterMatch:
    """Test full ELO update flow."""

    def test_winner_gains_loser_loses(self, session: Session):
        """Winner should gain ELO, loser should lose."""
        # Create two players
        player1 = PlayerElo(user_id=100, elo=1000, games_played=10, k_factor_games=10)
        player2 = PlayerElo(user_id=101, elo=1000, games_played=10, k_factor_games=10)
        session.add(player1)
        session.add(player2)
        session.commit()

        # Player 1 wins 72-65
        change1, change2 = update_elo_after_match(
            session=session,
            player1_user_id=100,
            player2_user_id=101,
            player1_score=72,
            player2_score=65,
        )

        session.refresh(player1)
        session.refresh(player2)

        assert change1 > 0  # Winner gains
        assert change2 < 0  # Loser loses
        assert change1 == -change2  # Zero-sum when equal ELO
        assert player1.elo > 1000
        assert player2.elo < 1000
        assert player1.games_played == 11
        assert player2.games_played == 11

    def test_draw_minimal_change(self, session: Session):
        """Draw between equal players should give zero change."""
        player1 = PlayerElo(user_id=200, elo=1000, games_played=10, k_factor_games=10)
        player2 = PlayerElo(user_id=201, elo=1000, games_played=10, k_factor_games=10)
        session.add(player1)
        session.add(player2)
        session.commit()

        # Draw (equal scores)
        change1, change2 = update_elo_after_match(
            session=session,
            player1_user_id=200,
            player2_user_id=201,
            player1_score=70,
            player2_score=70,
        )

        assert change1 == 0
        assert change2 == 0

    def test_upset_gives_more_points(self, session: Session):
        """Lower rated player winning should gain more points."""
        # Player 1 is underdog (lower ELO)
        player1 = PlayerElo(user_id=300, elo=900, games_played=10, k_factor_games=10)
        player2 = PlayerElo(user_id=301, elo=1100, games_played=10, k_factor_games=10)
        session.add(player1)
        session.add(player2)
        session.commit()

        # Underdog wins
        change1, change2 = update_elo_after_match(
            session=session,
            player1_user_id=300,
            player2_user_id=301,
            player1_score=75,
            player2_score=60,
        )

        # Underdog gains more than they would vs equal opponent
        assert change1 > 16  # More than K/2
        session.refresh(player1)
        assert player1.elo > 900

    def test_new_player_k_factor(self, session: Session):
        """New player should have higher K-factor applied."""
        # New player (k_factor_games=0)
        new_player = PlayerElo(user_id=400, elo=1000, games_played=0, k_factor_games=0)
        # Experienced player
        exp_player = PlayerElo(
            user_id=401, elo=1000, games_played=20, k_factor_games=20
        )
        session.add(new_player)
        session.add(exp_player)
        session.commit()

        # New player wins
        change_new, change_exp = update_elo_after_match(
            session=session,
            player1_user_id=400,
            player2_user_id=401,
            player1_score=80,
            player2_score=50,
        )

        # New player has K=50, experienced has K=32
        # For equal ELO win: change = K * 0.5
        # New player gains 25, experienced loses 16
        assert change_new == 25  # K=50 * 0.5
        assert change_exp == -16  # K=32 * 0.5

    def test_increments_games_played(self, session: Session):
        """Should increment games_played and k_factor_games."""
        player1 = PlayerElo(user_id=500, elo=1000, games_played=5, k_factor_games=3)
        player2 = PlayerElo(user_id=501, elo=1000, games_played=8, k_factor_games=6)
        session.add(player1)
        session.add(player2)
        session.commit()

        update_elo_after_match(
            session=session,
            player1_user_id=500,
            player2_user_id=501,
            player1_score=70,
            player2_score=60,
        )

        session.refresh(player1)
        session.refresh(player2)

        assert player1.games_played == 6
        assert player1.k_factor_games == 4
        assert player2.games_played == 9
        assert player2.k_factor_games == 7
