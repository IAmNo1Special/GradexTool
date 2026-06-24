"""Shared utilities for Discord bot mods.revocord.

This module provides decorators and helpers.
"""

import asyncio
import functools
import json
import logging
import time
import typing
from collections.abc import Callable, Coroutine
from pathlib import Path
from typing import Any, TypeVar
from unittest.mock import MagicMock

import discord
from discord import app_commands, ui

logger = logging.getLogger("discord_bot")

T = TypeVar("T")

BASE_DIR = Path(__file__).parent.parent.parent
ACCOUNTS_FILE = BASE_DIR / "data" / "accounts.json"

_accounts_lock = None


def get_lock() -> asyncio.Lock:
    global _accounts_lock
    if _accounts_lock is None:
        _accounts_lock = asyncio.Lock()
    return _accounts_lock


WORLD_MAP = {
    "drassius city": ["route1"],
    "route1": ["drassius city", "marquis island"],
    "marquis island": ["route1", "route2"],
    "route2": ["marquis island", "kadrick town"],
    "kadrick town": ["route2", "route3"],
    "route3": ["kadrick town", "ramboo metropolis"],
    "ramboo metropolis": ["route3", "route4 (caves)"],
    "route4 (caves)": ["ramboo metropolis", "cinvia harbor"],
    "cinvia harbor": ["route4 (caves)", "route5 (cruiseship)"],
    "route5 (cruiseship)": ["cinvia harbor", "sakura burgh"],
    "sakura burgh": ["route5 (cruiseship)", "yikati town"],
    "yikati town": ["sakura burgh"],
}


def normalize_channel_name(name: str) -> str:
    """Normalize a channel name to match Discord's text/forum channel naming.

    Discord lowercases, replaces spaces/underscores with hyphens, and removes
    most punctuation/special characters (like parentheses, apostrophes, commas, etc.).
    """
    # 1. Lowercase
    name = name.lower()
    # 2. Replace spaces/underscores with hyphens
    name = name.replace(" ", "-").replace("_", "-")
    # 3. Keep only alphanumeric characters and hyphens
    normalized = ""
    for char in name:
        if char.isalnum() or char == "-":
            normalized += char
    # 4. Collapse multiple consecutive hyphens
    while "--" in normalized:
        normalized = normalized.replace("--", "-")
    # 5. Strip leading/trailing hyphens
    return normalized.strip("-")


def load_accounts() -> dict[str, Any]:
    """Load the accounts JSON file."""
    if not ACCOUNTS_FILE.exists():
        return {}
    with open(ACCOUNTS_FILE, encoding="utf-8") as f:
        try:
            return json.load(f)  # type: ignore[no-any-return]
        except json.JSONDecodeError:
            return {}


def save_accounts(accounts: dict[str, Any]) -> None:
    """Save the accounts JSON file."""
    ACCOUNTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(ACCOUNTS_FILE, "w", encoding="utf-8") as f:
        json.dump(accounts, f, indent=4)


async def get_or_create_account(user_id: int) -> dict[str, Any]:
    """Get an account by user ID, or create a new one with defaults."""
    async with get_lock():
        accounts = load_accounts()
        str_id = str(user_id)

        defaults = {
            "current_city": "drassius city",
            "current_location": "revocenter",
            "is_logged_in": False,
            "energy": 100,
            "max_energy": 100,
            "last_energy_update": time.time(),
            "arrival_time": 0.0,
            "destination_city": "",
            "destination_location": "",
            "trainer_level": 1,
            "trainer_xp": 25,
            "coins": 500,
            "rank": "Rookie",
            "battles_won": 0,
            "battles_lost": 0,
            "inventory": {"159": 5, "4": 2, "31": 1},
            "caught_revomon": [],
        }

        if str_id not in accounts:
            accounts[str_id] = defaults
            save_accounts(accounts)
        else:
            # Ensure existing accounts have all new fields
            modified = False
            for k, v in defaults.items():
                if k not in accounts[str_id]:
                    accounts[str_id][k] = v
                    modified = True

            # Process energy regeneration (1 energy per 60 seconds)
            acc = accounts[str_id]
            now = time.time()
            if acc["energy"] < acc["max_energy"]:
                time_passed = now - acc["last_energy_update"]
                regen = int(time_passed / 60)
                if regen > 0:
                    acc["energy"] = min(acc["max_energy"], acc["energy"] + regen)
                    acc["last_energy_update"] = now - (time_passed % 60)
                    modified = True
            else:
                acc["last_energy_update"] = now

            if modified:
                save_accounts(accounts)

        return accounts[str_id]  # type: ignore[no-any-return]


