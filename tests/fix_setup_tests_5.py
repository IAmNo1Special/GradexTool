path = r"f:\projects\Revomon\GradexTool\tests\mods\revocord\test_setup.py"
with open(path, encoding="utf-8") as f:
    text = f.read()

text = text.replace(
    '@patch("mods.revocord.setup.initial_wilds_spawn", new_callable=AsyncMock)',
    '@patch("mods.revocord.hunting.initial_wilds_spawn", new_callable=AsyncMock)',
)

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("Done")
