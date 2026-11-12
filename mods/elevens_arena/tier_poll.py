"""Tier List cog for managing tier voting and results.

One parameterized cog serves both voting formats (Global Standard and
Baby Cup). The two formats used to live in near-identical files
(tierlist1.py / tierlist2.py, ~285 lines each); the only real differences
were the format name, the thread name, the poll question casing, and
which Revomon are eligible for a poll. Those differences now live in a
small TierFormat record, and both cogs are thin subclasses of TierPoll.

Merging also fixes a copy-pasted bug both files shared: after creating
the results thread, the code re-fetched it from the *voting* forum
instead of the results forum, so the handle it got back was the voting
thread. The monthly results image then went to the voting thread, and
the results thread it had just made was left orphaned. (It self-healed
on the next call, once the orphan existed to be found, which is why
nobody noticed.)
"""

import asyncio
import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from io import BytesIO
from typing import Any, ClassVar

import discord
import pytz
from discord.ext import commands, tasks

from data import RevomonTable
from utils.revomon_utils import get_attributes
from utils.tl_img_gen import create_tier_list_with_images

logger = logging.getLogger(__name__)


def _gs_eligible(name: str, attribs: dict[str, Any]) -> bool:
    """Global Standard polls cover Revomon with no evolution."""
    return attribs["evolution"] == "None"


def _bc_eligible(name: str, attribs: dict[str, Any]) -> bool:
    """Baby Cup polls cover unevolved Revomon, plus Kindling."""
    return (
        attribs["evolution"] != "None" and f"-> {name}" not in attribs["evolution_tree"]
    ) or name == "Kindling"


@dataclass(frozen=True)
class TierFormat:
    """Everything that differs between the two tier-list formats."""

    key: str
    label: str
    thread_name: str
    other_thread_name: str
    title_question: bool
    eligible: Callable[[str, dict[str, Any]], bool]
    skip_names: frozenset[str] = frozenset()


GS_FORMAT = TierFormat(
    key="gs",
    label="Global Standard",
    thread_name="Global-Standard-format",
    other_thread_name="Baby-Cup-format",
    title_question=True,
    eligible=_gs_eligible,
)

BC_FORMAT = TierFormat(
    key="bc",
    label="Baby Cup",
    thread_name="Baby-Cup-format",
    other_thread_name="Global-Standard-format",
    title_question=False,
    eligible=_bc_eligible,
    skip_names=frozenset({"Vyphern"}),
)


