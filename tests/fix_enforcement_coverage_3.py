path = r"f:\projects\Revomon\GradexTool\tests\mods\core\test_enforcement.py"
with open(path, encoding="utf-8") as f:
    text = f.read()

# Remove the previously appended test block if it exists
text = text.split(
    '\n    @pytest.mark.asyncio\n    @patch("mods.core.enforcement.scripts.gradexDB.delete_guild_data"'
)[0]

test = """
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
        mock_delete.assert_called_once_with(123)"""

with open(path, "w", encoding="utf-8") as f:
    f.write(text + test)

print("Done")
