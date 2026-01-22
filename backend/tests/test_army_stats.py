"""Tests for army statistics tracking."""

from datetime import datetime, timedelta

import pytest
from app.league.models import (
    ArmyMatchupStats,
    ArmyStats,
    Group,
    League,
    LeaguePlayer,
    Match,
)
from app.league.service import update_army_stats_after_match
from sqlmodel import Session, select


class TestUpdateArmyStatsAfterMatch:
    """Test army statistics tracking after match confirmation."""

    def test_creates_faction_stats_on_first_match(self, session: Session):
        """Creates ArmyStats record for new faction."""
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

        player1 = LeaguePlayer(
            league_id=league.id,
            group_id=group.id,
            user_id=101,
            group_army_faction="Stormcast Eternals",
        )
        player2 = LeaguePlayer(
            league_id=league.id,
            group_id=group.id,
            user_id=102,
            group_army_faction="Ironjawz",
        )
        session.add_all([player1, player2])
        session.commit()

        update_army_stats_after_match(
            session=session,
            player1=player1,
            player2=player2,
            player1_score=72,
            player2_score=65,
            phase="group",
        )
        session.commit()

        stormcast_stats = session.scalars(
            select(ArmyStats).where(ArmyStats.faction == "Stormcast Eternals")
        ).first()
        ironjawz_stats = session.scalars(
            select(ArmyStats).where(ArmyStats.faction == "Ironjawz")
        ).first()

        assert stormcast_stats is not None
        assert stormcast_stats.games_played == 1
        assert stormcast_stats.wins == 1

        assert ironjawz_stats is not None
        assert ironjawz_stats.games_played == 1
        assert ironjawz_stats.losses == 1

    def test_updates_existing_faction_stats(self, session: Session):
        """Updates existing ArmyStats record."""
        # Pre-create stats
        existing_stats = ArmyStats(
            faction="Stormcast Eternals",
            games_played=5,
            wins=3,
            draws=1,
            losses=1,
        )
        session.add(existing_stats)
        session.commit()

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

        player1 = LeaguePlayer(
            league_id=league.id,
            group_id=group.id,
            user_id=101,
            group_army_faction="Stormcast Eternals",
        )
        player2 = LeaguePlayer(
            league_id=league.id,
            group_id=group.id,
            user_id=102,
            group_army_faction="Ironjawz",
        )
        session.add_all([player1, player2])
        session.commit()

        update_army_stats_after_match(
            session=session,
            player1=player1,
            player2=player2,
            player1_score=72,
            player2_score=65,
            phase="group",
        )
        session.commit()

        session.refresh(existing_stats)
        assert existing_stats.games_played == 6
        assert existing_stats.wins == 4

    def test_tracks_draws_correctly(self, session: Session):
        """Correctly tracks draw results."""
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

        player1 = LeaguePlayer(
            league_id=league.id,
            group_id=group.id,
            user_id=101,
            group_army_faction="Stormcast Eternals",
        )
        player2 = LeaguePlayer(
            league_id=league.id,
            group_id=group.id,
            user_id=102,
            group_army_faction="Ironjawz",
        )
        session.add_all([player1, player2])
        session.commit()

        # Draw
        update_army_stats_after_match(
            session=session,
            player1=player1,
            player2=player2,
            player1_score=70,
            player2_score=70,
            phase="group",
        )
        session.commit()

        stormcast_stats = session.scalars(
            select(ArmyStats).where(ArmyStats.faction == "Stormcast Eternals")
        ).first()
        ironjawz_stats = session.scalars(
            select(ArmyStats).where(ArmyStats.faction == "Ironjawz")
        ).first()

        assert stormcast_stats.draws == 1
        assert ironjawz_stats.draws == 1

    def test_skips_when_no_factions(self, session: Session):
        """Does nothing when neither player has faction set."""
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

        player1 = LeaguePlayer(
            league_id=league.id, group_id=group.id, user_id=101, group_army_faction=None
        )
        player2 = LeaguePlayer(
            league_id=league.id, group_id=group.id, user_id=102, group_army_faction=None
        )
        session.add_all([player1, player2])
        session.commit()

        update_army_stats_after_match(
            session=session,
            player1=player1,
            player2=player2,
            player1_score=72,
            player2_score=65,
            phase="group",
        )
        session.commit()

        all_stats = session.scalars(select(ArmyStats)).all()
        assert len(all_stats) == 0


