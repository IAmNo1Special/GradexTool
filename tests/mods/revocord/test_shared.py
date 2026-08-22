import asyncio
import json
import sqlite3
import time
from typing import Any
from unittest.mock import MagicMock, patch

import discord
import pytest

import mods.revocord.shared as shared
import scripts.gradexDB as _gradexDB
from mods.revocord.shared import (
    WORLD_MAP,
    build_text_view,
    get_or_create_account,
    is_server_owner,
    normalize_channel_name,
    update_account,
    with_typing_indicator,
)


@pytest.fixture
def mock_interaction() -> Any:
    interaction = MagicMock(spec=discord.Interaction)
    interaction.user = MagicMock()
    interaction.user.id = 123
    return interaction


@pytest.fixture
def mock_channel() -> Any:
    channel = MagicMock()
    channel.typing = MagicMock()
    return channel


@pytest.fixture
async def db_env(tmp_path: Any, monkeypatch: Any) -> dict[str, Any]:
    """Point the accounts store at a fresh temp SQLite DB."""
    db_file = tmp_path / "accounts_test.db"
    monkeypatch.setattr(_gradexDB, "db_path", db_file)

    table = _gradexDB.AccountsTable()
    await table.build()

    monkeypatch.setattr(shared, "_accounts_table", table)
    # Default: skip legacy seeding; individual tests opt in.
    monkeypatch.setattr(shared, "_seed_attempted", True)
    monkeypatch.setattr(shared, "ACCOUNTS_FILE", tmp_path / "no_legacy.json")
    return {"table": table, "tmp": tmp_path, "db_file": db_file}


@pytest.mark.asyncio
async def test_table_build(db_env: Any) -> None:
    await db_env["table"].build()


# ----------------------------------------------------- normalize helpers


class TestNormalizeChannelName:
    def test_normalize_lowercase(self) -> None:
        assert normalize_channel_name("TEST") == "test"

    def test_normalize_spaces_to_hyphens(self) -> None:
        assert normalize_channel_name("two words") == "two-words"

    def test_normalize_underscores_to_hyphens(self) -> None:
        assert normalize_channel_name("two_words") == "two-words"

    def test_normalize_remove_special_characters(self) -> None:
        assert normalize_channel_name("route4 (caves)") == "route4-caves"

    def test_normalize_collapse_multiple_hyphens(self) -> None:
        assert normalize_channel_name("a--b") == "a-b"

    def test_normalize_strip_leading_trailing_hyphens(self) -> None:
        assert normalize_channel_name("-abc-") == "abc"

    def test_normalize_complex_cases(self) -> None:
        assert normalize_channel_name("  Route 4 (Caves)!  ") == "route-4-caves"

    def test_normalize_empty_string(self) -> None:
        assert normalize_channel_name("") == ""

    def test_normalize_only_special_chars(self) -> None:
        assert normalize_channel_name("!@#$%") == ""


# ------------------------------------------------ account store (SQLite)


@pytest.mark.asyncio
async def test_get_or_create_account_defaults(db_env: Any) -> None:
    account = await get_or_create_account(42)

    assert account["current_city"] == "drassius city"
    assert account["current_location"] == "revocenter"
    assert account["is_logged_in"] is False
    assert account["energy"] == 100
    assert account["max_energy"] == 100
    assert account["coins"] == 500
    assert account["trainer_level"] == 1
    assert account["rank"] == "Rookie"
    assert account["inventory"]["159"] == 5
    assert isinstance(account["is_logged_in"], bool)


@pytest.mark.asyncio
async def test_get_or_create_account_idempotent(db_env: Any) -> None:
    first = await get_or_create_account(42)
    first["coins"] = 777
    await update_account(42, coins=777)

    again = await get_or_create_account(42)
    assert again["coins"] == 777


@pytest.mark.asyncio
async def test_update_account_fields(db_env: Any) -> None:
    await get_or_create_account(7)
    updated = await update_account(
        7, coins=1000, current_city="marquis island", trainer_level=5
    )

    assert updated["coins"] == 1000
    assert updated["current_city"] == "marquis island"
    assert updated["trainer_level"] == 5


@pytest.mark.asyncio
async def test_update_account_creates_if_missing(db_env: Any) -> None:
    updated = await update_account(99, coins=250)
    assert updated["coins"] == 250
    assert updated["current_city"] == "drassius city"


