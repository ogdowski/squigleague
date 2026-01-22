"""Tests for matchup ID generation (word pairs)."""

import pytest
from app.matchup.words import generate_matchup_id


class TestGenerateMatchupId:
    """Test matchup ID generation."""

    def test_generates_string(self):
        """Returns a non-empty string."""
        matchup_id = generate_matchup_id()
        assert isinstance(matchup_id, str)
        assert len(matchup_id) > 0

    def test_contains_hyphen(self):
        """Generated ID contains hyphen separator."""
        matchup_id = generate_matchup_id()
        assert "-" in matchup_id

    def test_format_adjective_noun(self):
        """ID follows adjective-noun format."""
        matchup_id = generate_matchup_id()
        parts = matchup_id.split("-")
        assert len(parts) >= 2

    def test_generates_unique_ids(self):
        """Generates different IDs on multiple calls."""
        ids = set()
        for _ in range(100):
            ids.add(generate_matchup_id())

        # Should have mostly unique IDs (some collisions possible with limited word pool)
        assert len(ids) >= 50

    def test_lowercase(self):
        """Generated ID is lowercase."""
        matchup_id = generate_matchup_id()
        assert matchup_id == matchup_id.lower()

    def test_no_spaces(self):
        """Generated ID has no spaces."""
        for _ in range(50):
            matchup_id = generate_matchup_id()
            assert " " not in matchup_id

    def test_reasonable_length(self):
        """Generated ID has reasonable length."""
        for _ in range(50):
            matchup_id = generate_matchup_id()
            # Should be between 5 and 50 characters
            assert 5 <= len(matchup_id) <= 50
