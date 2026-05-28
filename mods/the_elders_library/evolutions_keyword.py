import discord
from discord.ext import commands
from utils.helpers import respond


class evolutions(commands.Cog):
    def __init__(self, gradex):
        self.gradex = gradex

    def evolutions_embed():
        embed = discord.Embed(
            title="Full Evolutions List Pt.1",
            description="""__**Revomon**__->__**Evolution**__->__**At Lvl**__

- Dekute->Desuke->16
- Desuke->Deksciple->32
- Deksciple->(Final Evolution)
- Gorlit->Gorox->16
- Gorox->Gorcano->32
- Gorcano->(Final Evolution)
- Zorelle->Zorene->16
- Zorene->Blizzora->32
- Blizzora->(Final Evolution)
- Spydull	--->	Spookoon	--->	10
- Spookoon	--->	Skultergeist	--->	20
- Skultergeist	(Final Evolution)
- Chikito	--->	Falcolt	--->	18
- Falcolt	(Final Evolution)
- Pincub	--->	Camprikine	--->	20
- Camprikine	(Final Evolution)
- Swiftling	--->	Veloswift	--->	20
- Veloswift	(Final Evolution)
- Fungas	--->	Smogshroom	--->	22
- Smogshroom	(Final Evolution)
- Echomaus	--->	Radarent	--->	34
- Radarent	(Final Evolution)
- Dosoil	--->	Comboworm	--->	22
- Comboworm	(Final Evolution)
- Navixy	--->	Farinade	--->	33
- Farinade	(Final Evolution)
- Lycub	--->	Champlion	--->	28
- Champlion	(Final Evolution)
- Vyphern	--->	Wyverdant	--->	34
- Sumbear	--->	Grizleaf	--->	16
- Grizleaf	--->	Wintursa	--->	32
- Wintursa	(Final Evolution)
- Blazlet	--->	Coalbra	--->	14
- Coalbra	--->	Volcanolisk	--->	36
- Volcanolisk	(Final Evolution)
- Pupple	--->	Sharku	--->	18
- Sharku	--->	Tidju	--->	30
- Tidju	(Final Evolution)
- Raival	(Final Evolution)
- Dominevo	(Final Evolution)
- Twilevo	(Final Evolution)
- Venturevo	(Final Evolution)
- Loftevo	(Final Evolution)
- Drakevo	(Final Evolution)
- Hauntevo	(Final Evolution)
- R3v-Up	(Final Evolution)
- Tipply	--->	Hassurugu	--->	25
- Hassurugu	--->	Masakaridon	--->	34
- Masakaridon	(Final Evolution)
- Dexuno	--->	Dexdeux	--->	20
- Dexdeux	--->	Dexdrei	--->	45
- Dexdrei	--->	Dexfyre	--->	55
- Dexfyre	(Final Evolution)
- Dregg	--->	Wyvegg	--->	30
- Wyvegg	--->	Craggon	--->	55
- Craggon	(Final Evolution)
- Skwitzen	--->	Skwimera	--->	15
- Skwimera	--->	Skwerberos	--->	30
- Skwerberos	(Final Evolution)
- Monking	(Final Evolution)
- Koigup	--->	Koigar	--->	16
- Koigar	--->	Slisces	--->	36
- Slisces	(Final Evolution)
- Somnap	--->	Soarnap	--->	17
- Soarnap	--->	Soarnox	--->	34
- Soarnox	(Final Evolution)
- Spectreat	(Final Evolution)""",
            color=discord.Color.red(),
        )
        embed.set_thumbnail(
            url="https://media.discordapp.net/attachments/983557860803874826/1076036559893172354/THE_ELDER.png"
        )
        embed.set_footer(
            text="The Elder's Library · Global Revomon Association"
        )
        return embed

    class evolutions_buttons(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)

        @discord.ui.button(
            label="Page 2",
            style=discord.ButtonStyle.green,
            custom_id="Evolution Page 2",
        )
        async def page2(
            self, interaction: discord.Interaction, Button: discord.ui.Button
        ):
            page2_embed = discord.Embed(
                title="Full Evolutions List Pt.2",
                description="""__**Revomon**__->__**Evolution**__->__**At Lvl**__

- Mummole	--->	Ghopher	--->	43
- Ghopher	(Final Evolution)
- Hookanga	--->	Roojab	--->	28
- Roojab	--->	Kangkross	--->	34
- Kangkross	(Final Evolution)
- Wolpan	--->	Panlow	--->	24
- Panlow	--->	Opawan	--->	34
- Opawan	(Final Evolution)
- Turtislet	--->	Shellacay	--->	14
- Shellacay	--->	Atolloise	--->	34
- Atolloise	(Final Evolution)
- Scorpyd	--->	Tetrapion	--->	22
- Tetrapion	(Final Evolution)
- Bouldorable	--->	Rockonid	--->	17
- Rockonid	--->	Pandozer	--->	34
- Pandozer	(Final Evolution)
- Frostoast	--->	Furnice	--->	22
- Furnice	(Final Evolution)
- Peafrost	--->	Kickundra	--->	22
- Kickundra	(Final Evolution)
- Bluezilla	(Final Evolution)
- Polluvern	(Final Evolution)
- Locuna	--->	Lunacoon	--->	17
- Lunacoon	--->	Moontis	--->	34
- Moontis	(Final Evolution)
- Bookwyrm	--->	Leximinth	--->	22
Leximinth	(Final Evolution)
Teddream	--->	Bearmare	--->	25
Bearmare	--->	Nightmort	--->	34
Nightmort	(Final Evolution)
Reingifir	(Final Evolution)
Cupidove	--->	Dovamour	--->	14
Dovamour	--->	Romanfrig	--->	34
Romanfrig	(Final Evolution)
Wyverdant	(Final Evolution)
Odonymph	--->	Drakefly	--->	22
Drakefly	--->	Meganeudra	--->	30
Meganeudra	(Final Evolution)
Ninesee	--->	Bloomsee	--->	18
Bloomsee	--->	Gardsee	--->	27
Gardsee	(Final Evolution)
Mirrate	--->	Miraflect	--->	15
Miraflect	(Final Evolution)
Soleel	--->	Doubeel	--->	16
Doubeel	--->	Triplydra	--->	36
Triplydra	(Final Evolution)
Floatiloch	--->	Raftnesse	--->	17
Raftnesse	(Final Evolution)
Fawneel	--->	Buckalloy	--->	52
Buckalloy	(Final Evolution)
Caracell	--->	Snattery	--->	17
Snattery	--->	Eschargot	--->	34
Eschargot	(Final Evolution)
Vachita	--->	Vacapow	--->	17
Vacapow	--->	Moomega	--->	34
Moomega	(Final Evolution)
Hobeex	--->	Honikoba	--->	21
Honikoba	(Final Evolution)
Rokilo	--->	Gravilon	--->	25
Gravilon	--->	Construkto	--->	34
Construkto	(Final Evolution)
Yelloon	--->	Roughoon	--->	25
Roughoon	--->	Azuroon	--->	34
Azuroon	(Final Evolution)""",
                color=discord.Color.red(),
            )
            page2_embed.set_thumbnail(
                url="https://media.discordapp.net/attachments/983557860803874826/1076036559893172354/THE_ELDER.png"
            )
            page2_embed.set_footer(
                text="The Elder's Library · Global Revomon Association"
            )
            await interaction.response.defer()
            await interaction.followup.send(embed=page2_embed, ephemeral=True)

        @discord.ui.button(
            label="Page 3",
            style=discord.ButtonStyle.green,
            custom_id="Evolution Page 3",
        )
        async def page3(
            self, interaction: discord.Interaction, Button: discord.ui.Button
        ):
            page3_embed = discord.Embed(
                title="Full Evolutions List Pt.3",
                description="""__**Revomon**__-> __**Evolution**__->__**At Lvl**__

- Kasket->(Final Evolution)
- Skadire->(Final Evolution)
- Khepreetle->(Final Evolution)
- Murdoll->(Final Evolution)
- Holleader->(Final Evolution)
- Kindling->(Final Evolution)
- Elvifir->Twinkletree->24
- Twinkletree->(Final Evolution)""",
                color=discord.Color.red(),
            )
            page3_embed.set_thumbnail(
                url="https://media.discordapp.net/attachments/983557860803874826/1076036559893172354/THE_ELDER.png"
            )
            page3_embed.set_footer(
                text="The Elder's Library · Global Revomon Association"
            )
            await interaction.response.defer()
            await interaction.followup.send(embed=page3_embed, ephemeral=True)

        @discord.ui.button(
            label="❌", style=discord.ButtonStyle.red, custom_id="exit"
        )
        async def exit_embed(
            self, interaction: discord.Interaction, Button: discord.ui.Button
        ):
            await interaction.message.delete()

    @commands.Cog.listener()
    async def on_ready(self):
        print("The Elder's Library(Evolutions Keyword) is ready!")
        print("---------------------------")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Ignore messages from bots (including self)
        if message.author.bot:
            return

        try:
            prompt = message.content.lower().strip()
            if prompt == "all evolutions" or prompt == "evolutions":
                embed = self.evolutions_embed()
                buttons = self.evolutions_buttons()
                await respond(
                    self.gradex, message=message, embed=embed, buttons=buttons
                )
        except Exception as e:
            print(f"An error occurred during on_message: {e}")


async def setup(gradex: commands.Bot):
    await gradex.add_cog(evolutions(gradex))
