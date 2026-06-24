import json
from typing import Any
from unittest.mock import AsyncMock, MagicMock, mock_open, patch

import pytest

from mods.revocord.wilds_loop import WildsLoopCog, setup


class TestWildsLoopDataLoading:
    @patch("pathlib.Path.exists")
    @patch("builtins.open", new_callable=mock_open)
    def test_load_data_success(self, mock_file: Any, mock_exists: Any) -> None:
        mock_exists.return_value = True

        # We need side_effect to return different data based on what file is opened
        ev_data = json.dumps({"1": {"to": "Raichu"}})
        revomon_data = json.dumps(
            {"revomons": [{"name": "Pikachu", "type1": "neutral"}]}
        )
        natures_data = json.dumps([{"name": "hardy"}])

        def mock_open_side_effect(*args: Any, **kwargs: Any) -> Any:
            filename = str(args[0])
            if "evolutions.json" in filename:
                return mock_open(read_data=ev_data).return_value
            elif "revomon.json" in filename:
                return mock_open(read_data=revomon_data).return_value
            elif "natures.json" in filename:
                return mock_open(read_data=natures_data).return_value
            return mock_open(read_data="").return_value

        mock_file.side_effect = mock_open_side_effect

        bot = MagicMock()
        with patch("discord.ext.tasks.Loop.start"):
            cog = WildsLoopCog(bot)

        assert "raichu" in cog.evolved_names
        assert len(cog.revomons) == 1
        assert cog.revomons[0]["name"] == "Pikachu"
        assert len(cog.natures) == 1

    @patch("pathlib.Path.exists")
    @patch("builtins.open")
    def test_load_data_exceptions(self, mock_file: Any, mock_exists: Any) -> None:
        mock_exists.return_value = True
        mock_file.side_effect = Exception("Read error")

        bot = MagicMock()
        with patch("discord.ext.tasks.Loop.start"):
            cog = WildsLoopCog(bot)

        assert len(cog.evolved_names) == 0
        assert len(cog.revomons) == 0
        assert len(cog.natures) == 0

    @patch("pathlib.Path.exists")
    def test_load_data_no_files(self, mock_exists: Any) -> None:
        mock_exists.return_value = False

        bot = MagicMock()
        with patch("discord.ext.tasks.Loop.start"):
            cog = WildsLoopCog(bot)

        assert len(cog.evolved_names) == 0
        assert len(cog.revomons) == 0
        assert len(cog.natures) == 0


class TestWildsLoopSpawning:
    @pytest.fixture
    def cog(self) -> Any:
        bot = MagicMock()
        with patch("discord.ext.tasks.Loop.start"):
            cog = WildsLoopCog(bot)
        cog.revomons = [
            {
                "name": "Pikachu",
                "type1": "neutral",
                "dex_id": "25",
                "ability1": "static",
            }
        ]
        cog.natures = [{"name": "hardy"}]
        cog.evolved_names = set()
        return cog

    @pytest.mark.asyncio
    async def test_do_spawn_no_channel(self, cog: Any) -> None:
        guild = MagicMock()
        guild.text_channels = []
        await cog._do_spawn(guild)

    @pytest.mark.asyncio
    @patch("mods.revocord.wilds_loop.get_guild_biome")
    async def test_do_spawn_no_eligible(self, mock_biome: Any, cog: Any) -> None:
        mock_biome.return_value = (
            "water"  # Pikachu is neutral, but we will make allowed_types NOT neutral
        )
        cog.revomons = [{"name": "Pikachu", "type1": "fire"}]
        # water biome doesn't allow fire
        guild = MagicMock()
        guild.text_channels = [MagicMock(name="wilds")]
        guild.text_channels[0].name = "wilds"

        with patch("mods.revocord.wilds_loop.BIOME_TYPES", {"water": {"water"}}):
            await cog._do_spawn(guild)
        guild.text_channels[0].send.assert_not_called()

    @pytest.mark.asyncio
    @patch("mods.revocord.wilds_loop.get_guild_biome")
    @patch("mods.revocord.wilds_loop.active_spawns_table")
    @patch("pathlib.Path.exists")
    async def test_do_spawn_success_no_image(
        self, mock_exists: Any, mock_table: Any, mock_biome: Any, cog: Any
    ) -> None:
        mock_biome.return_value = "unknown"  # defaults to {"neutral"} allowed_types
        mock_exists.return_value = False

        guild = MagicMock()
        guild.id = 123
        wilds = MagicMock()
        wilds.name = "wilds"
        guild.text_channels = [wilds]

        msg = MagicMock()
        msg.id = 999
        msg.edit = AsyncMock()
        wilds.send = AsyncMock(return_value=msg)
        mock_table.add_spawn = AsyncMock()

        await cog._do_spawn(guild)

        wilds.send.assert_called_once()
        kwargs = wilds.send.call_args[1]
        assert "embed" in kwargs
        assert "view" in kwargs
        assert kwargs["embed"].description == "*Image sprite not found*"

        msg.edit.assert_called_once()
        mock_table.add_spawn.assert_called_once()

    @pytest.mark.asyncio
    @patch("random.random")
    @patch("mods.revocord.wilds_loop.get_guild_biome")
    @patch("mods.revocord.wilds_loop.active_spawns_table")
    @patch("pathlib.Path.exists")
    async def test_do_spawn_success_with_image(
        self,
        mock_exists: Any,
        mock_table: Any,
        mock_biome: Any,
        mock_rand: Any,
        cog: Any,
    ) -> None:
        mock_rand.return_value = 0.0  # Force shiny
        mock_exists.side_effect = [
            False,
            True,
        ]  # Shiny image doesn't exist, fallback does!
        mock_biome.return_value = "unknown"  # defaults to {"neutral"} allowed_types
        mock_exists.return_value = True

        guild = MagicMock()
        guild.id = 123
        wilds = MagicMock()
        wilds.name = "wilds"
        guild.text_channels = [wilds]

        msg = MagicMock()
        msg.id = 999
        msg.edit = AsyncMock()
        wilds.send = AsyncMock(return_value=msg)
        mock_table.add_spawn = AsyncMock()

        with patch("discord.File"):
            await cog._do_spawn(guild)

        wilds.send.assert_called_once()
        kwargs = wilds.send.call_args[1]
        assert "file" in kwargs
        assert "view" in kwargs
        assert kwargs["embed"].image.url == "attachment://revomon.png"


