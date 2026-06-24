from typing import Any

import discord
from discord.ext import commands

from utils.helpers import respond


class sapdaddy(commands.Cog):  # noqa: N801
    def __init__(self, gradex: Any) -> None:
        self.gradex = gradex

    def sapdaddy_embed(self) -> Any:
        embed = discord.Embed(
            title="➡Sapdaddy's Official Youtube⬅",
            description="Select a video from below.",
            url="https://www.youtube.com/@NicksGamesL33t",
            color=discord.Color.red(),
        )
        embed.set_image(
            url="https://yt3.googleusercontent.com/lvlTdwCX8VHLYfI5i1mgVC704xzb_VlYT_XNVPEaqkY8EeMaRIJfmwnb-gZ6E1D-2wKzmRPS=s88-c-k-c0x00ffffff-no-rj"
        )
        embed.set_thumbnail(
            url="https://media.discordapp.net/attachments/983557860803874826/1076036559893172354/THE_ELDER.png"
        )
        embed.set_author(name="Sap Daddy")
        embed.set_footer(text="The Elder's Library · Global Revomon Association")
        return embed

    class sapdaddy_buttons(discord.ui.View):  # noqa: N801
        def __init__(self) -> None:
            super().__init__(timeout=None)

        @discord.ui.button(
            label="Does my mon have the Hidden Ability?!?",
            style=discord.ButtonStyle.green,
            custom_id="sapdaddy1",
        )
        async def video1(
            self,
            interaction: discord.Interaction,
            Button: discord.ui.Button[Any],  # noqa: N803
        ) -> None:
            await interaction.response.defer()
            await interaction.followup.send(
                content="[🎞](https://youtu.be/watch?v=YE8zJM_zN98)",
                ephemeral=True,
            )

        @discord.ui.button(
            label="EV Train at GODLIKE speed!!!",
            style=discord.ButtonStyle.green,
            custom_id="sapdaddy2",
        )
        async def video2(
            self,
            interaction: discord.Interaction,
            Button: discord.ui.Button[Any],  # noqa: N803
        ) -> None:
            await interaction.response.defer()
            await interaction.followup.send(
                content="[🎞](https://youtu.be/watch?v=wewZChz-jlc)",
                ephemeral=True,
            )

        @discord.ui.button(
            label="Exclusive Interview with Revomon CEO",
            style=discord.ButtonStyle.green,
            custom_id="sapdaddy3",
        )
        async def video3(
            self,
            interaction: discord.Interaction,
            Button: discord.ui.Button[Any],  # noqa: N803
        ) -> None:
            await interaction.response.defer()
            await interaction.followup.send(
                content="[🎞](https://www.youtube.com/watch?v=5SEzlyGON0E)",
                ephemeral=True,
            )

        @discord.ui.button(
            label="How to Beat the Podium and Earn $$!!",
            style=discord.ButtonStyle.green,
            custom_id="sapdaddy4",
        )
        async def video4(
            self,
            interaction: discord.Interaction,
            Button: discord.ui.Button[Any],  # noqa: N803
        ) -> None:
            await interaction.response.defer()
            await interaction.followup.send(
                content="[🎞](https://www.youtube.com/watch?v=m9_OPeGfzE4)",
                ephemeral=True,
            )

        @discord.ui.button(
            label="PVP Guide! (Part 1)",
            style=discord.ButtonStyle.green,
            custom_id="sapdaddy5",
        )
        async def video5(
            self,
            interaction: discord.Interaction,
            Button: discord.ui.Button[Any],  # noqa: N803
        ) -> None:
            await interaction.response.defer()
            await interaction.followup.send(
                content="[🎞](https://www.youtube.com/watch?v=8G3NFKtGWuo)",
                ephemeral=True,
            )

        @discord.ui.button(
            label="PVP Guide! (Part 2)",
            style=discord.ButtonStyle.green,
            custom_id="sapdaddy6",
        )
        async def video6(
            self,
            interaction: discord.Interaction,
            Button: discord.ui.Button[Any],  # noqa: N803
        ) -> None:
            await interaction.response.defer()
            await interaction.followup.send(
                content="[🎞](https://www.youtube.com/watch?v=xEo4DDZXGOI)",
                ephemeral=True,
            )

        @discord.ui.button(
            label="PVP Guide! (Part 3)",
            style=discord.ButtonStyle.green,
            custom_id="sapdaddy7",
        )
        async def video7(
            self,
            interaction: discord.Interaction,
            Button: discord.ui.Button[Any],  # noqa: N803
        ) -> None:
            await interaction.response.defer()
            await interaction.followup.send(
                content="[🎞](https://www.youtube.com/watch?v=Z9T03ckC-6c)",
                ephemeral=True,
            )

        @discord.ui.button(
            label="How to Play Revomon on your PC!!!",
            style=discord.ButtonStyle.green,
            custom_id="sapdaddy8",
        )
        async def video8(
            self,
            interaction: discord.Interaction,
            Button: discord.ui.Button[Any],  # noqa: N803
        ) -> None:
            await interaction.response.defer()
            await interaction.followup.send(
                content="[🎞](https://www.youtube.com/watch?v=WOfw92OsXbk)\n\n*Spawn rates on all platforms are now the same*",
                ephemeral=True,
            )

        @discord.ui.button(
            label="Flexing My Shiny Revomon Collection!!",
            style=discord.ButtonStyle.green,
            custom_id="sapdaddy9",
        )
        async def video9(
            self,
            interaction: discord.Interaction,
            Button: discord.ui.Button[Any],  # noqa: N803
        ) -> None:
            await interaction.response.defer()
            await interaction.followup.send(
                content="[🎞](https://www.youtube.com/watch?v=XzLwvV52wao)",
                ephemeral=True,
            )

        @discord.ui.button(
            label="The 6th Sparkle Cup! New Shiny RARES?!",
            style=discord.ButtonStyle.green,
            custom_id="sapdaddy10",
        )
        async def video10(
            self,
            interaction: discord.Interaction,
            Button: discord.ui.Button[Any],  # noqa: N803
        ) -> None:
            await interaction.response.defer()
            await interaction.followup.send(
                content="[🎞](https://www.youtube.com/watch?v=eDbmnfZ4mss)",
                ephemeral=True,
            )

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
        print("The Elder's Library(Sap Daddy Keyword) is ready!")
        print("---------------------------")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        # Ignore messages from bots (including self)
        if message.author.bot:
            return
        try:
            prompt = message.content.lower().replace(" ", "")
            if prompt == "sapdaddy":
                embed = self.sapdaddy_embed()
                buttons = self.sapdaddy_buttons()
                await respond(
                    self.gradex, message=message, embed=embed, buttons=buttons
                )
        except Exception as e:
            print(f"An error occurred during on_message: {e}")


async def setup(gradex: commands.Bot) -> None:
    await gradex.add_cog(sapdaddy(gradex))
