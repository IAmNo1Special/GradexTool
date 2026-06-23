from typing import Any
"""Script to discover all valid caught Revomon IDs from the API."""

import asyncio
import json
import logging
import os
from dataclasses import dataclass
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from pathlib import Path

import httpx

logger = logging.getLogger(__name__)


REVOMON_API_BASE = "https://api.revomon.io/revomon"
REVODEX_CAUGHT_REVOMON_FILE = Path("data", "caught_revomon.json")
CAUGHT_REVOMON_SCAN_STATE_FILE = Path("data", "caught_revomon_scan_state.json")
USER_AGENT = "Mozilla/5.0 (compatible; Global Revomon Association)"


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


CONCURRENCY_LIMIT = max(1, _env_int("REVOMON_CAUGHT_CONCURRENCY", 25))
REQUEST_INTERVAL_SECONDS = max(
    0.0,
    _env_float("REVOMON_CAUGHT_REQUEST_INTERVAL", 1.0),
)
RATE_LIMIT_COOLDOWN_SECONDS = max(
    1.0,
    _env_float("REVOMON_CAUGHT_RATE_LIMIT_COOLDOWN", 60.0),
)
MAX_ATTEMPTS = max(1, _env_int("REVOMON_CAUGHT_MAX_ATTEMPTS", 8))
CLIENT_TIMEOUT_SECONDS = max(1.0, _env_float("REVOMON_CAUGHT_TIMEOUT", 30.0))
DEFAULT_MAX_ID = max(1, _env_int("REVOMON_CAUGHT_MAX_ID", 1_000_000))
DEFAULT_EMPTY_TAIL_LIMIT = max(
    1,
    _env_int("REVOMON_CAUGHT_EMPTY_TAIL_LIMIT", 100),
)
CHECKPOINT_INTERVAL = max(
    1,
    _env_int("REVOMON_CAUGHT_CHECKPOINT_INTERVAL", CONCURRENCY_LIMIT * 2),
)
COMPLETE_STATUSES = {"found", "not_found"}
KNOWN_STATUSES = COMPLETE_STATUSES | {"error", "rate_limited"}


@dataclass(frozen=True)
class CaughtRevomonResult:
    """Result for one caught Revomon ID lookup."""

    status: str
    data: dict[str, Any] | None = None


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


async def get_caught_revomon(
    client: httpx.AsyncClient,
    pacer: RequestPacer,
    id_catched_revomon: int,
    max_attempts: int = MAX_ATTEMPTS,
) -> CaughtRevomonResult:
    """Fetch a specific caught Revomon ID."""
    url = f"{REVOMON_API_BASE}/{id_catched_revomon}"
    last_status = "error"

    for attempt in range(1, max_attempts + 1):
        try:
            await pacer.wait_for_slot()
            response = await client.get(url)

            if response.status_code == 200:
                payload = response.json()
                if payload.get("error") is None and isinstance(
                    payload.get("data"), dict
                ):
                    inner_data = payload["data"].get("catchedRevomon", payload["data"])
                    return CaughtRevomonResult(
                        status="found",
                        data=inner_data,
                    )

                return CaughtRevomonResult(status="not_found")

            if response.status_code == 404:
                return CaughtRevomonResult(status="not_found")

            if response.status_code == 429:
                retry_after = _retry_after_seconds(response)
                wait_time = retry_after if retry_after is not None else RATE_LIMIT_COOLDOWN_SECONDS
                last_status = "rate_limited"
                await pacer.pause_all(wait_time)
                logger.warning(
                    "Rate limited on caught Revomon ID %s; pausing all "
                    "requests for %.1fs (attempt %s/%s)",
                    id_catched_revomon,
                    wait_time,
                    attempt,
                    max_attempts,
                )
                continue

            if 500 <= response.status_code < 600:
                wait_time = min(2 ** (attempt - 1), 30)
                last_status = "error"
                logger.warning(
                    "Server error %s testing ID %s; retrying in %.1fs (attempt %s/%s)",
                    response.status_code,
                    id_catched_revomon,
                    wait_time,
                    attempt,
                    max_attempts,
                )
                await asyncio.sleep(wait_time)
                continue

            if response.status_code == 400:
                logger.debug(
                    "HTTP 400 for caught Revomon ID %s; treating as not found",
                    id_catched_revomon,
                )
                return CaughtRevomonResult(status="not_found")

            logger.error(
                "HTTP %s testing caught Revomon ID %s",
                response.status_code,
                id_catched_revomon,
            )
            return CaughtRevomonResult(status="error")
        except httpx.HTTPError as e:
            wait_time = min(2 ** (attempt - 1), 30)
            last_status = "error"
            logger.warning(
                "HTTP error testing ID %s: %s; retrying in %.1fs (attempt %s/%s)",
                id_catched_revomon,
                e,
                wait_time,
                attempt,
                max_attempts,
            )
            await asyncio.sleep(wait_time)
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(
                "Invalid JSON testing caught Revomon ID %s: %s",
                id_catched_revomon,
                e,
            )
            return CaughtRevomonResult(status="error")

    return CaughtRevomonResult(status=last_status)


