from typing import Any
import asyncio
import logging

from abilities import get_abilities
from base_types import get_base_types
from capsules import get_capsules
from evolutions import get_evolutions
from fruitys import get_fruitys
from gradexDB import update_gradex_db
from items import get_items
from medicines import get_medicines
from movepools import get_movepools
from moves import get_moves
from natures import get_natures
from revomon import get_revomon_data
from type_charts import get_type_charts

from configs.logging_config import setup_logging

logger = setup_logging("gradex_tool.scripts")


async def build_data(
    save_to_file: bool = True,
    download_images: bool = True,
    process_caught_revomon: bool = False,
) -> None:
    logger.info("=== STARTING DATA BUILD ===\n")
    await get_revomon_data(download_images=download_images)
    get_evolutions(save_to_file=save_to_file)
    await get_base_types(save_to_file=save_to_file, download_images=download_images)
    await get_abilities()
    await get_natures(save_to_file=save_to_file)
    await get_movepools(save_to_file=save_to_file)
    await get_moves(save_to_file=save_to_file)
    await get_type_charts(generate_images=True)
    await get_medicines()
    get_capsules()
    get_fruitys()
    get_items()
    await update_gradex_db()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    asyncio.run(build_data())
