from typing import Any
import discord
from discord.ext import commands

from utils.helpers import respond


class allfruitys(commands.Cog):
    def __init__(self, gradex: Any) -> None:
        self.gradex = gradex

    def allfruitys_embed() -> Any:  # type: ignore[misc]
        embed = discord.Embed(
            title="Full Fruity List",
            description="""__**Fruity Name**__
Barka Fruity
Cassius Fruity
Chamo Fruity
Choda Fruity
Cozi Fruity
Dabip Fruity
Defo Fruity
Derlu Fruity
Ebla Fruity
Ertha Fruity
Frin Fruity
Frizy Fruity
Glandu Fruity
Globop Fruity
Golmon Fruity
Golu Fruity
Gunko Fruity
Gupon Fruity
Inchu Fruity
Iota Fruity
Issou Fruity
Jadwa Fruity
Juiti Fruity
Kanda Fruity
Kankoo Fruity
Karoto Fruity
Lee Fruity
Liech Fruity
Miopi Fruity
Mitsi Fruity
Nonomi Fruity
Osef Fruity
Paia Fruity
Papille Fruity
Papou Fruity
Peachu Fruity
Pritcha Fruity
Psiro Fruity
Ruka Fruity
Tavaa Fruity
Terter Fruity
Tibli Fruity
Tipli Fruity
Toktok Fruity
Trars Fruity
Trigo Fruity
Truduku Fruity
Vilvi Fruity
Vrio Fruity
Wilso Fruity
Wiltu Fruity
Yannoi Fruity
Yululu Fruity""",
            color=discord.Color.red(),
        )
        # embed.add_field(name="__Fruity__", value="Barka\nCassius\nChamo\nChoda\nCozi\nDabip\nDefo\nDerlu\nEbla\nErtha\nFrin\nFrizy\nGlandu\nGlobop\nGolmon\nGolu\nGunko\nGupon\nInchu\nIota\nIssou\nJadwa\nJuiti\nKanda\nKankoo\nKaroto\nLee\nLiech\nMiopi\nMitsi\nNonomi\nOsef\nPaia\nPapille\nPapou\nPeachu\nPritcha\nPsiro\nRuka\nTavaa\nTerter\nTibli\nTipli\nToktok\nTrars\nTrigo\nTruduku\nVilvi\nVrio\nWilso\nWiltu\nYannoi\nYululu")
        embed.set_footer(text="The Elder's Library · Global Revomon Association")
        return embed

    class allfruitys_buttons(discord.ui.View):
        def __init__(self) -> None:
            super().__init__(timeout=None)

        @discord.ui.button(label="❌", style=discord.ButtonStyle.red, custom_id="exit")
        async def exit_embed(
            self, interaction: discord.Interaction, Button: discord.ui.Button[Any]
        ) -> None:
            if interaction.message:

                await interaction.message.delete()

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        print("The Elder's Library(All Fruitys Keyword) is ready!")
        print("---------------------------")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        # Ignore messages from bots (including self)
        if message.author.bot:
            return

        try:
            prompt = message.content.lower().strip()
            if prompt == "all fruitys" or prompt == "fruitys":
                embed = allfruitys.allfruitys_embed()
                buttons = allfruitys.allfruitys_buttons()
                await respond(
                    self.gradex, message=message, embed=embed, buttons=buttons
                )
        except Exception as e:
            print(f"An error occurred during on_message: {e}")


async def setup(gradex: commands.Bot) -> None:
    await gradex.add_cog(allfruitys(gradex))
