
path = r"f:\projects\Revomon\GradexTool\tests\mods\revocord\test_setup.py"
with open(path, encoding="utf-8") as f:
    text = f.read()

# Add test for user not being Member
not_member_test = '''    @pytest.mark.asyncio
    @patch("discord.ext.commands.Bot")
    async def test_not_member(self, mock_bot):
        cog = SetupCog(mock_bot)
        mock_interaction = AsyncMock()

        # User is not a Member
        mock_interaction.user = discord.User(state=MagicMock(), data={'id': 1, 'username': 'test', 'discriminator': '0', 'avatar': None})

        await cog.setup_command.callback(cog, mock_interaction)

        mock_interaction.followup.send.assert_called_once()
        assert "server member" in mock_interaction.followup.send.call_args[0][0]

'''
text = text.replace('class TestSetupCogErrorHandling:', not_member_test + 'class TestSetupCogErrorHandling:')

# Fix test_setup_existing_sync to cover position updates
text = text.replace(
    '        mock_channel.position = 0',
    '        mock_channel.position = 999  # Force position update (line 194 / 226)'
)

# Add test for original error logging
original_error_test = '''    @pytest.mark.asyncio
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
text = text.replace('class TestBiomeSelect:', original_error_test + 'class TestBiomeSelect:')

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("Done")
