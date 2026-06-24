import re

path = r"f:\projects\Revomon\GradexTool\tests\mods\revocord\test_setup.py"
with open(path, encoding="utf-8") as f:
    text = f.read()

# Fix test_setup_full_creation
text = re.sub(
    r'(async def test_setup_full_creation.*?)(await setup_cog\.setup_command\.callback\(setup_cog, mock_interaction\))',
    r'\1await setup_cog.execute_setup(mock_interaction, mock_interaction.user, mock_interaction.guild)',
    text,
    flags=re.DOTALL
)

# Fix test_setup_portal_fail to use Exception raising instead of side_effect
portal_fail_mock = '''
        async def mock_create_text_channel(name, **kwargs):
            if name == "portal":
                raise Exception("Portal channel failed to generate.")
            channel = MagicMock()
            channel.name = name
            channel.position = kwargs.get("position", 0)
            channel.edit = AsyncMock()
            return channel

        mock_guild.create_text_channel = mock_create_text_channel
'''
text = re.sub(
    r'        def mock_create_text_channel.*?mock_guild\.create_text_channel = AsyncMock\(side_effect=mock_create_text_channel\)',
    portal_fail_mock.strip(),
    text,
    flags=re.DOTALL
)

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("Done")
