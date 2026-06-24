import re

path = r"f:\projects\Revomon\GradexTool\tests\mods\revocord\test_setup.py"
with open(path, encoding="utf-8") as f:
    text = f.read()

# I will use regex to find and replace the problematic tests entirely

text = re.sub(
    r'    @pytest\.mark\.asyncio\n    @patch\("mods\.revocord\.setup\.logger"\)\n    async def test_app_command_error_original.*?assert "Original error" in mock_logger\.error\.call_args\[0\]\[0\]',
    '''    @pytest.mark.asyncio
    @patch("mods.revocord.setup.logger")
    async def test_app_command_error_original(self, mock_logger):
        bot = MagicMock()
        cog = SetupCog(bot)
        mock_interaction = AsyncMock()
        mock_interaction.response.is_done.return_value = True

        error = app_commands.AppCommandError("Command failed")
        error.original = Exception("Original error")

        await cog.setup_command.on_error(cog, mock_interaction, error)

        mock_logger.error.assert_called_once()
        assert "Original error" in str(mock_logger.error.call_args[1].get('exc_info') or mock_logger.error.call_args[0][1] if len(mock_logger.error.call_args[0]) > 1 else mock_logger.error.call_args[0][0])''',
    text,
    flags=re.DOTALL
)

text = re.sub(
    r'    @pytest\.mark\.asyncio\n    @patch\("mods\.revocord\.setup\.logger"\)\n    async def test_setup_exception.*?assert "Failed to add cog" in mock_logger\.error\.call_args\[0\]\[0\]',
    '''    @pytest.mark.asyncio
    @patch("mods.revocord.setup.logger")
    async def test_setup_exception(self, mock_logger):
        from mods.revocord.setup import setup
        bot = MagicMock()
        bot.add_cog = AsyncMock(side_effect=Exception("Failed to add cog"))

        await setup(bot)

        mock_logger.error.assert_called_once()
        assert "Failed to add cog" in str(mock_logger.error.call_args[0][1])''',
    text,
    flags=re.DOTALL
)

text = text.replace(
    'mock_category.channels = [mock_news, mock_event_board, mock_portal, mock_wilds]',
    'mock_category.channels = [mock_news, mock_event_board, mock_portal, mock_wilds, mock_support]'
)

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("Done")
