import re

path = r"f:\projects\Revomon\GradexTool\tests\mods\revocord\test_hunting_part2.py"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

# Add a patch for _cleanup_wilds_spawn to all tests in TestOnInteractionPart2
text = re.sub(
    r'(class TestOnInteractionPart2:\s+@pytest\.fixture\(autouse=True\)\s+def setup_method\(self, mock_bot\):\s+)',
    r'\g<1>patcher = patch("mods.revocord.hunting.HuntingCog._cleanup_wilds_spawn", new_callable=AsyncMock)\n        self.mock_cleanup = patcher.start()\n        self.addCleanup(patcher.stop)\n        ',
    text
)

# Also need to add addCleanup support to the fixture, but pytest setup_method doesn't have addCleanup.
# Better to yield or use a proper fixture.

# Alternatively, just use patch.object on all methods or inside the setup.

text2 = '''    @pytest.fixture(autouse=True)
    def setup_method(self, mock_bot):
        patcher = patch("mods.revocord.hunting.HuntingCog._cleanup_wilds_spawn", new_callable=AsyncMock)
        self.mock_cleanup = patcher.start()
        yield
        patcher.stop()'''

text = re.sub(
    r'    @pytest\.fixture\(autouse=True\)\n    def setup_method\(self, mock_bot\):.*?mock_bot',
    text2,
    text,
    flags=re.DOTALL
)

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("Done")
