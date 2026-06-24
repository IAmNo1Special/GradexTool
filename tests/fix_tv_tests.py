
path = r"f:\projects\Revomon\GradexTool\tests\mods\revocord\test_tv.py"
with open(path, encoding="utf-8") as f:
    text = f.read()

text = text.replace(
    'bot = MagicMock()',
    'bot = MagicMock()\n        bot.emojis = []'
)

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("Done")
