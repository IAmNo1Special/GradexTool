import asyncio
from datetime import datetime, timedelta
from io import BytesIO
from typing import Any

import discord
import pytz
from discord.ext import commands, tasks

from data import RevomonTable
from utils.revomon_utils import get_attributes
from utils.tl_img_gen import create_tier_list_with_images


class BcTierPoll(commands.Cog):
    """Baby Cup Tier Poll cog for managing tier voting and results."""

    def __init__(self, gradex: commands.Bot) -> None:
        self.gradex = gradex
        self.bc_polls: list[discord.Poll] = list()
        self.bc_img_paths: dict[str, list[str]] = {
            "S": [],
            "A": [],
            "B": [],
            "C": [],
            "D": [],
        }

    def reset(self) -> None:
        """Reset the tier poll data."""
        self.bc_polls = list()
        self.bc_img_paths = {"S": [], "A": [], "B": [], "C": [], "D": []}

    def is_new_month(self) -> Any:
        """Check if it's a new month."""
        est_tz = pytz.timezone("America/New_York")
        today = datetime.now(tz=est_tz)
        if today.day == 1:
            return True
        else:
            return False

    async def get_winning_tiers(self, poll: discord.Poll) -> Any:
        """Get the winning tiers for a poll."""
        await poll.end()
        poll_msg = poll.message
        if poll_msg is None:
            return None, []
        await self.gradex.wait_for(
            "message_edit",
            check=lambda before, after: (
                before.author == poll_msg.author and before.id == poll_msg.id
            ),
        )
        if poll_msg.poll is None:
            return None, []
        print(f"{poll_msg.poll.question}'s poll has ended")
        final_poll: Any = poll_msg.poll
        if final_poll.answers is None:
            return None, []
        votes = {answer: answer.vote_count for answer in final_poll.answers}
        mon_name = final_poll.question
        max_votes = max(votes.values())
        winning_tiers = [
            tier for tier, vote_count in votes.items() if vote_count == max_votes
        ]
        # await ended_poll.message.delete()

        return mon_name, winning_tiers

    async def create_tier_channels(self, server: discord.Guild | None) -> Any:
        """Create the tier list channels."""
        if server is None:
            return None, None, None, None
        # Get the category with the name "𝐂𝐨𝐮𝐧𝐭𝐞𝐫𝐝𝐞𝐱"
        cdex_category: Any = discord.utils.get(server.categories, name="𝐂𝐨𝐮𝐧𝐭𝐞𝐫𝐝𝐞𝐱")
        if cdex_category is None:
            return None, None, None, None

        # Check if Tier List Forum already exists, if not create them
        tier_vote_forum: Any = discord.utils.get(cdex_category.forums, name="tierlist-polls")
        while tier_vote_forum is None:
            tier_vote_forum = discord.utils.get(
                cdex_category.forums, name="tierlist-polls"
            )

        # Check if Tier List Forum already exists, if not create them
        tier_results_forum = discord.utils.get(
            cdex_category.forums, name="tierlist-results"
        )
        while tier_results_forum is None:
            tier_results_forum = discord.utils.get(
                cdex_category.forums, name="tierlist-results"
            )

        bc_vote_thread = discord.utils.get(
            tier_vote_forum.threads, name="Baby-Cup-format"
        )
        if bc_vote_thread is None:
            bc_vote_thread = await tier_vote_forum.create_thread(
                name="Baby-Cup-format",
                content="Vote which tier each Revomon in the Baby Cup belongs to.",
            )
            bc_vote_thread = discord.utils.get(
                tier_vote_forum.threads, name="Baby-Cup-format"
            )

        bc_results_thread = discord.utils.get(
            tier_results_forum.threads, name="Baby-Cup-format"
        )
        if bc_results_thread is None:
            bc_results_thread = await tier_results_forum.create_thread(
                name="Baby-Cup-format",
                content="Results of which tier each Revomon in the Baby Cup belongs to.",
            )
            bc_results_thread = discord.utils.get(
                tier_vote_forum.threads, name="Baby-Cup-format"
            )

        return (
            tier_vote_forum,
            bc_vote_thread,
            tier_results_forum,
            bc_results_thread,
        )

    async def create_polls(self, gra_server: discord.Guild | None) -> None:
        """Create the polls for the tier list."""
        if gra_server is None:
            return
        try:
            self.reset()

            _, bc_vote_thread, _, _ = await self.create_tier_channels(server=gra_server)

            # Define poll duration (31 days)
            dur = timedelta(hours=768)
            for name in await RevomonTable().get_names():
                if name == "Vyphern":
                    continue
                attribs: Any = await get_attributes(name)
                if (
                    attribs["evolution"] != "None"
                    and f"-> {name}" not in attribs["evolution_tree"]
                    or name == "Kindling"
                ):
                    # Create the poll and add answer options
                    poll: discord.Poll = discord.Poll(
                        question=name, duration=dur, multiple=False
                    )
                    poll.add_answer(text="S")
                    poll.add_answer(text="A")
                    poll.add_answer(text="B")
                    poll.add_answer(text="C")
                    poll.add_answer(text="D")

                    # Send the poll to the "gs_vote_thread"
                    await bc_vote_thread.send(poll=poll)
                    # Add the poll to the dictionary
                    self.bc_polls.append(poll)
                    await asyncio.sleep(1)

            await asyncio.sleep(2)

            if not self.update_bc_tierlist.is_running():
                self.update_bc_tierlist.start()

        except Exception as e:
            print(f"Error during Eleven's Arena(Tier list): {e}")

    async def open_polls(self) -> None:
        """Open the polls for the tier list."""
        gra_server = discord.utils.get(
            self.gradex.guilds, name="Global Revomon Association"
        )
        if gra_server is None:
            return
        cdex_category: Any = discord.utils.get(gra_server.categories, name="𝐂𝐨𝐮𝐧𝐭𝐞𝐫𝐝𝐞𝐱")
        if cdex_category is None:
            return
        voting_forum: Any = discord.utils.get(cdex_category.forums, name="tierlist-polls")
        if voting_forum is None:
            print("Creating new tier list voting forum")
            await self.create_polls(gra_server=gra_server)
        else:
            bc_vote_thread: Any = discord.utils.get(
                voting_forum.threads, name="Baby-Cup-format"
            )
            if bc_vote_thread is None:
                print("Creating new tier list voting forum")
                await self.create_polls(gra_server)

    async def create_save_send_tier_img(
        self, poll: discord.Poll, img_paths: dict[str, list[str]], format: str
    ) -> None:
        """Create, save, and send the tier list image."""
        if poll.message is None:
            return
        gra_server = poll.message.guild
        if gra_server is None:
            return
        format = format.casefold()
        full_format = "Baby Cup"
        tier_list_image = create_tier_list_with_images(
            1800, 900, img_paths, font_size=40, row_gap=20
        )
        print(f"{full_format} Tier list image created")
        tierlist_img_name = f"bc_tierlist({datetime.now().strftime('%m-%d-%Y')}).png"
        # tierlist_fp = f"./data/Images/Tierlists/{tierlist_img_name}"
        img_bytes = BytesIO()
        tier_list_image.save(img_bytes, format="PNG")
        img_bytes.seek(0)
        img_for_discord = img_bytes
        print(f"{full_format} Tier list image saved")
        _, _, _, bc_results_thread = await self.create_tier_channels(server=gra_server)
        print(f"{full_format} Tier list channels found")
        await bc_results_thread.send(
            file=discord.File(img_for_discord, filename=tierlist_img_name)
        )
        print(f"{full_format} Tier list image sent")

    async def begin_new_voting(self) -> None:
        """Begin a new month of tier voting."""
        await asyncio.sleep(5)
        print("Beginning a new month of bc tier voting...")
        await self.open_polls()

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """Called when the bot is ready and connected to Discord."""
        print("Eleven's Arena Mod(bc tierlist Mod) is ready!")
        print("---------------------------")
        await asyncio.sleep(5)
        await self.begin_new_voting()

    @tasks.loop(hours=24.0)
    async def update_bc_tierlist(self) -> None:
        """Update the Baby Cup tier list based on poll results."""
        if self.is_new_month():
            for poll in self.bc_polls:
                mon_name, bc_winning_tiers = await self.get_winning_tiers(poll=poll)

                if len(bc_winning_tiers) == 1:
                    new_tier = str(bc_winning_tiers[0])
                    print(f"{mon_name}'s new bc tier: {new_tier}")
                else:
                    attr: Any = await get_attributes(mon_name)
                    new_tier = str(attr["cdex_tier"])
                    print(f"{mon_name}'s bc tier remains unchanged: {new_tier}")

                img_path = f"./data/Images/Revomon/{mon_name.title()}-nft.png"
                self.bc_img_paths[new_tier].append(img_path)
                print("Tier list image paths created")
                await asyncio.sleep(2)

            await self.create_save_send_tier_img(
                poll=self.bc_polls[0], img_paths=self.bc_img_paths, format="bc"
            )

            if self.bc_polls[0].message is None:
                return
            forum: Any = getattr(self.bc_polls[0].message.channel, "parent", None)
            if forum is None:
                return
            bc_vote_thread: Any = discord.utils.get(
                forum.threads, name="Baby-Cup-format"
            )
            gs_vote_thread: Any = discord.utils.get(
                forum.threads, name="Global-Standard-format"
            )
            if bc_vote_thread:
                await bc_vote_thread.delete(
                    reason=f"Tier Voting For The Baby Cup Format Has Ended. {datetime.now().strftime('%m-%d-%Y')}"
                )
            while gs_vote_thread is not None:
                await asyncio.sleep(5)
                gs_vote_thread = discord.utils.get(
                    forum.threads, name="Global-Standard-format"
                )
            else:
                await self.begin_new_voting()


async def setup(gradex: commands.Bot) -> None:
    try:
        await gradex.add_cog(BcTierPoll(gradex))
    except Exception:
        print("ERROR in TierPoll 'setup' function")
