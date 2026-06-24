from typing import Any

"""Comprehensive tests for enforcement.py cog."""

from unittest.mock import AsyncMock, MagicMock  # noqa: E402

import discord  # noqa: E402
import pytest  # noqa: E402

from mods.core.enforcement import EnforcementCog, setup  # noqa: E402


class TestEnforcementCogInitialization:
    """Test suite for EnforcementCog initialization."""

    def test_enforcement_cog_init(self, mock_bot: Any) -> None:
        """Test EnforcementCog initialization."""
        cog = EnforcementCog(mock_bot)

        assert cog.bot == mock_bot
        assert cog.category_name == "RevoCord"
        assert isinstance(cog.protected_channels, dict)
        assert isinstance(cog.expected_positions, dict)
        assert isinstance(cog, EnforcementCog)

    def test_enforcement_cog_is_cog(self, mock_bot: Any) -> None:
        """Test that EnforcementCog is a proper Discord Cog."""
        from discord.ext import commands

        cog = EnforcementCog(mock_bot)
        assert isinstance(cog, commands.Cog)

    def test_enforcement_cog_protected_channels_setup(self, mock_bot: Any) -> None:
        """Test that protected channels are set up correctly."""
        cog = EnforcementCog(mock_bot)

        # Should have channels for all workspaces
        assert "portal" in cog.protected_channels
        assert "news" in cog.protected_channels
        assert "wilds" in cog.protected_channels

        # Portal and news should be TextChannels
        assert cog.protected_channels["portal"] == discord.TextChannel
        assert cog.protected_channels["news"] == discord.TextChannel

    def test_enforcement_cog_expected_positions_setup(self, mock_bot: Any) -> None:
        """Test that expected positions are set up correctly."""
        cog = EnforcementCog(mock_bot)

        # Should have positions for all channels
        assert "portal" in cog.expected_positions
        assert "news" in cog.expected_positions
        assert "wilds" in cog.expected_positions

        # Positions should be correct
        assert cog.expected_positions["news"] == 0
        assert cog.expected_positions["portal"] == 2
        assert cog.expected_positions["wilds"] == 3


class TestEnforcementCogEventListeners:
    """Test suite for EnforcementCog event listeners."""

    def test_cog_has_on_message_listener(self, mock_bot: Any) -> None:
        """Test that EnforcementCog has on_message listener."""
        cog = EnforcementCog(mock_bot)

        assert hasattr(cog, 'on_message')
        assert callable(cog.on_message)

    def test_cog_has_on_guild_channel_update_listener(self, mock_bot: Any) -> None:
        """Test that EnforcementCog has on_guild_channel_update listener."""
        cog = EnforcementCog(mock_bot)

        assert hasattr(cog, 'on_guild_channel_update')
        assert callable(cog.on_guild_channel_update)

    def test_cog_has_on_guild_channel_delete_listener(self, mock_bot: Any) -> None:
        """Test that EnforcementCog has on_guild_channel_delete listener."""
        cog = EnforcementCog(mock_bot)

        assert hasattr(cog, 'on_guild_channel_delete')
        assert callable(cog.on_guild_channel_delete)


class TestEnforcementCogSetup:
    """Test suite for enforcement setup function."""

    @pytest.mark.asyncio
    async def test_setup_adds_cog(self, mock_bot: Any) -> None:
        """Test that setup function adds the cog to bot."""
        await setup(mock_bot)

        mock_bot.add_cog.assert_called_once()

        call_args = mock_bot.add_cog.call_args
        cog = call_args[0][0]
        assert isinstance(cog, EnforcementCog)

    @pytest.mark.asyncio
    async def test_setup_handles_exception(self, mock_bot: Any) -> None:
        """Test that setup handles exceptions gracefully."""
        mock_bot.add_cog = AsyncMock(side_effect=Exception("Setup error"))

        await setup(mock_bot)

        mock_bot.add_cog.assert_called_once()


