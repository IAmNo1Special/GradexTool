import discord
from discord.ext import commands
from data.gradexDB import NaturesTable
from utils.helpers import respond


class nature_search(commands.Cog):
    def __init__(self, gradex):
        self.gradex = gradex

    def nature_search_embed(self, nature_name):
        nature_info = NaturesTable().get_info(nature_name=nature_name.lower())[
            0
        ]
        embed = discord.Embed(
            title=f"{nature_info[0].title()} Nature", color=discord.Color.red()
        )
        if nature_info[1] is None:
            embed.add_field(
                name="__**Stat Boosted**__", value="*None*", inline=False
            )
        else:
            embed.add_field(
                name="__**Stat Boosted**__",
                value=f"*{nature_info[1].title()} Stat (+10%)*",
                inline=False,
            )
        if nature_info[2] is None:
            embed.add_field(
                name="__**Stat Reduced**__", value="*None*", inline=False
            )
        else:
            embed.add_field(
                name="__**Stat Reduced**__",
                value=f"*{nature_info[2].title()} Stat (-10%)*",
                inline=False,
            )
        if nature_info[3] is not None and nature_info[4] is not None:
            embed.add_field(
                name="__**Likes**__",
                value=f"*{nature_info[3].title()} flavored Fruitys*",
                inline=False,
            )
            embed.add_field(
                name="__**Dislikes**__",
                value=f"*{nature_info[4].title()} flavored Fruitys*",
                inline=False,
            )
        embed.set_thumbnail(
            url="https://media.discordapp.net/attachments/983557860803874826/1076036559893172354/THE_ELDER.png"
        )
        embed.set_footer(
            text="The Elder's Library · Global Revomon Association"
        )
        return embed

    class nature_search_buttons(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)

        @discord.ui.button(
            label="❌", style=discord.ButtonStyle.red, custom_id="exit"
        )
        async def exit_embed(
            self, interaction: discord.Interaction, Button: discord.ui.Button
        ):
            await interaction.message.delete()

    @commands.Cog.listener()
    async def on_ready(self):
        print("The Elder's Library(Nature Search) is ready!")
        print("---------------------------")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Ignore messages from bots (including self)
        if message.author.bot:
            return

        try:
            prompt = message.content.lower().strip()
            if prompt in NaturesTable().get_names():
                embed = self.nature_search_embed(prompt)
                buttons = self.nature_search_buttons()
                await respond(
                    self.gradex, message=message, embed=embed, buttons=buttons
                )
        except Exception as e:
            print(f"An error occurred during 'nature_search' on_message: {e}")


async def setup(gradex: commands.Bot):
    await gradex.add_cog(nature_search(gradex))