class TierPoll(commands.Cog):
    """Tier Poll cog for managing tier voting and results for one format."""

    FORMAT: ClassVar[TierFormat]

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.format = self.FORMAT
        self.polls: list[discord.Poll] = list()
        self.img_paths: dict[str, list[str]] = {
            "S": [],
            "A": [],
            "B": [],
            "C": [],
            "D": [],
        }

    def reset(self) -> None:
        """Reset the tier poll data."""
        self.polls = list()
        self.img_paths = {"S": [], "A": [], "B": [], "C": [], "D": []}

    def is_new_month(self) -> bool:
        """Check if it's a new month."""
        est_tz = pytz.timezone("America/New_York")
        today = datetime.now(tz=est_tz)
        return today.day == 1

    def poll_question(self, name: str) -> str:
        """Question text for a poll.

        Global Standard title-cases the name; Baby Cup uses it as-is.
        """
        return name.title() if self.format.title_question else name

    async def get_winning_tiers(self, poll: discord.Poll) -> Any:
        """Get the winning tiers for a poll."""
        final_poll = await poll.end()
        if final_poll is None or final_poll.answers is None:
            return None, []
        print(f"{final_poll.question}'s poll has ended")
        votes = {answer: answer.vote_count for answer in final_poll.answers}
        mon_name = final_poll.question
        max_votes = max(votes.values())
        winning_tiers = [
            tier for tier, vote_count in votes.items() if vote_count == max_votes
        ]
        # await ended_poll.message.delete()

        return mon_name, winning_tiers

    async def create_tier_channels(self, server: discord.Guild | None) -> Any:
        """Create tier list channels."""
        if server is None:
            return None, None, None, None
        print("attempting to create tier list channels")
        # Get the category with the name "𝐂𝐨𝐮𝐧𝐭𝐞𝐫𝐝𝐞𝐱"
        cdex_category: Any = discord.utils.get(server.categories, name="𝐂𝐨𝐮𝐧𝐭𝐞𝐫𝐝𝐞𝐱")
        if cdex_category is None:
            return None, None, None, None

        # Check if Tier List Forum already exists, if not create them
        tier_vote_forum: Any = discord.utils.get(
            cdex_category.forum_channels, name="tierlist-polls"
        )
        if tier_vote_forum is None:
            tier_vote_forum = await cdex_category.create_forum_channel(
                name="tierlist-polls", topic="Tier List"
            )

        # Check if Tier List Forum already exists, if not create them
        tier_results_forum = discord.utils.get(
            cdex_category.forum_channels, name="tierlist-results"
        )
        if tier_results_forum is None:
            tier_results_forum = await cdex_category.create_forum_channel(
                name="tierlist-results", topic="Tier List Results"
            )

        vote_thread = discord.utils.get(
            tier_vote_forum.threads, name=self.format.thread_name
        )
        while vote_thread is None:
            vote_thread = await tier_vote_forum.create_thread(
                name=self.format.thread_name,
                content=(
                    "Vote which tier each Revomon in the "
                    f"{self.format.label} format belongs to."
                ),
            )
            vote_thread = discord.utils.get(
                tier_vote_forum.threads, name=self.format.thread_name
            )

        results_thread = discord.utils.get(
            tier_results_forum.threads, name=self.format.thread_name
        )
        while results_thread is None:
            results_thread = await tier_results_forum.create_thread(
                name=self.format.thread_name,
                content=(
                    "Results of which tier each Revomon in the "
                    f"{self.format.label} format belongs to."
                ),
            )
            results_thread = discord.utils.get(
                tier_results_forum.threads, name=self.format.thread_name
            )

        return (
            tier_vote_forum,
            vote_thread,
            tier_results_forum,
            results_thread,
        )

    async def create_polls(self, gra_server: discord.Guild | None = None) -> None:
        """Create tier list polls."""
        if gra_server is None:
            gra_server = discord.utils.get(
                self.bot.guilds, name="Global Revomon Association"
            )
        if gra_server is None:
            logger.error("Error during Eleven's Arena(Tier list): server not found")
            return
        try:
            self.reset()
            print(f"{self.format.key} tier list retrieved server")

            _, vote_thread, _, _ = await self.create_tier_channels(server=gra_server)
            print(f"{self.format.key} tier list channels created")

            # Define poll duration (31 days)
            dur = timedelta(hours=768)
            for name in await RevomonTable().get_names():
                if name in self.format.skip_names:
                    continue
                attribs = await get_attributes(name)
                if self.format.eligible(name, attribs):
                    # Create the poll and add answer options
                    poll: discord.Poll = discord.Poll(
                        question=self.poll_question(name), duration=dur, multiple=False
                    )
                    poll.add_answer(text="S")
                    poll.add_answer(text="A")
                    poll.add_answer(text="B")
                    poll.add_answer(text="C")
                    poll.add_answer(text="D")

                    # Send the poll to the vote thread
                    await vote_thread.send(poll=poll)
                    # Add the poll to the list
                    self.polls.append(poll)
                    await asyncio.sleep(1)

            await asyncio.sleep(2)

            if not self.update_tierlist.is_running():
                self.update_tierlist.start()

        except Exception as e:
            logger.error(f"Error during Eleven's Arena(Tier list): {e}")

    async def open_polls(self) -> None:
        """Open tier list polls."""
        gra_server = discord.utils.get(
            self.bot.guilds, name="Global Revomon Association"
        )
        if gra_server is None:
            return
        cdex_category: Any = discord.utils.get(gra_server.categories, name="𝐂𝐨𝐮𝐧𝐭𝐞𝐫𝐝𝐞𝐱")
        if cdex_category is None:
            return
        voting_forum: Any = discord.utils.get(
            cdex_category.forum_channels, name="tierlist-polls"
        )
        if voting_forum is None:
            print(f"Creating new {self.format.key} tier list voting")
            await self.create_polls(gra_server)
        else:
            vote_thread = discord.utils.get(
                voting_forum.threads, name=self.format.thread_name
            )
            if vote_thread is None:
                print(f"Creating new {self.format.key} tier list voting")
                await self.create_polls(gra_server)

    async def create_save_send_tier_img(
        self,
        poll: discord.Poll,
        img_paths: dict[str, list[str]],
    ) -> None:
        """Create, save, and send tier list image."""
        if poll.message is None:
            return
        gra_server = poll.message.guild
        if gra_server is None:
            return
        tier_list_image = create_tier_list_with_images(
            1800, 900, img_paths, font_size=40, row_gap=20
        )
        print(f"{self.format.label} Tier list image created")
        tierlist_img_name = (
            f"{self.format.key}_tierlist({datetime.now().strftime('%m-%d-%Y')}).png"
        )
        # tierlist_fp = f"./data/Images/Tierlists/{tierlist_img_name}"
        img_bytes = BytesIO()
        tier_list_image.save(img_bytes, format="PNG")
        img_bytes.seek(0)
        img_for_discord = img_bytes
        print(f"{self.format.label} Tier list image saved")
        _, _, _, results_thread = await self.create_tier_channels(server=gra_server)
        print(f"{self.format.label} Tier list channels found")
        await results_thread.send(
            file=discord.File(img_for_discord, filename=tierlist_img_name)
        )
        print(f"{self.format.label} Tier list image sent")

    async def begin_new_voting(self) -> None:
        """Begin new voting cycle."""
        await asyncio.sleep(5)
        print(f"Beginning a new month of {self.format.key} tier voting...")
        await self.open_polls()

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """Called when the bot is ready."""
        print(f"Eleven's Arena Mod({self.format.key} tierlist Mod) is ready!")
        print("---------------------------")
        await self.begin_new_voting()

    @tasks.loop(hours=24.0)
    async def update_tierlist(self) -> None:
        """Update tier list based on new month."""
        if self.is_new_month():
            for poll in self.polls:
                mon_name, winning_tiers = await self.get_winning_tiers(poll=poll)

                if len(winning_tiers) == 1:
                    new_tier = str(winning_tiers[0])
                    print(f"{mon_name}'s new tier: {new_tier}")
                else:
                    attr: Any = await get_attributes(mon_name)
                    new_tier = str(attr["cdex_tier"])
                    print(f"{mon_name}'s tier remains unchanged: {new_tier}")

                img_path = f"./data/Images/Revomon/{mon_name.title()}-nft.png"
                self.img_paths[new_tier].append(img_path)
                print("Tier list image paths created")
                await asyncio.sleep(2)

            await self.create_save_send_tier_img(
                poll=self.polls[0], img_paths=self.img_paths
            )

            if self.polls[0].message is None:
                return
            forum: Any = getattr(self.polls[0].message.channel, "parent", None)
            if forum is None:
                return
            own_vote_thread: Any = discord.utils.get(
                forum.threads, name=self.format.thread_name
            )
            other_vote_thread: Any = discord.utils.get(
                forum.threads, name=self.format.other_thread_name
            )
            if own_vote_thread:
                await own_vote_thread.delete(
                    reason=(
                        "Tier Voting For The "
                        f"{self.format.label} Format Has Ended. "
                        f"{datetime.now().strftime('%m-%d-%Y')}"
                    )
                )
            while other_vote_thread is not None:
                await asyncio.sleep(5)
                other_vote_thread = discord.utils.get(
                    forum.threads, name=self.format.other_thread_name
                )
            else:
                await self.begin_new_voting()


class GsTierPoll(TierPoll):
    """Global Standard Tier Poll cog for managing tier voting and results."""

    FORMAT = GS_FORMAT


class BcTierPoll(TierPoll):
    """Baby Cup Tier Poll cog for managing tier voting and results."""

    FORMAT = BC_FORMAT


async def setup(bot: commands.Bot) -> None:
    try:
        await bot.add_cog(GsTierPoll(bot))
        await bot.add_cog(BcTierPoll(bot))
    except Exception:
        logger.error("ERROR in TierPoll 'setup' function")
