from typing import Any
from unittest.mock import AsyncMock, MagicMock

import discord
import pytest
from discord import Embed
from discord.ext import commands

from mods.the_elders_library.help_command import HelpCommand, setup


class TestHelpCommand:
    @pytest.fixture
    def mock_bot(self) -> Any:
        bot = MagicMock(spec=commands.Bot)
        bot.add_cog = AsyncMock()
        return bot

    @pytest.fixture
    def help_cog(self, mock_bot: Any) -> Any:
        return HelpCommand(mock_bot)

    @pytest.mark.asyncio
    async def test_on_ready(self, help_cog: Any, capsys: Any) -> None:
        await help_cog.on_ready()
        captured = capsys.readouterr()
        assert "Help Command is ready!" in captured.out
        assert "---------------------------" in captured.out

    def test_help_embed(self, help_cog: Any) -> None:
        embed = help_cog.help_embed()
        assert isinstance(embed, Embed)
        assert embed.title == "Help Menu"
        assert embed.description == "Gradex Tool commands"
        assert embed.color == discord.Color.red()

        fields = {f.name: f.value for f in embed.fields}
        assert "- **/evchart**" in fields
        assert "- **/search [category][keyword]**" in fields

    @pytest.mark.asyncio
    async def test_public_button(self, help_cog: Any) -> None:
        embed = help_cog.help_embed()
        button_view = help_cog.PublicButton(embed=embed)

        interaction = AsyncMock(spec=discord.Interaction)
        interaction.response = AsyncMock()
        interaction.followup = AsyncMock()

        # Call the button callback
        await button_view.children[0].callback(interaction)

        interaction.response.defer.assert_called_once_with(ephemeral=False, thinking=True)
        interaction.followup.send.assert_called_once_with(embed=embed, ephemeral=False)

    @pytest.mark.asyncio
    async def test_public_button_exception(self, help_cog: Any, capsys: Any) -> None:
        embed = help_cog.help_embed()
        button_view = help_cog.PublicButton(embed=embed)

        interaction = AsyncMock(spec=discord.Interaction)
        interaction.response.defer.side_effect = Exception("Test Error")

        # Call the button callback
        await button_view.children[0].callback(interaction)

        captured = capsys.readouterr()
        assert "An error occurred trying to click the 'Make Public[PublicButton]'" in captured.out

    @pytest.mark.asyncio
    async def test_help_command(self, help_cog: Any) -> None:
        interaction = AsyncMock(spec=discord.Interaction)
        interaction.response = AsyncMock()

        await help_cog.help.callback(help_cog, interaction)

        interaction.response.send_message.assert_called_once()
        kwargs = interaction.response.send_message.call_args.kwargs
        assert "embed" in kwargs
        assert "view" in kwargs
        assert kwargs["ephemeral"] is True


@pytest.mark.asyncio
async def test_setup_function() -> None:
    mock_bot = MagicMock(spec=commands.Bot)
    mock_bot.add_cog = AsyncMock()

    await setup(mock_bot)

    mock_bot.add_cog.assert_called_once()
    added_cog = mock_bot.add_cog.call_args[0][0]
    assert isinstance(added_cog, HelpCommand)

@pytest.mark.asyncio
async def test_setup_function_exception(capsys: Any) -> None:
    mock_bot = MagicMock(spec=commands.Bot)
    mock_bot.add_cog = AsyncMock(side_effect=Exception("Test Exception"))

    await setup(mock_bot)

    captured = capsys.readouterr()
    assert "ERROR in ModName 'setup' function" in captured.out
