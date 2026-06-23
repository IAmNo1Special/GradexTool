import re

path = r"f:\projects\Revomon\GradexTool\tests\mods\revocord\test_setup.py"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

# test_setup_full_creation
text = text.replace(
    '        assert mock_guild.create_text_channel.call_count == 2',
    '        assert mock_guild.create_text_channel.call_count == 5'
)

# test_setup_existing_sync
text = text.replace(
    '        mock_portal.edit = AsyncMock()',
    '        mock_portal.edit = AsyncMock()\n        \n        mock_news = MagicMock(spec=discord.TextChannel)\n        mock_news.name = "news"\n        mock_news.position = 0\n        mock_news.edit = AsyncMock()\n        \n        mock_event_board = MagicMock(spec=discord.TextChannel)\n        mock_event_board.name = "event-board"\n        mock_event_board.position = 1\n        mock_event_board.edit = AsyncMock()\n        \n        mock_wilds = MagicMock(spec=discord.TextChannel)\n        mock_wilds.name = "wilds"\n        mock_wilds.position = 3\n        mock_wilds.edit = AsyncMock()\n'
)

text = text.replace(
    'mock_category.channels = [mock_portal, mock_dashboard, mock_forum]',
    'mock_category.channels = [mock_portal, mock_dashboard, mock_forum, mock_news, mock_event_board, mock_wilds]'
)

text = text.replace(
    'mock_guild.channels = [mock_category, mock_portal, mock_dashboard, mock_forum]',
    'mock_guild.channels = [mock_category, mock_portal, mock_dashboard, mock_forum, mock_news, mock_event_board, mock_wilds]'
)

# test_setup_fetch_fallback
text = text.replace(
    '        mock_guild.fetch_channels = AsyncMock(return_value=[mock_category, mock_portal, mock_forum, mock_dashboard])',
    '        mock_guild.fetch_channels = AsyncMock(return_value=[mock_category, mock_portal, mock_forum, mock_dashboard, mock_news, mock_event_board, mock_wilds])'
)

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("Done")
