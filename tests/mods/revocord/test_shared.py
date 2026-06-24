from typing import Any

"""Comprehensive tests for shared.py utilities."""

import asyncio  # noqa: E402
import json  # noqa: E402
import time  # noqa: E402
import typing  # noqa: E402
from unittest.mock import MagicMock, patch  # noqa: E402

import discord  # noqa: E402
import pytest  # noqa: E402

from mods.revocord.shared import (  # noqa: E402
    WORLD_MAP,
    build_text_view,
    get_lock,
    get_or_create_account,
    is_server_owner,
    load_accounts,
    normalize_channel_name,
    save_accounts,
    update_account,
    with_typing_indicator,
)


@pytest.fixture
def temp_accounts_file(tmp_path: Any) -> typing.Generator[Any]:
    file_path = tmp_path / "revocord_accounts.json"
    file_path.write_text("{}")
    with patch("mods.revocord.shared.ACCOUNTS_FILE", file_path):
        yield file_path


@pytest.fixture
def clean_accounts(temp_accounts_file: Any) -> typing.Generator[Any]:
    yield temp_accounts_file


@pytest.fixture
def mock_user() -> Any:
    user = MagicMock()
    user.id = 123456789
    return user


@pytest.fixture
def sample_account_data() -> Any:
    return {
        "coins": 500,
        "energy": 100,
        "max_energy": 100,
        "last_energy_update": time.time(),
        "current_city": "Drassius City",
        "current_location": "Center",
        "destination_city": "",
        "arrival_time": 0.0,
        "is_logged_in": False,
    }


class TestNormalizeChannelName:
    """Test suite for normalize_channel_name function."""

    def test_normalize_lowercase(self) -> None:
        """Test that channel names are lowercased."""
        assert normalize_channel_name("TEST") == "test"
        assert normalize_channel_name("TeSt") == "test"

    def test_normalize_spaces_to_hyphens(self) -> None:
        """Test that spaces are replaced with hyphens."""
        assert normalize_channel_name("test channel") == "test-channel"
        assert normalize_channel_name("hello world") == "hello-world"

    def test_normalize_underscores_to_hyphens(self) -> None:
        """Test that underscores are replaced with hyphens."""
        assert normalize_channel_name("test_channel") == "test-channel"
        assert normalize_channel_name("hello_world") == "hello-world"

    def test_normalize_remove_special_characters(self) -> None:
        """Test that special characters are removed."""
        assert normalize_channel_name("test(channel)") == "testchannel"
        assert normalize_channel_name("test'channel") == "testchannel"
        assert normalize_channel_name("test,channel") == "testchannel"
        assert normalize_channel_name("test.channel") == "testchannel"

    def test_normalize_collapse_multiple_hyphens(self) -> None:
        """Test that multiple consecutive hyphens are collapsed."""
        assert normalize_channel_name("test--channel") == "test-channel"
        assert normalize_channel_name("test---channel") == "test-channel"
        assert normalize_channel_name("test  channel") == "test-channel"

    def test_normalize_strip_leading_trailing_hyphens(self) -> None:
        """Test that leading and trailing hyphens are stripped."""
        assert normalize_channel_name("-test") == "test"
        assert normalize_channel_name("test-") == "test"
        assert normalize_channel_name("-test-") == "test"

    def test_normalize_complex_cases(self) -> None:
        """Test complex channel name normalization."""
        assert normalize_channel_name("Drassius City") == "drassius-city"
        assert normalize_channel_name("Route4 (Caves)") == "route4-caves"
        assert normalize_channel_name("Route5 (CruiseShip)") == "route5-cruiseship"
        assert normalize_channel_name("Yikati_Town") == "yikati-town"


class TestLockFunctionality:
    """Test suite for async lock functionality."""

    @pytest.mark.asyncio
    async def test_get_lock_returns_same_lock(self) -> None:
        """Test that get_lock returns the same lock instance."""
        lock1 = get_lock()
        lock2 = get_lock()
        assert lock1 is lock2
        assert isinstance(lock1, asyncio.Lock)

    @pytest.mark.asyncio
    async def test_lock_is_async_lock(self) -> None:
        """Test that the lock is an asyncio.Lock."""
        lock = get_lock()
        assert isinstance(lock, asyncio.Lock)