class TestWildsLoopTasks:
    @pytest.mark.asyncio
    async def test_loop_no_revomons(self, cog: Any) -> None:
        cog.revomons = []
        await cog.wilds_spawn_loop()  # Should return immediately

    @pytest.mark.asyncio
    @patch("scripts.gradexDB.update_guild_spawn_config")
    @patch("mods.revocord.wilds_loop.get_guild_spawn_config")
    @patch("mods.revocord.wilds_loop.active_spawns_table")
    async def test_loop_temp_limit(
        self, mock_table: Any, mock_config: Any, mock_update: Any, cog: Any
    ) -> None:
        mock_config.return_value = {
            "max_spawn_limit": 5,
            "temp_limit_expires": 9999999999,
            "temp_spawn_limit": 5,
            "next_spawn_time": 0,
            "spawn_multiplier": 1.0,
            "spawn_multiplier_expires": 0,
        }
        mock_table.count_guild_spawns = AsyncMock(
            return_value=6
        )  # Over base limit, but under temp limit!
        cog._do_spawn = AsyncMock()

        guild = MagicMock()
        guild.id = 123
        cog.bot.guilds = [guild]

        await cog.wilds_spawn_loop()
        cog._do_spawn.assert_called_once()

    @pytest.fixture
    def cog(self) -> Any:
        bot = MagicMock()
        with patch("discord.ext.tasks.Loop.start"):
            cog = WildsLoopCog(bot)
        cog.revomons = [{"name": "Pikachu"}]
        return cog

    @pytest.mark.asyncio
    @patch("mods.revocord.wilds_loop.get_guild_spawn_config")
    @patch("mods.revocord.wilds_loop.active_spawns_table")
    @patch("scripts.gradexDB.update_guild_spawn_config")
    async def test_loop_spawn(
        self, mock_update: Any, mock_table: Any, mock_config: Any, cog: Any
    ) -> None:
        mock_config.return_value = {
            "max_spawn_limit": 5,
            "temp_limit_expires": 0,
            "temp_spawn_limit": 0,
            "next_spawn_time": 0,
            "spawn_multiplier": 2.0,
            "spawn_multiplier_expires": 9999999999,
        }
        mock_table.count_guild_spawns = AsyncMock(return_value=0)
        cog._do_spawn = AsyncMock()

        guild = MagicMock()
        guild.id = 123
        cog.bot.guilds = [guild]

        await cog.wilds_spawn_loop()

        cog._do_spawn.assert_called_once_with(guild)
        mock_update.assert_called_once()

    @pytest.mark.asyncio
    @patch("mods.revocord.wilds_loop.get_guild_spawn_config")
    @patch("mods.revocord.wilds_loop.active_spawns_table")
    async def test_loop_limit_reached(
        self, mock_table: Any, mock_config: Any, cog: Any
    ) -> None:
        mock_config.return_value = {
            "max_spawn_limit": 5,
            "temp_limit_expires": 0,
            "temp_spawn_limit": 0,
            "next_spawn_time": 0,
        }
        mock_table.count_guild_spawns = AsyncMock(return_value=5)
        cog._do_spawn = AsyncMock()

        guild = MagicMock()
        guild.id = 123
        cog.bot.guilds = [guild]

        await cog.wilds_spawn_loop()
        cog._do_spawn.assert_not_called()

    @pytest.mark.asyncio
    @patch("mods.revocord.wilds_loop.get_guild_spawn_config")
    async def test_loop_exception(self, mock_config: Any, cog: Any) -> None:
        mock_config.side_effect = Exception("DB error")
        guild = MagicMock()
        cog.bot.guilds = [guild]

        # Should not raise
        await cog.wilds_spawn_loop()

    @pytest.mark.asyncio
    async def test_before_loop(self, cog: Any) -> None:
        cog.bot.wait_until_ready = AsyncMock()
        await cog.before_wilds_spawn_loop()
        cog.bot.wait_until_ready.assert_called_once()

    @pytest.mark.asyncio
    async def test_cog_unload(self, cog: Any) -> None:
        cog.wilds_spawn_loop.cancel = MagicMock()
        await cog.cog_unload()
        cog.wilds_spawn_loop.cancel.assert_called_once()

    @pytest.mark.asyncio
    async def test_setup(self) -> None:
        bot = MagicMock()
        bot.add_cog = AsyncMock()
        with patch("discord.ext.tasks.Loop.start"):
            await setup(bot)
        bot.add_cog.assert_called_once()
