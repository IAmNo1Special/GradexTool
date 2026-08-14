from typing import Any, cast

from discord import ButtonStyle, Interaction, SelectOption
from discord.ext import commands
from discord.ui import Button, Select, View

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

__all__ = [
    "get_book_of_land_ids",
    "get_book_of_mon_names",
    "Buttons",
    "IntroView",
    "CompareIntroView",
    "MonPaginationView",
    "LandPaginationView",
    "ShareButton",
]


class MonPaginationView(View):
    """View for paginated Revomon list with sorting."""

    def __init__(
        self,
        bot: commands.Bot,
        user_id: int,
        book_of_names: list[list[str]],
        current_page: int,
        group_by_evo: bool,
        app_emojis: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(timeout=None)
        self.bot = bot
        self.user_id = user_id
        self.book_of_names = book_of_names
        self.current_page = current_page
        self.group_by_evo = group_by_evo
        self.app_emojis = app_emojis or {}

        self._build_buttons()

    def _build_buttons(self) -> None:
        curr_page_content = self.book_of_names[self.current_page - 1]
        row = 0
        items_in_row = 0

        for name in curr_page_content:
            button = self._create_mon_button_sync(name, row)
            self.add_item(button)
            items_in_row += 1

            should_increment = items_in_row >= 5

            if should_increment:
                row += 1
                items_in_row = 0

        # Add pagination buttons in their own row
        pagination_row = row + 1
        self.add_item(FirstPageButton(row=pagination_row))
        self.add_item(PreviousPageButton(row=pagination_row))
        self.add_item(SearchSortButton(row=pagination_row))
        self.add_item(NextPageButton(row=pagination_row))
        self.add_item(LastPageButton(row=pagination_row))
        self.add_item(ShareButton(row=pagination_row + 1))

    def _create_mon_button_sync(self, name: str, row: int) -> Button[View]:
        """Create button using only the name and cached emoji info."""
        emoji_name = name.lower().replace(" ", "_").replace("-", "_")
        emoji_id = self.app_emojis.get(emoji_name)

        mon_emoji = f"<:{emoji_name}:{emoji_id}>" if emoji_id else None

        button: Button[View] = Button(
            label=f"{name.title()}",
            emoji=mon_emoji,
            style=ButtonStyle.gray,
            row=row,
            custom_id=f"mon:{name.lower()}",
        )
        return button


class LandPaginationView(View):
    """View for paginated land list with sorting."""

    def __init__(
        self,
        user_id: int,
        book_of_land_ids: list[list[int]],
        current_page: int,
    ) -> None:
        super().__init__(timeout=None)
        self.user_id = user_id
        self.book_of_land_ids = book_of_land_ids
        self.current_page = current_page

        self._build_buttons()

    def _build_buttons(self) -> None:
        curr_page_content = self.book_of_land_ids[self.current_page - 1]
        row = 0

        for token_id in curr_page_content:
            button = self._create_land_button_sync(token_id, row)
            self.add_item(button)

            if len(self.children) % 3 == 0 or token_id == self.book_of_land_ids[-1][-1]:
                row += 1

        # Add pagination buttons in their own row
        pagination_row = row + 1
        self.add_item(FirstPageLandButton(row=pagination_row))
        self.add_item(PreviousPageLandButton(row=pagination_row))
        self.add_item(SearchSortLandButton(row=pagination_row))
        self.add_item(NextPageLandButton(row=pagination_row))
        self.add_item(LastPageLandButton(row=pagination_row))

    def _create_land_button_sync(self, token_id: int, row: int) -> Button[View]:
        """Create land button using cached info if possible."""
        button: Button[View] = Button(
            label=f"Land {token_id}",
            style=ButtonStyle.gray,
            row=row,
            custom_id=f"land:{token_id}",
        )
        return button


class IntroView(View):
    """View for Revomon intro with action buttons."""

    def __init__(self, attributes: dict[str, Any]) -> None:
        super().__init__(timeout=None)
        self.attributes = attributes

        self.add_item(StatsButton())
        self.add_item(SpawnsButton())
        self.add_item(MovesButton())
        self.add_item(TypesButton())
        self.add_item(CounterdexButton())


class CompareIntroView(View):
    """View for comparing two Revomon."""

    def __init__(self, attributes: dict[str, Any], attributes2: dict[str, Any]) -> None:
        super().__init__(timeout=None)
        self.attributes = attributes
        self.attributes2 = attributes2

        self.add_item(CompareStatsButton())
        self.add_item(CompareSpawnsButton())
        self.add_item(CompareMovesButton())
        self.add_item(CompareTypesButton())
        self.add_item(CompareCounterdexsButton())


# Action Buttons - these read attributes from their parent view
class StatsButton(Button[View]):
    def __init__(self) -> None:
        super().__init__(
            label="Stats", style=ButtonStyle.green, custom_id="action:stats"
        )

    async def callback(self, interaction: Interaction) -> None:
        view = self.view
        if view is not None and hasattr(view, "attributes"):
            embed = stats(view.attributes)
            await interaction.response.send_message(embed=embed, ephemeral=True)


class CompareStatsButton(Button[View]):
    def __init__(self) -> None:
        super().__init__(
            label="Compare Stats",
            style=ButtonStyle.green,
            custom_id="action:compare_stats",
        )

    async def callback(self, interaction: Interaction) -> None:
        view = self.view
        if (
            view is not None
            and hasattr(view, "attributes")
            and hasattr(view, "attributes2")
        ):
            embed = compare_stats(view.attributes, view.attributes2)
            await interaction.response.send_message(embed=embed, ephemeral=True)


class SpawnsButton(Button[View]):
    def __init__(self) -> None:
        super().__init__(
            label="Spawns", style=ButtonStyle.green, custom_id="action:spawns"
        )

    async def callback(self, interaction: Interaction) -> None:
        view = self.view
        if view is not None and hasattr(view, "attributes"):
            embed = spawns(view.attributes)
            await interaction.response.send_message(embed=embed, ephemeral=True)


class CompareSpawnsButton(Button[View]):
    def __init__(self) -> None:
        super().__init__(
            label="Compare Spawns",
            style=ButtonStyle.green,
            custom_id="action:compare_spawns",
        )

    async def callback(self, interaction: Interaction) -> None:
        view = self.view
        if (
            view is not None
            and hasattr(view, "attributes")
            and hasattr(view, "attributes2")
        ):
            embed = compare_spawns(view.attributes, view.attributes2)
            await interaction.response.send_message(embed=embed, ephemeral=True)


class MovesButton(Button[View]):
    def __init__(self) -> None:
        super().__init__(
            label="Moves", style=ButtonStyle.green, custom_id="action:moves"
        )

    async def callback(self, interaction: Interaction) -> None:
        view = self.view
        if view is not None and hasattr(view, "attributes"):
            embed = moves(view.attributes)
            await interaction.response.send_message(embed=embed, ephemeral=True)


class CompareMovesButton(Button[View]):
    def __init__(self) -> None:
        super().__init__(
            label="Compare Moves",
            style=ButtonStyle.green,
            custom_id="action:compare_moves",
        )

    async def callback(self, interaction: Interaction) -> None:
        view = self.view
        if (
            view is not None
            and hasattr(view, "attributes")
            and hasattr(view, "attributes2")
        ):
            embed = compare_moves(view.attributes, view.attributes2)
            await interaction.response.send_message(embed=embed, ephemeral=True)


class TypesButton(Button[View]):
    def __init__(self) -> None:
        super().__init__(
            label="Types", style=ButtonStyle.green, custom_id="action:types"
        )

    async def callback(self, interaction: Interaction) -> None:
        view = self.view
        if view is not None and hasattr(view, "attributes"):
            embed = types(view.attributes)
            await interaction.response.send_message(embed=embed, ephemeral=True)


class CompareTypesButton(Button[View]):
    def __init__(self) -> None:
        super().__init__(
            label="Compare Types",
            style=ButtonStyle.green,
            custom_id="action:compare_types",
        )

    async def callback(self, interaction: Interaction) -> None:
        view = self.view
        if (
            view is not None
            and hasattr(view, "attributes")
            and hasattr(view, "attributes2")
        ):
            embed, embed2 = compare_types(view.attributes, view.attributes2)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            await interaction.followup.send(embed=embed2, ephemeral=True)


class CounterdexButton(Button[View]):
    def __init__(self) -> None:
        super().__init__(
            label="Counterdex", style=ButtonStyle.green, custom_id="action:counterdex"
        )

    async def callback(self, interaction: Interaction) -> None:
        view = self.view
        if view is not None and hasattr(view, "attributes"):
            embed = counterdex(view.attributes)
            await interaction.response.send_message(embed=embed, ephemeral=True)


class CompareCounterdexsButton(Button[View]):
    def __init__(self) -> None:
        super().__init__(
            label="Compare Counterdexs",
            style=ButtonStyle.green,
            custom_id="action:compare_counterdexs",
        )

    async def callback(self, interaction: Interaction) -> None:
        view = self.view
        if (
            view is not None
            and hasattr(view, "attributes")
            and hasattr(view, "attributes2")
        ):
            embed = compare_counterdexs(view.attributes, view.attributes2)
            await interaction.response.send_message(embed=embed, ephemeral=True)


# Pagination Buttons for Mon
class FirstPageButton(Button[View]):
    def __init__(self, row: int) -> None:
        super().__init__(
            emoji="\u23ee\ufe0f",
            style=ButtonStyle.green,
            row=row,
            custom_id="page:first",
        )

    async def callback(self, interaction: Interaction) -> None:
        await interaction.response.defer()


class PreviousPageButton(Button[View]):
    def __init__(self, row: int) -> None:
        super().__init__(
            emoji="\u23ea", style=ButtonStyle.green, row=row, custom_id="page:prev"
        )

    async def callback(self, interaction: Interaction) -> None:
        await interaction.response.defer()


class NextPageButton(Button[View]):
    def __init__(self, row: int) -> None:
        super().__init__(
            emoji="\u23e9", style=ButtonStyle.green, row=row, custom_id="page:next"
        )

    async def callback(self, interaction: Interaction) -> None:
        await interaction.response.defer()


class LastPageButton(Button[View]):
    def __init__(self, row: int) -> None:
        super().__init__(
            emoji="\u23ef\ufe0f",
            style=ButtonStyle.green,
            row=row,
            custom_id="page:last",
        )

    async def callback(self, interaction: Interaction) -> None:
        await interaction.response.defer()


class ShareButton(Button[View]):
    def __init__(self, row: int) -> None:
        super().__init__(
            emoji="\U0001f4e4",
            style=ButtonStyle.green,
            row=row,
            custom_id="mon:share",
        )

    async def callback(self, interaction: Interaction) -> None:
        view = self.view
        if view is not None and hasattr(view, "book_of_names"):
            mon_view = cast(MonPaginationView, view)
            new_view = MonPaginationView(
                bot=mon_view.bot,
                user_id=mon_view.user_id,
                book_of_names=mon_view.book_of_names,
                current_page=mon_view.current_page,
                group_by_evo=mon_view.group_by_evo,
                app_emojis=mon_view.app_emojis,
            )
            await interaction.response.defer()
            await interaction.followup.send(view=new_view, ephemeral=False)


# Pagination Buttons for Land
class FirstPageLandButton(Button[View]):
    def __init__(self, row: int) -> None:
        super().__init__(
            emoji="\u23ee\ufe0f",
            style=ButtonStyle.green,
            row=row,
            custom_id="land_page:first",
        )

    async def callback(self, interaction: Interaction) -> None:
        await interaction.response.defer()


class PreviousPageLandButton(Button[View]):
    def __init__(self, row: int) -> None:
        super().__init__(
            emoji="\u23ea", style=ButtonStyle.green, row=row, custom_id="land_page:prev"
        )

    async def callback(self, interaction: Interaction) -> None:
        await interaction.response.defer()


class NextPageLandButton(Button[View]):
    def __init__(self, row: int) -> None:
        super().__init__(
            emoji="\u23e9", style=ButtonStyle.green, row=row, custom_id="land_page:next"
        )

    async def callback(self, interaction: Interaction) -> None:
        await interaction.response.defer()


class LastPageLandButton(Button[View]):
    def __init__(self, row: int) -> None:
        super().__init__(
            emoji="\u23ef\ufe0f",
            style=ButtonStyle.green,
            row=row,
            custom_id="land_page:last",
        )

    async def callback(self, interaction: Interaction) -> None:
        await interaction.response.defer()


class SearchSortButton(Button[View]):
    """Button to open sort options for mon list."""

    def __init__(self, row: int) -> None:
        super().__init__(
            label="",
            emoji="\U0001f50d",
            style=ButtonStyle.secondary,
            custom_id="mon:search_sort",
            row=row,
        )

    async def callback(self, interaction: Interaction) -> None:
        sort_by_menu: Select[View] = Select(
            placeholder="Sort by...",
            custom_id="mon_sort_by_select",
            row=0,
            options=[
                SelectOption(
                    label="Dex #",
                    value="dex_id",
                    description="Sort by Pok\u00e9dex number",
                ),
                SelectOption(
                    label="Name", value="name", description="Sort alphabetically"
                ),
                SelectOption(
                    label="Type", value="type1", description="Sort by primary type"
                ),
                SelectOption(label="HP", value="hp", description="Sort by HP stat"),
                SelectOption(
                    label="ATK", value="atk", description="Sort by Attack stat"
                ),
                SelectOption(
                    label="DEF", value="def", description="Sort by Defense stat"
                ),
                SelectOption(
                    label="SPA", value="spa", description="Sort by Sp. Attack stat"
                ),
                SelectOption(
                    label="SPD", value="spd", description="Sort by Sp. Defense stat"
                ),
                SelectOption(
                    label="SPE", value="spe", description="Sort by Speed stat"
                ),
                SelectOption(
                    label="Rarity", value="rarity", description="Sort by rarity"
                ),
            ],
        )

        sort_order_menu: Select[View] = Select(
            placeholder="Sort order...",
            custom_id="mon_sort_order_select",
            row=1,
            options=[
                SelectOption(
                    label="Ascending",
                    value="asc",
                    emoji="\u2b06\ufe0f",
                    description="A \u2192 Z, lowest \u2192 highest",
                ),
                SelectOption(
                    label="Descending",
                    value="desc",
                    emoji="\u2b07\ufe0f",
                    description="Z \u2192 A, highest \u2192 lowest",
                ),
            ],
        )

        apply_button: Button[View] = Button(
            label="Apply Sort",
            emoji="\u2705",
            style=ButtonStyle.success,
            custom_id="apply_mon_sort",
            row=2,
        )

        cancel_button: Button[View] = Button(
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
            sorted_names = await RevomonTable().get_sorted_names(
                sort_by=sort_by_value, asc=asc
            )
            group_by_evo = sort_by_value == "dex_id"
            book_of_names = await get_book_of_mon_names(
                names=sorted_names, group_by_evo=group_by_evo
            )

            new_view = MonPaginationView(
                bot=cast(commands.Bot, apply_interaction.client),
                user_id=apply_interaction.user.id,
                book_of_names=book_of_names,
                current_page=1,
                group_by_evo=group_by_evo,
                app_emojis={},
            )
            await apply_interaction.response.edit_message(view=new_view)

        async def cancel_sort_callback(cancel_interaction: Interaction) -> None:
            await cancel_interaction.response.defer()

        cast(Any, sort_by_menu).callback = sort_by_callback
        cast(Any, sort_order_menu).callback = sort_order_callback
        cast(Any, apply_button).callback = apply_sort_callback
        cast(Any, cancel_button).callback = cancel_sort_callback

        await interaction.response.edit_message(view=sort_view)


class SearchSortLandButton(Button[View]):
    """Button to open sort options for land list."""

    def __init__(self, row: int) -> None:
        super().__init__(
            label="",
            emoji="\U0001f50d",
            style=ButtonStyle.secondary,
            custom_id="land:search_sort",
            row=row,
        )

    async def callback(self, interaction: Interaction) -> None:
        sort_by_menu: Select[View] = Select(
            placeholder="Sort by...",
            custom_id="land_sort_by_select",
            row=0,
            options=[
                SelectOption(label="Biome", value="biome", description="Sort by biome"),
                SelectOption(
                    label="Land Type",
                    value="land_type",
                    description="Sort by land type",
                ),
                SelectOption(
                    label="Rarity", value="rarity", description="Sort by rarity"
                ),
                SelectOption(
                    label="Price", value="for_sale_usd", description="Sort by price"
                ),
                SelectOption(label="Size", value="size", description="Sort by size"),
                SelectOption(
                    label="Owner's Address",
                    value="owners_address",
                    description="Sort by owner",
                ),
            ],
        )

        sort_order_menu: Select[View] = Select(
            placeholder="Sort order...",
            custom_id="land_sort_order_select",
            row=1,
            options=[
                SelectOption(
                    label="Ascending",
                    value="asc",
                    emoji="\u2b06\ufe0f",
                    description="A \u2192 Z, lowest \u2192 highest",
                ),
                SelectOption(
                    label="Descending",
                    value="desc",
                    emoji="\u2b07\ufe0f",
                    description="Z \u2192 A, highest \u2192 lowest",
                ),
            ],
        )

        apply_button: Button[View] = Button(
            label="Apply Sort",
            emoji="\u2705",
            style=ButtonStyle.success,
            custom_id="apply_land_sort",
            row=2,
        )

        cancel_button: Button[View] = Button(
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
            sort_by_value = (
                sort_by_menu.values[0] if sort_by_menu.values else "token_id"
            )
            asc = True
            if sort_order_menu.values:
                asc = sort_order_menu.values[0] == "asc"
            sorted_lands = await OwnedLandsTable().get_info(
                sort_by=sort_by_value, asc=asc
            )
            if sorted_lands:
                sorted_token_ids = [land[0] for land in sorted_lands]
                book_of_land_ids = await get_book_of_land_ids(
                    token_ids=sorted_token_ids
                )

                new_view = LandPaginationView(
                    user_id=apply_interaction.user.id,
                    book_of_land_ids=book_of_land_ids,
                    current_page=1,
                )
                await apply_interaction.response.edit_message(view=new_view)

        async def cancel_sort_callback(cancel_interaction: Interaction) -> None:
            await cancel_interaction.response.defer()

        cast(Any, sort_by_menu).callback = sort_by_callback
        cast(Any, sort_order_menu).callback = sort_order_callback
        cast(Any, apply_button).callback = apply_sort_callback
        cast(Any, cancel_button).callback = cancel_sort_callback

        await interaction.response.edit_message(view=sort_view)


class Buttons(commands.Cog):
    def __init__(self, gradex: commands.Bot) -> None:
        self.gradex = gradex
        self.app_emojis: dict[str, Any] | None = None
        self.book_of_names: list[list[str]] | None = None
        self.current_page: dict[int, int] = {}
        self.attributes: dict[str, Any] = {}
        self.attributes2: dict[str, Any] = {}
        self.book_of_land_ids: list[list[int]] | None = None
        self.book_of_land_current_page: dict[int, int] = {}
        self.land_attributes: dict[str, Any] = {}

    async def mon_button(self, name: str, row: int) -> Button[View]:
        """Create a mon button with info from database."""
        revomon_table = globals()["RevomonTable"]
        info = await revomon_table().get_info(name)
        dex_num = info[0][0] if info else 0

        button: Button[View] = Button(
            label=f"{dex_num}. {name.title()}",
            style=ButtonStyle.gray,
            row=row,
            custom_id=name,
        )
        cast(Any, button).callback = self.on_button_click
        return button

    async def land_button(self, token_id: int, row: int) -> Button[View]:
        """Create a land button with info from database."""
        owned_lands_table = globals()["OwnedLandsTable"]
        land_obj = owned_lands_table()
        land_info = (await land_obj.get_info(token_id=token_id))[0]

        button: Button[View] = Button(
            label=f"{token_id}. {land_info[4].title()} · {land_info[3].title()} (${land_info[11]})",
            style=ButtonStyle.gray,
            row=row,
            custom_id=f"land {token_id}",
        )
        cast(Any, button).callback = self.on_button_click
        return button

    async def stats_button(self) -> Button[View]:
        button: Button[View] = Button(
            label="Stats", style=ButtonStyle.green, custom_id="stats"
        )
        cast(Any, button).callback = self.on_button_click
        return button

    async def compare_stats_button(self) -> Button[View]:
        button: Button[View] = Button(
            label="Compare Stats", style=ButtonStyle.green, custom_id="compare_stats"
        )
        cast(Any, button).callback = self.on_button_click
        return button

    async def spawns_button(self) -> Button[View]:
        button: Button[View] = Button(
            label="Spawns", style=ButtonStyle.green, custom_id="spawns"
        )
        cast(Any, button).callback = self.on_button_click
        return button

    async def compare_spawns_button(self) -> Button[View]:
        button: Button[View] = Button(
            label="Compare Spawns", style=ButtonStyle.green, custom_id="compare_Spawns"
        )
        cast(Any, button).callback = self.on_button_click
        return button

    async def moves_button(self) -> Button[View]:
        button: Button[View] = Button(
            label="Moves", style=ButtonStyle.green, custom_id="moves"
        )
        cast(Any, button).callback = self.on_button_click
        return button

    async def compare_moves_button(self) -> Button[View]:
        button: Button[View] = Button(
            label="Compare Moves",
            style=ButtonStyle.green,
            custom_id="compare_move_list",
        )
        cast(Any, button).callback = self.on_button_click
        return button

    async def types_button(self) -> Button[View]:
        button: Button[View] = Button(
            label="Types", style=ButtonStyle.green, custom_id="types"
        )
        cast(Any, button).callback = self.on_button_click
        return button

    async def compare_types_button(self) -> Button[View]:
        button: Button[View] = Button(
            label="Compare Types", style=ButtonStyle.green, custom_id="compare_types"
        )
        cast(Any, button).callback = self.on_button_click
        return button

    async def counterdex_button(self) -> Button[View]:
        button: Button[View] = Button(
            label="Counterdex", style=ButtonStyle.green, custom_id="counterdex"
        )
        cast(Any, button).callback = self.on_button_click
        return button

    async def compare_counterdexs_button(self) -> Button[View]:
        button: Button[View] = Button(
            label="Compare Counterdexs",
            style=ButtonStyle.green,
            custom_id="compare_counterdexs",
        )
        cast(Any, button).callback = self.on_button_click
        return button

    def first_page_button(self, row: int) -> Button[View]:
        button: Button[View] = Button(
            emoji="\u23ee\ufe0f",
            style=ButtonStyle.green,
            row=row,
            custom_id="first_page",
        )
        cast(Any, button).callback = self.on_button_click
        return button

    def previous_button(self, row: int) -> Button[View]:
        button: Button[View] = Button(
            emoji="\u23ea", style=ButtonStyle.green, row=row, custom_id="previous_page"
        )
        cast(Any, button).callback = self.on_button_click
        return button

    def next_button(self, row: int) -> Button[View]:
        button: Button[View] = Button(
            emoji="\u23e9", style=ButtonStyle.green, row=row, custom_id="next_page"
        )
        cast(Any, button).callback = self.on_button_click
        return button

    def last_page_button(self, row: int) -> Button[View]:
        button: Button[View] = Button(
            emoji="\u23ed\ufe0f",
            style=ButtonStyle.green,
            row=row,
            custom_id="last_page",
        )
        cast(Any, button).callback = self.on_button_click
        return button

    def first_page_button_land(self, row: int) -> Button[View]:
        button: Button[View] = Button(
            emoji="\u23ee\ufe0f",
            style=ButtonStyle.green,
            row=row,
            custom_id="first_page_land",
        )
        cast(Any, button).callback = self.on_button_click
        return button

    def previous_button_land(self, row: int) -> Button[View]:
        button: Button[View] = Button(
            emoji="\u23ea",
            style=ButtonStyle.green,
            row=row,
            custom_id="previous_page_land",
        )
        cast(Any, button).callback = self.on_button_click
        return button

    def next_button_land(self, row: int) -> Button[View]:
        button: Button[View] = Button(
            emoji="\u23e9", style=ButtonStyle.green, row=row, custom_id="next_page_land"
        )
        cast(Any, button).callback = self.on_button_click
        return button

    def last_page_button_land(self, row: int) -> Button[View]:
        button: Button[View] = Button(
            emoji="\u23ed\ufe0f",
            style=ButtonStyle.green,
            row=row,
            custom_id="last_page_land",
        )
        cast(Any, button).callback = self.on_button_click
        return button

    async def exit_button(self, row: int) -> Button[View]:
        button: Button[View] = Button(
            emoji="\u274c", style=ButtonStyle.red, row=row, custom_id="exit"
        )
        cast(Any, button).callback = self.on_button_click
        return button

    async def search_button_land(self, row: int) -> Button[View]:
        button: Button[View] = Button(
            emoji="\U0001f50e",
            style=ButtonStyle.green,
            row=row,
            custom_id="search_land",
        )
        cast(Any, button).callback = self.on_button_click
        return button

    async def filter_button_land(self, row: int) -> Button[View]:
        button: Button[View] = Button(
            emoji="filter", style=ButtonStyle.green, row=row, custom_id="filter_land"
        )
        cast(Any, button).callback = self.on_button_click
        return button

    async def sort_by_button_land(self, row: int) -> Button[View]:
        button: Button[View] = Button(
            emoji="sortby", style=ButtonStyle.green, row=row, custom_id="sort_by_land"
        )
        cast(Any, button).callback = self.on_button_click
        return button

    async def search_settings_button_land(self, row: int) -> Button[View]:
        button: Button[View] = Button(
            emoji="\u2699\ufe0f",
            style=ButtonStyle.green,
            row=row,
            custom_id="search_settings_land",
        )
        cast(Any, button).callback = self.on_button_click
        return button

    async def mon_view(self, user_id: int) -> View:
        if self.book_of_names is None:
            self.book_of_names = await get_book_of_mon_names()

        self.current_page[user_id] = self.current_page.get(user_id, 1)
        page = self.current_page[user_id]

        view = MonPaginationView(
            bot=self.gradex,
            user_id=user_id,
            book_of_names=self.book_of_names,
            current_page=page,
            group_by_evo=True,
            app_emojis=self.app_emojis or {},
        )
        return view

    async def land_view(self, user_id: int, token_ids: list[int] | None = None) -> View:
        if token_ids is not None:
            self.book_of_land_ids = await get_book_of_land_ids(token_ids=token_ids)
        elif self.book_of_land_ids is None:
            self.book_of_land_ids = await get_book_of_land_ids()

        self.book_of_land_current_page[user_id] = self.book_of_land_current_page.get(
            user_id, 1
        )
        page = self.book_of_land_current_page[user_id]

        view = LandPaginationView(
            user_id=user_id,
            book_of_land_ids=self.book_of_land_ids,
            current_page=page,
        )
        return view

    async def intro_view(self, attributes: dict[str, Any]) -> View:
        self.attributes = attributes
        view = IntroView(attributes)
        return view

    async def compare_intros_view(
        self, attributes: dict[str, Any], attributes2: dict[str, Any]
    ) -> View:
        self.attributes = attributes
        self.attributes2 = attributes2
        view = CompareIntroView(attributes, attributes2)
        return view

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        print("utils(Button Utils) is ready!")
        print("---------------------------")

    @commands.Cog.listener()
    async def on_button_click(self, interaction: Interaction) -> None:
        try:
            if interaction.user.bot or not interaction.message:
                return

            raw_data = interaction.data
            custom_id: str = (
                str(cast(dict[str, Any], raw_data).get("custom_id", ""))
                if raw_data
                else ""
            )
            print(f"Button Clicked!\nCustom ID: {custom_id}")

            # Handle mon buttons (format: mon:name or just name)
            if custom_id.startswith("mon:") or custom_id in ("mon1", "mon2", "mon3"):
                name = custom_id[4:] if custom_id.startswith("mon:") else custom_id
                await interaction.response.defer()
                print(f"{interaction.user} clicked {name.title()}")

                attributes = await get_attributes(revomon_name=name.lower())

                # Load and cache application emojis
                if self.app_emojis is None:
                    from utils.emoji_utils import list_application_emojis

                    try:
                        emojis = await list_application_emojis()
                        self.app_emojis = {e["name"]: e["id"] for e in emojis}
                    except Exception as e:
                        print(f"Failed to fetch application emojis: {e}")
                        self.app_emojis = {}

                book_of_names = await get_book_of_mon_names()
                _ = MonPaginationView(
                    bot=self.gradex,
                    user_id=interaction.user.id,
                    book_of_names=book_of_names,
                    current_page=1,
                    group_by_evo=True,
                    app_emojis=self.app_emojis,
                )

                # Show intro first
                intro_view = IntroView(attributes)
                embed = intro(attributes)
                await interaction.followup.send(
                    embed=embed, view=intro_view, ephemeral=True
                )
                print("Intro embed sent!")

            # Handle land buttons (format: land:token_id or "land N")
            elif custom_id.startswith("land:") or custom_id.startswith("land "):
                if custom_id.startswith("land:"):
                    raw_token_id = int(custom_id[5:])
                else:
                    raw_token_id = int(custom_id.split()[1])
                await interaction.response.defer()
                print(f"{interaction.user} clicked land {raw_token_id}")

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

                embed = land_intro(attributes=land_dict)
                await interaction.followup.send(embed=embed, ephemeral=True)
                print("Land Intro embed sent!")

            # Handle pagination buttons (mon)
            elif custom_id in ("first_page", "previous_page", "next_page", "last_page"):
                await interaction.response.defer()

                # Update current page
                user_id = interaction.user.id
                if custom_id == "first_page":
                    self.current_page[user_id] = 1
                elif custom_id == "previous_page":
                    self.current_page[user_id] = max(
                        1, self.current_page.get(user_id, 1) - 1
                    )
                elif custom_id == "next_page":
                    self.current_page[user_id] = self.current_page.get(user_id, 1) + 1
                elif custom_id == "last_page":
                    self.current_page[user_id] = (
                        len(self.book_of_names) if self.book_of_names else 1
                    )

                # Create new view using the mon_view method (can be mocked in tests)
                if self.book_of_names is not None:
                    new_view = await self.mon_view(user_id)
                    await interaction.followup.edit_message(
                        message_id=interaction.message.id, view=new_view
                    )

            # Handle pagination buttons (land)
            elif custom_id in (
                "first_page_land",
                "previous_page_land",
                "next_page_land",
                "last_page_land",
            ):
                await interaction.response.defer()

                user_id = interaction.user.id
                if custom_id == "first_page_land":
                    self.book_of_land_current_page[user_id] = 1
                elif custom_id == "previous_page_land":
                    self.book_of_land_current_page[user_id] = max(
                        1, self.book_of_land_current_page.get(user_id, 1) - 1
                    )
                elif custom_id == "next_page_land":
                    self.book_of_land_current_page[user_id] = (
                        self.book_of_land_current_page.get(user_id, 1) + 1
                    )
                elif custom_id == "last_page_land":
                    self.book_of_land_current_page[user_id] = (
                        len(self.book_of_land_ids) if self.book_of_land_ids else 1
                    )

                if self.book_of_land_ids is not None:
                    new_view = await self.land_view(user_id)
                    await interaction.followup.edit_message(
                        message_id=interaction.message.id, view=new_view
                    )

            # Handle land action buttons
            elif custom_id in (
                "exit",
                "search_land",
                "filter_land",
                "sort_by_land",
                "search_settings_land",
            ):
                await interaction.response.defer()

                if custom_id == "search_settings_land":
                    from data import RevomonTable

                    revomon_table = RevomonTable()
                    await revomon_table.get_names()
                    await interaction.followup.send(
                        "Search settings opened", ephemeral=True
                    )

            # Handle info action buttons
            elif custom_id in (
                "stats",
                "compare_stats",
                "spawns",
                "compare_spawns",
                "moves",
                "compare_moves",
                "types",
                "counterdex",
                "compare_counterdexs",
                "compare_types",
            ):
                await interaction.response.defer()

                # Get attributes from the view
                view = getattr(interaction.message, "view", None)
                if view and hasattr(view, "attributes"):
                    attributes = view.attributes
                    if custom_id == "stats":
                        embed = stats(attributes)
                    elif custom_id == "compare_stats":
                        attributes2 = getattr(view, "attributes2", {})
                        embed = compare_stats(attributes, attributes2)
                    elif custom_id == "spawns":
                        embed = spawns(attributes)
                    elif custom_id == "compare_spawns":
                        attributes2 = getattr(view, "attributes2", {})
                        embed = compare_spawns(attributes, attributes2)
                    elif custom_id == "moves":
                        embed = moves(attributes)
                    elif custom_id == "compare_moves":
                        attributes2 = getattr(view, "attributes2", {})
                        embed = compare_moves(attributes, attributes2)
                    elif custom_id == "types":
                        embed = types(attributes)
                    elif custom_id == "counterdex":
                        embed = counterdex(attributes)
                    elif custom_id == "compare_counterdexs":
                        attributes2 = getattr(view, "attributes2", {})
                        embed = compare_counterdexs(attributes, attributes2)
                    elif custom_id == "compare_types":
                        attributes2 = getattr(view, "attributes2", {})
                        embed1, embed2 = compare_types(attributes, attributes2)
                        await interaction.followup.send(embed=embed1, ephemeral=True)
                        await interaction.followup.send(embed=embed2, ephemeral=True)
                        return

                    if "embed" in locals():
                        await interaction.followup.send(embed=embed, ephemeral=True)

            # Handle search/sort for mons
            elif custom_id == "mon:search_sort":
                pass  # Handled in SearchSortButton.callback

            elif custom_id == "apply_mon_sort":
                pass  # Handled in apply_sort_callback

            elif custom_id == "cancel_mon_sort":
                pass  # Handled in cancel_sort_callback

            # Handle search/sort for lands
            elif custom_id == "land:search_sort":
                pass  # Handled in SearchSortLandButton.callback

            elif custom_id == "apply_land_sort":
                pass  # Handled in apply_sort_callback

            elif custom_id == "cancel_land_sort":
                pass  # Handled in cancel_sort_callback

            # Handle action buttons (these read attributes from their parent view)
            elif custom_id.startswith("action:"):
                _ = custom_id[7:]
                await interaction.response.defer()

        except Exception as e:
            print(f"Error: {e}")


async def setup(gradex: commands.Bot) -> None:
    await gradex.add_cog(Buttons(gradex))
