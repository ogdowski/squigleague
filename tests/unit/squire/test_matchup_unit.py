"""
Unit Tests for Matchup System

Tests matchup creation, list submission, and battle plan generation logic.
Uses mocked database - no external dependencies.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
import uuid

from squire.matchup import (
    Matchup,
    MatchupPlayer,
    create_matchup,
    get_matchup,
    submit_list,
    _matchups
)
from squire.battle_plans import GameSystem, BattlePlan


class TestMatchupPlayer:
    """Test MatchupPlayer dataclass"""
    
    def test_create_matchup_player(self):
        """Test creating a matchup player"""
        player = MatchupPlayer(
            name="TestPlayer",
            army_list="Test Army\nUnit 1\nUnit 2"
        )
        
        assert player.name == "TestPlayer"
        assert player.army_list == "Test Army\nUnit 1\nUnit 2"
        assert isinstance(player.submitted_at, datetime)
    
    def test_matchup_player_timestamp(self):
        """Test that submission timestamp is set automatically"""
        player = MatchupPlayer(name="Player", army_list="Army")
        
        assert player.submitted_at is not None
        assert isinstance(player.submitted_at, datetime)
        assert player.submitted_at <= datetime.utcnow()


class TestMatchup:
    """Test Matchup dataclass"""
    
    def test_create_matchup(self):
        """Test creating a matchup"""
        matchup = Matchup(
            matchup_id="test123",
            game_system=GameSystem.AOS,
            creator_user_id="user123"
        )
        
        assert matchup.matchup_id == "test123"
        assert matchup.game_system == GameSystem.AOS
        assert matchup.creator_user_id == "user123"
        assert matchup.player1 is None
        assert matchup.player2 is None
        assert matchup.battle_plan is None
    
    def test_matchup_incomplete_initially(self):
        """Test that new matchup is not complete"""
        matchup = Matchup(
            matchup_id="test123",
            game_system=GameSystem.AOS
        )
        
        assert matchup.is_complete() is False
    
    def test_add_first_player(self):
        """Test adding first player to matchup"""
        matchup = Matchup(
            matchup_id="test123",
            game_system=GameSystem.AOS
        )
        
        is_complete = matchup.add_player("Player1", "Army1")
        
        assert is_complete is False  # Not complete yet
        assert matchup.player1 is not None
        assert matchup.player1.name == "Player1"
        assert matchup.player1.army_list == "Army1"
        assert matchup.player2 is None
        assert matchup.battle_plan is None
    
    def test_add_second_player_completes_matchup(self):
        """Test that adding second player completes matchup and generates battle plan"""
        matchup = Matchup(
            matchup_id="test123",
            game_system=GameSystem.WARHAMMER_40K
        )
        
        # Add first player
        matchup.add_player("Player1", "Army1")
        
        # Add second player
        is_complete = matchup.add_player("Player2", "Army2")
        
        assert is_complete is True
        assert matchup.is_complete() is True
        assert matchup.player2 is not None
        assert matchup.player2.name == "Player2"
        assert matchup.battle_plan is not None
        assert matchup.battle_plan.game_system == GameSystem.WARHAMMER_40K
    
    def test_add_third_player_raises_error(self):
        """Test that adding third player raises error"""
        matchup = Matchup(
            matchup_id="test123",
            game_system=GameSystem.AOS
        )
        
        matchup.add_player("Player1", "Army1")
        matchup.add_player("Player2", "Army2")
        
        with pytest.raises(ValueError, match="already has two players"):
            matchup.add_player("Player3", "Army3")
    
    def test_waiting_count_zero(self):
        """Test waiting count with no players"""
        matchup = Matchup(
            matchup_id="test123",
            game_system=GameSystem.AOS
        )
        
        assert matchup.get_waiting_count() == 0
    
    def test_waiting_count_one(self):
        """Test waiting count with one player"""
        matchup = Matchup(
            matchup_id="test123",
            game_system=GameSystem.AOS
        )
        matchup.add_player("Player1", "Army1")
        
        assert matchup.get_waiting_count() == 1
    
    def test_waiting_count_two(self):
        """Test waiting count with two players"""
        matchup = Matchup(
            matchup_id="test123",
            game_system=GameSystem.AOS
        )
        matchup.add_player("Player1", "Army1")
        matchup.add_player("Player2", "Army2")
        
        assert matchup.get_waiting_count() == 2


class TestMatchupFunctions:
    """Test module-level matchup functions"""
    
    def setup_method(self):
        """Clear matchups before each test"""
        _matchups.clear()
    
    def test_create_matchup_function(self):
        """Test create_matchup function"""
        matchup = create_matchup(GameSystem.AOS, creator_user_id="user123")
        
        assert matchup is not None
        assert matchup.matchup_id is not None
        assert len(matchup.matchup_id) > 0
        assert matchup.game_system == GameSystem.AOS
        assert matchup.creator_user_id == "user123"
        assert matchup.is_complete() is False
    
    def test_create_matchup_generates_unique_id(self):
        """Test that each matchup gets unique ID"""
        matchup1 = create_matchup(GameSystem.AOS)
        matchup2 = create_matchup(GameSystem.AOS)
        
        assert matchup1.matchup_id != matchup2.matchup_id
    
    def test_get_matchup_existing(self):
        """Test retrieving existing matchup"""
        matchup = create_matchup(GameSystem.WARHAMMER_40K)
        matchup_id = matchup.matchup_id
        
        retrieved = get_matchup(matchup_id)
        
        assert retrieved is not None
        assert retrieved.matchup_id == matchup_id
        assert retrieved.game_system == GameSystem.WARHAMMER_40K
    
    def test_get_matchup_nonexistent(self):
        """Test retrieving nonexistent matchup returns None"""
        retrieved = get_matchup("nonexistent_id")
        
        assert retrieved is None
    
    def test_submit_list_first_player(self):
        """Test submitting list as first player"""
        matchup = create_matchup(GameSystem.AOS)
        matchup_id = matchup.matchup_id
        
        result = submit_list(matchup_id, "Player1", "Army1")
        
        assert result is not None
        assert result.player1 is not None
        assert result.player1.name == "Player1"
        assert result.is_complete() is False
    
    def test_submit_list_second_player(self):
        """Test submitting list as second player"""
        matchup = create_matchup(GameSystem.AOS)
        matchup_id = matchup.matchup_id
        
        submit_list(matchup_id, "Player1", "Army1")
        result = submit_list(matchup_id, "Player2", "Army2")
        
        assert result.is_complete() is True
        assert result.battle_plan is not None
    
    def test_submit_list_nonexistent_matchup_raises_error(self):
        """Test submitting to nonexistent matchup raises ValueError"""
        with pytest.raises(ValueError, match="not found"):
            submit_list("nonexistent_id", "Player", "Army")


class TestMatchupWithUserTracking:
    """Test matchup creator tracking"""
    
    def setup_method(self):
        """Clear matchups before each test"""
        _matchups.clear()
    
    def test_matchup_stores_creator_id(self):
        """Test that matchup stores creator user ID"""
        user_id = str(uuid.uuid4())
        matchup = create_matchup(GameSystem.AOS, creator_user_id=user_id)
        
        assert matchup.creator_user_id == user_id
    
    def test_matchup_without_creator_id(self):
        """Test that matchup can be created without creator ID"""
        matchup = create_matchup(GameSystem.AOS)
        
        assert matchup.creator_user_id is None
    
    def test_retrieve_matchup_preserves_creator_id(self):
        """Test that retrieving matchup preserves creator ID"""
        user_id = str(uuid.uuid4())
        matchup = create_matchup(GameSystem.WARHAMMER_40K, creator_user_id=user_id)
        matchup_id = matchup.matchup_id
        
        retrieved = get_matchup(matchup_id)
        
        assert retrieved.creator_user_id == user_id
