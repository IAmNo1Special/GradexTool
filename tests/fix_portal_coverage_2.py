
path = r"f:\projects\Revomon\GradexTool\tests\mods\revocord\test_portal.py"
with open(path, encoding="utf-8") as f:
    text = f.read()

text = text.replace(
    'mock_interaction.user = MagicMock(spec=discord.User)  # Not a Member',
    'mock_interaction.user = "not a member"'
)

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("Done")
