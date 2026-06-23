import re

path = r"f:\projects\Revomon\GradexTool\tests\mods\revocord\test_portal.py"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

new_test = """    @pytest.mark.asyncio
    async def test_login_callback_not_member(self, mock_interaction: Any) -> None:
        view = PortalLoginView()
        login_button = next((child for child in view.children if getattr(child, 'custom_id', '') == "persistent_portal_login"))
        
        mock_interaction.user = discord.User(state=MagicMock(), data={'id': 1, 'username': 'test', 'discriminator': '1234', 'avatar': None})
        
        await login_button.callback(mock_interaction)
        
        mock_interaction.response.defer.assert_called_once_with(ephemeral=True)
        mock_interaction.followup.send.assert_not_called()
"""

text = text.replace(
    'class TestGameConsoleView:',
    new_test + '\nclass TestGameConsoleView:'
)

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("Done")
