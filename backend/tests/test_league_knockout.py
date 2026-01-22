"""Tests for league knockout phase logic."""

from datetime import datetime, timedelta

import pytest
from app.league.models import Group, League, LeaguePlayer, Match
from app.league.service import (
    advance_to_next_knockout_round,
    all_round_matches_confirmed,
    generate_knockout_matches,
    get_advancement_rules,
    get_qualified_players,
    get_round_matches,
    get_round_winners,
)
from sqlmodel import Session


class TestGetAdvancementRules:
    """Test knockout advancement rules based on player count."""

    def test_8_to_11_players_2_groups_top4(self):
        """8-11 players: 2 groups, top 2 from each = top 4."""
        for count in range(8, 12):
            num_groups, direct, best = get_advancement_rules(count)
            assert num_groups == 2
            assert direct == 2  # 1st and 2nd from each group
            assert best == 0

    def test_12_to_15_players_3_groups_top4(self):
        """12-15 players: 3 groups, 1st places + best 2nd = top 4."""
        for count in range(12, 16):
            num_groups, direct, best = get_advancement_rules(count)
            assert num_groups == 3
            assert direct == 1  # Only 1st from each group
            assert best == 1  # Plus best 2nd place

    def test_16_to_19_players_4_groups_top8(self):
        """16-19 players: 4 groups, top 2 from each = top 8."""
        for count in range(16, 20):
            num_groups, direct, best = get_advancement_rules(count)
            assert num_groups == 4
            assert direct == 2
            assert best == 0

    def test_20_to_23_players_5_groups_top8(self):
        """20-23 players: 5 groups, 1st places + 3 best 2nd = top 8."""
        for count in range(20, 24):
            num_groups, direct, best = get_advancement_rules(count)
            assert num_groups == 5
            assert direct == 1
            assert best == 3

    def test_24_to_27_players_6_groups_top8(self):
        """24-27 players: 6 groups, 1st places + 2 best 2nd = top 8."""
        for count in range(24, 28):
            num_groups, direct, best = get_advancement_rules(count)
            assert num_groups == 6
            assert direct == 1
            assert best == 2

    def test_28_to_31_players_7_groups_top8(self):
        """28-31 players: 7 groups, 1st places + best 2nd = top 8."""
        for count in range(28, 32):
            num_groups, direct, best = get_advancement_rules(count)
            assert num_groups == 7
            assert direct == 1
            assert best == 1

    def test_32_plus_players_8_groups_top16(self):
        """32+ players: 8 groups, top 2 from each = top 16."""
        for count in [32, 40, 48]:
            num_groups, direct, best = get_advancement_rules(count)
            assert num_groups == 8
            assert direct == 2
            assert best == 0


