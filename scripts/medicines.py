from typing import Any
"""Script to fetch medicine/potion data from PokeAPI and save to potions.json."""

import asyncio
import json
import logging
import os
from pathlib import Path

import httpx
from helpers import to_sentence_case

logger = logging.getLogger(__name__)


# Medicine category ID in PokeAPI is 26
POKEAPI_MEDICINE_CATEGORY = "https://pokeapi.co/api/v2/item-category/26"
POKEAPI_ITEM_BASE = "https://pokeapi.co/api/v2/item"
MEDICINES_FILE = Path("data", "medicines.json")

# Limit concurrency to avoid 429s
CONCURRENCY_LIMIT = 10


async def fetch_url(client: httpx.AsyncClient, url: str) -> dict[str, Any] | None:
    """Fetch JSON data from a URL."""
    try:
        response = await client.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()  # type: ignore[no-any-return]
        return None
    except httpx.HTTPError as e:
        logger.error(f"  HTTP error fetching {url}: {e}")
        return None
    except Exception as e:
        logger.error(f"  Unexpected error fetching {url}: {e}")
        return None


def process_string(text: str) -> str:
    """Clean up a string: replace newlines with spaces, normalize quotes."""
    if not text:
        return text
    text = text.replace("\n", " ").replace("\r", " ")
    text = text.replace("\u2018", "'").replace("\u2019", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = text.replace("Pokémon", "Revomon").replace("Pokemon", "Revomon")
    while "  " in text:
        text = text.replace("  ", " ")
    return text.strip()


async def get_medicine_categories(client: httpx.AsyncClient) -> list[dict[str, Any]]:
    """Get all medicine sub-categories from PokeAPI."""
    category_ids = [27, 28, 29, 30, 42, 43]
    all_items = []
    for cat_id in category_ids:
        url = f"https://pokeapi.co/api/v2/item-category/{cat_id}"
        logger.info(f"  Fetching category {cat_id}...")
        cat_data = await fetch_url(client, url)
        if cat_data:
            items = cat_data.get("items", [])
            cat_name = cat_data.get("name", "unknown")
            for item in items:
                all_items.append(
                    {
                        "name": item["name"],
                        "url": item["url"],
                        "category": cat_name,
                    }
                )
            logger.info(f"    Found {len(items)} items in '{cat_name}'")
    return all_items


async def process_item(
    semaphore: asyncio.Semaphore,
    client: httpx.AsyncClient,
    item_ref: dict[str, Any],
    potions_list: list[dict[str, Any]],
) -> None:
    """Fetch and process a single item with concurrency limit."""
    name = item_ref["name"]
    category = item_ref["category"]

    async with semaphore:
        logger.info(f"  Fetching '{name}'...")
        item_data = await fetch_url(client, item_ref["url"])
        if not item_data:
            logger.error(f"  Failed to fetch '{name}', skipping.")
            return

        effect = ""
        short_effect = ""
        for entry in item_data.get("effect_entries", []):
            if entry.get("language", {}).get("name") == "en":
                effect = process_string(entry.get("effect", ""))
                short_effect = process_string(entry.get("short_effect", ""))
                break

        flavor_text = ""
        en_flavor_entries = [
            ft
            for ft in item_data.get("flavor_text_entries", [])
            if ft.get("language", {}).get("name") == "en"
        ]
        if en_flavor_entries:
            flavor_text = process_string(en_flavor_entries[-1].get("text", ""))

        potion_entry = {
            "name": name.lower(),
            "category": category.lower(),
            "cost": item_data.get("cost"),
            "effect": to_sentence_case(effect) if effect else "",
            "short_effect": to_sentence_case(short_effect) if short_effect else "",
            "flavor_text": to_sentence_case(flavor_text) if flavor_text else "",
        }
        potions_list.append(potion_entry)


async def get_medicines() -> None:

    logger.info("Fetching medicine categories from PokeAPI...")
    async with httpx.AsyncClient(timeout=10) as client:
        medicine_items = await get_medicine_categories(client)
        logger.info(
            f"Found {len(medicine_items)} total medicine items. Fetching details..."
        )

        potions_list: list[dict[str, Any]] = []
        semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
        tasks = [
            process_item(semaphore, client, item_ref, potions_list)
            for item_ref in medicine_items
        ]
        await asyncio.gather(*tasks)

    # Sort alphabetically by name
    potions_list.sort(key=lambda x: x["name"])

    # Assign sequential IDs and build dict
    potions_dict = {}
    for i, potion in enumerate(potions_list, start=1):
        potion["idPotion"] = i
        potions_dict[str(i)] = potion

    logger.info(f"Saving {len(potions_dict)} potions/medicine to {MEDICINES_FILE}...")
    os.makedirs(MEDICINES_FILE.parent, exist_ok=True)
    with open(MEDICINES_FILE, "w", encoding="utf-8") as f:
        json.dump(potions_dict, f, indent=2, ensure_ascii=False)

    logger.info("Done!")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    asyncio.run(get_medicines())
