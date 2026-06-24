from typing import Any
import re

path = r"f:\projects\Revomon\GradexTool\tests\mods\revocord\test_setup.py"
with open(path, encoding="utf-8") as f:
    text = f.read()

# 1. We MUST revert test_sends_biome_view to use setup_command.callback
text = text.replace(
    'await setup_cog.execute_setup(mock_interaction, mock_interaction.user, mock_interaction.guild)',
    'await setup_cog.setup_command.callback(setup_cog, mock_interaction)'
)

# 2. But we DO want test_setup_full_creation to use execute_setup.
def replace_in_test(test_name: Any, old: Any, new: Any, content: Any) -> str:
    pattern = rf"(def {test_name}\(.*?\):.*?)({re.escape(old)})"
    return re.sub(pattern, r"\1" + new, content, flags=re.DOTALL)

tests_to_execute_setup = [
    "test_setup_full_creation",
    "test_setup_existing_sync",
    "test_setup_fetch_fallback",
    "test_forbidden_exception",
    "test_generic_exception",
    "test_setup_portal_fail"
]

for test_name in tests_to_execute_setup:
    text = replace_in_test(
        test_name,
        "await setup_cog.setup_command.callback(setup_cog, mock_interaction)",
        "await setup_cog.execute_setup(mock_interaction, mock_interaction.user, mock_interaction.guild)",
        text
    )

# 3. Ensure test_setup_portal_fail uses a synchronous side_effect
sync_mock = '''
        def mock_create_text_channel(**kwargs: Any) -> None:
            if kwargs.get("name") == "portal":
                return None
            channel = MagicMock(spec=discord.TextChannel)
            channel.name = kwargs.get("name")
            channel.position = kwargs.get("position", 0)
            channel.edit = AsyncMock()
            return channel

        mock_guild.create_text_channel = AsyncMock(side_effect=mock_create_text_channel)
'''
text = re.sub(
    r'        # Override create_text_channel to return None specifically for portal.*?mock_guild\.create_text_channel = AsyncMock\(side_effect=mock_create_text_channel\)',
    sync_mock.strip(),
    text,
    flags=re.DOTALL
)

# 4. Add mock_category.edit = AsyncMock() to all places where mock_category is created
text = text.replace(
    'mock_category.name = "RevoCord"\n',
    'mock_category.name = "RevoCord"\n        mock_category.edit = AsyncMock()\n'
)

# 5. Fix test_setup_full_creation to not raise coroutine error on text channels
text = text.replace(
    'mock_guild.create_text_channel = AsyncMock(side_effect=[MagicMock(), MagicMock(), mock_portal, MagicMock()])',
    '''
        def mock_create_ch(*args: Any, **kwargs: Any) -> None:
            ch = MagicMock()
            ch.position = kwargs.get("position", 0)
            ch.edit = AsyncMock()
            return ch
        mock_guild.create_text_channel = AsyncMock(side_effect=lambda *args, **kwargs: mock_portal if kwargs.get("name") == "portal" else mock_create_ch(*args, **kwargs))
    '''
)

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("Done")