class TestArmyMatchupStats:
    """Test faction vs faction statistics."""

    def test_creates_matchup_stats(self, session: Session):
        """Creates ArmyMatchupStats for faction vs faction."""
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

        player1 = LeaguePlayer(
            league_id=league.id,
            group_id=group.id,
            user_id=101,
            group_army_faction="Stormcast Eternals",
        )
        player2 = LeaguePlayer(
            league_id=league.id,
            group_id=group.id,
            user_id=102,
            group_army_faction="Ironjawz",
        )
        session.add_all([player1, player2])
        session.commit()

        update_army_stats_after_match(
            session=session,
            player1=player1,
            player2=player2,
            player1_score=72,
            player2_score=65,
            phase="group",
        )
        session.commit()

        # Stormcast vs Ironjawz
        stormcast_vs_ironjawz = session.scalars(
            select(ArmyMatchupStats).where(
                ArmyMatchupStats.faction == "Stormcast Eternals",
                ArmyMatchupStats.opponent_faction == "Ironjawz",
            )
        ).first()

        # Ironjawz vs Stormcast
        ironjawz_vs_stormcast = session.scalars(
            select(ArmyMatchupStats).where(
                ArmyMatchupStats.faction == "Ironjawz",
                ArmyMatchupStats.opponent_faction == "Stormcast Eternals",
            )
        ).first()

        assert stormcast_vs_ironjawz is not None
        assert stormcast_vs_ironjawz.games_played == 1
        assert stormcast_vs_ironjawz.wins == 1

        assert ironjawz_vs_stormcast is not None
        assert ironjawz_vs_stormcast.games_played == 1
        assert ironjawz_vs_stormcast.losses == 1

    def test_skips_matchup_stats_for_mirror_match(self, session: Session):
        """Does not create matchup stats for mirror matches (same faction)."""
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

        player1 = LeaguePlayer(
            league_id=league.id,
            group_id=group.id,
            user_id=101,
            group_army_faction="Stormcast Eternals",
        )
        player2 = LeaguePlayer(
            league_id=league.id,
            group_id=group.id,
            user_id=102,
            group_army_faction="Stormcast Eternals",  # Same faction
        )
        session.add_all([player1, player2])
        session.commit()

        update_army_stats_after_match(
            session=session,
            player1=player1,
            player2=player2,
            player1_score=72,
            player2_score=65,
            phase="group",
        )
        session.commit()

        # Global stats should still be updated (both players played)
        stormcast_stats = session.scalars(
            select(ArmyStats).where(ArmyStats.faction == "Stormcast Eternals")
        ).first()
        assert stormcast_stats.games_played == 2  # Both players counted

        # But matchup stats should not be created for mirror
        matchup_stats = session.scalars(select(ArmyMatchupStats)).all()
        assert len(matchup_stats) == 0

    def test_uses_knockout_faction_in_knockout_phase(self, session: Session):
        """Uses knockout_army_faction for knockout phase matches."""
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

        player1 = LeaguePlayer(
            league_id=league.id,
            group_id=group.id,
            user_id=101,
            group_army_faction="Stormcast Eternals",  # Different in group
            knockout_army_faction="Fyreslayers",  # Changed for knockout
        )
        player2 = LeaguePlayer(
            league_id=league.id,
            group_id=group.id,
            user_id=102,
            group_army_faction="Ironjawz",
            knockout_army_faction="Gloomspite Gitz",
        )
        session.add_all([player1, player2])
        session.commit()

        update_army_stats_after_match(
            session=session,
            player1=player1,
            player2=player2,
            player1_score=72,
            player2_score=65,
            phase="knockout",  # Knockout phase
        )
        session.commit()

        # Should use knockout factions
        fyreslayers_stats = session.scalars(
            select(ArmyStats).where(ArmyStats.faction == "Fyreslayers")
        ).first()
        gloomspite_stats = session.scalars(
            select(ArmyStats).where(ArmyStats.faction == "Gloomspite Gitz")
        ).first()

        assert fyreslayers_stats is not None
        assert fyreslayers_stats.wins == 1
        assert gloomspite_stats is not None
        assert gloomspite_stats.losses == 1

        # Group factions should not be updated
        stormcast_stats = session.scalars(
            select(ArmyStats).where(ArmyStats.faction == "Stormcast Eternals")
        ).first()
        assert stormcast_stats is None

    def test_handles_partial_faction_data(self, session: Session):
        """Handles case where only one player has faction set."""
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

        player1 = LeaguePlayer(
            league_id=league.id,
            group_id=group.id,
            user_id=101,
            group_army_faction="Stormcast Eternals",
        )
        player2 = LeaguePlayer(
            league_id=league.id,
            group_id=group.id,
            user_id=102,
            group_army_faction=None,  # No faction
        )
        session.add_all([player1, player2])
        session.commit()

        update_army_stats_after_match(
            session=session,
            player1=player1,
            player2=player2,
            player1_score=72,
            player2_score=65,
            phase="group",
        )
        session.commit()

        # Stormcast stats should be created
        stormcast_stats = session.scalars(
            select(ArmyStats).where(ArmyStats.faction == "Stormcast Eternals")
        ).first()
        assert stormcast_stats is not None
        assert stormcast_stats.wins == 1

        # No matchup stats (need both factions)
        matchup_stats = session.scalars(select(ArmyMatchupStats)).all()
        assert len(matchup_stats) == 0
