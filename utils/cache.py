"""Caching utilities for external API calls."""

import asyncio
import time
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

T = TypeVar("T")


class TTLCache[T]:
    """Simple TTL-based cache with async support."""

    def __init__(self, ttl_seconds: int = 300, maxsize: int = 100) -> None:
        self.ttl_seconds = ttl_seconds
        self.maxsize = maxsize
        self._cache: dict[str, tuple[float, T]] = {}
        self._lock = asyncio.Lock()

    def _is_expired(self, timestamp: float) -> bool:
        return time.time() - timestamp > self.ttl_seconds

    async def get(self, key: str) -> T | None:
        async with self._lock:
            if key in self._cache:
                timestamp, value = self._cache[key]
                if not self._is_expired(timestamp):
                    return value
                else:
                    del self._cache[key]
            return None

    async def set(self, key: str, value: T) -> None:
        async with self._lock:
            # Evict oldest if at maxsize
            if len(self._cache) >= self.maxsize:
                oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k][0])
                del self._cache[oldest_key]
            self._cache[key] = (time.time(), value)

    async def delete(self, key: str) -> None:
        async with self._lock:
            self._cache.pop(key, None)

    async def clear(self) -> None:
        async with self._lock:
            self._cache.clear()


# Global cache instances
_podium_cache = TTLCache[Any](ttl_seconds=300, maxsize=10)  # 5 minutes
_pvp_cache = TTLCache[Any](ttl_seconds=300, maxsize=10)  # 5 minutes


async def cached_podium_api(endpoint: str) -> Any:
    """Fetch podium data with caching."""
    cached = await _podium_cache.get(endpoint)
    if cached is not None:
        return cached

    import httpx

    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(f"https://api.revomon.io/leaderboard/{endpoint}")
        if response.status_code == 200:
            data = response.json()
            await _podium_cache.set(endpoint, data)
            return data
        return None


async def cached_pvp_api() -> Any:
    """Fetch PvP leaderboard data with caching."""
    cached = await _pvp_cache.get("pvp_top_fifteen")
    if cached is not None:
        return cached

    import httpx

    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(
            "https://api.revomon.io/leaderboard/pvp_top_fifteen"
        )
        if response.status_code == 200:
            data = response.json()
            await _pvp_cache.set("pvp_top_fifteen", data)
            return data
        return None


async def invalidate_podium_cache() -> None:
    """Invalidate the podium cache."""
    await _podium_cache.clear()


async def invalidate_pvp_cache() -> None:
    """Invalidate the PvP cache."""
    await _pvp_cache.clear()


def cached(
    ttl_seconds: int = 300, maxsize: int = 100
) -> Callable[[Callable[..., Awaitable[T]]], Callable[..., Awaitable[T]]]:
    """Decorator for caching async function results with TTL."""

    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        cache = TTLCache[T](ttl_seconds=ttl_seconds, maxsize=maxsize)

        async def wrapper(*args: Any, **kwargs: Any) -> T:
            # Create cache key from function name and arguments
            key = f"{func.__name__}:{args}:{kwargs}"
            cached = await cache.get(key)
            if cached is not None:
                return cached
            result = await func(*args, **kwargs)
            await cache.set(key, result)
            return result

        return wrapper

    return decorator