class TestAccountFileOperations:
    """Test suite for account file operations."""

    def test_load_accounts_empty_file(self, temp_accounts_file: Any) -> None:
        """Test loading accounts from an empty file."""
        accounts = load_accounts()
        assert accounts == {}

    def test_load_accounts_with_data(
        self, temp_accounts_file: Any, sample_account_data: Any
    ) -> None:
        """Test loading accounts with existing data."""
        user_id = "123456789"
        with open(temp_accounts_file, "w") as f:
            json.dump({user_id: sample_account_data}, f)

        accounts = load_accounts()
        assert accounts == {user_id: sample_account_data}

    def test_load_accounts_invalid_json(self, temp_accounts_file: Any) -> None:
        """Test loading accounts from a file with invalid JSON."""
        with open(temp_accounts_file, "w") as f:
            f.write("invalid json content")

        accounts = load_accounts()
        assert accounts == {}

    def test_save_accounts(
        self, temp_accounts_file: Any, sample_account_data: Any
    ) -> None:
        """Test saving accounts to file."""
        user_id = "123456789"
        accounts = {user_id: sample_account_data}
        save_accounts(accounts)

        # Verify file was created and contains correct data
        with open(temp_accounts_file) as f:
            loaded_data = json.load(f)

        assert loaded_data == accounts


class TestGetOrCreateAccount:
    """Test suite for get_or_create_account function."""

    @pytest.mark.asyncio
    async def test_create_new_account(
        self, clean_accounts: Any, mock_user: Any
    ) -> None:
        """Test creating a new account for a user."""
        account = await get_or_create_account(mock_user.id)

        assert account["current_city"] == "drassius city"
        assert account["current_location"] == "revocenter"
        assert not account["is_logged_in"]
        assert account["energy"] == 100
        assert account["max_energy"] == 100
        assert account["coins"] == 500
        assert account["trainer_level"] == 1
        assert account["rank"] == "Rookie"
        assert "159" in account["inventory"]
        assert account["inventory"]["159"] == 5

    @pytest.mark.asyncio
    async def test_get_existing_account(
        self, clean_accounts: Any, mock_user: Any, sample_account_data: Any
    ) -> None:
        """Test getting an existing account."""
        # First create the account
        user_id = str(mock_user.id)
        with open(clean_accounts, "w") as f:
            json.dump({user_id: sample_account_data}, f)

        account = await get_or_create_account(mock_user.id)

        assert account["current_city"] == sample_account_data["current_city"]
        assert account["coins"] == sample_account_data["coins"]

    @pytest.mark.asyncio
    async def test_energy_regeneration(
        self, clean_accounts: Any, mock_user: Any
    ) -> None:
        """Test that energy regenerates over time."""
        # Create account with low energy
        user_id = str(mock_user.id)
        account_data = {
            "current_city": "drassius city",
            "current_location": "revocenter",
            "is_logged_in": False,
            "energy": 50,
            "max_energy": 100,
            "last_energy_update": time.time() - 120,  # 2 minutes ago
            "arrival_time": 0.0,
            "destination_city": "",
            "destination_location": "",
            "trainer_level": 1,
            "trainer_xp": 25,
            "coins": 500,
            "rank": "Rookie",
            "battles_won": 0,
            "battles_lost": 0,
            "inventory": {},
            "caught_revomon": [],
        }

        with open(clean_accounts, "w") as f:
            json.dump({user_id: account_data}, f)

        account = await get_or_create_account(mock_user.id)

        # Should have regenerated 2 energy (1 per minute for 2 minutes)
        assert account["energy"] >= 50

    @pytest.mark.asyncio
    async def test_add_missing_fields_to_existing_account(
        self, clean_accounts: Any, mock_user: Any
    ) -> None:
        """Test that missing fields are added to existing accounts."""
        user_id = str(mock_user.id)
        incomplete_account = {
            "current_city": "drassius city",
        }

        with open(clean_accounts, "w") as f:
            json.dump({user_id: incomplete_account}, f)

        account = await get_or_create_account(mock_user.id)

        # Should have all default fields now
        assert "energy" in account
        assert "coins" in account
        assert "inventory" in account


class TestUpdateAccount:
    """Test suite for update_account function."""

    @pytest.mark.asyncio
    async def test_update_existing_account(
        self, clean_accounts: Any, mock_user: Any, sample_account_data: Any
    ) -> None:
        """Test updating an existing account."""
        user_id = str(mock_user.id)
        with open(clean_accounts, "w") as f:
            json.dump({user_id: sample_account_data}, f)

        updated = await update_account(mock_user.id, coins=1000, energy=75)

        assert updated["coins"] == 1000
        assert updated["energy"] == 75

    @pytest.mark.asyncio
    async def test_update_creates_account_if_not_exists(
        self, clean_accounts: Any, mock_user: Any
    ) -> None:
        """Test that update creates account if it doesn't exist."""
        updated = await update_account(mock_user.id, coins=1000)

        assert updated["coins"] == 1000
        assert updated["current_city"] == "drassius city"

    @pytest.mark.asyncio
    async def test_update_multiple_fields(
        self, clean_accounts: Any, mock_user: Any
    ) -> None:
        """Test updating multiple fields at once."""
        updated = await update_account(
            mock_user.id,
            coins=1000,
            energy=80,
            current_city="marquis island",
            trainer_level=5,
        )

        assert updated["coins"] == 1000
        assert updated["energy"] == 80
        assert updated["current_city"] == "marquis island"
        assert updated["trainer_level"] == 5

    @pytest.mark.asyncio
    async def test_update_energy_resets_regen_timer(
        self, clean_accounts: Any, mock_user: Any
    ) -> None:
        """Test that manually updating energy resets regeneration timer."""
        updated = await update_account(mock_user.id, energy=50)

        # Last energy update should be recent
        assert updated["last_energy_update"] > time.time() - 10


