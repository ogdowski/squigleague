"""Tests for league service business logic."""

from datetime import datetime, timedelta

import pytest
from app.league.models import Group, League, LeaguePlayer, Match, PlayerElo
from app.league.service import (
    calculate_knockout_rounds,
    calculate_knockout_size,
    calculate_num_groups,
    confirm_match_result,
    draw_groups,
    generate_group_matches,
    get_allowed_knockout_sizes,
    get_group_standings,
    get_knockout_constraints,
    get_knockout_round_names,
    get_league_player_count,
    get_next_knockout_round,
    get_qualified_players,
    submit_match_result,
)
from sqlmodel import Session, select


class TestCalculateNumGroups:
    """Test group count calculation."""

    def test_8_players_makes_2_groups(self):
        """8 players with min=4, max=6 makes 2 groups of 4."""
        assert calculate_num_groups(8, min_group_size=4, max_group_size=6) == 2

    def test_20_players_makes_5_groups(self):
        """20 players with min=4, max=6 makes 5 groups of 4."""
        # min_groups = ceil(20/6) = 4, max_groups = 20/4 = 5
        # Prefer more groups (smaller sizes), so 5
        assert calculate_num_groups(20, min_group_size=4, max_group_size=6) == 5

    def test_16_players_makes_4_groups(self):
        """16 players with min=4, max=6 makes 4 groups of 4."""
        assert calculate_num_groups(16, min_group_size=4, max_group_size=6) == 4

    def test_24_players_makes_6_groups(self):
        """24 players with min=4, max=6 makes 6 groups of 4."""
        assert calculate_num_groups(24, min_group_size=4, max_group_size=6) == 6

    def test_fewer_than_min_makes_1_group(self):
        """Fewer players than min_group_size makes 1 group."""
        assert calculate_num_groups(3, min_group_size=4, max_group_size=6) == 1

    def test_10_players_makes_2_groups(self):
        """10 players makes 2 groups (5 each, within 4-6 range)."""
        # min_groups = ceil(10/6) = 2, max_groups = 10/4 = 2
        assert calculate_num_groups(10, min_group_size=4, max_group_size=6) == 2

    def test_13_players_makes_3_groups(self):
        """13 players makes 3 groups."""
        # min_groups = ceil(13/6) = 3, max_groups = 13/4 = 3
        assert calculate_num_groups(13, min_group_size=4, max_group_size=6) == 3


class TestKnockoutConstraints:
    """Test knockout size constraints."""

    def test_small_league_4_to_7_players(self):
        """4-7 players: top 2 only."""
        for player_count in range(4, 8):
            default, min_size, max_size = get_knockout_constraints(player_count)
            assert default == 2
            assert max_size == 2

    def test_medium_league_8_to_15_players(self):
        """8-15 players: default top 4, max top 8."""
        for player_count in range(8, 16):
            default, min_size, max_size = get_knockout_constraints(player_count)
            assert default == 4
            assert max_size == 8

    def test_large_league_16_to_47_players(self):
        """16-47 players: default top 8, max top 16."""
        for player_count in [16, 24, 32, 47]:
            default, min_size, max_size = get_knockout_constraints(player_count)
            assert default == 8
            assert max_size == 16

    def test_very_large_league_48_plus_players(self):
        """48+ players: default top 16, max top 32."""
        for player_count in [48, 64, 100]:
            default, min_size, max_size = get_knockout_constraints(player_count)
            assert default == 16
            assert max_size == 32


class TestCalculateKnockoutSize:
    """Test knockout size calculation."""

    def test_returns_default_when_no_config(self):
        """Returns default size when configured_size is None."""
        assert calculate_knockout_size(8) == 4
        assert calculate_knockout_size(16) == 8
        assert calculate_knockout_size(6) == 2

    def test_respects_valid_configured_size(self):
        """Uses configured size when valid."""
        assert calculate_knockout_size(16, configured_size=4) == 4
        assert calculate_knockout_size(20, configured_size=8) == 8

    def test_caps_at_player_count(self):
        """Cannot have knockout larger than player count."""
        # 6 players can't have top 8
        result = calculate_knockout_size(6, configured_size=8)
        assert result <= 6

    def test_caps_at_max_allowed(self):
        """Configured size capped at max for player count."""
        # 10 players max is top 8, not top 16
        result = calculate_knockout_size(10, configured_size=16)
        assert result <= 8


class TestGetAllowedKnockoutSizes:
    """Test allowed knockout sizes."""

    def test_small_league_only_top_2(self):
        """Small leagues can only have top 2."""
        assert get_allowed_knockout_sizes(5) == [2]
        assert get_allowed_knockout_sizes(7) == [2]

    def test_medium_league_options(self):
        """Medium leagues have multiple options."""
        sizes = get_allowed_knockout_sizes(12)
        assert 2 in sizes
        assert 4 in sizes
        assert 8 in sizes
        assert 16 not in sizes

    def test_large_league_options(self):
        """Large leagues have more options."""
        sizes = get_allowed_knockout_sizes(32)
        assert 2 in sizes
        assert 4 in sizes
        assert 8 in sizes
        assert 16 in sizes
        assert 32 not in sizes  # max is 16 for 32 players


