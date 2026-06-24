from typing import Any

"""Comprehensive tests for the guardrails/users.py mod."""

from unittest.mock import AsyncMock, MagicMock, patch  # noqa: E402

import discord  # noqa: E402
import pytest  # noqa: E402
from discord.ext import commands  # noqa: E402

from mods.guardrails.users import UsersGuardrail, setup  # noqa: E402


@pytest.fixture
def mock_bot() -> Any:
    bot = AsyncMock(spec=commands.Bot)
    bot.add_cog = AsyncMock()
    return bot

class TestUsersGuardrail:
    """Test suite for UsersGuardrail cog."""

    @pytest.mark.asyncio
    async def test_initialization(self, mock_bot: Any) -> None:
        """Test that UsersGuardrail initializes correctly."""
        cog = UsersGuardrail(mock_bot)
        assert cog.gradex_tool == mock_bot
        assert cog.cog_name == "UsersGuardrail"

    @pytest.mark.asyncio
    async def test_on_ready(self, mock_bot: Any) -> None:
        """Test the on_ready event handler."""
        cog = UsersGuardrail(mock_bot)
        with patch('mods.guardrails.users.logger.info') as mock_info:
            await cog.on_ready()
            assert mock_info.call_count == 2
            mock_info.assert_any_call("UsersGuardrail is ready!")

    @pytest.mark.asyncio
    async def test_on_message_bot_message(self, mock_bot: Any) -> None:
        """Test handling bot messages."""
        cog = UsersGuardrail(mock_bot)
        mock_message = MagicMock(spec=discord.Message)
        mock_message.author = MagicMock(spec=discord.Member)
        mock_message.author.bot = True

        with patch('mods.guardrails.users.user_check') as mock_user_check:
            await cog.on_message(mock_message)
            mock_user_check.assert_not_called()

    @pytest.mark.asyncio
    async def test_on_message_user_message(self, mock_bot: Any) -> None:
        """Test handling normal user messages."""
        cog = UsersGuardrail(mock_bot)
        mock_message = MagicMock(spec=discord.Message)
        mock_message.author = MagicMock(spec=discord.Member)
        mock_message.author.bot = False

        with patch('mods.guardrails.users.user_check', new_callable=AsyncMock) as mock_user_check:
            await cog.on_message(mock_message)
            mock_user_check.assert_called_once_with(gradex_tool=mock_bot, user=mock_message.author)

    @pytest.mark.asyncio
    async def test_on_message_exception(self, mock_bot: Any) -> None:
        """Test handling normal user messages with exception."""
        cog = UsersGuardrail(mock_bot)
        mock_message = MagicMock(spec=discord.Message)
        mock_message.author = MagicMock(spec=discord.Member)
        mock_message.author.bot = False

        with patch('mods.guardrails.users.user_check', new_callable=AsyncMock) as mock_user_check:
            mock_user_check.side_effect = Exception("Test exception")
            with patch('mods.guardrails.users.logger.error') as mock_error:
                await cog.on_message(mock_message)
                mock_error.assert_called_once_with("An error occurred during main(on_message): Test exception")

    @patch('mods.guardrails.users.GRA_GUILD_ID', new=None)
    @pytest.mark.asyncio
    async def test_on_member_join_no_guild_id(self, mock_bot: Any) -> None:
        """Test on_member_join when GRA_GUILD_ID is not set."""
        cog = UsersGuardrail(mock_bot)
        mock_member = MagicMock(spec=discord.Member)

        with patch('mods.guardrails.users.logger.error') as mock_error:
            await cog.on_member_join(mock_member)
            mock_error.assert_called_once_with("GRA_GUILD_ID not found in configuration!")

    @patch('mods.guardrails.users.GRA_GUILD_ID', new="12345")
    @pytest.mark.asyncio
    async def test_on_member_join_wrong_guild(self, mock_bot: Any) -> None:
        """Test on_member_join when guild ID doesn't match."""
        cog = UsersGuardrail(mock_bot)
        mock_member = MagicMock(spec=discord.Member)
        mock_member.guild = MagicMock(spec=discord.Guild)
        mock_member.guild.id = 54321  # Doesn't match

        mock_member.add_roles = AsyncMock()
        await cog.on_member_join(mock_member)
        mock_member.add_roles.assert_not_called()

    @patch('mods.guardrails.users.GRA_GUILD_ID', new="12345")
    @pytest.mark.asyncio
    async def test_on_member_join_role_found(self, mock_bot: Any) -> None:
        """Test on_member_join when role is found."""
        cog = UsersGuardrail(mock_bot)
        mock_member = MagicMock(spec=discord.Member)
        mock_member.guild = MagicMock(spec=discord.Guild)
        mock_member.guild.id = 12345
        mock_member.add_roles = AsyncMock()

        mock_role = MagicMock(spec=discord.Role)

        with patch('mods.guardrails.users.utils.get', return_value=mock_role) as mock_get:
            with patch('mods.guardrails.users.logger.info') as mock_info:
                await cog.on_member_join(mock_member)
                mock_get.assert_called_once_with(mock_member.guild.roles, name="Fresh Spawn")
                mock_member.add_roles.assert_called_once_with(mock_role)
                assert mock_info.call_count >= 2

    @patch('mods.guardrails.users.GRA_GUILD_ID', new="12345")
    @pytest.mark.asyncio
    async def test_on_member_join_role_not_found(self, mock_bot: Any) -> None:
        """Test on_member_join when role is not found."""
        cog = UsersGuardrail(mock_bot)
        mock_member = MagicMock(spec=discord.Member)
        mock_member.guild = MagicMock(spec=discord.Guild)
        mock_member.guild.id = 12345
        mock_member.add_roles = AsyncMock()

        with patch('mods.guardrails.users.utils.get', return_value=None) as mock_get:
            with patch('mods.guardrails.users.logger.warning') as mock_warn:
                await cog.on_member_join(mock_member)
                mock_get.assert_called_once_with(mock_member.guild.roles, name="Fresh Spawn")
                mock_member.add_roles.assert_not_called()
                mock_warn.assert_called_once_with("Role Fresh Spawn not found!")

    @pytest.mark.asyncio
    async def test_on_app_command_completion_success(self, mock_bot: Any) -> None:
        """Test on_app_command_completion success case."""
        cog = UsersGuardrail(mock_bot)
        mock_interaction = MagicMock(spec=discord.Interaction)
        mock_interaction.client = mock_bot
        mock_interaction.user = MagicMock(spec=discord.Member)

        mock_command = MagicMock()
        mock_command.name = "test_cmd"

        with patch('mods.guardrails.users.user_check', new_callable=AsyncMock) as mock_user_check:
            await cog.on_app_command_completion(mock_interaction, mock_command)
            mock_user_check.assert_called_once_with(gradex_tool=mock_bot, user=mock_interaction.user)

    @pytest.mark.asyncio
    async def test_on_app_command_completion_exception(self, mock_bot: Any) -> None:
        """Test on_app_command_completion exception case."""
        cog = UsersGuardrail(mock_bot)
        mock_interaction = MagicMock(spec=discord.Interaction)
        mock_interaction.client = mock_bot
        mock_interaction.user = MagicMock(spec=discord.Member)

        mock_command = MagicMock()
        mock_command.name = "test_cmd"

        with patch('mods.guardrails.users.user_check', new_callable=AsyncMock) as mock_user_check:
            mock_user_check.side_effect = Exception("Command failed")
            with patch('mods.guardrails.users.logger.error') as mock_error:
                await cog.on_app_command_completion(mock_interaction, mock_command)
                mock_error.assert_called_once_with("An error occurred during UsersGuardrail(on_app_command_completion): Command failed")

@pytest.mark.asyncio
async def test_setup_success(mock_bot: Any) -> None:
    """Test setup function successfully adds cog."""
    with patch('mods.guardrails.users.logger.info') as mock_info:
        await setup(mock_bot)
        mock_bot.add_cog.assert_called_once()
        assert mock_info.call_count == 2
        mock_info.assert_any_call("Loading UsersGuardrail Cog...")
        mock_info.assert_any_call("Successfully loaded UsersGuardrail")

@pytest.mark.asyncio
async def test_setup_exception(mock_bot: Any) -> None:
    """Test setup function handles exception when adding cog."""
    mock_bot.add_cog.side_effect = Exception("Load error")
    with patch('mods.guardrails.users.logger.error') as mock_error:
        await setup(mock_bot)
        mock_error.assert_called_once_with("Error loading UsersGuardrail: Load error")
