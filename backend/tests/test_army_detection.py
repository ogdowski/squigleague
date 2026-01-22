"""Tests for army faction detection."""

import pytest
from app.matchup.constants import ARMY_FACTIONS, detect_army_faction


class TestArmyFactions:
    """Test army factions list."""

    def test_all_grand_alliances_represented(self):
        """All four Grand Alliances should have factions."""
        order_factions = [
            "Cities of Sigmar",
            "Daughters of Khaine",
            "Fyreslayers",
            "Idoneth Deepkin",
            "Kharadron Overlords",
            "Lumineth Realm-lords",
            "Seraphon",
            "Stormcast Eternals",
            "Sylvaneth",
        ]
        chaos_factions = [
            "Blades of Khorne",
            "Disciples of Tzeentch",
            "Hedonites of Slaanesh",
            "Maggotkin of Nurgle",
            "Skaven",
            "Slaves to Darkness",
        ]
        death_factions = [
            "Flesh-eater Courts",
            "Nighthaunt",
            "Ossiarch Bonereapers",
            "Soulblight Gravelords",
        ]
        destruction_factions = [
            "Gloomspite Gitz",
            "Ironjawz",
            "Kruleboyz",
            "Ogor Mawtribes",
            "Sons of Behemat",
        ]

        for faction in (
            order_factions + chaos_factions + death_factions + destruction_factions
        ):
            assert faction in ARMY_FACTIONS, f"{faction} missing from ARMY_FACTIONS"


