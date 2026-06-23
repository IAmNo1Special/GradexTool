from typing import Any
import discord
from discord.ext import commands

from utils.helpers import respond


class allitems(commands.Cog):
    def __init__(self, gradex: Any) -> None:
        self.gradex = gradex

    def allitems_embed(self) -> Any:
        embed = discord.Embed(
            title="Full Item List",
            description="""__**Item Name**__

Clan Gem
Green Orb
Blue Orb
Red Orb
Potion
Toxic Cure
Burning Cure
Freezing Cure
Sleeping Cure
Paralysis Cure
Full Recovery
Full Potion
Hyper Potion
Super potion
Full Cure
PP Aid
Full PP Aid
Mixture
Full Mixture
Effect Guard
Critic UP
Attack UP
Defense UP
Speed UP
Accuracy UP
Sp atk UP
Sp def UP
move 01
move 02
move 03
move 04
move 05
move 06
move 07
move 08
move 09
move 10
move 11
move 12
move 13
move 14
move 15
move 16
move 17
move 18
move 19
move 20
move 21
move 22
move 23
move 24
move 25
move 26
move 27
move 28
move 29
move 30
move 31
move 32
move 33
move 34
move 35
move 36
move 37
move 38
move 39
move 40
move 41
move 42
move 43
move 44
move 45
move 46
move 47
move 48
move 49
move 50
move 51
move 52
move 53
move 54
move 55
move 56
move 57
move 58
move 59
move 60
move 61
move 62
move 63
move 64
move 65
move 66
move 67
move 68
move 69
move 70
move 71
move 72
move 73
move 74
move 75
move 76
move 77
move 78
move 79
move 80
move 81
move 82
move 83
move 84
move 85
move 86
move 87
move 88
move 89
move 90
move 91
move 92
move 93
move 94
move 95
move 96
move 97
move 98
move 99
move 100
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
        embed.set_footer(text="The Elder's Library · Global Revomon Association")
        return embed

    class allitems_buttons(discord.ui.View):
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
        print("The Elder's Library(All Items Keyword) is ready!")
        print("---------------------------")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        # Ignore messages from bots (including self)
        if message.author.bot:
            return

        try:
            prompt = message.content.lower().strip()
            if prompt == "all items" or prompt == "items":
                embed = self.allitems_embed()
                buttons = self.allitems_buttons
                await respond(
                    self.gradex, message=message, embed=embed, buttons=buttons  # type: ignore[arg-type]
                )
        except Exception as e:
            print(f"An error occurred during on_message: {e}")


async def setup(gradex: commands.Bot) -> None:
    await gradex.add_cog(allitems(gradex))
