from typing import Any
from discord import Color, Embed, Interaction, app_commands
from discord.ext import commands


class Spawn2(commands.Cog):
    def __init__(self, gradex: Any) -> None:
        self.gradex = gradex

    def spawn_embed(self) -> Any:
        embed = Embed(title="Spawn Chart", color=Color.red())
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

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        print("The Elder's Library(Spawn Command) is ready!")
        print("---------------------------")

    @app_commands.command(
        name="spawnchart", description="Displays the spawn chart & spawn times."
    )
    @app_commands.allowed_installs(guilds=True, users=True)
    async def spawnchart(self, interaction: Interaction) -> None:
        embed = self.spawn_embed()
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(gradex: commands.Bot) -> None:
    await gradex.add_cog(Spawn2(gradex))
