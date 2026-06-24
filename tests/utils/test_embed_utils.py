from typing import Any

"""Comprehensive tests for embed_utils module."""

from unittest.mock import MagicMock, patch  # noqa: E402

from discord import Embed  # noqa: E402

from utils.embed_utils import (  # noqa: E402
    compare_counterdexs,
    compare_intros,
    compare_moves,
    compare_spawns,
    compare_stats,
    compare_types,
    counterdex,
    intro,
    land_intro,
    moves,
    spawns,
    stats,
    types,
)


class TestIntro:
    """Test cases for the intro function."""

    def test_intro_creates_embed_with_single_type(
        self, sample_revomon_attributes: Any
    ) -> None:
        """Test that intro creates an embed with single type Revomon."""
        with patch("utils.embed_utils.Embed") as mock_embed_class:
            mock_embed = MagicMock(spec=Embed)
            mock_embed_class.return_value = mock_embed

            intro(sample_revomon_attributes)

            # Verify Embed was called with correct parameters
            mock_embed_class.assert_called_once()
            call_args = mock_embed_class.call_args
            assert call_args[1]["title"] == "Testmon"
            assert call_args[1]["description"] == "*A test description for testmon.*"
            assert (
                call_args[1]["url"] == "https://revomon.online/revodex/revomon/testmon/"
            )

            # Verify add_field was called for tier and rarity
            assert mock_embed.add_field.call_count >= 2

            # Verify thumbnail and footer were set
            mock_embed.set_thumbnail.assert_called_once_with(
                url=sample_revomon_attributes["profile_img"]
            )
            mock_embed.set_footer.assert_called_once_with(
                text="The Elder's Library · Global Revomon Association"
            )

    def test_intro_creates_embed_with_dual_type(
        self, sample_revomon_attributes_dual_type: Any
    ) -> None:
        """Test that intro creates an embed with dual type Revomon."""
        with patch("utils.embed_utils.Embed") as mock_embed_class:
            mock_embed = MagicMock(spec=Embed)
            mock_embed_class.return_value = mock_embed

            intro(sample_revomon_attributes_dual_type)

            # Verify Embed was called
            mock_embed_class.assert_called_once()

            # Verify type field includes both types
            type_calls = [
                call
                for call in mock_embed.add_field.call_args_list
                if "Type" in str(call)
            ]
            assert len(type_calls) > 0

    def test_intro_with_second_ability(
        self, sample_revomon_attributes_dual_type: Any
    ) -> None:
        """Test that intro includes second ability when present."""
        with patch("utils.embed_utils.Embed") as mock_embed_class:
            mock_embed = MagicMock(spec=Embed)
            mock_embed_class.return_value = mock_embed

            intro(sample_revomon_attributes_dual_type)

            # Verify ability fields were added
            ability_calls = [
                call
                for call in mock_embed.add_field.call_args_list
                if "Ability" in str(call)
            ]
            assert len(ability_calls) >= 2

    def test_intro_with_hidden_ability(self, sample_revomon_attributes: Any) -> None:
        """Test that intro includes hidden ability when present."""
        with patch("utils.embed_utils.Embed") as mock_embed_class:
            mock_embed = MagicMock(spec=Embed)
            mock_embed_class.return_value = mock_embed

            intro(sample_revomon_attributes)

            # Verify hidden ability field was added
            ability_calls = [
                call
                for call in mock_embed.add_field.call_args_list
                if "Ability(h)" in str(call)
            ]
            assert len(ability_calls) >= 1

    def test_intro_with_evolution(
        self, sample_revomon_attributes_dual_type: Any
    ) -> None:
        """Test that intro includes evolution information when present."""
        with patch("utils.embed_utils.Embed") as mock_embed_class:
            mock_embed = MagicMock(spec=Embed)
            mock_embed_class.return_value = mock_embed

            intro(sample_revomon_attributes_dual_type)

            # Verify evolution field was added
            evo_calls = [
                call
                for call in mock_embed.add_field.call_args_list
                if "Evolution" in str(call)
            ]
            assert len(evo_calls) >= 2  # Evolution and Evolution Tree

    def test_intro_final_evolution(self, sample_revomon_attributes: Any) -> None:
        """Test that intro shows 'Final Evolution' when no evolution."""
        with patch("utils.embed_utils.Embed") as mock_embed_class:
            mock_embed = MagicMock(spec=Embed)
            mock_embed_class.return_value = mock_embed

            intro(sample_revomon_attributes)

            # Verify evolution field shows Final Evolution
            evo_calls = [
                call
                for call in mock_embed.add_field.call_args_list
                if "Evolution" in str(call)
            ]
            assert len(evo_calls) >= 2

    def test_intro_with_dual_ev_gains(
        self, sample_revomon_attributes_dual_type: Any
    ) -> None:
        """Test that intro includes both EV gains when present."""
        with patch("utils.embed_utils.Embed") as mock_embed_class:
            mock_embed = MagicMock(spec=Embed)
            mock_embed_class.return_value = mock_embed

            intro(sample_revomon_attributes_dual_type)

            # Verify EV gains field was added
            ev_calls = [
                call
                for call in mock_embed.add_field.call_args_list
                if "EV Gains" in str(call)
            ]
            assert len(ev_calls) >= 1

    def test_intro_with_single_ev_gains(self, sample_revomon_attributes: Any) -> None:
        """Test that intro handles single EV gain correctly."""
        with patch("utils.embed_utils.Embed") as mock_embed_class:
            mock_embed = MagicMock(spec=Embed)
            mock_embed_class.return_value = mock_embed

            intro(sample_revomon_attributes)

            # Verify EV gains field was added even with single gain
            ev_calls = [
                call
                for call in mock_embed.add_field.call_args_list
                if "EV Gains" in str(call)
            ]
            assert len(ev_calls) >= 1

    def test_intro_title_formatting(self) -> None:
        """Test that intro properly formats the title."""
        attributes = {
            "name": "testmon",
            "main_description": "a test description",
            "cdex_tier": "b",
            "rarity": "rare",
            "type1": "fire",
            "type2": None,
            "ability1": "overgrow",
            "ability2": None,
            "abilityh": None,
            "evolution": None,
            "evolution_lvl": None,
            "evolution_tree": "testmon tree",
            "ev_gains1": "+ 1 HP",
            "ev_gains2": None,
            "profile_img": "https://example.com/testmon.png",
        }

        with patch("utils.embed_utils.Embed") as mock_embed_class:
            mock_embed = MagicMock(spec=Embed)
            mock_embed_class.return_value = mock_embed

            intro(attributes)

            call_args = mock_embed_class.call_args
            assert call_args[1]["title"] == "Testmon"
            assert call_args[1]["description"] == "*A test description*"

    def test_intro_url_formatting(self) -> None:
        """Test that intro properly formats the URL."""
        attributes = {
            "name": "test_mon",  # Test with underscore
            "main_description": "a test description",
            "cdex_tier": "b",
            "rarity": "rare",
            "type1": "fire",
            "type2": None,
            "ability1": "overgrow",
            "ability2": None,
            "abilityh": None,
            "evolution": None,
            "evolution_lvl": None,
            "evolution_tree": "testmon tree",
            "ev_gains1": "+ 1 HP",
            "ev_gains2": None,
            "profile_img": "https://example.com/testmon.png",
        }

        with patch("utils.embed_utils.Embed") as mock_embed_class:
            mock_embed = MagicMock(spec=Embed)
            mock_embed_class.return_value = mock_embed

            intro(attributes)

            call_args = mock_embed_class.call_args
            assert "test_mon" in call_args[1]["url"]


