import re

path = r"f:\projects\Revomon\GradexTool\tests\mods\revocord\test_setup.py"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

# Fix generic and forbidden exception
text = text.replace(
    '''    @pytest.mark.asyncio
    async def test_forbidden_exception(self, setup_cog: Any, mock_interaction: Any) -> None:
        mock_guild = mock_interaction.guild
        mock_guild.categories = []
        
        class FakeResponse:
            status = 403
            reason = "Forbidden"
            
        mock_guild.fetch_channels = AsyncMock(side_effect=discord.Forbidden(FakeResponse(), "Forbidden"))  # type: ignore
        
        await setup_cog.setup_command.callback(setup_cog, mock_interaction)''',
    '''    @pytest.mark.asyncio
    async def test_forbidden_exception(self, setup_cog: Any, mock_interaction: Any) -> None:
        mock_guild = mock_interaction.guild
        mock_guild.categories = []
        
        class FakeResponse:
            status = 403
            reason = "Forbidden"
            
        mock_guild.fetch_channels = AsyncMock(side_effect=discord.Forbidden(FakeResponse(), "Forbidden"))  # type: ignore
        
        await setup_cog.execute_setup(mock_interaction, mock_interaction.user, mock_interaction.guild)'''
)

text = text.replace(
    '''    @pytest.mark.asyncio
    async def test_generic_exception(self, setup_cog: Any, mock_interaction: Any) -> None:
        mock_guild = mock_interaction.guild
        mock_guild.categories = []
        mock_guild.fetch_channels = AsyncMock(side_effect=Exception("Random error"))
        
        await setup_cog.setup_command.callback(setup_cog, mock_interaction)''',
    '''    @pytest.mark.asyncio
    async def test_generic_exception(self, setup_cog: Any, mock_interaction: Any) -> None:
        mock_guild = mock_interaction.guild
        mock_guild.categories = []
        mock_guild.fetch_channels = AsyncMock(side_effect=Exception("Random error"))
        
        await setup_cog.execute_setup(mock_interaction, mock_interaction.user, mock_interaction.guild)'''
)

# Fix test_setup_portal_fail by just throwing an exception directly inside create_text_channel, or returning a normal MagicMock then raising in _ensure_core_channel? No, if it returns None, _ensure_core_channel returns (None, True).
text = re.sub(
    r'    @pytest\.mark\.asyncio\n    @patch\("mods\.revocord\.setup\.asyncio\.sleep", new_callable=AsyncMock\)\n    @patch\("mods\.revocord\.hunting\.initial_wilds_spawn", new_callable=AsyncMock\)\n    async def test_setup_portal_fail.*?assert len\(calls\) > 0',
    '''    @pytest.mark.asyncio
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
        
        async def mock_create_text_channel(name, **kwargs):
            if name == "portal":
                return None
            channel = MagicMock()
            channel.name = name
            channel.position = kwargs.get("position", 0)
            channel.edit = AsyncMock()
            return channel
            
        mock_guild.create_text_channel = mock_create_text_channel
        
        await setup_cog.execute_setup(mock_interaction, mock_interaction.user, mock_interaction.guild)
        
        mock_interaction.followup.send.assert_called()
        calls = [call for call in mock_interaction.followup.send.mock_calls if "Portal channel failed to generate." in str(call)]
        assert len(calls) > 0''',
    text,
    flags=re.DOTALL
)

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("Done")
