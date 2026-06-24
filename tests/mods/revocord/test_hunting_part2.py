import time
from typing import Any
from unittest.mock import AsyncMock, MagicMock, PropertyMock, patch

import discord
import pytest

from mods.revocord.hunting import HuntingCog, WildSpawnView, initial_wilds_spawn


@pytest.fixture
def mock_bot() -> Any:
    bot = MagicMock()
    bot.add_cog = AsyncMock()
    return bot

@pytest.fixture
def mock_interaction() -> Any:
    interaction = MagicMock(spec=discord.Interaction)
    interaction.user = MagicMock(spec=discord.Member)
    interaction.user.id = 123
    interaction.guild = MagicMock()
    interaction.guild.id = 456
    interaction.guild_id = 456

    interaction.response = MagicMock()
    interaction.response.send_message = AsyncMock()
    interaction.response.edit_message = AsyncMock()
    interaction.response.defer = AsyncMock()
    interaction.followup = MagicMock()
    interaction.followup.send = AsyncMock()
    interaction.edit_original_response = AsyncMock()
    return interaction

class TestHuntingCogInitPart2:
    def test_init_exceptions(self, mock_bot: Any) -> None:
        with patch("pathlib.Path.exists", return_value=True), \
             patch("builtins.open", side_effect=Exception("Test Error")):
            cog = HuntingCog(mock_bot)
            cog._cleanup_wilds_spawn = AsyncMock()
            assert not cog.evolved_names
            assert not cog.revomons
            assert not cog.natures

    def test_init_dict_data(self, mock_bot: Any) -> None:
        mock_file = MagicMock()
        mock_file.__enter__.return_value.read.side_effect = [
            '{"evo1": {"to": "evo2"}}', # evolutions
            '{"revomons": [{"mon_id": 1}]}', # revomons
            '[{"name": "hardy"}]' # natures
        ]
        with patch("pathlib.Path.exists", return_value=True), \
             patch("builtins.open", return_value=mock_file), \
             patch("json.load", side_effect=[
                 {"evo1": {"to": "evo2"}},
                 {"revomons": [{"mon_id": 1}]},
                 [{"name": "hardy"}]
             ]):
            cog = HuntingCog(mock_bot)
            cog._cleanup_wilds_spawn = AsyncMock()
            assert "evo2" in cog.evolved_names
            assert cog.revomons == [{"mon_id": 1}]
            assert cog.natures == [{"name": "hardy"}]

    def test_get_revomon_image_path_shiny_fallback(self, mock_bot: Any) -> None:
        cog = HuntingCog(mock_bot)
        cog._cleanup_wilds_spawn = AsyncMock()
        revomon_data = {"dex_id": 1}
        with patch("pathlib.Path.exists", return_value=False):
            path = cog._get_revomon_image_path(revomon_data, True)
            assert str(path).endswith("1.png")

class TestWildSpawnViewPart2:
    def test_event_msg_id_0(self) -> None:
        chosen = {"name": "TestMon", "type1": "neutral"}
        view = WildSpawnView(chosen, False, 123, 0)
        assert len(view.children) == 4