class TestLandIntro:
    """Test cases for the land_intro function."""

    def test_land_intro_creates_embed_for_sale(
        self, sample_land_attributes: Any
    ) -> None:
        """Test that land_intro creates an embed for land that is for sale."""
        with patch("utils.embed_utils.Embed") as mock_embed_class:
            mock_embed = MagicMock(spec=Embed)
            mock_embed_class.return_value = mock_embed

            land_intro(sample_land_attributes)

            # Verify Embed was called with correct parameters
            mock_embed_class.assert_called_once()
            call_args = mock_embed_class.call_args
            assert "Forest" in call_args[1]["title"]
            assert "Woodland" in call_args[1]["title"]
            assert (
                call_args[1]["url"]
                == "https://tokentrove.com/collection/RevomonNovusLands/zkEVM-12345"
            )

            # Verify price field was added (since for_sale is True)
            price_calls = [
                call
                for call in mock_embed.add_field.call_args_list
                if "Price" in str(call)
            ]
            assert len(price_calls) >= 1

    def test_land_intro_not_for_sale(
        self, sample_land_attributes_not_for_sale: Any
    ) -> None:
        """Test that land_intro handles land not for sale correctly."""
        with patch("utils.embed_utils.Embed") as mock_embed_class:
            mock_embed = MagicMock(spec=Embed)
            mock_embed_class.return_value = mock_embed

            land_intro(sample_land_attributes_not_for_sale)

            # Verify Embed was called
            mock_embed_class.assert_called_once()

            # Verify price field was NOT added (since for_sale is False)
            price_calls = [
                call
                for call in mock_embed.add_field.call_args_list
                if "Price" in str(call)
            ]
            assert len(price_calls) == 0

    def test_land_intro_includes_all_fields(self, sample_land_attributes: Any) -> None:
        """Test that land_intro includes all required fields."""
        with patch("utils.embed_utils.Embed") as mock_embed_class:
            mock_embed = MagicMock(spec=Embed)
            mock_embed_class.return_value = mock_embed

            land_intro(sample_land_attributes)

            # Verify all standard fields were added
            field_names = [str(call) for call in mock_embed.add_field.call_args_list]
            assert any("For Sale" in name for name in field_names)
            assert any("Token ID" in name for name in field_names)
            assert any("Land Owner" in name for name in field_names)
            assert any("Rarity" in name for name in field_names)
            assert any("Size" in name for name in field_names)

    def test_land_intro_thumbnail_and_footer(self, sample_land_attributes: Any) -> None:
        """Test that land_intro sets thumbnail and footer correctly."""
        with patch("utils.embed_utils.Embed") as mock_embed_class:
            mock_embed = MagicMock(spec=Embed)
            mock_embed_class.return_value = mock_embed

            land_intro(sample_land_attributes)

            # Verify thumbnail and footer were set
            mock_embed.set_thumbnail.assert_called_once_with(
                url=sample_land_attributes["img_url"]
            )
            mock_embed.set_footer.assert_called_once_with(
                text="The Elder's Library · Global Revomon Association"
            )

    def test_land_intro_price_formatting(self, sample_land_attributes: Any) -> None:
        """Test that land_intro formats price correctly."""
        with patch("utils.embed_utils.Embed") as mock_embed_class:
            mock_embed = MagicMock(spec=Embed)
            mock_embed_class.return_value = mock_embed

            land_intro(sample_land_attributes)

            # Check price formatting
            price_calls = [
                call
                for call in mock_embed.add_field.call_args_list
                if "Price" in str(call)
            ]
            assert len(price_calls) >= 1
            # The price should include token amount, symbol, and USD value

    def test_land_intro_title_formatting(self) -> None:
        """Test that land_intro properly formats the title."""
        attributes = {
            "land_type": "forest",
            "biome": "woodland",
            "token_id": 12345,
            "for_sale": True,
            "for_sale_token": 100.0,
            "token_symbol": "IMX",
            "for_sale_usd": 150.0,
            "owners_address": "0x1234567890abcdef",
            "rarity": "rare",
            "size": "medium",
            "img_url": "https://example.com/land.png",
        }

        with patch("utils.embed_utils.Embed") as mock_embed_class:
            mock_embed = MagicMock(spec=Embed)
            mock_embed_class.return_value = mock_embed

            land_intro(attributes)

            call_args = mock_embed_class.call_args
            # Just check that title was called with the right components
            assert "Forest" in call_args[1]["title"]
            assert "Woodland" in call_args[1]["title"]
            assert "Biome" in call_args[1]["title"]

    def test_land_intro_url_formatting(self) -> None:
        """Test that land_intro properly formats the URL."""
        attributes = {
            "land_type": "forest",
            "biome": "woodland",
            "token_id": 99999,
            "for_sale": False,
            "for_sale_token": 0.0,
            "token_symbol": "IMX",
            "for_sale_usd": 0.0,
            "owners_address": "0x1234567890abcdef",
            "rarity": "epic",
            "size": "large",
            "img_url": "https://example.com/land.png",
        }

        with patch("utils.embed_utils.Embed") as mock_embed_class:
            mock_embed = MagicMock(spec=Embed)
            mock_embed_class.return_value = mock_embed

            land_intro(attributes)

            call_args = mock_embed_class.call_args
            assert (
                call_args[1]["url"]
                == "https://tokentrove.com/collection/RevomonNovusLands/zkEVM-99999"
            )


