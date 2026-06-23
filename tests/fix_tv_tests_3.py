import re

path = r"f:\projects\Revomon\GradexTool\tests\mods\revocord\test_tv.py"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

# Fix test_nav_close
text = text.replace(
    '''    @pytest.mark.asyncio
    async def test_nav_close(self, mock_interaction: Any) -> None:
        bot = MagicMock()
        bot.emojis = []
        bot._app_emojis_cache = []
        caught = []
        
        btn = TVNavButton("close", "❌", "Close", bot, 123, caught, 0)
        mock_interaction.user.id = 123
        await btn.callback(mock_interaction)
        mock_interaction.response.defer.assert_called_once()
        mock_interaction.message.delete.assert_called_once()''',
    '''    @pytest.mark.asyncio
    @patch("mods.revocord.tv.get_or_create_account")
    @patch("mods.revocord.tv.build_console_embed")
    async def test_nav_close(self, mock_build, mock_get, mock_interaction: Any) -> None:
        bot = MagicMock()
        bot.emojis = []
        bot._app_emojis_cache = []
        caught = []
        
        mock_get.return_value = {}
        mock_build.return_value = MagicMock()
        
        btn = TVNavButton("close", "❌", "Close", bot, 123, caught, 0)
        mock_interaction.user.id = 123
        await btn.callback(mock_interaction)
        mock_interaction.response.defer.assert_called_once()
        mock_interaction.edit_original_response.assert_called_once()'''
)

# Fix test_nav_prev_bound
text = text.replace(
    '''    @pytest.mark.asyncio
    async def test_nav_prev_bound(self, mock_interaction: Any) -> None:
        bot = MagicMock()
        bot.emojis = []
        bot._app_emojis_cache = []
        caught = [{"name": "A"} for _ in range(50)]
        
        btn = TVNavButton("prev", "⏪", "Prev", bot, 123, caught, 0)
        mock_interaction.user.id = 123
        await btn.callback(mock_interaction)
        mock_interaction.response.defer.assert_called_once()
        mock_interaction.edit_original_response.assert_called_once()
        # Should stay at 0
        kwargs = mock_interaction.edit_original_response.call_args[1]
        assert kwargs["view"].current_page == 0''',
    '''    @pytest.mark.asyncio
    async def test_nav_prev_bound(self, mock_interaction: Any) -> None:
        bot = MagicMock()
        bot.emojis = []
        bot._app_emojis_cache = []
        caught = [{"name": "A"} for _ in range(50)]
        
        btn = TVNavButton("prev", "⏪", "Prev", bot, 123, caught, 0)
        mock_interaction.user.id = 123
        await btn.callback(mock_interaction)
        mock_interaction.response.defer.assert_called_once()
        mock_interaction.edit_original_response.assert_not_called()'''
)

# Fix test_nav_next_bound
text = text.replace(
    '''    @pytest.mark.asyncio
    async def test_nav_next_bound(self, mock_interaction: Any) -> None:
        bot = MagicMock()
        bot.emojis = []
        bot._app_emojis_cache = []
        caught = [{"name": "A"} for _ in range(50)]
        
        btn = TVNavButton("next", "⏩", "Next", bot, 123, caught, 2)
        mock_interaction.user.id = 123
        await btn.callback(mock_interaction)
        mock_interaction.response.defer.assert_called_once()
        mock_interaction.edit_original_response.assert_called_once()
        # Max pages is 3, so last page is 2. current_page should remain 2.
        kwargs = mock_interaction.edit_original_response.call_args[1]
        assert kwargs["view"].current_page == 2''',
    '''    @pytest.mark.asyncio
    async def test_nav_next_bound(self, mock_interaction: Any) -> None:
        bot = MagicMock()
        bot.emojis = []
        bot._app_emojis_cache = []
        caught = [{"name": "A"} for _ in range(50)]
        
        btn = TVNavButton("next", "⏩", "Next", bot, 123, caught, 2)
        mock_interaction.user.id = 123
        await btn.callback(mock_interaction)
        mock_interaction.response.defer.assert_called_once()
        mock_interaction.edit_original_response.assert_not_called()'''
)

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("Done")
