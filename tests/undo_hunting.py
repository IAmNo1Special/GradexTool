import re

path = r"f:\projects\Revomon\GradexTool\tests\mods\revocord\test_hunting_part2.py"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

# Replace "cog = HuntingCog(mock_bot)\n        cog._cleanup_wilds_spawn = AsyncMock()" back to "cog = HuntingCog(mock_bot)"
# We need to match the exact string, but it could have any indentation.
# Actually, let's just use re.sub to match "cog = HuntingCog(mock_bot)" followed by ANY whitespace and "cog._cleanup_wilds_spawn = AsyncMock()"
text = re.sub(
    r'cog = HuntingCog\(mock_bot\)\s+cog\._cleanup_wilds_spawn = AsyncMock\(\)',
    r'cog = HuntingCog(mock_bot)',
    text
)

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("Done")
