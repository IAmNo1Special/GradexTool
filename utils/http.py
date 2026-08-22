"""Consolidated async HTTP helpers with retry/backoff and Retry-After support.

Single source of truth for outbound HTTP across runtime cogs and ETL scripts.
"""

import asyncio
import logging
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from typing import Any

import httpx

logger = logging.getLogger(__name__)


def _retry_after_seconds(response: httpx.Response, default: float = 5.0) -> float:
    """Best-effort parse of a Retry-After header (delay or HTTP-date)."""
    raw = response.headers.get("Retry-After")
    if raw is None:
        return default
    try:
        return max(0.0, float(raw))
    except ValueError:
        pass
    try:
        retry_date = parsedate_to_datetime(raw)
    except (TypeError, ValueError, IndexError, OverflowError):
        return default
    if retry_date.tzinfo is None:
        retry_date = retry_date.replace(tzinfo=UTC)
    return max(0.0, (retry_date - datetime.now(UTC)).total_seconds())


async def safe_get(
    url: str,
    client: httpx.AsyncClient | None = None,
    timeout: int = 10,
    retries: int = 5,
    backoff_factor: float = 1.0,
    no_retry: frozenset[int] = frozenset(),
) -> httpx.Response | None:
    """GET a URL with timeout, retries, rate-limit awareness, and backoff.

    Status codes in ``no_retry`` return None immediately (e.g. 404).
    """
    should_close = client is None
    if client is None:
        client = httpx.AsyncClient(timeout=timeout)

    try:
        for attempt in range(retries):
            try:
                response = await client.get(url)
                if response.status_code == 200:
                    return response

                if response.status_code in no_retry:
                    logger.info(
                        "GET %s -> HTTP %s; not retrying", url, response.status_code
                    )
                    return None

                if response.status_code == 429:
                    wait_time = _retry_after_seconds(response)
                    logger.warning(
                        "Rate limited (429) on %s. Sleeping for %.1f seconds...",
                        url,
                        wait_time,
                    )
                    await asyncio.sleep(wait_time)
                    continue

                logger.warning(
                    "Failed to fetch %s: HTTP status %s. Retrying (%s/%s)...",
                    url,
                    response.status_code,
                    attempt + 1,
                    retries,
                )
            except httpx.RequestError as e:
                logger.warning(
                    "Failed to fetch %s: %s. Retrying (%s/%s)...",
                    url,
                    e,
                    attempt + 1,
                    retries,
                )
            if attempt < retries - 1:
                await asyncio.sleep(backoff_factor * (2**attempt))
        return None
    finally:
        if should_close:
            await client.aclose()


async def safe_post(
    url: str,
    json_payload: dict[str, Any],
    client: httpx.AsyncClient | None = None,
    timeout: int = 15,
    retries: int = 3,
    backoff_factor: float = 1.0,
) -> httpx.Response | None:
    """POST JSON to a URL with timeout, retries, and exponential backoff."""
    should_close = client is None
    if client is None:
        client = httpx.AsyncClient(timeout=timeout)

    try:
        for attempt in range(retries):
            try:
                response = await client.post(url, json=json_payload)
                if response.status_code == 200:
                    return response

                if response.status_code == 429:
                    wait_time = _retry_after_seconds(response)
                    logger.warning(
                        "Rate limited (429) on %s. Sleeping for %.1f seconds...",
                        url,
                        wait_time,
                    )
                    await asyncio.sleep(wait_time)
                    continue

                logger.warning(
                    "Failed to post to %s: HTTP status %s. Retrying (%s/%s)...",
                    url,
                    response.status_code,
                    attempt + 1,
                    retries,
                )
            except httpx.RequestError as e:
                logger.warning(
                    "Failed to post to %s: %s. Retrying (%s/%s)...",
                    url,
                    e,
                    attempt + 1,
                    retries,
                )
            if attempt < retries - 1:
                await asyncio.sleep(backoff_factor * (2**attempt))
        return None
    finally:
        if should_close:
            await client.aclose()


async def fetch_json(
    url: str,
    client: httpx.AsyncClient | None = None,
    timeout: int = 10,
    retries: int = 5,
    backoff_factor: float = 1.0,
    no_retry: frozenset[int] = frozenset(),
) -> Any | None:
    """GET and parse JSON; returns None on failure."""
    response = await safe_get(
        url,
        client=client,
        timeout=timeout,
        retries=retries,
        backoff_factor=backoff_factor,
        no_retry=no_retry,
    )
    if response is None:
        return None
    try:
        return response.json()
    except ValueError as e:
        logger.error("Invalid JSON from %s: %s", url, e)
        return None
