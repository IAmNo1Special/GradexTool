from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mods.revomon.pvp_command import PvpLeaderboard2, setup


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


class TestPvpLeaderboard2:
    def test_get_current_pvp_data_empty(self, mock_bot: Any) -> None:
        cog = PvpLeaderboard2(mock_bot)
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": {"pvpTopFifteen": []}}
        with patch("requests.get", return_value=mock_response):
            cog.get_current_pvp_data()
            assert cog.rankings is None

    def test_get_current_pvp_data_success(self, mock_bot: Any) -> None:
        cog = PvpLeaderboard2(mock_bot)
        mock_response = MagicMock()
        # Mock 1 valid entry, then 1 empty dict to trigger break
        mock_response.json.return_value = {
            "data": {
                "pvpTopFifteen": [
                    {
                        "username": "u1",
                        "profilePicture": "p1",
                        "amount": 100,
                        "elo": 1500,
                        "rank": 1,
                        "loseCount": 10,
                        "winCount": 20,
                    },
                    {},
                ]
            }
        }
        with patch("requests.get", return_value=mock_response):
            cog.get_current_pvp_data()
            assert cog.rankings is not None
            assert len(cog.rankings) == 1
            assert cog.rankings[0]["Name"] == "u1"
            assert cog.rankings[0]["Winning"] == "66.67%"

    @patch("mods.revomon.pvp_command.ImageFont.truetype")
    @patch("mods.revomon.pvp_command.Image.new")
    @patch("mods.revomon.pvp_command.ImageDraw.Draw")
    def test_update_pvp_image_no_data(
        self, mock_draw: Any, mock_new: Any, mock_truetype: Any, mock_bot: Any
    ) -> None:
        cog = PvpLeaderboard2(mock_bot)
        mock_image = MagicMock()
        mock_new.return_value = mock_image
        mock_draw_instance = MagicMock()
        mock_draw_instance.textbbox.return_value = (0, 0, 100, 20)
        mock_draw.return_value = mock_draw_instance

        cog.update_pvp_image(None)
        assert "image_bytes" in cog.pvp_img
        mock_image.save.assert_called_once()

    @patch("mods.revomon.pvp_command.ImageFont.truetype")
    @patch("mods.revomon.pvp_command.Image.new")
    @patch("mods.revomon.pvp_command.ImageDraw.Draw")
    def test_update_pvp_image_with_data(
        self, mock_draw: Any, mock_new: Any, mock_truetype: Any, mock_bot: Any
    ) -> None:
        cog = PvpLeaderboard2(mock_bot)
        mock_image = MagicMock()
        mock_new.return_value = mock_image
        mock_draw_instance = MagicMock()
        mock_draw.return_value = mock_draw_instance

        data = [
            {
                "Rank": 1,
                "Name": "u1",
                "Elo": 1500,
                "Wins": 20,
                "Losses": 10,
                "Winning": "66.67%",
                "Reward": "100 REVO",
            },
            {
                "Rank": 2,
                "Name": "u2",
                "Elo": 1400,
                "Wins": 10,
                "Losses": 20,
                "Winning": "33.33%",
                "Reward": "50 REVO",
            },
            {
                "Rank": 3,
                "Name": "u3",
                "Elo": 1300,
                "Wins": 5,
                "Losses": 25,
                "Winning": "16.67%",
                "Reward": "25 REVO",
            },
            {
                "Rank": 4,
                "Name": "u4",
                "Elo": 1200,
                "Wins": 0,
                "Losses": 30,
                "Winning": "0.00%",
                "Reward": "0 REVO",
            },
        ]
        cog.update_pvp_image(data)  # type: ignore
        assert "image_bytes" in cog.pvp_img
        mock_image.save.assert_called_once()

    @patch(
        "mods.revomon.pvp_command.ImageFont.truetype",
        side_effect=Exception("Font Exception"),
    )
    @patch("mods.revomon.pvp_command.ImageFont.load_default")
    @patch("mods.revomon.pvp_command.Image.new")
    @patch("mods.revomon.pvp_command.ImageDraw.Draw")
    def test_update_pvp_image_font_exception(
        self,
        mock_draw: Any,
        mock_new: Any,
        mock_load_default: Any,
        mock_truetype: Any,
        mock_bot: Any,
    ) -> None:
        cog = PvpLeaderboard2(mock_bot)
        mock_image = MagicMock()
        mock_new.return_value = mock_image
        mock_draw_instance = MagicMock()
        mock_draw.return_value = mock_draw_instance

        cog.update_pvp_image([])
        mock_load_default.assert_called_once()

    @patch("mods.revomon.pvp_command.ImageFont.truetype")
    @patch("mods.revomon.pvp_command.Image.new")
    @patch("mods.revomon.pvp_command.ImageDraw.Draw")
    def test_update_pvp_image_save_exception(
        self, mock_draw: Any, mock_new: Any, mock_truetype: Any, mock_bot: Any
    ) -> None:
        cog = PvpLeaderboard2(mock_bot)
        mock_image = MagicMock()
        mock_image.save.side_effect = Exception("Save Exception")
        mock_new.return_value = mock_image
        mock_draw_instance = MagicMock()
        mock_draw.return_value = mock_draw_instance

        cog.update_pvp_image([])
        # Exception is caught and printed

    def test_current_pvp_embed(self, mock_bot: Any) -> None:
        cog = PvpLeaderboard2(mock_bot)
        embed = cog.current_pvp_embed()
        assert embed.footer.text == "Global Revomon Association"

    @pytest.mark.asyncio
    async def test_on_ready(self, mock_bot: Any) -> None:
        cog = PvpLeaderboard2(mock_bot)
        await cog.on_ready()

    @pytest.mark.asyncio
    async def test_pvp_command_success(
        self, mock_bot: Any, mock_interaction: Any
    ) -> None:
        cog = PvpLeaderboard2(mock_bot)
        mock_bytes = MagicMock()
        cog.pvp_img = {"image_bytes": mock_bytes}

        with (
            patch.object(cog, "get_current_pvp_data"),
            patch.object(cog, "update_pvp_image"),
            patch.object(cog, "current_pvp_embed", return_value=MagicMock()),
            patch("mods.revomon.pvp_command.File"),
        ):
            await cog.pvp.callback(cog, mock_interaction)  # type: ignore
            mock_interaction.response.defer.assert_called_once_with(
                thinking=True, ephemeral=True
            )
            mock_interaction.followup.send.assert_called_once()
            mock_bytes.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_pvp_command_exceptions(
        self, mock_bot: Any, mock_interaction: Any
    ) -> None:
        cog = PvpLeaderboard2(mock_bot)
        mock_bytes = MagicMock()
        cog.pvp_img = {"image_bytes": mock_bytes}

        with (
            patch.object(
                cog, "get_current_pvp_data", side_effect=Exception("Get Data Error")
            ),
            patch.object(
                cog, "update_pvp_image", side_effect=Exception("Update Image Error")
            ),
            patch.object(
                cog, "current_pvp_embed", side_effect=Exception("Embed Error")
            ),
            patch("mods.revomon.pvp_command.File"),
        ):
            with pytest.raises(UnboundLocalError):
                await cog.pvp.callback(cog, mock_interaction)  # type: ignore
