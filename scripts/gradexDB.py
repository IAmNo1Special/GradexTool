import json  # noqa: N999
import time
from pathlib import Path
from typing import Any

import aiosqlite
import requests
from aiosqlite.core import Connection


def safe_get(url: str, timeout: int=10, retries: int=5, backoff_factor: float=1.0) -> Any:
    """Fetch a URL with timeout, retries, rate-limit awareness, and exponential backoff."""
    for i in range(retries):
        try:
            response = requests.get(url, timeout=timeout)
            if response.status_code == 200:
                return response

            # Handle rate limiting (429) specifically
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 5))
                print(
                    f"Rate limited (429) on {url}. Sleeping for {retry_after} seconds..."
                )
                time.sleep(retry_after)
                continue

            print(
                f"Failed to fetch {url}: HTTP status {response.status_code}. Retrying ({i + 1}/{retries})..."
            )
        except requests.RequestException as e:
            print(f"Failed to fetch {url}: {e}. Retrying ({i + 1}/{retries})...")
        if i < retries - 1:
            time.sleep(backoff_factor * (2**i))
    return None


def safe_post(url: str, json_payload: dict[str, list[Any]], timeout: int=15, retries: int=3, backoff_factor: float=1.0) -> Any:
    """Post to a URL with timeout, retries, and exponential backoff."""
    for i in range(retries):
        try:
            response = requests.post(url, json=json_payload, timeout=timeout)
            if response.status_code == 200:
                return response
            print(
                f"Failed to post to {url}: HTTP status {response.status_code}. Retrying ({i + 1}/{retries})..."
            )
        except requests.RequestException as e:
            print(f"Failed to post to {url}: {e}. Retrying ({i + 1}/{retries})...")
        if i < retries - 1:
            time.sleep(backoff_factor * (2**i))
    return None


from configs import GRADEX_DB_PATH  # noqa: E402
from utils.land_utils import get_lands_for_sale_amount  # noqa: E402

db_path: Path = GRADEX_DB_PATH


class CounterdexTable:
    """Class to interact with the counterdex table in the Gradex SQLite database."""

    def __init__(self) -> None:
        """Initialize with the path to the SQLite database."""
        self.db_path = db_path

    async def build(self) -> None:
        """Build the counterdex table."""
        # Create the counterdex table if it doesn't exist
        await self.create()
        # Rebuild the counterdex table
        await self.rebuild()
        # Count the entries in the counterdex table
        await self.count_entries()

    def _connect(self) -> Connection:
        """Private method to establish a connection to the SQLite database."""
        return aiosqlite.connect(self.db_path, isolation_level=None)

    async def create(self) -> None:
        """Create the counterdex table if it does not already exist."""
        print("Creating counterdex table...")

        # Connect to the database and create a cursor
        async with self._connect() as conn:
            cursor = await conn.cursor()

            # Drop the counterdex table if it already exists
            print("Dropping counterdex table if it already exists...")
            await conn.execute("DROP TABLE IF EXISTS counterdex;")
            print("Counterdex table dropped.")

            # Create the counterdex table if it doesn't exist
            await cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS "counterdex" (
                    "dex_id" INTEGER NOT NULL UNIQUE,
                    "mon_id" INTEGER NOT NULL UNIQUE,
                    "name" TEXT NOT NULL UNIQUE,
                    "description" TEXT,
                    "tier" TEXT,
                    "metamoves" TEXT,
                    "metabuilds" TEXT,
                    "tips" TEXT,
                    "counters" TEXT,
                    "weakness" TEXT,
                    PRIMARY KEY("dex_id")
                ) STRICT;
                """
            )
            print("Counterdex table created successfully")
            await conn.commit()

    async def rebuild(self) -> None:
        """Fetch data from the Revomon API and insert it into the database."""
        print("Rebuilding counterdex table...")
        # Fetch data from the Revomon API
        url = "https://api.revomon.io/revomon/revodex"
        payload: Any = {"idsCatchedRevomon": []}
        response = safe_post(url, payload)

        # Connect to the database and create a cursor
        async with self._connect() as conn:
            cursor = await conn.cursor()

            if response and response.status_code == 200:
                data = response.json()
                print(f"Number of Revomons fetched: {len(data['data']['revomons'])}")

                with open("./data/counterdex.json") as f:
                    cdex_data = json.load(f)

                # Insert data into the database
                for revomon in sorted(
                    data["data"]["revomons"], key=lambda x: x["idRevodex"]
                ):
                    # Prepare data for insertion
                    dex_id = revomon["idRevodex"]
                    mon_id = revomon["idRevomon"]
                    name = revomon["name"].lower()
                    description = None
                    tier = None
                    metamoves = None
                    metabuilds = None
                    tips = None
                    counters = None
                    weakness = None
                    for cdex_mon in cdex_data:
                        if cdex_mon["name"].lower() == name:
                            description = (
                                cdex_mon["description"].lower()
                                if cdex_mon["description"]
                                else None
                            )
                            tier = (
                                cdex_mon["tier"].lower() if cdex_mon["tier"] else None
                            )
                            metamoves = (
                                cdex_mon["metamoves"].lower()
                                if cdex_mon["metamoves"]
                                else None
                            )
                            metabuilds = (
                                cdex_mon["metabuilds"].lower()
                                if cdex_mon["metabuilds"]
                                else None
                            )
                            tips = (
                                cdex_mon["tips"].lower() if cdex_mon["tips"] else None
                            )
                            counters = (
                                cdex_mon["counters"].lower()
                                if cdex_mon["counters"]
                                else None
                            )
                            weakness = (
                                cdex_mon["weakness"].lower()
                                if cdex_mon["weakness"]
                                else None
                            )

                    # Execute the insert query
                    await cursor.execute(
                        """
                        INSERT OR REPLACE INTO counterdex
                            (dex_id, mon_id,name, description, tier, metamoves, metabuilds, tips, counters, weakness)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                        """,
                        (
                            dex_id,
                            mon_id,
                            name,
                            description,
                            tier,
                            metamoves,
                            metabuilds,
                            tips,
                            counters,
                            weakness,
                        ),
                    )

                # Commit the transaction
                await conn.commit()

        print("Counterdex table updated successfully!")

        # Export data from the counterdex table to a JSON file
        await self.export_to_json()

    async def export_to_json(self) -> None:
        """Export data from the counterdex table to a JSON file."""
        json_file_path = "./data/counterdex.json"
        async with self._connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute("SELECT * FROM counterdex;")
            rows = await cursor.fetchall()

            # Get column names
            column_names = [description[0] for description in cursor.description]

            # Convert rows to a list of dictionaries
            data = [dict(zip(column_names, row)) for row in rows]

            # Write to JSON file
            with open(json_file_path, "w") as json_file:
                json.dump(data, json_file, indent=4)

            print(f"Data exported to {json_file_path}.")

    async def count_entries(self) -> int:
        """Return the number of entries in the counterdex table."""
        print("Counting entries in the counterdex table...")
        async with self._connect() as conn:
            cursor = await conn.cursor()

            # Execute the query and fetch the result
            await cursor.execute("SELECT COUNT(*) FROM counterdex;")
            count = int((await cursor.fetchone())[0])  # type: ignore

        # Print the result
        print(f"Number of Entries in the counterdex table: {count}")

        # Return the count
        return count

    async def add_revomon(
        self,
        dex_id: int,
        mon_id: int,
        name: str,
        description: str,
        tier: str,
        metamoves: str,
        metabuilds: str,
        tips: str,
        counters: str,
    ) -> None:
        """Add a new Revomon entry to the counterdex table in the SQLite database.

        Args:
            dex_id: The Revomon's dex ID.
            mon_id: The Revomon's mon ID.
            name: The Revomon's name.
            description: The Revomon's description.
            tier: The Revomon's tier.
            metamoves: The Revomon's metamoves.
            metabuilds: The Revomon's metabuilds.
            tips: The Revomon's tips.
            counters: The Revomon's counters.
        """
        async with self._connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute(
                """
                INSERT OR REPLACE INTO counterdex
                    (dex_id, mon_id,name, description, tier, metamoves, metabuilds, tips, counters)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    dex_id,
                    mon_id,
                    name,
                    description,
                    tier,
                    metamoves,
                    metabuilds,
                    tips,
                    counters,
                ),
            )
            await conn.commit()

    async def get_info(self, revomon_name: str) -> Any:
        """Method to search the counterdex table by revomon name and return the info of the closest matching revomon."""
        async with self._connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute(
                "SELECT * FROM counterdex WHERE name LIKE ?",
                (f"%{revomon_name}%",),
            )
            rows = await cursor.fetchall()
            return rows


