from unittest.mock import AsyncMock, MagicMock, patch

import discord
import pytest

from mods.revocord.broadcaster import broadcast_encounter, update_encounter_broadcast


class TestBroadcaster:
    @pytest.mark.asyncio
    async def test_broadcast_encounter_not_notable(self):
        user = MagicMock(spec=discord.Member)
        embed = MagicMock(spec=discord.Embed)
        res = await broadcast_encounter(MagicMock(), user, "Pikachu", "25", "Common", False, embed)
        assert res == 0

    @pytest.mark.asyncio
    async def test_broadcast_encounter_no_event_board(self):
        user = MagicMock(spec=discord.Member)
        user.guild.channels = []
        embed = MagicMock(spec=discord.Embed)
        res = await broadcast_encounter(MagicMock(), user, "Pikachu", "25", "Legendary", False, embed)
        assert res == 0

    @pytest.mark.asyncio
    @patch("mods.revocord.broadcaster.EventBoardLogsTable")
    async def test_broadcast_encounter_success(self, mock_table_cls):
        user = MagicMock(spec=discord.Member)
        user.display_name = "Ash"

        event_board = MagicMock(spec=discord.TextChannel)
        event_board.name = "event-board"
        user.guild.channels = [event_board]

        msg = MagicMock()
        msg.id = 999
        event_board.send = AsyncMock(return_value=msg)

        embed = MagicMock(spec=discord.Embed)
        field = MagicMock()
        field.name = "Ability"
        field.value = "Static"
        field.inline = True
        embed.fields = [field]
        embed.footer.text = "RC-ID: #123"

        mock_table = MagicMock()
        mock_table_cls.return_value = mock_table

        mock_conn = AsyncMock()
        mock_cursor = AsyncMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_table._connect.return_value.__aenter__.return_value = mock_conn

        res = await broadcast_encounter(MagicMock(), user, "Pikachu", "25", "Common", True, embed)

        assert res == 999
        event_board.send.assert_called_once()
        mock_cursor.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_broadcast_encounter_exception(self):
        user = MagicMock(spec=discord.Member)
        event_board = MagicMock(spec=discord.TextChannel)
        event_board.name = "event-board"
        user.guild.channels = [event_board]

        event_board.send = AsyncMock(side_effect=Exception("API error"))

        embed = MagicMock(spec=discord.Embed)
        embed.fields = []
        embed.footer = None

        res = await broadcast_encounter(MagicMock(), user, "Pikachu", "25", "Rare", False, embed)
        assert res == 0

    @pytest.mark.asyncio
    async def test_update_encounter_no_msg_id(self):
        await update_encounter_broadcast(MagicMock(), 0, "Caught", 0)

    @pytest.mark.asyncio
    async def test_update_encounter_no_event_board(self):
        guild = MagicMock()
        guild.channels = []
        await update_encounter_broadcast(guild, 999, "Caught", 0)

    @pytest.mark.asyncio
    async def test_update_encounter_no_msg_found(self):
        guild = MagicMock()
        event_board = MagicMock(spec=discord.TextChannel)
        event_board.name = "event-board"
        guild.channels = [event_board]
        event_board.fetch_message = AsyncMock(return_value=None)

        await update_encounter_broadcast(guild, 999, "Caught", 0)

    @pytest.mark.asyncio
    @patch("mods.revocord.broadcaster.EventBoardLogsTable")
    async def test_update_encounter_success_caught(self, mock_table_cls):
        guild = MagicMock()
        event_board = MagicMock(spec=discord.TextChannel)
        event_board.name = "event-board"
        guild.channels = [event_board]

        msg = MagicMock()
        embed = MagicMock(spec=discord.Embed)
        embed.description = "Base text"
        msg.embeds = [embed]
        msg.edit = AsyncMock()

        event_board.fetch_message = AsyncMock(return_value=msg)

        mock_table = MagicMock()
        mock_table_cls.return_value = mock_table

        mock_conn = AsyncMock()
        mock_cursor = AsyncMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_table._connect.return_value.__aenter__.return_value = mock_conn

        await update_encounter_broadcast(guild, 999, "Caught", 12345)

        msg.edit.assert_called_once()
        assert "Captured successfully!" in embed.description
        assert embed.color == 12345
        mock_cursor.execute.assert_called_once()

    @pytest.mark.asyncio
    @patch("mods.revocord.broadcaster.EventBoardLogsTable")
    async def test_update_encounter_success_fled(self, mock_table_cls):
        guild = MagicMock()
        event_board = MagicMock(spec=discord.TextChannel)
        event_board.name = "event-board"
        guild.channels = [event_board]

        msg = MagicMock()
        embed = MagicMock(spec=discord.Embed)
        embed.description = "Base text"
        msg.embeds = [embed]
        msg.edit = AsyncMock()

        event_board.fetch_message = AsyncMock(return_value=msg)
        mock_table = MagicMock()
        mock_table_cls.return_value = mock_table
        mock_conn = AsyncMock()
        mock_cursor = AsyncMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_table._connect.return_value.__aenter__.return_value = mock_conn

        await update_encounter_broadcast(guild, 999, "Fled", 12345)

        assert "broke free and fled!" in embed.description

    @pytest.mark.asyncio
    @patch("mods.revocord.broadcaster.EventBoardLogsTable")
    async def test_update_encounter_success_ran(self, mock_table_cls):
        guild = MagicMock()
        event_board = MagicMock(spec=discord.TextChannel)
        event_board.name = "event-board"
        guild.channels = [event_board]

        msg = MagicMock()
        embed = MagicMock(spec=discord.Embed)
        embed.description = "Base text"
        msg.embeds = [embed]
        msg.edit = AsyncMock()

        event_board.fetch_message = AsyncMock(return_value=msg)
        mock_table = MagicMock()
        mock_table_cls.return_value = mock_table
        mock_conn = AsyncMock()
        mock_cursor = AsyncMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_table._connect.return_value.__aenter__.return_value = mock_conn

        await update_encounter_broadcast(guild, 999, "Ran", 12345)

        assert "trainer ran away!" in embed.description

    @pytest.mark.asyncio
    async def test_update_encounter_not_found(self):
        guild = MagicMock()
        event_board = MagicMock(spec=discord.TextChannel)
        event_board.name = "event-board"
        guild.channels = [event_board]

        event_board.fetch_message = AsyncMock(side_effect=discord.NotFound(MagicMock(), ""))

        # Should not raise
        await update_encounter_broadcast(guild, 999, "Caught", 0)

    @pytest.mark.asyncio
    async def test_update_encounter_exception(self):
        guild = MagicMock()
        event_board = MagicMock(spec=discord.TextChannel)
        event_board.name = "event-board"
        guild.channels = [event_board]

        event_board.fetch_message = AsyncMock(side_effect=Exception("API error"))

        # Should not raise
        await update_encounter_broadcast(guild, 999, "Caught", 0)
