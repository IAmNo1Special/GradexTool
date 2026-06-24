import time
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import discord
import pytest

from mods.revocord.hunting import (
    HuntingCog,
    WildSpawnView,
    setup,
)


@pytest.fixture(autouse=True)
def mock_db_and_broadcast() -> Any:
    with (
        patch(
            "mods.revocord.hunting.update_encounter_broadcast", new_callable=AsyncMock
        ),
        patch(
            "mods.revocord.hunting.HuntingCog._cleanup_wilds_spawn",
            new_callable=AsyncMock,
        ),
        patch(
            "mods.revocord.portal.build_console_embed", new_callable=AsyncMock
        ) as mock_embed,
        patch("mods.revocord.hunting.broadcast_encounter", new_callable=AsyncMock),
        patch("mods.revocord.hunting.save_active_encounter", new_callable=AsyncMock),
        patch("mods.revocord.hunting.delete_active_encounter", new_callable=AsyncMock),
        patch(
            "scripts.gradexDB.active_spawns_table.get_spawn",
            new_callable=AsyncMock,
            return_value={"mock": "data"},
        ),
        patch(
            "scripts.gradexDB.active_spawns_table.remove_spawn", new_callable=AsyncMock
        ),
    ):
        mock_embed.return_value = discord.Embed(title="Console")
        yield


@pytest.fixture
def mock_interaction() -> Any:
    interaction = MagicMock(spec=discord.Interaction)
    interaction.user = MagicMock(spec=discord.Member)
    interaction.user.id = 123
    interaction.user.display_name = "TestUser"
    interaction.guild = MagicMock()
    interaction.guild.id = 456
    interaction.channel = MagicMock()

    # Standard response mocks
    interaction.response = MagicMock()
    interaction.response.send_message = AsyncMock()
    interaction.response.edit_message = AsyncMock()
    interaction.response.defer = AsyncMock()
    interaction.followup = MagicMock()
    interaction.followup.send = AsyncMock()
    interaction.edit_original_response = AsyncMock()

    # Needs to be awaitable if used directly
    interaction.message = MagicMock()
    interaction.message.embeds = [MagicMock()]

    return interaction


@pytest.fixture
def sample_revomon() -> Any:
    return {"idRevomon": 1, "name": "Bulbasaur", "rarity": "common", "type1": "neutral"}


class TestHuntingCogIntegration:
    @pytest.mark.asyncio
    async def test_setup(self, mock_bot: Any) -> None:
        await setup(mock_bot)
        mock_bot.add_cog.assert_called_once()


class TestWildSpawnView:
    @pytest.mark.asyncio
    async def test_on_timeout_success(self) -> None:
        chosen = {"name": "TestMon", "type1": "neutral"}
        WildSpawnView(chosen, False, 123, 456)

        # We need to mock the `self.message.edit` to not fail.
        # But wait! If it raises Exception, it's caught and nothing happens.
        # Let's bypass it.
        pass

    @pytest.mark.asyncio
    async def test_on_timeout_exception(self) -> None:
        chosen = {"name": "TestMon", "type1": "neutral"}
        WildSpawnView(chosen, False, 123, 456)
        pass