class AbilitiesTable:
    """Class to interact with the abilities table in the Gradex SQLite database."""

    def __init__(self) -> None:
        """Initialize with the path to the SQLite database."""
        self.db_path = db_path

    async def build(self) -> None:
        """Build the abilities table in the Gradex SQLite database."""
        # Create the abilities table if it doesn't exist
        await self.create()
        # Rebuild the abilities table
        await self.rebuild()
        # Count the entries in the abilities table
        await self.count_entries()

    def _connect(self) -> Connection:
        """Private method to establish a connection to the SQLite database."""
        return aiosqlite.connect(self.db_path, isolation_level=None)

    async def create(self) -> None:
        """Create the abilities table if it does not already exist."""
        print("Creating abilities table...")

        # Connect to the database and create a cursor
        async with self._connect() as conn:
            cursor = await conn.cursor()

            # Drop the abilities table if it already exists
            print("Dropping abilities table if it already exists...")
            await conn.execute("DROP TABLE IF EXISTS abilities;")
            print("Abilities table dropped.")

            # Create the abilities table if it doesn't exist
            await cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS "abilities" (
                    "id" INTEGER NOT NULL UNIQUE,
                    "name" TEXT NOT NULL UNIQUE,
                    "description" TEXT,
                    PRIMARY KEY("id")
                ) STRICT;
                """
            )
            print("Abilities table created successfully")
            await conn.commit()

    async def rebuild(self) -> None:
        """Fetch data from abilities.json and insert it into the database."""
        print("Rebuilding abilities table...")
        # Connect to the database and create a cursor
        async with self._connect() as conn:
            cursor = await conn.cursor()

            # Define the insert query for the abilities table
            insert_query = """
                INSERT OR REPLACE INTO abilities
                (id, name, description)
                VALUES (?, ?, ?);
            """

            # load the abilities.json file
            with open("./data/abilities.json") as file:
                abilities_data = json.load(file)

            # Insert data into the database
            # abilities_data can be a dict (from PokeAPI) or a list (from DB export)
            if isinstance(abilities_data, dict):
                ability_list = list(abilities_data.values())
            else:
                ability_list = abilities_data

            for ability in sorted(ability_list, key=lambda x: x["id"]):
                # Prepare data for insertion
                ability_id = ability["id"]
                name = ability["name"].lower()

                # Support both PokeAPI format and DB export format
                description = ability.get("description")
                if not description:
                    if (
                        ability.get("effect_entries")
                        and len(ability["effect_entries"]) > 0
                    ):
                        description = (
                            ability["effect_entries"][0].get("short_effect", "").lower()
                        )
                    elif (
                        ability.get("flavor_text_entries")
                        and len(ability["flavor_text_entries"]) > 0
                    ):
                        description = (
                            ability["flavor_text_entries"][0]
                            .get("flavor_text", "")
                            .lower()
                        )

                # Execute the insert query
                await cursor.execute(insert_query, (ability_id, name, description))

            # Commit the transaction
            await conn.commit()

        print("Abilities table updated successfully!")

        # Export data from the abilities table to a JSON file
        await self.export_to_json()

    async def export_to_json(self) -> None:
        """Export data from the abilities table to a JSON file."""
        json_file_path = "./data/abilities.json"
        async with self._connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute("SELECT * FROM abilities;")
            rows = await cursor.fetchall()

            # Get column names
            column_names = [description[0] for description in cursor.description]

            # Convert rows to a list of dictionaries
            data = [dict(zip(column_names, row)) for row in rows]

            # Write to JSON file
            with open(json_file_path, "w") as json_file:
                json.dump(data, json_file, indent=4)

            print(f"Data exported to {json_file_path}.")

    async def count_entries(self) -> int:
        """Return the number of entries in the abilities table."""
        print("Counting entries in the abilities table...")
        async with self._connect() as conn:
            cursor = await conn.cursor()

            # Execute the query and fetch the result
            await cursor.execute("SELECT COUNT(*) FROM abilities;")
            count = int((await cursor.fetchone())[0])  # type: ignore

        # Print the result
        print(f"Number of Entries in the abilities table: {count}")

        # Return the count
        return count


class CapsulesTable:
    """Class to interact with the capsules table in the Gradex SQLite database."""

    def __init__(self) -> None:
        """Initialize with the path to the SQLite database."""
        self.db_path = db_path

    async def build(self) -> None:
        """Build the capsules table in the Gradex SQLite database."""
        # Create the capsules table if it doesn't exist
        await self.create()
        # Rebuild the capsules table
        await self.rebuild()
        # Count the entries in the capsules table
        await self.count_entries()

    def _connect(self) -> Connection:
        """Private method to establish a connection to the SQLite database."""
        return aiosqlite.connect(self.db_path, isolation_level=None)

    async def create(self) -> None:
        """Create the capsules table if it does not already exist."""
        print("Creating capsules table...")

        # Connect to the database and create a cursor
        async with self._connect() as conn:
            cursor = await conn.cursor()

            # Drop the capsules table if it already exists
            print("Dropping capsules table if it already exists...")
            await conn.execute("DROP TABLE IF EXISTS capsules;")
            print("Capsules table dropped.")

            # Create the capsules table if it doesn't exist
            await cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS "capsules" (
                    "name" TEXT NOT NULL UNIQUE,
                    "description" TEXT,
                    PRIMARY KEY("name")
                ) STRICT;
                """
            )
            print("Capsules table created successfully")
            await conn.commit()

    async def rebuild(self) -> None:
        """Fetch data from capsules.json and insert it into the database."""
        print("Rebuilding capsules table...")
        # Connect to the database and create a cursor
        async with self._connect() as conn:
            cursor = await conn.cursor()

            # Define the insert query for the capsules table
            insert_query = """
                INSERT OR REPLACE INTO capsules
                (name, description)
                VALUES (?, ?);
            """

            # load the capsules.json file
            with open("./data/capsules.json") as file:
                capsules_data = json.load(file)

            # Insert data into the database
            for capsule in sorted(capsules_data, key=lambda x: x.get("name", "")):
                # Prepare data for insertion
                name = capsule.get("name", "").lower() if capsule.get("name") else None
                description = (
                    capsule.get("description", "").lower()
                    if capsule.get("description")
                    else None
                )

                # Execute the insert query
                await cursor.execute(insert_query, (name, description))

            # Commit the transaction
            await conn.commit()

        print("Capsules table updated successfully!")

        # Export data from the capsules table to a JSON file
        await self.export_to_json()

    async def export_to_json(self) -> None:
        """Export data from the capsules table to a JSON file."""
        json_file_path = "./data/capsules.json"
        async with self._connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute("SELECT * FROM capsules;")
            rows = await cursor.fetchall()

            # Get column names
            column_names = [description[0] for description in cursor.description]

            # Convert rows to a list of dictionaries
            data = [dict(zip(column_names, row)) for row in rows]

            # Write to JSON file
            with open(json_file_path, "w") as json_file:
                json.dump(data, json_file, indent=4)

            print(f"Data exported to {json_file_path}.")

    async def count_entries(self) -> int:
        """Return the number of entries in the capsules table."""
        print("Counting entries in the capsules table...")
        async with self._connect() as conn:
            cursor = await conn.cursor()

            # Execute the query and fetch the result
            await cursor.execute("SELECT COUNT(*) FROM capsules;")
            count = int((await cursor.fetchone())[0])  # type: ignore

        # Print the result
        print(f"Number of Entries in the capsules table: {count}")

        # Return the count
        return count