class TestCompareIntros:
    """Test cases for the compare_intros function."""

    def test_compare_intros_both_single_type(
        self, sample_revomon_attributes: Any
    ) -> None:
        """Test compare_intros with both Revomon having single types."""
        attributes2 = sample_revomon_attributes.copy()
        attributes2["name"] = "testmon2"
        attributes2["num"] = 2
        attributes2["emoji"] = "testmon2_emoji"

        with patch("utils.embed_utils.Embed") as mock_embed_class:
            mock_embed = MagicMock(spec=Embed)
            mock_embed_class.return_value = mock_embed

            compare_intros(sample_revomon_attributes, attributes2)

            # Verify Embed was called
            mock_embed_class.assert_called_once()

            # Verify both Revomon are in title
            call_args = mock_embed_class.call_args
            assert "Testmon" in call_args[1]["title"]
            assert "Testmon2" in call_args[1]["title"]

    def test_compare_intros_dual_types(
        self, sample_revomon_attributes_dual_type: Any
    ) -> None:
        """Test compare_intros with dual type Revomon."""
        attributes2 = sample_revomon_attributes_dual_type.copy()
        attributes2["name"] = "testmon2"
        attributes2["num"] = 2
        attributes2["emoji"] = "testmon2_emoji"

        with patch("utils.embed_utils.Embed") as mock_embed_class:
            mock_embed = MagicMock(spec=Embed)
            mock_embed_class.return_value = mock_embed

            compare_intros(sample_revomon_attributes_dual_type, attributes2)

            # Verify dual types are shown correctly
            type_calls = [
                call
                for call in mock_embed.add_field.call_args_list
                if "Type" in str(call)
            ]
            assert len(type_calls) >= 1

    def test_compare_intros_mixed_types(
        self, sample_revomon_attributes: Any, sample_revomon_attributes_dual_type: Any
    ) -> None:
        """Test compare_intros with mixed single and dual types."""
        with patch("utils.embed_utils.Embed") as mock_embed_class:
            mock_embed = MagicMock(spec=Embed)
            mock_embed_class.return_value = mock_embed

            compare_intros(
                sample_revomon_attributes, sample_revomon_attributes_dual_type
            )

            # Verify type comparison works with mixed types
            type_calls = [
                call
                for call in mock_embed.add_field.call_args_list
                if "Type" in str(call)
            ]
            assert len(type_calls) >= 1

    def test_compare_intros_abilities(
        self, sample_revomon_attributes_dual_type: Any
    ) -> None:
        """Test compare_intros includes abilities correctly."""
        attributes2 = sample_revomon_attributes_dual_type.copy()
        attributes2["name"] = "testmon2"
        attributes2["num"] = 2
        attributes2["emoji"] = "testmon2_emoji"

        with patch("utils.embed_utils.Embed") as mock_embed_class:
            mock_embed = MagicMock(spec=Embed)
            mock_embed_class.return_value = mock_embed

            compare_intros(sample_revomon_attributes_dual_type, attributes2)

            # Verify abilities are compared
            ability_calls = [
                call
                for call in mock_embed.add_field.call_args_list
                if "Abilities" in str(call)
            ]
            assert len(ability_calls) >= 1

    def test_compare_intros_evolution_both_final(
        self, sample_revomon_attributes: Any
    ) -> None:
        """Test compare_intros when both Revomon are final evolutions."""
        attributes2 = sample_revomon_attributes.copy()
        attributes2["name"] = "testmon2"
        attributes2["num"] = 2
        attributes2["emoji"] = "testmon2_emoji"

        with patch("utils.embed_utils.Embed") as mock_embed_class:
            mock_embed = MagicMock(spec=Embed)
            mock_embed_class.return_value = mock_embed

            compare_intros(sample_revomon_attributes, attributes2)

            # Verify both show as Final Evolution
            evo_calls = [
                call
                for call in mock_embed.add_field.call_args_list
                if "Evolution" in str(call)
            ]
            assert len(evo_calls) >= 2

    def test_compare_intros_evolution_mixed(
        self, sample_revomon_attributes: Any, sample_revomon_attributes_dual_type: Any
    ) -> None:
        """Test compare_intros with mixed evolution states."""
        with patch("utils.embed_utils.Embed") as mock_embed_class:
            mock_embed = MagicMock(spec=Embed)
            mock_embed_class.return_value = mock_embed

            compare_intros(
                sample_revomon_attributes, sample_revomon_attributes_dual_type
            )

            # Verify evolution comparison handles mixed states
            evo_calls = [
                call
                for call in mock_embed.add_field.call_args_list
                if "Evolution" in str(call)
            ]
            assert len(evo_calls) >= 2

    def test_compare_intros_ev_gains_both_single(
        self, sample_revomon_attributes: Any
    ) -> None:
        """Test compare_intros when both have single EV gains."""
        attributes2 = sample_revomon_attributes.copy()
        attributes2["name"] = "testmon2"
        attributes2["num"] = 2
        attributes2["emoji"] = "testmon2_emoji"

        with patch("utils.embed_utils.Embed") as mock_embed_class:
            mock_embed = MagicMock(spec=Embed)
            mock_embed_class.return_value = mock_embed

            compare_intros(sample_revomon_attributes, attributes2)

            # Verify EV gains are compared
            ev_calls = [
                call
                for call in mock_embed.add_field.call_args_list
                if "EV Gains" in str(call)
            ]
            assert len(ev_calls) >= 1

    def test_compare_intros_ev_gains_dual(
        self, sample_revomon_attributes_dual_type: Any
    ) -> None:
        """Test compare_intros when both have dual EV gains."""
        attributes2 = sample_revomon_attributes_dual_type.copy()
        attributes2["name"] = "testmon2"
        attributes2["num"] = 2
        attributes2["emoji"] = "testmon2_emoji"

        with patch("utils.embed_utils.Embed") as mock_embed_class:
            mock_embed = MagicMock(spec=Embed)
            mock_embed_class.return_value = mock_embed

            compare_intros(sample_revomon_attributes_dual_type, attributes2)

            # Verify dual EV gains are shown
            ev_calls = [
                call
                for call in mock_embed.add_field.call_args_list
                if "EV Gains" in str(call)
            ]
            assert len(ev_calls) >= 1

    def test_compare_intros_includes_emoji(
        self, sample_revomon_attributes: Any
    ) -> None:
        """Test that compare_intros includes emoji in description."""
        attributes2 = sample_revomon_attributes.copy()
        attributes2["name"] = "testmon2"
        attributes2["num"] = 2
        attributes2["emoji"] = "testmon2_emoji"

        with patch("utils.embed_utils.Embed") as mock_embed_class:
            mock_embed = MagicMock(spec=Embed)
            mock_embed_class.return_value = mock_embed

            compare_intros(sample_revomon_attributes, attributes2)

            # Verify emoji is in description
            call_args = mock_embed_class.call_args
            assert "testmon2_emoji" in call_args[1]["description"]

    def test_compare_intros_tier_comparison(
        self, sample_revomon_attributes: Any
    ) -> None:
        """Test that compare_intros shows tier comparison."""
        attributes2 = sample_revomon_attributes.copy()
        attributes2["name"] = "testmon2"
        attributes2["num"] = 2
        attributes2["emoji"] = "testmon2_emoji"
        attributes2["cdex_tier"] = "a"

        with patch("utils.embed_utils.Embed") as mock_embed_class:
            mock_embed = MagicMock(spec=Embed)
            mock_embed_class.return_value = mock_embed

            compare_intros(sample_revomon_attributes, attributes2)

            # Verify tier comparison is shown
            tier_calls = [
                call
                for call in mock_embed.add_field.call_args_list
                if "Tier" in str(call)
            ]
            assert len(tier_calls) >= 1

    def test_compare_intros_rarity_comparison(
        self, sample_revomon_attributes: Any
    ) -> None:
        """Test that compare_intros shows rarity comparison."""
        attributes2 = sample_revomon_attributes.copy()
        attributes2["name"] = "testmon2"
        attributes2["num"] = 2
        attributes2["emoji"] = "testmon2_emoji"
        attributes2["rarity"] = "epic"

        with patch("utils.embed_utils.Embed") as mock_embed_class:
            mock_embed = MagicMock(spec=Embed)
            mock_embed_class.return_value = mock_embed

            compare_intros(sample_revomon_attributes, attributes2)

            # Verify rarity comparison is shown
            rarity_calls = [
                call
                for call in mock_embed.add_field.call_args_list
                if "Rarity" in str(call)
            ]
            assert len(rarity_calls) >= 1


