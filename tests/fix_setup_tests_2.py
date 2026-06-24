path = r"f:\projects\Revomon\GradexTool\tests\mods\revocord\test_setup.py"
with open(path, encoding="utf-8") as f:
    text = f.read()

# Fix the test_setup_full_creation
text = text.replace(
    '@patch("mods.revocord.setup.ORDERED_WORKSPACES", ["portal", "Route 1", "dashboard"])\n    @patch("mods.revocord.setup.asyncio.sleep", new_callable=AsyncMock)',
    '@patch("mods.revocord.setup.asyncio.sleep", new_callable=AsyncMock)',
)

# Fix the test_biome_callback
text = text.replace('select.values = ["Desert"]', 'select._values = ["Desert"]')

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("Done")
