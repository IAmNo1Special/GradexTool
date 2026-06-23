from typing import Any
"""Script to extract evolution data from revomon.json and save to evolutions.json."""

import json
import logging
import os

from configs import EVOLUTIONS_FILE, REVOMON_FILE

logger = logging.getLogger(__name__)


def get_evolutions(save_to_file: bool = False) -> dict:  # type: ignore[type-arg]
    if not REVOMON_FILE.exists():
        logger.error(
            f"{REVOMON_FILE} not found. Please run 'scripts/revomon.py' script first."
        )
        raise FileNotFoundError(
            f"{REVOMON_FILE} not found. Please run 'scripts/revomon.py' script first."
        )

    logger.info(f"Reading {REVOMON_FILE}...")
    with open(REVOMON_FILE, encoding="utf-8") as f:
        revomons = json.load(f)

    # Build a name -> revomon lookup for resolving evolution targets
    {r["name"]: r for r in revomons}

    evolutions_list = []

    for revomon in revomons:
        name = revomon.get("name", "")
        evolution = revomon.get("evolution", "")
        level = revomon.get("levelEvolution")

        if evolution:
            evolutions_list.append(
                {
                    "from": name,
                    "to": evolution,
                    "level": level,
                    "final": False,
                }
            )
        else:
            # No evolution
            evolutions_list.append(
                {
                    "from": name,
                    "to": None,
                    "level": None,
                    "final": True,
                }
            )

    # Sort alphabetically by "from" name
    evolutions_list.sort(key=lambda x: x["from"])

    # Assign sequential IDs and build dict
    evolutions_dict = {}
    for i, entry in enumerate(evolutions_list, start=1):
        entry["idEvolution"] = i
        evolutions_dict[str(i)] = entry

    if save_to_file:
        logger.info(
            f"Saving {len(evolutions_dict)} evolution entries to {EVOLUTIONS_FILE}..."
        )
        os.makedirs(EVOLUTIONS_FILE.parent, exist_ok=True)
        with open(EVOLUTIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(evolutions_dict, f, indent=2, ensure_ascii=False)

    logger.info("Done!")
    return evolutions_dict


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    get_evolutions(save_to_file=True)
