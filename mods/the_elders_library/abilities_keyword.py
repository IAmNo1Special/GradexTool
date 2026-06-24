from typing import Any

import discord
from discord.ext import commands

from utils.helpers import respond


class allabilities(commands.Cog):  # noqa: N801
    def __init__(self, gradex: Any) -> None:
        self.gradex = gradex

    def allabilities_embed(self) -> Any:
        embed = discord.Embed(title="Full Ability List", color=discord.Color.red())
        embed.add_field(
            name="__Ability__",
            value="Adaptability\nAftermath\nAnger Point\nBad Dreams\nBattery\nBattle Armor\nBig Pecks\nBlaze\nChlorophyll\nClear Body\nCloud Nine\nCompetitive\nCursed Body\nCute Charm\nDamp\nDark Aura\nDefiant\nDrizzle\nFlame Body\nFlare Boost\nFlash Fire\nFriend Guard\nGluttony\nGuts\nHarvest\nHealer\nHoney Gather\nHustle\nHyper Cutter\nInfiltrator\nInner Focus\nInsomnia\nIntimidate\nIron Fist\nKeen Eye\nKlutz\nLeaf Guard\nLevitate\nLight Metal\nLightning Rod\nMagic Bounce\nMarvel Scale\nMultiscale\nNatural Cure\nNo Guard\nOblivious\nOvercoat\nOvergrow\nPickup\nPlus\nToxic Point\nPrankster\nPressure\nQuick Feet\nRain Dish\nReckless\nRefrigerate\nRegenerator\nRivalry\nStone Head\nRun Away\nSand Force\nSand Rush\nSand Stream\nSand Veil\nScrappy\nSerene Grace\nShadow Tag\nShed Skin\nSheer Force\nShield Dust\nSniper\nSnow Warning\nSolar Power\nSoundproof\nSpeed Boost\nStatic\nSteadfast\nStorm Drain\nSturdy\nSuper Luck\nSwarm\nSwift Swim\nSynchronize\nTangled Feet\nTechnician\nTelepathy\nTorrent\nTough Claws\nUnburden\nUnnerve\nVital Spirit\nWater Absorb\nWeak Armor",
            inline=False,
        )
        embed.set_thumbnail(
            url="https://media.discordapp.net/attachments/983557860803874826/1076036559893172354/THE_ELDER.png"
        )
        embed.set_author(name="The Elder's Library")
        embed.set_footer(text="Global Revomon Association")
        return embed

    class allabilities_buttons(discord.ui.View):  # noqa: N801
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
        print("The Elder's Library(All Abilities Keyword) is ready!")
        print("---------------------------")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        # Ignore messages from bots (including self)
        if message.author.bot:
            return

        try:
            prompt = message.content.lower().strip()
            if prompt == "all abilities" or prompt == "abilities":
                embed = self.allabilities_embed()
                buttons = self.allabilities_buttons()
                await respond(self.gradex, message, embed=embed, view=buttons)  # type: ignore[call-arg]
        except Exception as e:
            print(f"An error occurred during on_message: {e}")


async def setup(gradex: commands.Bot) -> None:
    await gradex.add_cog(allabilities(gradex))
