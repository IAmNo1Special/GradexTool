from typing import Any

"""Tests for various keyword and search components in the elders library mod."""

from pathlib import Path  # noqa: E402

import pytest  # noqa: E402

# List of all previously untested components
COMPONENTS = [
    "abilities_keyword.py",
    "ability_search.py",
    "evchart_command.py",
    "evchart_keyword.py",
    "evolutions_command.py",
    "evolutions_keyword.py",
    "fruity_search.py",
    "fruitys_keyword.py",
    "help_keyword.py",
    "item_search.py",
    "items_keyword.py",
    "move_search.py",
    "moves_keyword.py",
    "moves_priority_keyword.py",
    "nature_search.py",
    "natures_keyword.py",
    "pokemon_keyword.py",
    "sapdaddy_command.py",
    "sapdaddy_keyword.py",
    "spawn_command.py",
    "spawn_keyword.py",
    "tierlist_keyword.py",
]


@pytest.mark.elders_library
class TestMissingComponentsStructure:
    """Test suite for verifying structure of missing components."""

    @pytest.mark.parametrize("component_file", COMPONENTS)
    def test_component_exists(self, component_file: Any) -> None:
        """Test that the component file exists."""
        file_path = (
            Path(__file__).parent.parent.parent.parent
            / "mods"
            / "the_elders_library"
            / component_file
        )
        assert file_path.exists(), f"File {component_file} should exist"

    @pytest.mark.parametrize("component_file", COMPONENTS)
    def test_component_syntax_valid(self, component_file: Any) -> None:
        """Test that the component file has valid Python syntax."""
        file_path = (
            Path(__file__).parent.parent.parent.parent
            / "mods"
            / "the_elders_library"
            / component_file
        )
        if not file_path.exists():
            pytest.skip(f"File {component_file} does not exist")

        try:
            import ast

            with open(file_path, encoding="utf-8") as f:
                ast.parse(f.read())
        except SyntaxError as e:
            pytest.fail(f"{component_file} contains syntax error: {e}")

    @pytest.mark.parametrize("component_file", COMPONENTS)
    def test_component_has_setup_function(self, component_file: Any) -> None:
        """Test that the component file defines an async setup function if it's a cog."""
        file_path = (
            Path(__file__).parent.parent.parent.parent
            / "mods"
            / "the_elders_library"
            / component_file
        )
        if not file_path.exists():
            pytest.skip(f"File {component_file} does not exist")

        content = file_path.read_text(encoding="utf-8")

        # Only check for setup function if it contains a Cog class
        if (
            "commands.Cog" in content
            or "app_commands" in content
            or "bot.listen" in content
        ):
            assert "async def setup" in content, (
                f"{component_file} should have an async setup function"
            )
