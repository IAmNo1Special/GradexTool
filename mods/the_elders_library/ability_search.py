from typing import Any

import discord
from discord.ext import commands

from data import AbilitiesTable, RevomonTable
from utils.helpers import respond


class ability_search(commands.Cog):  # noqa: N801
    def __init__(self, gradex: Any) -> None:
        self.gradex = gradex

    async def ability_search_embed(self, ability_name: Any) -> Any:
        ability_info = await AbilitiesTable().get_info(ability_name.lower())[0]  # type: ignore[attr-defined]
        embed = discord.Embed(
            title=ability_name,
            description=f"*{ability_info[1].capitalize()}*",
            color=discord.Color.red(),
        )
        can_learn = await RevomonTable().has_ability(ability_name=ability_name.lower())  # type: ignore[attr-defined]
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

    class ability_search_buttons(discord.ui.View):  # noqa: N801
        def __init__(self) -> None:
            super().__init__(timeout=None)

        @discord.ui.button(label="❌", style=discord.ButtonStyle.red, custom_id="exit")
        async def exit_embed(
            self, interaction: discord.Interaction, Button: discord.ui.Button[Any]  # noqa: N803
        ) -> None:
            if interaction.message:

                await interaction.message.delete()

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        print("The Elder's Library(Ability Search) is ready!")
        print("---------------------------")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        # Ignore messages from bots (including self)
        if message.author.bot:
            return

        try:
            prompt = message.content.lower().strip()
            if prompt in await AbilitiesTable().get_names():  # type: ignore[attr-defined]
                embed = self.ability_search_embed(prompt)
                buttons = self.ability_search_buttons()
                await respond(
                    self.gradex, message=message, embed=embed, buttons=buttons  # type: ignore[arg-type]
                )

        except Exception as e:
            print(f"An error occurred during 'ability_search' on_message: {e}")


async def setup(gradex: Any) -> None:
    await gradex.add_cog(ability_search(gradex))