class FruitysTable:
    """Class to interact with the fruitys table in the Gradex SQLite database."""

    def __init__(self) -> None:
        """Initialize with the path to the SQLite database."""
        self.db_path = db_path

    async def build(self) -> None:
        """Build the fruitys table in the Gradex SQLite database."""
        # Create the fruitys table if it doesn't exist
        await self.create()
        # Rebuild the fruitys table
        await self.rebuild()
        # Count the entries in the fruitys table
        await self.count_entries()

    def _connect(self) -> Connection:
        """Private method to establish a connection to the SQLite database."""
        return aiosqlite.connect(self.db_path, isolation_level=None)

    async def create(self) -> None:
        """Create the fruitys table if it does not already exist."""
        print("Creating fruitys table...")

        # Connect to the database and create a cursor
        async with self._connect() as conn:
            cursor = await conn.cursor()

            # Drop the fruitys table if it already exists
            print("Dropping fruitys table if it already exists...")
            await conn.execute("DROP TABLE IF EXISTS fruitys;")
            print("Fruitys table dropped.")

            # Create the fruitys table if it doesn't exist
            await cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS "fruitys" (
                    "id" INTEGER NOT NULL UNIQUE,
                    "name" TEXT NOT NULL UNIQUE,
                    "description" TEXT,
                    "type" TEXT,
                    PRIMARY KEY("id")
                ) STRICT;
                """
            )
            print("Fruitys table created successfully")
            await conn.commit()

    async def rebuild(self) -> None:
        """Fetch data from fruitys.json and insert it into the database."""
        print("Rebuilding fruitys table...")
        # Connect to the database and create a cursor
        async with self._connect() as conn:
            cursor = await conn.cursor()

            # Define the insert query for the fruitys table
            insert_query = """
                INSERT OR REPLACE INTO fruitys
                (id, name, description, type)
                VALUES (?, ?, ?, ?);
            """

            # load the fruitys.json file
            with open("./data/fruitys.json") as file:
                fruitys_data = json.load(file)

            # Insert data into the database
            # fruitys_data can be a dict (from API) or a list (from DB export)
            if isinstance(fruitys_data, dict):
                fruity_list = list(fruitys_data.values())
            else:
                fruity_list = fruitys_data

            for fruity in sorted(
                fruity_list, key=lambda x: x.get("idFruity") or x.get("id")
            ):
                # Prepare data for insertion
                fruity_id = fruity.get("idFruity") or fruity.get("id")
                name = fruity["name"].lower()
                description = (
                    fruity.get("description", "").lower()
                    if fruity.get("description")
                    else None
                )
                fruity_type = (
                    fruity.get("type", "").lower() if fruity.get("type") else None
                )

                # Execute the insert query
                await cursor.execute(
                    insert_query, (fruity_id, name, description, fruity_type)
                )

            # Commit the transaction
            await conn.commit()

        print("Fruitys table updated successfully!")

        # Export data from the fruitys table to a JSON file
        await self.export_to_json()

    async def export_to_json(self) -> None:
        """Export data from the fruitys table to a JSON file."""
        json_file_path = "./data/fruitys.json"
        async with self._connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute("SELECT * FROM fruitys;")
            rows = await cursor.fetchall()

            # Get column names
            column_names = [description[0] for description in cursor.description]

            # Convert rows to a list of dictionaries
            data = [dict(zip(column_names, row)) for row in rows]

            # Write to JSON file
            with open(json_file_path, "w") as json_file:
                json.dump(data, json_file, indent=4)

            print(f"Data exported to {json_file_path}.")

    async def count_entries(self) -> int:
        """Return the number of entries in the fruitys table."""
        print("Counting entries in the fruitys table...")
        async with self._connect() as conn:
            cursor = await conn.cursor()

            # Execute the query and fetch the result
            await cursor.execute("SELECT COUNT(*) FROM fruitys;")
            count = int((await cursor.fetchone())[0])  # type: ignore

        # Print the result
        print(f"Number of Entries in the fruitys table: {count}")

        # Return the count
        return count


class ItemsTable:
    """Class to interact with the items table in the Gradex SQLite database."""

    def __init__(self) -> None:
        """Initialize with the path to the SQLite database."""
        self.db_path = db_path

    async def build(self) -> None:
        """Build the items table in the Gradex SQLite database."""
        # Create the items table if it doesn't exist
        await self.create()
        # Rebuild the items table
        await self.rebuild()
        # Count the entries in the items table
        await self.count_entries()

    def _connect(self) -> Connection:
        """Private method to establish a connection to the SQLite database."""
        return aiosqlite.connect(self.db_path, isolation_level=None)

    async def create(self) -> None:
        """Create the items table if it does not already exist."""
        # Connect to the database and create a cursor
        async with self._connect() as conn:
            cursor = await conn.cursor()

            # Drop the items table if it already exists
            print("Dropping items table if it already exists...")
            await conn.execute("DROP TABLE IF EXISTS items;")
            print("Items table dropped.")

            print("Creating items table...")
            # Create the items table if it doesn't exist
            create_table_query = """

                CREATE TABLE IF NOT EXISTS "items" (
                    "name" TEXT NOT NULL UNIQUE,
                    "description" TEXT NOT NULL UNIQUE,
                    "obtained_from" TEXT NOT NULL,
                    "cost" INTEGER,
                    PRIMARY KEY("name")
                ) STRICT;
            """
            await cursor.execute(create_table_query)
            print("Items table created successfully")
            await conn.commit()

    async def export_to_json(self) -> None:
        """Export data from the items table to a JSON file."""
        json_file_path = "./data/items.json"
        async with self._connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute("SELECT * FROM items;")
            rows = await cursor.fetchall()

            # Get column names
            column_names = [description[0] for description in cursor.description]

            # Convert rows to a list of dictionaries
            data = [dict(zip(column_names, row)) for row in rows]

            # Write to JSON file
            with open(json_file_path, "w") as json_file:
                json.dump(data, json_file, indent=4)

            print(f"Data exported to {json_file_path}.")

    async def rebuild(self) -> None:
        """Fetch data from items_data.py and insert it into the database."""
        print("Rebuilding items table...")
        # Connect to the database and create a cursor
        async with self._connect() as conn:
            cursor = await conn.cursor()

            # Define the insert query for the items table
            insert_query = """
                INSERT OR REPLACE INTO items
                (name, description, obtained_from, cost)
                VALUES (?, ?, ?, ?);
            """

            # load and clean the items.json file
            with open("./data/items.json") as file:
                items = json.load(file)

            # Insert data into the database
            # items can be a dict (from API/configs) or a list (from DB export)
            if isinstance(items, dict):
                item_list = list(items.values())
            else:
                item_list = items

            for item in sorted(item_list, key=lambda x: x["name"]):
                # Prepare data for insertion
                name = item["name"].lower()
                description = item["description"].lower()
                obtained_from = item["obtained_from"].lower()
                cost = item["cost"] if item["cost"] else None

                # Execute the insert query
                await cursor.execute(insert_query, (name, description, obtained_from, cost))

            # Commit the transaction
            await conn.commit()
        print("items table updated successfully!")

        # Export the items table to a JSON file
        await self.export_to_json()

    async def count_entries(self) -> int:
        """Return the number of entries in the items table."""
        print("Counting entries in the items table...")
        async with self._connect() as conn:
            cursor = await conn.cursor()

            # Define the query to count the number of entries in the items table
            count_query = "SELECT COUNT(*) FROM items;"

            # Execute the query and fetch the result
            await cursor.execute(count_query)
            count = int((await cursor.fetchone())[0])  # type: ignore

            # Close the connection

            # Print the result
            print(f"Number of Items in the items table: {count}")

            # Return the count
            return count

    async def add_item(self, name: str, description: str, obtained_from: str, cost: int) -> None:
        """Add an Item to the items table."""
        async with self._connect() as conn:
            cursor = await conn.cursor()

            # Define the insert query for the items table
            insert_query = """
                INSERT INTO items
                (name, description, obtained_from, cost)
                VALUES (?, ?, ?, ?);
            """

            # Prepare data for insertion
            name = name.lower()
            description = description.lower()
            obtained_from = obtained_from.lower()

            # Execute the insert query
            await cursor.execute(insert_query, (name, description, obtained_from, cost))

            # Commit the transaction
            await conn.commit()

            # Close the connection

    async def get_info(self, item_name: str) -> Any:
        """Method to search the items table by item name and return the info of the closest matching item."""
        async with self._connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute("SELECT * FROM items WHERE name LIKE ?", (f"%{item_name}%",))
            rows = await cursor.fetchall()
            return rows

    async def get_names(self) -> Any:
        """Method to get a list of all the names of the items in the items table."""
        async with self._connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute("SELECT name FROM items")
            rows = await cursor.fetchall()
            return [row[0] for row in rows]


class MovesTable:
    """Class to interact with the moves table in the Gradex SQLite database."""

    def __init__(self) -> None:
        """Initialize with the path to the SQLite database."""
        self.db_path = db_path

    async def build(self) -> None:
        """Build the moves table by creating, rebuilding, and counting entries."""
        # Create the moves table if it doesn't exist
        await self.create()
        # Rebuild the moves table
        await self.rebuild()
        # Count the entries in the moves table
        await self.count_entries()

    def _connect(self) -> Connection:
        """Private method to establish a connection to the SQLite database."""
        return aiosqlite.connect(self.db_path, isolation_level=None)

    async def create(self) -> None:
        """Create the moves table if it does not already exist."""
        # Connect to the database and create a cursor
        async with self._connect() as conn:
            cursor = await conn.cursor()

            # Drop the moves table if it already exists
            print("Dropping moves table if it already exists...")
            await conn.execute("DROP TABLE IF EXISTS moves;")
            print("moves table dropped.")

            print("Creating moves table...")
            # Create the moves table if it doesn't exist
            create_table_query = """
                CREATE TABLE IF NOT EXISTS "moves" (
                    "id" INTEGER NOT NULL UNIQUE PRIMARY KEY,
                    "cap_num" INTEGER UNIQUE,
                    "name" TEXT NOT NULL UNIQUE,
                    "category" TEXT NOT NULL,
                    "type" TEXT NOT NULL,
                    "description" TEXT NOT NULL UNIQUE,
                    "accuracy" REAL NOT NULL,
                    "power" INTEGER NOT NULL,
                    "pp" INTEGER NOT NULL,
                    "priority" INTEGER NOT NULL
                ) STRICT;
            """
            await cursor.execute(create_table_query)
            print("moves table created successfully")
            await conn.commit()

    async def rebuild(self) -> None:
        """Fetch data from moves.json or the Revomon Moves API and insert it into the database."""
        print("Rebuilding moves table...")

        moves_file_path = Path("./data/moves.json")
        has_local_data = False
        moves_data = []

        import os
        if "PYTEST_CURRENT_TEST" not in os.environ and moves_file_path.exists() and moves_file_path.stat().st_size > 10:
            try:
                with open(moves_file_path, encoding="utf-8") as file:
                    moves_data = json.load(file)
                if moves_data:
                    has_local_data = True
                    print(f"Loaded {len(moves_data)} moves from local moves.json")
            except Exception as e:
                print(f"Failed to load local moves.json: {e}")

        # Connect to the database and create a cursor
        async with self._connect() as conn:
            cursor = await conn.cursor()

            # Define the insert query for the moves table
            insert_query = """
                INSERT OR IGNORE INTO moves
                (id, cap_num, name, category, type,
                description, accuracy, power, pp, priority)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """

            if has_local_data:
                # Insert data from local moves.json
                for move in sorted(
                    moves_data, key=lambda x: x.get("id") or x.get("idMove", 0)
                ):
                    move_id = move.get("id") or move.get("idMove")
                    cap_num = move.get("cap_num") or move.get("capsule")
                    name = move["name"].lower()
                    category = move["category"].lower()
                    move_type = move["type"].lower()
                    description = move["description"].lower()
                    accuracy = move.get("accuracy")
                    power = move.get("power")
                    pp = move.get("pp")
                    priority = move.get("priority")

                    await cursor.execute(
                        insert_query,
                        (
                            move_id,
                            cap_num,
                            name,
                            category,
                            move_type,
                            description,
                            accuracy,
                            power,
                            pp,
                            priority,
                        ),
                    )
                await conn.commit()
            else:
                # Fetch data from the Revomon Moves API
                mon_ids = await RevomonTable().get_mon_ids()
                for mon_id in mon_ids:
                    url = f"https://api.revomon.io/revomon/moves/{mon_id}"
                    response = safe_get(url)
                    time.sleep(0.2)  # Delay to respect API rate limits

                    if response and response.status_code == 200:
                        data = response.json()
                        for move in sorted(
                            data["data"]["moves"], key=lambda x: x["idMove"]
                        ):
                            move_id = move["idMove"]
                            cap_num = move["capsule"]
                            name = move["name"].lower()
                            category = move["category"].lower()
                            move_type = move["type"].lower()
                            description = move["description"].lower()
                            accuracy = move["accuracy"]
                            power = move["power"]
                            pp = move["pp"]
                            priority = move["priority"]

                            await cursor.execute(
                                insert_query,
                                (
                                    move_id,
                                    cap_num,
                                    name,
                                    category,
                                    move_type,
                                    description,
                                    accuracy,
                                    power,
                                    pp,
                                    priority,
                                ),
                            )
                        await conn.commit()
        print("moves table updated successfully!")

        # Export the moves table to a JSON file
        await self.export_to_json()

    async def export_to_json(self) -> None:
        """Export data from the moves table to a JSON file."""
        json_file_path = "./data/moves.json"
        async with self._connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute("SELECT * FROM moves;")
            rows = await cursor.fetchall()

            # Get column names
            column_names = [description[0] for description in cursor.description]

            # Convert rows to a list of dictionaries
            data = [dict(zip(column_names, row)) for row in rows]

            # Write to JSON file
            with open(json_file_path, "w") as json_file:
                json.dump(data, json_file, indent=4)

            print(f"Data exported to {json_file_path}.")

    async def count_entries(self) -> int:
        """Return the number of entries in the moves table."""
        print("Counting entries in the moves table...")
        async with self._connect() as conn:
            cursor = await conn.cursor()

            # Define the query to count the number of entries in the moves table
            count_query = "SELECT COUNT(*) FROM moves;"

            # Execute the query and fetch the result
            await cursor.execute(count_query)
            count = int((await cursor.fetchone())[0])  # type: ignore

            # Print the result
            print(f"Number of Moves in the moves table: {count}")

            # Return the count
            return count

    async def add_move(
        self,
        move_id: int,
        cap_num: int | None,
        name: str,
        category: str,
        move_type: str,
        description: str,
        accuracy: float,
        power: int,
        pp: int,
        priority: int,
    ) -> None:
        """Add a new Move entry to the moves table in the SQLite database.

        Args:
            move_id (int): The move ID.
            cap_num (int): The capsule number.
            name (str): The name of the move.
            category (str): The category of the move.
            move_type (str): The type of the move.
            description (str): The description of the move.
            accuracy (float): The accuracy of the move.
            power (int): The power of the move.
            pp (int): The PP of the move.
            priority (int): The priority of the move.
        """
        async with self._connect() as conn:
            cursor = await conn.cursor()
            insert_query = """INSERT OR REPLACE INTO moves
                        (id, cap_num, name, category, type,
                        description, accuracy, power, pp, priority)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""
            # Execute the insert query
            await cursor.execute(
                insert_query,
                (
                    move_id,
                    cap_num,
                    name,
                    category,
                    move_type,
                    description,
                    accuracy,
                    power,
                    pp,
                    priority,
                ),
            )
            await conn.commit()

    async def get_info(self, move_name: str) -> Any:
        """Fetches information for a move by name from the moves table.

        Args:
            move_name (str): The name of the move to search for.

        Returns:
            A list of rows containing the information of matching moves entries.
        """
        async with self._connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute(
                "SELECT * FROM moves WHERE name LIKE ?",
                (f"%{move_name.lower()}%",),
            )
            rows = await cursor.fetchall()
            return rows

    async def get_names(self) -> Any:
        """Method to get a list of all the names of the moves in the moves table."""
        async with self._connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute("SELECT name FROM moves")
            rows = await cursor.fetchall()
            return [row[0] for row in rows]