class TestCalculateKnockoutRounds:
    """Test knockout round calculations."""

    def test_top_2_has_1_round(self):
        """Top 2 (final only) = 1 round."""
        assert calculate_knockout_rounds(2) == 1

    def test_top_4_has_2_rounds(self):
        """Top 4 = 2 rounds (semi + final)."""
        assert calculate_knockout_rounds(4) == 2

    def test_top_8_has_3_rounds(self):
        """Top 8 = 3 rounds (quarter + semi + final)."""
        assert calculate_knockout_rounds(8) == 3

    def test_top_16_has_4_rounds(self):
        """Top 16 = 4 rounds."""
        assert calculate_knockout_rounds(16) == 4


class TestGetKnockoutRoundNames:
    """Test knockout round name generation."""

    def test_top_2_rounds(self):
        """Top 2 only has final."""
        assert get_knockout_round_names(2) == ["final"]

    def test_top_4_rounds(self):
        """Top 4 has semi and final."""
        assert get_knockout_round_names(4) == ["semi", "final"]

    def test_top_8_rounds(self):
        """Top 8 has quarter, semi, and final."""
        assert get_knockout_round_names(8) == ["quarter", "semi", "final"]

    def test_top_16_rounds(self):
        """Top 16 has round_of_16, quarter, semi, and final."""
        assert get_knockout_round_names(16) == [
            "round_of_16",
            "quarter",
            "semi",
            "final",
        ]


class TestGetNextKnockoutRound:
    """Test knockout round progression."""

    def test_round_of_16_to_quarter(self):
        assert get_next_knockout_round("round_of_16") == "quarter"

    def test_quarter_to_semi(self):
        assert get_next_knockout_round("quarter") == "semi"

    def test_semi_to_final(self):
        assert get_next_knockout_round("semi") == "final"

    def test_final_returns_none(self):
        assert get_next_knockout_round("final") is None


class TestDrawGroups:
    """Test group drawing."""

    def test_creates_correct_number_of_groups(self, session: Session):
        """Drawing creates the expected number of groups."""
        league = League(
            name="Test League",
            organizer_id=1,
            registration_end=datetime.utcnow() + timedelta(days=7),
            min_group_size=4,
            max_group_size=6,
        )
        session.add(league)
        session.commit()

        # Add 8 players
        for i in range(8):
            player = LeaguePlayer(league_id=league.id, user_id=i + 100)
            session.add(player)
        session.commit()

        groups = draw_groups(session, league)

        assert len(groups) == 2  # 8 players / 4 min = 2 groups

    def test_assigns_all_players_to_groups(self, session: Session):
        """All players should be assigned to a group."""
        league = League(
            name="Test League",
            organizer_id=1,
            registration_end=datetime.utcnow() + timedelta(days=7),
            min_group_size=4,
            max_group_size=6,
        )
        session.add(league)
        session.commit()

        players = []
        for i in range(8):
            player = LeaguePlayer(league_id=league.id, user_id=i + 100)
            session.add(player)
            players.append(player)
        session.commit()

        draw_groups(session, league)

        for player in players:
            session.refresh(player)
            assert player.group_id is not None

    def test_groups_have_balanced_sizes(self, session: Session):
        """Groups should have roughly equal sizes."""
        league = League(
            name="Test League",
            organizer_id=1,
            registration_end=datetime.utcnow() + timedelta(days=7),
            min_group_size=4,
            max_group_size=6,
        )
        session.add(league)
        session.commit()

        # Add 10 players -> 2 groups of 5
        for i in range(10):
            player = LeaguePlayer(league_id=league.id, user_id=i + 100)
            session.add(player)
        session.commit()

        groups = draw_groups(session, league)

        # Count players per group
        for group in groups:
            session.refresh(group)
            count = len(
                session.scalars(
                    select(LeaguePlayer).where(LeaguePlayer.group_id == group.id)
                ).all()
            )
            assert 4 <= count <= 6


class TestGenerateGroupMatches:
    """Test group match generation."""

    def test_generates_round_robin_matches(self, session: Session):
        """Generates all possible pairings within each group."""
        league = League(
            name="Test League",
            organizer_id=1,
            registration_end=datetime.utcnow() + timedelta(days=7),
            min_group_size=4,
            max_group_size=6,
        )
        session.add(league)
        session.commit()

        # Create a group with 4 players
        group = Group(league_id=league.id, name="Group A")
        session.add(group)
        session.commit()

        players = []
        for i in range(4):
            player = LeaguePlayer(
                league_id=league.id, group_id=group.id, user_id=i + 100
            )
            session.add(player)
            players.append(player)
        session.commit()

        matches = generate_group_matches(session, league)

        # 4 players = 6 matches (n*(n-1)/2 = 4*3/2 = 6)
        assert len(matches) == 6

        # All matches should be in group phase
        for match in matches:
            assert match.phase == "group"
            assert match.status == "scheduled"


