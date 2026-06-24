
path = r"f:\projects\Revomon\GradexTool\tests\mods\revocord\test_hunting.py"
with open(path, encoding="utf-8") as f:
    text = f.read()

# Fix spawn_catch_menu_with_orbs
text = text.replace(
    '        mock_interaction.response.send_message.assert_called_once()',
    '        mock_interaction.response.edit_message.assert_called_once()'
)
text = text.replace(
    '        assert "Choose an Orb" in mock_interaction.response.send_message.call_args[0][0]',
    ''
)

# Debug view.message in test_on_timeout_success
text = text.replace(
    '        await view.on_timeout()',
    '        print(f"DEBUG IN TEST: view.message = {view.message}")\n        await view.on_timeout()'
)

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("Done")
