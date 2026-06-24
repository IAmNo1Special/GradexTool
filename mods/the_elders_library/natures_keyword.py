from typing import Any

import discord
from discord.ext import commands

from utils.helpers import respond


class allnatures(commands.Cog):  # noqa: N801
    def __init__(self, gradex: Any) -> None:
        self.gradex = gradex

    def allnatures_embed(self) -> Any:
        embed = discord.Embed(
            title="Full Nature List",
            description="The Elder: Only 20 out of the total 25 natures increase one Stat by 10% while reducing another stat by 10%. 5 natures are considered neutral and have no effect at all.",
            color=discord.Color.red(),
        )
        embed.add_field(
            name="__Nature__",
            value="Bold\nModest\nCalm\nTimid\nLonely\nMild\nGentle\nHasty\nAdamant\nImpish\nCareful\nJolly\nNaughty\nLax\nRash\nNaive\nBrave\nRelaxed\nQuiet\nSassy",
            inline=False,
        )
        embed.set_thumbnail(
            url="https://media.discordapp.net/attachments/983557860803874826/1076036559893172354/THE_ELDER.png"
        )
        embed.set_image(
            url="https://s3.amazonaws.com/appforest_uf/f1674293258259x900123748435524000/NATURE%20TABLE.jpg"
        )
        embed.set_footer(text="The Elder's Library · Global Revomon Association")
        return embed

    class nature_buttons(discord.ui.View):  # noqa: N801
        def __init__(self) -> None:
            super().__init__(timeout=None)

        @discord.ui.button(label="❌", style=discord.ButtonStyle.red, custom_id="exit")
        async def exit_embed(
            self,
            interaction: discord.Interaction,
            Button: discord.ui.Button[Any],  # noqa: N803
        ) -> None:
            if interaction.message:
                await interaction.message.delete()

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        print("The Elder's Library(All Natures Keyword) is ready!")
        print("---------------------------")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        # Ignore messages from bots (including self)
        if message.author.bot:
            return

        try:
            prompt = message.content.lower().strip()
            if prompt == "all natures" or prompt == "natures":
                embed = self.allnatures_embed()
                buttons = self.nature_buttons()
                await respond(
                    self.gradex, message=message, embed=embed, buttons=buttons
                )
        except Exception as e:
            print(f"An error occurred during on_message: {e}")


async def setup(gradex: commands.Bot) -> None:
    await gradex.add_cog(allnatures(gradex))
