import json
import logging
import os
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Any

import requests
from revomon import RevomonTable

from configs import GRADEX_DB_PATH

logger = logging.getLogger(__name__)


db_path: Path = GRADEX_DB_PATH


def get_capsules() -> None:
    moves_path = Path("data", "moves.json")
    output_path = Path("data", "capsules.json")

    if not moves_path.exists():
        logger.info(f"{moves_path} not found. Falling back to generating it...")
        # Import and run moves.py to generate moves.json
        from scripts.gradex.moves import main as build_moves_data

        build_moves_data()

    logger.info(f"Reading {moves_path}...")
    with open(moves_path, encoding="utf-8") as f:
        moves_data = json.load(f)

    capsules_list = []

    for move in moves_data:
        capsule = move.get("capsule") if move.get("capsule") is not None else move.get("cap_num")
        id_move = move.get("idMove") if move.get("idMove") is not None else move.get("id")
        move_name = move.get("name", "")
        if capsule is not None and id_move is not None:
            capsules_list.append(
                {
                    "name": f"capsule {capsule}",
                    "description": f"teaches {move_name}"
                }
            )

    # Sort by capsule name
    sorted_capsules = sorted(capsules_list, key=lambda x: x["name"])

    logger.info(f"Saving {len(sorted_capsules)} capsules to {output_path}...")
    os.makedirs(output_path.parent, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(sorted_capsules, f, indent=2, ensure_ascii=False)

    logger.info("Done!")


class CapsulesTable:
    """Class to interact with the capsules table in the Gradex SQLite database."""

    def __init__(self) -> None:
        """Initialize with the path to the SQLite database."""
        self.db_path = db_path

    async def build(self) -> None:
        """Build the capsules table."""
        # Create the capsules table if it doesn't exist
        self.create()
        # Rebuild the capsules table
        await self.rebuild()
        # Count the entries in the capsules table
        self.count_entries()

    def _connect(self) -> Any:
        """Private method to establish a connection to the SQLite database."""
        return sqlite3.connect(self.db_path)

    def create(self) -> None:
        """Create the capsules table if it does not already exist."""
        # Connect to the database and create a cursor
        with closing(self._connect()) as conn, conn:
            cursor = conn.cursor()

            # Drop the capsules table if it already exists
            print("Dropping capsules table if it already exists...")
            conn.execute("DROP TABLE IF EXISTS capsules;")
            print("Capsules table dropped.")

            print("Creating capsules table...")
            # Create the capsules table if it doesn't exist
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS "capsules" (
                    "cap_num" INTEGER NOT NULL UNIQUE,
                    "move_id" INTEGER NOT NULL UNIQUE,
                    "move_name" TEXT NOT NULL UNIQUE,
                    PRIMARY KEY("cap_num")
                ) STRICT;
                """
            )
            print("capsules table created successfully")
            conn.commit()

    async def rebuild(self) -> None:
        """Fetch data from the Revomon Moves API and insert it into the database."""
        print("Rebuilding capsules table...")

        # get a list of all the mon_ids in the revomon table
        mon_ids = RevomonTable().get_mon_ids()

        # Fetch data from the Revomon Moves API
        for mon_id in mon_ids:
            url = f"https://api.revomon.io/revomon/moves/{mon_id}"
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()

                # Connect to the database and create a cursor
                with closing(self._connect()) as conn, conn:
                    cursor = conn.cursor()

                    # Insert data into the database
                    for move in sorted(
                        data["data"]["moves"], key=lambda x: x["idMove"]
                    ):
                        if move["capsule"]:
                            # Prepare data for insertion
                            cap_num = move["capsule"]
                            move_id = move["idMove"]
                            move_name = move["name"].lower()

                            # Execute the insert query
                            cursor.execute(
                                """
                                INSERT OR IGNORE INTO capsules
                                    (cap_num, move_id, move_name)
                                    VALUES (?, ?, ?);
                                """,
                                (cap_num, move_id, move_name),
                            )

                            # Check if the row was inserted
                            if (
                                cursor.rowcount == 0
                            ):  # If the row was not inserted, it means it already exists
                                continue
                            else:
                                print(f"Added capsule: {move['capsule']}")
                        else:
                            continue

                    # Commit the transaction
                    conn.commit()
        print("capsules table updated successfully!")

        # Export the capsules table to a JSON file
        self.export_to_json()

    def export_to_json(self) -> None:
        """Export data from the capsules table to a JSON file."""
        json_file_path = "./data/capsules.json"
        with closing(self._connect()) as conn, conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM capsules;")
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
        """Return the number of entries in the capsules table."""
        print("Counting entries in the capsules table...")
        with closing(self._connect()) as conn, conn:
            cursor = conn.cursor()

            # Execute the query and fetch the result
            cursor.execute("SELECT COUNT(*) FROM capsules;")
            count = cursor.fetchone()[0]

            # Close the connection

            # Print the result
            print(f"Number of Capsules in the capsules table: {count}")

            # Return the count
            return count

    def add_capsule(self, cap_num: int, move_id: int, move_name: str) -> None:
        """Add a new Capsule entry to the capsules table in the SQLite database.

        Args:
            cap_num (int): The capsule number.
            move_id (int): The move ID.
            move_name (str): The name of the move.

        """
        with closing(self._connect()) as conn, conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO capsules
                    (cap_num, move_id, move_name)
                    VALUES (?, ?, ?);
                """,
                (cap_num, move_id, move_name),
            )
            conn.commit()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    get_capsules()
