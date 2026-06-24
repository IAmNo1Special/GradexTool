from typing import Any

"""Comprehensive tests for health.py cog."""

import asyncio  # noqa: E402
from unittest.mock import AsyncMock, MagicMock, patch  # noqa: E402

import pytest  # noqa: E402

from mods.core.health import _HEARTBEAT_INTERVAL, HealthCog, setup  # noqa: E402


class TestHealthCogConstants:
    """Test suite for health cog constants."""

    def test_heartbeat_interval_constant(self) -> None:
        """Test that _HEARTBEAT_INTERVAL is properly defined."""
        assert isinstance(_HEARTBEAT_INTERVAL, int)
        assert _HEARTBEAT_INTERVAL > 0
        assert _HEARTBEAT_INTERVAL == 300  # 5 minutes


class TestHealthCogInitialization:
    """Test suite for HealthCog initialization."""

    def test_health_cog_init(self, mock_bot: Any) -> None:
        """Test HealthCog initialization."""
        cog = HealthCog(mock_bot)

        assert cog.bot == mock_bot
        assert cog._start_time == 0.0
        assert cog._heartbeat_task is None
        assert isinstance(cog, HealthCog)

    def test_health_cog_is_cog(self, mock_bot: Any) -> None:
        """Test that HealthCog is a proper Discord Cog."""
        from discord.ext import commands

        cog = HealthCog(mock_bot)
        assert isinstance(cog, commands.Cog)


class TestHealthCogMethods:
    """Test suite for HealthCog methods."""

    def test_cog_has_heartbeat_loop(self, mock_bot: Any) -> None:
        """Test that HealthCog has _heartbeat_loop method."""
        cog = HealthCog(mock_bot)

        assert hasattr(cog, "_heartbeat_loop")
        assert callable(cog._heartbeat_loop)

    def test_cog_has_sleep_method(self, mock_bot: Any) -> None:
        """Test that HealthCog has _sleep method."""
        cog = HealthCog(mock_bot)

        assert hasattr(cog, "_sleep")
        assert callable(cog._sleep)

    def test_cog_has_cog_unload(self, mock_bot: Any) -> None:
        """Test that HealthCog has cog_unload method."""
        cog = HealthCog(mock_bot)

        assert hasattr(cog, "cog_unload")
        assert callable(cog.cog_unload)


class TestHealthCogSetup:
    """Test suite for health setup function."""

    @pytest.mark.asyncio
    async def test_setup_adds_cog(self, mock_bot: Any) -> None:
        """Test that setup function adds the cog to bot."""
        await setup(mock_bot)

        mock_bot.add_cog.assert_called_once()

        call_args = mock_bot.add_cog.call_args
        cog = call_args[0][0]
        assert isinstance(cog, HealthCog)

    @pytest.mark.asyncio
    async def test_setup_handles_exception(self, mock_bot: Any) -> None:
        """Test that setup handles exceptions gracefully."""
        mock_bot.add_cog = AsyncMock(side_effect=Exception("Setup error"))

        await setup(mock_bot)

        mock_bot.add_cog.assert_called_once()


class TestHealthCogIntegration:
    """Integration tests for health system."""

    @pytest.mark.asyncio
    async def test_cog_lifecycle(self, mock_bot: Any) -> None:
        """Test cog lifecycle: setup -> initialization."""
        await setup(mock_bot)

        cog = HealthCog(mock_bot)

        # Verify setup was called
        mock_bot.add_cog.assert_called_once()

        # Verify cog was created
        assert isinstance(cog, HealthCog)


# Note: Complex async tests for heartbeat loop have been simplified to avoid
# timing issues and Discord library dependencies. The structural tests
# provide good coverage of the health monitoring functionality.


