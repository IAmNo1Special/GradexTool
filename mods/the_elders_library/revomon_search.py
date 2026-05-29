from data.gradexDB import RevomonTable
from discord import Client, Message
from discord.ext import commands

from utils.button_utils import Buttons
from utils.embed_utils import compare_intros, intro
from utils.helpers import respond
from utils.revomon_utils import get_attributes


class revomon_search(commands.Cog):
    def __init__(self, gradex: Client):
        self.gradex = gradex
        self.selected_mon_message = None

    @commands.Cog.listener()
    async def on_ready(self):
        print("The Elder's Library(Revomon Search) is ready!")
        print("---------------------------")

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        try:
            # Ignore messages from bots (including self)
            if message.author.bot:
                return

            # Save User's Cleaned Input As The Search Prompt
            prompt = message.content.lower().strip()
            buttons = Buttons(self.gradex)
            if "&" in prompt:
                prompt, prompt2 = map(str.strip, prompt.split("&"))
                if (
                    prompt in RevomonTable().get_names()
                    and prompt2 in RevomonTable().get_names()
                ):
                    attributes = get_attributes(revomon_name=prompt)
                    attributes2 = get_attributes(revomon_name=prompt2)
                    embed = compare_intros(
                        attributes=attributes, attributes2=attributes2
                    )
                    buttons = await buttons.compare_intros_view(
                        attributes=attributes, attributes2=attributes2
                    )
                    await respond(self.gradex, message, embed, buttons)
            # Check if User's Prompt is a Revomon's Name
            elif prompt in RevomonTable().get_names():
                # Load Data From Revomon Database
                attributes = get_attributes(revomon_name=prompt)
                embed = intro(attributes=attributes)
                buttons = await buttons.intro_view(attributes=attributes)
                await respond(self.gradex, message, embed, buttons)
        except Exception as e:
            print(f"An error occurred during revomon_search on_message: {e}")


async def setup(gradex: commands.Bot):
    await gradex.add_cog(revomon_search(gradex))
