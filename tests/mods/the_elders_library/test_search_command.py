from typing import Any
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
import discord
from discord.ext import commands
from discord import Embed

from mods.the_elders_library.search_command import SearchCommand, setup


class TestSearchCommand:
    @pytest.fixture
    def mock_bot(self) -> Any:
        bot = MagicMock(spec=commands.Bot)
        bot.add_cog = AsyncMock()
        return bot

    @pytest.fixture
    def search_cog(self, mock_bot: Any) -> Any:
        return SearchCommand(mock_bot)

    @pytest.mark.asyncio
    async def test_on_ready(self, search_cog: Any, capsys: Any) -> None:
        await search_cog.on_ready()
        captured = capsys.readouterr()
        assert "The Elder's Library(Search Command) is ready!" in captured.out
        assert "---------------------------" in captured.out

    @patch('mods.the_elders_library.search_command.AbilitiesTable')
    @patch('mods.the_elders_library.search_command.RevomonTable')
    @pytest.mark.asyncio
    async def test_ability_search_embed(self, mock_revomon_table: Any, mock_abilities_table: Any, search_cog: Any) -> None:
        mock_abilities_instance = mock_abilities_table.return_value
        mock_abilities_instance.get_info = AsyncMock(return_value=[("Blaze", "Powers up Fire-type moves.")])
        
        mock_revomon_instance = mock_revomon_table.return_value
        mock_revomon_instance.get_names = AsyncMock(return_value=["Charmander"])
        mock_revomon_instance.has_ability = AsyncMock(return_value=True)

        embed = await search_cog.ability_search_embed("Blaze")
        assert embed.title == "Blaze"
        assert "Powers up fire-type moves." in embed.description
        assert "Charmander" in embed.description

    @patch('mods.the_elders_library.search_command.AbilitiesTable')
    @pytest.mark.asyncio
    async def test_allabilities_embed(self, mock_abilities_table: Any, search_cog: Any) -> None:
        mock_abilities_instance = mock_abilities_table.return_value
        mock_abilities_instance.get_names = AsyncMock(return_value=["Blaze", "Overgrow"])

        embed = await search_cog.allabilities_embed()
        assert embed.title == "All Abilities"
        assert "Blaze" in embed.description
        assert "Overgrow" in embed.description

    @patch('mods.the_elders_library.search_command.FruitysTable')
    @pytest.mark.asyncio
    async def test_fruity_search_embed(self, mock_fruitys_table: Any, search_cog: Any) -> None:
        mock_fruitys_instance = mock_fruitys_table.return_value
        mock_fruitys_instance.get_info = AsyncMock(return_value=[("Apple", "Restores 20 HP", "healing")])

        embed = await search_cog.fruity_search_embed("Apple")
        assert embed.title == "Apple"
        assert "Restores 20 hp" in embed.description
        assert embed.fields[0].value == "Healing"

    @patch('mods.the_elders_library.search_command.FruitysTable')
    @pytest.mark.asyncio
    async def test_allfruitys_embed(self, mock_fruitys_table: Any, search_cog: Any) -> None:
        mock_fruitys_instance = mock_fruitys_table.return_value
        mock_fruitys_instance.get_names = AsyncMock(return_value=["Apple", "Orange"])

        embed = await search_cog.allfruitys_embed()
        assert embed.title == "All Fruitys"
        assert "Apple" in embed.description
        assert "Orange" in embed.description

    @patch('mods.the_elders_library.search_command.ItemsTable')
    @pytest.mark.asyncio
    async def test_item_search_embed(self, mock_items_table: Any, search_cog: Any) -> None:
        mock_items_instance = mock_items_table.return_value
        mock_items_instance.get_info = AsyncMock(return_value=[("Potion", "Heals 20 HP", "Shop", "100")])

        embed = await search_cog.item_search_embed("Potion")
        assert embed.title == "Potion"
        assert "Heals 20 hp" in embed.description
        assert embed.fields[0].value == "*Shop*"
        assert embed.fields[1].value == "*100*"

    @patch('mods.the_elders_library.search_command.ItemsTable')
    @pytest.mark.asyncio
    async def test_allitems_embed(self, mock_items_table: Any, search_cog: Any) -> None:
        mock_items_instance = mock_items_table.return_value
        mock_items_instance.get_names = AsyncMock(return_value=["Potion", "Pokeball"])

        embed = await search_cog.allitems_embed()
        assert embed.title == "All Items"
        assert "Potion" in embed.description
        assert "Pokeball" in embed.description

    @patch('mods.the_elders_library.search_command.MovesTable')
    @patch('mods.the_elders_library.search_command.RevomonMovesTable')
    @pytest.mark.asyncio
    async def test_move_search_embed(self, mock_revomon_moves_table: Any, mock_moves_table: Any, search_cog: Any) -> None:
        mock_moves_instance = mock_moves_table.return_value
        # (0, Capsule, Name, Category, Type, Description, Accuracy, Damage, PP, Priority)
        mock_moves_instance.get_info = AsyncMock(return_value=[(0, 1, "Flamethrower", "Special", "Fire", "Burns opponent.", 100, 90, 15, 0)])
        
        mock_revomon_moves_instance = mock_revomon_moves_table.return_value
        mock_revomon_moves_instance.get_mons_for_move = AsyncMock(return_value=["Charmander"])

        embed = await search_cog.move_search_embed("Flamethrower")
        assert embed.title == "Flamethrower"
        assert "Burns opponent." in embed.description
        assert embed.fields[0].value == "*Fire*"
        assert embed.fields[1].value == "*Special*"

    @patch('mods.the_elders_library.search_command.NaturesTable')
    @pytest.mark.asyncio
    async def test_nature_search_embed(self, mock_natures_table: Any, search_cog: Any) -> None:
        mock_natures_instance = mock_natures_table.return_value
        mock_natures_instance.get_info = AsyncMock(return_value=[("Adamant", "Attack", "Special Attack", "Spicy", "Dry")])

        embed = await search_cog.nature_search_embed("Adamant")
        assert embed.title == "Adamant Nature"
        assert "Attack" in embed.fields[0].value
        assert "Special Attack" in embed.fields[1].value
        assert "Spicy" in embed.fields[2].value
        assert "Dry" in embed.fields[3].value

    @patch('mods.the_elders_library.search_command.NaturesTable')
    @pytest.mark.asyncio
    async def test_nature_search_embed_neutral(self, mock_natures_table: Any, search_cog: Any) -> None:
        mock_natures_instance = mock_natures_table.return_value
        mock_natures_instance.get_info = AsyncMock(return_value=[("Hardy", None, None, None, None)])

        embed = await search_cog.nature_search_embed("Hardy")
        assert embed.title == "Hardy Nature"
        assert "*None*" in embed.fields[0].value
        assert "*None*" in embed.fields[1].value

    @patch('mods.the_elders_library.search_command.NaturesTable')
    @pytest.mark.asyncio
    async def test_allnatures_embed(self, mock_natures_table: Any, search_cog: Any) -> None:
        mock_natures_instance = mock_natures_table.return_value
        mock_natures_instance.get_names = AsyncMock(return_value=["Adamant", "Hardy"])

        embed = await search_cog.allnatures_embed()
        assert embed.title == "All Natures"
        assert "Adamant" in embed.fields[0].value

    @patch.object(SearchCommand, 'allabilities_embed')
    @patch.object(SearchCommand, 'ability_search_embed')
    @pytest.mark.asyncio
    async def test_abilities_command(self, mock_ability_search_embed: Any, mock_allabilities_embed: Any, search_cog: Any) -> None:
        interaction = AsyncMock(spec=discord.Interaction)
        interaction.response = AsyncMock()

        mock_allabilities_embed.return_value = "all_embed"
        mock_ability_search_embed.return_value = "search_embed"

        # Test no name
        await search_cog.abilities.callback(search_cog, interaction, name=None)
        interaction.response.send_message.assert_called_with(embed="all_embed", ephemeral=True)

        # Test with name
        await search_cog.abilities.callback(search_cog, interaction, name="Blaze")
        interaction.response.send_message.assert_called_with(embed="search_embed", ephemeral=True)

    @pytest.mark.asyncio
    async def test_abilities_command_exception(self, search_cog: Any, capsys: Any) -> None:
        interaction = AsyncMock(spec=discord.Interaction)
        interaction.response.send_message.side_effect = Exception("Test Exception")

        await search_cog.abilities.callback(search_cog, interaction, name=None)
        captured = capsys.readouterr()
        assert "Error during search_command(abilities subcommand):" in captured.out

    @patch.object(SearchCommand, 'allfruitys_embed')
    @patch.object(SearchCommand, 'fruity_search_embed')
    @pytest.mark.asyncio
    async def test_fruitys_command(self, mock_fruity_search_embed: Any, mock_allfruitys_embed: Any, search_cog: Any) -> None:
        interaction = AsyncMock(spec=discord.Interaction)
        interaction.response = AsyncMock()

        mock_allfruitys_embed.return_value = "all_embed"
        mock_fruity_search_embed.return_value = "search_embed"

        await search_cog.fruitys.callback(search_cog, interaction, name=None)
        interaction.response.send_message.assert_called_with(embed="all_embed", ephemeral=True)

        await search_cog.fruitys.callback(search_cog, interaction, name="Apple")
        interaction.response.send_message.assert_called_with(embed="search_embed", ephemeral=True)

    @pytest.mark.asyncio
    async def test_fruitys_command_exception(self, search_cog: Any, capsys: Any) -> None:
        interaction = AsyncMock(spec=discord.Interaction)
        interaction.response.send_message.side_effect = Exception("Test Exception")

        await search_cog.fruitys.callback(search_cog, interaction, name=None)
        captured = capsys.readouterr()
        assert "Error during search_command(fruitys subcommand):" in captured.out

    @patch.object(SearchCommand, 'allitems_embed')
    @patch.object(SearchCommand, 'item_search_embed')
    @pytest.mark.asyncio
    async def test_items_command(self, mock_item_search_embed: Any, mock_allitems_embed: Any, search_cog: Any) -> None:
        interaction = AsyncMock(spec=discord.Interaction)
        interaction.response = AsyncMock()

        mock_allitems_embed.return_value = "all_embed"
        mock_item_search_embed.return_value = "search_embed"

        await search_cog.items.callback(search_cog, interaction, name=None)
        interaction.response.send_message.assert_called_with(embed="all_embed", ephemeral=True)

        await search_cog.items.callback(search_cog, interaction, name="Potion")
        interaction.response.send_message.assert_called_with(embed="search_embed", ephemeral=True)

    @patch.object(SearchCommand, 'move_search_embed')
    @pytest.mark.asyncio
    async def test_moves_command(self, mock_move_search_embed: Any, search_cog: Any) -> None:
        interaction = AsyncMock(spec=discord.Interaction)
        interaction.response = AsyncMock()

        mock_move_search_embed.return_value = "search_embed"

        await search_cog.moves.callback(search_cog, interaction, name="Flamethrower")
        interaction.response.send_message.assert_called_with(embed="search_embed", ephemeral=True)

    @pytest.mark.asyncio
    async def test_moves_command_exception(self, search_cog: Any, capsys: Any) -> None:
        interaction = AsyncMock(spec=discord.Interaction)
        interaction.response.send_message.side_effect = Exception("Test Exception")

        await search_cog.moves.callback(search_cog, interaction, name="Flamethrower")
        captured = capsys.readouterr()
        assert "Error during search_command(moves subcommand):" in captured.out

    @patch.object(SearchCommand, 'allnatures_embed')
    @patch.object(SearchCommand, 'nature_search_embed')
    @pytest.mark.asyncio
    async def test_natures_command(self, mock_nature_search_embed: Any, mock_allnatures_embed: Any, search_cog: Any) -> None:
        interaction = AsyncMock(spec=discord.Interaction)
        interaction.response = AsyncMock()

        mock_allnatures_embed.return_value = "all_embed"
        mock_nature_search_embed.return_value = "search_embed"

        await search_cog.natures.callback(search_cog, interaction, name=None)
        interaction.response.send_message.assert_called_with(embed="all_embed", ephemeral=True)

        await search_cog.natures.callback(search_cog, interaction, name="Adamant")
        interaction.response.send_message.assert_called_with(embed="search_embed", ephemeral=True)

    @patch('mods.the_elders_library.search_command.Buttons')
    @patch('mods.the_elders_library.search_command.RevomonTable')
    @patch('mods.the_elders_library.search_command.get_attributes')
    @patch('mods.the_elders_library.search_command.compare_intros')
    @patch('mods.the_elders_library.search_command.intro')
    @pytest.mark.asyncio
    async def test_revomon_command(self, mock_intro: Any, mock_compare_intros: Any, mock_get_attributes: Any, mock_revomon_table: Any, mock_buttons_class: Any, search_cog: Any) -> None:
        interaction = AsyncMock(spec=discord.Interaction)
        interaction.response = AsyncMock()
        interaction.user.id = 123

        mock_buttons_instance = AsyncMock()
        mock_buttons_instance.mon_view = AsyncMock(return_value="mon_view")
        mock_buttons_instance.compare_intros_view = AsyncMock(return_value="compare_view")
        mock_buttons_instance.intro_view = AsyncMock(return_value="intro_view")
        mock_buttons_class.return_value = mock_buttons_instance

        # Test no name
        await search_cog.revomon.callback(search_cog, interaction, name=None)
        interaction.response.send_message.assert_called_with(view="mon_view", ephemeral=True)

        # Test compare mode
        mock_revomon_table.return_value.get_names = AsyncMock(return_value=["mon1", "mon2"])
        mock_get_attributes.side_effect = ["attrs1", "attrs2"]
        mock_compare_intros.return_value = "compare_embed"

        await search_cog.revomon.callback(search_cog, interaction, name="mon1 & mon2")
        interaction.response.send_message.assert_called_with(embed="compare_embed", view="compare_view", ephemeral=True)

        # Reset side_effect for single mon test
        mock_get_attributes.side_effect = None
        mock_get_attributes.return_value = "attrs1"
        mock_intro.return_value = "intro_embed"

        await search_cog.revomon.callback(search_cog, interaction, name="mon1")
        interaction.response.send_message.assert_called_with(embed="intro_embed", view="intro_view", ephemeral=True)

    @pytest.mark.asyncio
    async def test_revomon_command_exception(self, search_cog: Any, capsys: Any) -> None:
        interaction = AsyncMock(spec=discord.Interaction)
        interaction.response.send_message.side_effect = Exception("Test Exception")

        await search_cog.revomon.callback(search_cog, interaction, name=None)
        captured = capsys.readouterr()
        assert "An error occurred during search_command(revomon subcommand):" in captured.out


@pytest.mark.asyncio
async def test_setup_function() -> None:
    mock_bot = MagicMock(spec=commands.Bot)
    mock_bot.add_cog = AsyncMock()
    
    await setup(mock_bot)
    
    mock_bot.add_cog.assert_called_once()
    added_cog = mock_bot.add_cog.call_args[0][0]
    assert isinstance(added_cog, SearchCommand)

@pytest.mark.asyncio
async def test_setup_function_exception(capsys: Any) -> None:
    mock_bot = MagicMock(spec=commands.Bot)
    mock_bot.add_cog = AsyncMock(side_effect=Exception("Test Exception"))
    
    await setup(mock_bot)
    
    captured = capsys.readouterr()
    assert "ERROR in ModName 'setup' function" in captured.out