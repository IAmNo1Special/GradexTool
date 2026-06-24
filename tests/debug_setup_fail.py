
path = r"f:\projects\Revomon\GradexTool\tests\mods\revocord\test_setup.py"
with open(path, encoding="utf-8") as f:
    text = f.read()

# Add print to test_setup_portal_fail
print_code = '''        await setup_cog.setup_command.callback(setup_cog, mock_interaction)
        print("Calls:", mock_interaction.followup.send.mock_calls)'''
text = text.replace('        await setup_cog.setup_command.callback(setup_cog, mock_interaction)', print_code)

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("Done")
