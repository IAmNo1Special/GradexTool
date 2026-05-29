import discord
from data.gradexDB import AbilitiesTable, RevomonTable
from discord.ext import commands

from utils.helpers import respond


class ability_search(commands.Cog):
    def __init__(self, gradex):
        self.gradex = gradex

    def ability_search_embed(self, ability_name):
        ability_info = AbilitiesTable().get_info(ability_name.lower())[0]
        embed = discord.Embed(
            title=ability_name,
            description=f"*{ability_info[1].capitalize()}*",
            color=discord.Color.red(),
        )
        can_learn = RevomonTable().has_ability(ability_name=ability_name.lower())
        learned_by = ""
        for revomon in can_learn:
            learned_by += f"- *{revomon}*\n"
        embed.add_field(
            name="__**Learned By**__", value=learned_by, inline=False
        ) if can_learn else embed.add_field(
            name="__**Learned By**__", value="None", inline=False
        )
        embed.set_thumbnail(
            url="https://media.discordapp.net/attachments/983557860803874826/1076036559893172354/THE_ELDER.png"
        )
        embed.set_author(name="The Elder's Library")
        embed.set_footer(text="Global Revomon Association")
        return embed

    class ability_search_buttons(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)

        @discord.ui.button(label="❌", style=discord.ButtonStyle.red, custom_id="exit")
        async def exit_embed(
            self, interaction: discord.Interaction, Button: discord.ui.Button
        ):
            await interaction.message.delete()

    @commands.Cog.listener()
    async def on_ready(self):
        print("The Elder's Library(Ability Search) is ready!")
        print("---------------------------")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Ignore messages from bots (including self)
        if message.author.bot:
            return

        try:
            prompt = message.content.lower().strip()
            if prompt in AbilitiesTable().get_names():
                embed = self.ability_search_embed(prompt)
                buttons = self.ability_search_buttons()
                await respond(
                    self.gradex, message=message, embed=embed, buttons=buttons
                )

        except Exception as e:
            print(f"An error occurred during 'ability_search' on_message: {e}")


async def setup(gradex):
    await gradex.add_cog(ability_search(gradex))
