path = r"f:\projects\Revomon\GradexTool\tests\mods\revocord\test_setup.py"
with open(path, encoding="utf-8") as f:
    text = f.read()

portal_fail_test = """    @pytest.mark.asyncio
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
            await setup_cog.setup_command.callback(setup_cog, mock_interaction)

"""

text = text.replace(
    "class TestSetupCogErrorHandling:",
    portal_fail_test + "class TestSetupCogErrorHandling:",
)

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("Done")
