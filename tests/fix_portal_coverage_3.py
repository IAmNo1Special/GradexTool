import re

path = r"f:\projects\Revomon\GradexTool\tests\mods\revocord\test_portal.py"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

test = '''
    @pytest.mark.asyncio
    async def test_portal_login_not_member(self) -> None:
        view = PortalLoginView()
        mock_interaction = MagicMock(spec=discord.Interaction)
        mock_interaction.response.defer = AsyncMock()
        mock_interaction.user = "not a member"
        
        button = view.children[0]
        await button.callback(mock_interaction)
        
        mock_interaction.response.defer.assert_called_once()
        mock_interaction.followup.send.assert_not_called()
'''

text = text.replace(
    'class TestPortalLoginViewButtons:',
    'class TestPortalLoginViewButtons:' + test
)

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("Done")