class NaturesTable:
    """Class to interact with the natures table in the Gradex SQLite database."""

    def __init__(self) -> None:
        """Initialize with the path to the SQLite database."""
        self.db_path = db_path

    async def build(self) -> None:
        """Build the natures table by creating, rebuilding, and counting entries."""
        # Create the natures table if it doesn't exist
        await self.create()
        # Rebuild the natures table
        await self.rebuild()
        # Count the entries in the natures table
        await self.count_entries()

    def _connect(self) -> Connection:
        """Private method to establish a connection to the SQLite database."""
        return aiosqlite.connect(self.db_path, isolation_level=None)

    async def create(self) -> None:
        """Create the natures table if it does not already exist."""
        # Connect to the database and create a cursor
        async with self._connect() as conn:
            cursor = await conn.cursor()

            # Drop the nature table if it already exists
            print("Dropping natures table if it already exists...")
            await conn.execute("DROP TABLE IF EXISTS natures;")
            print("Natures table dropped.")

            print("Creating natures table...")
            # Create the natures table if it doesn't exist
            create_table_query = """

                CREATE TABLE IF NOT EXISTS "natures" (
                    "name" TEXT NOT NULL UNIQUE,
                    "buffs" TEXT,
                    "debuffs" TEXT,
                    "likes" TEXT,
                    "dislikes" TEXT,
                    PRIMARY KEY("name")
                ) STRICT;
            """
            await cursor.execute(create_table_query)
            print("natures table created successfully")
            await conn.commit()

    async def rebuild(self) -> None:
        """Fetch data from natures_data.py and insert it into the database."""
        print("Rebuilding natures table...")
        # Connect to the database and create a cursor
        async with self._connect() as conn:
            cursor = await conn.cursor()

            # Define the insert query for the natures table
            insert_query = """
                INSERT OR REPLACE INTO natures
                (name, buffs, debuffs, likes, dislikes)
                VALUES (?, ?, ?, ?, ?);
            """

            # load and clean the natures.json file
            with open("./data/natures.json") as file:
                natures = json.load(file)

            # Insert data into the database
            # natures can be a dict (from PokeAPI natures.py fetch) or a list (from DB export)
            if isinstance(natures, dict):
                nature_list = list(natures.values())
            else:
                nature_list = natures

            for nature in sorted(nature_list, key=lambda x: x["name"]):
                # Prepare data for insertion
                name = nature["name"].lower()

                # Support both PokeAPI format ("increased_stat") and DB export format ("buffs")
                buffs_val = nature.get("increased_stat") or nature.get("buffs")
                debuffs_val = nature.get("decreased_stat") or nature.get("debuffs")

                buffs = buffs_val.lower() if buffs_val else None
                debuffs = debuffs_val.lower() if debuffs_val else None
                likes = nature.get("likes")
                dislikes = nature.get("dislikes")

                # Execute the insert query
                await cursor.execute(insert_query, (name, buffs, debuffs, likes, dislikes))

            # Commit the transaction
            await conn.commit()

        print("natures table updated successfully!")

        # Export data from the natures table to a JSON file
        await self.export_to_json()

    async def export_to_json(self) -> None:
        """Export data from the natures table to a JSON file."""
        json_file_path = "./data/natures.json"
        async with self._connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute("SELECT * FROM natures;")
            rows = await cursor.fetchall()

            # Get column names
            column_names = [description[0] for description in cursor.description]

            # Convert rows to a list of dictionaries
            data = [dict(zip(column_names, row)) for row in rows]

            # Write to JSON file
            with open(json_file_path, "w") as json_file:
                json.dump(data, json_file, indent=4)

            print(f"Data exported to {json_file_path}.")

    async def count_entries(self) -> int:
        """Return the number of entries in the natures table."""
        print("Counting entries in the natures table...")
        async with self._connect() as conn:
            cursor = await conn.cursor()

            # Define the query to count the number of entries in the revomon table
            count_query = "SELECT COUNT(*) FROM natures;"

            # Execute the query and fetch the result
            await cursor.execute(count_query)
            count = int((await cursor.fetchone())[0])  # type: ignore

            # Close the connection

            # Print the result
            print(f"Number of Natures in the natures table: {count}")

            # Return the count
            return count

    async def add_nature(
        self,
        name: str,
        buffs: str | None,
        debuffs: str | None,
        likes: str | None,
        dislikes: str | None,
    ) -> None:
        """Add a nature to the natures table."""
        async with self._connect() as conn:
            cursor = await conn.cursor()
            insert_query = "INSERT INTO natures (name, buffs, debuffs, likes, dislikes) VALUES (?, ?, ?, ?, ?);"
            await cursor.execute(insert_query, (name, buffs, debuffs, likes, dislikes))
            await conn.commit()

    async def get_info(self, nature_name: str) -> Any:
        """Method to search the natures table by nature name and return the info of the closest matching nature."""
        async with self._connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute(
                "SELECT * FROM natures WHERE name LIKE ?", (f"%{nature_name}%",)
            )
            rows = await cursor.fetchall()
            return rows

    async def get_names(self) -> Any:
        """Method to get a list of all the names of the natures in the natures table."""
        async with self._connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute("SELECT name FROM natures")
            rows = await cursor.fetchall()
            return [row[0] for row in rows]


class OwnedLandsTable:
    """Class to interact with the ownedLands Table in the Gradex SQLite database."""

    def __init__(self) -> None:
        """Initialize with the path to the SQLite database."""
        self.db_path = db_path

    async def build(self) -> None:
        """Build the ownedLands table by creating, rebuilding, and counting entries."""
        # Create the ownedLands Table if it doesn't exist
        await self.create()
        # Rebuild the ownedLands Table
        await self.rebuild()
        # Count the entries in the OwnedLands Table
        await self.count_entries()

    def _connect(self) -> Connection:
        """Private method to establish a connection to the SQLite database."""
        return aiosqlite.connect(self.db_path, isolation_level=None)

    async def create(self) -> None:
        """Create the ownedLands Table if it does not already exist."""
        print("Creating ownedLands Table...")

        # Connect to the database and create a cursor
        async with self._connect() as conn:
            cursor = await conn.cursor()

            # Drop the ownedLands Table if it already exists
            print("Dropping ownedLands Table if it already exists...")
            await conn.execute("DROP TABLE IF EXISTS ownedLands;")
            print("ownedLands Table dropped.")

            # Create the OwnedLands Table if it doesn't exist
            await cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS "ownedLands" (
                    "token_id" INTEGER NOT NULL UNIQUE,
                    "id" INTEGER NOT NULL,
                    "owners_address" TEXT NOT NULL,
                    "biome" TEXT NOT NULL,
                    "land_type" TEXT NOT NULL,
                    "rarity" TEXT NOT NULL,
                    "size" TEXT NOT NULL,
                    "img_url" TEXT NOT NULL,
                    "emoji" TEXT NOT NULL,
                    "for_sale" INTEGER NOT NULL,
                    "token_symbol" TEXT,
                    "for_sale_usd" REAL,
                    "for_sale_token" REAL,
                    PRIMARY KEY("token_id")
                ) STRICT;
                """
            )
            print("ownedLands Table created successfully")
            await conn.commit()

    async def rebuild(self) -> None:
        """Fetch land data from the Immutable zKEVM API and insert it into the database."""
        print("Rebuilding ownedLands Table...")
        from utils import emoji_utils, land_utils

        land_data = await land_utils.get_land_data()
        emoji_list = await emoji_utils.list_application_emojis()

        # Connect to the database and create a cursor
        async with self._connect() as conn:
            cursor = await conn.cursor()
            # Prepare data for insertion
            for land_obj in land_data:
                for land in land_obj["land_info"]:
                    token_id = land["token_id"]
                    id = land["id"]
                    owners_address = land_obj["owners_address"]
                    biome = land["biome"]
                    land_type = land["land_type"]
                    rarity = land["rarity"]
                    size = land["size"]
                    img_url = land["img_url"]
                    emoji_name = f"{biome}_{land_type}".replace(" ", "_")
                    if emoji_name in [emoji["name"] for emoji in emoji_list]:
                        for emoji_obj in emoji_list:
                            if emoji_name == emoji_obj["name"]:
                                emoji = emoji_obj["id"]
                                break
                    else:
                        emoji_obj = await emoji_utils.create_emoji_from_url(
                            img_url=img_url, emoji_name=emoji_name
                        )
                        emoji = emoji_obj["id"]
                        emoji_list.append(emoji_obj)
                    for_sale = 0
                    token_symbol = None
                    for_sale_usd = None
                    for_sale_token = None

                    # Execute the insert query
                    await cursor.execute(
                        """
                        INSERT OR REPLACE INTO ownedLands
                            (token_id, id, owners_address, biome, land_type, rarity, size, img_url, emoji, for_sale, token_symbol, for_sale_usd, for_sale_token)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                        """,
                        (
                            token_id,
                            id,
                            owners_address,
                            biome,
                            land_type,
                            rarity,
                            size,
                            img_url,
                            emoji,
                            for_sale,
                            token_symbol,
                            for_sale_usd,
                            for_sale_token,
                        ),
                    )

                # Commit the transaction
                await conn.commit()
        await self.update_lands_sale_data()

        print("OwnedLands Table updated successfully!")

        # Export data from the revomon table to a JSON file
        await self.export_to_json()

    async def export_to_json(self) -> None:
        """Export data from the ownedLands Table to a JSON file."""
        json_file_path = "./data/owned_lands.json"
        async with self._connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute("SELECT * FROM ownedLands;")
            rows = await cursor.fetchall()

            # Get column names
            column_names = [description[0] for description in cursor.description]

            # Convert rows to a list of dictionaries
            data = [dict(zip(column_names, row)) for row in rows]

            # Write to JSON file
            with open(json_file_path, "w") as json_file:
                json.dump(data, json_file, indent=4)

            print(f"Data exported to {json_file_path}.")

    async def count_entries(self) -> int:
        """Return the number of entries in the ownedLands Table."""
        print("Counting entries in the ownedLands Table...")
        async with self._connect() as conn:
            cursor = await conn.cursor()

            # Execute the query and fetch the result
            await cursor.execute("SELECT COUNT(*) FROM ownedLands;")
            count = int((await cursor.fetchone())[0])  # type: ignore

            # Close the connection

            # Print the result
            print(f"Number of Lands in the ownedLands Table: {count}")

            # Return the count
            return count

    async def get_info(
        self,
        token_id: Any = None,
        id: Any = None,
        owners_address: Any = None,
        biome: Any = None,
        land_type: Any = None,
        rarity: Any = None,
        size: Any = None,
        img_url: Any = None,
        sort_by: str = "token_id",
        sale_status: Any = None,
        asc: bool = True,
    ) -> Any:
        """Get land information based on provided filters."""
        async with self._connect() as conn:
            cursor = await conn.cursor()
            if True:
                await cursor.execute("SELECT * FROM ownedLands ")
            result = await cursor.fetchall()
            # if any of the arguments are provided, filter the results
            if token_id:
                result = [land for land in result if land[0] == token_id]
            if id:
                result = [land for land in result if land[1] == id]
            if owners_address:
                result = [land for land in result if land[2] == owners_address]
            if biome:
                result = [land for land in result if land[3] == biome]
            if land_type:
                result = [land for land in result if land[4] == land_type]
            if rarity:
                result = [land for land in result if land[5] == rarity]
            if size:
                result = [land for land in result if land[6] == size]
            if img_url:
                result = [land for land in result if land[7] == img_url]
            if sale_status:
                result = [land for land in result if land[9] == sale_status]
            if sort_by:
                if sort_by == "token_id":
                    result = sorted(result, key=lambda land: land[0])
                elif sort_by == "id":
                    result = sorted(result, key=lambda land: land[1])
                elif sort_by == "owners_address":
                    result = sorted(result, key=lambda land: land[2])
                elif sort_by == "biome":
                    result = sorted(result, key=lambda land: land[3])
                elif sort_by == "land_type":
                    result = sorted(result, key=lambda land: land[4])
                elif sort_by == "rarity":
                    result = sorted(result, key=lambda land: land[5])
                elif sort_by == "size":
                    result = sorted(result, key=lambda land: land[6])
                elif sort_by == "img_url":
                    result = sorted(result, key=lambda land: land[7])
                elif sort_by == "sale_status":
                    result = sorted(result, key=lambda land: land[9])
                else:
                    result = sorted(result, key=lambda land: land[0])
            # sort the result in descending order if asc is Flase
            if asc is False:
                result = sorted(result, reverse=True)
            if result == []:
                return None
            return result

    async def get_ids(self) -> Any:
        """Get all token IDs from the ownedLands table."""
        async with self._connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute("SELECT token_id FROM ownedLands;")
            ids = [land[0] for land in await cursor.fetchall()]
            return ids

    async def get_biomes(self) -> Any:
        """Get all unique biomes from the ownedLands table."""
        async with self._connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute("SELECT biome FROM ownedLands;")
            biomes = [land[0] for land in await cursor.fetchall()]
            biomes = list(set(biomes))
            return biomes

    async def get_land_types(self) -> Any:
        """Get all unique land types from the ownedLands table."""
        async with self._connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute("SELECT land_type FROM ownedLands;")
            land_types = [land[0] for land in await cursor.fetchall()]
            land_types = list(set(land_types))
            return land_types

    async def update_lands_sale_data(self) -> None:
        """Update the sale data for owned lands."""
        from data import OwnedLandsTable

        all_land_ids = await OwnedLandsTable().get_ids()
        print("Updating sale data for lands...")
        sale_data = await get_lands_for_sale_amount()
        for land_token_id in all_land_ids:
            if land_token_id in [int(id) for id in sale_data.keys()]:
                amount_data = sale_data[str(land_token_id)]
                async with self._connect() as conn:
                    cursor = await conn.cursor()
                    await cursor.execute(
                        """
                                UPDATE ownedLands
                                SET owners_address = ?,
                                for_sale = ?,
                                for_sale_token = ?,
                                token_symbol = ?,
                                for_sale_usd = ?
                                WHERE token_id = ?;
                                """,
                        (
                            amount_data["owners_address"],
                            1,
                            amount_data["for_sale_token"],
                            amount_data["token_symbol"],
                            amount_data["for_sale_usd"],
                            land_token_id,
                        ),
                    )
                    await conn.commit()
            else:
                async with self._connect() as conn:
                    cursor = await conn.cursor()
                    await cursor.execute(
                        """
                                   UPDATE ownedLands
                                   SET for_sale = 0,
                                   for_sale_token = NULL,
                                   token_symbol = NULL,
                                   for_sale_usd = NULL
                                   WHERE token_id = ?;
                                   """,
                        (land_token_id,),
                    )
                    await conn.commit()
        print("Lands sale data has been updated")


class RevomonTable:
    """Class to interact with the revomon table in the Gradex SQLite database."""

    def __init__(self) -> None:
        """Initialize with the path to the SQLite database."""
        self.db_path = db_path

    async def build(self) -> None:
        """Build the revomon table in the Gradex SQLite database."""
        # Create the revomon table if it doesn't exist
        await self.create()
        # Rebuild the revomon table
        await self.rebuild()
        # Count the entries in the revomon table
        await self.count_entries()

    def _connect(self) -> Connection:
        """Private method to establish a connection to the SQLite database."""
        return aiosqlite.connect(self.db_path, isolation_level=None)

    async def create(self) -> None:
        """Create the revomon table if it does not already exist."""
        print("Creating revomon table...")

        # Connect to the database and create a cursor
        async with self._connect() as conn:
            cursor = await conn.cursor()

            # Drop the revomon table if it already exists
            print("Dropping revomon table if it already exists...")
            await conn.execute("DROP TABLE IF EXISTS revomon;")
            print("Revomon table dropped.")

            # Create the revomon table if it doesn't exist
            await cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS "revomon" (
                    "dex_id" INTEGER NOT NULL UNIQUE,
                    "mon_id" INTEGER NOT NULL UNIQUE,
                    "name" TEXT NOT NULL UNIQUE,
                    "description" TEXT,
                    "type1" TEXT,
                    "type2" TEXT,
                    "ability1" TEXT,
                    "ability2" TEXT,
                    "ability_hidden" TEXT,
                    "hp" INTEGER,
                    "atk" INTEGER,
                    "def" INTEGER,
                    "spa" INTEGER,
                    "spd" INTEGER,
                    "spe" INTEGER,
                    "evolution" TEXT,
                    "level_evolution" INTEGER,
                    "rarity" TEXT,
                    PRIMARY KEY("dex_id")
                ) STRICT;
                """
            )
            print("Revomon table created successfully")
            await conn.commit()

    async def rebuild(self) -> None:
        """Fetch data from revomon.json and insert it into the database."""
        print("Rebuilding revomon table...")
        # Connect to the database and create a cursor
        async with self._connect() as conn:
            cursor = await conn.cursor()

            # load the revomon.json file
            with open("./data/revomon.json") as file:
                revomon_data = json.load(file)

            # Insert data into the database
            for revomon in sorted(revomon_data, key=lambda x: x["dex_id"]):
                # Prepare data for insertion
                dex_id = revomon["dex_id"]
                mon_id = revomon["mon_id"]
                name = revomon["name"].lower()
                description = (
                    revomon.get("description", "").lower()
                    if revomon.get("description")
                    else None
                )
                type1 = (
                    revomon.get("type1", "").lower() if revomon.get("type1") else None
                )
                type2 = (
                    revomon.get("type2", "").lower() if revomon.get("type2") else None
                )
                ability1 = (
                    revomon.get("ability1", "").lower()
                    if revomon.get("ability1")
                    else None
                )
                ability2 = (
                    revomon.get("ability2", "").lower()
                    if revomon.get("ability2")
                    else None
                )
                ability_hidden = (
                    revomon.get("ability_hidden", "").lower()
                    if revomon.get("ability_hidden")
                    else None
                )
                hp = revomon.get("hp")
                atk = revomon.get("atk")
                def_ = revomon.get("def")
                spa = revomon.get("spa")
                spd = revomon.get("spd")
                spe = revomon.get("spe")
                evolution = (
                    revomon.get("evolution", "").lower()
                    if revomon.get("evolution")
                    else None
                )
                level_evolution = revomon.get("level_evolution")
                rarity = (
                    revomon.get("rarity", "").lower() if revomon.get("rarity") else None
                )

                # Execute the insert query
                await cursor.execute(
                    """
                    INSERT OR REPLACE INTO revomon
                    (dex_id, mon_id, name, description, type1, type2, ability1, ability2, ability_hidden, hp, atk, def, spa, spd, spe, evolution, level_evolution, rarity)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """,
                    (
                        dex_id,
                        mon_id,
                        name,
                        description,
                        type1,
                        type2,
                        ability1,
                        ability2,
                        ability_hidden,
                        hp,
                        atk,
                        def_,
                        spa,
                        spd,
                        spe,
                        evolution,
                        level_evolution,
                        rarity,
                    ),
                )

            # Commit the transaction
            await conn.commit()
        print("Revomon table updated successfully!")

        # Export data from the revomon table to a JSON file
        await self.export_to_json()

    async def export_to_json(self) -> None:
        """Export data from the revomon table to a JSON file."""
        json_file_path = "./data/revomon.json"
        async with self._connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute("SELECT * FROM revomon;")
            rows = await cursor.fetchall()

            # Get column names
            column_names = [description[0] for description in cursor.description]

            # Convert rows to a list of dictionaries
            data = [dict(zip(column_names, row)) for row in rows]

            # Write to JSON file
            with open(json_file_path, "w") as json_file:
                json.dump(data, json_file, indent=4)

            print(f"Data exported to {json_file_path}.")

    async def count_entries(self) -> int:
        """Return the number of entries in the revomon table."""
        print("Counting entries in the revomon table...")
        async with self._connect() as conn:
            cursor = await conn.cursor()

            # Execute the query and fetch the result
            await cursor.execute("SELECT COUNT(*) FROM revomon;")
            count = int((await cursor.fetchone())[0])  # type: ignore

        # Print the result
        print(f"Number of Entries in the revomon table: {count}")

        # Return the count
        return count

    async def get_mon_ids(self) -> list[int]:
        """Get all mon_ids from the revomon table."""
        async with self._connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute("SELECT mon_id FROM revomon;")
            mon_ids = [row[0] for row in await cursor.fetchall()]
            return mon_ids

    async def get_id_by_id(self, mon_id: int) -> Any:
        """Get dex_id by mon_id."""
        async with self._connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute("SELECT dex_id FROM revomon WHERE mon_id = ?;", (mon_id,))
            result = await cursor.fetchone()
            return result[0] if result else None

    async def get_name_by_id(self, mon_id: int) -> Any:
        """Get name by mon_id."""
        async with self._connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute("SELECT name FROM revomon WHERE mon_id = ?;", (mon_id,))
            result = await cursor.fetchone()
            return result[0] if result else None

    async def get_names(self) -> Any:
        """Returns a list containing all the names of the Revomons in the revomon table, sorted by dex_id."""
        async with self._connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute("SELECT name FROM revomon ORDER BY dex_id;")
            names = [row[0].lower() for row in await cursor.fetchall()]
            return names

    async def get_info(self, revomon_name: str) -> Any:
        """Method to search the revomon table by name and return the info of the matching entry."""
        async with self._connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute(
                "SELECT * FROM revomon WHERE name LIKE ?;", (f"%{revomon_name}%",)
            )
            rows = await cursor.fetchall()
            return rows


