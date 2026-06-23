import re

path = r"f:\projects\Revomon\GradexTool\tests\mods\revomon\test_keywords.py"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

inner_test = '''    async def test_update_rankings_inner_exceptions(self, mock_bot: Any) -> None:
        cog = PvpLeaderboard(mock_bot)
        mock_channel = MagicMock()
        
        async def mock_history(*args, **kwargs):
            mock_msg = MagicMock()
            mock_msg.delete = AsyncMock()
            yield mock_msg
            
        mock_channel.history = mock_history
        mock_current_msg = MagicMock()
        mock_current_msg.edit = AsyncMock(side_effect=Exception("Edit Error"))
        mock_channel.send = AsyncMock(return_value=mock_current_msg)
        mock_bot.get_channel = MagicMock(return_value=mock_channel)
        
        with patch.object(cog, 'get_current_pvp_data', side_effect=Exception("Data Error")), \\
             patch.object(cog, 'update_pvp_image', side_effect=Exception("Image Error")), \\
             patch('asyncio.sleep', new_callable=AsyncMock, side_effect=Exception("Break Loop")):
            
            await cog.update_rankings()'''

text = re.sub(
    r'    async def test_update_rankings_inner_exceptions\(self, mock_bot: Any\) -> None:.*?await cog\.update_rankings\(\)',
    inner_test,
    text,
    flags=re.DOTALL
)

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("Done")
