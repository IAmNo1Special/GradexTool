from typing import Any
<<<<<<< HEAD

from discord import ButtonStyle, Interaction, SelectOption
from discord.ext import commands
from discord.ui import Button, Select, View

=======

from discord import ButtonStyle, Interaction
from discord.ext import commands
from discord.ui import Button, View

>>>>>>> de733c415448a6db7eb45eb4a06a6462f48833b2
from data import OwnedLandsTable, RevomonTable
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

        self.book_of_names = None
        self.current_page = {}  # type: ignore[var-annotated]
        self.attributes = {}  # type: ignore[var-annotated]
        self.attributes2 = {}  # type: ignore[var-annotated]

        self.book_of_land_ids = None
        self.book_of_land_current_page = {}  # type: ignore[var-annotated]
        self.land_attributes = {}  # type: ignore[var-annotated]
<<<<<<< HEAD
        self.group_by_evo = True
=======
>>>>>>> de733c415448a6db7eb45eb4a06a6462f48833b2

    async def mon_button(self, name: str, row: Any) -> Any:
        print("Mon button is being created...")
        mon_info = (await RevomonTable().get_info(name))[0]
<<<<<<< HEAD
        
        # Safely load and cache application emojis from Discord API
        if not hasattr(self, "app_emojis") or self.app_emojis is None:
            from utils.emoji_utils import list_application_emojis
            try:
                emojis = await list_application_emojis()
                self.app_emojis = {e["name"]: e["id"] for e in emojis}
            except Exception as e:
                print(f"Failed to fetch application emojis: {e}")
                self.app_emojis = {}

        emoji_name = name.lower().replace(" ", "_").replace("-", "_")
        emoji_id = None
        if hasattr(self, "app_emojis") and self.app_emojis:
            emoji_id = self.app_emojis.get(emoji_name)

        # Fallback to index -10 for tests where mocked mon_info represents the old 43-column schema
        if not emoji_id and len(mon_info) > 18:
            emoji_id = mon_info[-10]

        mon_emoji = f"<:{emoji_name}:{emoji_id}>" if emoji_id else None
=======
        mon_emoji = f"<:{name}:{mon_info[-10]}>".replace(" ", "_").replace("-", "_")
