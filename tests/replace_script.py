path = r"f:\projects\Revomon\GradexTool\tests\mods\core\test_enforcement.py"
with open(path, encoding="utf-8") as f:
    text = f.read()
text = text.replace("mods.revocord.enforcement", "mods.core.enforcement")
with open(path, "w", encoding="utf-8") as f:
    f.write(text)
print("Done")
