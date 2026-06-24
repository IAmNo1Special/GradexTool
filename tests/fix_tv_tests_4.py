path = r"f:\projects\Revomon\GradexTool\tests\mods\revocord\test_tv.py"
with open(path, encoding="utf-8") as f:
    text = f.read()

text = text.replace(
    '@patch("mods.revocord.tv.get_or_create_account")',
    '@patch("mods.revocord.shared.get_or_create_account")',
)
text = text.replace(
    '@patch("mods.revocord.tv.build_console_embed")',
    '@patch("mods.revocord.portal.build_console_embed")',
)

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("Done")
