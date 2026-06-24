path = r"f:\projects\Revomon\GradexTool\tests\mods\revocord\test_hunting.py"
with open(path, encoding="utf-8") as f:
    text = f.read()

# 1. test_on_timeout_success
text = text.replace(
    "        mock_message.edit = AsyncMock()\n        mock_message.embeds = [MagicMock()]",
    '        mock_message.edit = AsyncMock()\n        embed = MagicMock()\n        embed.description = "Original"\n        mock_message.embeds = [embed]',
)

# 2. test_handle_wilds_claim
text = text.replace(
    "        mock_interaction.guild.get_channel = MagicMock(return_value=mock_channel)",
    "        mock_interaction.guild.get_channel = MagicMock(return_value=mock_channel)\n        mock_interaction.message = None",
)

# 3. test_spawn_catch_menu_with_orbs
text = text.replace(
    '        mock_get_account.return_value = {"inventory": {159: 1, 4: 2, 31: 3}}',
    '        mock_get_account.return_value = {"inventory": {"159": 1, 159: 1, "4": 2, 4: 2, "31": 3, 31: 3}}',
)

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("Done")