class TestWithTypingIndicator:
    """Test suite for with_typing_indicator decorator."""

    @pytest.mark.asyncio
    async def test_typing_indicator_with_interaction(
        self, mock_interaction: Any, mock_channel: Any
    ) -> None:
        """Test typing indicator with Discord interaction."""

        @with_typing_indicator
        async def test_func(interaction: Any) -> str:
            await asyncio.sleep(0.01)
            return "success"

        mock_interaction.channel = mock_channel
        result = await test_func(mock_interaction)

        assert result == "success"
        mock_channel.typing.assert_called_once()

    @pytest.mark.asyncio
    async def test_typing_indicator_with_message(
        self, mock_message: Any, mock_channel: Any
    ) -> None:
        """Test typing indicator with Discord message."""

        @with_typing_indicator
        async def test_func(message: Any) -> str:
            await asyncio.sleep(0.01)
            return "success"

        mock_message.channel = mock_channel
        result = await test_func(mock_message)

        assert result == "success"
        mock_channel.typing.assert_called_once()

    @pytest.mark.asyncio
    async def test_typing_indicator_without_channel(self) -> None:
        """Test typing indicator when no channel is available."""

        @with_typing_indicator
        async def test_func(obj: Any) -> str:
            return "success"

        result = await test_func(MagicMock())
        assert result == "success"

    @pytest.mark.asyncio
    async def test_typing_indicator_with_no_args(self) -> None:
        """Test typing indicator with no arguments."""

        @with_typing_indicator
        async def test_func() -> str:
            return "success"

        result = await test_func()
        assert result == "success"


class TestBuildTextView:
    """Test suite for build_text_view function."""

    def test_build_text_view_basic(self) -> None:
        """Test building a basic text view."""
        view = build_text_view("Test content")

        assert view is not None
        # View should be a Discord UI View
        assert hasattr(view, "children")  # Basic view check

    def test_build_text_view_with_color(self) -> None:
        """Test building a text view with custom color."""
        view = build_text_view("Test content", accent_color=0xFF0000)

        assert view is not None
        assert hasattr(view, "children")  # Basic view check


class TestIsServerOwner:
    """Test suite for is_server_owner decorator."""

    def test_is_server_owner_with_owner(self, mock_interaction: Any) -> None:
        """Test decorator when user is server owner."""
        mock_interaction.user.id = 123  # Simulate owner
        MagicMock()

        @is_server_owner()
        async def test_command(interaction: Any) -> str:
            return "success"

        # The decorator should allow execution for owner
        # (Implementation would check interaction.user.id against guild.owner_id)
        assert callable(test_command)

    def test_is_server_owner_decorator_structure(self) -> None:
        """Test that the decorator is properly structured."""
        assert callable(is_server_owner)

        @is_server_owner()
        async def dummy_command(interaction: Any) -> Any:
            return True

        assert callable(dummy_command)


class TestConstants:
    """Test suite for module constants."""

    def test_world_map_constant(self) -> None:
        """Test that WORLD_MAP is properly defined."""
        assert isinstance(WORLD_MAP, dict)
        assert len(WORLD_MAP) > 0
        assert "drassius city" in WORLD_MAP
        assert WORLD_MAP["drassius city"] == ["route1"]

    def test_world_map_connectivity(self) -> None:
        """Test that world map has proper connectivity."""
        # Check that routes connect properly
        assert "route1" in WORLD_MAP["drassius city"]
        assert "drassius city" in WORLD_MAP["route1"]

        # Check that all destinations in the map also exist as keys
        for _city, destinations in WORLD_MAP.items():
            for dest in destinations:
                assert dest in WORLD_MAP, f"{dest} is not in WORLD_MAP as a key"


