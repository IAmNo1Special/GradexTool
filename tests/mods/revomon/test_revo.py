from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mods.revomon.revo import PriceTracker, setup


@pytest.fixture
def mock_bot() -> Any:
    bot = MagicMock()
    bot.wait_until_ready = AsyncMock()
    bot.get_channel = MagicMock()
    bot.add_cog = AsyncMock()
    return bot

@pytest.mark.asyncio
async def test_setup(mock_bot: Any) -> None:
    await setup(mock_bot)
    mock_bot.add_cog.assert_called_once()

class TestPriceTracker:
    def test_init(self, mock_bot: Any) -> None:
        with patch('discord.ext.tasks.Loop.start'):
            tracker = PriceTracker(mock_bot)
            assert tracker.gradex == mock_bot
            assert tracker.price_channel_id == 1254142506178838558

    def test_get_revo_price_success(self, mock_bot: Any) -> None:
        with patch('discord.ext.tasks.Loop.start'):
            tracker = PriceTracker(mock_bot)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"market_data": {"current_price": {"usd": 1.23}}}
        with patch('requests.get', return_value=mock_response):
            assert tracker.get_revo_price() == 1.23

    def test_get_revo_price_fail(self, mock_bot: Any) -> None:
        with patch('discord.ext.tasks.Loop.start'):
            tracker = PriceTracker(mock_bot)
        mock_response = MagicMock()
        mock_response.status_code = 404
        with patch('requests.get', return_value=mock_response):
            assert tracker.get_revo_price() is None

    @pytest.mark.asyncio
    async def test_update_price_success(self, mock_bot: Any) -> None:
        with patch('discord.ext.tasks.Loop.start'):
            tracker = PriceTracker(mock_bot)
        tracker.get_revo_price = MagicMock(return_value=1.23)  # type: ignore[method-assign]
        mock_channel = AsyncMock()
        tracker.gradex.get_channel.return_value = mock_channel  # type: ignore[attr-defined]
        await tracker.update_price()
        tracker.gradex.get_channel.assert_called_with(1254142506178838558)  # type: ignore[attr-defined]
        mock_channel.edit.assert_called_with(name="Revo: $1.23000")

    @pytest.mark.asyncio
    async def test_update_price_no_price(self, mock_bot: Any) -> None:
        with patch('discord.ext.tasks.Loop.start'):
            tracker = PriceTracker(mock_bot)
        tracker.get_revo_price = MagicMock(return_value=None)  # type: ignore[method-assign]
        await tracker.update_price()
        tracker.gradex.get_channel.assert_not_called()  # type: ignore[attr-defined]

    @pytest.mark.asyncio
    async def test_update_price_no_channel(self, mock_bot: Any) -> None:
        with patch('discord.ext.tasks.Loop.start'):
            tracker = PriceTracker(mock_bot)
        tracker.get_revo_price = MagicMock(return_value=1.23)  # type: ignore[method-assign]
        tracker.gradex.get_channel.return_value = None  # type: ignore[attr-defined]
        await tracker.update_price()
        # Should not raise exception

    @pytest.mark.asyncio
    async def test_before_update_price(self, mock_bot: Any) -> None:
        with patch('discord.ext.tasks.Loop.start'):
            tracker = PriceTracker(mock_bot)
        await tracker.before_update_price()
        mock_bot.wait_until_ready.assert_called_once()

    @pytest.mark.asyncio
    async def test_on_ready(self, mock_bot: Any) -> None:
        with patch('discord.ext.tasks.Loop.start'):
            tracker = PriceTracker(mock_bot)
        await tracker.on_ready()
