"""
Unit tests for herald/words.py - Exchange ID generation and validation

Tests the word-based exchange ID system that creates memorable IDs
in the format: adjective-noun-verb-XXXX
"""

import pytest
from herald.words import (
    generate_exchange_id,
    validate_exchange_id,
    ADJECTIVES,
    NOUNS_WARHAMMER,
    VERBS,
)


class TestGenerateExchangeID:
    """Tests for generate_exchange_id() function"""

    def test_generate_exchange_id__returns_string(self):
        """Test that generate_exchange_id returns a string"""
        exchange_id = generate_exchange_id(check_exists_callback=lambda x: False)
        assert isinstance(exchange_id, str)

    def test_generate_exchange_id__correct_format(self):
        """Test exchange ID follows format: adjective-noun-verb-XXXX"""
        exchange_id = generate_exchange_id(check_exists_callback=lambda x: False)

        parts = exchange_id.split("-")
        assert len(parts) == 4, f"Expected 4 parts, got {len(parts)}: {exchange_id}"

        adjective, noun, verb, mini_hash = parts

        # Check words are from dictionaries
        assert adjective in ADJECTIVES, f"Invalid adjective: {adjective}"
        assert noun in NOUNS_WARHAMMER, f"Invalid noun: {noun}"
        assert verb in VERBS, f"Invalid verb: {verb}"

        # Check hash format
        assert len(mini_hash) == 4, f"Hash should be 4 chars, got {len(mini_hash)}"
        assert all(
            c in "0123456789abcdef" for c in mini_hash
        ), f"Invalid hex chars in {mini_hash}"

    def test_generate_exchange_id__uses_words_from_dictionaries(self):
        """Test that all components come from defined word lists"""
        for _ in range(10):  # Test multiple generations
            exchange_id = generate_exchange_id(check_exists_callback=lambda x: False)
            adjective, noun, verb, mini_hash = exchange_id.split("-")

            assert adjective in ADJECTIVES
            assert noun in NOUNS_WARHAMMER
            assert verb in VERBS

    def test_generate_exchange_id__hash_is_hex(self):
        """Test that hash component is valid hexadecimal"""
        exchange_id = generate_exchange_id(check_exists_callback=lambda x: False)
        mini_hash = exchange_id.split("-")[3]

        # Should be convertible to int from hex
        try:
            int(mini_hash, 16)
        except ValueError:
            pytest.fail(f"Hash {mini_hash} is not valid hexadecimal")

    def test_generate_exchange_id__unique_generations(self):
        """Test that multiple calls generate different IDs"""
        ids = set()
        for _ in range(100):
            exchange_id = generate_exchange_id(check_exists_callback=lambda x: False)
            ids.add(exchange_id)

        # Should have at least 95 unique IDs out of 100 (allowing some collision chance)
        assert len(ids) >= 95, f"Only {len(ids)} unique IDs generated from 100 attempts"

    def test_generate_exchange_id__retries_on_collision(self):
        """Test that ID generation retries when callback indicates existence"""
        call_count = 0

        def check_exists(exchange_id):
            nonlocal call_count
            call_count += 1
            return call_count <= 2  # First 2 attempts "exist"

        exchange_id = generate_exchange_id(check_exists_callback=check_exists)

        assert call_count == 3, f"Expected 3 attempts, got {call_count}"
        assert exchange_id is not None
        assert validate_exchange_id(exchange_id)

    def test_generate_exchange_id__without_callback(self):
        """Test that ID generation works without existence check callback"""
        exchange_id = generate_exchange_id()  # No callback

        assert exchange_id is not None
        assert validate_exchange_id(exchange_id)

    def test_generate_exchange_id__fallback_after_max_attempts(self):
        """Test fallback to longer hash after max collision attempts"""
        call_count = 0

        def always_exists(exchange_id):
            nonlocal call_count
            call_count += 1
            return True  # Always say it exists

        exchange_id = generate_exchange_id(check_exists_callback=always_exists)

        # Should hit max attempts (10) and use fallback
        assert call_count == 10
        assert exchange_id is not None

        # Fallback ID has 6-char hash instead of 4
        parts = exchange_id.split("-")
        assert len(parts) == 4
        assert (
            len(parts[3]) == 6
        ), f"Fallback hash should be 6 chars, got {len(parts[3])}"


