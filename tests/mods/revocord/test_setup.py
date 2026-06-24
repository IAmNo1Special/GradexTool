from collections.abc import AsyncGenerator
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import discord
import pytest
from discord import app_commands

from mods.revocord.setup import BiomeSelect, BiomeSelectView, SetupCog, setup


class TestSetupCogInitialization:
    def test_setup_cog_init(self, mock_bot: Any) -> None:
        cog = SetupCog(mock_bot)
        assert cog.bot == mock_bot
        assert isinstance(cog, SetupCog)

    def test_setup_cog_has_setup_command(self, mock_bot: Any) -> None:
        cog = SetupCog(mock_bot)
        assert hasattr(cog, 'setup_command')
        assert cog.setup_command is not None

class TestSetupCogSetup:
    @pytest.mark.asyncio
    async def test_setup_adds_cog(self, mock_bot: Any) -> None:
        await setup(mock_bot)
        mock_bot.add_cog.assert_called_once()
        call_args = mock_bot.add_cog.call_args
        assert isinstance(call_args[0][0], SetupCog)

class TestSetupCogCommand:
    @pytest.fixture
    def setup_cog(self, mock_bot: Any) -> Any:
        return SetupCog(mock_bot)

    @pytest.mark.asyncio
    async def test_missing_roles_permission(self, setup_cog: Any, mock_interaction: Any) -> None:
        mock_interaction.app_permissions.manage_roles = False
        await setup_cog.setup_command.callback(setup_cog, mock_interaction)

        mock_interaction.followup.send.assert_called_once()
        assert "manage roles" in mock_interaction.followup.send.call_args[0][0].lower()

    @pytest.mark.asyncio
    async def test_missing_channels_permission(self, setup_cog: Any, mock_interaction: Any) -> None:
        mock_interaction.app_permissions.manage_roles = True
        mock_interaction.app_permissions.manage_channels = False
        await setup_cog.setup_command.callback(setup_cog, mock_interaction)

        mock_interaction.followup.send.assert_called_once()
        assert "manage channels" in mock_interaction.followup.send.call_args[0][0].lower()

    @pytest.mark.asyncio
    async def test_missing_messages_permission(self, setup_cog: Any, mock_interaction: Any) -> None:
        mock_interaction.app_permissions.manage_roles = True
        mock_interaction.app_permissions.manage_channels = True
        mock_interaction.app_permissions.manage_messages = False
        await setup_cog.setup_command.callback(setup_cog, mock_interaction)

        mock_interaction.followup.send.assert_called_once()
        assert "manage messages" in mock_interaction.followup.send.call_args[0][0].lower()

    @pytest.mark.asyncio
    async def test_no_guild(self, setup_cog: Any, mock_interaction: Any) -> None:
        mock_interaction.app_permissions.manage_roles = True
        mock_interaction.app_permissions.manage_channels = True
        mock_interaction.app_permissions.manage_messages = True
        mock_interaction.guild = None
        await setup_cog.setup_command.callback(setup_cog, mock_interaction)

        mock_interaction.followup.send.assert_called_once_with("This command must be used in a server.")

    @pytest.mark.asyncio
    async def test_sends_biome_view(self, setup_cog: Any, mock_interaction: Any) -> None:
        mock_interaction.app_permissions.manage_roles = True
        mock_interaction.app_permissions.manage_channels = True
        mock_interaction.app_permissions.manage_messages = True
        await setup_cog.setup_command.callback(setup_cog, mock_interaction)

        mock_interaction.followup.send.assert_called_once()
        assert "select a Biome" in mock_interaction.followup.send.call_args[0][0]
        assert isinstance(mock_interaction.followup.send.call_args[1]["view"], BiomeSelectView)

    @pytest.mark.asyncio
    @patch("mods.revocord.setup.asyncio.sleep", new_callable=AsyncMock)
    @patch("mods.revocord.hunting.initial_wilds_spawn", new_callable=AsyncMock)
    async def test_setup_full_creation(self, mock_spawn: Any, mock_sleep: Any, setup_cog: Any, mock_interaction: Any) -> None:
        mock_guild = mock_interaction.guild
        mock_guild.categories = []
        mock_guild.channels = []
        mock_guild.fetch_channels = AsyncMock(return_value=[])
        mock_guild.text_channels = []

        mock_category = MagicMock(spec=discord.CategoryChannel)
        mock_category.name = "RevoCord"
        mock_category.edit = AsyncMock()
        mock_guild.create_category = AsyncMock(return_value=mock_category)

        mock_portal = MagicMock(spec=discord.TextChannel)
        mock_portal.id = 999

        def mock_create_ch(*args: Any, **kwargs: Any) -> Any:
            ch = MagicMock()
            ch.position = kwargs.get("position", 0)
            ch.edit = AsyncMock()
            return ch
        mock_guild.create_text_channel = AsyncMock(side_effect=lambda *args, **kwargs: mock_portal if kwargs.get("name") == "portal" else mock_create_ch(*args, **kwargs))


        await setup_cog.execute_setup(mock_interaction, mock_interaction.user, mock_interaction.guild)

        mock_guild.create_category.assert_called_once()
        assert mock_guild.create_text_channel.call_count == 4
        mock_interaction.followup.send.assert_called_once()

    @pytest.mark.asyncio
    @patch("mods.revocord.setup.asyncio.sleep", new_callable=AsyncMock)
    @patch("mods.revocord.hunting.initial_wilds_spawn", new_callable=AsyncMock)
    @patch("scripts.gradexDB.active_spawns_table.count_guild_spawns", new_callable=AsyncMock, return_value=0)
    async def test_setup_existing_sync(self, mock_count: Any, mock_spawn: Any, mock_sleep: Any, setup_cog: Any, mock_interaction: Any) -> None:
        mock_guild = mock_interaction.guild
        mock_category = MagicMock(spec=discord.CategoryChannel)
        mock_category.name = "RevoCord"
        mock_category.edit = AsyncMock()
        mock_guild.categories = [mock_category]

        mock_news = MagicMock(spec=discord.TextChannel)
        mock_news.name = "news"
        mock_news.position = 999
        mock_news.edit = AsyncMock()

        mock_event_board = MagicMock(spec=discord.TextChannel)
        mock_event_board.name = "event-board"
        mock_event_board.position = 1
        mock_event_board.edit = AsyncMock()

        mock_portal = MagicMock(spec=discord.TextChannel)
        mock_portal.name = "portal"
        mock_portal.position = 999
        mock_portal.id = 999
        mock_portal.edit = AsyncMock()

        async def mock_history(*args: Any, **kwargs: Any) -> Any:
            msg = MagicMock(author=setup_cog.bot.user)
            yield msg
        mock_portal.history = mock_history


        mock_wilds = MagicMock(spec=discord.TextChannel)
        mock_wilds.name = "wilds"
        mock_wilds.position = 3
        mock_wilds.edit = AsyncMock()


        mock_support = MagicMock(spec=discord.ForumChannel)
        mock_support.name = "support"
        mock_support.position = 999
        mock_support.edit = AsyncMock()
        mock_category.channels = [mock_news, mock_event_board, mock_portal, mock_wilds, mock_support]

        mock_guild.channels = [mock_category, mock_news, mock_event_board, mock_portal, mock_wilds]

        await setup_cog.execute_setup(mock_interaction, mock_interaction.user, mock_interaction.guild)

        mock_guild.create_category.assert_not_called()
        mock_guild.create_text_channel.assert_not_called()

    @pytest.mark.asyncio
    @patch("mods.revocord.setup.asyncio.sleep", new_callable=AsyncMock)
    @patch("mods.revocord.hunting.initial_wilds_spawn", new_callable=AsyncMock)
    async def test_setup_fetch_fallback(self, mock_spawn: Any, mock_sleep: Any, setup_cog: Any, mock_interaction: Any) -> None:
        mock_guild = mock_interaction.guild
        mock_guild.categories = []
        mock_guild.channels = []

        mock_category = MagicMock(spec=discord.CategoryChannel)
        mock_category.name = "RevoCord"
        mock_category.edit = AsyncMock()

        mock_news = MagicMock(spec=discord.TextChannel)
        mock_news.name = "news"
        mock_news.position = 999
        mock_news.edit = AsyncMock()

        mock_event_board = MagicMock(spec=discord.TextChannel)
        mock_event_board.name = "event-board"
        mock_event_board.position = 1
        mock_event_board.edit = AsyncMock()

        mock_portal = MagicMock(spec=discord.TextChannel)
        mock_portal.name = "portal"
        mock_portal.position = 999
        mock_portal.id = 999
        mock_portal.edit = AsyncMock()

        async def mock_history(*args: Any, **kwargs: Any) -> Any:
            msg = MagicMock(author=setup_cog.bot.user)
            yield msg
        mock_portal.history = mock_history


        mock_wilds = MagicMock(spec=discord.TextChannel)
        mock_wilds.name = "wilds"
        mock_wilds.position = 3
        mock_wilds.edit = AsyncMock()


        mock_support = MagicMock(spec=discord.ForumChannel)
        mock_support.name = "support"
        mock_support.position = 999
        mock_support.edit = AsyncMock()

        mock_guild.fetch_channels = AsyncMock(return_value=[mock_category, mock_news, mock_event_board, mock_portal, mock_wilds, mock_support])


        await setup_cog.execute_setup(mock_interaction, mock_interaction.user, mock_interaction.guild)

        mock_guild.create_category.assert_not_called()
        mock_guild.create_text_channel.assert_not_called()

    @pytest.mark.asyncio
    async def test_forbidden_exception(self, setup_cog: Any, mock_interaction: Any) -> None:
        mock_guild = mock_interaction.guild
        mock_guild.categories = []

        class FakeResponse:
            status = 403
            reason = "Forbidden"

        mock_guild.fetch_channels = AsyncMock(side_effect=discord.Forbidden(FakeResponse(), "Forbidden"))  # type: ignore

        await setup_cog.execute_setup(mock_interaction, mock_interaction.user, mock_interaction.guild)

        mock_interaction.followup.send.assert_called_with(
            "I don't have the required permissions to manage channels or permissions.",
            ephemeral=True
        )

    @pytest.mark.asyncio
    async def test_generic_exception(self, setup_cog: Any, mock_interaction: Any) -> None:
        mock_guild = mock_interaction.guild
        mock_guild.categories = []
        mock_guild.fetch_channels = AsyncMock(side_effect=Exception("Random error"))

        await setup_cog.execute_setup(mock_interaction, mock_interaction.user, mock_interaction.guild)

        mock_interaction.followup.send.assert_called_with(
            "An error occurred: Random error",
            ephemeral=True
        )

    @pytest.mark.asyncio
    @patch("discord.ext.commands.Bot")
    async def test_not_member(self, mock_bot: Any) -> None:
        cog = SetupCog(mock_bot)
        mock_interaction = AsyncMock()

        # User is not a Member
        mock_user = MagicMock(spec=discord.User)
        mock_interaction.user = mock_user

        await cog.setup_command.callback(cog, mock_interaction)  # type: ignore[arg-type]

        mock_interaction.followup.send.assert_called_once()
        assert "server member" in mock_interaction.followup.send.call_args[0][0]

    @pytest.mark.asyncio
    @patch("mods.revocord.setup.asyncio.sleep", new_callable=AsyncMock)
    @patch("mods.revocord.hunting.initial_wilds_spawn", new_callable=AsyncMock)
    @patch("mods.revocord.setup.discord.utils.get")
    async def test_setup_portal_fail(self, mock_get: Any, mock_spawn: Any, mock_sleep: Any, setup_cog: Any, mock_interaction: Any) -> None:
        mock_guild = mock_interaction.guild
        mock_guild.categories = []
        mock_guild.text_channels = []

        mock_get.return_value = None

        mock_category = MagicMock()
        mock_category.name = "RevoCord"
        mock_category.channels = []
        mock_category.edit = AsyncMock()
        mock_guild.create_category = AsyncMock(return_value=mock_category)

        mock_guild.fetch_channels = AsyncMock(return_value=[])

        async def real_mock_create(name: str, **kwargs: Any) -> Any:
            channel = MagicMock()
            if name == "portal":
                channel.__bool__.return_value = False
            channel.name = name
            channel.position = kwargs.get("position", 0)
            channel.edit = AsyncMock()
            return channel

        mock_guild.create_text_channel = real_mock_create

        await setup_cog.execute_setup(mock_interaction, mock_interaction.user, mock_interaction.guild)

        mock_interaction.followup.send.assert_called()
        calls = [call for call in mock_interaction.followup.send.mock_calls if "Portal channel failed to generate." in str(call)]
        assert len(calls) > 0