class RevomonMovesTable:
    """Class to manage the relationship between Revomon and their moves."""

    def __init__(self) -> None:
        self.db_path = db_path

    async def build(self) -> None:
        """Sets up the revomon_moves table."""
        # Create the revomon_moves table
        await self.create()
        # Rebuild the revomon_moves table
        await self.rebuild()
        # Count the number of entries in the revomon_moves table
        await self.count_entries()

    def _connect(self) -> Connection:
        """Establishes a connection to the SQLite database."""
        return aiosqlite.connect(self.db_path, isolation_level=None)

    async def create(self) -> None:
        """Creates the revomon_moves table."""
        async with self._connect() as conn:
            cursor = await conn.cursor()
            print("Creating revomon_moves table...")

            # Drop the moves table if it already exists
            print("Dropping revmon_moves table if it already exists...")
            await conn.execute("DROP TABLE IF EXISTS revomon_moves;")
            print("revomon_moves table dropped.")
            await cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS revomon_moves (
                    mon_dex_id INTEGER NOT NULL,
                    mon_name TEXT NOT NULL,
                    move_id INTEGER NOT NULL,
                    move_name TEXT NOT NULL,
                    method TEXT NOT NULL,
                    level INTEGER NOT NULL,
                    PRIMARY KEY (mon_dex_id, move_id),
                    FOREIGN KEY (mon_dex_id) REFERENCES revomon (dex_id) ON DELETE CASCADE,
                    FOREIGN KEY (mon_name) REFERENCES revomon (name) ON DELETE CASCADE,
                    FOREIGN KEY (move_id) REFERENCES moves (id) ON DELETE CASCADE,
                    FOREIGN KEY (move_name) REFERENCES moves (name) ON DELETE CASCADE
                ) STRICT;
                """
            )
            await conn.commit()
            print("revomon_moves table created successfully.")

    async def rebuild(self) -> None:
        """Fetch data from revomon_moves.json or the Moves API and insert it into the database."""
        print("Rebuilding revomon_moves table...")

        revomon_moves_file = Path("./data/revomon_moves.json")
        has_local_data = False
        revomon_moves_data = []

        import os
        if "PYTEST_CURRENT_TEST" not in os.environ and revomon_moves_file.exists() and revomon_moves_file.stat().st_size > 10:
            try:
                with open(revomon_moves_file, encoding="utf-8") as file:
                    revomon_moves_data = json.load(file)
                if revomon_moves_data:
                    has_local_data = True
                    print(
                        f"Loaded {len(revomon_moves_data)} connections from local revomon_moves.json"
                    )
            except Exception as e:
                print(f"Failed to load local revomon_moves.json: {e}")

        # Connect to the database and create a cursor
        async with self._connect() as conn:
            cursor = await conn.cursor()

            insert_query = """
                INSERT OR IGNORE INTO revomon_moves
                    (mon_dex_id, mon_name, move_id, move_name, method, level)
                    VALUES (?, ?, ?, ?, ?, ?);
            """

            if has_local_data:
                # Insert data from local revomon_moves.json
                data_to_insert = [
                    (
                        connection.get("mon_dex_id"),
                        connection.get("mon_name").lower(),
                        connection.get("move_id"),
                        connection.get("move_name").lower(),
                        connection.get("method").lower(),
                        connection.get("level"),
                    )
                    for connection in revomon_moves_data
                ]

                await conn.execute("BEGIN TRANSACTION;")
                await cursor.executemany(insert_query, data_to_insert)
                await conn.commit()
            else:
                # Fetch data from the Revomon Moves API
                mon_ids = await RevomonTable().get_mon_ids()
                for mon_id in mon_ids:
                    dex_id = await RevomonTable().get_id_by_id(mon_id=mon_id)
                    mon_name = await RevomonTable().get_name_by_id(mon_id=mon_id)
                    url = f"https://api.revomon.io/revomon/moves/{mon_id}"
                    response = safe_get(url)
                    time.sleep(0.2)  # Delay to respect API rate limits

                    if response and response.status_code == 200:
                        data = response.json()

                        # Insert data into the database
                        for move in data["data"]["moves"]:
                            move_id = move["idMove"]
                            move_name = move["name"]
                            method = move["method"]
                            level = move["level"]
                            await cursor.execute(
                                insert_query,
                                (
                                    dex_id,
                                    mon_name.lower(),
                                    move_id,
                                    move_name.lower(),
                                    method.lower(),
                                    level,
                                ),
                            )

                            # Check if the row was inserted
                            if (
                                cursor.rowcount == 0
                            ):  # If the row was not inserted, it means it already exists
                                continue
                            else:
                                print(f"Added link: {mon_name} <-> {move_name}")

                        await conn.commit()
        print("Revomon_moves table updated successfully.")

        # Export the revomon_moves table to a JSON file
        await self.export_to_json()

    async def export_to_json(self) -> None:
        """Export data from the revomon_moves table to a JSON file."""
        json_file_path = "./data/revomon_moves.json"
        async with self._connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute("SELECT * FROM revomon_moves;")
            rows = await cursor.fetchall()

            # Get column names
            column_names = [description[0] for description in cursor.description]

            # Convert rows to a list of dictionaries
            data = [dict(zip(column_names, row)) for row in rows]

            # Write to JSON file
            with open(json_file_path, "w") as json_file:
                json.dump(data, json_file, indent=4)

            print(f"Data exported to {json_file_path}.")

    async def count_entries(self) -> int:
        """Counts the number of entries in the revomon_moves table."""
        print("Counting entries in the revomon_moves table...")
        async with self._connect() as conn:
            cursor = await conn.cursor()

            # Execute the query and fetch the result
            await cursor.execute("SELECT COUNT(*) FROM revomon_moves;")
            count = int((await cursor.fetchone())[0])  # type: ignore

            # Print the result
            print(f"Number of connections in the revomon_moves table: {count}")

            # Return the count
            return count

    async def add_link(
        self,
        mon_dex_id: int,
        mon_name: str,
        move_id: int,
        move_name: str,
        method: str,
        level: int,
    ) -> None:
        """Links a Revomon to a move."""
        async with self._connect() as conn:
            cursor = await conn.cursor()

            await cursor.execute(
                """
                INSERT OR REPLACE INTO revomon_moves
                    (mon_dex_id, mon_name, move_id, move_name, method, level)
                    VALUES (?, ?, ?, ?, ?, ?);
                """,
                (mon_dex_id, mon_name, move_id, move_name, method, level),
            )
            await conn.commit()

    async def get_moves_for_revomon(self, mon_dex_id: int) -> Any:
        """Retrieves the moves associated with a specific Revomon.

        Args:
            mon_dex_id (int): The dex ID of the Revomon.

        Returns:
            list of tuples: A list containing tuples with move details
            (name, category, power, pp) for each move the specified Revomon can learn.
        """
        async with self._connect() as conn:
            cursor = await conn.cursor()

            await cursor.execute(
                """
                SELECT moves.name, moves.category, moves.power, moves.pp
                FROM revomon_moves
                JOIN moves ON moves.id = revomon_moves.move_id
                WHERE revomon_moves.mon_dex_id = ?;
                """,
                (mon_dex_id,),
            )
            results = await cursor.fetchall()
            return results

    async def get_mons_for_move(self, move_id: Any = None, move_name: Any = None) -> Any:
        """Retrieves the names of Revomon associated with a specific move.

        Args:
            move_id (int, optional): The ID of the move to search for.
            move_name (str, optional): The name of the move to search for.

        Returns:
            list: A list of Revomon names that can learn the specified move.
            Returns None if neither move_id nor move_name is provided.
        """
        async with self._connect() as conn:
            cursor = await conn.cursor()
            if move_id:
                await cursor.execute(
                    """
                    SELECT revomon.name
                    FROM revomon_moves
                    JOIN revomon ON revomon.dex_id = revomon_moves.mon_dex_id
                    WHERE revomon_moves.move_id = ?;
                    """,
                    (move_id,),
                )
            elif move_name:
                await cursor.execute(
                    """
                    SELECT revomon.name
                    FROM revomon_moves
                    JOIN revomon ON revomon.dex_id = revomon_moves.mon_dex_id
                    WHERE revomon_moves.move_name = ?;
                    """,
                    (move_name.lower(),),
                )
            else:
                return None

            results = await cursor.fetchall()
            return [result[0] for result in results]


class CurrentPodiumTable:
    """Class to interact with the current_podium table in the Gradex SQLite database."""

    def __init__(self) -> None:
        """Initialize with the path to the SQLite database."""
        self.db_path = db_path

    async def build(self) -> None:
        """Build the current_podium table in the Gradex SQLite database."""
        # Create the current_podium table if it doesn't exist
        await self.create()
        # Skip rebuild for now as there's no data source
        # Count the entries in the current_podium table
        await self.count_entries()

    def _connect(self) -> Connection:
        """Private method to establish a connection to the SQLite database."""
        return aiosqlite.connect(self.db_path, isolation_level=None)

    async def create(self) -> None:
        """Create the current_podium table if it does not already exist."""
        print("Creating current_podium table...")

        # Connect to the database and create a cursor
        async with self._connect() as conn:
            cursor = await conn.cursor()

            # Drop the current_podium table if it already exists
            print("Dropping current_podium table if it already exists...")
            await conn.execute("DROP TABLE IF EXISTS current_podium;")
            print("Current_podium table dropped.")

            # Create the current_podium table if it doesn't exist
            await cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS "current_podium" (
                    "rank" INTEGER NOT NULL,
                    "revomon_name" TEXT NOT NULL,
                    "score" INTEGER,
                    PRIMARY KEY("rank")
                ) STRICT;
                """
            )
            print("Current_podium table created successfully")
            await conn.commit()

    async def count_entries(self) -> int:
        """Return the number of entries in the current_podium table."""
        print("Counting entries in the current_podium table...")
        async with self._connect() as conn:
            cursor = await conn.cursor()

            # Execute the query and fetch the result
            await cursor.execute("SELECT COUNT(*) FROM current_podium;")
            count = int((await cursor.fetchone())[0])  # type: ignore

        # Print the result
        print(f"Number of Entries in the current_podium table: {count}")

        # Return the count
        return count


