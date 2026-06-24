"""Comprehensive tests for scripts/helpers.py."""

import pytest

from scripts.helpers import to_sentence_case


@pytest.mark.helpers
class TestToSentenceCase:
    """Test suite for the to_sentence_case function."""

    def test_basic_sentence_case(self) -> None:
        """Test basic sentence case conversion."""
        assert to_sentence_case("hello world") == "Hello world"
        assert to_sentence_case("this is a test") == "This is a test"

    def test_multiple_sentences(self) -> None:
        """Test conversion of multiple sentences."""
        assert to_sentence_case("hello. world") == "Hello. World"
        assert (
            to_sentence_case("first sentence. second sentence. third sentence")
            == "First sentence. Second sentence. Third sentence"
        )

    def test_preserves_internal_capitalization(self) -> None:
        """Test that internal capitalization is preserved."""
        assert to_sentence_case("hello World") == "Hello World"
        assert to_sentence_case("this is Python") == "This is Python"

    def test_empty_string(self) -> None:
        """Test handling of empty string."""
        assert to_sentence_case("") == ""

    def test_none_input(self) -> None:
        """Test handling of None input."""
        assert to_sentence_case(None) is None  # type: ignore[arg-type]

    def test_single_word(self) -> None:
        """Test single word conversion."""
        assert to_sentence_case("hello") == "Hello"
        assert to_sentence_case("WORLD") == "WORLD"

    def test_already_capitalized(self) -> None:
        """Test already capitalized sentences."""
        assert to_sentence_case("Hello world") == "Hello world"
        assert to_sentence_case("Hello. World") == "Hello. World"

    def test_preserves_special_characters(self) -> None:
        """Test preservation of special characters."""
        # The function only capitalizes first letter of sentences
        assert to_sentence_case("hello, world!") == "Hello, world!"
        # For "test? yes." - there's no period+space, so it treats as one sentence
        assert to_sentence_case("test? yes.") == "Test? yes."  # No change expected

    def test_numbers(self) -> None:
        """Test handling of numbers."""
        assert to_sentence_case("version 1.0 is released") == "Version 1.0 is released"
        assert to_sentence_case("item 1. item 2") == "Item 1. Item 2"

    def test_spaces_only(self) -> None:
        """Test handling of spaces only."""
        assert to_sentence_case("   ") == "   "

    def test_trailing_spaces(self) -> None:
        """Test handling of trailing spaces."""
        assert to_sentence_case("hello ") == "Hello "
        assert to_sentence_case("hello. world ") == "Hello. World "

    def test_leading_spaces(self) -> None:
        """Test handling of leading spaces."""
        assert to_sentence_case(" hello") == " hello"
        assert to_sentence_case(" hello. world") == " hello. World"

    def test_multiple_spaces_between_sentences(self) -> None:
        """Test handling of multiple spaces between sentences."""
        # The function doesn't normalize multiple spaces, it only capitalizes
        assert to_sentence_case("hello.  world") == "Hello.  world"  # Spaces preserved

    def test_no_periods(self) -> None:
        """Test text without periods."""
        assert to_sentence_case("hello world test") == "Hello world test"

    def test_uppercase_input(self) -> None:
        """Test uppercase input conversion."""
        assert to_sentence_case("HELLO WORLD") == "HELLO WORLD"
        assert to_sentence_case("HELLO. WORLD") == "HELLO. WORLD"

    def test_mixed_case_input(self) -> None:
        """Test mixed case input."""
        # The function capitalizes the first letter of each sentence
        assert (
            to_sentence_case("hELLo wORLD") == "HELLo wORLD"
        )  # First letter capitalized
        assert (
            to_sentence_case("hELLo. wORLD") == "HELLo. WORLD"
        )  # Both sentences capitalized

    def test_very_long_sentence(self) -> None:
        """Test very long sentence."""
        long_text = "this is a very long sentence that should still be processed correctly by the function without any issues"
        result = to_sentence_case(long_text)
        assert (
            result
            == "This is a very long sentence that should still be processed correctly by the function without any issues"
        )

    def test_only_period(self) -> None:
        """Test input with only a period."""
        assert to_sentence_case(".") == "."

    def test_period_with_space(self) -> None:
        """Test period followed by space."""
        assert to_sentence_case(". ") == ". "

    def test_sentence_with_newline_characters(self) -> None:
        """Test handling of newline characters (if any)."""
        text = "hello\nworld"
        # The function will capitalize first letter, preserving newline
        assert to_sentence_case(text) == "Hello\nworld"

    def test_unicode_characters(self) -> None:
        """Test handling of unicode characters."""
        assert to_sentence_case("héllo wörld") == "Héllo wörld"
        assert to_sentence_case("café. résumé") == "Café. Résumé"

    def test_consecutive_periods(self) -> None:
        """Test handling of consecutive periods."""
        assert to_sentence_case("hello.. world") == "Hello.. World"
        assert to_sentence_case("hello...world") == "Hello...world"


@pytest.mark.helpers
class TestEdgeCases:
    """Test edge cases for helper functions."""

    def test_very_short_text(self) -> None:
        """Test very short text."""
        assert to_sentence_case("a") == "A"
        assert to_sentence_case("a.") == "A."

    def test_only_numbers(self) -> None:
        """Test text with only numbers."""
        assert to_sentence_case("123") == "123"
        assert to_sentence_case("123. 456") == "123. 456"

    def test_mixed_punctuation(self) -> None:
        """Test mixed punctuation."""
        # Without period+space, treats as one sentence
        assert (
            to_sentence_case("hello, world! how are you?")
            == "Hello, world! how are you?"
        )
        # With period+space, capitalizes each sentence
        assert to_sentence_case("yes. no. maybe!") == "Yes. No. Maybe!"

    def test_tabs(self) -> None:
        """Test handling of tabs."""
        text = "hello\tworld"
        # The function capitalizes first letter, preserving tabs
        assert to_sentence_case(text) == "Hello\tworld"
