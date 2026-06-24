from typing import Any

import discord
from discord.ext import commands

from utils.helpers import respond


class Spawn(commands.Cog):
    """Spawn keyword cog for The Elder's Library."""

    def __init__(self, gradex: Any) -> None:
        self.gradex = gradex

    def spawn_embed(self) -> Any:
        """Create and return the spawn chart embed."""
        embed = discord.Embed(title="Spawn Chart", color=discord.Color.red())
        embed.add_field(name="__Morning time__", value="(4:00 to 9:59)", inline=False)
        embed.add_field(name="__Day Time__", value="(10:00 to 19:59)", inline=False)
        embed.add_field(name="__Night Time__", value="(20:00 to 3:59)", inline=False)
        embed.set_image(
            url="https://s3.amazonaws.com/appforest_uf/f1674461101975x224187182516942140/Counterdexspawnchart.png"
        )
        embed.set_thumbnail(
            url="https://s3.amazonaws.com/appforest_uf/f1674460627684x148979553672345730/Counterdexlogo.edit.png"
        )
        embed.set_footer(text="Counterdex · Global Revomon Association")
        return embed

    class SpawnButtons(discord.ui.View):
        """View for spawn chart buttons."""

        def __init__(self) -> None:
            super().__init__(timeout=None)

        @discord.ui.button(label="❌", style=discord.ButtonStyle.red, custom_id="exit")
        async def exit_embed(
            self, interaction: discord.Interaction, button: discord.ui.Button[Any]
        ) -> None:
            """Handle the exit button click."""
            if interaction.message:

                await interaction.message.delete()

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """Called when the cog is ready."""
        print("The Elder's Library(Spawn Keyword) is ready!")
        print("---------------------------")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """Called when a message is received."""
        # Ignore messages from bots (including self)
        if message.author.bot:
            return

        try:
            prompt = message.content.lower().strip()
            if prompt == "spawn":
                embed = self.spawn_embed()
                buttons = self.SpawnButtons()
                await respond(
                    self.gradex, message=message, embed=embed, buttons=buttons
                )
        except Exception as e:
            print(f"An error occurred during on_message: {e}")


async def setup(gradex: commands.Bot) -> None:
    await gradex.add_cog(Spawn(gradex))
