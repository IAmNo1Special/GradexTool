from typing import Any

"""Script to process fruity data from source fruitys.json and save to gradex fruitys.json."""

import json  # noqa: E402
import logging  # noqa: E402
import os  # noqa: E402
import sqlite3  # noqa: E402
from contextlib import closing  # noqa: E402
from pathlib import Path  # noqa: E402

from helpers import to_sentence_case  # noqa: E402

from configs import GRADEX_DB_PATH  # noqa: E402

db_path: Path = GRADEX_DB_PATH

logger = logging.getLogger(__name__)


OUTPUT_PATH = Path("data/fruitys.json")
FRUITYS = [
    {
        "name": "barka",
        "description": "consumed when struck by a super-effective toxic-type attack to halve the damage.",
        "type": "held",
    },
    {
        "name": "cassius",
        "description": "consumed at 1/2 max hp to recover 1/4 max hp.",
        "type": "held",
    },
    {
        "name": "chamo",
        "description": "consumed when struck by a super-effective spirit-type attack to halve the damage.",
        "type": "held",
    },
    {
        "name": "choda",
        "description": "consumed when struck by a super-effective sky-type attack to halve the damage.",
        "type": "held",
    },
    {
        "name": "cozi",
        "description": "consumed at 1/4 max hp when using a move to go first.",
        "type": "held",
    },
    {
        "name": "dabip",
        "description": "consumed when struck by a super-effective electric-type attack to halve the damage.",
        "type": "held",
    },
    {
        "name": "defo",
        "description": "consumed at 1/2 max hp to restore 1/8 max hp. confuses revomon that dislike bitter flavor.",
        "type": "held",
    },
    {
        "name": "derlu",
        "description": "drops special attack effort values by 10 and raises happiness.",
        "type": "ev",
    },
    {
        "name": "ebla",
        "description": "consumed at 1/2 max hp to restore 1/8 max hp. confuses revomon that dislike sweet flavor.",
        "type": "held",
    },
    {
        "name": "ertha",
        "description": "when the holder is hit by a special move, increases it's special defense by one stage.",
        "type": "held",
    },
    {
        "name": "frin",
        "description": "consumed when struck by a super-effective draconic-type attack to halve the damage.",
        "type": "held",
    },
    {
        "name": "frizy",
        "description": "consumed to deal 1/8 attacker's max hp when holder is struck by a special attack.",
        "type": "held",
    },
    {
        "name": "glandu",
        "description": "consumed at 1/4 max hp to boost defense.",
        "type": "held",
    },
    {
        "name": "globop",
        "description": "consumed when struck by a super-effective attack to restore 1/4 max hp.",
        "type": "held",
    },
    {
        "name": "golmon",
        "description": "consumed when struck by a super-effective time-type attack to halve the damage.",
        "type": "held",
    },
    {
        "name": "golu",
        "description": "consumed when frozen to cure frozen.",
        "type": "held",
    },
    {
        "name": "gunko",
        "description": "consumed when struck by a super-effective fire-type attack to halve the damage.",
        "type": "held",
    },
    {
        "name": "gupon",
        "description": "consumed when struck by a super-effective ice-type attack to halve the damage.",
        "type": "held",
    },
    {
        "name": "inchu",
        "description": "consumed at 1/2 max hp to restore 1/8 max hp. confuses revomon that dislike spicy flavor.",
        "type": "held",
    },
    {
        "name": "iota",
        "description": "consumed at 1/4 max hp to boost attack.",
        "type": "held",
    },
    {
        "name": "issou",
        "description": "drops speed effort values by 10 and raises happiness.",
        "type": "ev",
    },
    {
        "name": "jadwa",
        "description": "consumed when confused to cure confusion.",
        "type": "held",
    },
    {
        "name": "juiti",
        "description": "consumed when paralyzed to cure paralysis.",
        "type": "held",
    },
    {
        "name": "kanda",
        "description": "consumed when a move runs out of pp to restore it's pp by 10.",
        "type": "held",
    },
    {
        "name": "kankoo",
        "description": "drops attack effort values by 10 and raises happiness.",
        "type": "ev",
    },
    {
        "name": "karoto",
        "description": "drops hp effort values by 10 and raises happiness.",
        "type": "ev",
    },
    {
        "name": "lee",
        "description": "when the holder is hit by a physical move, increases it's defense by one stage.",
        "type": "held",
    },
    {
        "name": "liech",
        "description": "consumed at 1/4 max hp to boost special attack.",
        "type": "held",
    },
    {
        "name": "miopi",
        "description": "consumed at 1/4 max hp to boost a random stat by two stages.",
        "type": "held",
    },
    {
        "name": "mitsi",
        "description": "consumed at 1/4 max hp to boost accuracy of next move by 20%.",
        "type": "held",
    },
    {
        "name": "nonomi",
        "description": "consumed when struck by a super-effective stone-type attack to halve the damage.",
        "type": "held",
    },
    {
        "name": "osef",
        "description": "consumed when asleep to cure sleep.",
        "type": "held",
    },
    {
        "name": "paia",
        "description": "consumed at 1/2 max hp to restore 1/8 max hp. confuses revomon that dislike sour flavor.",
        "type": "held",
    },
    {
        "name": "papille",
        "description": "drops defense effort values by 10 and raises happiness.",
        "type": "ev",
    },
    {
        "name": "papou",
        "description": "consumed at 1/4 max hp to boost critical hit ratio by two stages.",
        "type": "held",
    },
    {
        "name": "peachu",
        "description": "consumed when toxiced to cure toxic.",
        "type": "held",
    },
    {
        "name": "pritcha",
        "description": "consumed when struck by a super-effective metal-type attack to halve the damage.",
        "type": "held",
    },
    {
        "name": "psiro",
        "description": "consumed when struck by a super-effective battle-type attack to halve the damage.",
        "type": "held",
    },
    {
        "name": "ruka",
        "description": "consumed when struck by a super-effective earth-type attack to halve the damage.",
        "type": "held",
    },
    {
        "name": "tavaa",
        "description": "consumed when struck by a super-effective bug-type attack to halve the damage.",
        "type": "held",
    },
    {
        "name": "terter",
        "description": "consumed when struck by a super-effective forest-type attack to halve the damage.",
        "type": "held",
    },
    {
        "name": "tibli",
        "description": "consumed at 1/2 max hp to restore 1/8 max hp. confuses revomon that dislike dry flavor.",
        "type": "held",
    },
    {
        "name": "tipli",
        "description": "consumed when struck by a super-effective phantom-type attack to halve the damage.",
        "type": "held",
    },
    {
        "name": "toktok",
        "description": "consumed at 1/4 max hp to boost special defense.",
        "type": "held",
    },
    {
        "name": "trars",
        "description": "consumed when struck by a super-effective twilight-type attack to halve the damage.",
        "type": "held",
    },
    {
        "name": "trigo",
        "description": "consumed at 1/4 max hp to boost speed.",
        "type": "held",
    },
    {
        "name": "truduku",
        "description": "consumed when struck by a super-effective water-type attack to halve the damage.",
        "type": "held",
    },
    {
        "name": "vilvi",
        "description": "consumed to cure any status condition or confusion.",
        "type": "held",
    },
    {
        "name": "vrio",
        "description": "consumed at 1/2 max hp to recover 10 hp.",
        "type": "held",
    },
    {
        "name": "wilso",
        "description": "drops special defense effort values by 10 and raises happiness.",
        "type": "ev",
    },
    {
        "name": "wiltu",
        "description": "consumed when burned to cure a burn.",
        "type": "held",
    },
    {
        "name": "yannoi",
        "description": "consumed to deal 1/8 attacker's max hp when holder is struck by a physical attack.",
        "type": "held",
    },
    {
        "name": "yululu",
        "description": "consumed when struck by a neutral-type attack to halve the damage.",
        "type": "held",
    },
]


