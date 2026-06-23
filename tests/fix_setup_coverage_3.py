import re

path = r"f:\projects\Revomon\GradexTool\tests\mods\revocord\test_setup.py"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

text = text.replace(
    'await cog.setup_command._has_any_error_handlers() # Just to touch it maybe\n        # Let's call the raw callback\n        await cog.setup_command_error(mock_interaction, error)',
    'await cog.setup_command.on_error(mock_interaction, error)'
)

text = text.replace(
    'assert "Failed to add cog" in mock_logger.error.call_args[0][0]',
    'assert "Failed to add cog" in str(mock_logger.error.call_args[0][1])'
)

# Add mock_support to mock_category.channels
text = text.replace(
    'mock_category.channels = [mock_news, mock_event_board, mock_portal, mock_wilds]',
    'mock_category.channels = [mock_news, mock_event_board, mock_portal, mock_wilds, mock_support]'
)

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("Done")
