from typing import Any

"""Script to discover all valid revomon IDs from the API."""

import asyncio  # noqa: E402
import json  # noqa: E402
import logging  # noqa: E402
import os  # noqa: E402
import sqlite3  # noqa: E402
from contextlib import closing  # noqa: E402
from dataclasses import dataclass  # noqa: E402
from datetime import UTC, datetime  # noqa: E402
from email.utils import parsedate_to_datetime  # noqa: E402
from pathlib import Path  # noqa: E402

import httpx  # noqa: E402
import requests  # noqa: E402
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


class RevomonTable:
    """Class to interact with the revomon table in the Gradex SQLite database."""

    def __init__(self) -> None:
        """Initialize with the path to the SQLite database."""
        self.db_path = db_path

    async def build(self) -> None:
        """Build the revomon table by creating, rebuilding, counting entries, and exporting to JSON."""
        # Create the revomon table if it doesn't exist
        self.create()
        # Rebuild the revomon table
        await self.rebuild()
        # Count the entries in the revomon table
        self.count_entries()
        self.export_to_json()

    def _connect(self) -> Any:
        """Private method to establish a connection to the SQLite database."""
        return sqlite3.connect(self.db_path)

    def create(self) -> None:
        """Create the revomon table if it does not already exist."""
        print("Creating revomon table...")

        # Connect to the database and create a cursor
        with closing(self._connect()) as conn, conn:
            cursor = conn.cursor()

            # Drop the revomon table if it already exists
            print("Dropping revomon table if it already exists...")
            conn.execute("DROP TABLE IF EXISTS revomon;")
            print("Revomon table dropped.")

            # Create the revomon table if it doesn't exist
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS "revomon" (
                    "dex_id" INTEGER NOT NULL UNIQUE,
                    "mon_id" INTEGER NOT NULL UNIQUE,
                    "name" TEXT NOT NULL UNIQUE,
                    "description" TEXT NOT NULL UNIQUE,
                    "rarity" TEXT NOT NULL,
                    "ability1" TEXT NOT NULL,
                    "ability2" TEXT,
                    "abilityh" TEXT,
                    "evo" TEXT,
                    "evo_lvl" INTEGER,
                    "evo_tree" TEXT NOT NULL,
                    "type1" TEXT NOT NULL,
                    "type1_img" TEXT NOT NULL,
                    "type2" TEXT,
                    "type2_img" TEXT,
                    "type_chart_img" TEXT,
                    "hp" INTEGER NOT NULL,
                    "atk" INTEGER NOT NULL,
                    "def" INTEGER NOT NULL,
                    "spa" INTEGER NOT NULL,
                    "spd" INTEGER NOT NULL,
                    "spe" INTEGER NOT NULL,
                    "stat_total" INTEGER NOT NULL,
                    "ev_hp" INTEGER NOT NULL,
                    "ev_atk" INTEGER NOT NULL,
                    "ev_def" INTEGER NOT NULL,
                    "ev_spa" INTEGER NOT NULL,
                    "ev_spd" INTEGER NOT NULL,
                    "ev_spe" INTEGER NOT NULL,
                    "img" TEXT NOT NULL,
                    "img_shiny" TEXT NOT NULL,
                    "nft_img" TEXT NOT NULL,
                    "nft_img_shiny" TEXT NOT NULL,
                    "emoji" TEXT NOT NULL,
                    "emoji_shiny" TEXT NOT NULL,
                    "spawn_loc1" TEXT,
                    "spawn_time1" TEXT,
                    "spawn_loc2" TEXT,
                    "spawn_time2" TEXT,
                    "spawn_loc3" TEXT,
                    "spawn_time3" TEXT,
                    "spawn_rate" TEXT NOT NULL,
                    "spawn_table" TEXT NOT NULL,
                    PRIMARY KEY("dex_id")
                ) STRICT;
                """
            )
            print("revomon table created successfully")
            conn.commit()

    async def rebuild(self) -> None:
        """Fetch data from the Revomon API and insert it into the database."""
        # Import helper function for getting evolution trees
        from data import TypesTable
        from utils.emoji_utils import (
            create_emoji_from_url,
            list_application_emojis,
        )
        from utils.revomon_utils import get_evo_trees

        print("Rebuilding revomon table...")
        # Fetch data from the Revomon API
        url = "https://api.revomon.io/revomon/revodex"
        payload: dict[str, list[int]] = {"idsCatchedRevomon": []}
        response = requests.post(url, json=payload)

        # Connect to the database and create a cursor
        with closing(self._connect()) as conn, conn:
            cursor = conn.cursor()

            if response.status_code == 200:
                data = response.json()
                print(f"Number of Revomons fetched: {len(data['data']['revomons'])}")

                with open("./data/revomon.json") as file:
                    revomon_table = json.load(file)

                emoji_dict = {
                    emoji["name"]: emoji["id"]
                    for emoji in await list_application_emojis()
                }

                # Insert data into the database
                for revomon in sorted(
                    data["data"]["revomons"], key=lambda x: x["idRevodex"]
                ):
                    # Prepare data for insertion
                    dex_id = revomon["idRevodex"]
                    mon_id = revomon["idRevomon"]
                    name = revomon["name"].lower()
                    description = revomon["description"].lower()
                    rarity = revomon["rarity"].lower()
                    ability1 = revomon["ability1"].lower()
                    ability2 = (
                        revomon["ability2"].lower() if revomon["ability2"] else None
                    )
                    abilityh = (
                        revomon["abilityHidden"].lower()
                        if revomon["abilityHidden"]
                        else None
                    )
                    evo = (
                        revomon["evolution"].lower()
                        if revomon["evolution"] != ""
                        else None
                    )
                    evo_lvl = (
                        revomon["levelEvolution"]
                        if revomon["levelEvolution"] != 0
                        else None
                    )
                    tree = get_evo_trees()
                    for branch in tree:
                        if name in branch.lower():
                            evo_tree = branch
                    type1: str = revomon["type1"].lower()
                    type1_img = f"https://app-v2.revomon.io/static/images/types/{type1.lower()}.png"
                    type2: str | None = (
                        revomon["type2"].lower() if revomon["type2"] else None
                    )
                    type2_img = (
                        f"https://app-v2.revomon.io/static/images/types/{type2.lower()}.png"
                        if type2
                        else None
                    )
                    types_info = await TypesTable().get_info(type1, type2)
                    type_chart_img = types_info[0][1] if types_info else None

                    # Base stats
                    hp = revomon["hp"]
                    atk = revomon["atk"]
                    def_ = revomon["def"]
                    spa = revomon["spa"]
                    spd = revomon["spd"]
                    spe = revomon["spe"]
                    stat_total = hp + atk + def_ + spa + spd + spe

                    # EV rewards
                    ev_hp = revomon["evhp"]
                    ev_atk = revomon["evatk"]
                    ev_def = revomon["evdef"]
                    ev_spa = revomon["evspa"]
                    ev_spd = revomon["evspd"]
                    ev_spe = revomon["evspe"]

                    # Placeholder values for images, emojis, spawn locations, and times
                    img = f"https://nft.revomon.io/image/raw/revomon/{dex_id}.png"
                    img_shiny = (
                        f"https://nft.revomon.io/image/raw/revomon/{dex_id}_shiny.png"
                    )
                    nft_img = f"https://nft.revomon.io/image/revomon/{dex_id}.png"
                    nft_img_shiny = (
                        f"https://nft.revomon.io/image/revomon/{dex_id}_shiny.png"
                    )
                    if "-" in name:
                        emoji_name = name.replace("-", "_")
                    else:
                        emoji_name = name
                    if emoji_name not in emoji_dict:
                        emoji_obj = await create_emoji_from_url(img, emoji_name)
                        emoji = emoji_obj["id"]
                    else:
                        emoji = emoji_dict[emoji_name]
                    if f"{emoji_name}_shiny" not in emoji_dict:
                        emoji_obj = await create_emoji_from_url(
                            img_shiny, f"{emoji_name}_shiny"
                        )
                        emoji_shiny = emoji_obj["id"]
                    else:
                        emoji_shiny = emoji_dict[f"{emoji_name}_shiny"]

                    for mon in sorted(revomon_table, key=lambda x: x["dex_id"]):
                        if mon["name"].lower() == name.lower():
                            spawn_loc1 = (
                                mon["spawn_loc1"].lower() if mon["spawn_loc1"] else None
                            )
                            spawn_time1 = (
                                mon["spawn_time1"].lower()
                                if mon["spawn_time1"]
                                else None
                            )
                            spawn_loc2 = (
                                mon["spawn_loc2"].lower() if mon["spawn_loc2"] else None
                            )
                            spawn_time2 = (
                                mon["spawn_time2"].lower()
                                if mon["spawn_time2"]
                                else None
                            )
                            spawn_loc3 = (
                                mon["spawn_loc3"].lower() if mon["spawn_loc3"] else None
                            )
                            spawn_time3 = (
                                mon["spawn_time3"].lower()
                                if mon["spawn_time3"]
                                else None
                            )
                            spawn_rate = (
                                "0.1%"
                                if mon["rarity"] == "legendary"
                                else "1%"
                                if mon["rarity"] == "rare"
                                else "98.9%"
                            )

                            spawn_table = f"{spawn_loc1.title() if spawn_loc1 else ''}\n{spawn_time1 if spawn_time1 else ''}\n\n{spawn_loc2.title() if spawn_loc2 else ''}\n{spawn_time2 if spawn_time2 else ''}\n\n{spawn_loc3.title() if spawn_loc3 else ''}\n{spawn_time3 if spawn_time3 else ''}\n\nSPAWN RATE\n{spawn_rate}"

                    # Execute the insert query
                    cursor.execute(
                        """
                        INSERT OR REPLACE INTO revomon
                            (dex_id, mon_id, name, description, rarity, ability1, ability2, abilityh, evo, evo_lvl, evo_tree, type1, type1_img, type2, type2_img, type_chart_img,
                            hp, atk, def, spa, spd, spe, stat_total, ev_hp, ev_atk, ev_def, ev_spa, ev_spd, ev_spe, img, img_shiny, nft_img, nft_img_shiny, emoji, emoji_shiny,
                            spawn_loc1, spawn_time1, spawn_loc2, spawn_time2, spawn_loc3, spawn_time3, spawn_rate, spawn_table)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                        """,
                        (
                            dex_id,
                            mon_id,
                            name,
                            description,
                            rarity,
                            ability1,
                            ability2,
                            abilityh,
                            evo,
                            evo_lvl,
                            evo_tree,
                            type1,
                            type1_img,
                            type2,
                            type2_img,
                            type_chart_img,
                            hp,
                            atk,
                            def_,
                            spa,
                            spd,
                            spe,
                            stat_total,
                            ev_hp,
                            ev_atk,
                            ev_def,
                            ev_spa,
                            ev_spd,
                            ev_spe,
                            img,
                            img_shiny,
                            nft_img,
                            nft_img_shiny,
                            emoji,
                            emoji_shiny,
                            spawn_loc1,
                            spawn_time1,
                            spawn_loc2,
                            spawn_time2,
                            spawn_loc3,
                            spawn_time3,
                            spawn_rate,
                            spawn_table,
                        ),
                    )

                # Commit the transaction
                conn.commit()

        print("revomon table updated successfully!")

        # Export data from the revomon table to a JSON file
        self.export_to_json()

    def export_to_json(self) -> None:
        """Export data from the revomon table to a JSON file."""
        json_file_path = "./data/revomon.json"
        with closing(self._connect()) as conn, conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM revomon;")
            rows = cursor.fetchall()

            # Get column names
            column_names = [description[0] for description in cursor.description]

            # Convert rows to a list of dictionaries
            data = [dict(zip(column_names, row, strict=True)) for row in rows]

            # Write to JSON file
            with open(json_file_path, "w") as json_file:
                json.dump(data, json_file, indent=4)

            print(f"Data exported to {json_file_path}.")

    def count_entries(self) -> Any:
        """Return the number of entries in the revomon table."""
        print("Counting entries in the revomon table...")
        with closing(self._connect()) as conn, conn:
            cursor = conn.cursor()

            # Execute the query and fetch the result
            cursor.execute("SELECT COUNT(*) FROM revomon;")
            count = cursor.fetchone()[0]

            # Close the connection

            # Print the result
            print(f"Number of Revomon in the revomon table: {count}")

            # Return the count
            return count

    def add_revomon(
        self,
        dex_id: int,
        mon_id: int,
        name: str,
        description: str,
        rarity: str,
        ability1: str,
        ability2: str,
        abilityh: str,
        evo: str,
        evo_lvl: int,
        evo_tree: str,
        type1: str,
        type1_img: str,
        type2: str,
        type2_img: str,
        type_chart_img: str | None,
        hp: int,
        atk: int,
        def_: int,
        spa: int,
        spd: int,
        spe: int,
        stat_total: int,
        ev_hp: int,
        ev_atk: int,
        ev_def: int,
        ev_spa: int,
        ev_spd: int,
        ev_spe: int,
        img: str,
        img_shiny: str,
        nft_img: str,
        nft_img_shiny: str,
        emoji: str | None,
        emoji_shiny: str | None,
        spawn_loc1: str,
        spawn_time1: str,
        spawn_loc2: str | None,
        spawn_time2: str | None,
        spawn_loc3: str | None,
        spawn_time3: str | None,
    ) -> None:
        """Add a new Revomon entry to the revomon table in the SQLite database.

        Args:
            dex_id: The Revomon's dex ID.
            mon_id: The Revomon's mon ID.
            name: The Revomon's name.
            description: The Revomon's description.
            rarity: The Revomon's rarity.
            ability1: The Revomon's first ability.
            ability2: The Revomon's second ability.
            abilityh: The Revomon's hidden ability.
            evo: The Revomon's evolution.
            evo_lvl: The level at which the Revomon evolves.
            evo_tree: The Revomon's evolution tree.
            type1: The Revomon's first type.
            type1_img: The URL of the image for the Revomon's first type.
            type2: The Revomon's second type.
            type2_img: The URL of the image for the Revomon's second type.
            type_chart_img: The URL of the image for the Revomon's type chart.
            hp: The Revomon's HP.
            atk: The Revomon's attack.
            def_: The Revomon's defense.
            spa: The Revomon's special attack.
            spd: The Revomon's special defense.
            spe: The Revomon's speed.
            stat_total: The sum of the Revomon's stats.
            ev_hp: The Revomon's HP EVs.
            ev_atk: The Revomon's attack EVs.
            ev_def: The Revomon's defense EVs.
            ev_spa: The Revomon's special attack EVs.
            ev_spd: The Revomon's special defense EVs.
            ev_spe: The Revomon's speed EVs.
            img: The URL of the image for the Revomon.
            img_shiny: The URL of the shiny image for the Revomon.
            nft_img: The URL of the NFT image for the Revomon.
            nft_img_shiny: The URL of the shiny NFT image for the Revomon.
            emoji: The emoji for the Revomon.
            emoji_shiny: The shiny emoji for the Revomon.
            spawn_loc1: The first spawn location for the Revomon.
            spawn_time1: The first spawn time for the Revomon.
            spawn_loc2: The second spawn location for the Revomon.
            spawn_time2: The second spawn time for the Revomon.
            spawn_loc3: The third spawn location for the Revomon.
            spawn_time3: The third spawn time for the Revomon.
        """
        with closing(self._connect()) as conn, conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT OR REPLACE INTO revomon
                    (dex_id, mon_id,name, description, rarity, ability1, ability2, abilityh, evo, evo_lvl, evo_tree, type1, type1_img, type2, type2_img, type_chart_img,
                    hp, atk, def, spa, spd, spe, stat_total, ev_hp, ev_atk, ev_def, ev_spa, ev_spd, ev_spe, img, img_shiny, nft_img, nft_img_shiny, emoji, emoji_shiny,
                    spawn_loc1, spawn_time1, spawn_loc2, spawn_time2, spawn_loc3, spawn_time3)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    dex_id,
                    mon_id,
                    name,
                    description,
                    rarity,
                    ability1,
                    ability2,
                    abilityh,
                    evo,
                    evo_lvl,
                    evo_tree,
                    type1,
                    type1_img,
                    type2,
                    type2_img,
                    type_chart_img,
                    hp,
                    atk,
                    def_,
                    spa,
                    spd,
                    spe,
                    stat_total,
                    ev_hp,
                    ev_atk,
                    ev_def,
                    ev_spa,
                    ev_spd,
                    ev_spe,
                    img,
                    img_shiny,
                    nft_img,
                    nft_img_shiny,
                    emoji,
                    emoji_shiny,
                    spawn_loc1,
                    spawn_time1,
                    spawn_loc2,
                    spawn_time2,
                    spawn_loc3,
                    spawn_time3,
                ),
            )
            conn.commit()

    def get_mon_ids(self) -> list[int]:
        """Returns a list containing all the mon_ids in the revomon table."""
        print("Getting mon_ids...")
        # Connect to the database and create a cursor
        with closing(self._connect()) as conn, conn:
            cursor = conn.cursor()

            # Get the mon_ids from the revomon table
            cursor.execute("SELECT mon_id FROM revomon")

            # Return the list of mon_ids
            mon_ids = [row[0] for row in cursor.fetchall()]

            # Close the connection

            print(f"Got {len(mon_ids)} mon_ids")
            return mon_ids

    def get_names(self) -> list[str]:
        """Returns a list containing all the names of the Revomons in the revomon table, sorted by dex_id."""
        print("Getting names...")
        # Connect to the database and create a cursor
        with closing(self._connect()) as conn, conn:
            cursor = conn.cursor()

            cursor.execute("SELECT name FROM revomon ORDER BY dex_id")

            # Return the list of names
            names = [row[0].lower() for row in cursor.fetchall()]

        print(f"Got {len(names)} names")
        return names

    def get_name_by_id(
        self, mon_id: int | None = None, dex_id: int | None = None
    ) -> str:
        """Returns the name of the Revomon with the given mon_id or dex_id."""
        print("Getting name...")
        # Connect to the database and create a cursor
        with closing(self._connect()) as conn, conn:
            cursor = conn.cursor()

            # Get the name from the revomon table
            if dex_id is not None:
                cursor.execute("SELECT name FROM revomon WHERE dex_id = ?", (dex_id,))
            else:
                cursor.execute("SELECT name FROM revomon WHERE mon_id = ?", (mon_id,))

            # Return the name
            name = cursor.fetchone()[0]

            # Close the connection
            # Return the name
            print(f"Got name: {name}")
            return str(name)

    def get_id_by_id(self, mon_id: int | None = None, dex_id: int | None = None) -> int:
        """Returns the mon_id or dex_id of the Revomon with the given mon_id or dex_id."""
        with closing(self._connect()) as conn, conn:
            cursor = conn.cursor()

            # Get the mon_id or dex_id from the revomon table
            if dex_id is not None:
                print("Getting mon_id from dex_id...")
                cursor.execute("SELECT mon_id FROM revomon WHERE dex_id = ?", (dex_id,))
            else:
                print("Getting dex_id from mon_id...")
                cursor.execute("SELECT dex_id FROM revomon WHERE mon_id = ?", (mon_id,))

            # Fetch the result
            result = cursor.fetchone()
            if result is None:
                raise ValueError("No Revomon found with the given ID.")

            id = result[0]
            print(f"Got mon_id: {id}") if dex_id is not None else print(
                f"Got dex_id: {id}"
            )
            return int(id)

    def get_info(self, revomon_name: str) -> list[Any]:
        """Fetches information for a Revomon by name from the revomon table.

        Args:
            revomon_name (str): The name of the Revomon to search for.

        Returns:
            A list of rows containing the information of matching Revomon entries.
        """
        revomon_name = revomon_name.lower()
        with closing(self._connect()) as conn, conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM revomon WHERE name LIKE ?",
                (f"%{revomon_name}%",),
            )
            rows = cursor.fetchall()
            return list(rows)

    def has_ability(self, ability_name: str, mon_name: str | None = None) -> Any:
        """Check if a given Revomon has a specified ability.

        Args:
            ability_name (str): The name of the ability to look for.
            mon_name (str, optional): The name of the Revomon to check.
                Defaults to None.

        Returns:
            bool: True if the Revomon has the specified ability, otherwise False.
            If mon_name is None, returns a list of Revomon names that have the specified ability.
        """
        with closing(self._connect()) as conn, conn:
            cursor = conn.cursor()
            if mon_name is not None:
                cursor.execute(
                    """
                    SELECT name from revomon
                    WHERE name = ? AND ability1 = ? OR ability2 = ? OR abilityh = ?;
                    """,
                    (
                        mon_name.lower(),
                        ability_name.lower(),
                        ability_name.lower(),
                        ability_name.lower(),
                    ),
                )
                results = cursor.fetchall()
                if results:
                    return True
                else:
                    return False
            else:
                cursor.execute(
                    """
                    SELECT name from revomon
                    WHERE ability1 = ? OR ability2 = ? OR abilityh = ?;
                    """,
                    (
                        ability_name.lower(),
                        ability_name.lower(),
                        ability_name.lower(),
                    ),
                )
                results = cursor.fetchall()
                if results:
                    results = [result[0] for result in results]
                return results


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    asyncio.run(get_revomon_data(download_images=True))