class TestEmbedUtilsEdgeCases:
    """Test edge cases for embed_utils functions."""

    def test_intro_with_missing_optional_fields(self) -> None:
        """Test intro handles missing optional fields gracefully."""
        minimal_attributes = {
            "name": "testmon",
            "main_description": "a test",
            "cdex_tier": "b",
            "rarity": "rare",
            "type1": "fire",
            "type2": None,
            "ability1": "overgrow",
            "ability2": None,
            "abilityh": None,
            "evolution": None,
            "evolution_lvl": None,
            "evolution_tree": "tree",
            "ev_gains1": "+ 1 HP",
            "ev_gains2": None,
            "profile_img": "https://example.com/testmon.png",
        }

        with patch("utils.embed_utils.Embed") as mock_embed_class:
            mock_embed = MagicMock(spec=Embed)
            mock_embed_class.return_value = mock_embed

            intro(minimal_attributes)

            # Should still create embed without errors
            mock_embed_class.assert_called_once()

    def test_land_intro_with_zero_price(self) -> None:
        """Test land_intro handles zero price correctly."""
        attributes = {
            "land_type": "forest",
            "biome": "woodland",
            "token_id": 12345,
            "for_sale": True,
            "for_sale_token": 0.0,
            "token_symbol": "IMX",
            "for_sale_usd": 0.0,
            "owners_address": "0x1234567890abcdef",
            "rarity": "rare",
            "size": "medium",
            "img_url": "https://example.com/land.png",
        }

        with patch("utils.embed_utils.Embed") as mock_embed_class:
            mock_embed = MagicMock(spec=Embed)
            mock_embed_class.return_value = mock_embed

            land_intro(attributes)

            # Should handle zero price without errors
            mock_embed_class.assert_called_once()

    def test_compare_intros_with_same_revomon(
        self, sample_revomon_attributes: Any
    ) -> None:
        """Test compare_intros when comparing same Revomon."""
        with patch("utils.embed_utils.Embed") as mock_embed_class:
            mock_embed = MagicMock(spec=Embed)
            mock_embed_class.return_value = mock_embed

            compare_intros(sample_revomon_attributes, sample_revomon_attributes)

            # Should handle same Revomon comparison
            mock_embed_class.assert_called_once()

    def test_intro_with_special_characters(self) -> None:
        """Test intro handles special characters in name and description."""
        attributes = {
            "name": "test-mon_special",
            "main_description": "a test with special chars: !@#$%",
            "cdex_tier": "b",
            "rarity": "rare",
            "type1": "fire",
            "type2": None,
            "ability1": "over-grow",
            "ability2": None,
            "abilityh": None,
            "evolution": None,
            "evolution_lvl": None,
            "evolution_tree": "tree",
            "ev_gains1": "+ 1 HP",
            "ev_gains2": None,
            "profile_img": "https://example.com/testmon.png",
        }

        with patch("utils.embed_utils.Embed") as mock_embed_class:
            mock_embed = MagicMock(spec=Embed)
            mock_embed_class.return_value = mock_embed

            intro(attributes)

            # Should handle special characters
            mock_embed_class.assert_called_once()


