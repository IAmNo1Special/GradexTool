import re

path = r"f:\projects\Revomon\GradexTool\tests\mods\revocord\test_hunting.py"
with open(path, encoding="utf-8") as f:
    text = f.read()

# Fix the placement of the fixture
text = re.sub(
    r'(@pytest\.fixture\(autouse=True\)[\s\S]*?yield\n)',
    '',
    text
)

fixture_code = '''
@pytest.fixture(autouse=True)
def mock_db_and_broadcast():
    with patch("mods.revocord.hunting.update_encounter_broadcast", new_callable=AsyncMock), \\
         patch("mods.revocord.hunting.HuntingCog._cleanup_wilds_spawn", new_callable=AsyncMock), \\
         patch("mods.revocord.portal.build_console_embed", new_callable=AsyncMock), \\
         patch("mods.revocord.hunting.get_or_create_account", new_callable=AsyncMock, return_value={}), \\
         patch("mods.revocord.hunting.broadcast_encounter", new_callable=AsyncMock):
        yield
'''

text = re.sub(r'(import pytest\n)', r'\1' + fixture_code, text)

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("Done")
