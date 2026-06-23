from typing import Any
from discord import ButtonStyle, Color, Embed, Interaction, app_commands, ui
from discord.ext import commands


class SapDaddy2(commands.Cog):
    def __init__(self, gradex: Any) -> None:
        self.gradex = gradex

    def sapdaddy_embed(self) -> Any:
        embed = Embed(
            title="➡Sapdaddy's Official Youtube⬅",
            description="Select a video from below.",
            url="https://www.youtube.com/@NicksGamesL33t",
            color=Color.red(),
        )
        embed.set_thumbnail(
            url="https://yt3.googleusercontent.com/lvlTdwCX8VHLYfI5i1mgVC704xzb_VlYT_XNVPEaqkY8EeMaRIJfmwnb-gZ6E1D-2wKzmRPS=s88-c-k-c0x00ffffff-no-rj"
        )
        embed.set_author(name="Sap Daddy")
        embed.set_footer(text="The Elder's Library · Global Revomon Association")
        return embed

    class sapdaddy_buttons(ui.View):
        def __init__(self) -> None:
            super().__init__(timeout=None)

        @ui.button(
            label="Does my mon have the Hidden Ability?!?",
            style=ButtonStyle.green,
            custom_id="sapdaddy1",
        )
        async def video1(self, interaction: Interaction, Button: ui.Button[Any]) -> None:
            await interaction.response.defer()
            await interaction.followup.send(
                content="[🎞](https://youtu.be/watch?v=YE8zJM_zN98)",
                ephemeral=True,
            )

        @ui.button(
            label="EV Train at GODLIKE speed!!!",
            style=ButtonStyle.green,
            custom_id="sapdaddy2",
        )
        async def video2(self, interaction: Interaction, Button: ui.Button[Any]) -> None:
            await interaction.response.defer()
            await interaction.followup.send(
                content="[🎞](https://youtu.be/watch?v=wewZChz-jlc)",
                ephemeral=True,
            )

        @ui.button(
            label="Exclusive Interview with Revomon CEO",
            style=ButtonStyle.green,
            custom_id="sapdaddy3",
        )
        async def video3(self, interaction: Interaction, Button: ui.Button[Any]) -> None:
            await interaction.response.defer()
            await interaction.followup.send(
                content="[🎞](https://www.youtube.com/watch?v=5SEzlyGON0E)",
                ephemeral=True,
            )

        @ui.button(
            label="How to Beat the Podium and Earn $$!!",
            style=ButtonStyle.green,
            custom_id="sapdaddy4",
        )
        async def video4(self, interaction: Interaction, Button: ui.Button[Any]) -> None:
            await interaction.response.defer()
            await interaction.followup.send(
                content="[🎞](https://www.youtube.com/watch?v=m9_OPeGfzE4)",
                ephemeral=True,
            )

        @ui.button(
            label="PVP Guide! (Part 1)",
            style=ButtonStyle.green,
            custom_id="sapdaddy5",
        )
        async def video5(self, interaction: Interaction, Button: ui.Button[Any]) -> None:
            await interaction.response.defer()
            await interaction.followup.send(
                content="[🎞](https://www.youtube.com/watch?v=8G3NFKtGWuo)",
                ephemeral=True,
            )

        @ui.button(
            label="PVP Guide! (Part 2)",
            style=ButtonStyle.green,
            custom_id="sapdaddy6",
        )
        async def video6(self, interaction: Interaction, Button: ui.Button[Any]) -> None:
            await interaction.response.defer()
            await interaction.followup.send(
                content="[🎞](https://www.youtube.com/watch?v=xEo4DDZXGOI)",
                ephemeral=True,
            )

        @ui.button(
            label="PVP Guide! (Part 3)",
            style=ButtonStyle.green,
            custom_id="sapdaddy7",
        )
        async def video7(self, interaction: Interaction, Button: ui.Button[Any]) -> None:
            await interaction.response.defer()
            await interaction.followup.send(
                content="[🎞](https://www.youtube.com/watch?v=Z9T03ckC-6c)",
                ephemeral=True,
            )

        @ui.button(
            label="How to Play Revomon on your PC!!!",
            style=ButtonStyle.green,
            custom_id="sapdaddy8",
        )
        async def video8(self, interaction: Interaction, Button: ui.Button[Any]) -> None:
            await interaction.response.defer()
            await interaction.followup.send(
                content="[🎞](https://www.youtube.com/watch?v=WOfw92OsXbk)\n\n*Spawn rates on all platforms are now the same*",
                ephemeral=True,
            )

        @ui.button(
            label="Flexing My Shiny Revomon Collection!!",
            style=ButtonStyle.green,
            custom_id="sapdaddy9",
        )
        async def video9(self, interaction: Interaction, Button: ui.Button[Any]) -> None:
            await interaction.response.defer()
            await interaction.followup.send(
                content="[🎞](https://www.youtube.com/watch?v=XzLwvV52wao)",
                ephemeral=True,
            )

        @ui.button(
            label="The 6th Sparkle Cup! New Shiny RARES?!",
            style=ButtonStyle.green,
            custom_id="sapdaddy10",
        )
        async def video10(self, interaction: Interaction, Button: ui.Button[Any]) -> None:
            await interaction.response.defer()
            await interaction.followup.send(
                content="[🎞](https://www.youtube.com/watch?v=eDbmnfZ4mss)",
                ephemeral=True,
            )

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        print("The Elder's Library(Sap Daddy Command) is ready!")
        print("---------------------------")

    @app_commands.command(name="sapdaddy", description="Sap Daddy Command")
    @app_commands.allowed_installs(guilds=True, users=True)
    async def sapdaddy(self, interaction: Interaction) -> None:
        embed = self.sapdaddy_embed()
        buttons = self.sapdaddy_buttons()
        await interaction.response.send_message(
            embed=embed, view=buttons, ephemeral=True
        )


async def setup(gradex: commands.Bot) -> None:
    await gradex.add_cog(SapDaddy2(gradex))