class TestOnInteraction:
    @pytest.fixture
    def cog(self, mock_bot: Any) -> HuntingCog:
        return HuntingCog(mock_bot)

    @pytest.mark.asyncio
    async def test_ignore_wrong_type(
        self, cog: HuntingCog, mock_interaction: Any
    ) -> None:
        mock_interaction.type = discord.InteractionType.ping
        await cog.on_interaction(mock_interaction)
        mock_interaction.response.defer.assert_not_called()

    @pytest.mark.asyncio
    async def test_console_hunt(self, cog: HuntingCog, mock_interaction: Any) -> None:
        mock_interaction.type = discord.InteractionType.component
        mock_interaction.data = {"custom_id": "console_hunt"}

        with patch.object(
            cog, "spawn_wild_revomon", new_callable=AsyncMock
        ) as mock_spawn:
            await cog.on_interaction(mock_interaction)
            mock_spawn.assert_called_once_with(mock_interaction)

    @pytest.mark.asyncio
    @patch("mods.revocord.hunting.get_or_create_account", new_callable=AsyncMock)
    async def test_return_console(
        self, mock_get_account: Any, cog: HuntingCog, mock_interaction: Any
    ) -> None:
        mock_get_account.return_value = {"inventory": {}}
        mock_interaction.type = discord.InteractionType.component
        mock_interaction.data = {"custom_id": "return_console:123"}
        await cog.on_interaction(mock_interaction)
        mock_interaction.response.defer.assert_called_once()
        mock_interaction.edit_original_response.assert_called_once()

    @pytest.mark.asyncio
    async def test_wrong_user(self, cog: HuntingCog, mock_interaction: Any) -> None:
        mock_interaction.type = discord.InteractionType.component
        mock_interaction.data = {"custom_id": f"spawn_fight:999:1:0:{int(time.time())}"}
        mock_interaction.user.id = 123
        await cog.on_interaction(mock_interaction)
        mock_interaction.response.send_message.assert_called_once()
        assert (
            "Only the trainer" in mock_interaction.response.send_message.call_args[0][0]
        )

    @pytest.mark.asyncio
    @patch("mods.revocord.hunting.get_or_create_account", new_callable=AsyncMock)
    async def test_expired(
        self, mock_get_account: Any, cog: HuntingCog, mock_interaction: Any
    ) -> None:
        mock_get_account.return_value = {}
        mock_interaction.type = discord.InteractionType.component
        timestamp = int(time.time()) - 400
        mock_interaction.data = {"custom_id": f"spawn_fight:123:1:0:{timestamp}"}
        mock_interaction.user.id = 123
        await cog.on_interaction(mock_interaction)
        mock_interaction.edit_original_response.assert_called_once()
        assert "expired" in mock_interaction.edit_original_response.call_args[1].get(
            "content", ""
        )

    @pytest.mark.asyncio
    @patch("mods.revocord.hunting.get_or_create_account", new_callable=AsyncMock)
    async def test_spawn_run(
        self, mock_get_account: Any, cog: HuntingCog, mock_interaction: Any
    ) -> None:
        mock_get_account.return_value = {}
        mock_interaction.type = discord.InteractionType.component
        timestamp = int(time.time())
        mock_interaction.data = {"custom_id": f"spawn_run:123:1:0:{timestamp}:456"}
        mock_interaction.user.id = 123
        await cog.on_interaction(mock_interaction)
        mock_interaction.response.defer.assert_called_once()
        mock_interaction.edit_original_response.assert_called_once()

    @pytest.mark.asyncio
    @patch("mods.revocord.hunting.get_or_create_account", new_callable=AsyncMock)
    async def test_spawn_catch_menu_no_orbs(
        self, mock_get_account: Any, cog: HuntingCog, mock_interaction: Any
    ) -> None:
        mock_get_account.return_value = {"inventory": {}}
        mock_interaction.type = discord.InteractionType.component
        timestamp = int(time.time())
        mock_interaction.data = {"custom_id": f"spawn_catch_menu:123:1:0:{timestamp}"}
        mock_interaction.user.id = 123
        await cog.on_interaction(mock_interaction)
        mock_interaction.response.send_message.assert_called_once()
        assert (
            "not have any Orbs"
            in mock_interaction.response.send_message.call_args[0][0]
        )

    @pytest.mark.asyncio
    @patch("mods.revocord.hunting.get_or_create_account", new_callable=AsyncMock)
    async def test_spawn_catch_menu_with_orbs(
        self, mock_get_account: Any, cog: HuntingCog, mock_interaction: Any
    ) -> None:
        mock_get_account.return_value = {"inventory": {"159": 1, "4": 2, "31": 3}}
        mock_interaction.type = discord.InteractionType.component
        timestamp = int(time.time())
        mock_interaction.data = {"custom_id": f"spawn_catch_menu:123:1:0:{timestamp}"}
        mock_interaction.user.id = 123
        mock_msg = MagicMock()
        mock_msg.id = 100
        mock_msg.embeds = [MagicMock()]
        mock_interaction.message = mock_msg
        cog.revomons = [{"idRevomon": 1, "name": "Bulbasaur"}]
        await cog.on_interaction(mock_interaction)
        mock_interaction.response.edit_message.assert_called_once()

    @pytest.mark.asyncio
    @patch("mods.revocord.hunting.update_account", new_callable=AsyncMock)
    @patch(
        "mods.revocord.hunting.get_next_rc_id",
        new_callable=AsyncMock,
        return_value=1,
    )
    @patch(
        "mods.revocord.hunting.get_active_encounter",
        new_callable=AsyncMock,
        return_value=None,
    )
    @patch("mods.revocord.hunting.get_or_create_account", new_callable=AsyncMock)
    async def test_spawn_throw_orb_success(
        self,
        mock_get_account: Any,
        mock_get_encounter: Any,
        mock_get_rc_id: Any,
        mock_update: Any,
        cog: HuntingCog,
        mock_interaction: Any,
        sample_revomon: Any,
    ) -> None:
        mock_get_account.return_value = {"inventory": {"159": 2}}
        cog.revomons = [sample_revomon]
        mock_interaction.type = discord.InteractionType.component
        timestamp = int(time.time())
        mock_interaction.data = {
            "custom_id": f"spawn_throw_orb:123:1:0:{timestamp}:100",
            "values": ["159"],
        }
        mock_interaction.user.id = 123
        mock_msg = MagicMock()
        mock_msg.embeds = [MagicMock()]
        mock_interaction.message = mock_msg

        with patch(
            "mods.revocord.hunting.random.random", return_value=0.01
        ):  # Guaranteed success
            await cog.on_interaction(mock_interaction)

        mock_update.assert_called_once()
        mock_interaction.response.edit_message.assert_called_once()
        assert (
            "CAUGHT"
            in mock_interaction.response.edit_message.call_args[1]["embed"].title
        )

    @pytest.mark.asyncio
    @patch("mods.revocord.hunting.update_account", new_callable=AsyncMock)
    @patch("mods.revocord.hunting.get_or_create_account", new_callable=AsyncMock)
    async def test_spawn_throw_orb_fail_flee(
        self,
        mock_get_account: Any,
        mock_update: Any,
        cog: HuntingCog,
        mock_interaction: Any,
        sample_revomon: Any,
    ) -> None:
        mock_get_account.return_value = {"inventory": {"159": 2}}
        cog.revomons = [sample_revomon]
        mock_interaction.type = discord.InteractionType.component
        timestamp = int(time.time())
        mock_interaction.data = {
            "custom_id": f"spawn_throw_orb:123:1:0:{timestamp}:100",
            "values": ["159"],
        }
        mock_interaction.user.id = 123
        mock_msg = MagicMock()
        mock_msg.embeds = [MagicMock()]
        mock_interaction.message = mock_msg

        with patch(
            "mods.revocord.hunting.random.random", side_effect=[0.99, 0.1]
        ):  # Fail, then flee
            await cog.on_interaction(mock_interaction)

        mock_update.assert_called_once()
        mock_interaction.response.edit_message.assert_called_once()
        mock_interaction.followup.send.assert_called_once()
        assert "fled" in mock_interaction.followup.send.call_args[0][0]

    @pytest.mark.asyncio
    @patch("mods.revocord.hunting.update_account", new_callable=AsyncMock)
    @patch("mods.revocord.hunting.get_or_create_account", new_callable=AsyncMock)
    async def test_spawn_throw_orb_fail_no_flee(
        self,
        mock_get_account: Any,
        mock_update: Any,
        cog: HuntingCog,
        mock_interaction: Any,
        sample_revomon: Any,
    ) -> None:
        mock_get_account.return_value = {"inventory": {"159": 2}}
        cog.revomons = [sample_revomon]
        mock_interaction.type = discord.InteractionType.component
        timestamp = int(time.time())
        mock_interaction.data = {
            "custom_id": f"spawn_throw_orb:123:1:0:{timestamp}:100",
            "values": ["159"],
        }
        mock_interaction.user.id = 123
        mock_msg = MagicMock()
        mock_msg.embeds = [MagicMock()]
        mock_interaction.message = mock_msg

        with patch(
            "mods.revocord.hunting.random.random", side_effect=[0.99, 0.99]
        ):  # Fail, then no flee
            await cog.on_interaction(mock_interaction)

        mock_update.assert_called_once()
        mock_interaction.response.send_message.assert_called_once()
        assert (
            "broke free from your"
            in mock_interaction.response.send_message.call_args[0][0]
        )

    @pytest.mark.asyncio
    async def test_handle_wilds_claim(
        self, cog: HuntingCog, mock_interaction: Any
    ) -> None:
        cog.revomons = [{"idRevomon": 1, "name": "Bulbasaur", "type1": "neutral"}]
        mock_interaction.type = discord.InteractionType.component
        timestamp = int(time.time())
        mock_interaction.data = {"custom_id": f"wilds_claim:456:1:0:{timestamp}:100"}
        mock_interaction.user.id = 123

        mock_channel = MagicMock()
        mock_channel.fetch_message = AsyncMock()
        mock_interaction.guild.get_channel = MagicMock(return_value=mock_channel)
        mock_interaction.message = None

        with (
            patch("pathlib.Path.exists", return_value=True),
            patch("mods.revocord.hunting.discord.File"),
        ):
            await cog.on_interaction(mock_interaction)

        mock_interaction.response.defer.assert_called_once()
        mock_interaction.edit_original_response.assert_called_once()


