"""Data module - redirects to scripts module for database access."""

# This module exists to maintain compatibility with imports that expect data.gradexDB
# The actual implementation is in scripts.gradexDB

import sys  # noqa: E402
from pathlib import Path  # noqa: E402

# Add parent directory to path to ensure scripts module can be imported
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from scripts import gradexDB  # noqa: E402,F401
from scripts.gradexDB import (  # noqa: E402
    AbilitiesTable,
    AccountsTable,
    CapsulesTable,
    CounterdexTable,
    CurrentPodiumTable,
    EventBoardLogsTable,
    FruitysTable,
    ItemsTable,
    MovesTable,
    NaturesTable,
    OwnedLandsTable,
    RevomonMovesTable,
    RevomonTable,
    TypesTable,
    UsersTable,
    WeeklyPodiumTable,
    update_gradex_db,
)  # noqa: E402


class LandsTable:
    """Placeholder for LandsTable - implement if needed."""

    pass


class CaughtRevomonTable:
    """Placeholder for CaughtRevomonTable - implement if needed."""

    pass


__all__ = [
    "gradexDB",
    "CounterdexTable",
    "RevomonTable",
    "RevomonMovesTable",
    "NaturesTable",
    "TypesTable",
    "ItemsTable",
    "MovesTable",
    "AbilitiesTable",
    "FruitysTable",
    "CapsulesTable",
    "UsersTable",
    "OwnedLandsTable",
    "CurrentPodiumTable",
    "WeeklyPodiumTable",
    "EventBoardLogsTable",
    "LandsTable",
    "CaughtRevomonTable",
    "AccountsTable",
    "update_gradex_db",
]
