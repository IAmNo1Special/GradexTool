
path = r"f:\projects\Revomon\GradexTool\tests\mods\revocord\test_hunting.py"

with open(path, encoding="utf-8") as f:
    text = f.read()

# Add get_guild_biome mock and fix the Bulbasaur type to neutral
def fix_test(test_name, text):
    r'(async def ' + test_name + r'\(self,.*?mock_interaction: Any\)[^\:]*:\n\s+mock_get_account\.return_value = \{"current_city": "drassius city"\}\n\s+cog\.revomons = \[\{"mon_id": 1, "dex_id": 1, "name": "Bulbasaur"\}\])'

    # We want to insert @patch("mods.revocord.hunting.get_guild_biome", return_value="Plains")
    # before the def, and change the revomon to have type1="neutral"

    # Actually, let's just do a string replace since it's very specific
    old_def = 'async def ' + test_name + '(self, '
    new_def = '@patch("mods.revocord.hunting.get_guild_biome", return_value="Plains")\n    async def ' + test_name + '(self, mock_biome: Any, '
    text = text.replace(old_def, new_def)

    # The tests also set cog.revomons
    text = text.replace('cog.revomons = [{"mon_id": 1, "dex_id": 1, "name": "Bulbasaur"}]', 'cog.revomons = [{"mon_id": 1, "dex_id": 1, "name": "Bulbasaur", "type1": "neutral"}]')

    return text

text = fix_test("test_spawn_success_shiny_file_exists", text)
text = fix_test("test_spawn_success_shiny_fallback_to_normal", text)
text = fix_test("test_spawn_success_not_shiny_no_file", text)

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("Done")
