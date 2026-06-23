from typing import Any
"""Script to process type data from source types.json and save to gradex types.json.

Also downloads type images from the Revomon CDN.
"""

import asyncio
import json
import logging
import os

import httpx

from configs import (
    BASE_TYPES_FILE,
    BASE_TYPES_IMAGES_DIR,
    REVOMON_BASE_TYPES_IMAGE_ENDPOINT,
    REVOMON_FILE,
)

logger = logging.getLogger(__name__)


def save_base_types_file(base_type_names: list[str]) -> None:
    """Save base type names to BASE_TYPES_FILE."""
    logger.info(f"Saving {len(base_type_names)} types to {BASE_TYPES_FILE}...")
    os.makedirs(BASE_TYPES_FILE.parent, exist_ok=True)
    with open(BASE_TYPES_FILE, "w", encoding="utf-8") as f:
        json.dump(base_type_names, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved {len(base_type_names)} types to {BASE_TYPES_FILE}")


async def download_base_type_images(
    client: httpx.AsyncClient,
    base_type_name: str,
) -> bool:
    """Download a base type image for the give base type name."""
    semaphore = asyncio.Semaphore(10)
    async with semaphore:
        try:
            save_path = BASE_TYPES_IMAGES_DIR / f"{base_type_name}.png"
            save_path.parent.mkdir(parents=True, exist_ok=True)
            img_url = f"{REVOMON_BASE_TYPES_IMAGE_ENDPOINT}/{base_type_name}.png"
            response = await client.get(img_url, timeout=30)
            if response.status_code == 200:
                with open(save_path, "wb") as f:
                    f.write(response.content)
                return True
            return False
        except httpx.HTTPError as e:
            logger.error(
                f"  HTTP error downloading type image for {base_type_name}: {e}"
            )
            return False
        except Exception as e:
            logger.error(
                f"  Unexpected error downloading type image for {base_type_name}: {e}"
            )
            return False


async def get_base_types(
    save_to_file: bool = False, download_images: bool = False
) -> list[str]:
    """Get a list of names of each unique base type for all Revomon in REVOMON_FILE and optionally save them to BASE_TYPES_FILE."""
    with open(REVOMON_FILE, encoding="utf-8") as f:
        revomon_data = json.load(f)

    base_types = set()
    for revomon in revomon_data:
        if revomon["type1"] is not None:
            base_types.add(revomon["type1"].lower())
        if revomon["type2"] is not None:
            base_types.add(revomon["type2"].lower())
    base_type_names = sorted(base_types)
    if save_to_file:
        save_base_types_file(base_type_names)
    # Download base type images if requested
    if download_images:
        logger.info(f"Downloading base type images for {len(base_type_names)} types...")
        async with httpx.AsyncClient(timeout=30) as client:
            tasks = []
            for base_type_name in base_type_names:
                tasks.append(download_base_type_images(client, base_type_name))

            results = await asyncio.gather(*tasks)
            logger.info(f"Downloaded {sum(results)}/{len(results)} base type images.")
    return base_type_names


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    asyncio.run(get_base_types(save_to_file=True, download_images=True))