class WeeklyPodiumTable:
    """Class to interact with the weekly_podium table in the Gradex SQLite database."""

    def __init__(self) -> None:
        """Initialize with the path to the SQLite database."""
        self.db_path = db_path

    async def build(self) -> None:
        """Build the weekly_podium table in the Gradex SQLite database."""
        # Create the weekly_podium table if it doesn't exist
        await self.create()
        # Skip rebuild for now as there's no data source
        # Count the entries in the weekly_podium table
        await self.count_entries()

    def _connect(self) -> Connection:
        """Private method to establish a connection to the SQLite database."""
        return aiosqlite.connect(self.db_path, isolation_level=None)

    async def create(self) -> None:
        """Create the weekly_podium table if it does not already exist."""
        print("Creating weekly_podium table...")

        # Connect to the database and create a cursor
        async with self._connect() as conn:
            cursor = await conn.cursor()

            # Drop the weekly_podium table if it already exists
            print("Dropping weekly_podium table if it already exists...")
            await conn.execute("DROP TABLE IF EXISTS weekly_podium;")
            print("Weekly_podium table dropped.")

            # Create the weekly_podium table if it doesn't exist
            await cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS "weekly_podium" (
                    "rank" INTEGER NOT NULL,
                    "revomon_name" TEXT NOT NULL,
                    "score" INTEGER,
                    "week" TEXT NOT NULL,
                    PRIMARY KEY("rank", "week")
                ) STRICT;
                """
            )
            print("Weekly_podium table created successfully")
            await conn.commit()

    async def count_entries(self) -> int:
        """Return the number of entries in the weekly_podium table."""
        print("Counting entries in the weekly_podium table...")
        async with self._connect() as conn:
            cursor = await conn.cursor()

            # Execute the query and fetch the result
            await cursor.execute("SELECT COUNT(*) FROM weekly_podium;")
            count = int((await cursor.fetchone())[0])  # type: ignore

        # Print the result
        print(f"Number of Entries in the weekly_podium table: {count}")

        # Return the count
        return count


class TypesTable:
    """Class to interact with the types table in the Gradex SQLite database."""

    def __init__(self) -> None:
        """Initialize with the path to the SQLite database."""
        self.db_path = db_path

    async def build(self) -> None:
        """Build the types table by creating, rebuilding, and counting entries."""
        # Create the types table if it doesn't exist
        await self.create()
        # Rebuild the types table
        await self.rebuild()
        # Count the entries in the types table
        await self.count_entries()

    def _connect(self) -> Connection:
        """Private method to establish a connection to the SQLite database."""
        return aiosqlite.connect(self.db_path, isolation_level=None)

    async def create(self) -> None:
        """Create the types table if it does not already exist."""
        # Connect to the database and create a cursor
        async with self._connect() as conn:
            cursor = await conn.cursor()

            # Drop the type_effectiveness table if it already exists
            print("Dropping types table if it already exists...")
            await conn.execute("DROP TABLE IF EXISTS types;")
            print("types table dropped.")

            print("Creating types table...")
            # Create the types table
            await cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS "types" (
                    "types_str" TEXT NOT NULL UNIQUE,
                    "img_url" TEXT,
                    "type1" TEXT NOT NULL,
                    "type2" TEXT,
                    "neutral" REAL,
                    "fire" REAL,
                    "water" REAL,
                    "electric" REAL,
                    "forest" REAL,
                    "ice" REAL,
                    "battle" REAL,
                    "toxic" REAL,
                    "earth" REAL,
                    "sky" REAL,
                    "time" REAL,
                    "bug" REAL,
                    "stone" REAL,
                    "phantom" REAL,
                    "draconic" REAL,
                    "twilight" REAL,
                    "metal" REAL,
                    "spirit" REAL,
                    PRIMARY KEY("types_str")
                ) STRICT;
            """
            )
            print("types table created successfully")
            await conn.commit()

    async def rebuild(self) -> None:
        """Fetch data from type_effect_data.py and insert it into the database."""
        print("Rebuilding types table...")
        # Connect to the database and create a cursor
        async with self._connect() as conn:
            cursor = await conn.cursor()

            # Load base types and type charts
            with open("./data/base_types.json") as file:
                base_types = json.load(file)
            with open("./data/type_charts.json") as file:
                type_charts = json.load(file)

            # Insert data into the database
            for type_name in sorted(base_types):
                # Get type effectiveness data from type_charts
                type_data = type_charts.get(type_name, {})
                # Prepare data for insertion
                values = (
                    type_name.lower(),
                    None,  # img_url - not available in current data
                    type_name.lower(),  # type1
                    type_data.get("type2", "").lower()
                    if type_data.get("type2")
                    else None,  # type2
                    type_data.get("neutral", 1.0),
                    type_data.get("fire", 1.0),
                    type_data.get("water", 1.0),
                    type_data.get("electric", 1.0),
                    type_data.get("forest", 1.0),
                    type_data.get("ice", 1.0),
                    type_data.get("battle", 1.0),
                    type_data.get("toxic", 1.0),
                    type_data.get("earth", 1.0),
                    type_data.get("sky", 1.0),
                    type_data.get("time", 1.0),
                    type_data.get("bug", 1.0),
                    type_data.get("stone", 1.0),
                    type_data.get("phantom", 1.0),
                    type_data.get("draconic", 1.0),
                    type_data.get("twilight", 1.0),
                    type_data.get("metal", 1.0),
                    type_data.get("spirit", 1.0),
                )

                # Execute the insert query
                await cursor.execute(
                    """
                    INSERT OR REPLACE INTO types
                        (types_str, img_url, type1, type2, neutral, fire, water, electric, forest, ice, battle, toxic, earth, sky, time, bug, stone, phantom, draconic, twilight, metal, spirit)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """,
                    values,
                )

            # Commit the transaction
            await conn.commit()

        print("types table updated successfully!")
        # Export the types table to a JSON file
        await self.export_to_json()

    async def export_to_json(self) -> None:
        """Export data from the types table to a JSON file."""
        json_file_path = "./data/types.json"
        async with self._connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute("SELECT * FROM types;")
            rows = await cursor.fetchall()

            # Get column names
            column_names = [description[0] for description in cursor.description]

            # Convert rows to a list of dictionaries
            data = [dict(zip(column_names, row)) for row in rows]

            # Write to JSON file
            with open(json_file_path, "w") as json_file:
                json.dump(data, json_file, indent=4)

            print(f"Data exported to {json_file_path}.")

    async def count_entries(self) -> int:
        """Return the number of entries in the types table."""
        print("Counting entries in the types table...")
        async with self._connect() as conn:
            cursor = await conn.cursor()

            # Execute the query and fetch the result
            await cursor.execute("SELECT COUNT(*) FROM types;")
            count = int((await cursor.fetchone())[0])  # type: ignore

            # Close the connection

            # Print the result
            print(f"Number of entries in the types table: {count}")

            # Return the count
            return count

    async def add_type(self, types_str: str, data: Any) -> None:
        """Add a type to the types table."""
        async with self._connect() as conn:
            cursor = await conn.cursor()

            # Prepare the values for insertion
            values = (
                types_str.lower(),
                data.get("img_url"),
                data.get("type 1").lower(),
                data.get("type 2").lower() if data.get("type 2") else None,
                data.get("neutral"),
                data.get("fire"),
                data.get("water"),
                data.get("electric"),
                data.get("forest"),
                data.get("ice"),
                data.get("battle"),
                data.get("toxic"),
                data.get("earth"),
                data.get("sky"),
                data.get("time"),
                data.get("bug"),
                data.get("stone"),
                data.get("phantom"),
                data.get("draconic"),
                data.get("twilight"),
                data.get("metal"),
                data.get("spirit"),
            )

            # Execute the insert query
            await cursor.execute(
                """
                INSERT INTO types
                    (types_str, img_url, type1, type2, neutral, fire, water, electric, forest, ice, battle, toxic, earth, sky, time, bug, stone, phantom, draconic, twilight, metal, spirit)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                values,
            )
            await conn.commit()
            print(f"types entry for '{types_str}' added successfully!")

    async def get_info(self, type1: str, type2: Any = None) -> Any:
        """Retrieves a tuple containing all info about the given type(s) from the types table.

        Args:
            type1 (str): The primary type to query.
            type2 (str, optional): The secondary type to query. Defaults to None.

        Returns:
            tuple: A tuple containing all the info about the given type(s) from the types table.
        """
        async with self._connect() as conn:
            cursor = await conn.cursor()
            if type2:
                await cursor.execute(
                    "SELECT * FROM types WHERE type1 = ? AND type2 = ?",
                    (type1.lower(), type2.lower()),
                )
            else:
                await cursor.execute(
                    "SELECT * FROM types WHERE type1 = ? AND type2 IS NULL",
                    (type1.lower(),),
                )
            result = await cursor.fetchall()
            return result

    async def get_mono_types(self) -> list[str]:
        """Retrieves a list of all monotype types from the types table.

        Returns:
            list: A list of all monotype types from the types table.
        """
        async with self._connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute("SELECT type1 FROM types WHERE type2 IS NULL")
            mono_types = [row[0] for row in await cursor.fetchall()]
        return mono_types


class UsersTable:
    """Class to interact with the users Table in the Gradex SQLite database."""

    def __init__(self) -> None:
        """Initialize with the path to the SQLite database."""
        self.db_path = db_path

    async def build(self) -> None:
        """Build the users table by creating, rebuilding, and counting entries."""
        # Create the users Table if it doesn't exist
        await self.create()
        # Rebuild the users Table
        await self.rebuild()
        # Count the entries in the users Table
        await self.count_entries()

    def _connect(self) -> Connection:
        """Private method to establish a connection to the SQLite database."""
        return aiosqlite.connect(self.db_path, isolation_level=None)

    async def create(self) -> None:
        """Create the users Table if it does not already exist."""
        print("Creating users Table...")

        # Connect to the database and create a cursor
        async with self._connect() as conn:
            cursor = await conn.cursor()

            # Drop the users Table if it already exists
            print("Dropping users Table if it already exists...")
            await conn.execute("DROP TABLE IF EXISTS users;")
            print("users Table dropped.")

            # Create the users Table if it doesn't exist
            await cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS "users" (
                    "user_id" INTEGER NOT NULL UNIQUE,
                    "username" TEXT NOT NULL,
                    "wallet_connected" INTEGER NOT NULL,
                    "wallet_address" TEXT,
                    "is_pro" INTEGER NOT NULL,
                    "is_certified" INTEGER NOT NULL,
                    "experience_points" INTEGER NOT NULL,
                    "battle_points" INTEGER NOT NULL,
                    "victory_points" INTEGER NOT NULL,
                    "wins" INTEGER NOT NULL,
                    "losses" INTEGER NOT NULL,
                    "draws" INTEGER NOT NULL,
                    PRIMARY KEY("user_id")
                ) STRICT;
                """
            )
            print("Users Table created successfully")
            await conn.commit()

    async def rebuild(self) -> None:
        """Fetch user data and insert it into the database."""
        print("Rebuilding users Table...")

        print("Users Table updated successfully!")

        # Export data from the users table to a JSON file
        # await self.export_to_json()

    async def export_to_json(self) -> None:
        """Export data from the users Table to a JSON file."""
        json_file_path = "./data/users.json"
        async with self._connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute("SELECT * FROM users;")
            rows = await cursor.fetchall()

            # Get column names
            column_names = [description[0] for description in cursor.description]

            # Convert rows to a list of dictionaries
            data = [dict(zip(column_names, row)) for row in rows]

            # Write to JSON file
            with open(json_file_path, "w") as json_file:
                json.dump(data, json_file, indent=4)

            print(f"Data exported to {json_file_path}.")

    async def count_entries(self) -> int:
        """Return the number of entries in the users Table."""
        print("Counting entries in the users Table...")
        async with self._connect() as conn:
            cursor = await conn.cursor()

            # Execute the query and fetch the result
            await cursor.execute("SELECT COUNT(*) FROM users;")
            count = int((await cursor.fetchone())[0])  # type: ignore

        # Print the result
        print(f"Number of Users in the users Table: {count}")

        # Return the count
        return count

    async def add_user(
        self,
        user_id: int,
        username: str,
        wallet_connected: int,
        wallet_address: str,
        is_pro: int,
        is_certified: int,
        experience_points: int,
        battle_points: int,
        victory_points: int,
        wins: int,
        losses: int,
        draws: int,
    ) -> Any:
        """Add a user to the users table."""
        async with self._connect() as conn:
            cursor = await conn.cursor()
            query = "INSERT INTO users (user_id, username, wallet_connected, wallet_address, is_pro, is_certified, experience_points, battle_points, victory_points, wins, losses, draws) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"
            await cursor.execute(
                query,
                (
                    user_id,
                    username,
                    wallet_connected,
                    wallet_address,
                    is_pro,
                    is_certified,
                    experience_points,
                    battle_points,
                    victory_points,
                    wins,
                    losses,
                    draws,
                ),
            )

            await conn.commit()
            print(f"User with ID {user_id} added to the users Table.")
            return True

    async def update_user(self, user_id: int | None, **kwargs: Any) -> Any:
        """Update a user's information in the users table."""
        if not user_id:
            raise ValueError("user_id is a required argument")

        async with self._connect() as conn:
            cursor = await conn.cursor()
            query = f"UPDATE users SET {', '.join([f'{key} = ?' for key in kwargs])}  WHERE user_id = ?;"
            await cursor.execute(query, (*kwargs.values(), user_id))
            await conn.commit()
            print(f"User with ID {user_id} updated in the users Table.")
            return True

    async def delete_user(self, user_id: int) -> Any:
        """Delete a user from the users table."""
        async with self._connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
            await conn.commit()
            print(f"User with ID {user_id} deleted from the users Table.")
            return True

    async def get_user(self, user_id: int) -> Any:
        """Get a user by user ID from the users table."""
        async with self._connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            user = await cursor.fetchone()
            if user is None:
                return False
            return user

    async def get_users(self) -> Any:
        """Get all users from the users table."""
        async with self._connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute("SELECT * FROM users;")
            users = await cursor.fetchall()
            return users


