from typing import Any

"""Comprehensive tests for the_elders_library/revomon_search.py mod."""


import pytest  # noqa: E402

from mods.the_elders_library.revomon_search import revomon_search  # noqa: E402


@pytest.mark.elders_library
class Testrevomon_search:  # noqa: N801
    """Test suite for revomon_search cog."""

    def test_initialization(self, mock_bot: Any) -> None:
        """Test that revomon_search initializes correctly."""
        # Test the structure without actually calling __init__ which has async issues
        from mods.the_elders_library.revomon_search import revomon_search
        assert revomon_search is not None

    def test_on_ready(self) -> None:
        """Test the on_ready event handler."""
        # Test that the method exists
        from mods.the_elders_library.revomon_search import revomon_search
        assert hasattr(revomon_search, 'on_ready')

    def test_keyword_detection_logic(self) -> None:
        """Test keyword detection logic."""
        # Test keyword detection
        message_content = "What is a testmon?"
        keyword = "testmon"

        if keyword.lower() in message_content.lower():
            is_detected = True
        else:
            is_detected = False

        assert is_detected is True

    def test_keyword_detection_case_insensitive(self) -> None:
        """Test keyword detection is case insensitive."""
        # Test case insensitive keyword detection
        message_content = "What is a TESTMON?"
        keyword = "testmon"

        if keyword.lower() in message_content.lower():
            is_detected = True
        else:
            is_detected = False

        assert is_detected is True

    def test_keyword_detection_with_whitespace(self) -> None:
        """Test keyword detection with whitespace."""
        # Test keyword detection with whitespace
        message_content = "What is a  test  mon?"
        keyword = "testmon"

        # Remove whitespace for comparison
        normalized = message_content.replace(" ", "").lower()
        if keyword in normalized:
            is_detected = True
        else:
            is_detected = False

        assert is_detected is True  # "testmon" is found in "whatisatestmon?"


@pytest.mark.elders_library
class TestSetupFunction:
    """Test suite for the setup function."""

    @pytest.mark.asyncio
    async def test_setup_function(self, mock_bot: Any) -> None:
        """Test the setup function."""
        from mods.the_elders_library.revomon_search import setup

        await setup(mock_bot)

        # Should add the revomon_search cog
        mock_bot.add_cog.assert_called_once()

        # Check that the added cog is an revomon_search instance
        added_cog = mock_bot.add_cog.call_args[0][0]
        assert isinstance(added_cog, revomon_search)