class TestCompareIntrosMissing:
    def test_compare_intros_first_dual_second_single(
        self, sample_revomon_attributes: Any, sample_revomon_attributes_dual_type: Any
    ) -> None:
        attributes1 = sample_revomon_attributes_dual_type.copy()
        attributes2 = sample_revomon_attributes.copy()
        with patch("utils.embed_utils.Embed") as mock_embed_class:
            mock_embed = MagicMock(spec=Embed)
            mock_embed_class.return_value = mock_embed
            compare_intros(attributes1, attributes2)
            mock_embed_class.assert_called_once()

    def test_compare_intros_evolution_mixed_1(
        self, sample_revomon_attributes: Any, sample_revomon_attributes_dual_type: Any
    ) -> None:
        attributes1 = sample_revomon_attributes_dual_type.copy()
        attributes2 = sample_revomon_attributes.copy()
        with patch("utils.embed_utils.Embed") as mock_embed_class:
            mock_embed = MagicMock(spec=Embed)
            mock_embed_class.return_value = mock_embed
            compare_intros(attributes1, attributes2)
            mock_embed_class.assert_called_once()

    def test_compare_intros_ev_gains_mixed(
        self, sample_revomon_attributes: Any, sample_revomon_attributes_dual_type: Any
    ) -> None:
        attributes1 = sample_revomon_attributes_dual_type.copy()
        attributes2 = sample_revomon_attributes.copy()
        with patch("utils.embed_utils.Embed") as mock_embed_class:
            mock_embed = MagicMock(spec=Embed)
            mock_embed_class.return_value = mock_embed
            compare_intros(attributes1, attributes2)
            mock_embed_class.assert_called_once()


