import discord.embeds
from discord import Color, Embed, Interaction, app_commands
from discord.ext import commands

from data import (
    AbilitiesTable,
    FruitysTable,
    ItemsTable,
    MovesTable,
    NaturesTable,
    OwnedLandsTable,
    RevomonMovesTable,
    RevomonTable,
)
from utils.button_utils import Buttons
from utils.embed_utils import compare_intros, intro
from utils.revomon_utils import get_attributes


class SearchCommand(commands.Cog):
    def __init__(self, gradex: commands.Bot) -> None:
        self.gradex = gradex

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        print("The Elder's Library(Search Command) is ready!")
        print("---------------------------")

    async def ability_search_embed(self, ability_name: str) -> discord.embeds.Embed:
        ability_info = (await AbilitiesTable().get_info(ability_name.lower()))[0]
        embed = Embed(
            title=ability_info[0].title(),
            description=f"*{ability_info[1].capitalize()}*",
            color=Color.red(),
        )
        learned_by = ""
        for revomon in await RevomonTable().get_names():
            if await RevomonTable().has_ability(
                mon_name=revomon, ability_name=ability_info[0]
            ):
                learned_by += f"- *{revomon.title()}*\n"
        embed.description += f"\n\n__**Learned By**__\n{learned_by}"  # type: ignore[operator]
        embed.set_thumbnail(
            url="https://media.discordapp.net/attachments/983557860803874826/1076036559893172354/THE_ELDER.png"
        )
        embed.set_footer(text="The Elder's Library · Global Revomon Association")
        return embed

    async def allabilities_embed(self) -> discord.embeds.Embed:
        all_abilities_str = ""
        for ability in sorted(await AbilitiesTable().get_names()):
            all_abilities_str += f"- {ability.title()}\n"
        embed = Embed(
            title="All Abilities",
            description=f"__**Name**__\n{all_abilities_str}",
            color=Color.red(),
        )
        embed.set_thumbnail(
            url="https://media.discordapp.net/attachments/983557860803874826/1076036559893172354/THE_ELDER.png"
        )
        embed.set_footer(text="The Elder's Library · Global Revomon Association")
        return embed

    async def fruity_search_embed(self, fruity_name: str) -> discord.embeds.Embed:
        fruity_info = (await FruitysTable().get_info(fruity_name.lower()))[0]
        embed = Embed(
            title=fruity_info[0].title(),
            description=f"*{fruity_info[1].capitalize()}*",
            color=Color.red(),
        )
        embed.add_field(name="__**Type**__", value=fruity_info[2].title(), inline=True)
        # embed.set_thumbnail(url="") PLACEHOLDER FOR FRUITY IMAGE
        embed.set_footer(text="The Elder's Library · Global Revomon Association")
        return embed

    async def allfruitys_embed(self) -> discord.embeds.Embed:
        fruitys_str = ""
        for fruity in sorted(await FruitysTable().get_names()):
            fruitys_str += f"- **{fruity.title()}** Fruity\n"
        embed = Embed(
            title="All Fruitys",
            description=f"__**Name**__\n{fruitys_str}",
            color=Color.red(),
        )
        embed.add_field(name="__Name__", value=fruitys_str)
        embed.set_footer(text="The Elder's Library · Global Revomon Association")
        return embed

    async def item_search_embed(self, item_name: str) -> discord.embeds.Embed:
        item_info = (await ItemsTable().get_info(item_name.lower()))[0]
        embed = Embed(
            title=item_info[0].title(),
            description=f"*{item_info[1].capitalize()}*",
            color=Color.red(),
        )
        embed.add_field(
            name="__**Obtained From**__",
            value=f"*{item_info[2].title()}*",
            inline=False,
        )
        if item_info[3] is not None:
            embed.add_field(
                name="__**Cost(IGC)**__",
                value=f"*{item_info[3]}*",
                inline=False,
            )
        embed.set_thumbnail(
            url="https://media.discordapp.net/attachments/983557860803874826/1076036559893172354/THE_ELDER.png"
        )
        embed.set_footer(text="The Elder's Library · Global Revomon Association")
        return embed

    async def allitems_embed(self) -> discord.embeds.Embed:
        items_str = ""
        for item in sorted(await ItemsTable().get_names()):
            items_str += f"- {item.title()}\n"
        embed = Embed(
            title="All Items",
            description=f"__**Name**__\n{items_str}",
            color=Color.red(),
        )
        embed.set_thumbnail(
            url="https://media.discordapp.net/attachments/983557860803874826/1076036559893172354/THE_ELDER.png"
        )
        embed.set_footer(text="The Elder's Library · Global Revomon Association")

        return embed

    async def move_search_embed(self, move_name: str) -> discord.embeds.Embed:
        move_info = (await MovesTable().get_info(move_name.lower()))[0]
        embed = Embed(
            title=move_info[2].title(),
            description=f"*{move_info[5].capitalize()}*",
            color=Color.red(),
        )
        embed.add_field(
            name="__**Type**__", value=f"*{move_info[4].title()}*", inline=False
        )
        embed.add_field(
            name="__**Category**__",
            value=f"*{move_info[3].title()}*",
            inline=False,
        )
        if move_info[7] != 0:
            embed.add_field(
                name="__**Damage**__", value=f"*{move_info[7]}*", inline=False
            )
        if move_info[6] != 0.0:
            embed.add_field(
                name="__**Accuracy**__", value=f"*{move_info[6]}*", inline=False
            )
        embed.add_field(name="__**PP**__", value=f"*{move_info[8]}*", inline=False)
        embed.add_field(name="__**Priority**__", value=f"*{move_info[9]}*")
        if move_info[1] is not None:
            embed.add_field(
                name="__**Capsule #**__",
                value=f"*{move_info[1]}*",
                inline=False,
            )
        learned_by = ""
        for revomon in sorted(
            await RevomonMovesTable().get_mons_for_move(move_name=move_info[2])
        ):
            learned_by += f"- *{revomon.title()}*\n"
        embed.add_field(name="__**Learned By**__", value=learned_by, inline=False)
        embed.set_thumbnail(
            url="https://media.discordapp.net/attachments/983557860803874826/1076036559893172354/THE_ELDER.png"
        )
        embed.set_footer(text="The Elder's Library · Global Revomon Association")

        return embed

    async def nature_search_embed(self, nature_name: str) -> discord.embeds.Embed:
        nature_info = (await NaturesTable().get_info(nature_name.lower()))[0]
        embed = Embed(title=f"{nature_info[0].title()} Nature", color=Color.red())
        if nature_info[1] is None:
            embed.add_field(name="__**Stat Boosted**__", value="*None*", inline=False)
        else:
            embed.add_field(
                name="__**Stat Boosted**__",
                value=f"*{nature_info[1].title()} Stat (+10%)*",
                inline=False,
            )
        if nature_info[2] is None:
            embed.add_field(name="__**Stat Reduced**__", value="*None*", inline=False)
        else:
            embed.add_field(
                name="__**Stat Reduced**__",
                value=f"*{nature_info[2].title()} Stat (-10%)*",
                inline=False,
            )
        if nature_info[3] is not None:
            embed.add_field(
                name="__**Likes**__",
                value=f"*{nature_info[3].title()} flavored Fruitys*",
                inline=False,
            )
        if nature_info[4] is not None:
            embed.add_field(
                name="__**Dislikes**__",
                value=f"*{nature_info[4].title()} flavored Fruitys*",
                inline=False,
            )
        embed.set_thumbnail(
            url="https://media.discordapp.net/attachments/983557860803874826/1076036559893172354/THE_ELDER.png"
        )
        embed.set_footer(text="The Elder's Library · Global Revomon Association")
        return embed

    async def allnatures_embed(self) -> discord.embeds.Embed:
        nature_info = await NaturesTable().get_names()
        nature_str = ""
        for nature in sorted(nature_info):
            nature_str += f"- {nature.title()}\n"
        embed = Embed(
            title="All Natures",
            description="The Elder: *Only 20 out of the total 25 natures increase one Stat by 10% while reducing another stat by 10%. 5 natures are considered neutral and have no effect at all.*",
            color=Color.red(),
        )
        embed.add_field(name="__Nature__", value=f"{nature_str}", inline=False)
        embed.set_thumbnail(
            url="https://media.discordapp.net/attachments/983557860803874826/1076036559893172354/THE_ELDER.png"
        )
        embed.set_image(
            url="https://s3.amazonaws.com/appforest_uf/f1674293258259x900123748435524000/NATURE%20TABLE.jpg"
        )
        embed.set_footer(text="The Elder's Library · Global Revomon Association")
        return embed

    allowed_installs = app_commands.AppInstallationType(guild=True, user=True)
    search_group = app_commands.Group(
        name="search",
        description="Search for info for any Revomon related keyword.",
        allowed_installs=allowed_installs,
    )

    @search_group.command(
        name="abilities",
        description="Search for info about any Revomon ability.",
    )
    @app_commands.describe(
        name="The name of the ability you'd like more info on. Enter 'all' for a list of all the ability names."
    )
    async def abilities(
        self, interaction: Interaction, name: str | None = None
    ) -> None:
        try:
            if not name:
                embed = await self.allabilities_embed()
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            embed = await self.ability_search_embed(ability_name=name.lower())
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            print(f"Error during search_command(abilities subcommand): {e}")

    @search_group.command(
        name="fruitys", description="Search for info about any Revomon fruity."
    )
    @app_commands.describe(
        name="The name of the fruity you'd like more info on. Enter 'all' for a list of all the fruity names."
    )
    async def fruitys(self, interaction: Interaction, name: str | None = None) -> None:
        try:
            if not name:
                embed = await self.allfruitys_embed()
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            embed = await self.fruity_search_embed(fruity_name=name.lower())
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            print(f"Error during search_command(fruitys subcommand): {e}")

    @search_group.command(
        name="items", description="Search for info about any in-game item."
    )
    @app_commands.describe(
        name="The name of the item you'd like more info on. Enter 'all' for a list of all the in-game item names."
    )
    async def items(self, interaction: Interaction, name: str | None = None) -> None:
        if not name:
            embed = await self.allitems_embed()
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        embed = await self.item_search_embed(name.lower())
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @search_group.command(
        name="moves", description="Search for info about any Revomon move."
    )
    @app_commands.describe(name="The name of the move you'd like more info on.")
    async def moves(self, interaction: Interaction, name: str) -> None:
        try:
            embed = await self.move_search_embed(name.lower())
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            print(f"Error during search_command(moves subcommand): {e}")

    @search_group.command(
        name="natures", description="Search for info about any Revomon nature."
    )
    @app_commands.describe(name="The name of the nature you'd like more info on.")
    async def natures(self, interaction: Interaction, name: str | None = None) -> None:
        if not name:
            embed = await self.allnatures_embed()
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        embed = await self.nature_search_embed(name.lower())
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @search_group.command(
        name="revomon", description="Search for info about any Revomon."
    )
    @app_commands.describe(name="The name of the revomon you'd like more info on.")
    async def revomon(self, interaction: Interaction, name: str | None = None) -> None:
        try:
            buttons = Buttons(self.gradex)
            if not name:
                mon_main_view = await buttons.mon_view(user_id=interaction.user.id)
                await interaction.response.send_message(
                    view=mon_main_view, ephemeral=True
                )
                return

            if "&" in name:
                revomon_name1, revomon_name2 = map(str.strip, name.split("&"))
                if (
                    revomon_name1.lower() in await RevomonTable().get_names()
                    and revomon_name2.lower() in await RevomonTable().get_names()
                ):
                    attributes = await get_attributes(revomon_name=revomon_name1)
                    attributes2 = await get_attributes(revomon_name=revomon_name2)
                    embed = compare_intros(
                        attributes=attributes, attributes2=attributes2
                    )
                    buttons = await buttons.compare_intros_view(
                        attributes=attributes, attributes2=attributes2
                    )
                    await interaction.response.send_message(
                        embed=embed, view=buttons, ephemeral=True
                    )
            # Check if User's Prompt is a Revomon's Name
            elif name.lower() in await RevomonTable().get_names():
                # Load Data From Revomon Database
                attributes = await get_attributes(revomon_name=name)
                embed = intro(attributes=attributes)
                buttons = await buttons.intro_view(attributes=attributes)
                await interaction.response.send_message(
                    embed=embed, view=buttons, ephemeral=True
                )
        except Exception as e:
            print(f"An error occurred during search_command(revomon subcommand): {e}")

    @search_group.command(name="land-nfts", description="Search for info about any Revomon Novus land. Leave all options blank to view all lands.")
    @app_commands.choices(biome=[
        app_commands.Choice(name="Beach", value="beach"),
        app_commands.Choice(name="Caves", value="caves"),
        app_commands.Choice(name="Crater", value="crater"),
        app_commands.Choice(name="Desert", value="desert"),
        app_commands.Choice(name="Forest", value="forest"),
        app_commands.Choice(name="Jungle", value="jungle"),
        app_commands.Choice(name="Plains", value="plains"),
        app_commands.Choice(name="Swamp", value="swamp"),
        app_commands.Choice(name="Tundra", value="tundra"),
        app_commands.Choice(name="Underwater", value="underwater"),
        app_commands.Choice(name="Urban", value="urban")
        ])
    @app_commands.choices(land_type=[
        app_commands.Choice(name="Arena", value="arena"),
        app_commands.Choice(name="Clinic", value="clinic"),
        app_commands.Choice(name="Gym", value="gym"),
        app_commands.Choice(name="Labs", value="labs"),
        app_commands.Choice(name="Mine", value="mine"),
        app_commands.Choice(name="Safari Park", value="safari park"),
        app_commands.Choice(name="Shop", value="shop")
        ])
    @app_commands.choices(rarity=[
        app_commands.Choice(name="Common", value="common"),
        app_commands.Choice(name="Rare", value="Rare"),
        app_commands.Choice(name="Legendary", value="legendary"),
        app_commands.Choice(name="Mythic", value="mythic")
        ])
    @app_commands.choices(sale_status=[
        app_commands.Choice(name="For Sale", value="1"),
        app_commands.Choice(name="Not For Sale", value="0")
        ])
    @app_commands.choices(size=[
        app_commands.Choice(name="1x1", value="1x1"),
        app_commands.Choice(name="2x2", value="2x2"),
        app_commands.Choice(name="3x3", value="3x3"),
        app_commands.Choice(name="6x6", value="6x6")])
    @app_commands.describe(owners_address="The wallet address of the owner of the land.",
                           token_id="The token ID of the land.",
                           land_type="The type of land.",
                           biome="The biome of the land.",
                           rarity="The rarity of the land.",
                           sale_status="The sale status of the land.",
                           size="The size of the land."
                           )
    async def Land_nfts(self, interaction: Interaction, biome: app_commands.Choice[str] = None, land_type: app_commands.Choice[str] = None, owners_address: str = None, rarity: app_commands.Choice[str] = None, sale_status: app_commands.Choice[str] = None, size: app_commands.Choice[str] = None, token_id: int = None):  # type: ignore[assignment]
        await interaction.response.defer(ephemeral=True)

        buttons = Buttons(self.gradex)
        if not token_id and not owners_address and not land_type and not biome and not rarity and not size and not sale_status:
            land_main_view = await buttons.land_view(user_id=interaction.user.id)
            await interaction.followup.send(view=land_main_view, ephemeral=True)
            return
        else:
            try:
                # Build the response message dynamically
                lands_data = OwnedLandsTable()
                response_message = await lands_data.get_info(token_id=token_id if token_id else None, id=None, owners_address=owners_address.lower() if owners_address else None, biome=biome.value if biome else None, land_type=land_type.value if land_type else None, rarity=rarity.value if rarity else None, size=size.value if size else None, img_url=None, asc=True, sale_status=int(sale_status.value) if sale_status else None)  # type: ignore[attr-defined]
                if response_message:
                    token_ids = [land[0] for land in response_message]
                    land_main_view = await buttons.land_view(token_ids=token_ids, user_id=interaction.user.id)
                    await interaction.followup.send(view=land_main_view, ephemeral=True)
                else:
                    await interaction.followup.send("No lands found that match your criteria.", ephemeral=True)
            except Exception as e:
                print(f"An error occurred during search_command(lands subcommand): {e}")


async def setup(gradex: commands.Bot) -> None:
    try:
        await gradex.add_cog(SearchCommand(gradex))
    except Exception:
        print("ERROR in ModName 'setup' function")
