import re

path = r"f:\projects\Revomon\GradexTool\tests\mods\revocord\test_portal.py"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

test = '''    @pytest.mark.asyncio
    async def test_portal_login_not_member(self) -> None:
        view = PortalLoginView()
        mock_interaction = MagicMock(spec=discord.Interaction)
        mock_interaction.response.defer = AsyncMock()
        mock_interaction.user = MagicMock(spec=discord.User)  # Not a Member
        
        button = view.children[0]
        await button.callback(mock_interaction)
        
        mock_interaction.response.defer.assert_called_once()
        mock_interaction.followup.send.assert_not_called()'''

text = re.sub(
    r'class TestPortalLoginView:.*?(?=class TestGameConsoleView:)',
    r'class TestPortalLoginView:\n' + test + r'\n\n',
    text,
    flags=re.DOTALL
)

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("Done")
