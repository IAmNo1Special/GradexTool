import re

path = r"f:\projects\Revomon\GradexTool\tests\mods\revocord\test_hunting.py"
with open(path, encoding="utf-8") as f:
    text = f.read()

# 1. Start by changing ALL `mock_interaction.edit_original_response` to `mock_interaction.response.send_message`
# to undo the global replace. Same for `followup.send`.
text = text.replace("mock_interaction.edit_original_response", "mock_interaction.response.send_message")

# Now apply specific fixes

# test_expired
text = re.sub(
    r'(async def test_expired\(self,.*?\):[\s\S]*?)mock_interaction\.response\.send_message\.assert_called_once\(\)\n\s*assert "expired" in mock_interaction\.response\.send_message\.call_args\[0\]\[0\]',
    r'\1mock_interaction.edit_original_response.assert_called_once()\n        assert "expired" in mock_interaction.edit_original_response.call_args[1]["content"]',
    text
)

# test_expired_delete_exception
text = re.sub(
    r'(async def test_expired_delete_exception\(self,.*?\):[\s\S]*?)mock_interaction\.response\.send_message\.assert_called_once\(\)',
    r'\1mock_interaction.edit_original_response.assert_called_once()',
    text
)

# test_no_database
text = re.sub(
    r'(async def test_no_database\(self,.*?\):[\s\S]*?)mock_interaction\.response\.send_message\.assert_called_once\(\)\n\s*assert "unavailable" in mock_interaction\.response\.send_message\.call_args\[0\]\[0\]',
    r'\1mock_interaction.followup.send.assert_called_once()\n        assert "unavailable" in mock_interaction.followup.send.call_args[0][0]',
    text
)

# test_no_eligible
text = re.sub(
    r'(async def test_no_eligible\(self,.*?\):[\s\S]*?)mock_interaction\.response\.send_message\.assert_called_once\(\)\n\s*assert "No wild" in mock_interaction\.response\.send_message\.call_args\[0\]\[0\]',
    r'\1mock_interaction.followup.send.assert_called_once()\n        assert "No wild" in mock_interaction.followup.send.call_args[0][0]',
    text
)

# test_spawn_success_shiny_file_exists
text = re.sub(
    r'(async def test_spawn_success_shiny_file_exists\(self,.*?\):[\s\S]*?)mock_interaction\.response\.send_message\.assert_called_once\(\)\n\s*kwargs = mock_interaction\.response\.send_message\.call_args\[1\]',
    r'\1mock_interaction.edit_original_response.assert_called_once()\n        kwargs = mock_interaction.edit_original_response.call_args[1]',
    text
)

# test_spawn_success_not_shiny_no_file
text = re.sub(
    r'(async def test_spawn_success_not_shiny_no_file\(self,.*?\):[\s\S]*?)mock_interaction\.response\.send_message\.assert_called_once\(\)\n\s*kwargs = mock_interaction\.response\.send_message\.call_args\[1\]',
    r'\1mock_interaction.edit_original_response.assert_called_once()\n        kwargs = mock_interaction.edit_original_response.call_args[1]',
    text
)

# test_spawn_throw_orb_success
text = re.sub(
    r'(async def test_spawn_throw_orb_success\(self,.*?\):[\s\S]*?)mock_interaction\.response\.send_message\.assert_called_once\(\)\n\s*assert "CAUGHT" in mock_interaction\.response\.send_message\.call_args\[0\]\[0\]',
    r'\1mock_interaction.response.edit_message.assert_called_once()\n        assert "CAUGHT" in mock_interaction.response.edit_message.call_args[1]["embed"].title',
    text
)

# test_spawn_throw_orb_fail_flee
text = re.sub(
    r'(async def test_spawn_throw_orb_fail_flee\(self,.*?\):[\s\S]*?)mock_interaction\.response\.send_message\.assert_called_once\(\)\n\s*assert "fled" in mock_interaction\.response\.send_message\.call_args\[0\]\[0\]',
    r'\1mock_interaction.response.edit_message.assert_called_once()\n        mock_interaction.followup.send.assert_called_once()\n        assert "fled" in mock_interaction.followup.send.call_args[0][0]',
    text
)

# Add patch for broadcast_encounter to prevent it returning MagicMock which causes warning
patch_broadcast = 'patch("mods.revocord.hunting.broadcast_encounter", new_callable=AsyncMock).start()\n'
if patch_broadcast not in text:
    text = text.replace('patch("mods.revocord.hunting.get_or_create_account", new_callable=AsyncMock, return_value={}).start()\n', 'patch("mods.revocord.hunting.get_or_create_account", new_callable=AsyncMock, return_value={}).start()\n' + patch_broadcast)

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("Done")
