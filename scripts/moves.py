import asyncio
import json
import logging
import os
from dataclasses import dataclass
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any

import httpx
from helpers import to_sentence_case

logger = logging.getLogger(__name__)

REVODEX_MOVES_API_BASE = "https://api.revomon.io/revomon/moves"
GRADEX_REVOMON_FILE = Path("data", "revomon.json")
GRADEX_MOVEPOOLS_FILE = Path("data", "movepools.json")
GRADEX_MOVES_FILE = Path("data", "moves.json")
USER_AGENT = "Mozilla/5.0 (compatible; Global Revomon Association)"


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default

    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default

    try:
        return int(value)
    except ValueError:
        logger.warning("Invalid %s=%r; using %s", name, value, default)
        return default


def _env_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None:
        return default

    try:
        return float(value)
    except ValueError:
        logger.warning("Invalid %s=%r; using %s", name, value, default)
        return default


CONCURRENCY_LIMIT = max(1, _env_int("REVOMON_MOVES_CONCURRENCY", 5))
REQUEST_INTERVAL_SECONDS = max(
    0.0,
    _env_float("REVOMON_MOVES_REQUEST_INTERVAL", 1.0),
)
RATE_LIMIT_COOLDOWN_SECONDS = max(
    1.0,
    _env_float("REVOMON_MOVES_RATE_LIMIT_COOLDOWN", 60.0),
)
MAX_ATTEMPTS = max(1, _env_int("REVOMON_MOVES_MAX_ATTEMPTS", 8))
CLIENT_TIMEOUT_SECONDS = max(1.0, _env_float("REVOMON_MOVES_TIMEOUT", 30.0))
REFRESH_MOVEPOOL_CACHE = _env_bool("REVOMON_MOVES_REFRESH", False)


@dataclass(frozen=True)
class MovesFetchResult:
    """Result for one Revomon move-list request."""

    status: str
    moves: list[dict[str, Any]] | None = None


class RequestPacer:
    """Coordinates all requests against one shared remote rate limit."""

    def __init__(self, min_interval_seconds: float) -> None:
        self._min_interval_seconds = max(0.0, min_interval_seconds)
        self._lock = asyncio.Lock()
        self._next_request_at = 0.0

    async def wait_for_slot(self) -> None:
        """Wait until another request can be started."""
        while True:
            async with self._lock:
                now = asyncio.get_running_loop().time()
                wait_time = self._next_request_at - now
                if wait_time <= 0:
                    self._next_request_at = now + self._min_interval_seconds
                    return

            await asyncio.sleep(wait_time)

    async def pause_all(self, seconds: float) -> None:
        """Pause all future requests for at least the requested duration."""
        async with self._lock:
            resume_at = asyncio.get_running_loop().time() + max(0.0, seconds)
            self._next_request_at = max(self._next_request_at, resume_at)


def _retry_after_seconds(response: httpx.Response) -> float | None:
    retry_after = response.headers.get("Retry-After")
    if retry_after is None:
        return None

    try:
        return max(0.0, float(retry_after))
    except ValueError:
        pass

    try:
        retry_after_date = parsedate_to_datetime(retry_after)
    except (TypeError, ValueError, IndexError, OverflowError):
        return None

    if retry_after_date.tzinfo is None:
        retry_after_date = retry_after_date.replace(tzinfo=UTC)

    return max(
        0.0,
        (retry_after_date - datetime.now(UTC)).total_seconds(),
    )


def _load_json_file(path: Path) -> dict[str, Any] | list[Any] | None:
    if not path.exists():
        return None

    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)  # type: ignore
    except (OSError, json.JSONDecodeError) as e:
        logger.warning("Could not read %s: %s", path, e)
        return None


