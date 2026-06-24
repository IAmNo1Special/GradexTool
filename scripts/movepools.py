from typing import Any

"""Script to get movepool data for all revomons from the API."""

import asyncio  # noqa: E402
import json  # noqa: E402
import logging  # noqa: E402
from pathlib import Path  # noqa: E402

import httpx  # noqa: E402
from helpers import to_sentence_case  # noqa: E402

logger = logging.getLogger(__name__)


REVODEX_MOVES_API_BASE = "https://api.revomon.io/revomon/moves"
REVODEX_REVOMON_FILE = Path("data", "revomon.json")
REVODEX_MOVEPOOLS_FILE = Path("data", "movepools.json")

# Limit concurrency to avoid 429s
CONCURRENCY_LIMIT = 25


async def get_raw_movepool(client: httpx.AsyncClient, id_revomon: int) -> dict[str, Any] | None:
    """Get the raw movepool data for a specific revomon from the Revomon Revodex API."""
    try:
        url = f"{REVODEX_MOVES_API_BASE}/{id_revomon}"
        response = await client.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("error") is None and "data" in data:
                return data["data"]  # type: ignore[no-any-return]
        return None
    except httpx.HTTPError as e:
        logger.error(f"HTTP error getting movepool for ID {id_revomon}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error getting movepool for ID {id_revomon}: {e}")
        return None


async def get_movepool(
    semaphore: asyncio.Semaphore,
    client: httpx.AsyncClient,
    revomon: dict[str, Any],
    movepool_data: dict[str, Any],
) -> None:
    """Fetch and process a single revomon's movepool with concurrency limit."""
    id_revomon = revomon.get("idRevomon") or revomon.get("mon_id")
    name = revomon.get("name", "Unknown")

    if not id_revomon:
        return

    async with semaphore:
        movepool = await get_raw_movepool(client, id_revomon)

        if movepool:
            # Process moves
            revomon["movepool"] = []
            if "moves" in movepool:
                revomon["movepool"] = [
                    move["idMove"] for move in movepool["moves"] if "idMove" in move
                ]
                for move in movepool["moves"]:
                    for field in ["category", "name", "type"]:
                        if field in move and move[field] is not None:
                            move[field] = move[field].lower()
                    if "description" in move and move["description"] is not None:
                        move["description"] = to_sentence_case(move["description"])

            movepool_data[id_revomon] = movepool["moves"]
            logger.info(f"[OK] Got movepool for {name} (ID: {id_revomon})")
        else:
            logger.info(f"[FAIL] No movepool found for {name} (ID: {id_revomon})")
            revomon["movepool"] = []
            movepool_data[id_revomon] = None


async def get_movepools(save_to_file: bool = False) -> dict[str, Any]:
    """Get movepools for all revomons from revomon.json."""
    if not REVODEX_REVOMON_FILE.exists():
        logger.info(
            f"{REVODEX_REVOMON_FILE} not found. Please run 'scripts/revomon.py' first."
        )
        raise FileNotFoundError(
            f"{REVODEX_REVOMON_FILE} not found. Please run 'scripts/revomon.py' first."
        )

    with open(REVODEX_REVOMON_FILE, encoding="utf-8") as f:
        revomon_data = json.load(f)

    movepool_data: dict[str, Any] = {}

    logger.info(f"Getting movepools for {len(revomon_data)} revomon...")
    logger.info(f"Concurrency limit: {CONCURRENCY_LIMIT}")

    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
    async with httpx.AsyncClient(timeout=10) as client:
        tasks = [
            get_movepool(semaphore, client, revomon, movepool_data)
            for revomon in revomon_data
        ]

        # Process in chunks to save progress periodically
        chunk_size = 50
        for i in range(0, len(tasks), chunk_size):
            chunk = tasks[i : i + chunk_size]
            await asyncio.gather(*chunk)
            if save_to_file:
                _save_movepools_to_file(movepool_data)

    # Final save
    if save_to_file:
        _save_movepools_to_file(movepool_data, sort=True)
        with open(REVODEX_REVOMON_FILE, "w", encoding="utf-8") as f:
            json.dump(revomon_data, f, indent=2)
        logger.info(f"Updated {REVODEX_REVOMON_FILE} with movepools")

    logger.info("\nLearnlists retrieval complete!")
    logger.info(f"Total revomons processed: {len(movepool_data)}")
    return movepool_data


def _save_movepools_to_file(movepool_data: dict[str, Any], sort: bool = True) -> None:
    """Save current progress to file."""
    if sort:
        movepool_data = dict(sorted(movepool_data.items()))
    with open(REVODEX_MOVEPOOLS_FILE, "w", encoding="utf-8") as f:
        json.dump(movepool_data, f, indent=2)
    logger.info(f"Progress saved to {REVODEX_MOVEPOOLS_FILE}")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    asyncio.run(get_movepools(save_to_file=True))
