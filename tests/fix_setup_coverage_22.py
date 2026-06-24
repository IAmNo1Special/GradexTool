import re

path = r"f:\projects\Revomon\GradexTool\tests\mods\revocord\test_setup.py"
with open(path, encoding="utf-8") as f:
    text = f.read()

# Replace setup_command.callback with execute_setup in existing sync and fetch fallback
text = re.sub(
    r'(async def test_setup_existing_sync.*?)(await setup_cog\.setup_command\.callback\(setup_cog, mock_interaction\))',
    r'\1await setup_cog.execute_setup(mock_interaction, mock_interaction.user, mock_interaction.guild)',
    text,
    flags=re.DOTALL
)

text = re.sub(
    r'(async def test_setup_fetch_fallback.*?)(await setup_cog\.setup_command\.callback\(setup_cog, mock_interaction\))',
    r'\1await setup_cog.execute_setup(mock_interaction, mock_interaction.user, mock_interaction.guild)',
    text,
    flags=re.DOTALL
)

# In test_setup_existing_sync, change mock_portal.position so line 193 is hit
text = text.replace(
    'mock_portal.position = 2',
    'mock_portal.position = 999' # so it's != 2
)

# To cover initial wilds spawn trigger (lines 213-216), mock active_spawns_table in test_setup_existing_sync
text = re.sub(
    r'    async def test_setup_existing_sync\(self, mock_spawn: Any, mock_sleep: Any, setup_cog: Any, mock_interaction: Any\) -> None:',
    '''    @patch("scripts.gradexDB.active_spawns_table.count_guild_spawns", new_callable=AsyncMock, return_value=0)
    async def test_setup_existing_sync(self, mock_count: Any, mock_spawn: Any, mock_sleep: Any, setup_cog: Any, mock_interaction: Any) -> None:''',
    text
)

# To cover lines 231-233, 244 (Portal message already exists), make mock_history return a message from the bot
text = text.replace(
    '''        async def mock_history(*args: Any, **kwargs: Any) -> AsyncGenerator[Any, None]:
            yield MagicMock(author=setup_cog.bot.user)''',
    '''        async def mock_history(*args: Any, **kwargs: Any) -> AsyncGenerator[Any, None]:
            yield MagicMock(author=setup_cog.bot.user)''' # It already does! Wait, test_setup_existing_sync has mock_history
)

# Ensure mock_history is in test_setup_existing_sync
history_mock = '''
        async def mock_history(*args: Any, **kwargs: Any):
            msg = MagicMock(author=setup_cog.bot.user)
            yield msg
        mock_portal.history = mock_history
'''
text = re.sub(
    r'mock_portal = MagicMock\(spec=discord\.TextChannel\)\n        mock_portal\.name = "portal"\n        mock_portal\.position = 999\n        mock_portal\.id = 999\n        mock_portal\.edit = AsyncMock\(\)',
    r'mock_portal = MagicMock(spec=discord.TextChannel)\n        mock_portal.name = "portal"\n        mock_portal.position = 999\n        mock_portal.id = 999\n        mock_portal.edit = AsyncMock()\n' + history_mock,
    text
)

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("Done")
