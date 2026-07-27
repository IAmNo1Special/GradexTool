from typing import Any

"""Script to discover all valid revomon IDs from the API."""

import asyncio  # noqa: E402
import json  # noqa: E402
import logging  # noqa: E402
import os  # noqa: E402
from dataclasses import dataclass  # noqa: E402
from datetime import UTC, datetime  # noqa: E402
from email.utils import parsedate_to_datetime  # noqa: E402
from pathlib import Path  # noqa: E402

import httpx  # noqa: E402
from helpers import to_sentence_case  # noqa: E402

from configs import (  # noqa: E402
    GRADEX_DB_PATH,
    REVOMON_FILE,
    REVOMON_IMAGES_DOWNLOAD_MANIFEST_FILE,
    REVOMON_NFT_IMAGE_ENDPOINT,
    REVOMON_NFT_IMAGES_DIR,
    REVOMON_RAW_IMAGE_ENDPOINT,
    REVOMON_RAW_IMAGES_DIR,
    REVOMON_REVODEX_ENDPOINT,
    USER_AGENT,
)

db_path: Path = GRADEX_DB_PATH
logger = logging.getLogger(__name__)


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


# Worker concurrency is intentionally separate from request pacing. The pacer below
# controls how quickly requests are started, even when several workers are active.
CONCURRENCY_LIMIT = max(1, _env_int("REVOMON_IMAGE_CONCURRENCY", 3))
REQUEST_INTERVAL_SECONDS = max(
    0.0,
    _env_float("REVOMON_IMAGE_REQUEST_INTERVAL", 0.75),
)
RATE_LIMIT_COOLDOWN_SECONDS = max(
    1.0,
    _env_float("REVOMON_RATE_LIMIT_COOLDOWN", 60.0),
)
MAX_DOWNLOAD_ATTEMPTS = max(1, _env_int("REVOMON_IMAGE_MAX_ATTEMPTS", 8))
CLIENT_TIMEOUT_SECONDS = max(1.0, _env_float("REVOMON_IMAGE_TIMEOUT", 60.0))


@dataclass(frozen=True)
class ImageDownloadResult:
    """Result for one image download attempt."""

    success: bool
    status: str


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


def _is_downloaded(path: Path) -> bool:
    return path.is_file() and path.stat().st_size > 0


