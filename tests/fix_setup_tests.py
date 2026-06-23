import re

path = r"f:\projects\Revomon\GradexTool\tests\mods\revocord\test_setup.py"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

# Replace setup_command.callback with execute_setup for the actual execution tests
text = re.sub(
    r'await setup_cog\.setup_command\.callback\(setup_cog, mock_interaction\)',
    r'await setup_cog.execute_setup(mock_interaction, mock_interaction.user, mock_interaction.guild)',
    text
)

# Also need to add tests for BiomeSelectView and BiomeSelect, and the setup_command itself
# Actually wait, test_missing_roles_permission etc STILL test setup_command.callback.
# Let's write a targeted script.
