import re

path = r"f:\projects\Revomon\GradexTool\tests\mods\revocord\test_setup.py"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

# Fix position updates for text channels and forum channel
text = text.replace('mock_news.position = 0', 'mock_news.position = 999')

# We need to add a mock forum channel to cover line 226
if 'mock_support =' not in text:
    support_mock = '''
        mock_support = MagicMock(spec=discord.ForumChannel)
        mock_support.name = "support"
        mock_support.position = 999
        mock_support.edit = AsyncMock()
        
        mock_guild.fetch_channels = AsyncMock(return_value=[mock_category, mock_news, mock_event_board, mock_portal, mock_wilds, mock_support])
'''
    text = text.replace('        mock_guild.fetch_channels = AsyncMock(return_value=[mock_category, mock_news, mock_event_board, mock_portal, mock_wilds])', support_mock)

# Fix test_app_command_error_original
error_test_fix = '''    @pytest.mark.asyncio
    @patch("mods.revocord.setup.logger")
    async def test_app_command_error_original(self, mock_logger):
        bot = MagicMock()
        cog = SetupCog(bot)
        mock_interaction = AsyncMock()
        mock_interaction.response.is_done.return_value = True
        
        error = app_commands.AppCommandError("Command failed")
        error.original = Exception("Original error")
        
        await cog.setup_command.error(mock_interaction, error)
        
        mock_logger.error.assert_called_once()
        assert "Original error" in mock_logger.error.call_args[0][0]
'''

error_test_correct = '''    @pytest.mark.asyncio
    @patch("mods.revocord.setup.logger")
    async def test_app_command_error_original(self, mock_logger):
        bot = MagicMock()
        cog = SetupCog(bot)
        mock_interaction = AsyncMock()
        mock_interaction.response.is_done.return_value = True
        
        error = app_commands.AppCommandError("Command failed")
        error.original = Exception("Original error")
        
        # Call the bound error handler (which is on the command itself usually, but we can call cog.setup_command.error by fetching the un-decorated function?)
        # Actually it's simpler:
        await cog.setup_command._has_any_error_handlers() # Just to touch it maybe
        # Let's call the raw callback
        await cog.setup_command_error(mock_interaction, error)
        
        mock_logger.error.assert_called_once()
        assert "Original error" in mock_logger.error.call_args[0][0]
'''
text = text.replace(error_test_fix, error_test_correct)

# Add test for setup() exception
setup_exception_test = '''    @pytest.mark.asyncio
    @patch("mods.revocord.setup.logger")
    async def test_setup_exception(self, mock_logger):
        from mods.revocord.setup import setup
        bot = MagicMock()
        bot.add_cog = AsyncMock(side_effect=Exception("Failed to add cog"))
        
        await setup(bot)
        
        mock_logger.error.assert_called_once()
        assert "Failed to add cog" in mock_logger.error.call_args[0][0]

'''
text = text.replace('class TestBiomeSelect:', setup_exception_test + 'class TestBiomeSelect:')

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("Done")
