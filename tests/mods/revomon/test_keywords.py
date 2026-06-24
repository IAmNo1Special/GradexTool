from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import discord
import pytest

from mods.revomon.podium_keyword import Podium
from mods.revomon.podium_keyword import setup as podium_setup
from mods.revomon.pvp_keyword import PvpLeaderboard
from mods.revomon.pvp_keyword import setup as pvp_setup


@pytest.fixture
def mock_bot() -> Any:
    bot = MagicMock()
    bot.add_cog = AsyncMock()
    bot.get_channel = AsyncMock()
    return bot

@pytest.fixture
def mock_message() -> Any:
    message = MagicMock()
    message.author.bot = False
    message.content = ""
    return message

# --- Podium Keyword Tests ---

@pytest.mark.asyncio
async def test_podium_setup(mock_bot: Any) -> None:
    await podium_setup(mock_bot)
    mock_bot.add_cog.assert_called_once()

class TestPodiumKeyword:
    def test_convert_time(self, mock_bot: Any) -> None:
        cog = Podium(mock_bot)
        assert cog.convert_time(3661) == "01:01:01"

    def test_get_weekly_podium_data(self, mock_bot: Any) -> None:
        cog = Podium(mock_bot)
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {
                "weeklyPodium": [
                    {"username": "u1", "profilePicture": "p1", "times": 3600},
                    {"username": "u2", "profilePicture": "p2", "times": 3601},
                    {"username": "u3", "profilePicture": "p3", "times": 3602},
                ]
            }
        }
        with patch('requests.get', return_value=mock_response):
            res = cog.get_weekly_podium_data()
            assert res["first"]["user"] == "u1"
            assert res["second"]["user"] == "u2"
            assert res["third"]["user"] == "u3"

    def test_get_current_podium_data(self, mock_bot: Any) -> None:
        cog = Podium(mock_bot)
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {
                "currentPodium": [
                    {"username": "u1", "profilePicture": "p1"},
                    {"username": "u2", "profilePicture": "p2"},
                    {"username": "u3", "profilePicture": "p3"},
                ]
            }
        }
        with patch('requests.get', return_value=mock_response):
            res = cog.get_current_podium_data()
            assert res["first"]["user"] == "u1"

    @patch('mods.revomon.podium_keyword.ImageFont.truetype')
    @patch('mods.revomon.podium_keyword.Image.new')
    @patch('mods.revomon.podium_keyword.ImageDraw.Draw')
    def test_podium_img_weekly(self, mock_draw: Any, mock_new: Any, mock_truetype: Any, mock_bot: Any) -> None:
        cog = Podium(mock_bot)
        mock_image = MagicMock()
        mock_new.return_value = mock_image
        mock_draw_instance = MagicMock()
        mock_draw_instance.textbbox.return_value = (0, 0, 100, 20)
        mock_draw.return_value = mock_draw_instance

        with patch.object(cog, 'get_weekly_podium_data', return_value={
            "first": {"user": "u1", "time": "01:00:00"},
            "second": {"user": "u2", "time": "01:00:01"},
            "third": {"user": "u3", "time": "01:00:02"},
        }):
            cog.podium_img("weekly")
            assert "image_bytes" in cog.weekly_podium_img
            mock_image.save.assert_called_once()

    @patch('mods.revomon.podium_keyword.ImageFont.truetype')
    @patch('mods.revomon.podium_keyword.Image.new')
    @patch('mods.revomon.podium_keyword.ImageDraw.Draw')
    def test_podium_img_current(self, mock_draw: Any, mock_new: Any, mock_truetype: Any, mock_bot: Any) -> None:
        cog = Podium(mock_bot)
        mock_image = MagicMock()
        mock_new.return_value = mock_image
        mock_draw_instance = MagicMock()
        mock_draw_instance.textbbox.return_value = (0, 0, 100, 20)
        mock_draw.return_value = mock_draw_instance

        with patch.object(cog, 'get_current_podium_data', return_value={
            "first": {"user": "u1"},
            "second": {"user": "u2"},
            "third": {"user": "u3"},
        }):
            cog.podium_img("current")
            assert "image_bytes" in cog.current_podium_img
            mock_image.save.assert_called_once()

    def test_current_podium_embed(self, mock_bot: Any) -> None:
        cog = Podium(mock_bot)
        with patch.object(cog, 'podium_img'):
            embed = cog.current_podium_embed()
            assert embed.footer.text == "Global Revomon Association"

    def test_weekly_podium_embed(self, mock_bot: Any) -> None:
        cog = Podium(mock_bot)
        with patch.object(cog, 'podium_img'):
            embed = cog.weekly_podium_embed()
            assert embed.footer.text == "Global Revomon Association"

    @pytest.mark.asyncio
    async def test_update_rankings_success(self, mock_bot: Any) -> None:
        cog = Podium(mock_bot)
        mock_channel = MagicMock(spec=discord.TextChannel)
        mock_msg1 = AsyncMock()
        mock_msg2 = AsyncMock()
        mock_history = AsyncMock()
        mock_history.__aiter__.return_value = [mock_msg1, mock_msg2]
        mock_channel.history.return_value = mock_history

        mock_current_msg = MagicMock()
        mock_current_msg.edit = AsyncMock()
        mock_weekly_msg = MagicMock()
        mock_weekly_msg.edit = AsyncMock()
        mock_channel.send = AsyncMock(side_effect=[mock_current_msg, mock_weekly_msg])

        mock_bot.fetch_channel = AsyncMock(return_value=mock_channel)

        cog.current_podium_img = {"image_bytes": MagicMock()}
        cog.weekly_podium_img = {"image_bytes": MagicMock()}

        with patch.object(cog, 'podium_img'), \
             patch.object(cog, 'current_podium_embed', return_value=MagicMock()), \
             patch.object(cog, 'weekly_podium_embed', return_value=MagicMock()), \
             patch('mods.revomon.podium_keyword.discord.File'), \
             patch('asyncio.sleep', side_effect=Exception("Break Loop")):

            await cog.update_rankings()

            mock_channel.history.assert_called_once_with(limit=2)
            mock_msg1.delete.assert_called_once()
            mock_msg2.delete.assert_called_once()
            mock_current_msg.edit.assert_called_once()
            mock_weekly_msg.edit.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_rankings_exception(self, mock_bot: Any) -> None:
        cog = Podium(mock_bot)
        mock_bot.get_channel.side_effect = Exception("Channel Error")
        await cog.update_rankings()
        # Exception is caught and printed

    @pytest.mark.asyncio
    async def test_on_ready(self, mock_bot: Any) -> None:
        cog = Podium(mock_bot)
        with patch.object(cog, 'update_rankings', new_callable=AsyncMock) as mock_update:
            await cog.on_ready()
            mock_update.assert_called_once()

    @pytest.mark.asyncio
    async def test_on_message_bot(self, mock_bot: Any, mock_message: Any) -> None:
        cog = Podium(mock_bot)
        mock_message.author.bot = True
        await cog.on_message(mock_message)
        # Does nothing

    @pytest.mark.asyncio
    async def test_on_message_podium(self, mock_bot: Any, mock_message: Any) -> None:
        cog = Podium(mock_bot)
        mock_message.content = " podium "

        with patch.object(cog, 'current_podium_embed', return_value=MagicMock()), \
             patch.object(cog, 'weekly_podium_embed', return_value=MagicMock()), \
             patch('mods.revomon.podium_keyword.respond', new_callable=AsyncMock) as mock_respond:

            await cog.on_message(mock_message)
            assert mock_respond.call_count == 2

    @pytest.mark.asyncio
    async def test_on_message_exception(self, mock_bot: Any, mock_message: Any) -> None:
        cog = Podium(mock_bot)
        mock_message.content = "podium"

        with patch.object(cog, 'current_podium_embed', side_effect=Exception("Embed Error")):
            await cog.on_message(mock_message)