def _load_results() -> dict[int, dict[str, Any]]:
    if not REVODEX_CAUGHT_REVOMON_FILE.exists():
        return {}

    try:
        with open(REVODEX_CAUGHT_REVOMON_FILE, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        logger.warning("Could not read %s: %s", REVODEX_CAUGHT_REVOMON_FILE, e)
        return {}

    if not isinstance(data, dict):
        return {}

    results = {}
    for key, value in data.items():
        try:
            results[int(key)] = value
        except (TypeError, ValueError):
            logger.warning("Skipping non-numeric caught Revomon ID key: %r", key)

    return results


def _load_scan_state(start_id: int) -> dict[str, Any]:
    if not CAUGHT_REVOMON_SCAN_STATE_FILE.exists():
        return {"version": 1, "next_id": start_id, "statuses": {}}

    try:
        with open(CAUGHT_REVOMON_SCAN_STATE_FILE, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        logger.warning("Could not read %s: %s", CAUGHT_REVOMON_SCAN_STATE_FILE, e)
        return {"version": 1, "next_id": start_id, "statuses": {}}

    if not isinstance(data, dict):
        return {"version": 1, "next_id": start_id, "statuses": {}}

    raw_statuses = data.get("statuses", {})
    if not isinstance(raw_statuses, dict):
        raw_statuses = {}

    statuses = {}
    for key, value in raw_statuses.items():
        try:
            normalized_key = str(int(key))
        except (TypeError, ValueError):
            logger.warning("Skipping non-numeric scan-state ID key: %r", key)
            continue

        normalized_status = str(value)
        if normalized_status not in KNOWN_STATUSES:
            logger.warning(
                "Skipping unknown scan-state status for ID %s: %r",
                normalized_key,
                value,
            )
            continue

        statuses[normalized_key] = normalized_status

    try:
        next_id = int(data.get("next_id", start_id))
    except (TypeError, ValueError):
        next_id = start_id

    data["version"] = 1
    data["next_id"] = max(start_id, next_id)
    data["statuses"] = statuses
    return data


def _save_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_name(path.name + ".tmp")
    with open(temp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    temp_path.replace(path)


def save_progress(results: dict[int, dict[str, Any]], state: dict[str, Any]) -> None:
    """Save current progress to files."""
    sorted_results = {
        str(id_catched_revomon): results[id_catched_revomon]
        for id_catched_revomon in sorted(results)
    }
    next_id = state.get("next_id", 1)
    sorted_state = {
        **state,
        "statuses": {
            key: state["statuses"][key]
            for key in sorted(state["statuses"], key=int)
            if state["statuses"][key] != "not_found" or int(key) >= next_id
        },
    }

    _save_json(REVODEX_CAUGHT_REVOMON_FILE, sorted_results)
    _save_json(CAUGHT_REVOMON_SCAN_STATE_FILE, sorted_state)
    logger.info(
        "Progress saved: %s valid IDs found; next ID %s",
        len(results),
        state["next_id"],
    )


def _advance_frontier(
    id_catched_revomon: int,
    status: str,
    last_found_id: int | None,
    missing_tail: int,
) -> tuple[int | None, int]:
    if status == "found":
        return id_catched_revomon, 0

    if status == "not_found":
        return last_found_id, missing_tail + 1

    return last_found_id, missing_tail


def _recompute_frontier(
    statuses: dict[str, str],
    start_id: int,
    next_id: int,
) -> tuple[int | None, int]:
    last_found_id = None
    missing_tail = 0

    for id_catched_revomon in range(start_id, next_id):
        status = statuses.get(str(id_catched_revomon), "not_found")
        if status in COMPLETE_STATUSES:
            last_found_id, missing_tail = _advance_frontier(
                id_catched_revomon,
                status,
                last_found_id,
                missing_tail,
            )

    return last_found_id, missing_tail


def _build_state_dict(
    start_id: int,
    max_id: int,
    empty_tail_limit: int,
    next_id: int,
    last_found_id: int | None,
    missing_tail: int,
    statuses: dict[str, str],
    stop_reason: str | None = None,
) -> dict[str, Any]:
    d: dict[str, Any] = {
        "start_id": start_id,
        "max_id": max_id,
        "empty_tail_limit": empty_tail_limit,
        "next_id": next_id,
        "last_found_id": last_found_id,
        "consecutive_missing_after_last_found": missing_tail,
        "statuses": statuses,
    }
    if stop_reason is not None:
        d["stop_reason"] = stop_reason
    return d


def _found_name(data: dict[str, Any] | None) -> str:
    if not isinstance(data, dict):
        return "Unknown"

    return str(data.get("name", "Unknown"))


async def _process_batch(
    client: httpx.AsyncClient,
    pacer: RequestPacer,
    ids: list[int],
) -> list[CaughtRevomonResult]:
    tasks = [
        get_caught_revomon(client, pacer, id_catched_revomon)
        for id_catched_revomon in ids
    ]
    return await asyncio.gather(*tasks)


async def get_caught_revomon_data(
    start_id: int = 1,
    max_id: int = DEFAULT_MAX_ID,
    empty_tail_limit: int = DEFAULT_EMPTY_TAIL_LIMIT,
) -> dict[int, dict[str, Any]]:
    """Discover valid caught Revomon IDs by testing a range."""
    results = _load_results()
    state = _load_scan_state(start_id)
    statuses = state["statuses"]

    for id_catched_revomon in results:
        statuses.setdefault(str(id_catched_revomon), "found")

    current_id = int(state.get("next_id", start_id))
    last_found_id = state.get("last_found_id")
    missing_tail = state.get("consecutive_missing_after_last_found")

    if (
        last_found_id is None
        or missing_tail is None
        or (last_found_id is not None and last_found_id not in results)
    ):
        last_found_id, missing_tail = _recompute_frontier(
            statuses,
            start_id,
            current_id,
        )

    checked_since_save = 0
    stop_reason = "max_id"

    logger.info(
        "Discovering caught Revomon IDs from %s to %s...",
        current_id,
        max_id,
    )
    logger.info("Concurrency limit: %s", CONCURRENCY_LIMIT)
    logger.info("Request interval: %.2fs", REQUEST_INTERVAL_SECONDS)
    logger.info("Rate-limit cooldown: %.1fs", RATE_LIMIT_COOLDOWN_SECONDS)
    logger.info("Empty-tail stop: %s misses after last found", empty_tail_limit)

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
        while current_id <= max_id:
            existing_status = statuses.get(str(current_id))
            if existing_status in COMPLETE_STATUSES:
                last_found_id, missing_tail = _advance_frontier(
                    current_id,
                    existing_status,
                    last_found_id,
                    missing_tail,
                )
                current_id += 1
                continue

            batch_ids: list[int] = []
            candidate_id = current_id
            while candidate_id <= max_id and len(batch_ids) < CONCURRENCY_LIMIT:
                if statuses.get(str(candidate_id)) in COMPLETE_STATUSES:
                    break
                batch_ids.append(candidate_id)
                candidate_id += 1

            batch_results = await _process_batch(client, pacer, batch_ids)
            should_pause = False
            pause_id = None

            for id_catched_revomon, result in zip(
                batch_ids, batch_results, strict=True
            ):
                statuses[str(id_catched_revomon)] = result.status

                if result.status not in COMPLETE_STATUSES:
                    if not should_pause:
                        logger.warning(
                            "Pausing discovery at ID %s after status"
                            " %s; rerun to retry from this ID.",
                            id_catched_revomon,
                            result.status,
                        )
                        pause_id = id_catched_revomon
                        should_pause = True
                        stop_reason = result.status
                    continue

                if result.status == "found" and result.data is not None:
                    results[id_catched_revomon] = result.data

                if not should_pause:
                    last_found_id, missing_tail = _advance_frontier(
                        id_catched_revomon,
                        result.status,
                        last_found_id,
                        missing_tail,
                    )

                    if result.status == "found":
                        logger.info(
                            "[OK] Found valid ID: %s - %s",
                            id_catched_revomon,
                            _found_name(result.data),
                        )
                    elif id_catched_revomon % 100 == 0:
                        logger.info(
                            "Testing... reached ID %s; empty tail %s/%s",
                            id_catched_revomon,
                            missing_tail,
                            empty_tail_limit,
                        )

                checked_since_save += 1

            if should_pause:
                assert pause_id is not None
                current_id = pause_id
            else:
                current_id = candidate_id

            state.update(
                _build_state_dict(
                    start_id,
                    max_id,
                    empty_tail_limit,
                    current_id,
                    last_found_id,
                    missing_tail,
                    statuses,
                )
            )

            if checked_since_save >= CHECKPOINT_INTERVAL:
                save_progress(results, state)
                checked_since_save = 0

            if should_pause:
                break

            if last_found_id is not None and missing_tail >= empty_tail_limit:
                stop_reason = "empty_tail"
                break

    state.update(
        _build_state_dict(
            start_id,
            max_id,
            empty_tail_limit,
            current_id,
            last_found_id,
            missing_tail,
            statuses,
            stop_reason,
        )
    )
    save_progress(results, state)

    if stop_reason == "empty_tail":
        logger.info(
            "Discovery stopped after %s consecutive missing IDs after last "
            "found ID %s.",
            missing_tail,
            last_found_id,
        )
    elif stop_reason == "max_id":
        logger.info("Discovery reached max ID %s.", max_id)
    else:
        logger.info("Discovery paused because of status: %s", stop_reason)

    logger.info("Total valid IDs found: %s", len(results))
    logger.info("Results saved to %s", REVODEX_CAUGHT_REVOMON_FILE)
    return results


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    asyncio.run(get_caught_revomon_data())