def _load_download_manifest() -> dict[str, dict[str, str]]:
    if not REVOMON_IMAGES_DOWNLOAD_MANIFEST_FILE.exists():
        return {}

    try:
        with open(REVOMON_IMAGES_DOWNLOAD_MANIFEST_FILE, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        logger.warning(
            "Could not read %s: %s", REVOMON_IMAGES_DOWNLOAD_MANIFEST_FILE, e
        )
        return {}

    if not isinstance(data, dict):
        return {}

    return data


def _save_download_manifest(manifest: dict[str, dict[str, str]]) -> None:
    REVOMON_IMAGES_DOWNLOAD_MANIFEST_FILE.parent.mkdir(parents=True, exist_ok=True)
    temp_path = REVOMON_IMAGES_DOWNLOAD_MANIFEST_FILE.with_suffix(".json.tmp")
    with open(temp_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)
    temp_path.replace(REVOMON_IMAGES_DOWNLOAD_MANIFEST_FILE)


def _record_manifest_results(
    manifest: dict[str, dict[str, str]],
    id_revodex: int,
    updates: dict[str, str],
) -> bool:
    manifest_entry = manifest.setdefault(str(id_revodex), {})
    changed = False

    for image_type, status in updates.items():
        if manifest_entry.get(image_type) != status:
            manifest_entry[image_type] = status
            changed = True

    return changed


def _status_label(result: ImageDownloadResult) -> str:
    labels = {
        "downloaded": "OK",
        "exists": "SKIP",
        "not_found": "MISS",
        "rate_limited": "FAIL",
    }
    return labels.get(result.status, "FAIL")


async def _download_image(
    client: httpx.AsyncClient,
    pacer: RequestPacer,
    url: str,
    save_path: Path,
    max_attempts: int = MAX_DOWNLOAD_ATTEMPTS,
) -> ImageDownloadResult:
    """Download an image from a URL with retry logic for rate limiting."""
    if _is_downloaded(save_path):
        return ImageDownloadResult(success=True, status="exists")

    last_status = "failed"
    for attempt in range(1, max_attempts + 1):
        try:
            await pacer.wait_for_slot()
            response = await client.get(url)

            if response.status_code == 200:
                save_path.parent.mkdir(parents=True, exist_ok=True)
                temp_path = save_path.with_suffix(f"{save_path.suffix}.tmp")
                temp_path.write_bytes(response.content)
                temp_path.replace(save_path)
                return ImageDownloadResult(success=True, status="downloaded")

            if response.status_code == 404:
                return ImageDownloadResult(success=False, status="not_found")

            if response.status_code == 429:
                retry_after = _retry_after_seconds(response)
                wait_time = (
                    retry_after
                    if retry_after is not None
                    else RATE_LIMIT_COOLDOWN_SECONDS
                )
                last_status = "rate_limited"
                await pacer.pause_all(wait_time)
                logger.warning(
                    "Rate limited on %s; pausing all downloads for %.1fs "
                    "(attempt %s/%s)",
                    url,
                    wait_time,
                    attempt,
                    max_attempts,
                )
                continue

            if 500 <= response.status_code < 600:
                wait_time = min(2 ** (attempt - 1), 30)
                last_status = "failed"
                logger.warning(
                    "Server error %s downloading %s; retrying in %.1fs (attempt %s/%s)",
                    response.status_code,
                    url,
                    wait_time,
                    attempt,
                    max_attempts,
                )
                await asyncio.sleep(wait_time)
                continue

            logger.error("HTTP %s downloading %s", response.status_code, url)
            return ImageDownloadResult(success=False, status="failed")
        except httpx.HTTPError as e:
            wait_time = min(2 ** (attempt - 1), 30)
            last_status = "failed"
            logger.warning(
                "HTTP error downloading %s: %s; retrying in %.1fs (attempt %s/%s)",
                url,
                e,
                wait_time,
                attempt,
                max_attempts,
            )
            await asyncio.sleep(wait_time)
        except OSError as e:
            logger.error("File error saving %s: %s", save_path, e)
            return ImageDownloadResult(success=False, status="failed")

    return ImageDownloadResult(success=False, status=last_status)


def _build_image_variants(id_revodex: int) -> dict[str, dict[str, str | Path]]:
    return {
        "raw_normal": {
            "url": f"{REVOMON_RAW_IMAGE_ENDPOINT}/{id_revodex}.png",
            "path": REVOMON_RAW_IMAGES_DIR / f"{id_revodex}.png",
        },
        "raw_shiny": {
            "url": f"{REVOMON_RAW_IMAGE_ENDPOINT}/{id_revodex}_shiny.png",
            "path": REVOMON_RAW_IMAGES_DIR / f"{id_revodex}_shiny.png",
        },
        "nft_normal": {
            "url": f"{REVOMON_NFT_IMAGE_ENDPOINT}/{id_revodex}.png",
            "path": REVOMON_NFT_IMAGES_DIR / f"{id_revodex}.png",
        },
        "nft_shiny": {
            "url": f"{REVOMON_NFT_IMAGE_ENDPOINT}/{id_revodex}_shiny.png",
            "path": REVOMON_NFT_IMAGES_DIR / f"{id_revodex}_shiny.png",
        },
    }


async def _process_revomon_images(
    semaphore: asyncio.Semaphore,
    client: httpx.AsyncClient,
    pacer: RequestPacer,
    revomon: dict[str, Any],
    results: dict[int, dict[str, bool]],
    manifest: dict[str, dict[str, str]],
    manifest_lock: asyncio.Lock,
) -> None:
    """Download all image variants for a single revomon with concurrency limit."""
    id_revodex = revomon.get("idRevodex")
    name = revomon.get("name", "Unknown")

    if not id_revodex:
        return

    async with semaphore:
        id_revodex = int(id_revodex)
        image_manifest = manifest.get(str(id_revodex), {})
        revomon_results = {}
        manifest_updates = {}

        for image_type, image_data in _build_image_variants(id_revodex).items():
            image_path = image_data["path"]

            if not isinstance(image_path, Path):
                raise TypeError(f"Expected Path for {image_type}")

            if _is_downloaded(image_path):
                result = ImageDownloadResult(success=True, status="exists")
            elif image_manifest.get(image_type) == "not_found":
                result = ImageDownloadResult(success=False, status="not_found")
            else:
                image_url = image_data["url"]
                if not isinstance(image_url, str):
                    raise TypeError(f"Expected URL string for {image_type}")

                result = await _download_image(
                    client,
                    pacer,
                    image_url,
                    image_path,
                )

            revomon_results[image_type] = result.success
            manifest_updates[image_type] = result.status

            logger.info(
                "[%s] %s (%s) - %s",
                _status_label(result),
                name,
                id_revodex,
                image_type,
            )

        results[id_revodex] = revomon_results

        async with manifest_lock:
            changed = _record_manifest_results(
                manifest,
                id_revodex,
                manifest_updates,
            )
            if changed:
                _save_download_manifest(manifest)


async def _download_revomon_images(
    revomon_data: list[dict[str, Any]],
) -> dict[int, dict[str, bool]]:
    """Download images for all revomons from revodex."""
    results: dict[int, dict[str, bool]] = {}
    manifest = _load_download_manifest()
    manifest_lock = asyncio.Lock()

    logger.info(f"Downloading images for {len(revomon_data)} revomons...")
    logger.info(f"Concurrency limit: {CONCURRENCY_LIMIT}")
    logger.info(f"Request interval: {REQUEST_INTERVAL_SECONDS:.2f}s")
    logger.info(f"Rate-limit cooldown: {RATE_LIMIT_COOLDOWN_SECONDS:.1f}s")

    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
    pacer = RequestPacer(REQUEST_INTERVAL_SECONDS)
    timeout = httpx.Timeout(CLIENT_TIMEOUT_SECONDS, connect=10)
    limits = httpx.Limits(
        max_connections=CONCURRENCY_LIMIT,
        max_keepalive_connections=CONCURRENCY_LIMIT,
    )

    async with httpx.AsyncClient(
        headers={"User-Agent": USER_AGENT},
        limits=limits,
        timeout=timeout,
    ) as client:
        tasks = [
            _process_revomon_images(
                semaphore,
                client,
                pacer,
                revomon,
                results,
                manifest,
                manifest_lock,
            )
            for revomon in revomon_data
        ]
        try:
            await asyncio.gather(*tasks)
        finally:
            _save_download_manifest(manifest)

    logger.info("Image download complete!")
    logger.info(f"Total revomons processed: {len(results)}")
    return results


async def get_revomon_data(
    download_images: bool = False,
) -> list[dict[str, Any]] | None:
    """Get revomon data from the official Revodex API.

    Returns:
        The revomon data if valid, None otherwise
    """
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                REVOMON_REVODEX_ENDPOINT,
                json={"idsCatchedRevomon": []},
                headers={"User-Agent": "Mozilla/5.0"},
            )

            if response.status_code == 200:
                resp_data = response.json()
                if resp_data.get("error") is None and "data" in resp_data:
                    raw_revomon_data = resp_data["data"]["revomons"]
                    # Clean up the data - remove unnecessary fields
                    # Sort by idRevodex
                    revomon_data = sorted(
                        raw_revomon_data, key=lambda x: x.get("idRevodex", 0)
                    )

                    # Process each entry
                    for revomon in revomon_data:
                        # Remove isOwned field
                        if "isOwned" in revomon:
                            del revomon["isOwned"]

                        # Lowercase specified fields
                        fields_to_lower = [
                            "ability1",
                            "ability2",
                            "abilityHidden",
                            "evolution",
                            "name",
                            "rarity",
                            "type1",
                            "type2",
                        ]
                        for field in fields_to_lower:
                            if field in revomon and isinstance(revomon[field], str):
                                revomon[field] = revomon[field].lower()
                        # Sentence case description
                        if "description" in revomon and isinstance(
                            revomon["description"], str
                        ):
                            revomon["description"] = to_sentence_case(
                                revomon["description"]
                            )
                    # Save response to JSON file
                    REVOMON_FILE.parent.mkdir(parents=True, exist_ok=True)
                    with open(REVOMON_FILE, "w", encoding="utf-8") as f:
                        json.dump(revomon_data, f, indent=2)
                    logger.info(f"Response saved to {REVOMON_FILE}")
                    if download_images:
                        await _download_revomon_images(revomon_data)
                    return revomon_data

            logger.info(f"API returned status {response.status_code}")
            return None
    except httpx.HTTPError as e:
        logger.error(f"HTTP error occurred: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return None


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    asyncio.run(get_revomon_data(download_images=True))
