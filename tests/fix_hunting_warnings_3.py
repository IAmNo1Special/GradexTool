from typing import Any
import re

path = r"f:\projects\Revomon\GradexTool\tests\mods\revocord\test_hunting_part2.py"
with open(path, encoding="utf-8") as f:
    text = f.read()

def repl(match: Any) -> str:
    indent = match.group(1)
    return f"{indent}cog = HuntingCog(mock_bot)\n{indent}cog._cleanup_wilds_spawn = AsyncMock()"

text = re.sub(r'([ \t]+)cog = HuntingCog\(mock_bot\)', repl, text)

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("Done")
