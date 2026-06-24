from typing import Any

import discord
from discord.ext import commands

from utils.helpers import respond


class tierlist(commands.Cog):  # noqa: N801
    def __init__(self, gradex: Any) -> None:
        self.gradex = gradex

    def tierlist_embed(self) -> Any:
        embed = discord.Embed(title="Tier List", color=discord.Color.red())
        embed.set_thumbnail(
            url="https://media.discordapp.net/attachments/983557860803874826/1076036559893172354/THE_ELDER.png"
        )
        self.file = discord.File(
            "./data/Images/Tierlists/tier_list.png",
            filename="tier_list.png",
        )
        embed.set_image(url="attachment://tier_list.png")
        embed.set_footer(text="The Elder's Library · Global Revomon Association")
        return embed

    class tierlist_buttons(discord.ui.View):  # noqa: N801
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
        print("The Elder's Library(Tier List Keyword) is ready!")
        print("---------------------------")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        # Ignore messages from bots (including self)
        if message.author.bot:
            return

        try:
            prompt = message.content.lower().strip()
            if prompt == "tier list" or prompt == "tierlist":
                embed = self.tierlist_embed()
                buttons = self.tierlist_buttons()
                await respond(
                    self.gradex,
                    message=message,
                    embed=embed,
                    buttons=buttons,
                    file=self.file,
                )
        except Exception as e:
            print(f"An error occurred during on_message: {e}")


async def setup(gradex: Any) -> None:
    await gradex.add_cog(tierlist(gradex))
