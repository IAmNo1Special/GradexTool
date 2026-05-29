from data.gradexDB import OwnedLandsTable, RevomonTable
from discord import ButtonStyle, Interaction
from discord.ext import commands
from discord.ui import Button, View

from utils.embed_utils import (
    compare_counterdexs,
    compare_moves,
    compare_spawns,
    compare_stats,
    compare_types,
    counterdex,
    intro,
    land_intro,
    moves,
    spawns,
    stats,
    types,
)
from utils.revomon_utils import (
    get_attributes,
    get_book_of_land_ids,
    get_book_of_mon_names,
)


class Buttons(commands.Cog):
    def __init__(self, gradex: commands.Bot) -> None:
        self.gradex = gradex

        self.book_of_names = get_book_of_mon_names()
        self.current_page = {}
        self.attributes = {}
        self.attributes2 = {}

        self.book_of_land_ids = None
        self.book_of_land_current_page = {}
        self.land_attributes = {}

    async def mon_button(self, name: str, row):
        print("Mon button is being created...")
        mon_info = RevomonTable().get_info(name)[0]
        mon_emoji = f"<:{name}:{mon_info[-10]}>".replace(" ", "_").replace("-", "_")
        dex_num = mon_info[0]
        mon_button = Button(
            label=f"{dex_num}. {name.title()}",
            emoji=mon_emoji,
            style=ButtonStyle.gray,
            row=row,
            custom_id=f"{name.lower()}",
        )
        mon_button.callback = self.on_button_click
        print(f"Mon button for {name} has been created!")
        return mon_button

    async def land_button(self, token_id: int, row):
        print("Land button is being created...")
        land_info = OwnedLandsTable().get_info(token_id=token_id)[0]
        land_emoji = f"<:{land_info[3]}_{land_info[4]}:{land_info[8]}>".replace(
            " ", "_"
        )
        land_price = f"(${land_info[-2]})" if land_info[-2] else ""
        land_button = Button(
            label=f"{token_id}. {land_info[4].title()} · {land_info[3].title()} {land_price}",
            emoji=land_emoji,
            style=ButtonStyle.gray,
            row=row,
            custom_id=f"land {token_id}",
        )
        land_button.callback = self.on_button_click
        print(f"Land button for land {token_id} has been created!")
        return land_button

    async def stats_button(self):
        print("Stats button(Intro_buttons) is being created...")
        stats_button = Button(label="Stats", style=ButtonStyle.green, custom_id="stats")
        stats_button.callback = self.on_button_click
        print("Stats button(Intro_buttons) has been created!")
        return stats_button

    async def compare_stats_button(self):
        print("Compare Stats button(Intro_buttons) is being created...")
        compare_stats_button = Button(
            label="Compare Stats",
            style=ButtonStyle.green,
            custom_id="compare_stats",
        )
        compare_stats_button.callback = self.on_button_click
        print("Compare Stats button(Intro_buttons) has been created!")
        return compare_stats_button

    async def spawns_button(self):
        print("Spawn button(Intro_buttons) is being created...")
        spawn_info_button = Button(
            label="Spawns", style=ButtonStyle.green, custom_id="spawns"
        )
        spawn_info_button.callback = self.on_button_click
        print("Spawn button(Intro_buttons) has been created!")
        return spawn_info_button

    async def compare_spawns_button(self):
        print("Compare Spawns button(Intro_buttons) is being created...")
        compare_spawns_button = Button(
            label="Compare Spawns",
            style=ButtonStyle.green,
            custom_id="compare_Spawns",
        )
        compare_spawns_button.callback = self.on_button_click
        print("Compare Spawns button(Intro_buttons) has been created!")
        return compare_spawns_button

    async def moves_button(self):
        print("Moves button(Intro_buttons) is being created...")
        moves_button = Button(label="Moves", style=ButtonStyle.green, custom_id="moves")
        moves_button.callback = self.on_button_click
        print("Moves button(Intro_buttons) has been created!")
        return moves_button

    async def compare_moves_button(self):
        print("Compare Move List button(Intro_buttons) is being created...")
        compare_move_list_button = Button(
            label="Compare Moves",
            style=ButtonStyle.green,
            custom_id="compare_move_list",
        )
        compare_move_list_button.callback = self.on_button_click
        print("Compare Move List button(Intro_buttons) has been created!")
        return compare_move_list_button

    async def types_button(self):
        print("Types button(Intro_buttons) is being created...")
        types_button = Button(label="Types", style=ButtonStyle.green, custom_id="types")
        types_button.callback = self.on_button_click
        print("Types button(Intro_buttons) has been created!")
        return types_button

    async def compare_types_button(self):
        print("Compare Types button(Intro_buttons) is being created...")
        compare_types_button = Button(
            label="Compare Types",
            style=ButtonStyle.green,
            custom_id="compare_types",
        )
        compare_types_button.callback = self.on_button_click
        print("Compare Types button(Intro_buttons) has been created!")
        return compare_types_button

    async def counterdex_button(self):
        print("Counterdex button(Intro_buttons) is being created...")
        counterdex_button = Button(
            label="Counterdex", style=ButtonStyle.green, custom_id="counterdex"
        )
        counterdex_button.callback = self.on_button_click
        print("Counterdex button(Intro_buttons) has been created!")
        return counterdex_button

    async def compare_counterdexs_button(self):
        print("compare_counterdexs button(Intro_buttons) is being created...")
        compare_counterdexs_button = Button(
            label="Compare Counterdexs",
            style=ButtonStyle.green,
            custom_id="compare_counterdexs",
        )
        compare_counterdexs_button.callback = self.on_button_click
        print("compare_counterdexs button(Intro_buttons) has been created!")
        return compare_counterdexs_button

    def first_page_button(self, row):
        print("First page button is being created...")
        first_page_button = Button(
            emoji="⏮️", style=ButtonStyle.green, row=row, custom_id="first_page"
        )
        first_page_button.callback = self.on_button_click
        print("First page button has been created!")
        return first_page_button

    def previous_button(self, row):
        print("Previous button is being created...")
        previous_button = Button(
            emoji="⏪",
            style=ButtonStyle.green,
            row=row,
            custom_id="previous_page",
        )
        previous_button.callback = self.on_button_click
        print("Previous button has been created!")
        return previous_button

    def next_button(self, row):
        print("Next button is being created...")
        next_button = Button(
            emoji="⏩", style=ButtonStyle.green, row=row, custom_id="next_page"
        )
        next_button.callback = self.on_button_click
        print("Next button has been created!")
        return next_button

    def last_page_button(self, row):
        print("Last page button is being created...")
        last_page_button = Button(
            emoji="⏭️", style=ButtonStyle.green, row=row, custom_id="last_page"
        )
        last_page_button.callback = self.on_button_click
        print("Last page button has been created!")
        return last_page_button

    def first_page_button_land(self, row):
        print("First page button is being created...")
        first_page_button = Button(
            emoji="⏮️",
            style=ButtonStyle.green,
            row=row,
            custom_id="first_page_land",
        )
        first_page_button.callback = self.on_button_click
        print("First page button has been created!")
        return first_page_button

    def previous_button_land(self, row):
        print("Previous button is being created...")
        previous_button = Button(
            emoji="⏪",
            style=ButtonStyle.green,
            row=row,
            custom_id="previous_page_land",
        )
        previous_button.callback = self.on_button_click
        print("Previous button has been created!")
        return previous_button

    def next_button_land(self, row):
        print("Next button is being created...")
        next_button = Button(
            emoji="⏩",
            style=ButtonStyle.green,
            row=row,
            custom_id="next_page_land",
        )
        next_button.callback = self.on_button_click
        print("Next button has been created!")
        return next_button

    def last_page_button_land(self, row):
        print("Last page button is being created...")
        last_page_button = Button(
            emoji="⏭️",
            style=ButtonStyle.green,
            row=row,
            custom_id="last_page_land",
        )
        last_page_button.callback = self.on_button_click
        print("Last page button has been created!")
        return last_page_button

    async def exit_button(self, row: int):
        print("exit button is being created...")
        exit_button = Button(
            emoji="❌", style=ButtonStyle.red, row=row, custom_id="exit"
        )
        exit_button.callback = self.on_button_click
        print("exit button has been created!")
        return exit_button

    async def search_button_land(self, row: int):
        print("Search button is being created...")
        search_button = Button(
            emoji="🔎",
            style=ButtonStyle.green,
            row=row,
            custom_id="search_land",
        )
        search_button.callback = self.on_button_click
        print("Search button has been created!")
        return search_button

    async def filter_button_land(self, row: int):
        print("Filter button is being created...")
        filter_emoji = "<:filter:1327457883587219516>"
        filter_button = Button(
            emoji=filter_emoji,
            style=ButtonStyle.green,
            row=row,
            custom_id="filter_land",
        )
        filter_button.callback = self.on_button_click
        print("Filter button has been created!")
        return filter_button

    async def sort_by_button_land(self, row: int):
        print("Sort by button is being created...")
        sort_by_emoji = "<:sortby:1327458375994314875>"
        sort_by_button = Button(
            emoji=sort_by_emoji,
            style=ButtonStyle.green,
            row=row,
            custom_id="sort_by_land",
        )
        sort_by_button.callback = self.on_button_click
        print("Sort by button has been created!")
        return sort_by_button

    async def search_settings_button_land(self, row: int):
        print("Search settings button is being created...")
        search_settings_button = Button(
            emoji="⚙️",
            style=ButtonStyle.green,
            row=row,
            custom_id="search_settings_land",
        )
        search_settings_button.callback = self.on_button_click
        print("Search settings button has been created!")
        return search_settings_button

    async def mon_view(self, user_id: int):
        print("Mon View are being created...")
        view = View(timeout=None)
        if self.current_page.get(user_id) is not None:
            curr_page = self.current_page[user_id]
        else:
            curr_page = 1
            self.current_page[user_id] = curr_page
        curr_page_content = self.book_of_names[curr_page - 1]
        row = 0
        for name in curr_page_content:
            button = await self.mon_button(name=name, row=row)
            view.add_item(button)
            if RevomonTable().get_info(name)[0][8] is None:
                row += 1
            if row == 4 or name == self.book_of_names[-1][-1]:
                first_page_button = self.first_page_button(row=row)
                prev_button = self.previous_button(row=row)
                next_button = self.next_button(row=row)
                last_page_button = self.last_page_button(row=row)
                view.add_item(first_page_button)
                view.add_item(prev_button)
                view.add_item(next_button)
                view.add_item(last_page_button)
                return view

    async def land_view(self, user_id: int = None, token_ids: list = None):
        print("Land View are being created...")
        view = View(timeout=None)
        if token_ids is not None:
            self.book_of_land_ids = get_book_of_land_ids(token_ids=token_ids)
        elif token_ids is None and self.book_of_land_ids is None:
            self.book_of_land_ids = get_book_of_land_ids()
        if self.book_of_land_current_page.get(user_id) is not None:
            curr_page = self.book_of_land_current_page[user_id]
        else:
            curr_page = 1
            self.book_of_land_current_page[user_id] = curr_page
        curr_page_content = self.book_of_land_ids[curr_page - 1]
        row = 0
        for token_id in curr_page_content:
            button = await self.land_button(token_id=token_id, row=row)
            view.add_item(button)
            if len(view.children) % 3 == 0 or token_id == self.book_of_land_ids[-1][-1]:
                row += 1
            if row == 4 or token_id == self.book_of_land_ids[-1][-1]:
                first_page_button = self.first_page_button_land(row=row)
                prev_button = self.previous_button_land(row=row)
                next_button = self.next_button_land(row=row)
                last_page_button = self.last_page_button_land(row=row)
                view.add_item(first_page_button)
                view.add_item(prev_button)
                view.add_item(next_button)
                view.add_item(last_page_button)
                # view.add_item(await self.search_settings_button_land(row=row))
                print("Land View has been created!")
                return view

    async def intro_view(self, attributes: dict = None):
        print("Intro buttons are being created...")
        if attributes is not None:
            self.attributes = attributes
        intro_view = View(timeout=None)
        intro_view.add_item(await self.stats_button())
        intro_view.add_item(await self.spawns_button())
        intro_view.add_item(await self.moves_button())
        intro_view.add_item(await self.types_button())
        intro_view.add_item(await self.counterdex_button())
        print("Intro buttons have been created!")
        return intro_view

    async def compare_intros_view(
        self, attributes: dict = None, attributes2: dict = None
    ):
        print("Compare Intros buttons are being created...")
        if attributes is not None:
            self.attributes = attributes
        if attributes2 is not None:
            self.attributes2 = attributes2
        compare_intros_view = View(timeout=None)
        compare_intros_view.add_item(await self.compare_stats_button())
        compare_intros_view.add_item(await self.compare_spawns_button())
        compare_intros_view.add_item(await self.compare_moves_button())
        compare_intros_view.add_item(await self.compare_types_button())
        compare_intros_view.add_item(await self.compare_counterdexs_button())
        print("Compare Intros buttons have been created!")
        return compare_intros_view

    @commands.Cog.listener()
    async def on_ready(self):
        print("utils(Button Utils) is ready!")
        print("---------------------------")

    @commands.Cog.listener()
    async def on_button_click(self, interaction: Interaction):
        try:
            if interaction.user.bot:
                return

            custom_id = interaction.data["custom_id"]
            print(f"Button Clicked!\nCustom ID: {custom_id}")

            if custom_id.lower() in RevomonTable().get_names():
                await interaction.response.defer()
                print(f"{interaction.user} clicked {custom_id.title()}")
                self.attributes = get_attributes(revomon_name=custom_id.lower())
                view = await self.intro_view(attributes=self.attributes)
                embed = intro(self.attributes)
                await interaction.followup.send(embed=embed, view=view, ephemeral=True)
                print("Intro embed sent!")

            if "land " in custom_id.lower():
                raw_token_id = int(custom_id.split(" ")[1])
                await interaction.response.defer()
                print(f"{interaction.user} clicked {custom_id.title()}")
                land_obj = OwnedLandsTable()
                land_info = land_obj.get_info(token_id=raw_token_id)[0]
                land_dict = {
                    "token_id": land_info[0],
                    "id": land_info[1],
                    "owners_address": land_info[2],
                    "biome": land_info[3],
                    "land_type": land_info[4],
                    "rarity": land_info[5],
                    "size": land_info[6],
                    "img_url": land_info[7],
                    "emoji": land_info[8],
                    "for_sale": bool(land_info[9]),
                    "token_symbol": land_info[10],
                    "for_sale_usd": land_info[11],
                    "for_sale_token": land_info[12],
                }

                self.land_attributes = land_dict
                embed = land_intro(attributes=self.land_attributes)
                await interaction.followup.send(embed=embed, ephemeral=True)
                print("Land Intro embed sent!")

            if custom_id == "last_page":
                await interaction.response.defer()
                self.current_page[interaction.user.id] -= 1
                if self.current_page[interaction.user.id] < 1:
                    self.current_page[interaction.user.id] = 1
                self.current_page[interaction.user.id] = len(self.book_of_names)
                view = await self.mon_view(user_id=interaction.user.id)
                await interaction.followup.edit_message(
                    message_id=interaction.message.id, view=view
                )

            if custom_id == "previous_page":
                await interaction.response.defer()
                self.current_page[interaction.user.id] -= 1
                if self.current_page[interaction.user.id] < 1:
                    self.current_page[interaction.user.id] = 1
                view = await self.mon_view(user_id=interaction.user.id)
                await interaction.followup.edit_message(
                    message_id=interaction.message.id, view=view
                )

            if custom_id == "next_page":
                await interaction.response.defer()
                self.current_page[interaction.user.id] += 1
                if self.current_page[interaction.user.id] < 1:
                    self.current_page[interaction.user.id] = 1
                view = await self.mon_view(user_id=interaction.user.id)
                await interaction.followup.edit_message(
                    message_id=interaction.message.id, view=view
                )

            if custom_id == "first_page":
                await interaction.response.defer()
                self.current_page[interaction.user.id] = 1
                view = await self.mon_view(user_id=interaction.user.id)
                await interaction.followup.edit_message(
                    message_id=interaction.message.id, view=view
                )

            if custom_id == "last_page_land":
                await interaction.response.defer()
                user_id = interaction.user.id
                self.book_of_land_current_page[user_id] = len(self.book_of_land_ids)
                if self.book_of_land_current_page[user_id] < 1:
                    self.book_of_land_current_page[user_id] = 1
                view = await self.land_view(user_id=user_id)
                await interaction.followup.edit_message(
                    message_id=interaction.message.id, view=view
                )

            if custom_id == "previous_page_land":
                await interaction.response.defer()
                user_id = interaction.user.id
                self.book_of_land_current_page[user_id] -= 1
                if self.book_of_land_current_page[user_id] < 1:
                    self.book_of_land_current_page[user_id] = 1
                curr_page = self.book_of_land_current_page[user_id]
                view = await self.land_view(user_id=user_id)
                await interaction.followup.edit_message(
                    message_id=interaction.message.id, view=view
                )

            if custom_id == "next_page_land":
                await interaction.response.defer()
                user_id = interaction.user.id
                self.book_of_land_current_page[user_id] += 1
                if self.book_of_land_current_page[user_id] < 1:
                    self.book_of_land_current_page[user_id] = 1
                curr_page = self.book_of_land_current_page[user_id]
                print(curr_page)
                view = await self.land_view(user_id=user_id)
                await interaction.followup.edit_message(
                    message_id=interaction.message.id, view=view
                )

            if custom_id == "first_page_land":
                await interaction.response.defer()
                user_id = interaction.user.id
                self.book_of_land_current_page[user_id] = 1
                view = await self.land_view(user_id=user_id)
                await interaction.followup.edit_message(
                    message_id=interaction.message.id, view=view
                )

            if custom_id == "search_settings_land":
                await interaction.response.defer()
                view = View(timeout=None)
                view.add_item(await self.sort_by_button_land(row=1))
                view.add_item(await self.search_button_land(row=1))
                view.add_item(await self.filter_button_land(row=1))
                await interaction.followup.send(view=view, ephemeral=True)

            try:
                if custom_id == "stats":
                    print(f"{interaction.user} clicked {custom_id}")
                    embed = stats(self.attributes)
                    await interaction.response.defer()
                    await interaction.followup.send(embed=embed, ephemeral=True)
                    print("Stats embed sent!")
            except Exception as e:
                print(
                    f"An error occurred trying to click the 'Stats' Button from the Intro script: {e}"
                )

            if custom_id == "compare_stats":
                print(f"{interaction.user} clicked {custom_id}")
                embed = compare_stats(self.attributes, self.attributes2)
                await interaction.response.defer()
                await interaction.followup.send(embed=embed, ephemeral=True)
                print("Compare Stats embed sent!")

            if custom_id == "spawns":
                print(f"{interaction.user} clicked {custom_id}")
                embed = spawns(self.attributes)
                await interaction.response.defer()
                await interaction.followup.send(embed=embed, ephemeral=True)
                print("Compare Spawns embed sent!")

            if custom_id == "compare_spawns":
                print(f"{interaction.user} clicked {custom_id}")
                embed = compare_spawns(self.attributes, self.attributes2)
                await interaction.response.defer()
                await interaction.followup.send(embed=embed, ephemeral=True)
                print("Compare Spawns embed sent!")

            if custom_id == "moves":
                print(f"{interaction.user} clicked {custom_id}")
                embed = moves(self.attributes)
                await interaction.response.defer()
                await interaction.followup.send(embed=embed, ephemeral=True)
                print("Compare Spawns embed sent!")

            if custom_id == "compare_moves":
                print(f"{interaction.user} clicked {custom_id}")
                embed = compare_moves(self.attributes, self.attributes2)
                await interaction.response.defer()
                await interaction.followup.send(embed=embed, ephemeral=True)

            if custom_id == "types":
                print(f"{interaction.user} clicked {custom_id}")
                embed = types(self.attributes)
                await interaction.response.defer()
                await interaction.followup.send(embed=embed, ephemeral=True)
                print("Compare Spawns embed sent!")

            if custom_id == "compare_types":
                print(f"{interaction.user} clicked {custom_id}")
                embed, embed2 = compare_types(self.attributes, self.attributes2)
                await interaction.response.defer()
                await interaction.followup.send(embed=embed, ephemeral=True)
                await interaction.followup.send(embed=embed2, ephemeral=True)
                print("Compare Types embeds sent!")

            if custom_id == "counterdex":
                print(f"{interaction.user} clicked {custom_id}")
                embed = counterdex(self.attributes)
                await interaction.response.defer()
                await interaction.followup.send(embed=embed, ephemeral=True)
                print("Counterdex embed sent!")

            if custom_id == "compare_counterdexs":
                print(f"{interaction.user} clicked {custom_id}")
                embed = compare_counterdexs(self.attributes, self.attributes2)
                await interaction.response.defer()
                await interaction.followup.send(embed=embed, ephemeral=True)
                print("compare_counterdexs embed sent!")

        except Exception as e:
            print(f"Error: {e}")


async def setup(gradex: commands.Bot):
    await gradex.add_cog(Buttons(gradex))
