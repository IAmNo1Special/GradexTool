from typing import Any

from discord import ButtonStyle, Color, Embed, Interaction, app_commands, ui
from discord.ext import commands


class HelpCommand(commands.Cog):
    def __init__(self, gradex: commands.Bot) -> None:
        self.gradex = gradex

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        print("Help Command is ready!")
        print("---------------------------")

    def help_embed(self) -> Any:
        help_embed = Embed(
            title="Help Menu",
            description="Gradex Tool commands",
            color=Color.red(),
        )
        help_embed.set_thumbnail(
            url="https://media.discordapp.net/attachments/983557860803874826/1076036559893172354/THE_ELDER.png"
        )
        help_embed.set_footer(text="The Elder's Library · Global Revomon Association")
        help_embed.add_field(
            name="- **/evchart**",
            value=" - *Displays the Revomon EV chart image.*",
            inline=False,
        )
        help_embed.add_field(
            name="- **/evolutions**",
            value=" - *Displays the evolution trees for all Revomon.*",
            inline=False,
        )
        help_embed.add_field(
            name="- **/grade**", value=" - *Grade your Revomon.*", inline=False
        )
        help_embed.add_field(
            name="- **/podium**",
            value=" - *Displays the Revomon Podium Leaderboard image.*",
            inline=False,
        )
        help_embed.add_field(
            name="- **/pvp**",
            value=" - *Displays the Revomon PVP leaderboard image.*",
            inline=False,
        )
        help_embed.add_field(
            name="- **/sapdaddy**",
            value=" - *Displays SapDaddy's Library.*",
            inline=False,
        )
        help_embed.add_field(
            name="- **/search [category][keyword]**",
            value=" - *Search for information about a [keyword]. Leave [keyword] blank to display a list of all the keywords in a category.*",
            inline=False,
        )
        help_embed.add_field(
            name="**- /spawnchart**",
            value=" - *Displays the Revomon Spawn chart image.*",
            inline=False,
        )
        return help_embed

    class PublicButton(ui.View):
        def __init__(self, embed: Embed) -> None:
            self.embed = embed

            super().__init__(timeout=None)

        @ui.button(label="Make Public", style=ButtonStyle.green, custom_id="Save")
        async def make_public_button(self, interaction: Interaction, Button: ui.Button[Any]) -> None:  # noqa: N803
            try:
                await interaction.response.defer(ephemeral=False, thinking=True)
                embed = self.embed
                await interaction.followup.send(embed=embed, ephemeral=False)
            except Exception as e:
                print(
                    f"An error occurred trying to click the 'Make Public[PublicButton]' Button from the grade_command script: {e}"
                )

    @app_commands.command(
        name="help", description="Displays the Gradex Tool help menu."
    )
    @app_commands.allowed_installs(guilds=True, users=True)
    async def help(self, interaction: Interaction) -> None:
        embed = self.help_embed()
        buttons = self.PublicButton(embed=embed)
        await interaction.response.send_message(
            embed=embed, view=buttons, ephemeral=True
        )


async def setup(gradex: commands.Bot) -> None:
    try:
        await gradex.add_cog(HelpCommand(gradex))
    except Exception:
        print("ERROR in ModName 'setup' function")
