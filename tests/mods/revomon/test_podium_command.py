from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mods.revomon.podium_command import Podium2, setup


@pytest.fixture
def mock_bot() -> Any:
    bot = MagicMock()
    bot.add_cog = AsyncMock()
    return bot

@pytest.fixture
def mock_interaction() -> Any:
    interaction = AsyncMock()
    interaction.response.defer = AsyncMock()
    interaction.followup.send = AsyncMock()
    return interaction

@pytest.mark.asyncio
async def test_setup(mock_bot: Any) -> None:
    await setup(mock_bot)
    mock_bot.add_cog.assert_called_once()

class TestPodium2:
    def test_convert_time(self, mock_bot: Any) -> None:
        cog = Podium2(mock_bot)
        assert cog.convert_time(3661) == "01:01:01"

    def test_get_weekly_podium_data(self, mock_bot: Any) -> None:
        cog = Podium2(mock_bot)
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
            assert res["first"]["time"] == "01:00:00"

    def test_get_current_podium_data(self, mock_bot: Any) -> None:
        cog = Podium2(mock_bot)
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
            assert res["second"]["user"] == "u2"
            assert res["third"]["user"] == "u3"

    @patch('mods.revomon.podium_command.ImageFont.truetype')
    @patch('mods.revomon.podium_command.Image.new')
    @patch('mods.revomon.podium_command.ImageDraw.Draw')
    def test_podium_img_weekly(self, mock_draw: Any, mock_new: Any, mock_truetype: Any, mock_bot: Any) -> None:
        cog = Podium2(mock_bot)
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

    @patch('mods.revomon.podium_command.ImageFont.truetype')
    @patch('mods.revomon.podium_command.Image.new')
    @patch('mods.revomon.podium_command.ImageDraw.Draw')
    def test_podium_img_current(self, mock_draw: Any, mock_new: Any, mock_truetype: Any, mock_bot: Any) -> None:
        cog = Podium2(mock_bot)
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
        cog = Podium2(mock_bot)
        with patch.object(cog, 'podium_img'):
            embed = cog.current_podium_embed()
            assert embed.footer.text == "Global Revomon Association"

    def test_weekly_podium_embed(self, mock_bot: Any) -> None:
        cog = Podium2(mock_bot)
        with patch.object(cog, 'podium_img'):
            embed = cog.weekly_podium_embed()
            assert embed.footer.text == "Global Revomon Association"

    @pytest.mark.asyncio
    async def test_on_ready(self, mock_bot: Any) -> None:
        cog = Podium2(mock_bot)
        await cog.on_ready()

    @pytest.mark.asyncio
    async def test_podium_command(self, mock_bot: Any, mock_interaction: Any) -> None:
        cog = Podium2(mock_bot)
        mock_current_bytes = MagicMock()
        mock_weekly_bytes = MagicMock()
        cog.current_podium_img = {"image_bytes": mock_current_bytes}
        cog.weekly_podium_img = {"image_bytes": mock_weekly_bytes}

        with patch.object(cog, 'current_podium_embed', return_value=MagicMock()), \
             patch.object(cog, 'weekly_podium_embed', return_value=MagicMock()), \
             patch('mods.revomon.podium_command.File'):

            await cog.podium.callback(cog, mock_interaction) # type: ignore
            mock_interaction.response.defer.assert_called_once_with(thinking=True, ephemeral=True)
            assert mock_interaction.followup.send.call_count == 2
            mock_current_bytes.close.assert_called_once()
            mock_weekly_bytes.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_podium_command_exception(self, mock_bot: Any, mock_interaction: Any) -> None:
        cog = Podium2(mock_bot)
        with patch.object(cog, 'current_podium_embed', side_effect=Exception("Test Exception")):
            await cog.podium.callback(cog, mock_interaction) # type: ignore
        # Exception is caught and printed
