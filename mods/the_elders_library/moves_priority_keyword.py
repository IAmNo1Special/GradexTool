import logging
from typing import Any

import discord
from discord import Interaction, app_commands
from discord.ext import commands

logger = logging.getLogger(__name__)


class allprioritymoves(commands.Cog):  # noqa: N801
    def __init__(self, gradex: Any) -> None:
        self.gradex = gradex

    def allprioritymoves_embed(self) -> Any:
        embed = discord.Embed(
            title="Full Priority Move List", color=discord.Color.red()
        )
        embed.add_field(
            name="__Priority Moves__",
            value="Helping Hand\nProtect\nDetect\nEndure\nMagic Coat\nSnatch\nKings Shield\nSpiky Shield\nBaneful Bunker\nFake Out\nWide Guard\nQuick Guard\nCrafty Shield\nSpotlight\nExtreme Speed\nFollow Me\nFeint\nRage Powder\nAlly Switch\nFirst Impression\nQuick Attack\nBide\nMach Punch\nSucker Punch\nVacuum Wave\nBullet Punch\nIce Shard\nShadow Sneak\nAqua Jet\nIon Deluge\nWater Shuriken\nPowder\nBaby Doll Eyes\nAcceleStone\nVital Throw\nFocus Punch\nBeak Blast\nShell Trap\nRevenge\nAvalanche\nCounter\nMirror Coat\nWhirlwind\nRoar\nCircle Throw\nDraconic Tail\nTrick Room\n",
        )
        embed.set_footer(text="The Elder's Library · Global Revomon Association")
        return embed

    class allprioritymoves_buttons(discord.ui.View):  # noqa: N801
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
        print("The Elder's Library(Priority Moves Command) is ready!")
        print("---------------------------")

    @app_commands.command(
        name="priority-moves",
        description="Displays the full priority move list.",
    )
    @app_commands.allowed_installs(guilds=True, users=True)
    async def priority_moves(self, interaction: Interaction) -> None:
        try:
            embed = self.allprioritymoves_embed()
            buttons = self.allprioritymoves_buttons()
            await interaction.response.send_message(
                embed=embed, view=buttons, ephemeral=True
            )
        except Exception as e:
            logger.error(f"An error occurred during the 'priority-moves' command: {e}")


async def setup(gradex: commands.Bot) -> None:
    await gradex.add_cog(allprioritymoves(gradex))
