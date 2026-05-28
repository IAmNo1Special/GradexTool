import discord
from discord.ext import commands

from utils.helpers import respond


class evchart(commands.Cog):
    def __init__(self, gradex):
        self.gradex = gradex

    def evchart_embed():
        embed = discord.Embed(
            title="EV Training Chart",
            description="Effort Values",
            color=discord.Color.red(),
        )
        embed.set_thumbnail(
            url="https://s3.amazonaws.com/appforest_uf/f1674460627684x148979553672345730/Counterdexlogo.edit.png"
        )
        embed.set_image(
            url="https://media.discordapp.net/attachments/983557860803874826/1107791599494238290/EV_Train_List.png"
        )
        embed.set_footer(text="Counterdex · Global Revomon Association")
        return embed

    class evchart_buttons(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)

        @discord.ui.button(label="❌", style=discord.ButtonStyle.red, custom_id="exit")
        async def exit_embed(
            self, interaction: discord.Interaction, Button: discord.ui.Button
        ):
            await interaction.message.delete()

    @commands.Cog.listener()
    async def on_ready(self):
        print("The Elder's Library(Ev Chart Keyword) is ready!")
        print("---------------------------")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Ignore messages from bots (including self)
        if message.author.bot:
            return

        try:
            prompt = message.content.lower().strip()
            if prompt == "ev chart" or prompt == "evs":
                embed = self.evchart_embed()
                buttons = self.evchart_buttons()
                await respond(
                    self.gradex, message=message, embed=embed, buttons=buttons
                )
        except Exception as e:
            print(f"An error occurred during on_message: {e}")


async def setup(gradex: commands.Bot):
    await gradex.add_cog(evchart(gradex))
