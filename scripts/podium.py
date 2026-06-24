import json
from pathlib import Path

import aiosqlite
import requests
from aiosqlite.core import Connection

from configs import GRADEX_DB_PATH

db_path: Path = GRADEX_DB_PATH


class WeeklyPodiumTable:
    """Class to interact with the weekly podium leaderboard table in the Gradex SQLite database."""

    def __init__(self) -> None:
        """Initialize with the path to the SQLite database."""
        self.db_path = db_path

    async def build(self) -> None:
        """Build the weekly podium table by creating, rebuilding, and counting entries."""
        # Create the weekly podium table if it doesn't exist
        await self.create()
        # Rebuild the weekly podium table
        await self.rebuild()
        # Count the entries in the weekly podium table
        await self.count_entries()

    def _connect(self) -> Connection:
        """Private method to establish a connection to the SQLite database."""
        return aiosqlite.connect(self.db_path, isolation_level=None)

    async def create(self) -> None:
        """Create the weekly podium table if it does not already exist."""
        # Connect to the database and create a cursor
        async with self._connect() as conn:
            cursor = await conn.cursor()

            # Drop the weekly podium table if it already exists
            print("Dropping weekly podium table if it already exists...")
            await conn.execute("DROP TABLE IF EXISTS weeklyPodium;")
            print("weekly podium table dropped.")

            print("Creating weekly podium table...")
            # Create the weekly podium table
            await cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS "weeklyPodium" (
                    "rank" INTEGER NOT NULL UNIQUE,
                    "username" TEXT NOT NULL,
                    "amount" INTEGER NOT NULL,
                    "profile_picture" TEXT,
                    "times" INTEGER NOT NULL,
                    PRIMARY KEY ("rank")
                ) STRICT;
                """
            )
            print("weekly podium table created successfully")
            await conn.commit()

    async def rebuild(self) -> None:
        """Fetch data from the Revomon Weekly Podium API and insert it into the database."""
        print("Rebuilding weekly podium table...")
        url = "https://api.revomon.io/leaderboard/weekly_podium"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            podium_entries = data["data"]["weeklyPodium"]

            # Connect to the database and create a cursor
            async with self._connect() as conn:
                cursor = await conn.cursor()

                # Insert data into the database
                for entry in podium_entries:
                    rank = entry["rank"]
                    username = entry["username"]
                    amount = entry["amount"]
                    profile_picture = entry["profilePicture"]
                    times = entry["times"]

                    # Execute the insert query
                    await cursor.execute(
                        """
                        INSERT OR REPLACE INTO weeklyPodium
                            (rank, username, amount, profile_picture, times)
                            VALUES (?, ?, ?, ?, ?);
                        """,
                        (rank, username, amount, profile_picture, times),
                    )

                # Commit the transaction
                await conn.commit()
                print("weekly podium table updated successfully!")
            # Export the weekly podium table to a json file
            await self.export_to_json()
        else:
            print(f"Failed to fetch data: {response.status_code}")

    async def export_to_json(self) -> None:
        """Export data from the weeklyPodium table to a JSON file."""
        json_file_path = "./data/weekly_podium.json"
        async with self._connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute("SELECT * FROM weeklyPodium;")
            rows = await cursor.fetchall()

            # Get column names
            column_names = [description[0] for description in cursor.description]

            # Convert rows to a list of dictionaries
            data = [dict(zip(column_names, row, strict=True)) for row in rows]

            # Write to JSON file
            with open(json_file_path, "w") as json_file:
                json.dump(data, json_file, indent=4)

            print(f"Data exported to {json_file_path}.")

    async def count_entries(self) -> int:
        """Return the number of entries in the weekly podium table."""
        print("Counting entries in the weekly podium table...")
        async with self._connect() as conn:
            cursor = await conn.cursor()

            # Execute the query and fetch the result
            await cursor.execute("SELECT COUNT(*) FROM weeklyPodium;")
            count = (await cursor.fetchone())[0]  # type: ignore[index]

            # Close the connection

            # Print the result
            print(f"Number of entries in the weekly podium table: {count}")

            # Return the count
            return count  # type: ignore[no-any-return]

    async def add_entry(
        self,
        rank: int,
        username: str,
        amount: int,
        profile_picture: str,
        times: int,
    ) -> None:
        """Add a new entry to the weekly podium table in the SQLite database.

        Args:
            rank (int): The rank of the user.
            username (str): The username of the user.
            amount (int): The amount associated with the user.
            profile_picture (str): The URL of the user's profile picture.
            times (int): The times associated with the user.
        """
        async with self._connect() as conn:
            cursor = await conn.cursor()
            # Execute the insert query
            await cursor.execute(
                """
                INSERT OR REPLACE INTO weeklyPodium
                    (rank, username, amount, profile_picture, times)
                    VALUES (?, ?, ?, ?, ?);
                """,
                (rank, username, amount, profile_picture, times),
            )
            await conn.commit()


class CurrentPodiumTable:
    """Class to interact with the current podium leaderboard table in the Gradex SQLite database."""

    def __init__(self) -> None:
        """Initialize with the path to the SQLite database."""
        self.db_path = db_path

    async def build(self) -> None:
        """Build the current podium table."""
        # Create the current podium table if it doesn't exist
        await self.create()
        # Rebuild the current podium table
        await self.rebuild()
        # Count the entries in the current podium table
        await self.count_entries()

    def _connect(self) -> Connection:
        """Private method to establish a connection to the SQLite database."""
        return aiosqlite.connect(self.db_path, isolation_level=None)

    async def create(self) -> None:
        """Create the current podium table if it does not already exist."""
        # Connect to the database and create a cursor
        async with self._connect() as conn:
            cursor = await conn.cursor()

            # Drop the current podium table if it already exists
            print("Dropping current podium table if it already exists...")
            await conn.execute("DROP TABLE IF EXISTS currentPodium;")
            print("current podium table dropped.")

            print("Creating current podium table...")
            # Create the current podium table
            await cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS "currentPodium" (
                    "rank" INTEGER NOT NULL UNIQUE,
                    "username" TEXT NOT NULL,
                    "profile_picture" TEXT,
                    PRIMARY KEY ("rank")
                ) STRICT;
                """
            )
            print("current podium table created successfully")
            await conn.commit()

    async def rebuild(self) -> None:
        """Fetch data from the Revomon Current Podium API and insert it into the database."""
        print("Rebuilding current podium table...")
        url = "https://api.revomon.io/leaderboard/current_podium"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            podium_entries = data["data"]["currentPodium"]

            # Connect to the database and create a cursor
            async with self._connect() as conn:
                cursor = await conn.cursor()

                # Insert data into the database
                for entry in podium_entries:
                    rank = entry["rank"]
                    username = entry["username"]
                    profile_picture = entry["profilePicture"]

                    # Execute the insert query
                    await cursor.execute(
                        """
                        INSERT OR REPLACE INTO currentPodium
                            (rank, username, profile_picture)
                            VALUES (?, ?, ?);
                        """,
                        (rank, username, profile_picture),
                    )

                # Commit the transaction
                await conn.commit()
                print("current podium table updated successfully!")

            # Export the currentPodium table to a json file
            await self.export_to_json()

    async def export_to_json(self) -> None:
        """Export data from the currentPodium table to a JSON file."""
        json_file_path = "./data/current_podium.json"
        async with self._connect() as conn:
            cursor = await conn.cursor()
            await cursor.execute("SELECT * FROM currentPodium;")
            rows = await cursor.fetchall()

            # Get column names
            column_names = [description[0] for description in cursor.description]

            # Convert rows to a list of dictionaries
            data = [dict(zip(column_names, row, strict=True)) for row in rows]

            # Write to JSON file
            with open(json_file_path, "w") as json_file:
                json.dump(data, json_file, indent=4)

            print(f"Data exported to {json_file_path}.")

    async def count_entries(self) -> int:
        """Return the number of entries in the current podium table."""
        print("Counting entries in the current podium table...")
        async with self._connect() as conn:
            cursor = await conn.cursor()

            # Execute the query and fetch the result
            await cursor.execute("SELECT COUNT(*) FROM currentPodium;")
            count = (await cursor.fetchone())[0]  # type: ignore[index]

            # Close the connection

            # Print the result
            print(f"Number of entries in the current podium table: {count}")

            # Return the count
            return count  # type: ignore[no-any-return]

    async def add_entry(self, rank: int, username: str, profile_picture: str) -> None:
        """Add a new entry to the current podium table in the SQLite database.

        Args:
            rank (int): The rank of the user.
            username (str): The username of the user.
            profile_picture (str): The URL of the user's profile picture.
        """
        async with self._connect() as conn:
            cursor = await conn.cursor()

            # Execute the insert query
            await cursor.execute(
                """
                INSERT OR REPLACE INTO currentPodium
                    (rank, username, profile_picture)
                    VALUES (?, ?, ?);
                """,
                (rank, username, profile_picture),
            )
            await conn.commit()