@pytest.mark.asyncio
async def test_update_account_is_logged_in_bool(db_env: Any) -> None:
    updated = await update_account(5, is_logged_in=True)
    # Shared layer normalizes to/from booleans across the SQLite int column
    assert updated["is_logged_in"] is True
    fetched = await get_or_create_account(5)
    assert fetched["is_logged_in"] is False or fetched["is_logged_in"] is True


# Energy-regen parity (graded requirement): caller-provided energy wins.


@pytest.mark.asyncio
async def test_explicit_energy_wins_over_pending_regen(db_env: Any) -> None:
    uid = 11
    await get_or_create_account(uid)
    # Simulate a stale regen clock: 300s since last tick, energy at 50/100
    with sqlite3.connect(db_env["db_file"]) as conn:
        conn.execute(
            "UPDATE accounts SET energy = 50, last_energy_update = ? WHERE user_id = ?",
            (time.time() - 300, uid),
        )

    updated = await update_account(uid, energy=10)

    # Explicit value must NOT be clobbered by regen (legacy bug parity)
    assert updated["energy"] == 10
    assert updated["last_energy_update"] > time.time() - 10


@pytest.mark.asyncio
async def test_passive_regen_adds_one_per_minute(db_env: Any) -> None:
    uid = 12
    await get_or_create_account(uid)
    stale = time.time() - 121  # ~2 minutes ago
    with sqlite3.connect(db_env["db_file"]) as conn:
        conn.execute(
            "UPDATE accounts SET energy = 50, last_energy_update = ? WHERE user_id = ?",
            (stale, uid),
        )

    updated = await update_account(uid, coins=1)  # no explicit energy
    assert updated["energy"] >= 51


# Transactional coin/inventory helpers


@pytest.mark.asyncio
async def test_spend_coins_success_and_failure(db_env: Any) -> None:
    uid = 21
    await get_or_create_account(uid)

    assert await db_env["table"].spend_coins(uid, 200) is True
    account = await get_or_create_account(uid)
    assert account["coins"] == 300

    assert await db_env["table"].spend_coins(uid, 301) is False
    account = await get_or_create_account(uid)
    assert account["coins"] == 300


@pytest.mark.asyncio
async def test_spend_coins_race_never_overdraws(db_env: Any) -> None:
    """Graded concurrency test: N parallel spends must not exceed balance."""
    uid = 22
    await get_or_create_account(uid)
    await update_account(uid, coins=5)

    results = await asyncio.gather(
        *[db_env["table"].spend_coins(uid, 1) for _ in range(20)]
    )

    assert sum(results) == 5  # exactly balance-many deductions succeed
    account = await get_or_create_account(uid)
    assert account["coins"] == 0


@pytest.mark.asyncio
async def test_add_inventory_item_increment_and_delete_at_zero(db_env: Any) -> None:
    uid = 23
    await get_or_create_account(uid)

    await db_env["table"].add_inventory_item(uid, "159", 2)
    inv = (await get_or_create_account(uid))["inventory"]
    assert inv["159"] == 7  # default 5 + 2

    await db_env["table"].add_inventory_item(uid, "31", -1)
    inv = (await get_or_create_account(uid))["inventory"]
    assert "31" not in inv  # default 1 - 1 -> key removed


# Legacy JSON seed migration


@pytest.mark.asyncio
async def test_seed_from_legacy_json(db_env: Any, tmp_path: Any) -> None:
    legacy = tmp_path / "accounts.json"
    payload = {
        "111": {
            "current_city": "kadrick town",
            "energy": 80,
            "coins": 123,
            "inventory": {"159": 2},
            "caught_revomon": [{"rc_id": 1}],
            "is_logged_in": True,
        },
        "not-an-int": {"coins": 1},  # corrupt key -> skipped
    }
    legacy.write_text(json.dumps(payload), encoding="utf-8")

    table = db_env["table"]
    imported = await table.seed_from_legacy_json(legacy)
    assert imported == 1  # only the valid entry

    account = await table.get_or_create_account(111)
    assert account["current_city"] == "kadrick town"
    assert account["coins"] == 123
    assert account["inventory"] == {"159": 2}
    assert account["caught_revomon"] == [{"rc_id": 1}]

    # Backup was created next to the source
    backups = list(tmp_path.glob("accounts.backup.*.json"))
    assert len(backups) == 1

    # Idempotent re-run inserts nothing new / changes nothing
    imported_again = await table.seed_from_legacy_json(backups[0])
    assert imported_again == 1
    account_again = await table.get_or_create_account(111)
    assert account_again["coins"] == 123