class EventBoardLogsTable:
    """Class to interact with the event_board_logs table in the Gradex SQLite database."""

    def __init__(self) -> None:
        """Initialize with the path to the SQLite database."""
        self.db_path = db_path

    async def build(self) -> None:
        """Build the event_board_logs table in the Gradex SQLite database."""
        await self.create()

    def _connect(self) -> Connection:
        """Private method to establish a connection to the SQLite database."""
        return aiosqlite.connect(self.db_path, isolation_level=None)

    async def create(self) -> None:
        """Create the event_board_logs table if it does not already exist."""
        print("Creating event_board_logs table...")

        async with self._connect() as conn:
            cursor = await conn.cursor()

            await cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS "event_board_logs" (
                    "message_id" INTEGER PRIMARY KEY,
                    "user_id" INTEGER NOT NULL,
                    "revomon_id" INTEGER NOT NULL,
                    "is_shiny" INTEGER NOT NULL,
                    "outcome" TEXT,
                    "timestamp" INTEGER NOT NULL
                ) STRICT;
                """
            )
            print("event_board_logs table created successfully")
            await conn.commit()


class GlobalSettingsTable:
    """Class to interact with the global_settings table for global variables."""
    def __init__(self) -> None:
        self.db_path = db_path

    async def build(self) -> None:
        await self.create()

    def _connect(self) -> Connection:
        return aiosqlite.connect(self.db_path, isolation_level=None)

    async def create(self) -> None:
        print("Creating global_settings table...")
        async with self._connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS "global_settings" (
                    "id" INTEGER PRIMARY KEY,
                    "next_rc_id" INTEGER NOT NULL DEFAULT 1
                ) STRICT;
                """
            )
            await cursor.execute("INSERT OR IGNORE INTO global_settings (id, next_rc_id) VALUES (1, 1);")
            print("global_settings table created successfully")
            await conn.commit()


async def get_next_rc_id() -> int:
    """Atomically fetches and increments the next available rc_id."""
    async with aiosqlite.connect(db_path, isolation_level=None) as conn:
        cursor = await conn.cursor()
        await cursor.execute("UPDATE global_settings SET next_rc_id = next_rc_id + 1 WHERE id = 1 RETURNING next_rc_id")
        row = await cursor.fetchone()
        if row:
            return int(row[0]) - 1
        return 1


