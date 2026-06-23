import re

path = r"f:\projects\Revomon\GradexTool\tests\mods\revocord\test_setup.py"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

# Remove the print statements
text = text.replace('print("Calls:", mock_interaction.followup.send.mock_calls)', '')

# Fix test_setup_portal_fail
text = text.replace(
    'await setup_cog.setup_command.callback(setup_cog, mock_interaction)',
    'await setup_cog.execute_setup(mock_interaction, mock_interaction.user, mock_interaction.guild)'
)

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("Done")