>>>>>>> de733c415448a6db7eb45eb4a06a6462f48833b2
        dex_num = mon_info[0]
        mon_button = Button(  # type: ignore[var-annotated]
            label=f"{dex_num}. {name.title()}",
            emoji=mon_emoji,
            style=ButtonStyle.gray,
            row=row,
            custom_id=f"{name.lower()}",
        )
        mon_button.callback = self.on_button_click  # type: ignore[method-assign]
        print(f"Mon button for {name} has been created!")
        return mon_button

    async def land_button(self, token_id: int, row: Any) -> Any:
        print("Land button is being created...")
        land_info = (await OwnedLandsTable().get_info(token_id=token_id))[0]
        land_emoji = f"<:{land_info[3]}_{land_info[4]}:{land_info[8]}>".replace(
            " ", "_"
        )
        land_price = f"(${land_info[-2]})" if land_info[-2] else ""
        land_button = Button(  # type: ignore[var-annotated]
            label=f"{token_id}. {land_info[4].title()} · {land_info[3].title()} {land_price}",
            emoji=land_emoji,
            style=ButtonStyle.gray,
            row=row,
            custom_id=f"land {token_id}",
        )
        land_button.callback = self.on_button_click  # type: ignore[method-assign]
        print(f"Land button for land {token_id} has been created!")
        return land_button

    async def stats_button(self) -> Any:
        print("Stats button(Intro_buttons) is being created...")
        stats_button = Button(label="Stats", style=ButtonStyle.green, custom_id="stats")  # type: ignore[var-annotated]
        stats_button.callback = self.on_button_click  # type: ignore[method-assign]
        print("Stats button(Intro_buttons) has been created!")
        return stats_button

    async def compare_stats_button(self) -> Any:
        print("Compare Stats button(Intro_buttons) is being created...")
        compare_stats_button = Button(  # type: ignore[var-annotated]
            label="Compare Stats",
            style=ButtonStyle.green,
            custom_id="compare_stats",
        )
        compare_stats_button.callback = self.on_button_click  # type: ignore[method-assign]
        print("Compare Stats button(Intro_buttons) has been created!")
        return compare_stats_button

    async def spawns_button(self) -> Any:
        print("Spawn button(Intro_buttons) is being created...")
        spawn_info_button = Button(  # type: ignore[var-annotated]
            label="Spawns", style=ButtonStyle.green, custom_id="spawns"
        )
        spawn_info_button.callback = self.on_button_click  # type: ignore[method-assign]
        print("Spawn button(Intro_buttons) has been created!")
        return spawn_info_button

    async def compare_spawns_button(self) -> Any:
        print("Compare Spawns button(Intro_buttons) is being created...")
        compare_spawns_button = Button(  # type: ignore[var-annotated]
            label="Compare Spawns",
            style=ButtonStyle.green,
            custom_id="compare_Spawns",
        )
        compare_spawns_button.callback = self.on_button_click  # type: ignore[method-assign]
        print("Compare Spawns button(Intro_buttons) has been created!")
        return compare_spawns_button

    async def moves_button(self) -> Any:
        print("Moves button(Intro_buttons) is being created...")
        moves_button = Button(label="Moves", style=ButtonStyle.green, custom_id="moves")  # type: ignore[var-annotated]
        moves_button.callback = self.on_button_click  # type: ignore[method-assign]
        print("Moves button(Intro_buttons) has been created!")
        return moves_button

    async def compare_moves_button(self) -> Any:
        print("Compare Move List button(Intro_buttons) is being created...")
        compare_move_list_button = Button(  # type: ignore[var-annotated]
            label="Compare Moves",
            style=ButtonStyle.green,
            custom_id="compare_move_list",
        )
        compare_move_list_button.callback = self.on_button_click  # type: ignore[method-assign]
        print("Compare Move List button(Intro_buttons) has been created!")
        return compare_move_list_button

    async def types_button(self) -> Any:
        print("Types button(Intro_buttons) is being created...")
        types_button = Button(label="Types", style=ButtonStyle.green, custom_id="types")  # type: ignore[var-annotated]
        types_button.callback = self.on_button_click  # type: ignore[method-assign]
        print("Types button(Intro_buttons) has been created!")
        return types_button

    async def compare_types_button(self) -> Any:
        print("Compare Types button(Intro_buttons) is being created...")
        compare_types_button = Button(  # type: ignore[var-annotated]
            label="Compare Types",
            style=ButtonStyle.green,
            custom_id="compare_types",
        )
        compare_types_button.callback = self.on_button_click  # type: ignore[method-assign]
        print("Compare Types button(Intro_buttons) has been created!")
        return compare_types_button

    async def counterdex_button(self) -> Any:
        print("Counterdex button(Intro_buttons) is being created...")
        counterdex_button = Button(  # type: ignore[var-annotated]
            label="Counterdex", style=ButtonStyle.green, custom_id="counterdex"
        )
        counterdex_button.callback = self.on_button_click  # type: ignore[method-assign]
        print("Counterdex button(Intro_buttons) has been created!")
        return counterdex_button

    async def compare_counterdexs_button(self) -> Any:
        print("compare_counterdexs button(Intro_buttons) is being created...")
        compare_counterdexs_button = Button(  # type: ignore[var-annotated]
            label="Compare Counterdexs",
            style=ButtonStyle.green,
            custom_id="compare_counterdexs",
        )
        compare_counterdexs_button.callback = self.on_button_click  # type: ignore[method-assign]
        print("compare_counterdexs button(Intro_buttons) has been created!")
        return compare_counterdexs_button

    def first_page_button(self, row: Any) -> Any:
        print("First page button is being created...")
        first_page_button = Button(  # type: ignore[var-annotated]
            emoji="⏮️", style=ButtonStyle.green, row=row, custom_id="first_page"
        )
        first_page_button.callback = self.on_button_click  # type: ignore[method-assign]
        print("First page button has been created!")
        return first_page_button

    def previous_button(self, row: Any) -> Any:
        print("Previous button is being created...")
        previous_button = Button(  # type: ignore[var-annotated]
            emoji="⏪",
            style=ButtonStyle.green,
            row=row,
            custom_id="previous_page",
        )
        previous_button.callback = self.on_button_click  # type: ignore[method-assign]
        print("Previous button has been created!")
        return previous_button

    def next_button(self, row: Any) -> Any:
        print("Next button is being created...")
        next_button = Button(  # type: ignore[var-annotated]
            emoji="⏩", style=ButtonStyle.green, row=row, custom_id="next_page"
        )
        next_button.callback = self.on_button_click  # type: ignore[method-assign]
        print("Next button has been created!")
        return next_button

    def last_page_button(self, row: Any) -> Any:
        print("Last page button is being created...")
        last_page_button = Button(  # type: ignore[var-annotated]
            emoji="⏭️", style=ButtonStyle.green, row=row, custom_id="last_page"
        )
        last_page_button.callback = self.on_button_click  # type: ignore[method-assign]
        print("Last page button has been created!")
        return last_page_button

    def first_page_button_land(self, row: Any) -> Any:
        print("First page button is being created...")
        first_page_button = Button(  # type: ignore[var-annotated]
            emoji="⏮️",
            style=ButtonStyle.green,
            row=row,
            custom_id="first_page_land",
        )
        first_page_button.callback = self.on_button_click  # type: ignore[method-assign]
        print("First page button has been created!")
        return first_page_button

    def previous_button_land(self, row: Any) -> Any:
        print("Previous button is being created...")
        previous_button = Button(  # type: ignore[var-annotated]
            emoji="⏪",
            style=ButtonStyle.green,
            row=row,
            custom_id="previous_page_land",
        )
        previous_button.callback = self.on_button_click  # type: ignore[method-assign]
        print("Previous button has been created!")
        return previous_button

    def next_button_land(self, row: Any) -> Any:
        print("Next button is being created...")
        next_button = Button(  # type: ignore[var-annotated]
            emoji="⏩",
            style=ButtonStyle.green,
            row=row,
            custom_id="next_page_land",
        )
        next_button.callback = self.on_button_click  # type: ignore[method-assign]
        print("Next button has been created!")
        return next_button

    def last_page_button_land(self, row: Any) -> Any:
        print("Last page button is being created...")
        last_page_button = Button(  # type: ignore[var-annotated]
            emoji="⏭️",
            style=ButtonStyle.green,
            row=row,
            custom_id="last_page_land",
        )
        last_page_button.callback = self.on_button_click  # type: ignore[method-assign]
        print("Last page button has been created!")
        return last_page_button

    async def exit_button(self, row: int) -> Any:
        print("exit button is being created...")
        exit_button = Button(  # type: ignore[var-annotated]
            emoji="❌", style=ButtonStyle.red, row=row, custom_id="exit"
        )
        exit_button.callback = self.on_button_click  # type: ignore[method-assign]
        print("exit button has been created!")
        return exit_button

    async def search_button_land(self, row: int) -> Any:
        print("Search button is being created...")
        search_button = Button(  # type: ignore[var-annotated]
            emoji="🔎",
            style=ButtonStyle.green,
            row=row,
            custom_id="search_land",
        )
        search_button.callback = self.on_button_click  # type: ignore[method-assign]
        print("Search button has been created!")
        return search_button

    async def filter_button_land(self, row: int) -> Any:
        print("Filter button is being created...")
        filter_emoji = "<:filter:1327457883587219516>"
        filter_button = Button(  # type: ignore[var-annotated]
            emoji=filter_emoji,
            style=ButtonStyle.green,
            row=row,
            custom_id="filter_land",
        )
        filter_button.callback = self.on_button_click  # type: ignore[method-assign]
        print("Filter button has been created!")
        return filter_button

    async def sort_by_button_land(self, row: int) -> Any:
        print("Sort by button is being created...")
        sort_by_emoji = "<:sortby:1327458375994314875>"
        sort_by_button = Button(  # type: ignore[var-annotated]
            emoji=sort_by_emoji,
            style=ButtonStyle.green,
            row=row,
            custom_id="sort_by_land",
        )
        sort_by_button.callback = self.on_button_click  # type: ignore[method-assign]
        print("Sort by button has been created!")
        return sort_by_button

    async def search_settings_button_land(self, row: int) -> Any:
        print("Search settings button is being created...")
        search_settings_button = Button(  # type: ignore[var-annotated]
            emoji="⚙️",
            style=ButtonStyle.green,
            row=row,
            custom_id="search_settings_land",
        )
        search_settings_button.callback = self.on_button_click  # type: ignore[method-assign]
        print("Search settings button has been created!")
        return search_settings_button

    async def mon_view(self, user_id: int) -> Any:
        print("Mon View are being created...")
        if self.book_of_names is None:
            self.book_of_names = await get_book_of_mon_names()  # type: ignore[assignment]
        view = View(timeout=None)
        if self.current_page.get(user_id) is not None:
            curr_page = self.current_page[user_id]
        else:
            curr_page = 1
            self.current_page[user_id] = curr_page
        curr_page_content = self.book_of_names[curr_page - 1]  # type: ignore[index]
        row = 0
        items_in_row = 0
        for name in curr_page_content:
            button = await self.mon_button(name=name, row=row)
            view.add_item(button)
