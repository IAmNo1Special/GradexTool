path = r"f:\projects\Revomon\GradexTool\tests\mods\revocord\test_setup.py"
with open(path, encoding="utf-8") as f:
    text = f.read()

portal_fail_test_old = """    @pytest.mark.asyncio
    @patch("mods.revocord.setup.asyncio.sleep", new_callable=AsyncMock)
    @patch("mods.revocord.hunting.initial_wilds_spawn", new_callable=AsyncMock)
    async def test_setup_portal_fail(self, mock_spawn: Any, mock_sleep: Any, setup_cog: Any, mock_interaction: Any) -> None:
        mock_guild = mock_interaction.guild
        mock_guild.categories = []

        mock_category = MagicMock(spec=discord.CategoryChannel)
        mock_category.name = "RevoCord"
        mock_guild.create_category = AsyncMock(return_value=mock_category)

        mock_guild.fetch_channels = AsyncMock(return_value=[])

        # Override create_text_channel to return None specifically for portal
        async def mock_create_text_channel(**kwargs):
            if kwargs.get("name") == "portal":
                return None
            channel = MagicMock(spec=discord.TextChannel)
            channel.name = kwargs.get("name")
            return channel

        mock_guild.create_text_channel = AsyncMock(side_effect=mock_create_text_channel)

        with pytest.raises(Exception, match="Portal channel failed to generate."):
            await setup_cog.setup_command.callback(setup_cog, mock_interaction)"""

portal_fail_test_new = """    @pytest.mark.asyncio
    @patch("mods.revocord.setup.asyncio.sleep", new_callable=AsyncMock)
    @patch("mods.revocord.hunting.initial_wilds_spawn", new_callable=AsyncMock)
    async def test_setup_portal_fail(self, mock_spawn: Any, mock_sleep: Any, setup_cog: Any, mock_interaction: Any) -> None:
        mock_guild = mock_interaction.guild
        mock_guild.categories = []

        mock_category = MagicMock(spec=discord.CategoryChannel)
        mock_category.name = "RevoCord"
        mock_guild.create_category = AsyncMock(return_value=mock_category)

        mock_guild.fetch_channels = AsyncMock(return_value=[])

        # Override create_text_channel to return None specifically for portal
        async def mock_create_text_channel(**kwargs):
            if kwargs.get("name") == "portal":
                return None
            channel = MagicMock(spec=discord.TextChannel)
            channel.name = kwargs.get("name")
            return channel

        mock_guild.create_text_channel = AsyncMock(side_effect=mock_create_text_channel)

        await setup_cog.setup_command.callback(setup_cog, mock_interaction)

        # We expect it to catch the exception and send a followup
        mock_interaction.followup.send.assert_called()
        calls = [call for call in mock_interaction.followup.send.mock_calls if "Portal channel failed to generate." in str(call)]
        assert len(calls) > 0"""

text = text.replace(portal_fail_test_old, portal_fail_test_new)

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("Done")
