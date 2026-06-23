from typing import Any
"""Script to fetch ability data from PokeAPI and save to abilities.json."""

import asyncio
import json
import logging
import os
import sqlite3
from contextlib import closing
from pathlib import Path

import httpx

from configs import ABILITIES_FILE, GRADEX_DB_PATH, REVOMON_FILE, UNKNOWN_ABILITIES_FILE

logger = logging.getLogger(__name__)


def remove_key_recursive(obj: Any, key_to_remove: Any) -> None:
    if isinstance(obj, dict):
        keys = list(obj.keys())
        for k in keys:
            if k == key_to_remove:
                del obj[k]
            else:
                remove_key_recursive(obj[k], key_to_remove)
    elif isinstance(obj, list):
        for item in obj:
            remove_key_recursive(item, key_to_remove)


def process_string(s: Any) -> Any:
    if not isinstance(s, str):
        return s
    # Replace newline characters with space
    s = s.replace("\n", " ")
    # Replace smart quotes with straight quotes
    s = s.replace("’", "'")
    s = s.replace("‘", "'")
    s = s.replace("“", '"')
    s = s.replace("”", '"')
    return s


def traverse(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: traverse(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [traverse(x) for x in obj]
    elif isinstance(obj, str):
        return process_string(obj)
    else:
        return obj


# Limit concurrency to avoid 429s
CONCURRENCY_LIMIT = 10


async def fetch_ability(
    client: httpx.AsyncClient,
    semaphore: asyncio.Semaphore,
    ability: str,
    ability_to_revomon: dict[str, Any],
) -> Any:
    """Fetch a single ability from PokeAPI and process it."""
    async with semaphore:
        url = f"https://pokeapi.co/api/v2/ability/{ability}"
        try:
            response = await client.get(url, timeout=30)
            if response.status_code == 200:
                ability_data = response.json()

                # Filter for English only
                if "effect_entries" in ability_data:
                    ability_data["effect_entries"] = [
                        e
                        for e in ability_data["effect_entries"]
                        if e.get("language", {}).get("name") == "en"
                    ]
                if "flavor_text_entries" in ability_data:
                    en_entries = [
                        e
                        for e in ability_data["flavor_text_entries"]
                        if e.get("language", {}).get("name") == "en"
                    ]
                    if en_entries:
                        target_entry = en_entries[-1]
                        ability_data["flavor_text_entries"] = [
                            {"flavor_text": target_entry["flavor_text"]}
                        ]
                    else:
                        ability_data["flavor_text_entries"] = []

                # Remove unwanted fields
                if "generation" in ability_data:
                    del ability_data["generation"]
                if "is_main_series" in ability_data:
                    del ability_data["is_main_series"]
                if "names" in ability_data:
                    ability_data["names"] = [
                        e
                        for e in ability_data["names"]
                        if e.get("language", {}).get("name") == "en"
                    ]
                    for n in ability_data["names"]:
                        if "name" in n:
                            n["name"] = n["name"].lower()

                # Filter effect_changes (nested effect_entries)
                if "effect_changes" in ability_data:
                    for change in ability_data["effect_changes"]:
                        if "effect_entries" in change:
                            change["effect_entries"] = [
                                e
                                for e in change["effect_entries"]
                                if e.get("language", {}).get("name") == "en"
                            ]

                # Replace the pokemon list with our Revomon data
                ability_name_key = ability_data["name"]
                if ability_name_key in ability_to_revomon:
                    ability_data["pokemon"] = ability_to_revomon[ability_name_key]
                else:
                    ability_data["pokemon"] = []

                return ("found", ability_data)
            elif response.status_code == 404:
                return ("unknown", ability)
            else:
                logger.warning(f"  HTTP Error {response.status_code} for {ability}.")
                return ("unknown", ability)

        except httpx.HTTPError as e:
            logger.error(f"  HTTP error fetching {ability}: {e}")
            return ("unknown", ability)
        except Exception as e:
            logger.error(f"  Unexpected error fetching {ability}: {e}")
            return ("unknown", ability)


async def get_abilities() -> None:
    logger.info(f"Reading {REVOMON_FILE}...")
    if not os.path.exists(REVOMON_FILE):
        logger.error(
            f"{REVOMON_FILE} not found. Please run 'scripts/revomon.py' script first."
        )
        raise FileNotFoundError(
            f"{REVOMON_FILE} not found. Please run 'scripts/revomon.py' script first."
        )

    with open(REVOMON_FILE, encoding="utf-8") as f:
        revomons = json.load(f)
    logger.info(f"Found {len(revomons)} revomons.")

    # Build mapping of ability to revomons
    ability_to_revomon: dict[str, Any] = {}
    for r in revomons:
        revomon_name = r.get("name")
        id_revomon = r.get("idRevomon") or r.get("mon_id")

        abilities_mapping = [
            ("ability1", 1, False),
            ("ability2", 2, False),
            ("abilityHidden", 3, True),
        ]

        for field, slot, is_hidden in abilities_mapping:
            ability_name = r.get(field)
            if ability_name:
                normalized_name = ability_name.strip().lower().replace(" ", "-")
                if normalized_name not in ability_to_revomon:
                    ability_to_revomon[normalized_name] = []

                ability_to_revomon[normalized_name].append(
                    {
                        "is_hidden": is_hidden,
                        "monster": {
                            "name": revomon_name,
                            "url": f"https://api.revomon.io/revomon/{id_revomon}/",
                        },
                        "slot": slot,
                    }
                )

    unique_abilities = sorted(list(ability_to_revomon.keys()))
    logger.info(f"Found {len(unique_abilities)} unique abilities in revomon.json.")

    found_abilities = []
    unknown_abilities = []

    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
    async with httpx.AsyncClient(timeout=30) as client:
        tasks = [
            fetch_ability(client, semaphore, ability, ability_to_revomon)
            for ability in unique_abilities
        ]
        results = await asyncio.gather(*tasks)

        for res_type, res_val in results:
            if res_type == "found":
                found_abilities.append(res_val)
            else:
                unknown_abilities.append(res_val)

    # Sort found abilities by name to be safe
    found_abilities.sort(key=lambda x: x["name"])

    # Assign sequential ID to the 'id' field and create dict
    abilities_dict = {}
    for i, ability_data in enumerate(found_abilities, start=1):
        ability_data["id"] = i
        abilities_dict[str(i)] = ability_data

    # Remove all "language" fields
    logger.info("Removing all 'language' fields...")
    remove_key_recursive(abilities_dict, "language")

    # Remove all "version_group" fields
    logger.info("Removing all 'version_group' fields...")
    remove_key_recursive(abilities_dict, "version_group")

    # Remove all "names" fields
    logger.info("Removing all 'names' fields...")
    remove_key_recursive(abilities_dict, "names")

    # Clean up strings (newlines and quotes)
    logger.info("Cleaning up strings...")
    abilities_dict = traverse(abilities_dict)

    # Ensure output directory exists
    os.makedirs(os.path.dirname(ABILITIES_FILE), exist_ok=True)

    # Convert to string and replace references
    logger.info(f"Processing text replacements and saving to {ABILITIES_FILE}...")
    json_str = json.dumps(abilities_dict, indent=2, ensure_ascii=False)

    json_str = json_str.replace("Pokémon", "Monster")
    json_str = json_str.replace("Pokemon", "Monster")
    json_str = json_str.replace("pokemon", "monster")

    with open(ABILITIES_FILE, "w", encoding="utf-8") as f:
        f.write(json_str)

    logger.info(
        f"Saving {len(unknown_abilities)} unknown abilities to {UNKNOWN_ABILITIES_FILE}..."
    )
    with open(UNKNOWN_ABILITIES_FILE, "w", encoding="utf-8") as f:
        json.dump(unknown_abilities, f, indent=2)

    logger.info("Done!")


class AbilitiesTable:
    """Class to interact with the abilities table in the Gradex SQLite database."""

    def __init__(self) -> None:
        """Initialize with the path to the SQLite database."""
        db_path: Path = GRADEX_DB_PATH
        self.db_path = db_path

    def build(self) -> None:
        """Build the abilities table in the Gradex SQLite database."""
        # Create the abilities table if it doesn't exist
        self.create()
        # Rebuild the abilities table
        self.rebuild()
        # Count the entries in the abilities table
        self.count_entries()

    def _connect(self) -> Any:
        """Private method to establish a connection to the SQLite database."""
        return sqlite3.connect(self.db_path)

    def create(self) -> None:
        """Create the abilities table if it does not already exist."""
        # Connect to the database and create a cursor
        with closing(self._connect()) as conn, conn:
            cursor = conn.cursor()

            # Drop the abilities table if it already exists
            print("Dropping abilities table if it already exists...")
            conn.execute("DROP TABLE IF EXISTS abilities;")
            print("Abilities table dropped.")

            print("Creating abilities table...")
            # Create the abilities table if it doesn't exist
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS "abilities" (
                    "name" TEXT NOT NULL UNIQUE,
                    "description" TEXT NOT NULL UNIQUE,
                    PRIMARY KEY("name")
                ) STRICT;
                """
            )
            print("natures table created successfully")
            conn.commit()

    def rebuild(self) -> None:
        """Fetch data from abilities_data.py and insert it into the database."""
        print("Rebuilding abilities table...")
        # Connect to the database and create a cursor
        with closing(self._connect()) as conn, conn:
            cursor = conn.cursor()

            # load and clean the abilities.json file
            with open("./data/abilities.json") as file:
                abilities_db = json.load(file)

            # Insert data into the database
            for ability in sorted(abilities_db, key=lambda x: x["name"]):
                # Prepare data for insertion
                name = ability["name"].lower()
                description = ability["description"].lower()

                # Execute the insert query
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO abilities
                        (name, description)
                        VALUES (?, ?);
                    """,
                    (name, description),
                )

            # Commit the transaction
            conn.commit()
            print("abilities table updated successfully!")

        # Export the abilities table to a JSON file
        self.export_to_json()

    def export_to_json(self) -> None:
        """Export data from the abilities table to a JSON file."""
        json_file_path = "./data/abilities.json"
        with closing(self._connect()) as conn, conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM abilities;")
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
        """Return the number of entries in the abilities table."""
        print("Counting entries in the abilities table...")
        with closing(self._connect()) as conn, conn:
            cursor = conn.cursor()

            # Execute the query and fetch the result
            cursor.execute("SELECT COUNT(*) FROM abilities;")
            count = cursor.fetchone()[0]

            # Close the connection

            # Print the result
            print(f"Number of Abilities in the abilities table: {count}")

            # Return the count
            return count

    def add_ability(self, name: str, description: str) -> None:
        """Add an ability to the abilities table."""
        with closing(self._connect()) as conn, conn:
            cursor = conn.cursor()

            # Prepare data for insertion
            name = name.lower()
            description = description.lower()

            # Execute the insert query
            cursor.execute(
                """
                INSERT INTO abilities
                    (name, description)
                    VALUES (?, ?);
                """,
                (name, description),
            )

            # Commit the transaction
            conn.commit()

            # Close the connection

    def get_info(self, ability_name: str) -> list[Any]:
        """Fetches information for an ability by name from the abilities table.

        Args:
            ability_name (str): The name of the ability to search for.

        Returns:
            A list of rows containing the information of matching abilities entries.
        """
        with closing(self._connect()) as conn, conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM abilities WHERE name LIKE ?",
                (f"%{ability_name}%",),
            )
            rows = cursor.fetchall()
            return rows  # type: ignore[no-any-return]

    def get_names(self) -> list[str]:
        """Retrieve a list of all ability names from the abilities table."""
        with closing(self._connect()) as conn, conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM abilities")
            rows = cursor.fetchall()
            return [row[0] for row in rows]


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    asyncio.run(get_abilities())
