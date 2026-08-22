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

    @pytest.mark.asyncio
    @patch("mods.revomon.podium_command.fetch_json", new_callable=AsyncMock)
    async def test_get_weekly_podium_data(self, mock_fetch: Any, mock_bot: Any) -> None:
        cog = Podium2(mock_bot)
        mock_fetch.return_value = {
            "data": {
                "weeklyPodium": [
                    {"username": "u1", "profilePicture": "p1", "times": 3600},
                    {"username": "u2", "profilePicture": "p2", "times": 3601},
                    {"username": "u3", "profilePicture": "p3", "times": 3602},
                ]
            }
        }
        res = await cog.get_weekly_podium_data()
        assert res["first"]["user"] == "u1"
        assert res["second"]["user"] == "u2"
        assert res["third"]["user"] == "u3"
        assert res["first"]["time"] == "01:00:00"

    @pytest.mark.asyncio
    @patch("mods.revomon.podium_command.fetch_json", new_callable=AsyncMock)
    async def test_get_current_podium_data(
        self, mock_fetch: Any, mock_bot: Any
    ) -> None:
        cog = Podium2(mock_bot)
        mock_fetch.return_value = {
            "data": {
                "currentPodium": [
                    {"username": "u1", "profilePicture": "p1"},
                    {"username": "u2", "profilePicture": "p2"},
                    {"username": "u3", "profilePicture": "p3"},
                ]
            }
        }
        res = await cog.get_current_podium_data()
        assert res["first"]["user"] == "u1"
        assert res["second"]["user"] == "u2"
        assert res["third"]["user"] == "u3"

    @pytest.mark.asyncio
    @patch("mods.revomon.podium_command.ImageFont.truetype")
    @patch("mods.revomon.podium_command.Image.new")
    @patch("mods.revomon.podium_command.ImageDraw.Draw")
    async def test_podium_img_weekly(
        self, mock_draw: Any, mock_new: Any, mock_truetype: Any, mock_bot: Any
    ) -> None:
        cog = Podium2(mock_bot)
        mock_image = MagicMock()
        mock_new.return_value = mock_image
        mock_draw_instance = MagicMock()
        mock_draw_instance.textbbox.return_value = (0, 0, 100, 20)
        mock_draw.return_value = mock_draw_instance

        with patch.object(
            cog,
            "get_weekly_podium_data",
            new_callable=AsyncMock,
            return_value={
                "first": {"user": "u1", "time": "01:00:00"},
                "second": {"user": "u2", "time": "01:00:01"},
                "third": {"user": "u3", "time": "01:00:02"},
            },
        ):
            await cog.podium_img("weekly")
            assert "image_bytes" in cog.weekly_podium_img
            mock_image.save.assert_called_once()

    @pytest.mark.asyncio
    @patch("mods.revomon.podium_command.ImageFont.truetype")
    @patch("mods.revomon.podium_command.Image.new")
    @patch("mods.revomon.podium_command.ImageDraw.Draw")
    async def test_podium_img_current(
        self, mock_draw: Any, mock_new: Any, mock_truetype: Any, mock_bot: Any
    ) -> None:
        cog = Podium2(mock_bot)
        mock_image = MagicMock()
        mock_new.return_value = mock_image
        mock_draw_instance = MagicMock()
        mock_draw_instance.textbbox.return_value = (0, 0, 100, 20)
        mock_draw.return_value = mock_draw_instance

        with patch.object(
            cog,
            "get_current_podium_data",
            new_callable=AsyncMock,
            return_value={
                "first": {"user": "u1"},
                "second": {"user": "u2"},
                "third": {"user": "u3"},
            },
        ):
            await cog.podium_img("current")
            assert "image_bytes" in cog.current_podium_img
            mock_image.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_current_podium_embed(self, mock_bot: Any) -> None:
        cog = Podium2(mock_bot)
        with patch.object(cog, "podium_img", new_callable=AsyncMock):
            embed = await cog.current_podium_embed()
            assert embed.footer.text == "Global Revomon Association"

    @pytest.mark.asyncio
    async def test_weekly_podium_embed(self, mock_bot: Any) -> None:
        cog = Podium2(mock_bot)
        with patch.object(cog, "podium_img", new_callable=AsyncMock):
            embed = await cog.weekly_podium_embed()
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

        async def current_embed() -> Any:
            cog.current_podium_img["image_bytes"] = mock_current_bytes
            return MagicMock()

        async def weekly_embed() -> Any:
            cog.weekly_podium_img["image_bytes"] = mock_weekly_bytes
            return MagicMock()

        with (
            patch.object(
                cog,
                "current_podium_embed",
                new_callable=AsyncMock,
                side_effect=current_embed,
            ),
            patch.object(
                cog,
                "weekly_podium_embed",
                new_callable=AsyncMock,
                side_effect=weekly_embed,
            ),
            patch("mods.revomon.podium_command.File"),
        ):
            await cog.podium.callback(cog, mock_interaction)  # type: ignore[call-arg,arg-type]
            mock_interaction.response.defer.assert_called_once_with(
                thinking=True, ephemeral=True
            )
            assert mock_interaction.followup.send.call_count == 2
            mock_current_bytes.close.assert_called_once()
            mock_weekly_bytes.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_podium_command_exception(
        self, mock_bot: Any, mock_interaction: Any
    ) -> None:
        cog = Podium2(mock_bot)
        with patch.object(
            cog, "current_podium_embed", side_effect=Exception("Test Exception")
        ):
            await cog.podium.callback(cog, mock_interaction)  # type: ignore[call-arg,arg-type]
        # Exception is caught and printed