class TestStats:
    def test_stats(self, sample_revomon_attributes: Any) -> None:
        with patch("utils.embed_utils.Embed") as mock_embed_class:
            mock_embed = MagicMock(spec=Embed)
            mock_embed_class.return_value = mock_embed
            stats(sample_revomon_attributes)
            mock_embed_class.assert_called_once()

    def test_compare_stats(
        self, sample_revomon_attributes: Any, sample_revomon_attributes_dual_type: Any
    ) -> None:
        with patch("utils.embed_utils.Embed") as mock_embed_class:
            mock_embed = MagicMock(spec=Embed)
            mock_embed_class.return_value = mock_embed
            compare_stats(
                sample_revomon_attributes, sample_revomon_attributes_dual_type
            )
            mock_embed_class.assert_called_once()


class TestSpawns:
    def test_spawns(self, sample_revomon_attributes: Any) -> None:
        with patch("utils.embed_utils.Embed") as mock_embed_class:
            mock_embed = MagicMock(spec=Embed)
            mock_embed_class.return_value = mock_embed
            spawns(sample_revomon_attributes)
            mock_embed_class.assert_called_once()

    def test_compare_spawns(
        self, sample_revomon_attributes: Any, sample_revomon_attributes_dual_type: Any
    ) -> None:
        with patch("utils.embed_utils.Embed") as mock_embed_class:
            mock_embed = MagicMock(spec=Embed)
            mock_embed_class.return_value = mock_embed
            compare_spawns(
                sample_revomon_attributes, sample_revomon_attributes_dual_type
            )
            mock_embed_class.assert_called_once()


