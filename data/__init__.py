from typing import Any
"""Data module - redirects to scripts module for database access."""

# This module exists to maintain compatibility with imports that expect data.gradexDB
# The actual implementation is in scripts.gradexDB

import sys
from pathlib import Path

# Add parent directory to path to ensure scripts module can be imported
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from scripts import gradexDB
from scripts.gradexDB import *

# Make all gradexDB classes available at data module level
CounterdexTable = gradexDB.CounterdexTable  # type: ignore
AbilitiesTable = gradexDB.AbilitiesTable  # type: ignore
CapsulesTable = gradexDB.CapsulesTable  # type: ignore
FruitysTable = gradexDB.FruitysTable  # type: ignore
ItemsTable = gradexDB.ItemsTable  # type: ignore
MovesTable = gradexDB.MovesTable  # type: ignore
NaturesTable = gradexDB.NaturesTable  # type: ignore
OwnedLandsTable = gradexDB.OwnedLandsTable  # type: ignore
RevomonTable = gradexDB.RevomonTable  # type: ignore
RevomonMovesTable = gradexDB.RevomonMovesTable  # type: ignore
CurrentPodiumTable = gradexDB.CurrentPodiumTable  # type: ignore
WeeklyPodiumTable = gradexDB.WeeklyPodiumTable  # type: ignore
TypesTable = gradexDB.TypesTable  # type: ignore
UsersTable = gradexDB.UsersTable  # type: ignore
EventBoardLogsTable = gradexDB.EventBoardLogsTable  # type: ignore


# Add placeholders for classes that may be expected but don't exist in scripts/gradexDB.py
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
]
