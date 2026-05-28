import discord
from discord.ext import commands
from utils.helpers import respond


class pokemon_keyword(commands.Cog):
    def __init__(self, gradex):
        self.gradex = gradex

    def pokemon_embed(self):
        embed = discord.Embed(
            title="Revomon to Pokemon",
            description="""__**Revomon**__ <---> __**Pokémon**__

Blizorra <---> Blastoise
Camprikine <---> Raticate
Champlion <---> Primeape
Craggon <---> Dragonite
Deksiple <---> Venosaur
Dominevo <---> Espeon
Drakevo <---> Flareon *(With Shelgon's moves)*
Falcolt <---> Pidgeotto
Farinade <---> Golduck
Ghopher <---> Golurk
Gorcano <---> Charizard
Hauntevo <---> Sylveon *(With Drifblims moves)*
Loftevo <---> Leafeon
Masikoridon <---> Poliwrath
Monking <---> Landorus
R3vup <---> Silvally
Radarent <---> Raichu
Raival <---> Zapdos
Skultergeist <---> Beedrill
Skwerberos <---> Luxray
Slisces <---> Empoleon
Smogshroom <---> Arbok
Soarnox <---> Togekiss
Spectreat <---> Chandelure
Twilevo <---> Umbreon
Veloswift <---> Fearow
Venturevo <---> Linoone
Volcanalisk <---> Charizard
Vyphern <---> Tangela
Wintursa <---> Maganium
Comboworm <---> Sanslash
Tidju <---> Feraligatr
Polluvern <---> Naganadel
Moontis <---> Orbeetle *(Atk & Spa stats switched)*
Leximinth <---> Grimmsnarl
Kangkross <---> Machamp
Bluezilla <---> Turtonator *(Atk and Def stats switched)*
Kickundra <---> Crabominable
Furnice <---> Darmanitan
Atolloise <---> Ludicolo
Pandozer <---> Krookodile
Tetrapion <---> Armaldo
Opawan <---> Houndoom
Dexfyre <---> Metagross *(all stats except HP are boosted by 5 point)*
Reingifir <---> Tropius
Buckalloy <---> Bisharp
Triplydra <---> Swampert
Eschargot <---> Vikavolt
Raftnesse <---> Milotic
Miraflect <---> Wobbuffet
Gardsee <---> Jumpluff
Romanfrig <---> Staraptor
Nightmort <---> Gengar
Meganeudra <---> Scolipede
Moomega <---> Blissey
Kasket <---> Klefki
Honikoba <---> Vespiquen
Construkto <---> Gigalith
Azuroon <---> Conkeldurr
Skadire <---> Weavile *(Hp/Def/Spd are boosted by 20+ points)*
Khepreetle <---> Volcarona
Murdoll <---> Mimikyu
Holleander <---> Whimsicott
Kindling <---> Eevee
Twinkletree <---> Shiinotic""",
            color=discord.Color.red(),
        )
        embed.set_thumbnail(
            url="https://media.discordapp.net/attachments/983557860803874826/1076036559893172354/THE_ELDER.png"
        )
        embed.set_author(name="The Elder's Library")
        embed.set_footer(text="Global Revomon Association")
        return embed

    class pokemon_buttons(discord.ui.View):
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
        print("The Elder's Library(Pokemon Keyword) is ready!")
        print("---------------------------")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Ignore messages from bots (including self)
        if message.author.bot:
            return

        try:
            prompt = message.content.lower().strip()
            if prompt == "pokemon" or prompt == "pokémon":
                embed = self.pokemon_embed()
                buttons = self.pokemon_buttons()
                await respond(
                    self.gradex, message=message, embed=embed, buttons=buttons
                )
        except Exception as e:
            print(f"An error occurred during on_message: {e}")


async def setup(gradex: commands.Bot):
    await gradex.add_cog(pokemon_keyword(gradex))