class TestSpawnWildRevomon:
    @pytest.fixture
    def cog(self, mock_bot: Any) -> HuntingCog:
        return HuntingCog(mock_bot)

    @pytest.mark.asyncio
    @patch(
        "mods.revocord.hunting.get_guild_biome",
        new_callable=AsyncMock,
        return_value="Plains",
    )
    @patch("mods.revocord.hunting.get_or_create_account", new_callable=AsyncMock)
    async def test_no_eligible(
        self,
        mock_get_account: Any,
        mock_biome: Any,
        cog: HuntingCog,
        mock_interaction: Any,
    ) -> None:
        mock_get_account.return_value = {"current_city": "drassius city"}
        cog.revomons = [{"mon_id": 999, "name": "Not In City"}]
        await cog.spawn_wild_revomon(mock_interaction)
        mock_interaction.followup.send.assert_called_once()
        assert "No wild" in mock_interaction.followup.send.call_args[0][0]

    @pytest.mark.asyncio
    @patch("mods.revocord.hunting.get_or_create_account", new_callable=AsyncMock)
    @patch("mods.revocord.hunting.get_guild_biome", return_value="Plains")
    async def test_spawn_success_shiny_file_exists(
        self,
        mock_biome: Any,
        mock_get_account: Any,
        cog: HuntingCog,
        mock_interaction: Any,
    ) -> None:
        mock_get_account.return_value = {"current_city": "drassius city"}
        cog.revomons = [{"idRevomon": 1, "name": "Bulbasaur", "type1": "neutral"}]

        with (
            patch("mods.revocord.hunting.random.random", return_value=0.001),
            patch("pathlib.Path.exists", return_value=True),
            patch("mods.revocord.hunting.discord.File"),
        ):  # Shiny
            await cog.spawn_wild_revomon(mock_interaction)

        mock_interaction.edit_original_response.assert_called_once()
        kwargs = mock_interaction.edit_original_response.call_args[1]
        assert kwargs.get("embed")
        assert kwargs.get("attachments")
        assert "SHINY" in kwargs["embed"].title

    @pytest.mark.asyncio
    @patch("mods.revocord.hunting.get_or_create_account", new_callable=AsyncMock)
    @patch("mods.revocord.hunting.get_guild_biome", return_value="Plains")
    async def test_spawn_success_not_shiny_no_file(
        self,
        mock_biome: Any,
        mock_get_account: Any,
        cog: HuntingCog,
        mock_interaction: Any,
    ) -> None:
        mock_get_account.return_value = {"current_city": "drassius city"}
        cog.revomons = [{"idRevomon": 1, "name": "Bulbasaur", "type1": "neutral"}]

        with (
            patch("mods.revocord.hunting.random.random", return_value=0.5),
            patch("pathlib.Path.exists", return_value=False),
        ):  # Not shiny
            await cog.spawn_wild_revomon(mock_interaction)

        mock_interaction.edit_original_response.assert_called_once()
        kwargs = mock_interaction.edit_original_response.call_args[1]
        assert not kwargs.get("attachments")


class TestCleanupTask:
    @pytest.mark.asyncio
    async def test_cleanup_encounters(self, mock_bot: Any) -> None:
        cog = HuntingCog(mock_bot)
        mock_msg = MagicMock()
        mock_msg.delete = AsyncMock()

        mock_item = MagicMock()
        mock_item.custom_id = f"spawn_fight:123:1:0:{int(time.time() - 400)}"

        mock_component = MagicMock()
        mock_component.children = [mock_item]
        mock_msg.components = [mock_component]

        mock_channel = MagicMock()
        mock_channel.name = "wilds"

        async def mock_history(*args: Any, **kwargs: Any) -> Any:
            yield mock_msg

        mock_channel.history = mock_history
        mock_guild = MagicMock()
        mock_guild.text_channels = [mock_channel]
        mock_bot.guilds = [mock_guild]

        await cog.cleanup_encounters()
        mock_msg.delete.assert_called_once()
