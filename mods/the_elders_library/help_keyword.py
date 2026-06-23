from typing import Any
import discord
from discord.ext import commands

from utils.helpers import respond


class help_keyword(commands.Cog):
    def __init__(self, gradex: Any) -> None:
        self.gradex = gradex

    def help_embed(self) -> Any:
        embed = discord.Embed(
            title="Help Menu",
            description="*How can I help you?*",
            color=discord.Color.red(),
        )
        embed.set_thumbnail(
            url="https://media.discordapp.net/attachments/983557860803874826/1076036559893172354/THE_ELDER.png"
        )
        embed.set_footer(text="The Elder's Library · Global Revomon Association")
        return embed

    class gdex_help_buttons(discord.ui.View):
        def __init__(self) -> None:
            super().__init__(timeout=None)

        @discord.ui.button(
            label="1 | Revomon search",
            style=discord.ButtonStyle.green,
            custom_id="Mon Search Help",
        )
        async def mon_search_help(
            self, interaction: discord.Interaction, Button: discord.ui.Button[Any]
        ) -> None:
            mon_search_help_embed = discord.Embed(
                title="Revomon search",
                description="""Type the name of the Revomon you would like more information about. Includes everything you"ll need to know, even Counterdex PvP Builds. Type **All Revomon** for a list of all the Revomon in my library.""",
                color=discord.Color.red(),
            )
            mon_search_help_embed.set_thumbnail(
                url="https://media.discordapp.net/attachments/983557860803874826/1076036559893172354/THE_ELDER.png"
            )
            mon_search_help_embed.set_footer(
                text="The Elder's Library · Global Revomon Association"
            )
            await interaction.response.defer()
            await interaction.followup.send(embed=mon_search_help_embed, ephemeral=True)

        @discord.ui.button(
            label="2 | Move search",
            style=discord.ButtonStyle.green,
            custom_id="Move Search Help",
        )
        async def move_search_help(
            self, interaction: discord.Interaction, Button: discord.ui.Button[Any]
        ) -> None:
            move_search_help_embed = discord.Embed(
                title="Move search",
                description="""Type the name of the move you would like more information about. Type **All Moves** for a list of all the moves in my library.""",
                color=discord.Color.red(),
            )
            move_search_help_embed.set_thumbnail(
                url="https://media.discordapp.net/attachments/983557860803874826/1076036559893172354/THE_ELDER.png"
            )
            move_search_help_embed.set_footer(
                text="The Elder's Library · Global Revomon Association"
            )
            await interaction.response.defer()
            await interaction.followup.send(
                embed=move_search_help_embed, ephemeral=True
            )

        @discord.ui.button(
            label="3 | Priority Move search",
            style=discord.ButtonStyle.green,
            custom_id="PriMove Search Help",
        )
        async def primove_search_help(
            self, interaction: discord.Interaction, Button: discord.ui.Button[Any]
        ) -> None:
            primove_search_help_embed = discord.Embed(
                title="Priority Move search",
                description="""Type the name of the Priority Move you would like more information about. Type **All Priority Moves** for a list of all the priority moves in my library.""",
                color=discord.Color.red(),
            )
            primove_search_help_embed.set_thumbnail(
                url="https://media.discordapp.net/attachments/983557860803874826/1076036559893172354/THE_ELDER.png"
            )
            primove_search_help_embed.set_footer(
                text="The Elder's Library · Global Revomon Association"
            )
            await interaction.response.defer()
            await interaction.followup.send(
                embed=primove_search_help_embed, ephemeral=True
            )

        @discord.ui.button(
            label="4 | Ability search",
            style=discord.ButtonStyle.green,
            custom_id="Ability Search Help",
        )
        async def ability_search_help(
            self, interaction: discord.Interaction, Button: discord.ui.Button[Any]
        ) -> None:
            ability_search_help_embed = discord.Embed(
                title="Ability search",
                description="""Type the name of the Ability you would like more information about. Type **All Abilities** for a list of all the abilities in my library.""",
                color=discord.Color.red(),
            )
            ability_search_help_embed.set_thumbnail(
                url="https://media.discordapp.net/attachments/983557860803874826/1076036559893172354/THE_ELDER.png"
            )
            ability_search_help_embed.set_footer(
                text="The Elder's Library · Global Revomon Association"
            )
            await interaction.response.defer()
            await interaction.followup.send(
                embed=ability_search_help_embed, ephemeral=True
            )

        @discord.ui.button(
            label="5 | Nature search",
            style=discord.ButtonStyle.green,
            custom_id="Nature Search Help",
        )
        async def nature_search_help(
            self, interaction: discord.Interaction, Button: discord.ui.Button[Any]
        ) -> None:
            nature_search_help_embed = discord.Embed(
                title="Nature search",
                description="""Type the name of the Nature you would like more information about. Type **All Natures** for a list of all the natures in my library.""",
                color=discord.Color.red(),
            )
            nature_search_help_embed.set_thumbnail(
                url="https://media.discordapp.net/attachments/983557860803874826/1076036559893172354/THE_ELDER.png"
            )
            nature_search_help_embed.set_footer(
                text="The Elder's Library · Global Revomon Association"
            )
            await interaction.response.defer()
            await interaction.followup.send(
                embed=nature_search_help_embed, ephemeral=True
            )

        @discord.ui.button(
            label="6 | Item search",
            style=discord.ButtonStyle.green,
            custom_id="Item Search Help",
        )
        async def item_search_help(
            self, interaction: discord.Interaction, Button: discord.ui.Button[Any]
        ) -> None:
            item_search_help_embed = discord.Embed(
                title="Item search",
                description="""Type the name of the item you would like more information about. Type **All Items** for a list of all the items in my library.""",
                color=discord.Color.red(),
            )
            item_search_help_embed.set_thumbnail(
                url="https://media.discordapp.net/attachments/983557860803874826/1076036559893172354/THE_ELDER.png"
            )
            item_search_help_embed.set_footer(
                text="The Elder's Library · Global Revomon Association"
            )
            await interaction.response.defer()
            await interaction.followup.send(
                embed=item_search_help_embed, ephemeral=True
            )

        @discord.ui.button(
            label="7 | Fruity search",
            style=discord.ButtonStyle.green,
            custom_id="Fruity Search Help",
        )
        async def fruity_search_help(
            self, interaction: discord.Interaction, Button: discord.ui.Button[Any]
        ) -> None:
            fruity_search_help_embed = discord.Embed(
                title="Fruity search",
                description="""Type the name of the Fruity you would like more information about. Type **All Fruitys** for a list of all the fruitys in my library.""",
                color=discord.Color.red(),
            )
            fruity_search_help_embed.set_thumbnail(
                url="https://media.discordapp.net/attachments/983557860803874826/1076036559893172354/THE_ELDER.png"
            )
            fruity_search_help_embed.set_footer(
                text="The Elder's Library · Global Revomon Association"
            )
            await interaction.response.defer()
            await interaction.followup.send(
                embed=fruity_search_help_embed, ephemeral=True
            )

        @discord.ui.button(
            label="8 | Tier List",
            style=discord.ButtonStyle.green,
            custom_id="Tier List Help",
        )
        async def tier_list_help(
            self, interaction: discord.Interaction, Button: discord.ui.Button[Any]
        ) -> None:
            tier_list_help_embed = discord.Embed(
                title="Tier List",
                description="""Type **Tier List** to see the current meta tier list.""",
                color=discord.Color.red(),
            )
            tier_list_help_embed.set_thumbnail(
                url="https://media.discordapp.net/attachments/983557860803874826/1076036559893172354/THE_ELDER.png"
            )
            tier_list_help_embed.set_footer(
                text="The Elder's Library · Global Revomon Association"
            )
            await interaction.response.defer()
            await interaction.followup.send(embed=tier_list_help_embed, ephemeral=True)

        @discord.ui.button(
            label="9 | EV Training Chart",
            style=discord.ButtonStyle.green,
            custom_id="EV Chart Help",
        )
        async def ev_chart_help(
            self, interaction: discord.Interaction, Button: discord.ui.Button[Any]
        ) -> None:
            ev_chart_help_embed = discord.Embed(
                title="EV Training Chart",
                description="""Type **EV Chart** to find out ev_chartwhat EVs a Revomon gives once you defeat it.""",
                color=discord.Color.red(),
            )
            ev_chart_help_embed.set_thumbnail(
                url="https://media.discordapp.net/attachments/983557860803874826/1076036559893172354/THE_ELDER.png"
            )
            ev_chart_help_embed.set_footer(
                text="The Elder's Library · Global Revomon Association"
            )
            await interaction.response.defer()
            await interaction.followup.send(embed=ev_chart_help_embed, ephemeral=True)

        @discord.ui.button(
            label="10 | Spawn Locations",
            style=discord.ButtonStyle.green,
            custom_id="Spawn Locations Help",
        )
        async def spawn_help(
            self, interaction: discord.Interaction, Button: discord.ui.Button[Any]
        ) -> None:
            spawn_help_embed = discord.Embed(
                title="Spawn Locations",
                description="""Type **Spawn** to see when & where all Revomon spawn.""",
                color=discord.Color.red(),
            )
            spawn_help_embed.set_thumbnail(
                url="https://media.discordapp.net/attachments/983557860803874826/1076036559893172354/THE_ELDER.png"
            )
            spawn_help_embed.set_footer(
                text="The Elder's Library · Global Revomon Association"
            )
            await interaction.response.defer()
            await interaction.followup.send(embed=spawn_help_embed, ephemeral=True)

        @discord.ui.button(
            label="11 | Pokemon Counterparts",
            style=discord.ButtonStyle.green,
            custom_id="Pmon Help",
        )
        async def pmon_help(
            self, interaction: discord.Interaction, Button: discord.ui.Button[Any]
        ) -> None:
            pmon_help_embed = discord.Embed(
                title="Pokemon Counterparts",
                description="""Type **Pokémon** for a list of Revomon and their Pokémon counterpart.""",
                color=discord.Color.red(),
            )
            pmon_help_embed.set_thumbnail(
                url="https://media.discordapp.net/attachments/983557860803874826/1076036559893172354/THE_ELDER.png"
            )
            pmon_help_embed.set_footer(
                text="The Elder's Library · Global Revomon Association"
            )
            await interaction.followup.send(embed=pmon_help_embed, ephemeral=True)

    class help_buttons(discord.ui.View):
        def __init__(self) -> None:
            super().__init__(timeout=None)

        @discord.ui.button(
            label="1 | Gradex Tool",
            style=discord.ButtonStyle.green,
            custom_id="Gdex Help",
        )
        async def gdex_help(
            self, interaction: discord.Interaction, Button: discord.ui.Button[Any]
        ) -> None:
            gdex_help_embed = discord.Embed(
                title="Features & Instructions",
                description=""">>> 1 | *The Gradex Tool combines the knowledge of The Elder & his vast library of books about the world of Revomon with the added convenience & power of Discord.*

2 | **Owning Gradex Tool(Pro) or (Pro+) unlocks numerous Gradex Tool features.**

    3 | *Gain Pro+ membership by purchasing the NFT version of a tool. Pro+ grants you an ad free experience for as long as you own the NFT & the ability to use the Gradex Tool from your DMs.* 

4 | *Gain  Pro membership by purchasing a Gradex Tool (Pro) subscription. Pro grants you an ad free experience & the ability to use the Gradex Tool from your DMs for 30 days. Use the keyword `$store` to purchase a subscription.*

**Select a feature from below for instructions on how to use it. Enjoy!!**""",
                color=discord.Color.red(),
            )
            gdex_help_embed.set_thumbnail(
                url="https://media.discordapp.net/attachments/983557860803874826/1076036559893172354/THE_ELDER.png"
            )
            gdex_help_embed.set_image(
                url="https://media.discordapp.net/attachments/983557860803874826/1076037071539544124/grade-x_tool.png?width=749&height=655"
            )
            gdex_help_embed.set_footer(
                text="The Elder's Library · Global Revomon Association"
            )
            await interaction.response.defer()
            await interaction.followup.send(
                embed=gdex_help_embed,
                view=help_keyword.gdex_help_buttons(),
                ephemeral=True,
            )

        @discord.ui.button(
            label="2 | Tiptop's Top-up Shop",
            style=discord.ButtonStyle.green,
            custom_id="TTS Help",
        )
        async def tts_help(
            self, interaction: discord.Interaction, Button: discord.ui.Button[Any]
        ) -> None:
            tts_help_embed = discord.Embed(
                title="Tiptop's Top-up Shop",
                description="""Type **Tiptop** for access to Tiptop's Top-up Shop. This is where you can purchase and/or redeem your Global Revomon NFTs like the Gradex Tool(Pro+), In-Game Currency(IGC) and more!!""",
                color=discord.Color.red(),
            )
            tts_help_embed.set_thumbnail(
                url="https://media.discordapp.net/attachments/983557860803874826/1076036559893172354/THE_ELDER.png"
            )
            tts_help_embed.set_image(
                url="https://media.discordapp.net/attachments/983557860803874826/1076036560111271957/TIPTOP.png"
            )
            tts_help_embed.set_footer(
                text="The Elder's Library · Global Revomon Association"
            )
            await interaction.response.defer()
            await interaction.followup.send(embed=tts_help_embed, ephemeral=True)

        @discord.ui.button(
            label="3 | Eazy's EV Daycare",
            style=discord.ButtonStyle.green,
            custom_id="EED Help",
        )
        async def eed_help(
            self, interaction: discord.Interaction, Button: discord.ui.Button[Any]
        ) -> None:
            eed_help_embed = discord.Embed(
                title="Eazy's EV Daycare",
                description="""Type **Eazy** for access to Eazy's EV Daycare. This is where you can purchase and/or redeem your EV Training NFTs to have your Revomon EV trained by Eazy.""",
                color=discord.Color.red(),
            )
            eed_help_embed.set_thumbnail(
                url="https://media.discordapp.net/attachments/983557860803874826/1076036559893172354/THE_ELDER.png"
            )
            eed_help_embed.set_image(
                url="https://media.discordapp.net/attachments/983557860803874826/1076036559427612702/EAZY.png"
            )
            eed_help_embed.set_footer(
                text="The Elder's Library · Global Revomon Association"
            )
            await interaction.response.defer()
            await interaction.followup.send(embed=eed_help_embed, ephemeral=True)

        @discord.ui.button(
            label="4 | Eleven's Arena",
            style=discord.ButtonStyle.green,
            custom_id="EA Help",
        )
        async def ea_help(
            self, interaction: discord.Interaction, Button: discord.ui.Button[Any]
        ) -> None:
            ea_help_embed = discord.Embed(
                title="Eleven's Arena",
                description="""Type **Eleven** for access to Eleven's Arena. This is where you can find out more info about PvP and PvE events hosted by GRA.""",
                color=discord.Color.red(),
            )
            ea_help_embed.set_thumbnail(
                url="https://media.discordapp.net/attachments/983557860803874826/1076036559893172354/THE_ELDER.png"
            )
            # ea_help_embed.set_image(url="https://media.discordapp.net/attachments/983557860803874826/1076036559427612702/ELEVEN.png")
            ea_help_embed.set_footer(
                text="The Elder's Library · Global Revomon Association"
            )
            await interaction.response.defer()
            await interaction.followup.send(embed=ea_help_embed, ephemeral=True)

        @discord.ui.button(
            label="5 | How to gain your NFT Titles",
            style=discord.ButtonStyle.green,
            custom_id="Titles Help",
        )
        async def titles_help(
            self, interaction: discord.Interaction, Button: discord.ui.Button[Any]
        ) -> None:
            titles_help_embed = discord.Embed(
                title="How to gain your NFT Titles",
                description="""Follow the instructions in the {#collabland-join} channel to be awarded Titles that come with owning G.R.A. NFTs.""",
                color=discord.Color.red(),
            )
            titles_help_embed.set_thumbnail(
                url="https://media.discordapp.net/attachments/983557860803874826/1076036559893172354/THE_ELDER.png"
            )
            titles_help_embed.set_footer(
                text="The Elder's Library · Global Revomon Association"
            )
            await interaction.response.defer()
            await interaction.followup.send(embed=titles_help_embed, ephemeral=True)

        @discord.ui.button(
            label="6 | GRA Online Presence",
            style=discord.ButtonStyle.green,
            custom_id="OP Help",
        )
        async def op_help(
            self, interaction: discord.Interaction, Button: discord.ui.Button[Any]
        ) -> None:
            op_help_embed = discord.Embed(
                title="GRA Online Presence",
                description="""🔥 💯[OFFICIAL DAPP](https://www.globalrevomon.com/)

🐣 [TWITTER](https://twitter.com/GlobalRevoAssoc)

📸[INSTAGRAM](https://www.instagram.com/globalrevomonassoc/)

📰[OFFICIAL DISCORD](https://discord.gg/VzmYabnGm6)

📨EMAIL:
TheGlobalRevomonAssociation@Gmail.com""",
                color=discord.Color.red(),
            )
            op_help_embed.set_thumbnail(
                url="https://media.discordapp.net/attachments/983557860803874826/1076411902219001946/OFFICIAL_G.R.A_LOGO_350x350.jpg"
            )
            op_help_embed.set_footer(
                text="The Elder's Library · Global Revomon Association"
            )
            await interaction.response.defer()
            await interaction.followup.send(embed=op_help_embed, ephemeral=True)

        @discord.ui.button(label="❌", style=discord.ButtonStyle.red, custom_id="exit")
        async def exit_embed(
            self, interaction: discord.Interaction, Button: discord.ui.Button[Any]
        ) -> None:
            if interaction.message:
                await interaction.message.delete()

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        print("The Elder's Library(Help Keyword) is ready!")
        print("---------------------------")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        # Ignore messages from bots (including self)
        if message.author.bot:
            return

        try:
            # Save User's Cleaned Input As The Search Prompt
            prompt = message.content.lower().strip()
            # Check if User's Prompt is a Revomon's Name
            if prompt == "help":
                embed = self.help_embed()
                buttons = self.help_buttons()
                await respond(
                    self.gradex, message=message, embed=embed, buttons=buttons
                )
        except Exception as e:
            print(f"An error occurred during on_message: {e}")


async def setup(gradex: commands.Bot) -> None:
    await gradex.add_cog(help_keyword(gradex))