class TestGetGroupStandings:
    """Test group standings calculation."""

    def test_sorts_by_total_points(self, session: Session):
        """Standings sorted by total points descending."""
        league = League(
            name="Test League",
            organizer_id=1,
            registration_end=datetime.utcnow() + timedelta(days=7),
        )
        session.add(league)
        session.commit()

        group = Group(league_id=league.id, name="Group A")
        session.add(group)
        session.commit()

        # Create players with different points
        p1 = LeaguePlayer(
            league_id=league.id,
            group_id=group.id,
            user_id=101,
            total_points=3000,
            games_played=3,
        )
        p2 = LeaguePlayer(
            league_id=league.id,
            group_id=group.id,
            user_id=102,
            total_points=2500,
            games_played=3,
        )
        p3 = LeaguePlayer(
            league_id=league.id,
            group_id=group.id,
            user_id=103,
            total_points=2000,
            games_played=3,
        )
        session.add_all([p1, p2, p3])
        session.commit()

        standings = get_group_standings(session, group.id)

        assert standings[0].total_points == 3000
        assert standings[1].total_points == 2500
        assert standings[2].total_points == 2000

    def test_players_without_minimum_games_ranked_lower(self, session: Session):
        """Players who didn't meet minimum games are ranked lower."""
        league = League(
            name="Test League",
            organizer_id=1,
            registration_end=datetime.utcnow() + timedelta(days=7),
        )
        session.add(league)
        session.commit()

        group = Group(league_id=league.id, name="Group A")
        session.add(group)
        session.commit()

        # In 4-player group: max_games=3, min_required=2
        # Player with 2 games and 2000 pts should rank above
        # Player with 1 game and 3000 pts
        p1 = LeaguePlayer(
            league_id=league.id,
            group_id=group.id,
            user_id=101,
            total_points=3000,
            games_played=1,  # Didn't meet minimum
        )
        p2 = LeaguePlayer(
            league_id=league.id,
            group_id=group.id,
            user_id=102,
            total_points=2000,
            games_played=2,  # Met minimum
        )
        p3 = LeaguePlayer(
            league_id=league.id,
            group_id=group.id,
            user_id=103,
            total_points=1500,
            games_played=2,  # Met minimum
        )
        p4 = LeaguePlayer(
            league_id=league.id,
            group_id=group.id,
            user_id=104,
            total_points=1000,
            games_played=2,  # Met minimum
        )
        session.add_all([p1, p2, p3, p4])
        session.commit()

        standings = get_group_standings(session, group.id)

        # p2, p3, p4 should all rank above p1 despite lower points
        assert standings[0].user_id == 102  # 2000 pts, met minimum
        assert standings[1].user_id == 103  # 1500 pts, met minimum
        assert standings[2].user_id == 104  # 1000 pts, met minimum
        assert standings[3].user_id == 101  # 3000 pts, didn't meet minimum


