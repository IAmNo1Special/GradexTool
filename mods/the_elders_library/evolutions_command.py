from typing import Any

from discord import Color, Embed, Interaction, app_commands
from discord.ext import commands

from utils.revomon_utils import get_evo_trees


class Evolutions2(commands.Cog):
    def __init__(self, gradex: Any) -> None:
        self.gradex = gradex

    def evolutions_embed(self) -> Any:
        evo_trees = get_evo_trees()
        evo_trees_str = " ".join(branch for branch in evo_trees)
        embed = Embed(
            title="Full Evolutions List Pt.3",
            description=evo_trees_str,
            color=Color.red(),
        )
        embed.set_thumbnail(
            url="https://media.discordapp.net/attachments/983557860803874826/1076036559893172354/THE_ELDER.png"
        )
        embed.set_footer(text="The Elder's Library · Global Revomon Association")
        return embed

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        print("The Elder's Library(Evolutions Command) is ready!")
        print("---------------------------")

    @app_commands.command(
        name="evolutions", description="Displays the full evolution tree."
    )
    @app_commands.allowed_installs(guilds=True, users=True)
    async def evolutions(self, interaction: Interaction) -> None:
        embed = self.evolutions_embed()
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(gradex: commands.Bot) -> None:
    await gradex.add_cog(Evolutions2(gradex))
