from typing import Any
from discord import Color, Embed, Interaction, app_commands
from discord.ext import commands


class EvChart2(commands.Cog):
    def __init__(self, gradex: Any) -> None:
        self.gradex = gradex

    def evchart_embed(self) -> Any:
        embed = Embed(
            title="EV Training Chart",
            description="Effort Values",
            color=Color.red(),
        )
        embed.set_thumbnail(
            url="https://s3.amazonaws.com/appforest_uf/f1674460627684x148979553672345730/Counterdexlogo.edit.png"
        )
        embed.set_image(
            url="https://media.discordapp.net/attachments/983557860803874826/1107791599494238290/EV_Train_List.png"
        )
        embed.set_footer(text="Counterdex · Global Revomon Association")
        return embed

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        print("The Elder's Library(EV Chart Command) is ready!")
        print("---------------------------")

    @app_commands.command(name="evchart", description="Displays the EV Training Chart.")
    @app_commands.allowed_installs(guilds=True, users=True)
    async def evchart(self, interaction: Interaction) -> None:
        embed = self.evchart_embed()
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(gradex: commands.Bot) -> None:
    await gradex.add_cog(EvChart2(gradex))
