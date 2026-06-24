
path = r"f:\projects\Revomon\GradexTool\tests\mods\revocord\test_portal.py"
with open(path, encoding="utf-8") as f:
    text = f.read()

text = text.replace(
    '@patch("mods.revocord.portal.TVView")',
    '@patch("mods.revocord.tv.TVView")'
)
text = text.replace(
    '@patch("mods.revocord.portal.build_tv_embed")',
    '@patch("mods.revocord.tv.build_tv_embed")'
)

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("Done")