def _save_json_file(path: Path, data: dict[str, Any] | list[Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(f"{path.suffix}.tmp")
    with open(temp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    temp_path.replace(path)


def _id_revomon_list(revomon_data: list[dict[str, Any]]) -> list[int]:
    ids = []
    for revomon in revomon_data:
        id_revomon = revomon.get("idRevomon") or revomon.get("mon_id")
        if id_revomon is not None:
            ids.append(int(id_revomon))

    return ids


def _normalize_move(move: dict[str, Any]) -> dict[str, Any]:
    move_copy = dict(move)
    move_copy.pop("level", None)
    move_copy.pop("method", None)

    for field in ["category", "name", "type"]:
        if field in move_copy and move_copy[field] is not None:
            move_copy[field] = move_copy[field].lower()

    if "description" in move_copy and move_copy["description"] is not None:
        desc = move_copy["description"].replace("\u2019", "'")
        move_copy["description"] = to_sentence_case(desc)

    return move_copy


def _moves_from_movepools(
    movepools: dict[str, list[dict[str, Any]] | None],
) -> list[dict[str, Any]]:
    seen: set[int] = set()
    moves_list: list[dict[str, Any]] = []

    for id_revomon in sorted(movepools, key=int):
        moves = movepools[id_revomon]
        if not moves:
            continue

        for move in moves:
            id_move = move.get("idMove")
            if id_move is not None and id_move not in seen:
                seen.add(id_move)
                moves_list.append(_normalize_move(move))

    return sorted(moves_list, key=lambda move: move["idMove"])


def _load_movepools_cache() -> dict[str, list[dict[str, Any]] | None]:
    data = _load_json_file(GRADEX_MOVEPOOLS_FILE)
    if not isinstance(data, dict):
        return {}

    movepools: dict[str, list[dict[str, Any]] | None] = {}
    for key, value in data.items():
        try:
            normalized_key = str(int(key))
        except (TypeError, ValueError):
            logger.warning("Skipping non-numeric movepool key: %r", key)
            continue

        if value is None or isinstance(value, list):
            movepools[normalized_key] = value
        else:
            logger.warning("Skipping invalid movepool value for ID %s", key)

    return movepools


def _save_movepools_cache(movepools: dict[str, list[dict[str, Any]] | None]) -> None:
    sorted_movepools = {key: movepools[key] for key in sorted(movepools, key=int)}
    _save_json_file(GRADEX_MOVEPOOLS_FILE, sorted_movepools)


async def fetch_moves_for_revomon(
    client: httpx.AsyncClient,
    pacer: RequestPacer,
    id_revomon: int,
    max_attempts: int = MAX_ATTEMPTS,
) -> MovesFetchResult:
    url = f"{REVODEX_MOVES_API_BASE}/{id_revomon}"
    last_status = "error"

    for attempt in range(1, max_attempts + 1):
        try:
            await pacer.wait_for_slot()
            response = await client.get(url)

            if response.status_code == 200:
                payload = response.json()
                if payload.get("error") is None and "data" in payload:
                    return MovesFetchResult(
                        status="found",
                        moves=payload["data"].get("moves", []),
                    )

                return MovesFetchResult(status="not_found")

            if response.status_code == 404:
                return MovesFetchResult(status="not_found")

            if response.status_code == 429:
                retry_after = _retry_after_seconds(response)
                wait_time = retry_after if retry_after is not None else RATE_LIMIT_COOLDOWN_SECONDS
                last_status = "rate_limited"
                await pacer.pause_all(wait_time)
                logger.warning(
                    "Rate limited on moves for Revomon %s; pausing all "
                    "requests for %.1fs (attempt %s/%s)",
                    id_revomon,
                    wait_time,
                    attempt,
                    max_attempts,
                )
                continue

            if 500 <= response.status_code < 600:
                wait_time = min(2 ** (attempt - 1), 30)
                last_status = "error"
                logger.warning(
                    "Server error %s fetching moves for Revomon %s; retrying "
                    "in %.1fs (attempt %s/%s)",
                    response.status_code,
                    id_revomon,
                    wait_time,
                    attempt,
                    max_attempts,
                )
                await asyncio.sleep(wait_time)
                continue

            logger.error(
                "HTTP %s fetching moves for Revomon %s",
                response.status_code,
                id_revomon,
            )
            return MovesFetchResult(status="error")
        except httpx.HTTPError as e:
            wait_time = min(2 ** (attempt - 1), 30)
            last_status = "error"
            logger.warning(
                "HTTP error fetching moves for Revomon %s: %s; retrying in "
                "%.1fs (attempt %s/%s)",
                id_revomon,
                e,
                wait_time,
                attempt,
                max_attempts,
            )
            await asyncio.sleep(wait_time)
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(
                "Invalid JSON fetching moves for Revomon %s: %s",
                id_revomon,
                e,
            )
            return MovesFetchResult(status="error")

    return MovesFetchResult(status=last_status)


async def _fetch_missing_movepools(
    movepools: dict[str, list[dict[str, Any]] | None],
    missing_ids: list[int],
) -> list[int]:
    failed_ids = []
    timeout = httpx.Timeout(CLIENT_TIMEOUT_SECONDS, connect=10)
    limits = httpx.Limits(
        max_connections=CONCURRENCY_LIMIT,
        max_keepalive_connections=CONCURRENCY_LIMIT,
    )
    pacer = RequestPacer(REQUEST_INTERVAL_SECONDS)

    async with httpx.AsyncClient(
        headers={"User-Agent": USER_AGENT},
        limits=limits,
        timeout=timeout,
    ) as client:
        for start in range(0, len(missing_ids), CONCURRENCY_LIMIT):
            batch_ids = missing_ids[start : start + CONCURRENCY_LIMIT]
            tasks = [
                fetch_moves_for_revomon(client, pacer, id_revomon)
                for id_revomon in batch_ids
            ]
            batch_results = await asyncio.gather(*tasks)

            for id_revomon, result in zip(batch_ids, batch_results, strict=True):
                if result.status == "found":
                    movepools[str(id_revomon)] = result.moves or []
                    logger.info("[OK] Fetched moves for Revomon %s", id_revomon)
                elif result.status == "not_found":
                    movepools[str(id_revomon)] = None
                    logger.info(
                        "[MISS] No moves found for Revomon %s",
                        id_revomon,
                    )
                else:
                    failed_ids.append(id_revomon)
                    logger.warning(
                        "[FAIL] Could not fetch moves for Revomon %s (%s)",
                        id_revomon,
                        result.status,
                    )

            _save_movepools_cache(movepools)

    return failed_ids


async def get_moves(save_to_file: bool = False) -> list[dict[str, Any]]:
    movepools = _load_movepools_cache()
    revomon_data = _load_json_file(GRADEX_REVOMON_FILE)

    if not isinstance(revomon_data, list):
        if movepools:
            logger.warning(
                "%s not found; building moves from existing %s",
                GRADEX_REVOMON_FILE,
                GRADEX_MOVEPOOLS_FILE,
            )
        else:
            logger.error(
                "Error: neither %s nor %s are available.",
                GRADEX_REVOMON_FILE,
                GRADEX_MOVEPOOLS_FILE,
            )
            return []

    if isinstance(revomon_data, list):
        ids_revomon = _id_revomon_list(revomon_data)
        if REFRESH_MOVEPOOL_CACHE:
            missing_ids = ids_revomon
            logger.info("Refreshing cached move lists from the API.")
        else:
            missing_ids = [
                id_revomon
                for id_revomon in ids_revomon
                if str(id_revomon) not in movepools
            ]

        if missing_ids:
            logger.info(
                "Fetching %s missing move lists from the API...",
                len(missing_ids),
            )
            logger.info("Concurrency limit: %s", CONCURRENCY_LIMIT)
            logger.info("Request interval: %.2fs", REQUEST_INTERVAL_SECONDS)
            logger.info(
                "Rate-limit cooldown: %.1fs",
                RATE_LIMIT_COOLDOWN_SECONDS,
            )
            failed_ids = await _fetch_missing_movepools(movepools, missing_ids)
            if failed_ids:
                logger.error(
                    "Moves fetch paused with %s failed Revomon IDs. Rerun "
                    "the script to retry them: %s",
                    len(failed_ids),
                    failed_ids[:20],
                )
                return []
        else:
            logger.info(
                "Using cached move lists from %s; no API calls needed.",
                GRADEX_MOVEPOOLS_FILE,
            )

    final_moves = _moves_from_movepools(movepools)

    if save_to_file:
        logger.info(
            "Saving %s moves to %s...",
            len(final_moves),
            GRADEX_MOVES_FILE,
        )
        _save_json_file(GRADEX_MOVES_FILE, final_moves)

    logger.info("Done!")
    return final_moves


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    asyncio.run(get_moves(save_to_file=True))
