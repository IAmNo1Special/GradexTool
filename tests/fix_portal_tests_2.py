
path = r"f:\projects\Revomon\GradexTool\tests\mods\revocord\test_portal.py"
with open(path, encoding="utf-8") as f:
    text = f.read()

text = text.replace(
    '    @patch("mods.revocord.portal.get_or_create_account")\n    @patch("mods.revocord.tv.build_tv_embed")\n    @patch("mods.revocord.tv.TVView")\n    async def test_tv_button_success',
    '    @patch("mods.revocord.shared.get_or_create_account")\n    @patch("mods.revocord.tv.build_tv_embed")\n    @patch("mods.revocord.tv.TVView")\n    async def test_tv_button_success'
)

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("Done")