class TestGetQualifiedPlayers:
    """Test knockout qualification logic."""

    def test_qualifies_top_players_from_each_group(self, session: Session):
        """Top players from each group qualify for knockout."""
        league = League(
            name="Test League",
            organizer_id=1,
            registration_end=datetime.utcnow() + timedelta(days=7),
            knockout_size=4,
            has_knockout_phase=True,
        )
        session.add(league)
        session.commit()

        # Create 2 groups with 4 players each
        group_a = Group(league_id=league.id, name="Group A")
        group_b = Group(league_id=league.id, name="Group B")
        session.add_all([group_a, group_b])
        session.commit()

        # Group A players (sorted by points)
        a1 = LeaguePlayer(
            league_id=league.id,
            group_id=group_a.id,
            user_id=101,
            total_points=3000,
            games_played=3,
        )
        a2 = LeaguePlayer(
            league_id=league.id,
            group_id=group_a.id,
            user_id=102,
            total_points=2500,
            games_played=3,
        )
        a3 = LeaguePlayer(
            league_id=league.id,
            group_id=group_a.id,
            user_id=103,
            total_points=2000,
            games_played=3,
        )
        a4 = LeaguePlayer(
            league_id=league.id,
            group_id=group_a.id,
            user_id=104,
            total_points=1500,
            games_played=3,
        )

        # Group B players
        b1 = LeaguePlayer(
            league_id=league.id,
            group_id=group_b.id,
            user_id=201,
            total_points=2800,
            games_played=3,
        )
        b2 = LeaguePlayer(
            league_id=league.id,
            group_id=group_b.id,
            user_id=202,
            total_points=2400,
            games_played=3,
        )
        b3 = LeaguePlayer(
            league_id=league.id,
            group_id=group_b.id,
            user_id=203,
            total_points=1800,
            games_played=3,
        )
        b4 = LeaguePlayer(
            league_id=league.id,
            group_id=group_b.id,
            user_id=204,
            total_points=1200,
            games_played=3,
        )

        session.add_all([a1, a2, a3, a4, b1, b2, b3, b4])
        session.commit()

        qualified = get_qualified_players(session, league)

        # Top 4: a1 (3000), b1 (2800), a2 (2500), b2 (2400)
        assert len(qualified) == 4
        qualified_ids = [p.user_id for p in qualified]
        assert 101 in qualified_ids  # a1
        assert 102 in qualified_ids  # a2
        assert 201 in qualified_ids  # b1
        assert 202 in qualified_ids  # b2

    def test_best_runners_up_qualify_when_uneven_groups(self, session: Session):
        """Best runners-up qualify when groups don't divide evenly."""
        league = League(
            name="Test League",
            organizer_id=1,
            registration_end=datetime.utcnow() + timedelta(days=7),
            knockout_size=4,
            has_knockout_phase=True,
        )
        session.add(league)
        session.commit()

        # Create 3 groups (12-15 players scenario)
        groups = []
        for i, name in enumerate(["A", "B", "C"]):
            group = Group(league_id=league.id, name=f"Group {name}")
            session.add(group)
            groups.append(group)
        session.commit()

        # Add 4 players per group
        all_players = []
        for i, group in enumerate(groups):
            for j in range(4):
                player = LeaguePlayer(
                    league_id=league.id,
                    group_id=group.id,
                    user_id=100 * (i + 1) + j,
                    total_points=3000 - j * 500 - i * 100,  # Vary points
                    games_played=3,
                )
                session.add(player)
                all_players.append(player)
        session.commit()

        qualified = get_qualified_players(session, league)

        # With 3 groups and knockout_size=4:
        # guaranteed_per_group = 4 // 3 = 1 (only 1st places)
        # extra_spots = 4 % 3 = 1 (best runner-up)
        assert len(qualified) == 4

    def test_qualified_sorted_by_points_for_seeding(self, session: Session):
        """Qualified players are sorted by points (best first for seeding)."""
        league = League(
            name="Test League",
            organizer_id=1,
            registration_end=datetime.utcnow() + timedelta(days=7),
            knockout_size=4,
            has_knockout_phase=True,
        )
        session.add(league)
        session.commit()

        group_a = Group(league_id=league.id, name="Group A")
        group_b = Group(league_id=league.id, name="Group B")
        session.add_all([group_a, group_b])
        session.commit()

        # a1 has most points, then b1, then a2, then b2
        a1 = LeaguePlayer(
            league_id=league.id,
            group_id=group_a.id,
            user_id=101,
            total_points=3500,
            games_played=3,
        )
        a2 = LeaguePlayer(
            league_id=league.id,
            group_id=group_a.id,
            user_id=102,
            total_points=2500,
            games_played=3,
        )
        b1 = LeaguePlayer(
            league_id=league.id,
            group_id=group_b.id,
            user_id=201,
            total_points=3000,
            games_played=3,
        )
        b2 = LeaguePlayer(
            league_id=league.id,
            group_id=group_b.id,
            user_id=202,
            total_points=2000,
            games_played=3,
        )

        session.add_all([a1, a2, b1, b2])
        session.commit()

        qualified = get_qualified_players(session, league)

        # Should be sorted: a1(3500) > b1(3000) > a2(2500) > b2(2000)
        assert qualified[0].total_points == 3500
        assert qualified[1].total_points == 3000
        assert qualified[2].total_points == 2500
        assert qualified[3].total_points == 2000