class TestValidateExchangeID:
    """Tests for validate_exchange_id() function"""

    def test_validate_exchange_id__valid_id_returns_true(self):
        """Test that valid exchange IDs return True"""
        valid_ids = [
            "crimson-marine-charges-7a2f",
            "void-necron-awakens-b3e1",
            "blessed-captain-purges-4d2c",
            "ancient-farseer-teleports-9c4d",
            "cursed-daemon-manifests-1f8e",
        ]

        for exchange_id in valid_ids:
            assert validate_exchange_id(exchange_id), f"Should validate: {exchange_id}"

    def test_validate_exchange_id__invalid_format_returns_false(self):
        """Test that invalid formats return False"""
        invalid_ids = [
            "invalid",  # Too few parts
            "too-short",  # Only 2 parts
            "a-b-c",  # Only 3 parts
            "a-b-c-d-e",  # Too many parts
        ]

        for exchange_id in invalid_ids:
            assert not validate_exchange_id(
                exchange_id
            ), f"Should reject: {exchange_id}"

    def test_validate_exchange_id__invalid_adjective_returns_false(self):
        """Test that invalid adjective word returns False"""
        invalid_id = "notadjective-marine-charges-7a2f"
        assert not validate_exchange_id(invalid_id)

    def test_validate_exchange_id__invalid_noun_returns_false(self):
        """Test that invalid noun word returns False"""
        invalid_id = "crimson-notnoun-charges-7a2f"
        assert not validate_exchange_id(invalid_id)

    def test_validate_exchange_id__invalid_verb_returns_false(self):
        """Test that invalid verb word returns False"""
        invalid_id = "crimson-marine-notverb-7a2f"
        assert not validate_exchange_id(invalid_id)

    def test_validate_exchange_id__invalid_hash_length_returns_false(self):
        """Test that wrong hash length returns False"""
        invalid_ids = [
            "crimson-marine-charges-7a",  # Too short (2 chars)
            "crimson-marine-charges-7a2",  # Too short (3 chars)
            "crimson-marine-charges-7a2f1",  # Too long (5 chars)
            "crimson-marine-charges-7a2f11",  # Too long (6 chars)
        ]

        for exchange_id in invalid_ids:
            assert not validate_exchange_id(
                exchange_id
            ), f"Should reject: {exchange_id}"

    def test_validate_exchange_id__non_hex_hash_returns_false(self):
        """Test that non-hexadecimal hash returns False"""
        invalid_ids = [
            "crimson-marine-charges-ZZZZ",  # Invalid hex chars
            "crimson-marine-charges-GHIJ",  # Invalid hex chars
            "crimson-marine-charges-!!!!",  # Special chars
        ]

        for exchange_id in invalid_ids:
            assert not validate_exchange_id(
                exchange_id
            ), f"Should reject: {exchange_id}"

    def test_validate_exchange_id__validates_generated_ids(self):
        """Test that generated IDs always validate"""
        for _ in range(20):
            exchange_id = generate_exchange_id(check_exists_callback=lambda x: False)
            assert validate_exchange_id(
                exchange_id
            ), f"Generated ID should validate: {exchange_id}"


class TestWordLists:
    """Tests for word list constants"""

    def test_adjectives_list__has_50_words(self):
        """Test ADJECTIVES list has exactly 50 words"""
        assert len(ADJECTIVES) == 50, f"Expected 50 adjectives, got {len(ADJECTIVES)}"

    def test_nouns_list__has_50_words(self):
        """Test NOUNS_WARHAMMER list has exactly 50 words"""
        assert (
            len(NOUNS_WARHAMMER) == 50
        ), f"Expected 50 nouns, got {len(NOUNS_WARHAMMER)}"

    def test_verbs_list__has_50_words(self):
        """Test VERBS list has exactly 50 words"""
        assert len(VERBS) == 50, f"Expected 50 verbs, got {len(VERBS)}"

    def test_adjectives_list__no_duplicates(self):
        """Test ADJECTIVES list has no duplicates"""
        assert len(ADJECTIVES) == len(set(ADJECTIVES)), "ADJECTIVES has duplicates"

    def test_nouns_list__no_duplicates(self):
        """Test NOUNS_WARHAMMER list has no duplicates"""
        assert len(NOUNS_WARHAMMER) == len(
            set(NOUNS_WARHAMMER)
        ), "NOUNS_WARHAMMER has duplicates"

    def test_verbs_list__no_duplicates(self):
        """Test VERBS list has no duplicates"""
        assert len(VERBS) == len(set(VERBS)), "VERBS has duplicates"

    def test_word_lists__all_lowercase(self):
        """Test that all words are lowercase"""
        for word in ADJECTIVES:
            assert word.islower(), f"Adjective '{word}' is not lowercase"

        for word in NOUNS_WARHAMMER:
            assert word.islower(), f"Noun '{word}' is not lowercase"

        for word in VERBS:
            assert word.islower(), f"Verb '{word}' is not lowercase"

    def test_word_lists__no_spaces(self):
        """Test that words don't contain spaces"""
        for word in ADJECTIVES + NOUNS_WARHAMMER + VERBS:
            assert " " not in word, f"Word '{word}' contains space"

    def test_word_lists__no_hyphens(self):
        """Test that words don't contain hyphens (would break format)"""
        for word in ADJECTIVES + NOUNS_WARHAMMER + VERBS:
            assert "-" not in word, f"Word '{word}' contains hyphen"
