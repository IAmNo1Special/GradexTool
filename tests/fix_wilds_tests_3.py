path = r"f:\projects\Revomon\GradexTool\tests\mods\revocord\test_wilds_loop.py"
with open(path, encoding="utf-8") as f:
    text = f.read()

text = text.replace(
    'mock_biome.return_value = "electric"',
    'mock_biome.return_value = "unknown" # defaults to {"neutral"} allowed_types',
)

text = text.replace('"type1": "electric"', '"type1": "neutral"')

text = text.replace(
    '@patch("mods.revocord.wilds_loop.update_guild_spawn_config")',
    '@patch("scripts.gradexDB.update_guild_spawn_config")',
)

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("Done")