class TestGenerateKnockoutMatches:
    """Test knockout bracket generation."""

    def test_generates_correct_number_of_matches(self, session: Session):
        """Generates n/2 matches for n qualified players."""
        league = League(
            name="Test League",
            organizer_id=1,
            registration_end=datetime.utcnow() + timedelta(days=7),
            knockout_size=4,
            has_knockout_phase=True,
        )
        session.add(league)
        session.commit()

        group = Group(league_id=league.id, name="Group A")
        session.add(group)
        session.commit()

        # Add 4 players with points for seeding
        for i in range(4):
            player = LeaguePlayer(
                league_id=league.id,
                group_id=group.id,
                user_id=100 + i,
                total_points=3000 - i * 500,
                games_played=3,
            )
            session.add(player)
        session.commit()

        matches = generate_knockout_matches(session, league)

        # 4 players = 2 matches in first round (semi-finals)
        assert len(matches) == 2

    def test_pairs_best_vs_worst_seeding(self, session: Session):
        """Best seed plays worst seed (1v4, 2v3 for top 4)."""
        league = League(
            name="Test League",
            organizer_id=1,
            registration_end=datetime.utcnow() + timedelta(days=7),
            knockout_size=4,
            has_knockout_phase=True,
        )
        session.add(league)
        session.commit()

        group = Group(league_id=league.id, name="Group A")
        session.add(group)
        session.commit()

        # Add 4 players: p1(3000), p2(2500), p3(2000), p4(1500)
        players = []
        for i in range(4):
            player = LeaguePlayer(
                league_id=league.id,
                group_id=group.id,
                user_id=100 + i,
                total_points=3000 - i * 500,
                games_played=3,
            )
            session.add(player)
            players.append(player)
        session.commit()

        for p in players:
            session.refresh(p)

        matches = generate_knockout_matches(session, league)

        # Match 1: seed 1 (3000pts) vs seed 4 (1500pts)
        # Match 2: seed 2 (2500pts) vs seed 3 (2000pts)
        match_pairings = [(m.player1_id, m.player2_id) for m in matches]

        # Find which player has which seed
        seed1 = next(p for p in players if p.total_points == 3000)
        seed2 = next(p for p in players if p.total_points == 2500)
        seed3 = next(p for p in players if p.total_points == 2000)
        seed4 = next(p for p in players if p.total_points == 1500)

        # Verify 1v4 and 2v3 pairings
        assert (seed1.id, seed4.id) in match_pairings or (
            seed4.id,
            seed1.id,
        ) in match_pairings
        assert (seed2.id, seed3.id) in match_pairings or (
            seed3.id,
            seed2.id,
        ) in match_pairings

    def test_sets_correct_knockout_round(self, session: Session):
        """Matches have correct knockout_round set."""
        league = League(
            name="Test League",
            organizer_id=1,
            registration_end=datetime.utcnow() + timedelta(days=7),
            knockout_size=4,
            has_knockout_phase=True,
        )
        session.add(league)
        session.commit()

        group = Group(league_id=league.id, name="Group A")
        session.add(group)
        session.commit()

        for i in range(4):
            player = LeaguePlayer(
                league_id=league.id,
                group_id=group.id,
                user_id=100 + i,
                total_points=3000 - i * 500,
                games_played=3,
            )
            session.add(player)
        session.commit()

        matches = generate_knockout_matches(session, league)

        # Top 4 starts with semi-finals
        for match in matches:
            assert match.knockout_round == "semi"
            assert match.phase == "knockout"


class TestRoundMatches:
    """Test knockout round match queries."""

    def test_get_round_matches(self, session: Session):
        """Gets all matches for a specific round."""
        league = League(
            name="Test League",
            organizer_id=1,
            registration_end=datetime.utcnow() + timedelta(days=7),
        )
        session.add(league)
        session.commit()

        # Create matches in different rounds
        semi1 = Match(
            league_id=league.id,
            player1_id=1,
            player2_id=2,
            phase="knockout",
            knockout_round="semi",
            status="confirmed",
        )
        semi2 = Match(
            league_id=league.id,
            player1_id=3,
            player2_id=4,
            phase="knockout",
            knockout_round="semi",
            status="confirmed",
        )
        final = Match(
            league_id=league.id,
            player1_id=1,
            player2_id=3,
            phase="knockout",
            knockout_round="final",
            status="scheduled",
        )
        session.add_all([semi1, semi2, final])
        session.commit()

        semi_matches = get_round_matches(session, league.id, "semi")
        final_matches = get_round_matches(session, league.id, "final")

        assert len(semi_matches) == 2
        assert len(final_matches) == 1

    def test_all_round_matches_confirmed(self, session: Session):
        """Checks if all matches in round are confirmed."""
        league = League(
            name="Test League",
            organizer_id=1,
            registration_end=datetime.utcnow() + timedelta(days=7),
        )
        session.add(league)
        session.commit()

        semi1 = Match(
            league_id=league.id,
            player1_id=1,
            player2_id=2,
            phase="knockout",
            knockout_round="semi",
            status="confirmed",
        )
        semi2 = Match(
            league_id=league.id,
            player1_id=3,
            player2_id=4,
            phase="knockout",
            knockout_round="semi",
            status="pending_confirmation",
        )
        session.add_all([semi1, semi2])
        session.commit()

        # Not all confirmed
        assert all_round_matches_confirmed(session, league.id, "semi") is False

        # Confirm the second match
        semi2.status = "confirmed"
        session.commit()

        assert all_round_matches_confirmed(session, league.id, "semi") is True

    def test_get_round_winners(self, session: Session):
        """Gets winner IDs from completed round."""
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

        # Create players
        p1 = LeaguePlayer(league_id=league.id, group_id=group.id, user_id=101)
        p2 = LeaguePlayer(league_id=league.id, group_id=group.id, user_id=102)
        p3 = LeaguePlayer(league_id=league.id, group_id=group.id, user_id=103)
        p4 = LeaguePlayer(league_id=league.id, group_id=group.id, user_id=104)
        session.add_all([p1, p2, p3, p4])
        session.commit()

        # Create confirmed semi matches with scores
        semi1 = Match(
            league_id=league.id,
            player1_id=p1.id,
            player2_id=p2.id,
            phase="knockout",
            knockout_round="semi",
            status="confirmed",
            player1_score=72,
            player2_score=65,  # p1 wins
        )
        semi2 = Match(
            league_id=league.id,
            player1_id=p3.id,
            player2_id=p4.id,
            phase="knockout",
            knockout_round="semi",
            status="confirmed",
            player1_score=60,
            player2_score=70,  # p4 wins
        )
        session.add_all([semi1, semi2])
        session.commit()

        winners = get_round_winners(session, league.id, "semi")

        assert p1.id in winners
        assert p4.id in winners
        assert len(winners) == 2


