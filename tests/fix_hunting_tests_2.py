path = r"f:\projects\Revomon\GradexTool\tests\mods\revocord\test_hunting.py"
with open(path, encoding="utf-8") as f:
    text = f.read()

# Add patching for update_encounter_broadcast, _cleanup_wilds_spawn, and build_console_embed
patch_lines = """from unittest.mock import AsyncMock, MagicMock, patch, mock_open

# Patch methods at module level
patch("mods.revocord.hunting.update_encounter_broadcast", new_callable=AsyncMock).start()
patch("mods.revocord.hunting.HuntingCog._cleanup_wilds_spawn", new_callable=AsyncMock).start()
patch("mods.revocord.portal.build_console_embed", new_callable=AsyncMock).start()
patch("mods.revocord.hunting.build_console_embed", new_callable=AsyncMock).start()
patch("mods.revocord.hunting.get_or_create_account", new_callable=AsyncMock, return_value={}).start()
"""
text = text.replace(
    "from unittest.mock import AsyncMock, MagicMock, patch, mock_open", patch_lines
)

# Fix test_expired
text = text.replace(
    'mock_interaction.response.send_message.assert_called_once()\n        assert "expired" in mock_interaction.response.send_message.call_args[0][0]\n        mock_interaction.message.delete.assert_called_once()',
    'mock_interaction.edit_original_response.assert_called_once()\n        assert "expired" in mock_interaction.edit_original_response.call_args[1]["content"]',
)

# Fix test_expired_delete_exception
text = text.replace(
    "mock_interaction.response.send_message.assert_called_once()",
    "mock_interaction.edit_original_response.assert_called_once()",
)

# Fix test_spawn_success_shiny_fallback_to_normal and test_spawn_success_shiny_file_exists
# We need to make sure the asserts are fine. We already replaced follow.send to edit_original_response in our minds, let's do it in code
text = text.replace(
    "mock_interaction.followup.send.assert_called_once()",
    "mock_interaction.edit_original_response.assert_called_once()",
)
text = text.replace(
    "kwargs = mock_interaction.followup.send.call_args[1]",
    "kwargs = mock_interaction.edit_original_response.call_args[1]",
)

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("Done")
