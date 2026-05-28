import discord
from discord.ext import commands

from data.gradexDB import MovesTable, RevomonMovesTable
from utils.helpers import respond


class move_search(commands.Cog):
    def __init__(self, gradex):
        self.gradex = gradex

    def move_search_embed(self, move_name):
        move = MovesTable().get_info(move_name.lower())[0]
        embed = discord.Embed(title=move[2].title(), color=discord.Color.red())
        embed.add_field(name="__**Type**__", value=f"*{move[4]}*", inline=False)
        embed.add_field(name="__**Category**__", value=f"*{move[3]}*", inline=False)
        if move[-3] != 0:
            embed.add_field(name="__**Damage**__", value=f"*{move[-3]}*", inline=False)
        if move[-4] != 0.0:
            embed.add_field(
                name="__**Accuracy**__",
                value=f"*{move[-4] * 100}%*",
                inline=False,
            )
        embed.add_field(name="__**PP**__", value=f"*{move[-2]}*", inline=False)
        embed.add_field(name="__**Priority**__", value=f"*{move[-1]}*")
        if move[1] is not None:
            embed.add_field(name="__**Capsule #**__", value=f"*{move[1]}*\n")
        learned_by = ""
        for revomon in RevomonMovesTable().get_mons_for_move(move_name=move[2]):
            learned_by += f"- *{revomon}*\n"
        if learned_by:
            embed.add_field(name="__**Learned By**__", value=learned_by, inline=False)
        embed.set_thumbnail(
            url="https://media.discordapp.net/attachments/983557860803874826/1076036559893172354/THE_ELDER.png"
        )
        embed.set_author(name="The Elder's Library")
        embed.set_footer(text="Global Revomon Association")
        return embed

    class move_search_buttons(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)

        @discord.ui.button(label="❌", style=discord.ButtonStyle.red, custom_id="exit")
        async def exit_embed(
            self, interaction: discord.Interaction, Button: discord.ui.Button
        ):
            await interaction.message.delete()

    @commands.Cog.listener()
    async def on_ready(self):
        print("The Elder's Library(Move Search) is ready!")
        print("---------------------------")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Ignore messages from bots (including self)
        if message.author.bot:
            return

        try:
            prompt = message.content.lower().strip()
            if prompt in MovesTable().get_names():
                embed = self.move_search_embed(prompt)
                buttons = self.move_search_buttons()
                await respond(
                    self.gradex, message=message, embed=embed, buttons=buttons
                )
        except Exception as e:
            print(f"An error occurred during 'move_search' on_message: {e}")


async def setup(gradex: commands.Bot):
    await gradex.add_cog(move_search(gradex))