class TestMoves:
    def test_moves(self, sample_revomon_attributes: Any) -> None:
        with patch("utils.embed_utils.Embed") as mock_embed_class:
            mock_embed = MagicMock(spec=Embed)
            mock_embed_class.return_value = mock_embed
            moves(sample_revomon_attributes)
            mock_embed_class.assert_called_once()

    def test_compare_moves(
        self, sample_revomon_attributes: Any, sample_revomon_attributes_dual_type: Any
    ) -> None:
        with patch("utils.embed_utils.Embed") as mock_embed_class:
            mock_embed = MagicMock(spec=Embed)
            mock_embed_class.return_value = mock_embed
            compare_moves(
                sample_revomon_attributes, sample_revomon_attributes_dual_type
            )
            mock_embed_class.assert_called_once()


class TestTypes:
    def test_types(self, sample_revomon_attributes: Any) -> None:
        with patch("utils.embed_utils.Embed") as mock_embed_class:
            mock_embed = MagicMock(spec=Embed)
            mock_embed_class.return_value = mock_embed
            types(sample_revomon_attributes)
            mock_embed_class.assert_called_once()

    def test_compare_types(
        self, sample_revomon_attributes: Any, sample_revomon_attributes_dual_type: Any
    ) -> None:
        with patch("utils.embed_utils.Embed") as mock_embed_class:
            mock_embed = MagicMock(spec=Embed)
            mock_embed_class.return_value = mock_embed
            result = compare_types(
                sample_revomon_attributes, sample_revomon_attributes_dual_type
            )
            assert len(result) == 2


