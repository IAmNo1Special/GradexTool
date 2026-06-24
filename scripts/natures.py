from typing import Any

"""Script to fetch nature data from PokeAPI and save to natures.json."""

import asyncio  # noqa: E402
import json  # noqa: E402
import logging  # noqa: E402
import os  # noqa: E402
from pathlib import Path  # noqa: E402

import httpx  # noqa: E402

logger = logging.getLogger(__name__)


POKEAPI_NATURE_LIST = "https://pokeapi.co/api/v2/nature?limit=25"
POKEAPI_NATURE_BASE = "https://pokeapi.co/api/v2/nature"
NATURES_FILE = Path("data", "natures.json")

# Map PokeAPI stat names to revomon.json stat abbreviations
STAT_MAP = {
    "attack": "atk",
    "defense": "def",
    "special-attack": "spa",
    "special-defense": "spd",
    "speed": "spe",
    "hp": "hp",
}

# Limit concurrency to avoid 429s
CONCURRENCY_LIMIT = 10


async def fetch_nature(client: httpx.AsyncClient, name: str) -> dict[str, Any] | None:
    """Fetch a single nature from PokeAPI."""
    try:
        url = f"{POKEAPI_NATURE_BASE}/{name}"
        response = await client.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()  # type: ignore[no-any-return]
        return None
    except httpx.HTTPError as e:
        logger.error(f"  HTTP error fetching nature '{name}': {e}")
        return None
    except Exception as e:
        logger.error(f"  Unexpected error fetching nature '{name}': {e}")
        return None


async def process_nature(
    semaphore: asyncio.Semaphore,
    client: httpx.AsyncClient,
    name: str,
    natures_list: list[dict[str, Any]],
) -> None:
    """Fetch and process a single nature with concurrency limit."""
    async with semaphore:
        logger.info(f"  Fetching '{name}'...")
        nature_data = await fetch_nature(client, name)

        if nature_data:
            increased = nature_data.get("increased_stat")
            decreased = nature_data.get("decreased_stat")

            nature_entry = {
                "name": name.lower(),
                "increased_stat": STAT_MAP.get(increased["name"])
                if increased
                else None,
                "decreased_stat": STAT_MAP.get(decreased["name"])
                if decreased
                else None,
            }
            natures_list.append(nature_entry)
        else:
            logger.error(f"  Failed to fetch '{name}', skipping.")


async def get_natures(save_to_file: bool = False) -> None:
    """Fetch all natures from PokeAPI and save them to a JSON file."""
    logger.info("Fetching nature list from PokeAPI...")
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            response = await client.get(POKEAPI_NATURE_LIST)
            response.raise_for_status()
            data = response.json()
            nature_names = [n["name"] for n in data.get("results", [])]
        except httpx.HTTPError as e:
            logger.error(f"Error fetching nature list: {e}")
            return

        logger.info(f"Found {len(nature_names)} natures. Fetching details...")

        natures_list: list[dict[str, Any]] = []
        semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
        tasks = [
            process_nature(semaphore, client, name, natures_list)
            for name in nature_names
        ]
        await asyncio.gather(*tasks)

    # Sort alphabetically by name
    natures_list.sort(key=lambda x: x["name"])

    # Assign sequential IDs and build dict
    natures_dict = {}
    for i, nature in enumerate(natures_list, start=1):
        nature["idNature"] = i
        natures_dict[str(i)] = nature

    if save_to_file:
        logger.info(f"Saving {len(natures_dict)} natures to {NATURES_FILE}...")
        os.makedirs(NATURES_FILE.parent, exist_ok=True)
        with open(NATURES_FILE, "w", encoding="utf-8") as f:
            json.dump(natures_dict, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved {len(natures_dict)} natures to {NATURES_FILE}")
    logger.info("Done!")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    asyncio.run(get_natures(save_to_file=True))
