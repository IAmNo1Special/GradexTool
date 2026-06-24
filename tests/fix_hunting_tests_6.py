path = r"f:\projects\Revomon\GradexTool\tests\mods\revocord\test_hunting.py"
with open(path, encoding="utf-8") as f:
    text = f.read()

# test_expired
text = text.replace(
    'mock_interaction.response.send_message.assert_called_once()\n        assert "expired" in mock_interaction.response.send_message.call_args[0][0]',
    'mock_interaction.edit_original_response.assert_called_once()\n        assert "expired" in mock_interaction.edit_original_response.call_args[1].get("content", "")',
)

# test_expired_delete_exception
text = text.replace(
    "mock_interaction.message.delete = AsyncMock(side_effect=Exception())\n        await cog.on_interaction(mock_interaction)\n        mock_interaction.response.send_message.assert_called_once()",
    "mock_interaction.message.delete = AsyncMock(side_effect=Exception())\n        await cog.on_interaction(mock_interaction)\n        mock_interaction.edit_original_response.assert_called_once()",
)

# test_spawn_throw_orb_success
text = text.replace(
    'mock_msg.edit.assert_called_once()\n        mock_interaction.response.send_message.assert_called_once()\n        assert "Gotcha!" in mock_interaction.response.send_message.call_args[0][0]\n        assert "SHINY" in mock_interaction.response.send_message.call_args[0][0]',
    'mock_interaction.response.edit_message.assert_called_once()\n        assert "CAUGHT" in mock_interaction.response.edit_message.call_args[1]["embed"].title',
)

# test_spawn_throw_orb_fail_flee
text = text.replace(
    'mock_msg.edit.assert_called_once()\n        mock_interaction.response.send_message.assert_called_once()\n        assert "fled" in mock_interaction.response.send_message.call_args[0][0]',
    'mock_interaction.response.edit_message.assert_called_once()\n        mock_interaction.followup.send.assert_called_once()\n        assert "fled" in mock_interaction.followup.send.call_args[0][0]',
)

# test_no_database
text = text.replace(
    'mock_interaction.response.send_message.assert_called_once()\n        assert "unavailable" in mock_interaction.followup.send.call_args[0][0]',
    'mock_interaction.followup.send.assert_called_once()\n        assert "unavailable" in mock_interaction.followup.send.call_args[0][0]',
)

# test_no_eligible
text = text.replace(
    'mock_interaction.response.send_message.assert_called_once()\n        assert "No wild" in mock_interaction.followup.send.call_args[0][0]',
    'mock_interaction.followup.send.assert_called_once()\n        assert "No wild" in mock_interaction.followup.send.call_args[0][0]',
)

# test_spawn_success_shiny_file_exists
text = text.replace(
    "await cog.spawn_wild_revomon(mock_interaction)\n        mock_interaction.response.send_message.assert_called_once()\n        kwargs = mock_interaction.response.send_message.call_args[1]",
    "await cog.spawn_wild_revomon(mock_interaction)\n        mock_interaction.edit_original_response.assert_called_once()\n        kwargs = mock_interaction.edit_original_response.call_args[1]",
)

# test_spawn_success_not_shiny_no_file
text = text.replace(
    "await cog.spawn_wild_revomon(mock_interaction)\n        mock_interaction.response.send_message.assert_called_once()\n        kwargs = mock_interaction.response.send_message.call_args[1]",
    "await cog.spawn_wild_revomon(mock_interaction)\n        mock_interaction.edit_original_response.assert_called_once()\n        kwargs = mock_interaction.edit_original_response.call_args[1]",
)

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("Done")
