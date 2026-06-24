path = r"f:\projects\Revomon\GradexTool\tests\mods\revocord\test_wilds_loop.py"
with open(path, encoding="utf-8") as f:
    text = f.read()

# Fix test_do_spawn_no_eligible
text = text.replace(
    """    @pytest.mark.asyncio
    @patch("mods.revocord.wilds_loop.get_guild_biome")
    async def test_do_spawn_no_eligible(self, mock_biome, cog):
        mock_biome.return_value = "water" # Pikachu is electric
        guild = MagicMock()
        guild.text_channels = [MagicMock(name="wilds")]
        guild.text_channels[0].name = "wilds"

        await cog._do_spawn(guild)
        guild.text_channels[0].send.assert_not_called()""",
    """    @pytest.mark.asyncio
    @patch("mods.revocord.wilds_loop.get_guild_biome")
    async def test_do_spawn_no_eligible(self, mock_biome, cog):
        mock_biome.return_value = "water" # Pikachu is neutral, but we will make allowed_types NOT neutral
        cog.revomons = [{"name": "Pikachu", "type1": "fire"}]
        # water biome doesn't allow fire
        guild = MagicMock()
        guild.text_channels = [MagicMock(name="wilds")]
        guild.text_channels[0].name = "wilds"

        with patch("mods.revocord.wilds_loop.BIOME_TYPES", {"water": {"water"}}):
            await cog._do_spawn(guild)
        guild.text_channels[0].send.assert_not_called()""",
)

# Cover line 63 (shiny fallback image)
text = text.replace(
    """    @pytest.mark.asyncio
    @patch("mods.revocord.wilds_loop.get_guild_biome")
    @patch("mods.revocord.wilds_loop.active_spawns_table")
    @patch("pathlib.Path.exists")
    async def test_do_spawn_success_with_image(self, mock_exists, mock_table, mock_biome, cog):""",
    """    @pytest.mark.asyncio
    @patch("random.random")
    @patch("mods.revocord.wilds_loop.get_guild_biome")
    @patch("mods.revocord.wilds_loop.active_spawns_table")
    @patch("pathlib.Path.exists")
    async def test_do_spawn_success_with_image(self, mock_exists, mock_table, mock_biome, mock_rand, cog):
        mock_rand.return_value = 0.0 # Force shiny
        mock_exists.side_effect = [False, True] # Shiny image doesn't exist, fallback does!""",
)

# Add tests for lines 133 and 141
tests = """
    @pytest.mark.asyncio
    async def test_loop_no_revomons(self, cog):
        cog.revomons = []
        await cog.wilds_spawn_loop() # Should return immediately

    @pytest.mark.asyncio
    @patch("scripts.gradexDB.update_guild_spawn_config")
    @patch("mods.revocord.wilds_loop.get_guild_spawn_config")
    @patch("mods.revocord.wilds_loop.active_spawns_table")
    async def test_loop_temp_limit(self, mock_table, mock_config, mock_update, cog):
        mock_config.return_value = {
            "max_spawn_limit": 5,
            "temp_limit_expires": 9999999999,
            "temp_spawn_limit": 5,
            "next_spawn_time": 0,
            "spawn_multiplier": 1.0,
            "spawn_multiplier_expires": 0
        }
        mock_table.count_guild_spawns = AsyncMock(return_value=6) # Over base limit, but under temp limit!
        cog._do_spawn = AsyncMock()

        guild = MagicMock()
        guild.id = 123
        cog.bot.guilds = [guild]

        await cog.wilds_spawn_loop()
        cog._do_spawn.assert_called_once()
"""
text = text.replace("class TestWildsLoopTasks:", "class TestWildsLoopTasks:" + tests)

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("Done")