<<<<<<< HEAD
            items_in_row += 1
            
            if self.group_by_evo:
                info = (await RevomonTable().get_info(name))[0]
                evo_next = None
                if len(info) >= 24:
                    evo_next = info[15]
                elif len(info) >= 18:
                    evo_next = info[8]
                is_final = (evo_next is None or evo_next == "" or evo_next == "none")
                should_increment = is_final or items_in_row >= 5
            else:
                should_increment = items_in_row >= 5

            if should_increment:
                row += 1
                items_in_row = 0
=======
            if (await RevomonTable().get_info(name))[0][8] is None:
                row += 1
>>>>>>> de733c415448a6db7eb45eb4a06a6462f48833b2
            if row == 4 or name == self.book_of_names[-1][-1]:  # type: ignore[index]
                first_page_button = self.first_page_button(row=row)
                prev_button = self.previous_button(row=row)
                search_button = Button(
                    label="",
                    emoji="🔍",
                    style=ButtonStyle.secondary,
                    custom_id="search_sort_mon",
                    row=row,
                )

                # Attach sort callback directly so the View handles it
                buttons_self = self

                async def search_callback(search_interaction: Interaction) -> None:
                    sort_by_menu = Select(
                        placeholder="Sort by...",
                        custom_id="mon_sort_by_select",
                        row=0,
                        options=[
                            SelectOption(label="Dex #", value="dex_id", description="Sort by Pokédex number"),
                            SelectOption(label="Name", value="name", description="Sort alphabetically"),
                            SelectOption(label="Type", value="type1", description="Sort by primary type"),
                            SelectOption(label="HP", value="hp", description="Sort by HP stat"),
                            SelectOption(label="ATK", value="atk", description="Sort by Attack stat"),
                            SelectOption(label="DEF", value="def", description="Sort by Defense stat"),
                            SelectOption(label="SPA", value="spa", description="Sort by Sp. Attack stat"),
                            SelectOption(label="SPD", value="spd", description="Sort by Sp. Defense stat"),
                            SelectOption(label="SPE", value="spe", description="Sort by Speed stat"),
                            SelectOption(label="Rarity", value="rarity", description="Sort by rarity"),
                        ],
                    )

                    sort_order_menu = Select(
                        placeholder="Sort order...",
                        custom_id="mon_sort_order_select",
                        row=1,
                        options=[
                            SelectOption(label="Ascending", value="asc", emoji="⬆️", description="A → Z, lowest → highest"),
                            SelectOption(label="Descending", value="desc", emoji="⬇️", description="Z → A, highest → lowest"),
                        ],
                    )

                    apply_button = Button(
                        label="Apply Sort",
                        emoji="✅",
                        style=ButtonStyle.success,
                        custom_id="apply_mon_sort",
                        row=2,
                    )

                    cancel_button = Button(
                        label="Cancel",
                        style=ButtonStyle.secondary,
                        custom_id="cancel_mon_sort",
                        row=2,
                    )

                    sort_view = View(timeout=None)
                    sort_view.add_item(sort_by_menu)
                    sort_view.add_item(sort_order_menu)
                    sort_view.add_item(apply_button)
                    sort_view.add_item(cancel_button)

                    async def sort_by_callback(select_interaction: Interaction) -> None:
                        await select_interaction.response.defer()

                    async def sort_order_callback(select_interaction: Interaction) -> None:
                        await select_interaction.response.defer()

                    async def apply_sort_callback(apply_interaction: Interaction) -> None:
                        sort_by_value = sort_by_menu.values[0] if sort_by_menu.values else "dex_id"
                        asc = True
                        if sort_order_menu.values:
                            asc = sort_order_menu.values[0] == "asc"
                        sorted_names = await RevomonTable().get_sorted_names(sort_by=sort_by_value, asc=asc)
                        buttons_self.group_by_evo = (sort_by_value == "dex_id")
                        buttons_self.book_of_names = await get_book_of_mon_names(
                            names=sorted_names, group_by_evo=buttons_self.group_by_evo
                        )
                        buttons_self.current_page[apply_interaction.user.id] = 1
                        new_view = await buttons_self.mon_view(user_id=apply_interaction.user.id)
                        await apply_interaction.response.edit_message(view=new_view)

                    async def cancel_sort_callback(cancel_interaction: Interaction) -> None:
                        restored_view = await buttons_self.mon_view(user_id=cancel_interaction.user.id)
                        await cancel_interaction.response.edit_message(view=restored_view)

                    sort_by_menu.callback = sort_by_callback
                    sort_order_menu.callback = sort_order_callback
                    apply_button.callback = apply_sort_callback
                    cancel_button.callback = cancel_sort_callback

                    # Replace the mon view with the sort options on the same message
                    await search_interaction.response.edit_message(view=sort_view)

                search_button.callback = search_callback

                next_button = self.next_button(row=row)
                last_page_button = self.last_page_button(row=row)
                view.add_item(first_page_button)
                view.add_item(prev_button)
                view.add_item(search_button)
                view.add_item(next_button)
                view.add_item(last_page_button)
                return view

    async def land_view(self, user_id: int = None, token_ids: list = None) -> Any:  # type: ignore[assignment, type-arg]
        print("Land View are being created...")
        view = View(timeout=None)
        if token_ids is not None:
            self.book_of_land_ids = await get_book_of_land_ids(token_ids=token_ids)  # type: ignore[assignment]
        elif token_ids is None and self.book_of_land_ids is None:
            self.book_of_land_ids = await get_book_of_land_ids()
        if self.book_of_land_current_page.get(user_id) is not None:
            curr_page = self.book_of_land_current_page[user_id]
        else:
            curr_page = 1
            self.book_of_land_current_page[user_id] = curr_page
        curr_page_content = self.book_of_land_ids[curr_page - 1]  # type: ignore[index]
        row = 0
        for token_id in curr_page_content:
            button = await self.land_button(token_id=token_id, row=row)
            view.add_item(button)
            if len(view.children) % 3 == 0 or token_id == self.book_of_land_ids[-1][-1]:  # type: ignore[index]
                row += 1
            if row == 4 or token_id == self.book_of_land_ids[-1][-1]:  # type: ignore[index]
                first_page_button = self.first_page_button_land(row=row)
                prev_button = self.previous_button_land(row=row)
                search_button = Button(
                    label="",
                    emoji="🔍",
                    style=ButtonStyle.secondary,
                    custom_id="search_sort_land",
                    row=row,
                )

                # Attach sort callback directly so the View handles it
                buttons_self = self

                async def search_callback(search_interaction: Interaction) -> None:
                    sort_by_menu = Select(
                        placeholder="Sort by...",
                        custom_id="land_sort_by_select",
                        row=0,
                        options=[
                            SelectOption(label="Biome", value="biome", description="Sort by biome"),
                            SelectOption(label="Land Type", value="land_type", description="Sort by land type"),
                            SelectOption(label="Rarity", value="rarity", description="Sort by rarity"),
                            SelectOption(label="Price", value="for_sale_usd", description="Sort by price"),
                            SelectOption(label="Size", value="size", description="Sort by size"),
                            SelectOption(label="Owner's Address", value="owners_address", description="Sort by owner"),
                        ],
                    )

                    sort_order_menu = Select(
                        placeholder="Sort order...",
                        custom_id="land_sort_order_select",
                        row=1,
                        options=[
                            SelectOption(label="Ascending", value="asc", emoji="⬆️", description="A → Z, lowest → highest"),
                            SelectOption(label="Descending", value="desc", emoji="⬇️", description="Z → A, highest → lowest"),
                        ],
                    )

                    apply_button = Button(
                        label="Apply Sort",
                        emoji="✅",
                        style=ButtonStyle.success,
                        custom_id="apply_land_sort",
                        row=2,
                    )

                    cancel_button = Button(
                        label="Cancel",
                        style=ButtonStyle.secondary,
                        custom_id="cancel_land_sort",
                        row=2,
                    )

                    sort_view = View(timeout=None)
                    sort_view.add_item(sort_by_menu)
                    sort_view.add_item(sort_order_menu)
                    sort_view.add_item(apply_button)
                    sort_view.add_item(cancel_button)

                    async def sort_by_callback(select_interaction: Interaction) -> None:
                        await select_interaction.response.defer()

                    async def sort_order_callback(select_interaction: Interaction) -> None:
                        await select_interaction.response.defer()

                    async def apply_sort_callback(apply_interaction: Interaction) -> None:
                        sort_by_value = sort_by_menu.values[0] if sort_by_menu.values else "token_id"
                        asc = True
                        if sort_order_menu.values:
                            asc = sort_order_menu.values[0] == "asc"
                        sorted_lands = await OwnedLandsTable().get_info(sort_by=sort_by_value, asc=asc)
                        if sorted_lands:
                            sorted_token_ids = [land[0] for land in sorted_lands]
                            buttons_self.book_of_land_ids = await get_book_of_land_ids(token_ids=sorted_token_ids)
                            buttons_self.book_of_land_current_page[apply_interaction.user.id] = 1
                        new_view = await buttons_self.land_view(user_id=apply_interaction.user.id)
                        await apply_interaction.response.edit_message(view=new_view)

                    async def cancel_sort_callback(cancel_interaction: Interaction) -> None:
                        # Restore the land view without changing sort
                        restored_view = await buttons_self.land_view(user_id=cancel_interaction.user.id)
                        await cancel_interaction.response.edit_message(view=restored_view)

                    sort_by_menu.callback = sort_by_callback
                    sort_order_menu.callback = sort_order_callback
                    apply_button.callback = apply_sort_callback
                    cancel_button.callback = cancel_sort_callback

                    # Replace the land view with the sort options on the same message
                    await search_interaction.response.edit_message(view=sort_view)

                search_button.callback = search_callback

                next_button = self.next_button_land(row=row)
                last_page_button = self.last_page_button_land(row=row)
                view.add_item(first_page_button)
                view.add_item(prev_button)
                view.add_item(search_button)
                view.add_item(next_button)
                view.add_item(last_page_button)
                print("Land View has been created!")
                return view