class TestOnInteractionPart2:
    @pytest.mark.asyncio
    async def test_on_interaction_bad_data(self, mock_bot: Any, mock_interaction: Any) -> None:
        cog = HuntingCog(mock_bot)
        cog._cleanup_wilds_spawn = AsyncMock()
        mock_interaction.type = discord.InteractionType.component

        mock_interaction.data = None
        await cog.on_interaction(mock_interaction)

        mock_interaction.data = []
        await cog.on_interaction(mock_interaction)

        mock_interaction.data = {"custom_id": None}
        await cog.on_interaction(mock_interaction)

        mock_interaction.data = {"custom_id": "unknown_prefix:123"}
        await cog.on_interaction(mock_interaction)

        mock_interaction.data = {"custom_id": "spawn_fight:invalid_parts"}
        await cog.on_interaction(mock_interaction)

    @pytest.mark.asyncio
    @patch("mods.revocord.hunting.get_or_create_account", new_callable=AsyncMock)
    @patch("mods.revocord.hunting.delete_active_encounter", new_callable=AsyncMock)
    @patch("mods.revocord.portal.build_console_embed", new_callable=AsyncMock)
    @patch("mods.revocord.hunting.update_encounter_broadcast", new_callable=AsyncMock)
    async def test_expired_exception(self, mock_bcast: Any, mock_embed: Any, mock_del: Any, mock_get_acc: Any, mock_bot: Any, mock_interaction: Any) -> None:
        mock_get_acc.return_value = {}
        mock_embed.return_value = discord.Embed()
        mock_bcast.side_effect = Exception("Test")
        cog = HuntingCog(mock_bot)
        cog._cleanup_wilds_spawn = AsyncMock()
        mock_interaction.type = discord.InteractionType.component
        timestamp = int(time.time()) - 400
        mock_interaction.data = {"custom_id": f"spawn_fight:123:1:0:{timestamp}:100"}
        mock_interaction.user.id = 123
        await cog.on_interaction(mock_interaction)
        mock_interaction.edit_original_response.assert_called_once()

    @pytest.mark.asyncio
    @patch("mods.revocord.hunting.get_or_create_account", new_callable=AsyncMock)
    @patch("mods.revocord.hunting.delete_active_encounter", new_callable=AsyncMock)
    @patch("mods.revocord.portal.build_console_embed", new_callable=AsyncMock)
    @patch("mods.revocord.hunting.update_encounter_broadcast", new_callable=AsyncMock)
    async def test_spawn_run_exception(self, mock_bcast: Any, mock_embed: Any, mock_del: Any, mock_get_acc: Any, mock_bot: Any, mock_interaction: Any) -> None:
        mock_get_acc.return_value = {}
        mock_embed.return_value = discord.Embed()
        mock_bcast.side_effect = Exception("Test")
        cog = HuntingCog(mock_bot)
        cog._cleanup_wilds_spawn = AsyncMock()
        mock_interaction.type = discord.InteractionType.component
        timestamp = int(time.time())
        mock_interaction.data = {"custom_id": f"spawn_run:123:1:0:{timestamp}:100"}
        mock_interaction.user.id = 123
        await cog.on_interaction(mock_interaction)
        mock_interaction.edit_original_response.assert_called_once()

    @pytest.mark.asyncio
    async def test_spawn_fight(self, mock_bot: Any, mock_interaction: Any) -> None:
        cog = HuntingCog(mock_bot)
        cog._cleanup_wilds_spawn = AsyncMock()
        mock_interaction.type = discord.InteractionType.component
        mock_interaction.data = {"custom_id": f"spawn_fight:123:1:0:{int(time.time())}:456"}
        mock_interaction.user.id = 123
        await cog.on_interaction(mock_interaction)
        mock_interaction.response.send_message.assert_called_once()

    @pytest.mark.asyncio
    @patch("mods.revocord.hunting.broadcast_encounter", new_callable=AsyncMock)
    async def test_spawn_share(self, mock_broadcast: Any, mock_bot: Any, mock_interaction: Any) -> None:
        cog = HuntingCog(mock_bot)
        cog._cleanup_wilds_spawn = AsyncMock()
        cog.revomons = [{"idRevomon": 1, "name": "Bulbasaur"}]
        mock_interaction.type = discord.InteractionType.component
        mock_interaction.data = {"custom_id": f"spawn_share:123:1:0:{int(time.time())}"}
        mock_interaction.user.id = 123
        mock_msg = MagicMock()
        mock_msg.embeds = [MagicMock()]
        mock_interaction.message = mock_msg
        await cog.on_interaction(mock_interaction)
        mock_broadcast.assert_called_once()
        mock_interaction.followup.send.assert_called_once()

    @pytest.mark.asyncio
    async def test_spawn_share_no_message(self, mock_bot: Any, mock_interaction: Any) -> None:
        cog = HuntingCog(mock_bot)
        cog._cleanup_wilds_spawn = AsyncMock()
        mock_interaction.type = discord.InteractionType.component
        mock_interaction.data = {"custom_id": f"spawn_share:123:1:0:{int(time.time())}"}
        mock_interaction.user.id = 123
        mock_interaction.message = None
        await cog.on_interaction(mock_interaction)
        mock_interaction.response.defer.assert_called_once()

    @pytest.mark.asyncio
    async def test_spawn_throw_orb_bad_data(self, mock_bot: Any, mock_interaction: Any) -> None:
        cog = HuntingCog(mock_bot)
        cog._cleanup_wilds_spawn = AsyncMock()
        mock_interaction.type = discord.InteractionType.component
        timestamp = int(time.time())
        base_id = f"spawn_throw_orb:123:1:0:{timestamp}:100"

        # bad data
        mock_interaction.data = []
        await cog.on_interaction(mock_interaction)

        # no values
        mock_interaction.data = {"custom_id": base_id, "values": []}
        await cog.on_interaction(mock_interaction)

        # empty orb_id
        mock_interaction.data = {"custom_id": base_id, "values": [""]}
        await cog.on_interaction(mock_interaction)

    @pytest.mark.asyncio
    async def test_spawn_throw_orb_no_embeds(self, mock_bot: Any, mock_interaction: Any) -> None:
        cog = HuntingCog(mock_bot)
        cog._cleanup_wilds_spawn = AsyncMock()
        mock_interaction.type = discord.InteractionType.component
        timestamp = int(time.time())
        mock_interaction.data = {"custom_id": f"spawn_throw_orb:123:1:0:{timestamp}:100", "values": ["159"]}
        mock_interaction.message = MagicMock()
        mock_interaction.message.embeds = []
        await cog.on_interaction(mock_interaction)
        mock_interaction.response.send_message.assert_called_once()

    @pytest.mark.asyncio
    @patch("mods.revocord.hunting.get_or_create_account", new_callable=AsyncMock)
    async def test_spawn_throw_orb_empty_orb(self, mock_get_acc: Any, mock_bot: Any, mock_interaction: Any) -> None:
        mock_get_acc.return_value = {"inventory": {"159": 0}}
        cog = HuntingCog(mock_bot)
        cog._cleanup_wilds_spawn = AsyncMock()
        mock_interaction.type = discord.InteractionType.component
        timestamp = int(time.time())
        mock_interaction.data = {"custom_id": f"spawn_throw_orb:123:1:0:{timestamp}:100", "values": ["159"]}
        mock_interaction.message = MagicMock()
        mock_interaction.message.embeds = [MagicMock()]
        await cog.on_interaction(mock_interaction)
        mock_interaction.response.send_message.assert_called_once()
        assert "don't have any more" in mock_interaction.response.send_message.call_args[0][0]

    @pytest.mark.asyncio
    @patch("mods.revocord.hunting.get_or_create_account", new_callable=AsyncMock)
    async def test_spawn_throw_orb_no_data(self, mock_get_acc: Any, mock_bot: Any, mock_interaction: Any) -> None:
        mock_get_acc.return_value = {"inventory": {"159": 1}}
        cog = HuntingCog(mock_bot)
        cog._cleanup_wilds_spawn = AsyncMock()
        cog.revomons = []
        mock_interaction.type = discord.InteractionType.component
        timestamp = int(time.time())
        mock_interaction.data = {"custom_id": f"spawn_throw_orb:123:1:0:{timestamp}:100", "values": ["159"]}
        mock_interaction.message = MagicMock()
        mock_interaction.message.embeds = [MagicMock()]
        await cog.on_interaction(mock_interaction)
        mock_interaction.response.send_message.assert_called_once()
        assert "not found" in mock_interaction.response.send_message.call_args[0][0]

    @pytest.mark.asyncio
    @patch("mods.revocord.hunting.get_or_create_account", new_callable=AsyncMock)
    @patch("mods.revocord.hunting.update_account", new_callable=AsyncMock)
    @patch("mods.revocord.hunting.get_active_encounter", new_callable=AsyncMock)
    @patch("mods.revocord.hunting.delete_active_encounter", new_callable=AsyncMock)
    @patch("mods.revocord.hunting.get_next_rc_id", new_callable=AsyncMock)
    @patch("mods.revocord.hunting.update_encounter_broadcast", new_callable=AsyncMock)
    async def test_spawn_throw_orb_success_all_branches(self, mock_bcast: Any, mock_rc_id: Any, mock_del: Any, mock_get_enc: Any, mock_update: Any, mock_get_acc: Any, mock_bot: Any, mock_interaction: Any) -> None:
        mock_get_acc.return_value = {"inventory": {"159": 1}, "caught_revomon": []}
        mock_get_enc.return_value = '{"nature": "brave", "ability": "overgrow", "ivs": {"hp": 31, "atk": 31, "def": 31, "spa": 31, "spd": 31, "spe": 31}}'
        mock_rc_id.return_value = 1000

        cog = HuntingCog(mock_bot)
        cog._cleanup_wilds_spawn = AsyncMock()
        cog.revomons = [{"idRevomon": 1, "name": "Bulbasaur"}]
        mock_interaction.type = discord.InteractionType.component
        timestamp = int(time.time())
        mock_interaction.data = {"custom_id": f"spawn_throw_orb:123:1:0:{timestamp}:100", "values": ["159"]}
        mock_interaction.message = MagicMock()
        mock_interaction.message.embeds = [MagicMock()]

        with patch("mods.revocord.hunting.random.random", return_value=0.01), \
             patch("pathlib.Path.exists", return_value=False): # Force no image fallback
            await cog.on_interaction(mock_interaction)

        mock_update.assert_called_once()
        mock_interaction.response.edit_message.assert_called_once()

    @pytest.mark.asyncio
    @patch("mods.revocord.hunting.get_or_create_account", new_callable=AsyncMock)
    @patch("mods.revocord.hunting.update_account", new_callable=AsyncMock)
    @patch("mods.revocord.hunting.get_active_encounter", new_callable=AsyncMock)
    @patch("mods.revocord.hunting.delete_active_encounter", new_callable=AsyncMock)
    @patch("mods.revocord.hunting.get_next_rc_id", new_callable=AsyncMock)
    @patch("mods.revocord.hunting.update_encounter_broadcast", new_callable=AsyncMock)
    async def test_spawn_throw_orb_success_json_error(self, mock_bcast: Any, mock_rc_id: Any, mock_del: Any, mock_get_enc: Any, mock_update: Any, mock_get_acc: Any, mock_bot: Any, mock_interaction: Any) -> None:
        mock_get_acc.return_value = {"inventory": {"159": 1}, "caught_revomon": []}
        mock_get_enc.return_value = 'invalid json'
        mock_rc_id.return_value = 1000

        cog = HuntingCog(mock_bot)
        cog._cleanup_wilds_spawn = AsyncMock()
        cog.revomons = [{"idRevomon": 1, "name": "Bulbasaur"}]
        mock_interaction.type = discord.InteractionType.component
        timestamp = int(time.time())
        mock_interaction.data = {"custom_id": f"spawn_throw_orb:123:1:0:{timestamp}:100", "values": ["159"]}
        mock_interaction.message = MagicMock()
        mock_interaction.message.embeds = [MagicMock()]

        with patch("mods.revocord.hunting.random.random", return_value=0.01), \
             patch("pathlib.Path.exists", return_value=False): # Force no image fallback
            await cog.on_interaction(mock_interaction)

        mock_update.assert_called_once()

    @pytest.mark.asyncio
    @patch("mods.revocord.hunting.get_or_create_account", new_callable=AsyncMock)
    @patch("mods.revocord.hunting.update_account", new_callable=AsyncMock)
    @patch("mods.revocord.hunting.delete_active_encounter", new_callable=AsyncMock)
    @patch("mods.revocord.hunting.update_encounter_broadcast", new_callable=AsyncMock)
    async def test_spawn_throw_orb_fail_flee_no_image(self, mock_bcast: Any, mock_del: Any, mock_update: Any, mock_get_acc: Any, mock_bot: Any, mock_interaction: Any) -> None:
        mock_get_acc.return_value = {"inventory": {"159": 1}, "caught_revomon": []}
        mock_bcast.side_effect = [Exception("Test"), None]

        cog = HuntingCog(mock_bot)
        cog._cleanup_wilds_spawn = AsyncMock()
        cog.revomons = [{"idRevomon": 1, "name": "Bulbasaur"}]
        mock_interaction.type = discord.InteractionType.component
        timestamp = int(time.time())
        mock_interaction.data = {"custom_id": f"spawn_throw_orb:123:1:0:{timestamp}:100", "values": ["159"]}
        mock_interaction.message = MagicMock()
        mock_interaction.message.embeds = [MagicMock()]

        with patch("mods.revocord.hunting.random.random", side_effect=[0.99, 0.1]), \
             patch("pathlib.Path.exists", return_value=False):
            await cog.on_interaction(mock_interaction)

        mock_interaction.response.edit_message.assert_called_once()

    @pytest.mark.asyncio
    @patch("mods.revocord.hunting.get_or_create_account", new_callable=AsyncMock)
    @patch("mods.revocord.hunting.update_account", new_callable=AsyncMock)
    @patch("mods.revocord.hunting.delete_active_encounter", new_callable=AsyncMock)
    @patch("mods.revocord.hunting.update_encounter_broadcast", new_callable=AsyncMock)
    async def test_spawn_throw_orb_fail_flee_with_image(self, mock_bcast: Any, mock_del: Any, mock_update: Any, mock_get_acc: Any, mock_bot: Any, mock_interaction: Any) -> None:
        mock_get_acc.return_value = {"inventory": {"159": 1}, "caught_revomon": []}

        cog = HuntingCog(mock_bot)
        cog._cleanup_wilds_spawn = AsyncMock()
        cog.revomons = [{"idRevomon": 1, "name": "Bulbasaur"}]
        mock_interaction.type = discord.InteractionType.component
        timestamp = int(time.time())
        mock_interaction.data = {"custom_id": f"spawn_throw_orb:123:1:0:{timestamp}:100", "values": ["159"]}
        mock_interaction.message = MagicMock()
        mock_interaction.message.embeds = [MagicMock()]

        with patch("mods.revocord.hunting.random.random", side_effect=[0.99, 0.1]), \
             patch("pathlib.Path.exists", return_value=True), \
             patch("mods.revocord.hunting.discord.File"):
            await cog.on_interaction(mock_interaction)

        mock_interaction.response.edit_message.assert_called_once()

    @pytest.mark.asyncio
    @patch("mods.revocord.hunting.get_or_create_account", new_callable=AsyncMock)
    @patch("mods.revocord.hunting.update_account", new_callable=AsyncMock)
    @patch("mods.revocord.hunting.get_active_encounter", new_callable=AsyncMock)
    @patch("mods.revocord.hunting.delete_active_encounter", new_callable=AsyncMock)
    @patch("mods.revocord.hunting.get_next_rc_id", new_callable=AsyncMock)
    @patch("mods.revocord.hunting.update_encounter_broadcast", new_callable=AsyncMock)
    async def test_spawn_throw_orb_success_with_image(self, mock_bcast: Any, mock_rc_id: Any, mock_del: Any, mock_get_enc: Any, mock_update: Any, mock_get_acc: Any, mock_bot: Any, mock_interaction: Any) -> None:
        mock_get_acc.return_value = {"inventory": {"159": 1}, "caught_revomon": []}
        mock_get_enc.return_value = '{"nature": "brave", "ability": "overgrow", "ivs": {"hp": 31, "atk": 31, "def": 31, "spa": 31, "spd": 31, "spe": 31}}'
        mock_rc_id.return_value = 1000

        cog = HuntingCog(mock_bot)
        cog._cleanup_wilds_spawn = AsyncMock()
        cog.revomons = [{"idRevomon": 1, "name": "Bulbasaur"}]
        mock_interaction.type = discord.InteractionType.component
        timestamp = int(time.time())
        mock_interaction.data = {"custom_id": f"spawn_throw_orb:123:1:0:{timestamp}:100", "values": ["159"]}
        mock_interaction.message = MagicMock()
        mock_interaction.message.embeds = [MagicMock()]

        with patch("mods.revocord.hunting.random.random", return_value=0.01), \
             patch("pathlib.Path.exists", return_value=True), \
             patch("mods.revocord.hunting.discord.File"):
            await cog.on_interaction(mock_interaction)

        mock_interaction.response.edit_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_spawn_throw_orb_property_mock_data(self, mock_bot: Any) -> None:
        cog = HuntingCog(mock_bot)
        cog._cleanup_wilds_spawn = AsyncMock()
        mock_interaction = MagicMock(spec=discord.Interaction)
        mock_interaction.type = discord.InteractionType.component
        mock_interaction.user = MagicMock()
        mock_interaction.user.id = 123
        timestamp = int(time.time())
        custom_id_val = f"spawn_throw_orb:123:1:0:{timestamp}:100"

        class MockDict(dict[str, Any]):
            pass

        d1 = MockDict({"custom_id": custom_id_val})
        d2 = None

        type(mock_interaction).data = PropertyMock(side_effect=[d1, d1, d1, d2, d2, d2])

        await cog.on_interaction(mock_interaction)

    @pytest.mark.asyncio
    @patch("scripts.gradexDB.active_spawns_table.remove_spawn", new_callable=AsyncMock)
    async def test_cleanup_wilds_spawn_exception(self, mock_remove: Any, mock_bot: Any) -> None:
        cog = HuntingCog(mock_bot)
        mock_remove.side_effect = Exception("Test")
        await cog._cleanup_wilds_spawn(None, 100)  # type: ignore[arg-type]
        # Should not raise

    @pytest.mark.asyncio
    @patch("scripts.gradexDB.active_spawns_table.remove_spawn", new_callable=AsyncMock)
    async def test_cleanup_wilds_spawn_success(self, mock_remove: Any, mock_bot: Any) -> None:
        cog = HuntingCog(mock_bot)
        mock_guild = MagicMock()
        mock_channel = MagicMock()
        mock_channel.name = "wilds"
        mock_msg = MagicMock()
        mock_msg.delete = AsyncMock()
        mock_channel.fetch_message = AsyncMock(return_value=mock_msg)
        mock_guild.text_channels = [mock_channel]

        with patch("discord.utils.get", return_value=mock_channel):
            await cog._cleanup_wilds_spawn(mock_guild, 100)

        mock_msg.delete.assert_called_once()

    @pytest.mark.asyncio
    @patch("scripts.gradexDB.active_spawns_table.get_spawn", new_callable=AsyncMock)
    async def test_handle_wilds_claim_branches(self, mock_get_spawn: Any, mock_bot: Any, mock_interaction: Any) -> None:
        cog = HuntingCog(mock_bot)
        cog._cleanup_wilds_spawn = AsyncMock()
        mock_interaction.type = discord.InteractionType.component

        # < 6 parts
        mock_interaction.data = {"custom_id": "wilds_claim:456"}
        await cog.on_interaction(mock_interaction)

        # no spawn data
        mock_get_spawn.return_value = None
        timestamp = int(time.time())
        mock_interaction.data = {"custom_id": f"wilds_claim:456:1:0:{timestamp}:100"}
        await cog.on_interaction(mock_interaction)
        mock_interaction.followup.send.assert_called_once()

        # no chosen
        mock_interaction.followup.send.reset_mock()
        mock_get_spawn.return_value = {"mock": "data"}
        cog.revomons = [{"idRevomon": 2, "name": "Charmander"}]
        await cog.on_interaction(mock_interaction)
        mock_interaction.followup.send.assert_called_once()

        # edit exception
        mock_interaction.followup.send.reset_mock()
        cog.revomons = [{"idRevomon": 1, "name": "Bulbasaur"}]
        mock_interaction.message = MagicMock()
        mock_interaction.message.edit = AsyncMock(side_effect=Exception("Test"))
        with patch("mods.revocord.hunting.save_active_encounter", new_callable=AsyncMock):
            await cog.on_interaction(mock_interaction)

        # edit without message
        mock_interaction.message = None
        with patch("mods.revocord.hunting.save_active_encounter", new_callable=AsyncMock):
            await cog.on_interaction(mock_interaction)
            mock_interaction.edit_original_response.assert_called_once()

    @pytest.mark.asyncio
    @patch("mods.revocord.hunting.get_guild_biome", new_callable=AsyncMock)
    @patch("mods.revocord.hunting.get_or_create_account", new_callable=AsyncMock)
    async def test_spawn_wild_no_revomons(self, mock_get_acc: Any, mock_biome: Any, mock_bot: Any, mock_interaction: Any) -> None:
        cog = HuntingCog(mock_bot)
        cog._cleanup_wilds_spawn = AsyncMock()
        cog.revomons = []
        await cog.spawn_wild_revomon(mock_interaction)
        mock_interaction.followup.send.assert_called_once()

    @pytest.mark.asyncio
    @patch("mods.revocord.hunting.get_guild_biome", new_callable=AsyncMock)
    @patch("mods.revocord.hunting.get_or_create_account", new_callable=AsyncMock)
    async def test_spawn_wild_no_guild(self, mock_get_acc: Any, mock_biome: Any, mock_bot: Any, mock_interaction: Any) -> None:
        cog = HuntingCog(mock_bot)
        cog._cleanup_wilds_spawn = AsyncMock()
        cog.revomons = [{"idRevomon": 1}]
        mock_interaction.guild_id = None
        await cog.spawn_wild_revomon(mock_interaction)
        mock_interaction.followup.send.assert_called_once()

    @pytest.mark.asyncio
    @patch("mods.revocord.hunting.get_guild_biome", new_callable=AsyncMock)
    @patch("mods.revocord.hunting.get_or_create_account", new_callable=AsyncMock)
    @patch("mods.revocord.hunting.save_active_encounter", new_callable=AsyncMock)
    @patch("mods.revocord.hunting.broadcast_encounter", new_callable=AsyncMock)
    async def test_spawn_wild_abilities(self, mock_bcast: Any, mock_save: Any, mock_get_acc: Any, mock_biome: Any, mock_bot: Any, mock_interaction: Any) -> None:
        mock_biome.return_value = "Plains"
        cog = HuntingCog(mock_bot)
        cog._cleanup_wilds_spawn = AsyncMock()
        cog.revomons = [{"idRevomon": 1, "name": "Bulbasaur", "type1": "neutral", "ability1": "overgrow"}]
        mock_interaction.guild_id = 456
        with patch("pathlib.Path.exists", return_value=False):
            await cog.spawn_wild_revomon(mock_interaction)
        mock_interaction.edit_original_response.assert_called_once()

    @pytest.mark.asyncio
    async def test_cleanup_encounters_exception(self, mock_bot: Any) -> None:
        cog = HuntingCog(mock_bot)
        cog._cleanup_wilds_spawn = AsyncMock()
        mock_channel = MagicMock()
        async def mock_history(*args: Any, **kwargs: Any) -> Any:
            yield MagicMock()
            raise Exception("Test")
        mock_channel.history = mock_history
        mock_guild = MagicMock()
        mock_guild.text_channels = [mock_channel]
        mock_bot.guilds = [mock_guild]
        await cog.cleanup_encounters()
        # Should not raise

    @pytest.mark.asyncio
    @patch("scripts.gradexDB.get_guild_spawn_config", new_callable=AsyncMock)
    async def test_initial_wilds_spawn(self, mock_get_config: Any, mock_bot: Any) -> None:
        mock_get_config.return_value = {"max_spawn_limit": 3}
        mock_wild_cog = MagicMock()
        mock_wild_cog._do_spawn = AsyncMock()
        mock_bot.get_cog.return_value = mock_wild_cog
        mock_guild = MagicMock()
        mock_guild.id = 456

        await initial_wilds_spawn(mock_bot, mock_guild)
        mock_wild_cog._do_spawn.assert_called_once()

    @pytest.mark.asyncio
    @patch("scripts.gradexDB.get_guild_spawn_config", new_callable=AsyncMock)
    async def test_initial_wilds_spawn_no_cog(self, mock_get_config: Any, mock_bot: Any) -> None:
        mock_bot.get_cog.return_value = None
        mock_guild = MagicMock()
        await initial_wilds_spawn(mock_bot, mock_guild)
        mock_get_config.assert_not_called()

    @pytest.mark.asyncio
    @patch("scripts.gradexDB.get_guild_spawn_config", new_callable=AsyncMock)
    async def test_initial_wilds_spawn_exception(self, mock_get_config: Any, mock_bot: Any) -> None:
        mock_get_config.return_value = {"max_spawn_limit": 3}
        mock_wild_cog = MagicMock()
        mock_wild_cog._do_spawn = AsyncMock(side_effect=Exception("Test"))
        mock_bot.get_cog.return_value = mock_wild_cog
        mock_guild = MagicMock()
        await initial_wilds_spawn(mock_bot, mock_guild)
        mock_wild_cog._do_spawn.assert_called_once()
