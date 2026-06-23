import re

path = r"f:\projects\Revomon\GradexTool\tests\mods\revocord\test_wilds_loop.py"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

text = text.replace(
    'patch("discord.ext.tasks.loop.start")',
    'patch.object(WildsLoopCog.wilds_spawn_loop, "start")'
)

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("Done")