# --- PvpLeaderboard Keyword Tests ---

@pytest.mark.asyncio
async def test_pvp_setup(mock_bot: Any) -> None:
    await pvp_setup(mock_bot)
    mock_bot.add_cog.assert_called_once()

class TestPvpKeyword:
    def test_get_current_pvp_data_empty(self, mock_bot: Any) -> None:
        cog = PvpLeaderboard(mock_bot)
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": {"pvpTopFifteen": []}}
        with patch('requests.get', return_value=mock_response):
            cog.get_current_pvp_data()
            assert cog.rankings is None

    def test_get_current_pvp_data_success(self, mock_bot: Any) -> None:
        cog = PvpLeaderboard(mock_bot)
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": {"pvpTopFifteen": [
            {
                "username": "u1", "profilePicture": "p1", "amount": 100,
                "elo": 1500, "rank": 1, "loseCount": 10, "winCount": 20
            },
            {}
        ]}}
        with patch('requests.get', return_value=mock_response):
            cog.get_current_pvp_data()
            assert cog.rankings is not None
            assert len(cog.rankings) == 1
            assert cog.rankings[0]["Name"] == "u1"
            assert cog.rankings[0]["Winning"] == "66.67%"

    @patch('mods.revomon.pvp_keyword.ImageFont.truetype')
    @patch('mods.revomon.pvp_keyword.Image.new')
    @patch('mods.revomon.pvp_keyword.ImageDraw.Draw')
    def test_update_pvp_image_no_data(self, mock_draw: Any, mock_new: Any, mock_truetype: Any, mock_bot: Any) -> None:
        cog = PvpLeaderboard(mock_bot)
        mock_image = MagicMock()
        mock_new.return_value = mock_image
        mock_draw_instance = MagicMock()
        mock_draw_instance.textbbox.return_value = (0, 0, 100, 20)
        mock_draw.return_value = mock_draw_instance

        cog.update_pvp_image(None)
        assert "image_bytes" in cog.pvp_img
        mock_image.save.assert_called_once()

    @patch('mods.revomon.pvp_keyword.ImageFont.truetype')
    @patch('mods.revomon.pvp_keyword.Image.new')
    @patch('mods.revomon.pvp_keyword.ImageDraw.Draw')
    def test_update_pvp_image_with_data(self, mock_draw: Any, mock_new: Any, mock_truetype: Any, mock_bot: Any) -> None:
        cog = PvpLeaderboard(mock_bot)
        mock_image = MagicMock()
        mock_new.return_value = mock_image
        mock_draw_instance = MagicMock()
        mock_draw.return_value = mock_draw_instance

        data = [
            {"Rank": 1, "Name": "u1", "Elo": 1500, "Wins": 20, "Losses": 10, "Winning": "66.67%", "Reward": "100 REVO"},
            {"Rank": 2, "Name": "u2", "Elo": 1400, "Wins": 10, "Losses": 20, "Winning": "33.33%", "Reward": "50 REVO"},
            {"Rank": 3, "Name": "u3", "Elo": 1300, "Wins": 5, "Losses": 25, "Winning": "16.67%", "Reward": "25 REVO"},
            {"Rank": 4, "Name": "u4", "Elo": 1200, "Wins": 0, "Losses": 30, "Winning": "0.00%", "Reward": "0 REVO"},
        ]
        cog.update_pvp_image(data)  # type: ignore[arg-type]
        assert "image_bytes" in cog.pvp_img
        mock_image.save.assert_called_once()

    @patch('mods.revomon.pvp_keyword.ImageFont.truetype', side_effect=Exception("Font Exception"))
    @patch('mods.revomon.pvp_keyword.ImageFont.load_default')
    @patch('mods.revomon.pvp_keyword.Image.new')
    @patch('mods.revomon.pvp_keyword.ImageDraw.Draw')
    def test_update_pvp_image_font_exception(self, mock_draw: Any, mock_new: Any, mock_load_default: Any, mock_truetype: Any, mock_bot: Any) -> None:
        cog = PvpLeaderboard(mock_bot)
        mock_image = MagicMock()
        mock_new.return_value = mock_image
        mock_draw_instance = MagicMock()
        mock_draw.return_value = mock_draw_instance

        cog.update_pvp_image([])
        mock_load_default.assert_called_once()

    @patch('mods.revomon.pvp_keyword.ImageFont.truetype')
    @patch('mods.revomon.pvp_keyword.Image.new')
    @patch('mods.revomon.pvp_keyword.ImageDraw.Draw')
    def test_update_pvp_image_save_exception(self, mock_draw: Any, mock_new: Any, mock_truetype: Any, mock_bot: Any) -> None:
        cog = PvpLeaderboard(mock_bot)
        mock_image = MagicMock()
        mock_image.save.side_effect = Exception("Save Exception")
        mock_new.return_value = mock_image
        mock_draw_instance = MagicMock()
        mock_draw.return_value = mock_draw_instance

        cog.update_pvp_image([])

    def test_current_pvp_embed(self, mock_bot: Any) -> None:
        cog = PvpLeaderboard(mock_bot)
        embed = cog.current_pvp_embed()
        assert embed.footer.text == "Global Revomon Association"

    @pytest.mark.asyncio
    async def test_update_rankings_success(self, mock_bot: Any) -> None:
        cog = PvpLeaderboard(mock_bot)
        mock_channel = MagicMock()
        mock_msg1 = AsyncMock()
        mock_msg2 = AsyncMock()
        mock_history = AsyncMock()
        mock_history.__aiter__.return_value = [mock_msg1, mock_msg2]
        mock_channel.history.return_value = mock_history

        mock_current_msg = MagicMock()
        mock_current_msg.edit = AsyncMock()
        mock_channel.send = AsyncMock(return_value=mock_current_msg)

        mock_bot.get_channel = MagicMock(return_value=mock_channel)

        cog.pvp_img = {"image_bytes": MagicMock()}

        with patch.object(cog, 'get_current_pvp_data'), \
             patch.object(cog, 'update_pvp_image'), \
             patch.object(cog, 'current_pvp_embed', return_value=MagicMock()), \
             patch('mods.revomon.pvp_keyword.discord.File'), \
             patch('asyncio.sleep', side_effect=Exception("Break Loop")):

            await cog.update_rankings()

            mock_channel.history.assert_called_once_with(limit=2)
            mock_msg1.delete.assert_called_once()
            mock_msg2.delete.assert_called_once()
            mock_current_msg.edit.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_rankings_inner_exceptions(self, mock_bot: Any) -> None:
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

        with patch.object(cog, 'get_current_pvp_data', side_effect=Exception("Data Error")), \
             patch.object(cog, 'update_pvp_image', side_effect=Exception("Image Error")), \
             patch('asyncio.sleep', new_callable=AsyncMock, side_effect=Exception("Break Loop")):

            await cog.update_rankings()

    @pytest.mark.asyncio
    async def test_update_rankings_no_history(self, mock_bot: Any) -> None:
        cog = PvpLeaderboard(mock_bot)
        mock_channel = MagicMock()
        del mock_channel.history  # So hasattr returns False
        mock_bot.get_channel = MagicMock(return_value=mock_channel)

        await cog.update_rankings()
        mock_bot.get_channel.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_rankings_outer_exception(self, mock_bot: Any) -> None:
        cog = PvpLeaderboard(mock_bot)
        mock_bot.get_channel = MagicMock(side_effect=Exception("Channel Error"))
        await cog.update_rankings()

    @pytest.mark.asyncio
    async def test_on_ready(self, mock_bot: Any) -> None:
        cog = PvpLeaderboard(mock_bot)
        with patch.object(cog, 'update_rankings', new_callable=AsyncMock) as mock_update:
            await cog.on_ready()
            mock_update.assert_called_once()

    @pytest.mark.asyncio
    async def test_on_message_bot(self, mock_bot: Any, mock_message: Any) -> None:
        cog = PvpLeaderboard(mock_bot)
        mock_message.author.bot = True
        await cog.on_message(mock_message)

    @pytest.mark.asyncio
    async def test_on_message_pvp(self, mock_bot: Any, mock_message: Any) -> None:
        cog = PvpLeaderboard(mock_bot)
        mock_message.content = "pvp"

        with patch.object(cog, 'get_current_pvp_data'), \
             patch.object(cog, 'update_pvp_image'), \
             patch.object(cog, 'current_pvp_embed', return_value=MagicMock()), \
             patch('mods.revomon.pvp_keyword.respond', new_callable=AsyncMock) as mock_respond:

            await cog.on_message(mock_message)
            mock_respond.assert_called_once()

    @pytest.mark.asyncio
    async def test_on_message_exception(self, mock_bot: Any, mock_message: Any) -> None:
        cog = PvpLeaderboard(mock_bot)
        mock_message.content = "Pvp"

        with patch.object(cog, 'get_current_pvp_data', side_effect=Exception("Data Error")):
            await cog.on_message(mock_message)