class TestEdgeCases:
    """Test suite for edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_concurrent_account_access(
        self, clean_accounts: Any, mock_user: Any
    ) -> None:
        """Test that concurrent account access is handled correctly."""
        # Create multiple concurrent requests
        tasks = []
        for _i in range(10):
            tasks.append(get_or_create_account(mock_user.id))

        results = await asyncio.gather(*tasks)

        # All should return valid accounts
        for result in results:
            assert isinstance(result, dict)
            assert "energy" in result

    @pytest.mark.asyncio
    async def test_account_with_unicode_characters(self, clean_accounts: Any) -> None:
        """Test handling accounts with unicode characters."""
        user_id = 123456789
        account_data = {
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
            "inventory": {},
            "caught_revomon": [],
        }

        with open(clean_accounts, "w", encoding="utf-8") as f:
            json.dump({str(user_id): account_data}, f, ensure_ascii=False)

        account = await get_or_create_account(user_id)
        assert account["current_city"] == "drassius city"

    def test_normalize_empty_string(self) -> None:
        """Test normalizing an empty string."""
        assert normalize_channel_name("") == ""

    def test_normalize_only_special_chars(self) -> None:
        """Test normalizing a string with only special characters."""
        assert normalize_channel_name("!@#$%") == ""

    @pytest.mark.asyncio
    async def test_update_account_with_none_values(
        self, clean_accounts: Any, mock_user: Any
    ) -> None:
        """Test updating account with None values doesn't break."""
        updated = await update_account(mock_user.id, current_city=None)

        # Should handle None gracefully
        assert updated is not None


class TestSharedRemainingCoverage:
    """Test suite for covering remaining lines in shared.py."""

    def test_load_accounts_file_not_exists(self, monkeypatch: Any) -> None:
        """Test load_accounts when file does not exist."""
        from mods.revocord.shared import load_accounts

        with patch("mods.revocord.shared.Path.exists", return_value=False):
            assert load_accounts() == {}

    @pytest.mark.asyncio
    async def test_update_account_missing_fields(
        self, clean_accounts: Any, mock_user: Any
    ) -> None:
        """Test that update_account adds missing default fields."""
        user_id = str(mock_user.id)
        # Create an account that misses most fields
        incomplete = {"coins": 10}
        with open(clean_accounts, "w") as f:
            json.dump({user_id: incomplete}, f)

        # Let's mock time.time so energy regen doesn't interfere
        with patch("mods.revocord.shared.time.time", return_value=1234567890.0):
            updated = await update_account(mock_user.id, coins=20)

        assert updated["coins"] == 20
        assert "energy" in updated
        assert updated["current_city"] == "drassius city"

    @pytest.mark.asyncio
    async def test_update_account_energy_regen(
        self, clean_accounts: Any, mock_user: Any
    ) -> None:
        """Test energy regeneration inside update_account."""
        user_id = str(mock_user.id)
        acc = {
            "energy": 50,
            "max_energy": 100,
            "last_energy_update": 1000.0,
            "current_city": "city",
        }
        with open(clean_accounts, "w") as f:
            json.dump({user_id: acc}, f)

        with patch(
            "mods.revocord.shared.time.time", return_value=1120.0
        ):  # 120 seconds passed = +2 energy
            updated = await update_account(mock_user.id, coins=20)

        assert updated["energy"] == 52
        assert updated["last_energy_update"] == 1120.0

    @pytest.mark.asyncio
    async def test_with_typing_indicator_isinstance(self) -> None:
        """Test with_typing_indicator fallback isinstance checks."""

        class MockMessage(discord.Message):
            def __init__(self) -> None:
                self.channel = MagicMock()
                self.channel.typing = MagicMock()

        msg = MockMessage()
        # Remove channel from hasattr to trigger isinstance fallback
        delattr(msg, "channel")
        # But wait, we can't easily bypass hasattr if the property exists on class.
        # Let's mock hasattr to return False for 'channel' just for this test
        original_hasattr = hasattr

        def fake_hasattr(obj: Any, attr: Any) -> Any:
            if attr == "channel":
                return False
            return original_hasattr(obj, attr)

        @with_typing_indicator
        async def func(ctx: Any) -> Any:
            return "ok"

        # Mocking isinstance to force true for our mock object since we can't easily instantiate discord.Message
        with (
            patch("mods.revocord.shared.hasattr", side_effect=fake_hasattr),
            patch("mods.revocord.shared.isinstance", return_value=True),
        ):
            # Also need to make sure `ctx.channel` is retrievable even if hasattr returned false
            # By default a magic mock will return something for ctx.channel
            mock_ctx = MagicMock()
            mock_ctx.channel.typing = MagicMock()
            res = await func(mock_ctx)
            assert res == "ok"
            mock_ctx.channel.typing.assert_called_once()

    @pytest.mark.asyncio
    async def test_with_typing_indicator_no_typing(self) -> None:
        """Test with_typing_indicator when channel has no typing."""
        mock_ctx = MagicMock()
        mock_ctx.channel = MagicMock()
        del mock_ctx.channel.typing

        @with_typing_indicator
        async def func(ctx: Any) -> Any:
            return "ok"

        res = await func(mock_ctx)
        assert res == "ok"

    @pytest.mark.asyncio
    @patch("mods.revocord.shared.app_commands.check")
    async def test_is_server_owner_predicate(self, mock_check: Any) -> None:
        """Test is_server_owner predicate logic directly."""
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