class TestHealthCogLogic:
    @pytest.mark.asyncio
    async def test_spawn_background_task_success(self, mock_bot: Any) -> None:
        cog = HealthCog(mock_bot)

        async def my_task() -> int:
            return 42

        task = cog._spawn_background_task(my_task())
        await task
        assert task.result() is None  # wrapper returns None

    @pytest.mark.asyncio
    async def test_spawn_background_task_cancelled(self, mock_bot: Any) -> None:
        cog = HealthCog(mock_bot)

        async def my_task() -> None:
            raise asyncio.CancelledError()

        task = cog._spawn_background_task(my_task())
        await task

    @pytest.mark.asyncio
    async def test_spawn_background_task_exception_no_handler(
        self, mock_bot: Any
    ) -> None:
        cog = HealthCog(mock_bot)

        async def my_task() -> None:
            raise Exception("Fail")

        with patch("mods.core.health.logger") as mock_logger:
            task = cog._spawn_background_task(my_task())
            await task
            mock_logger.error.assert_called_once()

    @pytest.mark.asyncio
    async def test_spawn_background_task_exception_with_handler(
        self, mock_bot: Any
    ) -> None:
        cog = HealthCog(mock_bot)

        async def my_task() -> None:
            raise Exception("Fail")

        mock_handler = AsyncMock()
        task = cog._spawn_background_task(my_task(), on_error=mock_handler)
        await task
        mock_handler.assert_called_once()

    """Test suite for HealthCog logic."""

    @pytest.mark.asyncio
    @patch("mods.core.health.HealthCog._spawn_background_task")
    async def test_on_ready_spawns_task(self, mock_spawn: Any, mock_bot: Any) -> None:
        cog = HealthCog(mock_bot)
        assert cog._start_time == 0.0
        assert cog._heartbeat_task is None

        await cog.on_ready()

        assert cog._start_time > 0.0
        mock_spawn.assert_called_once()
        assert cog._heartbeat_task == mock_spawn.return_value

        # Cleanup unawaited coroutine
        coro = mock_spawn.call_args[0][0]
        coro.close()

        # Calling again shouldn't spawn a new task
        mock_spawn.reset_mock()
        await cog.on_ready()
        mock_spawn.assert_not_called()

    @pytest.mark.asyncio
    @patch("mods.core.health.logger")
    @patch("mods.core.health.time.monotonic")
    async def test_heartbeat_loop(
        self, mock_monotonic: Any, mock_logger: Any, mock_bot: Any
    ) -> None:
        cog = HealthCog(mock_bot)
        cog._start_time = 1000.0

        # We need the loop to run once and then stop.
        mock_bot.is_closed.side_effect = [False, True]

        # mock time to simulate 1h 1m 1s uptime -> 3661 seconds
        mock_monotonic.return_value = 4661.0

        mock_bot.latency = 0.123  # 123ms
        mock_bot.guilds = [1, 2, 3]  # length 3

        # mock sleep
        cog._sleep = AsyncMock()  # type: ignore[method-assign]

        await cog._heartbeat_loop()

        mock_bot.wait_until_ready.assert_called_once()
        mock_logger.info.assert_called_once_with(
            "Heartbeat: uptime=%dh%dm%ds, guilds=%d, latency=%dms", 1, 1, 1, 3, 123
        )
        cog._sleep.assert_called_once_with(300)

    @pytest.mark.asyncio
    @patch("mods.core.health.asyncio.sleep")
    async def test_sleep(self, mock_asyncio_sleep: Any, mock_bot: Any) -> None:
        cog = HealthCog(mock_bot)
        await cog._sleep(5)
        mock_asyncio_sleep.assert_called_once_with(5)

    @pytest.mark.asyncio
    @patch("mods.core.health.asyncio.sleep")
    async def test_sleep_cancelled(
        self, mock_asyncio_sleep: Any, mock_bot: Any
    ) -> None:
        mock_asyncio_sleep.side_effect = asyncio.CancelledError()
        cog = HealthCog(mock_bot)
        # Should catch CancelledError and not raise
        await cog._sleep(5)
        mock_asyncio_sleep.assert_called_once_with(5)

    @pytest.mark.asyncio
    async def test_cog_unload(self, mock_bot: Any) -> None:
        cog = HealthCog(mock_bot)

        # with no task
        await cog.cog_unload()

        # with task
        mock_task = MagicMock()
        cog._heartbeat_task = mock_task
        await cog.cog_unload()
        mock_task.cancel.assert_called_once()