class TestSetupCogErrorHandling:
    @pytest.mark.asyncio
    async def test_check_failure(self, mock_bot: Any, mock_interaction: Any) -> None:
        cog = SetupCog(mock_bot)
        error = app_commands.CheckFailure()
        await cog.setup_command_error(mock_interaction, error)  # type: ignore
        mock_interaction.response.send_message.assert_called_once()
        assert "owner" in mock_interaction.response.send_message.call_args[0][0].lower()

    @pytest.mark.asyncio
    async def test_generic_error(self, mock_bot: Any, mock_interaction: Any) -> None:
        cog = SetupCog(mock_bot)
        error = Exception("Unexpected error")
        await cog.setup_command_error(mock_interaction, error)  # type: ignore
        mock_interaction.response.send_message.assert_not_called()



    @pytest.mark.asyncio
    @patch("mods.revocord.setup.logger")
    async def test_setup_exception(self, mock_logger: Any) -> None:
        from mods.revocord.setup import setup
        bot = MagicMock()
        bot.add_cog = AsyncMock(side_effect=Exception("Failed to add cog"))

        await setup(bot)

        mock_logger.error.assert_called_once()
        assert "Failed to add cog" in str(mock_logger.error.call_args[0][1])

class TestBiomeSelect:
    @pytest.mark.asyncio
    @patch("mods.revocord.setup.set_guild_biome", new_callable=AsyncMock)
    async def test_biome_callback(self, mock_set_biome: Any, mock_bot: Any, mock_interaction: Any) -> None:
        cog = SetupCog(mock_bot)
        cog.execute_setup = AsyncMock() # type: ignore

        select = BiomeSelect(cog, mock_interaction.user, mock_interaction.guild)
        select._values = ["Desert"]

        await select.callback(mock_interaction)

        mock_interaction.response.defer.assert_called_once()
        mock_set_biome.assert_called_once_with(mock_interaction.guild.id, "Desert")
        mock_interaction.edit_original_response.assert_called_once()
        assert "Desert" in mock_interaction.edit_original_response.call_args[1].get("content", "")
        cog.execute_setup.assert_called_once_with(mock_interaction, mock_interaction.user, mock_interaction.guild)