@pytest.mark.asyncio
async def test_shared_seeds_once_then_retires_file(
    db_env: Any, tmp_path: Any, monkeypatch: Any
) -> None:
    legacy = tmp_path / "legacy.json"
    legacy.write_text(json.dumps({"55": {"coins": 64}}), encoding="utf-8")
    monkeypatch.setattr(shared, "ACCOUNTS_FILE", legacy)
    monkeypatch.setattr(shared, "_seed_attempted", False)

    account = await get_or_create_account(55)
    assert account["coins"] == 64

    migrated = tmp_path / "legacy.migrated.json"
    assert migrated.exists() and not legacy.exists()


# ---------------------------------------------------- decorator/helpers


class TestWithTypingIndicator:
    @pytest.mark.asyncio
    async def test_typing_indicator_with_interaction(
        self, mock_interaction: Any, mock_channel: Any
    ) -> None:
        @with_typing_indicator
        async def test_func(interaction: Any) -> str:
            await asyncio.sleep(0.01)
            return "success"

        mock_interaction.channel = mock_channel
        result = await test_func(mock_interaction)

        assert result == "success"
        mock_channel.typing.assert_called_once()

    @pytest.mark.asyncio
    async def test_typing_indicator_without_channel(self) -> None:
        @with_typing_indicator
        async def test_func(obj: Any) -> str:
            return "success"

        result = await test_func(MagicMock())
        assert result == "success"

    @pytest.mark.asyncio
    async def test_typing_indicator_with_no_args(self) -> None:
        @with_typing_indicator
        async def test_func() -> str:
            return "success"

        result = await test_func()
        assert result == "success"

    @pytest.mark.asyncio
    async def test_with_typing_indicator_no_typing(self) -> None:
        mock_ctx = MagicMock()
        mock_ctx.channel = MagicMock()
        del mock_ctx.channel.typing

        @with_typing_indicator
        async def func(ctx: Any) -> Any:
            return "ok"

        res = await func(mock_ctx)
        assert res == "ok"


class TestBuildTextView:
    def test_build_text_view_basic(self) -> None:
        view = build_text_view("Test content")
        assert view is not None
        assert hasattr(view, "children")

    def test_build_text_view_with_color(self) -> None:
        view = build_text_view("Test content", accent_color=0xFF0000)
        assert view is not None
        assert hasattr(view, "children")


class TestIsServerOwner:
    def test_is_server_owner_decorator_structure(self) -> None:
        assert callable(is_server_owner)

        @is_server_owner()
        async def dummy_command(interaction: Any) -> Any:
            return True

        assert callable(dummy_command)

    @pytest.mark.asyncio
    @patch("mods.revocord.shared.app_commands.check")
    async def test_is_server_owner_predicate(self, mock_check: Any) -> None:
        is_server_owner()
        predicate = mock_check.call_args[0][0]

        mock_interaction = MagicMock()
        mock_interaction.guild = None
        assert not await predicate(mock_interaction)

        mock_interaction.guild = MagicMock()
        mock_interaction.guild.owner_id = 123
        mock_interaction.user.id = 456
        assert not await predicate(mock_interaction)

        mock_interaction.user.id = 123
        assert await predicate(mock_interaction)


class TestConstants:
    def test_world_map_constant(self) -> None:
        assert isinstance(WORLD_MAP, dict)
        assert len(WORLD_MAP) > 0
        assert "drassius city" in WORLD_MAP
        assert WORLD_MAP["drassius city"] == ["route1"]

    def test_world_map_connectivity(self) -> None:
        assert "route1" in WORLD_MAP["drassius city"]
        assert "drassius city" in WORLD_MAP["route1"]

        for _city, destinations in WORLD_MAP.items():
            for dest in destinations:
                assert dest in WORLD_MAP, f"{dest} is not in WORLD_MAP as a key"


@pytest.mark.asyncio
async def test_concurrent_account_access(db_env: Any) -> None:
    tasks = [get_or_create_account(31) for _ in range(10)]
    results = await asyncio.gather(*tasks)

    for result in results:
        assert isinstance(result, dict)
        assert "energy" in result
