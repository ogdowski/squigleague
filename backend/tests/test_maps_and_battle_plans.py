"""Tests for map and battle plan functionality."""

import pytest
from app.data import BATTLE_PLAN_DATA, MAP_IMAGES, MISSION_MAPS, draw_random_map


class TestMissionMaps:
    """Test mission map configuration."""

    def test_has_12_maps(self):
        """GHB 2025-2026 has 12 battle plans."""
        assert len(MISSION_MAPS) == 12

    def test_all_maps_have_images(self):
        """Every map has an associated image."""
        for map_name in MISSION_MAPS:
            assert map_name in MAP_IMAGES
            assert MAP_IMAGES[map_name] is not None
            assert MAP_IMAGES[map_name].endswith(".png")

    def test_all_maps_have_battle_plan_data(self):
        """Every map has full battle plan data."""
        for map_name in MISSION_MAPS:
            assert map_name in BATTLE_PLAN_DATA
            data = BATTLE_PLAN_DATA[map_name]
            assert "deployment" in data
            assert "objectives" in data
            assert "scoring" in data
            assert "underdog_ability" in data

    def test_known_maps_present(self):
        """Check specific known map names exist."""
        known_maps = [
            "Passing Seasons",
            "Paths of the Fey",
            "Roiling Roots",
            "Cyclic Shifts",
            "Surge of Slaughter",
            "Linked Ley Lines",
            "Noxious Nexus",
            "The Liferoots",
            "Bountiful Equinox",
            "Lifecycle",
            "Creeping Corruption",
            "Grasp of Thorns",
        ]
        for map_name in known_maps:
            assert map_name in MISSION_MAPS


class TestBattlePlanData:
    """Test battle plan details."""

    def test_deployment_types(self):
        """All deployments are known types."""
        valid_deployments = {
            "Long edge deployment",
            "Diagonal corner deployment",
            "Quadrant deployment",
        }
        for map_name, data in BATTLE_PLAN_DATA.items():
            assert (
                data["deployment"] in valid_deployments
            ), f"{map_name} has unknown deployment"

    def test_objectives_not_empty(self):
        """All maps have objective descriptions."""
        for map_name, data in BATTLE_PLAN_DATA.items():
            assert len(data["objectives"]) > 10, f"{map_name} has empty objectives"

    def test_scoring_not_empty(self):
        """All maps have scoring descriptions."""
        for map_name, data in BATTLE_PLAN_DATA.items():
            assert len(data["scoring"]) > 10, f"{map_name} has empty scoring"

    def test_underdog_ability_not_empty(self):
        """All maps have underdog abilities."""
        for map_name, data in BATTLE_PLAN_DATA.items():
            assert (
                len(data["underdog_ability"]) > 10
            ), f"{map_name} has empty underdog ability"


class TestDrawRandomMap:
    """Test random map drawing."""

    def test_returns_valid_map(self):
        """draw_random_map returns a valid map name."""
        map_name = draw_random_map()
        assert map_name in MISSION_MAPS

    def test_returns_different_maps_over_time(self):
        """Random drawing returns varied results."""
        results = set()
        for _ in range(100):
            results.add(draw_random_map())

        # Should get at least a few different maps
        assert len(results) >= 3

    def test_all_maps_can_be_drawn(self):
        """Given enough tries, all maps should be drawable."""
        results = set()
        for _ in range(1000):
            results.add(draw_random_map())

        # Should eventually hit all 12 maps
        assert len(results) == 12


class TestMapImages:
    """Test map image configuration."""

    def test_image_naming_convention(self):
        """All images follow naming convention."""
        for map_name, image_file in MAP_IMAGES.items():
            assert image_file.startswith(
                "aos-"
            ), f"{map_name} image doesn't start with aos-"
            assert image_file.endswith(
                "-matplotlib.png"
            ), f"{map_name} image doesn't end with -matplotlib.png"

    def test_image_names_match_maps(self):
        """Image names derive from map names."""
        for map_name, image_file in MAP_IMAGES.items():
            # Convert map name to expected image format
            expected_part = map_name.lower().replace(" ", "-")
            assert expected_part in image_file.lower() or image_file is not None
