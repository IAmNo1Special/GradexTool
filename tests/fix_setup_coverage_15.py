import re

path = r"f:\projects\Revomon\GradexTool\tests\mods\revocord\test_setup.py"
with open(path, encoding="utf-8") as f:
    text = f.read()

text = text.replace(
    """    @pytest.mark.asyncio
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

        def mock_create_ch(*args, **kwargs):
            ch = MagicMock()
            ch.position = kwargs.get("position", 0)
            ch.edit = AsyncMock()
            return ch
        mock_guild.create_text_channel = AsyncMock(side_effect=lambda *args, **kwargs: mock_portal if kwargs.get("name") == "portal" else mock_create_ch(*args, **kwargs))


        await setup_cog.setup_command.callback(setup_cog, mock_interaction)""",
    """    @pytest.mark.asyncio
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

        def mock_create_ch(*args, **kwargs):
            ch = MagicMock()
            ch.position = kwargs.get("position", 0)
            ch.edit = AsyncMock()
            return ch
        mock_guild.create_text_channel = AsyncMock(side_effect=lambda *args, **kwargs: mock_portal if kwargs.get("name") == "portal" else mock_create_ch(*args, **kwargs))


        await setup_cog.execute_setup(mock_interaction, mock_interaction.user, mock_interaction.guild)""",
)

text = re.sub(
    r'    @pytest\.mark\.asyncio\n    @patch\("mods\.revocord\.setup\.asyncio\.sleep", new_callable=AsyncMock\)\n    @patch\("mods\.revocord\.hunting\.initial_wilds_spawn", new_callable=AsyncMock\)\n    async def test_setup_portal_fail.*?assert len\(calls\) > 0',
    """    @pytest.mark.asyncio
    @patch("mods.revocord.setup.asyncio.sleep", new_callable=AsyncMock)
    @patch("mods.revocord.hunting.initial_wilds_spawn", new_callable=AsyncMock)
    async def test_setup_portal_fail(self, mock_spawn: Any, mock_sleep: Any, setup_cog: Any, mock_interaction: Any) -> None:
        mock_guild = mock_interaction.guild
        mock_guild.categories = []
        mock_guild.text_channels = []

        mock_category = MagicMock()
        mock_category.name = "RevoCord"
        mock_category.channels = []
        mock_category.edit = AsyncMock()
        mock_guild.create_category = AsyncMock(return_value=mock_category)

        mock_guild.fetch_channels = AsyncMock(return_value=[])

        def mock_create_text_channel(*args, **kwargs):
            name = args[0] if args else kwargs.get("name")
            if name == "portal":
                return None
            channel = MagicMock()
            channel.name = name
            channel.position = kwargs.get("position", 0)
            channel.edit = AsyncMock()
            return channel

        mock_guild.create_text_channel = AsyncMock(side_effect=mock_create_text_channel)

        await setup_cog.execute_setup(mock_interaction, mock_interaction.user, mock_interaction.guild)

        mock_interaction.followup.send.assert_called()
        calls = [call for call in mock_interaction.followup.send.mock_calls if "Portal channel failed to generate." in str(call)]
        assert len(calls) > 0""",
    text,
    flags=re.DOTALL,
)

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("Done")
