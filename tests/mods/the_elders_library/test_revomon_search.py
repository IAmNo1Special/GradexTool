from typing import Any
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
import discord
from discord.ext import commands
from discord import Message

from mods.the_elders_library.revomon_search import revomon_search, setup


class TestRevomonSearch:
    @pytest.fixture
    def mock_bot(self) -> Any:
        bot = MagicMock(spec=commands.Bot)
        bot.add_cog = AsyncMock()
        return bot

    @pytest.fixture
    def revomon_search_cog(self, mock_bot: Any) -> Any:
        return revomon_search(mock_bot)

    @pytest.mark.asyncio
    async def test_on_ready(self, revomon_search_cog: Any, capsys: Any) -> None:
        await revomon_search_cog.on_ready()
        captured = capsys.readouterr()
        assert "The Elder's Library(Revomon Search) is ready!" in captured.out
        assert "---------------------------" in captured.out

    @patch('mods.the_elders_library.revomon_search.RevomonTable')
    @patch('mods.the_elders_library.revomon_search.Buttons')
    @patch('mods.the_elders_library.revomon_search.get_attributes', new_callable=AsyncMock)
    @patch('mods.the_elders_library.revomon_search.compare_intros')
    @patch('mods.the_elders_library.revomon_search.respond')
    @pytest.mark.asyncio
    async def test_on_message_compare(
        self, mock_respond: Any, mock_compare_intros: Any, mock_get_attributes: Any, mock_buttons_class: Any, mock_revomon_table: Any, revomon_search_cog: Any
    ) -> None:
        message = MagicMock(spec=Message)
        message.author.bot = False
        message.content = "mon1 & mon2"
        
        mock_revomon_table_instance = mock_revomon_table.return_value
        mock_revomon_table_instance.get_names = AsyncMock(return_value=["mon1", "mon2"])
        
        mock_buttons_instance = AsyncMock()
        mock_buttons_instance.compare_intros_view = AsyncMock(return_value="mock_compare_buttons")
        mock_buttons_class.return_value = mock_buttons_instance
        
        mock_get_attributes.side_effect = ["attrs1", "attrs2"]
        mock_compare_intros.return_value = "mock_compare_embed"
        
        await revomon_search_cog.on_message(message)
        
        mock_get_attributes.assert_any_call(revomon_name="mon1")
        mock_get_attributes.assert_any_call(revomon_name="mon2")
        mock_compare_intros.assert_called_once_with(attributes="attrs1", attributes2="attrs2")
        mock_buttons_instance.compare_intros_view.assert_called_once_with(attributes="attrs1", attributes2="attrs2")
        mock_respond.assert_called_once_with(revomon_search_cog.gradex, message, "mock_compare_embed", "mock_compare_buttons")

    @patch('mods.the_elders_library.revomon_search.RevomonTable')
    @patch('mods.the_elders_library.revomon_search.Buttons')
    @patch('mods.the_elders_library.revomon_search.get_attributes', new_callable=AsyncMock)
    @patch('mods.the_elders_library.revomon_search.intro')
    @patch('mods.the_elders_library.revomon_search.respond')
    @pytest.mark.asyncio
    async def test_on_message_intro(
        self, mock_respond: Any, mock_intro: Any, mock_get_attributes: Any, mock_buttons_class: Any, mock_revomon_table: Any, revomon_search_cog: Any
    ) -> None:
        message = MagicMock(spec=Message)
        message.author.bot = False
        message.content = "mon1"
        
        mock_revomon_table_instance = mock_revomon_table.return_value
        mock_revomon_table_instance.get_names = AsyncMock(return_value=["mon1", "mon2"])
        
        mock_buttons_instance = AsyncMock()
        mock_buttons_instance.intro_view = AsyncMock(return_value="mock_intro_buttons")
        mock_buttons_class.return_value = mock_buttons_instance
        
        mock_get_attributes.return_value = "attrs1"
        mock_intro.return_value = "mock_intro_embed"
        
        await revomon_search_cog.on_message(message)
        
        mock_get_attributes.assert_called_once_with(revomon_name="mon1")
        mock_intro.assert_called_once_with(attributes="attrs1")
        mock_buttons_instance.intro_view.assert_called_once_with(attributes="attrs1")
        mock_respond.assert_called_once_with(revomon_search_cog.gradex, message, "mock_intro_embed", "mock_intro_buttons")

    @pytest.mark.asyncio
    async def test_on_message_bot(self, revomon_search_cog: Any) -> None:
        message = MagicMock(spec=Message)
        message.author.bot = True
        
        # If the bot early returns, it won't crash or call anything else.
        await revomon_search_cog.on_message(message)

    @pytest.mark.asyncio
    async def test_on_message_exception(self, revomon_search_cog: Any, capsys: Any) -> None:
        message = MagicMock(spec=Message)
        # Mocking an exception in author.bot check to trigger the try-except
        type(message.author).bot = property(lambda self: int("error"))
        
        await revomon_search_cog.on_message(message)
        captured = capsys.readouterr()
        assert "An error occurred during revomon_search on_message" in captured.out


@pytest.mark.asyncio
async def test_setup_function() -> None:
    mock_bot = MagicMock(spec=commands.Bot)
    mock_bot.add_cog = AsyncMock()
    
    await setup(mock_bot)
    
    mock_bot.add_cog.assert_called_once()
    added_cog = mock_bot.add_cog.call_args[0][0]
    assert isinstance(added_cog, revomon_search)