class TestAdvanceToNextRound:
    """Test knockout round advancement."""

    def test_advances_when_all_matches_confirmed(self, session: Session):
        """Creates next round matches when current round is complete."""
        league = League(
            name="Test League",
            organizer_id=1,
            registration_end=datetime.utcnow() + timedelta(days=7),
            current_knockout_round="semi",
            days_per_match=14,
        )
        session.add(league)
        session.commit()

        group = Group(league_id=league.id, name="Group A")
        session.add(group)
        session.commit()

        # Create 4 players
        players = []
        for i in range(4):
            player = LeaguePlayer(
                league_id=league.id, group_id=group.id, user_id=100 + i
            )
            session.add(player)
            players.append(player)
        session.commit()

        # Create confirmed semi-final matches
        semi1 = Match(
            league_id=league.id,
            player1_id=players[0].id,
            player2_id=players[1].id,
            phase="knockout",
            knockout_round="semi",
            status="confirmed",
            player1_score=72,
            player2_score=65,
        )
        semi2 = Match(
            league_id=league.id,
            player1_id=players[2].id,
            player2_id=players[3].id,
            phase="knockout",
            knockout_round="semi",
            status="confirmed",
            player1_score=70,
            player2_score=68,
        )
        session.add_all([semi1, semi2])
        session.commit()

        new_round, new_matches = advance_to_next_knockout_round(session, league)

        assert new_round == "final"
        assert len(new_matches) == 1
        assert new_matches[0].knockout_round == "final"

    def test_does_not_advance_if_matches_pending(self, session: Session):
        """Does not advance if matches are not all confirmed."""
        league = League(
            name="Test League",
            organizer_id=1,
            registration_end=datetime.utcnow() + timedelta(days=7),
            current_knockout_round="semi",
        )
        session.add(league)
        session.commit()

        group = Group(league_id=league.id, name="Group A")
        session.add(group)
        session.commit()

        players = []
        for i in range(4):
            player = LeaguePlayer(
                league_id=league.id, group_id=group.id, user_id=100 + i
            )
            session.add(player)
            players.append(player)
        session.commit()

        # One confirmed, one pending
        semi1 = Match(
            league_id=league.id,
            player1_id=players[0].id,
            player2_id=players[1].id,
            phase="knockout",
            knockout_round="semi",
            status="confirmed",
            player1_score=72,
            player2_score=65,
        )
        semi2 = Match(
            league_id=league.id,
            player1_id=players[2].id,
            player2_id=players[3].id,
            phase="knockout",
            knockout_round="semi",
            status="pending_confirmation",
        )
        session.add_all([semi1, semi2])
        session.commit()

        new_round, new_matches = advance_to_next_knockout_round(session, league)

        assert new_round is None
        assert len(new_matches) == 0

    def test_returns_none_after_final(self, session: Session):
        """Returns None when trying to advance past final."""
        league = League(
            name="Test League",
            organizer_id=1,
            registration_end=datetime.utcnow() + timedelta(days=7),
            current_knockout_round="final",
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

        final = Match(
            league_id=league.id,
            player1_id=p1.id,
            player2_id=p2.id,
            phase="knockout",
            knockout_round="final",
            status="confirmed",
            player1_score=75,
            player2_score=60,
        )
        session.add(final)
        session.commit()

        new_round, new_matches = advance_to_next_knockout_round(session, league)

        assert new_round is None
        assert len(new_matches) == 0
