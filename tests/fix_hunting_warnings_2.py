import re

path = r"f:\projects\Revomon\GradexTool\tests\mods\revocord\test_hunting_part2.py"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

# Replace cog = HuntingCog(mock_bot) with cog._cleanup_wilds_spawn = AsyncMock() right after
# But wait, we need to import AsyncMock if it isn't, though it already is.
text = text.replace(
    "cog = HuntingCog(mock_bot)",
    "cog = HuntingCog(mock_bot)\n        cog._cleanup_wilds_spawn = AsyncMock()"
)

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("Done")
