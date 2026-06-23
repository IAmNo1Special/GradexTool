import re

path = r"f:\projects\Revomon\GradexTool\tests\mods\revomon\test_keywords.py"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

no_history_test = '''    @pytest.mark.asyncio
    async def test_update_rankings_no_history(self, mock_bot: Any) -> None:
        cog = PvpLeaderboard(mock_bot)
        mock_channel = MagicMock()
        del mock_channel.history  # So hasattr returns False
        mock_bot.get_channel = MagicMock(return_value=mock_channel)
        
        await cog.update_rankings()
        mock_bot.get_channel.assert_called_once()
'''

text = text.replace(
    '    @pytest.mark.asyncio\n    async def test_update_rankings_outer_exception',
    no_history_test + '\n    @pytest.mark.asyncio\n    async def test_update_rankings_outer_exception'
)

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("Done")