def get_fruitys() -> None:
    fruitys = FRUITYS.copy()
    logger.info(f"Found {len(fruitys)} fruitys. Processing...")

    # Process each fruity
    for fruity in fruitys:
        # Lowercase name
        if "name" in fruity and fruity["name"] is not None:
            fruity["name"] = fruity["name"].lower()
        # Lowercase type
        if "type" in fruity and fruity["type"] is not None:
            fruity["type"] = fruity["type"].lower()
        # Sentence case description
        if "description" in fruity and fruity["description"] is not None:
            fruity["description"] = to_sentence_case(fruity["description"])

    # Sort alphabetically by name
    fruitys.sort(key=lambda x: x.get("name", ""))

    # Assign sequential IDs and build dict
    fruitys_dict = {}
    for i, fruity in enumerate(fruitys, start=1):
        fruity["idFruity"] = i  # type: ignore[assignment]
        fruitys_dict[str(i)] = fruity

    logger.info(f"Saving {len(fruitys_dict)} fruitys to {OUTPUT_PATH}...")
    os.makedirs(OUTPUT_PATH.parent, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(fruitys_dict, f, indent=2, ensure_ascii=False)

    logger.info("Done!")


class FruitysTable:
    """Class to interact with the fruitys table in the Gradex SQLite database."""

    def __init__(self) -> None:
        """Initialize with the path to the SQLite database."""
        self.db_path = db_path

    def build(self) -> None:
        """Build the fruitys table."""
        # Create the fruitys table if it doesn't exist
        self.create()
        # Rebuild the fruitys table
        self.rebuild()
        # Count the entries in the fruitys table
        self.count_entries()

    def _connect(self) -> Any:
        """Private method to establish a connection to the SQLite database."""
        return sqlite3.connect(self.db_path)

    def create(self) -> None:
        """Create the fruitys table if it does not already exist."""
        # Connect to the database and create a cursor
        with closing(self._connect()) as conn, conn:
            cursor = conn.cursor()

            # Drop the fruitys table if it already exists
            print("Dropping fruitys table if it already exists...")
            conn.execute("DROP TABLE IF EXISTS fruitys;")
            print("Fruitys table dropped.")

            print("Creating fruitys table...")
            # Create the fruitys table if it doesn't exist
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS "fruitys" (
                    "name" TEXT NOT NULL UNIQUE,
                    "description" TEXT NOT NULL UNIQUE,
                    "type" TEXT NOT NULL,
                    PRIMARY KEY("name")
                ) STRICT;
                """
            )
            print("fruitys table created successfully")
            conn.commit()

    def rebuild(self) -> None:
        """Fetch data from fruitys_data.py and insert it into the database."""
        print("Rebuilding fruitys table...")

        # Connect to the database and create a cursor
        with closing(self._connect()) as conn, conn:
            cursor = conn.cursor()

            # load and clean the fruitys.json file
            with open("./data/fruitys.json") as file:
                fruitys_db = json.load(file)

            # Insert data into the database
            for fruity in sorted(fruitys_db, key=lambda x: x["name"]):
                # Prepare data for insertion
                name = fruity["name"].lower()
                description = fruity["description"].lower()
                type = fruity["type"]

                # Execute the insert query
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO fruitys
                        (name, description, type)
                        VALUES (?, ?, ?);
                    """,
                    (name, description, type),
                )

            # Commit the transaction
            conn.commit()
        print("fruityss table updated successfully!")

        # Export the fruitys table to a JSON file
        self.export_to_json()

    def export_to_json(self) -> None:
        """Export data from the fruitys table to a JSON file."""
        json_file_path = "./data/fruitys.json"
        with closing(self._connect()) as conn, conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM fruitys;")
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
        """Return the number of entries in the fruitys table."""
        print("Counting entries in the fruitys table...")

        # Connect to the database and create a cursor
        with closing(self._connect()) as conn, conn:
            cursor = conn.cursor()

            # Execute the query and fetch the result
            cursor.execute("SELECT COUNT(*) FROM fruitys;")
            count = cursor.fetchone()[0]

            # Close the connection

            # Print the result
            print(f"Number of Fruitys in the fruitys table: {count}")

            # Return the count
            return count

    def add_fruity(self, name: str, description: str, type: str) -> None:
        """Add a new fruity entry to the fruitss table in the SQLite database.

        Args:
            name (str): The name of the fruity.
            description (str): The description of the fruity.
            type (str): The type of the fruity.

        """
        with closing(self._connect()) as conn, conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT OR REPLACE INTO fruitys
                    (name, description, type)
                    VALUES (?, ?, ?);
                """,
                (name, description, type),
            )
            conn.commit()

    def get_info(self, fruity_name: str) -> list:  # type: ignore[type-arg]
        """Method to search the fruitys table by name and return hhe info of the matching entry."""
        with closing(self._connect()) as conn, conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM fruitys WHERE name LIKE ?", (f"%{fruity_name}%",)
            )
            rows = cursor.fetchall()
            return rows  # type: ignore[no-any-return]

    def get_type(self, fruity_name: str) -> str:
        """Get the type of a fruity by name."""
        with closing(self._connect()) as conn, conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT type FROM fruitys WHERE name LIKE ?",
                (f"%{fruity_name}%",),
            )
            rows = cursor.fetchall()
            return rows[0][0]  # type: ignore[no-any-return]

    def get_names(self) -> list:  # type: ignore[type-arg]
        """Method to get a list of all the names of the fruitys in the fruitys table."""
        with closing(self._connect()) as conn, conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM fruitys")
            rows = cursor.fetchall()
            return [row[0] for row in rows]


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    get_fruitys()
