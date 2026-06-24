from collections.abc import Callable, Coroutine
from typing import Any

"""Health cog: periodic heartbeat logging and bot uptime tracking."""

import asyncio  # noqa: E402
import logging  # noqa: E402
import time  # noqa: E402

logger = logging.getLogger(__name__)

from discord.ext import commands  # noqa: E402

# Heartbeat interval in seconds
_HEARTBEAT_INTERVAL = 300  # 5 minutes


class HealthCog(commands.Cog):
    """Monitors bot health and logs periodic heartbeats."""

    def __init__(self, bot: commands.Bot) -> None:
        """Initialize the HealthCog.

        Args:
            bot: The Discord bot instance.
        """
        self.bot = bot
        self._start_time: float = 0.0
        self._heartbeat_task: asyncio.Task[Any] | None = None

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """Start heartbeat loop when the bot is ready."""
        self._start_time = time.monotonic()
        if self._heartbeat_task is None:
            self._heartbeat_task = self._spawn_background_task(
                self._heartbeat_loop(), name="health_heartbeat"
            )

    def _spawn_background_task(
        self,
        coro: Coroutine[Any, Any, Any],
        name: str | None = None,
        on_error: Callable[[Exception], Coroutine[Any, Any, Any]] | None = None,
    ) -> asyncio.Task[Any]:
        """Create a background task with automatic error handling and cleanup.

        Args:
            coro: The coroutine to run.
            name: Optional task name for debugging.
            on_error: Optional error handler callback.

        Returns:
            The created task.
        """

        async def wrapper() -> None:
            try:
                await coro
            except asyncio.CancelledError:
                pass
            except Exception as e:
                if on_error:
                    await on_error(e)
                else:
                    logger.error("Background task %s failed: %s", name or "unknown", e)

        task = asyncio.create_task(wrapper(), name=name)
        return task

    async def _heartbeat_loop(self) -> None:
        """Periodically log bot health status."""
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            uptime_secs = int(time.monotonic() - self._start_time)
            hours, remainder = divmod(uptime_secs, 3600)
            minutes, seconds = divmod(remainder, 60)
            raw_latency = self.bot.latency
            latency = round(raw_latency * 1000) if raw_latency is not None and raw_latency == raw_latency else 0

            logger.info(
                "Heartbeat: uptime=%dh%dm%ds, guilds=%d, latency=%dms",
                hours,
                minutes,
                seconds,
                len(self.bot.guilds),
                latency,
            )
            await self._sleep(_HEARTBEAT_INTERVAL)

    async def _sleep(self, seconds: float) -> None:
        """Sleep that respects bot shutdown.

        Args:
            seconds: Duration to sleep in seconds.
        """
        try:
            await asyncio.sleep(seconds)
        except asyncio.CancelledError:
            pass

    async def cog_unload(self) -> None:
        """Cancel the heartbeat task when the cog is unloaded."""
        if self._heartbeat_task:
            self._heartbeat_task.cancel()


async def setup(bot: commands.Bot) -> None:
    """Set up the HealthCog.

    Args:
        bot: The Discord bot instance.
    """
    try:
        await bot.add_cog(HealthCog(bot))
    except Exception as e:
        logger.error('ERROR in HealthCog "setup" function: %s', e)
