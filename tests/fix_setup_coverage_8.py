path = r"f:\projects\Revomon\GradexTool\tests\mods\revocord\test_setup.py"
with open(path, encoding="utf-8") as f:
    text = f.read()

text = text.replace(
    "mock_guild.fetch_channels = AsyncMock(return_value=[])",
    "mock_guild.fetch_channels = AsyncMock(return_value=[])\n        mock_guild.text_channels = []",
)

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("Done")
