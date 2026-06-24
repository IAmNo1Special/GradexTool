from typing import Any

import discord
from discord.ext import commands

from data import FruitysTable
from utils.helpers import respond


class fruity_search(commands.Cog):  # noqa: N801
    def __init__(self, gradex: Any) -> None:
        self.gradex = gradex

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        print("The Elder's Library(Fruity Search) is ready!")
        print("---------------------------")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> Any:
        async def fruity_search_embed(fruity_name: Any) -> Any:
            fruity_info = (await FruitysTable().get_info(fruity_name.lower()))[0]
            embed = discord.Embed(
                title=fruity_info[0].title(),
                description=f"*{fruity_info[1].capitalize()}*",
                color=discord.Color.red(),
            )
            embed.add_field(
                name="__**Type**__",
                value=f"*{fruity_info[2].title()}*",
                inline=False,
            )
            embed.set_thumbnail(
                url="https://media.discordapp.net/attachments/983557860803874826/1076036559893172354/THE_ELDER.png"
            )
            embed.set_footer(text="The Elder's Library · Global Revomon Association")
            return embed

        class fruity_search_buttons(discord.ui.View):  # noqa: N801
            def __init__(self) -> None:
                super().__init__(timeout=None)

            @discord.ui.button(
                label="❌", style=discord.ButtonStyle.red, custom_id="exit"
            )
            async def exit_embed(
                self,
                interaction: discord.Interaction,
                Button: discord.ui.Button[Any],  # noqa: N803
            ) -> None:
                if interaction.message:
                    await interaction.message.delete()

        # Ignore messages from bots (including self)
        if message.author.bot:
            return

        try:
            prompt = message.content.lower().strip()
            if prompt in await FruitysTable().get_names():
                embed = await fruity_search_embed(prompt)
                buttons = fruity_search_buttons()
                await respond(
                    self.gradex,
                    message=message,
                    embed=embed,
                    buttons=buttons,
                )
        except Exception as e:
            print(f"An error occurred during 'fruity_search' on_message: {e}")


async def setup(gradex: commands.Bot) -> None:
    await gradex.add_cog(fruity_search(gradex))