class TestEnforcementCogIntegration:
    """Integration tests for enforcement system."""

    @pytest.mark.asyncio
    async def test_cog_lifecycle(self, mock_bot: Any) -> None:
        """Test cog lifecycle: setup -> initialization."""
        await setup(mock_bot)

        cog = EnforcementCog(mock_bot)

        # Verify setup was called
        mock_bot.add_cog.assert_called_once()

        # Verify cog has all required listeners
        assert hasattr(cog, 'on_message')
        assert hasattr(cog, 'on_guild_channel_update')
        assert hasattr(cog, 'on_guild_channel_delete')


# Note: Complex event listener tests have been simplified to avoid
# Discord library dependencies and timing issues. The structural tests
# provide good coverage of the enforcement functionality.

from unittest.mock import patch  # noqa: E402


class TestEnforcementCogLogic:
    """Test suite for EnforcementCog logic."""

    @pytest.mark.asyncio
    async def test_on_guild_channel_update_wrong_name(self, mock_bot: Any) -> None:
        cog = EnforcementCog(mock_bot)
        mock_before = MagicMock(spec=discord.TextChannel)
        mock_after = MagicMock(spec=discord.TextChannel)
        mock_after.name = "unprotected-channel"
        # Should return early and not edit
        await cog.on_guild_channel_update(mock_before, mock_after)
        mock_after.edit.assert_not_called()

    @pytest.mark.asyncio
    @patch("mods.core.enforcement.discord.utils.get")
    async def test_on_guild_channel_update_no_category(self, mock_get: Any, mock_bot: Any) -> None:
        cog = EnforcementCog(mock_bot)
        mock_before = MagicMock(spec=discord.TextChannel)
        mock_after = MagicMock(spec=discord.TextChannel)
        mock_after.name = "portal"
        mock_get.return_value = None
        # Should return early
        await cog.on_guild_channel_update(mock_before, mock_after)
        mock_after.edit.assert_not_called()

    @pytest.mark.asyncio
    @patch("mods.core.enforcement.logger")
    async def test_on_message_deletes_pin(self, mock_logger: Any, mock_bot: Any) -> None:
        cog = EnforcementCog(mock_bot)
        mock_msg = MagicMock()
        mock_msg.type = discord.MessageType.pins_add
        mock_msg.delete = AsyncMock()

        await cog.on_message(mock_msg)
        mock_msg.delete.assert_called_once()
        mock_logger.info.assert_called_with("Deleted pin notification.")

    @pytest.mark.asyncio
    @patch("mods.core.enforcement.logger")
    async def test_on_message_forbidden(self, mock_logger: Any, mock_bot: Any) -> None:
        cog = EnforcementCog(mock_bot)
        mock_msg = MagicMock()
        mock_msg.type = discord.MessageType.pins_add
        mock_msg.delete = AsyncMock(side_effect=discord.Forbidden(MagicMock(), ''))

        await cog.on_message(mock_msg)
        mock_logger.error.assert_called_with("Permissions failure: Cannot delete pin notification. Bot needs 'Manage Channels'.")

    @pytest.mark.asyncio
    @patch("mods.core.enforcement.logger")
    async def test_on_message_exception(self, mock_logger: Any, mock_bot: Any) -> None:
        cog = EnforcementCog(mock_bot)
        mock_msg = MagicMock()
        mock_msg.type = discord.MessageType.pins_add
        mock_msg.delete = AsyncMock(side_effect=Exception("foo"))

        await cog.on_message(mock_msg)
        mock_logger.error.assert_called()

    @pytest.mark.asyncio
    @patch("mods.core.enforcement.discord.utils.get")
    async def test_on_guild_channel_update(self, mock_get: Any, mock_bot: Any) -> None:
        cog = EnforcementCog(mock_bot)

        before = MagicMock()
        after = MagicMock(spec=discord.TextChannel)
        after.name = "portal"
        after.category_id = 999
        after.edit = AsyncMock()
        after.guild = MagicMock()

        mock_category = MagicMock()
        mock_category.id = 123
        mock_get.return_value = mock_category

        await cog.on_guild_channel_update(before, after)

        after.edit.assert_called_once_with(
            category=mock_category,
            position=2,
            sync_permissions=False,
            reason="RevoCord Enforcement: Channel movement restricted.",
        )

    @pytest.mark.asyncio
    @patch("mods.core.enforcement.discord.utils.get")
    async def test_on_guild_channel_update_wrong_type(self, mock_get: Any, mock_bot: Any) -> None:
        cog = EnforcementCog(mock_bot)

        before = MagicMock()
        after = MagicMock(spec=discord.ForumChannel)
        after.name = "portal"

        await cog.on_guild_channel_update(before, after)
        mock_get.assert_not_called()

    @pytest.mark.asyncio
    @patch("mods.core.enforcement.discord.utils.get")
    async def test_on_guild_channel_update_forbidden(self, mock_get: Any, mock_bot: Any) -> None:
        cog = EnforcementCog(mock_bot)

        before = MagicMock()
        after = MagicMock(spec=discord.TextChannel)
        after.name = "portal"
        after.category_id = 999
        after.edit = AsyncMock(side_effect=discord.Forbidden(MagicMock(), ''))

        mock_category = MagicMock()
        mock_category.id = 123
        mock_get.return_value = mock_category

        await cog.on_guild_channel_update(before, after)
        after.edit.assert_called_once()

    @pytest.mark.asyncio
    @patch("mods.core.enforcement.discord.utils.get")
    async def test_on_guild_channel_update_http_exception(self, mock_get: Any, mock_bot: Any) -> None:
        cog = EnforcementCog(mock_bot)

        before = MagicMock()
        after = MagicMock(spec=discord.TextChannel)
        after.name = "portal"
        after.category_id = 999
        mock_resp = MagicMock()
        mock_resp.status = 400
        mock_resp.reason = 'Bad Request'
        after.edit = AsyncMock(side_effect=discord.HTTPException(mock_resp, ''))

        mock_category = MagicMock()
        mock_category.id = 123
        mock_get.return_value = mock_category

        await cog.on_guild_channel_update(before, after)
        after.edit.assert_called_once()

    @pytest.mark.asyncio
    @patch("mods.core.enforcement.discord.utils.get")
    async def test_on_guild_channel_update_http_exception_race(self, mock_get: Any, mock_bot: Any) -> None:
        cog = EnforcementCog(mock_bot)

        before = MagicMock()
        after = MagicMock(spec=discord.TextChannel)
        after.name = "portal"
        after.category_id = 999
        mock_resp = MagicMock()
        mock_resp.status = 400
        mock_resp.reason = 'Bad Request'
        # mock code and message for HttpException
        exc = discord.HTTPException(mock_resp, message="parent_id: Category does not exist")
        exc.code = 50035
        after.edit = AsyncMock(side_effect=exc)

        mock_category = MagicMock()
        mock_category.id = 123
        mock_get.return_value = mock_category

        await cog.on_guild_channel_update(before, after)
        after.edit.assert_called_once()

    @pytest.mark.asyncio
    @patch("mods.core.enforcement.discord.utils.get")
    async def test_on_guild_channel_update_exception(self, mock_get: Any, mock_bot: Any) -> None:
        cog = EnforcementCog(mock_bot)

        before = MagicMock()
        after = MagicMock(spec=discord.TextChannel)
        after.name = "portal"
        after.category_id = 999
        after.edit = AsyncMock(side_effect=Exception("foo"))

        mock_category = MagicMock()
        mock_category.id = 123
        mock_get.return_value = mock_category

        await cog.on_guild_channel_update(before, after)
        after.edit.assert_called_once()

    @pytest.mark.asyncio
    async def test_on_guild_channel_delete(self, mock_bot: Any) -> None:
        cog = EnforcementCog(mock_bot)

        mock_channel = MagicMock(spec=discord.CategoryChannel)
        mock_channel.name = "RevoCord"

        child1 = MagicMock(spec=discord.TextChannel)
        child1.name = "portal"
        child1.category_id = None
        child1.delete = AsyncMock()

        child2 = MagicMock(spec=discord.TextChannel)
        child2.name = "unrelated"
        child2.category_id = None
        child2.delete = AsyncMock()

        child3 = MagicMock(spec=discord.TextChannel)
        child3.name = "dashboard"
        child3.category_id = 123
        child3.delete = AsyncMock()

        mock_channel.guild.channels = [child1, child2, child3]

        await cog.on_guild_channel_delete(mock_channel)

        child1.delete.assert_called_once()
        child2.delete.assert_not_called()
        child3.delete.assert_not_called()

    @pytest.mark.asyncio
    async def test_on_guild_channel_delete_forbidden(self, mock_bot: Any) -> None:
        cog = EnforcementCog(mock_bot)

        mock_channel = MagicMock(spec=discord.CategoryChannel)
        mock_channel.name = "RevoCord"

        child1 = MagicMock(spec=discord.TextChannel)
        child1.name = "portal"
        child1.category_id = None
        child1.delete = AsyncMock(side_effect=discord.Forbidden(MagicMock(), ''))

        mock_channel.guild.channels = [child1]

        await cog.on_guild_channel_delete(mock_channel)
        child1.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_on_guild_channel_delete_http(self, mock_bot: Any) -> None:
        cog = EnforcementCog(mock_bot)

        mock_channel = MagicMock(spec=discord.CategoryChannel)
        mock_channel.name = "RevoCord"

        child1 = MagicMock(spec=discord.TextChannel)
        child1.name = "portal"
        child1.category_id = None
        mock_resp = MagicMock()
        mock_resp.status = 400
        mock_resp.reason = 'Bad Request'
        child1.delete = AsyncMock(side_effect=discord.HTTPException(mock_resp, ''))

        mock_channel.guild.channels = [child1]

        await cog.on_guild_channel_delete(mock_channel)
        child1.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_on_guild_channel_delete_wrong_channel_type(self, mock_bot: Any) -> None:
        cog = EnforcementCog(mock_bot)
        mock_channel = MagicMock(spec=discord.TextChannel)
        await cog.on_guild_channel_delete(mock_channel)

    @pytest.mark.asyncio
    async def test_on_guild_channel_delete_wrong_name(self, mock_bot: Any) -> None:
        cog = EnforcementCog(mock_bot)
        mock_channel = MagicMock(spec=discord.CategoryChannel)
        mock_channel.name = "WrongName"
        await cog.on_guild_channel_delete(mock_channel)

    @pytest.mark.asyncio
    @patch("scripts.gradexDB.delete_guild_data", new_callable=AsyncMock)
    async def test_on_guild_channel_delete_success(self, mock_delete: Any, mock_bot: Any) -> None:
        cog = EnforcementCog(mock_bot)
        mock_channel = MagicMock(spec=discord.CategoryChannel)
        mock_channel.name = "RevoCord"
        mock_channel.guild.id = 123
        mock_channel.guild.channels = []

        await cog.on_guild_channel_delete(mock_channel)
        mock_delete.assert_called_once_with(123)

    @pytest.mark.asyncio
    @patch("scripts.gradexDB.delete_guild_data", new_callable=AsyncMock, side_effect=Exception("DB Error"))
    async def test_on_guild_channel_delete_exception(self, mock_delete: Any, mock_bot: Any) -> None:
        cog = EnforcementCog(mock_bot)
        mock_channel = MagicMock(spec=discord.CategoryChannel)
        mock_channel.name = "RevoCord"
        mock_channel.guild.id = 123
        mock_channel.guild.channels = []

        await cog.on_guild_channel_delete(mock_channel)
        mock_delete.assert_called_once_with(123)

    @pytest.mark.asyncio
    @patch("scripts.gradexDB.delete_guild_data", new_callable=AsyncMock)
    async def test_on_guild_remove_success(self, mock_delete: Any, mock_bot: Any) -> None:
        cog = EnforcementCog(mock_bot)
        mock_guild = MagicMock(spec=discord.Guild)
        mock_guild.id = 123

        await cog.on_guild_remove(mock_guild)
        mock_delete.assert_called_once_with(123)

    @pytest.mark.asyncio
    @patch("scripts.gradexDB.delete_guild_data", new_callable=AsyncMock, side_effect=Exception("DB Error"))
    async def test_on_guild_remove_exception(self, mock_delete: Any, mock_bot: Any) -> None:
        cog = EnforcementCog(mock_bot)
        mock_guild = MagicMock(spec=discord.Guild)
        mock_guild.id = 123

        await cog.on_guild_remove(mock_guild)
        mock_delete.assert_called_once_with(123)
