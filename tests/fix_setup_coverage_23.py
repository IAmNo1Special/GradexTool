import re

path = r"f:\projects\Revomon\GradexTool\tests\mods\revocord\test_setup.py"
with open(path, encoding="utf-8") as f:
    text = f.read()

# I will replace the test_setup_portal_fail again.
good_test = """    @pytest.mark.asyncio
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

        async def real_mock_create(name, **kwargs):
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
        assert len(calls) > 0"""

text = re.sub(
    r'    @pytest\.mark\.asyncio\n    @patch\("mods\.revocord\.setup\.asyncio\.sleep", new_callable=AsyncMock\)\n    @patch\("mods\.revocord\.hunting\.initial_wilds_spawn", new_callable=AsyncMock\)\n    @patch\("mods\.revocord\.setup\.discord\.utils\.get"\)\n    async def test_setup_portal_fail.*?assert len\(calls\) > 0',
    good_test,
    text,
    flags=re.DOTALL,
)

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("Done")
