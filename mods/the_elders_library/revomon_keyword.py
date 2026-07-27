import asyncio
from typing import Any

import discord
from discord.ext import commands

from utils.button_utils import MonPaginationView, get_book_of_mon_names


class allrevomon(commands.Cog):  # noqa: N801
    def __init__(self, gradex: Any) -> None:
        self.gradex = gradex

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        print("The Elder's Library(All Revomon Keyword) is ready!")
        print("---------------------------")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        try:
            # Ignore messages from bots (including self)
            if message.author.bot:
                return

            # Save User's Cleaned Input As The Search Prompt
            prompt = message.content.lower().strip()
            if prompt == "all revomon":
                book_of_names = await get_book_of_mon_names()
                view = MonPaginationView(
                    bot=self.gradex,
                    user_id=message.author.id,
                    book_of_names=book_of_names,
                    current_page=1,
                    group_by_evo=True,
                    app_emojis={},
                )
                for page in view:
                    await message.author.send(view=page)
                    asyncio.sleep(1)  # type: ignore[unused-coroutine]
        except Exception as e:
            print(f"An error occurred during on_message: {e}")


async def setup(gradex: commands.Bot) -> None:
    await gradex.add_cog(allrevomon(gradex))