class TestSubmitMatchResult:
    """Test match result submission."""

    def test_sets_pending_confirmation_status(self, session: Session):
        """Submitting result sets pending_confirmation status."""
        league = League(
            name="Test League",
            organizer_id=1,
            registration_end=datetime.utcnow() + timedelta(days=7),
        )
        session.add(league)
        session.commit()

        group = Group(league_id=league.id, name="Group A")
        session.add(group)
        session.commit()

        p1 = LeaguePlayer(league_id=league.id, group_id=group.id, user_id=101)
        p2 = LeaguePlayer(league_id=league.id, group_id=group.id, user_id=102)
        session.add_all([p1, p2])
        session.commit()

        match = Match(
            league_id=league.id,
            player1_id=p1.id,
            player2_id=p2.id,
            phase="group",
            status="scheduled",
        )
        session.add(match)
        session.commit()

        result = submit_match_result(
            session=session,
            match=match,
            player1_score=72,
            player2_score=65,
            submitted_by_id=101,
        )

        assert result.status == "pending_confirmation"
        assert result.player1_score == 72
        assert result.player2_score == 65

    def test_calculates_league_points(self, session: Session):
        """Submitting result calculates league points."""
        league = League(
            name="Test League",
            organizer_id=1,
            registration_end=datetime.utcnow() + timedelta(days=7),
            points_per_win=1000,
            points_per_draw=600,
            points_per_loss=200,
        )
        session.add(league)
        session.commit()

        group = Group(league_id=league.id, name="Group A")
        session.add(group)
        session.commit()

        p1 = LeaguePlayer(league_id=league.id, group_id=group.id, user_id=101)
        p2 = LeaguePlayer(league_id=league.id, group_id=group.id, user_id=102)
        session.add_all([p1, p2])
        session.commit()

        match = Match(
            league_id=league.id,
            player1_id=p1.id,
            player2_id=p2.id,
            phase="group",
            status="scheduled",
        )
        session.add(match)
        session.commit()

        result = submit_match_result(
            session=session,
            match=match,
            player1_score=72,
            player2_score=68,
            submitted_by_id=101,
        )

        # Win 72-68 (diff=4): 1000 + 54 = 1054
        # Loss 68-72 (diff=-4): 200 + 46 = 246
        assert result.player1_league_points == 1054
        assert result.player2_league_points == 246

    def test_updates_player_statistics(self, session: Session):
        """Submitting result updates player stats."""
        league = League(
            name="Test League",
            organizer_id=1,
            registration_end=datetime.utcnow() + timedelta(days=7),
        )
        session.add(league)
        session.commit()

        group = Group(league_id=league.id, name="Group A")
        session.add(group)
        session.commit()

        p1 = LeaguePlayer(
            league_id=league.id,
            group_id=group.id,
            user_id=101,
            games_played=0,
            games_won=0,
            games_lost=0,
            total_points=0,
        )
        p2 = LeaguePlayer(
            league_id=league.id,
            group_id=group.id,
            user_id=102,
            games_played=0,
            games_won=0,
            games_lost=0,
            total_points=0,
        )
        session.add_all([p1, p2])
        session.commit()

        match = Match(
            league_id=league.id,
            player1_id=p1.id,
            player2_id=p2.id,
            phase="group",
            status="scheduled",
        )
        session.add(match)
        session.commit()

        submit_match_result(
            session=session,
            match=match,
            player1_score=72,
            player2_score=68,
            submitted_by_id=101,
        )

        session.refresh(p1)
        session.refresh(p2)

        assert p1.games_played == 1
        assert p1.games_won == 1
        assert p2.games_played == 1
        assert p2.games_lost == 1


class TestConfirmMatchResult:
    """Test match result confirmation."""

    def test_sets_confirmed_status(self, session: Session):
        """Confirming result sets confirmed status."""
        league = League(
            name="Test League",
            organizer_id=1,
            registration_end=datetime.utcnow() + timedelta(days=7),
        )
        session.add(league)
        session.commit()

        group = Group(league_id=league.id, name="Group A")
        session.add(group)
        session.commit()

        p1 = LeaguePlayer(league_id=league.id, group_id=group.id, user_id=101)
        p2 = LeaguePlayer(league_id=league.id, group_id=group.id, user_id=102)
        session.add_all([p1, p2])
        session.commit()

        match = Match(
            league_id=league.id,
            player1_id=p1.id,
            player2_id=p2.id,
            phase="group",
            status="pending_confirmation",
            player1_score=72,
            player2_score=68,
            submitted_by_id=101,
        )
        session.add(match)
        session.commit()

        result = confirm_match_result(
            session=session,
            match=match,
            confirmed_by_id=102,
        )

        assert result.status == "confirmed"
        assert result.confirmed_by_id == 102
        assert result.confirmed_at is not None

    def test_updates_elo_on_confirm(self, session: Session):
        """Confirming result updates ELO ratings."""
        league = League(
            name="Test League",
            organizer_id=1,
            registration_end=datetime.utcnow() + timedelta(days=7),
        )
        session.add(league)
        session.commit()

        group = Group(league_id=league.id, name="Group A")
        session.add(group)
        session.commit()

        p1 = LeaguePlayer(league_id=league.id, group_id=group.id, user_id=101)
        p2 = LeaguePlayer(league_id=league.id, group_id=group.id, user_id=102)
        session.add_all([p1, p2])
        session.commit()

        # Create ELO records
        elo1 = PlayerElo(user_id=101, elo=1000, games_played=10, k_factor_games=10)
        elo2 = PlayerElo(user_id=102, elo=1000, games_played=10, k_factor_games=10)
        session.add_all([elo1, elo2])
        session.commit()

        match = Match(
            league_id=league.id,
            player1_id=p1.id,
            player2_id=p2.id,
            phase="group",
            status="pending_confirmation",
            player1_score=72,
            player2_score=68,
            submitted_by_id=101,
        )
        session.add(match)
        session.commit()

        result = confirm_match_result(
            session=session,
            match=match,
            confirmed_by_id=102,
        )

        session.refresh(elo1)
        session.refresh(elo2)

        # Winner gains ELO, loser loses
        assert elo1.elo > 1000
        assert elo2.elo < 1000
        assert result.player1_elo_before == 1000
        assert result.player1_elo_after > 1000