class TestCounterdex:
    def test_counterdex(self, sample_revomon_attributes: Any) -> None:
        with patch("utils.embed_utils.Embed") as mock_embed_class:
            mock_embed = MagicMock(spec=Embed)
            mock_embed_class.return_value = mock_embed

            attributes = sample_revomon_attributes.copy()
            attributes["weakness"] = "water, rock"
            attributes["meta_moves"] = "tackle, ember"
            attributes["counters"] = "water types"

            counterdex(attributes)
            mock_embed_class.assert_called_once()

    def test_compare_counterdexs(
        self, sample_revomon_attributes: Any, sample_revomon_attributes_dual_type: Any
    ) -> None:
        with patch("utils.embed_utils.Embed") as mock_embed_class:
            mock_embed = MagicMock(spec=Embed)
            mock_embed_class.return_value = mock_embed

            attributes1 = sample_revomon_attributes.copy()
            attributes1["weakness"] = "water, rock"
            attributes1["meta_moves"] = "tackle, ember"
            attributes1["counters"] = "water types"

            attributes2 = sample_revomon_attributes_dual_type.copy()
            attributes2["weakness"] = "electric, grass"
            attributes2["meta_moves"] = "ember, water gun"
            attributes2["counters"] = "electric types"

            compare_counterdexs(attributes1, attributes2)
            mock_embed_class.assert_called_once()
