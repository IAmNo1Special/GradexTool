path = r"f:\projects\Revomon\GradexTool\tests\mods\revocord\test_hunting.py"
with open(path, encoding="utf-8") as f:
    text = f.read()

text = text.replace(
    'patch("mods.revocord.hunting.build_console_embed", new_callable=AsyncMock).start()\n',
    "",
)

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("Done")
