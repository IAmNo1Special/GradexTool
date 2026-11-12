"""Tests for the merged tier-list cog (mods/elevens_arena/tier_poll.py)."""

import asyncio
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from mods.elevens_arena.tier_poll import (
    BC_FORMAT,
    GS_FORMAT,
    BcTierPoll,
    GsTierPoll,
    _bc_eligible,
    _gs_eligible,
    setup,
)


class FakeThread:
    """Stand-in for a discord.Thread."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.deleted = False
        self.sent: list[Any] = []

    async def delete(self, reason: str | None = None) -> None:
        """Mark the thread deleted."""
        self.deleted = True

    async def send(self, *args: Any, **kwargs: Any) -> None:
        """Record a send."""
        self.sent.append((args, kwargs))


class FakeForum:
    """Stand-in for a discord.ForumChannel."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.threads: list[FakeThread] = []
        self.create_thread_calls: list[str] = []

    async def create_thread(self, name: str, content: str = "") -> FakeThread:
        """Create a thread and record the call."""
        self.create_thread_calls.append(name)
        thread = FakeThread(name)
        self.threads.append(thread)
        return thread


class FakeCategory:
    """Stand-in for a discord.CategoryChannel."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.forum_channels: list[FakeForum] = []
        self.create_forum_calls: list[str] = []

    async def create_forum_channel(self, name: str, topic: str = "") -> FakeForum:
        """Create a forum channel and record the call."""
        self.create_forum_calls.append(name)
        forum = FakeForum(name)
        self.forum_channels.append(forum)
        return forum


class FakeGuild:
    """Stand-in for a discord.Guild."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.categories: list[FakeCategory] = []


def make_guild(
    vote_thread: bool = True, results_thread: bool = True
) -> tuple[FakeGuild, FakeForum, FakeForum]:
    """Build a guild with tierlist forums, optionally pre-seeded with threads."""
    guild = FakeGuild("Global Revomon Association")
    category = FakeCategory("𝐂𝐨𝐮𝐧𝐭𝐞𝐫𝐝𝐞𝐱")
    guild.categories.append(category)
    vote_forum = FakeForum("tierlist-polls")
    results_forum = FakeForum("tierlist-results")
    category.forum_channels.extend([vote_forum, results_forum])
    if vote_thread:
        vote_forum.threads.append(FakeThread("Global-Standard-format"))
    if results_thread:
        results_forum.threads.append(FakeThread("Global-Standard-format"))
    return guild, vote_forum, results_forum


class TestTierFormats:
    def test_formats_point_at_each_other(self) -> None:
        assert GS_FORMAT.thread_name == "Global-Standard-format"
        assert BC_FORMAT.thread_name == "Baby-Cup-format"
        assert GS_FORMAT.other_thread_name == BC_FORMAT.thread_name
        assert BC_FORMAT.other_thread_name == GS_FORMAT.thread_name
        assert GS_FORMAT.key == "gs"
        assert BC_FORMAT.key == "bc"

    def test_gs_eligible_only_when_no_evolution(self) -> None:
        assert _gs_eligible("Pikachu", {"evolution": "None"}) is True
        assert _gs_eligible("Raichu", {"evolution": "Pikachu"}) is False

    def test_bc_eligible_unevolved_and_kindling(self) -> None:
        # Unevolved (not the end of an evolution chain) is eligible.
        assert (
            _bc_eligible("Bulby", {"evolution": "Ivy", "evolution_tree": "Bulby"})
            is True
        )
        # A middle evolution whose name appears as an evolution target is not.
        assert (
            _bc_eligible(
                "Ivy",
                {"evolution": "Venus", "evolution_tree": "Bulby -> Ivy -> Venus"},
            )
            is False
        )
        # Kindling is always eligible, even with no evolution.
        assert (
            _bc_eligible("Kindling", {"evolution": "None", "evolution_tree": ""})
            is True
        )

    def test_bc_skips_vyphern(self) -> None:
        assert "Vyphern" in BC_FORMAT.skip_names
        assert len(GS_FORMAT.skip_names) == 0

    def test_poll_question_casing(self) -> None:
        gs_cog = GsTierPoll(bot=MagicMock())
        bc_cog = BcTierPoll(bot=MagicMock())
        assert gs_cog.poll_question("pikachu") == "Pikachu"
        assert bc_cog.poll_question("pikachu") == "pikachu"

    def test_is_new_month_returns_bool(self) -> None:
        assert isinstance(GsTierPoll(bot=MagicMock()).is_new_month(), bool)


class TestCreateTierChannels:
    @pytest.mark.asyncio
    async def test_missing_results_thread_created_once_and_returned(self) -> None:
        """Old code re-fetched the results thread from the voting forum."""
        guild, vote_forum, results_forum = make_guild(
            vote_thread=True, results_thread=False
        )
        cog = GsTierPoll(bot=MagicMock())

        _, vote_thread, _, results_thread = await asyncio.wait_for(
            cog.create_tier_channels(server=guild), timeout=5
        )

        assert vote_thread.name == "Global-Standard-format"
        assert vote_forum.create_thread_calls == []
        assert results_forum.create_thread_calls == ["Global-Standard-format"]
        assert results_thread is not None
        assert results_thread.name == "Global-Standard-format"
        assert results_thread in results_forum.threads

    @pytest.mark.asyncio
    async def test_both_threads_missing_each_created_once(self) -> None:
        guild, vote_forum, results_forum = make_guild(
            vote_thread=False, results_thread=False
        )
        cog = GsTierPoll(bot=MagicMock())

        _, vote_thread, _, results_thread = await asyncio.wait_for(
            cog.create_tier_channels(server=guild), timeout=5
        )

        assert vote_forum.create_thread_calls == ["Global-Standard-format"]
        assert results_forum.create_thread_calls == ["Global-Standard-format"]
        assert vote_thread is not None and results_thread is not None

    @pytest.mark.asyncio
    async def test_existing_threads_not_recreated(self) -> None:
        guild, vote_forum, results_forum = make_guild(
            vote_thread=True, results_thread=True
        )
        cog = GsTierPoll(bot=MagicMock())

        _, vote_thread, _, results_thread = await cog.create_tier_channels(server=guild)

        assert vote_forum.create_thread_calls == []
        assert results_forum.create_thread_calls == []
        assert vote_thread.name == "Global-Standard-format"
        assert results_thread.name == "Global-Standard-format"

    @pytest.mark.asyncio
    async def test_no_server_returns_nones(self) -> None:
        cog = GsTierPoll(bot=MagicMock())
        assert await cog.create_tier_channels(server=None) == (None, None, None, None)

    @pytest.mark.asyncio
    async def test_no_counterdex_category_returns_nones(self) -> None:
        guild = FakeGuild("Global Revomon Association")
        cog = GsTierPoll(bot=MagicMock())
        assert await cog.create_tier_channels(server=guild) == (
            None,
            None,
            None,
            None,
        )


class TestSetup:
    @pytest.mark.asyncio
    async def test_setup_adds_both_format_cogs(self) -> None:
        bot = MagicMock()
        bot.add_cog = AsyncMock()

        await setup(bot)

        assert bot.add_cog.call_count == 2
        added = [call.args[0] for call in bot.add_cog.call_args_list]
        assert {cog.qualified_name for cog in added} == {"GsTierPoll", "BcTierPoll"}
        by_name = {cog.qualified_name: cog for cog in added}
        assert by_name["GsTierPoll"].format is GS_FORMAT
        assert by_name["BcTierPoll"].format is BC_FORMAT