class TestDetectArmyFaction:
    """Test automatic army faction detection."""

    def test_detect_from_faction_name(self):
        """Detect faction from explicit faction name in list."""
        army_list = """Stormcast Eternals - Scions of the Storm

        Lord-Celestant on Stardrake - 500pts
        10x Liberators - 200pts
        """
        assert detect_army_faction(army_list) == "Stormcast Eternals"

    def test_detect_from_unit_keywords(self):
        """Detect faction from unit keywords."""
        # Ironjawz from Megaboss
        army_list = """Army List

        Megaboss on Maw-krusha - 480pts
        10x Brutes - 320pts
        """
        assert detect_army_faction(army_list) == "Ironjawz"

    def test_detect_gloomspite_from_squig(self):
        """Detect Gloomspite Gitz from squig keyword."""
        army_list = """My Army

        Loonboss on Giant Cave Squig
        20x Squig Hoppers
        """
        assert detect_army_faction(army_list) == "Gloomspite Gitz"

    def test_detect_fyreslayers_from_magmadroth(self):
        """Detect Fyreslayers from magmadroth keyword."""
        army_list = """Fyreslayer Force

        Auric Runefather on Magmadroth
        30x Vulkite Berzerkers
        """
        assert detect_army_faction(army_list) == "Fyreslayers"

    def test_detect_skaven_from_clanrat(self):
        """Detect Skaven from unit names."""
        army_list = """Evil Rats

        Grey Seer
        40x Clanrats
        20x Stormvermin
        """
        assert detect_army_faction(army_list) == "Skaven"

    def test_detect_sons_of_behemat(self):
        """Detect Sons of Behemat from mega-gargant."""
        army_list = """Big Boys

        Kraken-eater Mega-Gargant
        Warstomper Mega-Gargant
        """
        assert detect_army_faction(army_list) == "Sons of Behemat"

    def test_detect_soulblight_from_vampire(self):
        """Detect Soulblight Gravelords from vampire keyword."""
        army_list = """Undead Horde

        Vampire Lord
        40x Skeleton Warriors
        20x Zombies
        """
        assert detect_army_faction(army_list) == "Soulblight Gravelords"

    def test_detect_nighthaunt_from_chainrasp(self):
        """Detect Nighthaunt from unit names."""
        army_list = """Spooky Ghosts

        Spirit Torment
        40x Chainrasp Horde
        10x Grimghast Reapers
        """
        assert detect_army_faction(army_list) == "Nighthaunt"

    def test_detect_blades_of_khorne(self):
        """Detect Blades of Khorne from bloodthirster."""
        army_list = """Blood for the Blood God!

        Bloodthirster of Insensate Rage
        30x Bloodletters
        """
        assert detect_army_faction(army_list) == "Blades of Khorne"

    def test_detect_disciples_of_tzeentch(self):
        """Detect Disciples of Tzeentch from tzaangor."""
        army_list = """Change is Coming

        Lord of Change
        20x Tzaangors
        10x Pink Horrors
        """
        assert detect_army_faction(army_list) == "Disciples of Tzeentch"

    def test_case_insensitive_detection(self):
        """Detection should be case insensitive."""
        army_list = """STORMCAST ETERNALS

        LORD-CELESTANT
        """
        assert detect_army_faction(army_list) == "Stormcast Eternals"

        army_list_lower = """stormcast eternals

        liberators
        """
        assert detect_army_faction(army_list_lower) == "Stormcast Eternals"

    def test_returns_none_for_unknown(self):
        """Returns None if faction cannot be detected."""
        army_list = """Random Text

        Some Unit Name
        Another Unit
        """
        assert detect_army_faction(army_list) is None

    def test_returns_none_for_empty_string(self):
        """Returns None for empty input."""
        assert detect_army_faction("") is None
        assert detect_army_faction(None) is None

    def test_max_lines_parameter(self):
        """Only searches first N lines by default."""
        # Faction name is on line 12, outside default max_lines=10
        army_list = """Line 1
        Line 2
        Line 3
        Line 4
        Line 5
        Line 6
        Line 7
        Line 8
        Line 9
        Line 10
        Line 11
        Stormcast Eternals
        """
        # Should not find it with default max_lines=10
        assert detect_army_faction(army_list) is None

        # Should find it with max_lines=15
        assert detect_army_faction(army_list, max_lines=15) == "Stormcast Eternals"

    def test_exact_faction_name_priority(self):
        """Exact faction name should be matched before keywords."""
        # "Ironjawz" is both a faction name and a keyword
        army_list = """Ironjawz Army

        Some random unit
        """
        assert detect_army_faction(army_list) == "Ironjawz"

    def test_all_order_factions_detectable(self):
        """All Order factions should be detectable."""
        order_tests = [
            ("Cities of Sigmar\nFreeguild General", "Cities of Sigmar"),
            ("Daughters of Khaine\nMorathi", "Daughters of Khaine"),
            ("Fyreslayers\nAuric Runefather", "Fyreslayers"),
            ("Idoneth Deepkin\nAkhelian King", "Idoneth Deepkin"),
            ("Kharadron Overlords\nArkanaut Admiral", "Kharadron Overlords"),
            ("Lumineth Realm-lords\nTeclis", "Lumineth Realm-lords"),
            ("Seraphon\nSlann Starmaster", "Seraphon"),
            ("Stormcast Eternals\nLord-Celestant", "Stormcast Eternals"),
            ("Sylvaneth\nAlarielle the Everqueen", "Sylvaneth"),
        ]

        for army_list, expected in order_tests:
            result = detect_army_faction(army_list)
            assert result == expected, f"Failed to detect {expected}"

    def test_all_chaos_factions_detectable(self):
        """All Chaos factions should be detectable."""
        chaos_tests = [
            ("Blades of Khorne\nBloodthirster", "Blades of Khorne"),
            ("Disciples of Tzeentch\nLord of Change", "Disciples of Tzeentch"),
            ("Hedonites of Slaanesh\nKeeper of Secrets", "Hedonites of Slaanesh"),
            ("Maggotkin of Nurgle\nGreat Unclean One", "Maggotkin of Nurgle"),
            ("Skaven\nVerminlord", "Skaven"),
            ("Slaves to Darkness\nArchaon", "Slaves to Darkness"),
        ]

        for army_list, expected in chaos_tests:
            result = detect_army_faction(army_list)
            assert result == expected, f"Failed to detect {expected}"

    def test_all_death_factions_detectable(self):
        """All Death factions should be detectable."""
        death_tests = [
            ("Flesh-eater Courts\nAbhorrant Ghoul King", "Flesh-eater Courts"),
            ("Nighthaunt\nLady Olynder", "Nighthaunt"),
            ("Ossiarch Bonereapers\nKatakros", "Ossiarch Bonereapers"),
            ("Soulblight Gravelords\nMannfred", "Soulblight Gravelords"),
        ]

        for army_list, expected in death_tests:
            result = detect_army_faction(army_list)
            assert result == expected, f"Failed to detect {expected}"

    def test_all_destruction_factions_detectable(self):
        """All Destruction factions should be detectable."""
        destruction_tests = [
            ("Gloomspite Gitz\nLoonboss", "Gloomspite Gitz"),
            ("Ironjawz\nMegaboss", "Ironjawz"),
            ("Kruleboyz\nKillaboss", "Kruleboyz"),
            ("Ogor Mawtribes\nFrostlord on Stonehorn", "Ogor Mawtribes"),
            ("Sons of Behemat\nMega-Gargant", "Sons of Behemat"),
        ]

        for army_list, expected in destruction_tests:
            result = detect_army_faction(army_list)
            assert result == expected, f"Failed to detect {expected}"
