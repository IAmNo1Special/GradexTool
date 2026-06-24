from typing import Any
import re

path = r"f:\projects\Revomon\GradexTool\tests\mods\revocord\test_hunting_part2.py"
with open(path, encoding="utf-8") as f:
    text = f.read()

# Remove the mock for _cleanup_wilds_spawn in the two tests that test it!
# The tests are: test_cleanup_wilds_spawn_exception and test_cleanup_wilds_spawn_success

def repl(match: Any) -> Any:
    # match.group(0) is the entire method. We just replace cog._cleanup_wilds_spawn = AsyncMock() with nothing
    return match.group(0).replace("        cog._cleanup_wilds_spawn = AsyncMock()\n", "")

text = re.sub(
    r'(    @pytest\.mark\.asyncio\n    @patch\("scripts\.gradexDB\.active_spawns_table\.remove_spawn", new_callable=AsyncMock\)\n    async def test_cleanup_wilds_spawn_exception.*?)(?=\n    @pytest|\Z)',
    repl,
    text,
    flags=re.DOTALL
)

text = re.sub(
    r'(    @pytest\.mark\.asyncio\n    @patch\("scripts\.gradexDB\.active_spawns_table\.remove_spawn", new_callable=AsyncMock\)\n    async def test_cleanup_wilds_spawn_success.*?)(?=\n    @pytest|\Z)',
    repl,
    text,
    flags=re.DOTALL
)

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("Done")
