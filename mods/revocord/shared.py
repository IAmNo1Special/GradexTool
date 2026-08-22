"""Shared utilities for Discord bot mods.revocord.

Account state lives in the SQLite ``accounts`` table (scripts.gradexDB).
The legacy ``data/accounts.json`` store is seeded into SQLite once, on the
first account access after deploy, then retired.
"""

import functools
import logging
import typing
from collections.abc import Callable, Coroutine
from pathlib import Path
from typing import Any, TypeVar

import discord
from discord import app_commands, ui

from scripts.gradexDB import AccountsTable

logger = logging.getLogger("discord_bot")

T = TypeVar("T")

BASE_DIR = Path(__file__).parent.parent.parent
ACCOUNTS_FILE = BASE_DIR / "data" / "accounts.json"

_accounts_table: AccountsTable | None = None
_seed_attempted = False


def get_accounts_table() -> AccountsTable:
    """Process-wide AccountsTable singleton."""
    global _accounts_table
    if _accounts_table is None:
        _accounts_table = AccountsTable()
    return _accounts_table


async def _ensure_legacy_seeded(table: AccountsTable) -> None:
    """Seed the legacy JSON store into SQLite exactly once per process."""
    global _seed_attempted
    if _seed_attempted:
        return
    _seed_attempted = True
    try:
        if await table.count_accounts() > 0:
            return  # already migrated or has live data
        imported = await table.seed_from_legacy_json(ACCOUNTS_FILE)
        if imported:
            logger.info(
                "Seeded %d accounts from legacy %s", imported, ACCOUNTS_FILE.name
            )
            migrated_path = ACCOUNTS_FILE.with_suffix(".migrated.json")
            try:
                ACCOUNTS_FILE.rename(migrated_path)
                logger.info("Legacy account file retired to %s", migrated_path.name)
            except OSError as e:
                logger.warning(
                    "Could not retire legacy account file: %s "
                    "(INSERT OR IGNORE keeps re-seeding safe)",
                    e,
                )
    except Exception as e:
        logger.error("Legacy account seed failed: %s", e, exc_info=True)


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


async def get_or_create_account(user_id: int) -> dict[str, Any]:
    """Get an account by user ID, or create a new one with defaults."""
    table = get_accounts_table()
    await _ensure_legacy_seeded(table)
    account = await table.get_or_create_account(user_id)
    # Legacy JSON store exposed booleans for is_logged_in; keep parity.
    account["is_logged_in"] = bool(account.get("is_logged_in"))
    return account


async def update_account(user_id: int, **kwargs: Any) -> dict[str, Any]:
    """Update specific fields of an account."""
    table = get_accounts_table()
    await _ensure_legacy_seeded(table)
    if "is_logged_in" in kwargs and isinstance(kwargs["is_logged_in"], bool):
        kwargs["is_logged_in"] = int(kwargs["is_logged_in"])
    account = await table.update_account(user_id, **kwargs)
    account["is_logged_in"] = bool(account.get("is_logged_in"))
    return account


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


def is_server_owner() -> typing.Callable[..., Any]:
    """Check if the command invoker is the absolute server owner."""

    async def predicate(interaction: discord.Interaction) -> bool:
        if not interaction.guild:
            return False
        return interaction.user.id == interaction.guild.owner_id

    return app_commands.check(predicate)