async def update_account(user_id: int, **kwargs: Any) -> dict[str, Any]:
    """Update specific fields of an account."""
    async with get_lock():
        accounts = load_accounts()
        str_id = str(user_id)

        defaults = {
            "current_city": "drassius city",
            "current_location": "revocenter",
            "is_logged_in": False,
            "energy": 100,
            "max_energy": 100,
            "last_energy_update": time.time(),
            "arrival_time": 0.0,
            "destination_city": "",
            "destination_location": "",
            "trainer_level": 1,
            "trainer_xp": 25,
            "coins": 500,
            "rank": "Rookie",
            "battles_won": 0,
            "battles_lost": 0,
            "inventory": {"159": 5, "4": 2, "31": 1},
            "caught_revomon": [],
        }

        if str_id not in accounts:
            accounts[str_id] = defaults
        else:
            for k, v in defaults.items():
                if k not in accounts[str_id]:
                    accounts[str_id][k] = v

        # Before updating, regen energy
        acc = accounts[str_id]
        now = time.time()
        if acc["energy"] < acc["max_energy"]:
            time_passed = now - acc["last_energy_update"]
            regen = int(time_passed / 60)
            if regen > 0:
                acc["energy"] = min(acc["max_energy"], acc["energy"] + regen)
                acc["last_energy_update"] = now - (time_passed % 60)
        else:
            acc["last_energy_update"] = now

        for k, v in kwargs.items():
            acc[k] = v

        # If energy was manually updated (e.g. traveling or resting)
        if "energy" in kwargs:
            acc["last_energy_update"] = now

        save_accounts(accounts)
        return accounts[str_id]  # type: ignore[no-any-return]


def with_typing_indicator[T](
    func: Callable[..., Coroutine[Any, Any, T]],
) -> Callable[..., Coroutine[Any, Any, T]]:
    """Decorator that shows typing indicator while the wrapped function runs.

    Works with both discord.Interaction and discord.Message contexts.
    The first positional argument must be the interaction or message.

    Example:
        @with_typing_indicator
        async def process_message(message: discord.Message, content: str):
            # User sees "Bot is typing..." while this runs
            await long_running_task()
    """

    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> T:
        if not args:
            return await func(*args, **kwargs)

        ctx = args[0]
        channel = None

        # Try to extract channel from different context types
        if hasattr(ctx, "channel"):
            channel = ctx.channel
        elif isinstance(ctx, (discord.Message, discord.Interaction)):
            channel = ctx.channel

        if channel and hasattr(channel, "typing"):
            async with channel.typing():
                return await func(*args, **kwargs)
        else:
            return await func(*args, **kwargs)

    return wrapper


def build_text_view(content: str, *, accent_color: int | None = None) -> ui.LayoutView:
    """Build a V2 LayoutView containing a single Container with TextDisplay.

    In Components V2, plain ``content`` fields are disabled when the
    ``IS_COMPONENTS_V2`` flag is set.  All visible text must be expressed
    through ``TextDisplay`` components inside a ``Container``.

    Args:
        content: The markdown-formatted text to display.
        accent_color: Optional accent color for the container.

    Returns:
        A ``ui.LayoutView`` ready to be passed to ``send(view=...)``.
    """
    view = ui.LayoutView()
    text_display: Any = ui.TextDisplay(content)
    container = ui.Container(text_display, accent_color=accent_color)
    view.add_item(container)
    return view


def is_server_owner() -> MagicMock | typing.Callable[..., Any]:
    """Check if the command invoker is the absolute server owner."""

    async def predicate(interaction: discord.Interaction) -> bool:
        if not interaction.guild:
            return False
        return interaction.user.id == interaction.guild.owner_id

    return app_commands.check(predicate)