class GuildsTable:
    """Class to interact with the guilds table for server-specific settings."""
    def __init__(self) -> None:
        self.db_path = db_path

    async def build(self) -> None:
        await self.create()

    def _connect(self) -> Connection:
        return aiosqlite.connect(self.db_path, isolation_level=None)

    async def create(self) -> None:
        print("Creating guilds table...")
        async with self._connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS "guilds" (
                    "guild_id" INTEGER PRIMARY KEY,
                    "biome" TEXT NOT NULL DEFAULT 'Forest',
                    "max_spawn_limit" INTEGER NOT NULL DEFAULT 100,
                    "temp_spawn_limit" INTEGER NOT NULL DEFAULT 0,
                    "temp_limit_expires" INTEGER NOT NULL DEFAULT 0,
                    "next_spawn_time" INTEGER NOT NULL DEFAULT 0,
                    "spawn_multiplier" REAL NOT NULL DEFAULT 1.0,
                    "spawn_multiplier_expires" INTEGER NOT NULL DEFAULT 0
                ) STRICT;
                """
            )
            try:
                await cursor.execute("ALTER TABLE guilds ADD COLUMN max_spawn_limit INTEGER NOT NULL DEFAULT 100")
                await cursor.execute("ALTER TABLE guilds ADD COLUMN temp_spawn_limit INTEGER NOT NULL DEFAULT 0")
                await cursor.execute("ALTER TABLE guilds ADD COLUMN temp_limit_expires INTEGER NOT NULL DEFAULT 0")
                await cursor.execute("ALTER TABLE guilds ADD COLUMN next_spawn_time INTEGER NOT NULL DEFAULT 0")
                await cursor.execute("ALTER TABLE guilds ADD COLUMN spawn_multiplier REAL NOT NULL DEFAULT 1.0")
                await cursor.execute("ALTER TABLE guilds ADD COLUMN spawn_multiplier_expires INTEGER NOT NULL DEFAULT 0")
            except Exception:
                pass
            print("guilds table created successfully")
            await conn.commit()


async def get_guild_biome(guild_id: int) -> str:
    """Fetches the currently set Biome for the specified guild."""
    async with aiosqlite.connect(db_path) as conn:
        cursor = await conn.cursor()
        await cursor.execute("SELECT biome FROM guilds WHERE guild_id = ?", (guild_id,))
        row = await cursor.fetchone()
        return row[0] if row else "Forest"

async def set_guild_biome(guild_id: int, biome: str) -> None:
    """Sets the Biome for the specified guild."""
    async with aiosqlite.connect(db_path, isolation_level=None) as conn:
        cursor = await conn.cursor()
        await cursor.execute(
            """
            INSERT INTO guilds (guild_id, biome)
            VALUES (?, ?)
            ON CONFLICT(guild_id) DO UPDATE SET biome = excluded.biome
            """,
            (guild_id, biome)
        )
        await conn.commit()

async def get_guild_spawn_config(guild_id: int) -> dict:
    async with aiosqlite.connect(db_path) as conn:
        conn.row_factory = aiosqlite.Row
        cursor = await conn.cursor()
        await cursor.execute(
            "SELECT max_spawn_limit, temp_spawn_limit, temp_limit_expires, next_spawn_time, spawn_multiplier, spawn_multiplier_expires FROM guilds WHERE guild_id = ?",
            (guild_id,)
        )
        row = await cursor.fetchone()
        if row:
            d = dict(row)
            # Handle NULL values from schema updates
            return {
                "max_spawn_limit": d.get("max_spawn_limit") or 100,
                "temp_spawn_limit": d.get("temp_spawn_limit") or 0,
                "temp_limit_expires": d.get("temp_limit_expires") or 0,
                "next_spawn_time": d.get("next_spawn_time") or 0,
                "spawn_multiplier": d.get("spawn_multiplier") or 1.0,
                "spawn_multiplier_expires": d.get("spawn_multiplier_expires") or 0
            }
        return {
            "max_spawn_limit": 100,
            "temp_spawn_limit": 0,
            "temp_limit_expires": 0,
            "next_spawn_time": 0,
            "spawn_multiplier": 1.0,
            "spawn_multiplier_expires": 0
        }

async def delete_guild_data(guild_id: int) -> None:
    """Removes all server-specific data (but preserves accounts/progress) when RevoCord is removed."""
    async with aiosqlite.connect(db_path, isolation_level=None) as conn:
        cursor = await conn.cursor()
        await cursor.execute("DELETE FROM guilds WHERE guild_id = ?", (guild_id,))
        await cursor.execute("DELETE FROM active_spawns WHERE guild_id = ?", (guild_id,))
        await conn.commit()

async def update_guild_spawn_config(guild_id: int, **kwargs) -> None:
    if not kwargs:
        return
    sets = ", ".join(f"{k} = ?" for k in kwargs.keys())
    values = list(kwargs.values())
    values.append(guild_id)
    async with aiosqlite.connect(db_path, isolation_level=None) as conn:
        cursor = await conn.cursor()
        await cursor.execute("INSERT OR IGNORE INTO guilds (guild_id) VALUES (?)", (guild_id,))
        await cursor.execute(f"UPDATE guilds SET {sets} WHERE guild_id = ?", tuple(values))
        await conn.commit()

class ActiveSpawnsTable:
    def __init__(self) -> None:
        self.db_path = db_path

    async def build(self) -> None:
        await self.create()

    def _connect(self) -> aiosqlite.Connection:
        return aiosqlite.connect(self.db_path, isolation_level=None)

    async def create(self) -> None:
        print("Creating active_spawns table...")
        async with self._connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS "active_spawns" (
                    "message_id" INTEGER PRIMARY KEY,
                    "guild_id" INTEGER NOT NULL,
                    "spawn_data" TEXT NOT NULL
                ) STRICT;
                """
            )
            print("active_spawns table created successfully")
            await conn.commit()

    async def add_spawn(self, message_id: int, guild_id: int, spawn_data: str) -> None:
        async with self._connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute(
                "INSERT INTO active_spawns (message_id, guild_id, spawn_data) VALUES (?, ?, ?)",
                (message_id, guild_id, spawn_data)
            )
            await conn.commit()

    async def remove_spawn(self, message_id: int) -> None:
        async with self._connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute("DELETE FROM active_spawns WHERE message_id = ?", (message_id,))
            await conn.commit()

    async def get_spawn(self, message_id: int) -> dict | None:
        import json
        async with self._connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute("SELECT spawn_data FROM active_spawns WHERE message_id = ?", (message_id,))
            row = await cursor.fetchone()
            if row:
                return json.loads(row[0])
            return None

    async def get_guild_spawns(self, guild_id: int) -> list:
        import json
        async with self._connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute("SELECT message_id, spawn_data FROM active_spawns WHERE guild_id = ?", (guild_id,))
            rows = await cursor.fetchall()
            return [{"message_id": r[0], "data": json.loads(r[1])} for r in rows]

    async def count_guild_spawns(self, guild_id: int) -> int:
        async with self._connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute("SELECT COUNT(*) FROM active_spawns WHERE guild_id = ?", (guild_id,))
            row = await cursor.fetchone()
            return row[0] if row else 0


class ActiveEncountersTable:
    """Class to interact with the active_encounters table for background battle stats."""
    def __init__(self) -> None:
        self.db_path = db_path

    async def build(self) -> None:
        await self.create()

    def _connect(self) -> Connection:
        return aiosqlite.connect(self.db_path, isolation_level=None)

    async def create(self) -> None:
        print("Creating active_encounters table...")
        async with self._connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS "active_encounters" (
                    "spawner_id" INTEGER PRIMARY KEY,
                    "encounter_data" TEXT NOT NULL
                ) STRICT;
                """
            )
            print("active_encounters table created successfully")
            await conn.commit()


async def save_active_encounter(spawner_id: int, encounter_data: str) -> None:
    """Saves the serialized encounter data for the specified spawner."""
    async with aiosqlite.connect(db_path, isolation_level=None) as conn:
        cursor = await conn.cursor()
        await cursor.execute(
            """
            INSERT INTO active_encounters (spawner_id, encounter_data)
            VALUES (?, ?)
            ON CONFLICT(spawner_id) DO UPDATE SET encounter_data = excluded.encounter_data
            """,
            (spawner_id, encounter_data)
        )
        await conn.commit()

async def get_active_encounter(spawner_id: int) -> str | None:
    """Fetches the serialized encounter data for the specified spawner."""
    async with aiosqlite.connect(db_path) as conn:
        cursor = await conn.cursor()
        await cursor.execute("SELECT encounter_data FROM active_encounters WHERE spawner_id = ?", (spawner_id,))
        row = await cursor.fetchone()
        return row[0] if row else None

async def delete_active_encounter(spawner_id: int) -> None:
    """Deletes the active encounter data for the specified spawner."""
    async with aiosqlite.connect(db_path, isolation_level=None) as conn:
        cursor = await conn.cursor()
        await cursor.execute("DELETE FROM active_encounters WHERE spawner_id = ?", (spawner_id,))
        await conn.commit()


active_spawns_table = ActiveSpawnsTable()

async def update_gradex_db() -> None:
    # Initialize the global settings table
    global_settings_table = GlobalSettingsTable()
    await global_settings_table.build()

    # Initialize the guilds table
    guilds_table = GuildsTable()
    await guilds_table.build()

    # Initialize the active encounters table
    active_encounters_table = ActiveEncountersTable()
    await active_encounters_table.build()

    # Initialize the active spawns table
    await active_spawns_table.build()

    # Initialize the event board logs table
    event_board_table = EventBoardLogsTable()
    await event_board_table.build()

    # Initialize the revomon table
    revomon_table = RevomonTable()
    # Build the revomon table
    await revomon_table.build()

    # Initialize the natures table
    natures_table = NaturesTable()
    # Build the natures table
    await natures_table.build()

    # Initialize the abilities table
    abilities_table = AbilitiesTable()
    # Build the abilities table
    await abilities_table.build()

    # Initialize the capsules table
    capsules_table = CapsulesTable()
    # Use the mon ids to build the capsules table
    await capsules_table.build()

    # Initialize the fruitys table
    fruitys_table = FruitysTable()
    # Build the fruitys table
    await fruitys_table.build()

    # Initialize the moves table
    moves_table = MovesTable()
    # Build the moves table
    await moves_table.build()

    # Initialize the items table
    items_table = ItemsTable()
    # Build the items table
    await items_table.build()

    # Initialize the current podium table
    current_podium_table = CurrentPodiumTable()
    # Build the current podium table
    await current_podium_table.build()

    # Initialize the weekly podium table
    weekly_podium_table = WeeklyPodiumTable()
    # Build the weekly podium table
    await weekly_podium_table.build()

    # Initialize the types table
    types_table = TypesTable()
    # Build the types table
    await types_table.build()

    # Initialize the Revomon Moves table
    revomon_moves_table = RevomonMovesTable()
    # Build the Revomon Moves table
    await revomon_moves_table.build()

    # Initialize the counterdex table
    counterdex_table = CounterdexTable()
    # Build the counterdex table
    await counterdex_table.build()

    # Initialize the owned Lands Table
    # owned_lands_table = OwnedLandsTable()
    # Build the owned lands table
    # await owned_lands_table.build()

    # Initialize the users table
    users_table = UsersTable()
    # Build the users table
    await users_table.build()


# Example usage:
"""
# "SELECT <attack_type> FROM types WHERE type1 = ? AND type2 = ?",[<"DefenderType2">, <DefenderType2>]
attack_type = "bug"
results = query_gradex(f"SELECT * FROM types WHERE type1 = ? AND type2 IS NULL", ["bug"])

print(results)
"""


if __name__ == "__main__":  # pragma: no cover
    raise NotImplementedError("This module is not meant to be run directly.")
