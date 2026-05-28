import asyncio

import discord
from discord.ext import commands
from utils.button_utils import Buttons


class allrevomon(commands.Cog):
    def __init__(self, gradex):
        self.gradex = gradex

    @commands.Cog.listener()
    async def on_ready(self):
        print("The Elder's Library(All Revomon Keyword) is ready!")
        print("---------------------------")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        try:
            # Ignore messages from bots (including self)
            if message.author.bot:
                return

            # Save User's Cleaned Input As The Search Prompt
            prompt = message.content.lower().strip()
            if prompt == "all revomon":
                buttons = Buttons(self.gradex)
                mon_main_view = await buttons.mon_view()
                for page in mon_main_view:
                    await message.author.send(view=page)
                    asyncio.sleep(1)
        except Exception as e:
            print(f"An error occurred during on_message: {e}")


async def setup(gradex: commands.Bot):
    await gradex.add_cog(allrevomon(gradex))