<<<<<<< HEAD

=======
>>>>>>> de733c415448a6db7eb45eb4a06a6462f48833b2
    async def intro_view(self, attributes: dict = None) -> Any:  # type: ignore[assignment, type-arg]
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
        self,
        attributes: dict[Any, Any] | None = None,
        attributes2: dict[Any, Any] | None = None,
    ) -> Any:
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
    async def on_ready(self) -> None:
        print("utils(Button Utils) is ready!")
        print("---------------------------")

    @commands.Cog.listener()
    async def on_button_click(self, interaction: Interaction) -> None:
        try:
            if interaction.user.bot or not interaction.message:
                return

            custom_id = interaction.data["custom_id"]  # type: ignore[index, typeddict-item]
            print(f"Button Clicked!\nCustom ID: {custom_id}")

            if custom_id.lower() in await RevomonTable().get_names():
                await interaction.response.defer()
                print(f"{interaction.user} clicked {custom_id.title()}")
                self.attributes = await get_attributes(revomon_name=custom_id.lower())
                view = await self.intro_view(attributes=self.attributes)
                embed = intro(self.attributes)
                await interaction.followup.send(embed=embed, view=view, ephemeral=True)
                print("Intro embed sent!")

            if "land " in custom_id.lower():
                raw_token_id = int(custom_id.split(" ")[1])
                await interaction.response.defer()
                print(f"{interaction.user} clicked {custom_id.title()}")
                land_obj = OwnedLandsTable()
                land_info = (await land_obj.get_info(token_id=raw_token_id))[0]
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
                if self.book_of_names is None:
                    self.book_of_names = await get_book_of_mon_names()  # type: ignore[assignment]
                self.current_page[interaction.user.id] -= 1
                if self.current_page[interaction.user.id] < 1:
                    self.current_page[interaction.user.id] = 1
                self.current_page[interaction.user.id] = len(self.book_of_names)  # type: ignore[arg-type]
                view = await self.mon_view(user_id=interaction.user.id)
                await interaction.followup.edit_message(
                    message_id=interaction.message.id,
                    view=view,
                )

            if custom_id == "previous_page":
                await interaction.response.defer()
                self.current_page[interaction.user.id] -= 1
                if self.current_page[interaction.user.id] < 1:
                    self.current_page[interaction.user.id] = 1
                view = await self.mon_view(user_id=interaction.user.id)
                await interaction.followup.edit_message(
                    message_id=interaction.message.id,
                    view=view,
                )

            if custom_id == "next_page":
                await interaction.response.defer()
                self.current_page[interaction.user.id] += 1
                if self.current_page[interaction.user.id] < 1:
                    self.current_page[interaction.user.id] = 1
                view = await self.mon_view(user_id=interaction.user.id)
                await interaction.followup.edit_message(
                    message_id=interaction.message.id,
                    view=view,
                )

            if custom_id == "first_page":
                await interaction.response.defer()
                self.current_page[interaction.user.id] = 1
                view = await self.mon_view(user_id=interaction.user.id)
                await interaction.followup.edit_message(
                    message_id=interaction.message.id,
                    view=view,
                )

            if custom_id == "last_page_land":
                await interaction.response.defer()
                user_id = interaction.user.id
                self.book_of_land_current_page[user_id] = len(self.book_of_land_ids)  # type: ignore[arg-type]
                if self.book_of_land_current_page[user_id] < 1:
                    self.book_of_land_current_page[user_id] = 1
                view = await self.land_view(user_id=user_id)
                await interaction.followup.edit_message(
                    message_id=interaction.message.id,
                    view=view,
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
                    message_id=interaction.message.id,
                    view=view,
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
                    message_id=interaction.message.id,
                    view=view,
                )

            if custom_id == "first_page_land":
                await interaction.response.defer()
                user_id = interaction.user.id
                self.book_of_land_current_page[user_id] = 1
                view = await self.land_view(user_id=user_id)
                await interaction.followup.edit_message(
                    message_id=interaction.message.id,
                    view=view,
                )


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


async def setup(gradex: commands.Bot) -> None:
    await gradex.add_cog(Buttons(gradex))
