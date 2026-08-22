"""Small bounded TTL mapping for in-memory grading scratch state."""

import time
from typing import Any


class BoundedTTLStore:
    """Dict-like store with per-entry TTL and a hard size cap.

    Entries older than ``ttl_seconds`` are evicted lazily on access and on
    insert; when ``maxsize`` is reached, the oldest entry is dropped first.
    Used to keep per-user grading scratchpads from growing without bound.
    """

    def __init__(self, ttl_seconds: float = 1800.0, maxsize: int = 256) -> None:
        self.ttl_seconds = ttl_seconds
        self.maxsize = maxsize
        self._data: dict[Any, tuple[float, dict[str, Any]]] = {}

    def _evict_expired(self) -> None:
        now = time.monotonic()
        expired = [
            k for k, (ts, _) in self._data.items() if now - ts > self.ttl_seconds
        ]
        for key in expired:
            del self._data[key]

    def get(self, key: Any) -> dict[str, Any] | None:
        self._evict_expired()
        entry = self._data.get(key)
        if entry is None:
            return None
        return entry[1]

    def require(self, key: Any) -> dict[str, Any]:
        """Like get(), but typed for callers that know the entry exists."""
        entry = self.get(key)
        assert entry is not None, f"BoundedTTLStore: missing entry for {key!r}"
        return entry

    def set(self, key: Any, value: dict[str, Any]) -> None:
        self._evict_expired()
        if len(self._data) >= self.maxsize:
            oldest_key = min(self._data.keys(), key=lambda k: self._data[k][0])
            del self._data[oldest_key]
        self._data[key] = (time.monotonic(), value)

    def update(self, key: Any, **fields: Any) -> None:
        current = self.get(key)
        if current is None:
            return
        current.update(fields)

    def __contains__(self, key: Any) -> bool:
        return self.get(key) is not None

    def __len__(self) -> int:
        self._evict_expired()
        return len(self._data)
