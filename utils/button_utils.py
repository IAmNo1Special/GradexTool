import logging
from collections.abc import Callable
from typing import Any, cast

import discord
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
from utils.emoji_utils import list_application_emojis
from utils.revomon_utils import (
    get_attributes,
    get_book_of_land_ids,
    get_book_of_mon_names,
)

logger = logging.getLogger(__name__)

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
        self.total_pages = max(1, len(book_of_names))
        self.group_by_evo = group_by_evo
        self.app_emojis = app_emojis or {}

        self._build_buttons()

    def _build_buttons(self) -> None:
        if not self.book_of_names:
            return  # Empty book: no mon buttons, pagers render disabled
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

        # Add pagination buttons in their own row, capped to avoid exceeding Discord's 5-row limit
        pagination_row = min(row + 1, 3)
        self.add_item(FirstPageButton(row=pagination_row, total_pages=self.total_pages))
        self.add_item(
            PreviousPageButton(row=pagination_row, current_page=self.current_page)
        )
        self.add_item(SearchSortButton(row=pagination_row))
        self.add_item(
            NextPageButton(
                row=pagination_row,
                current_page=self.current_page,
                total_pages=self.total_pages,
            )
        )
        self.add_item(LastPageButton(row=pagination_row, total_pages=self.total_pages))
        self.add_item(ShareButton(row=min(pagination_row + 1, 4)))

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
        self.total_pages = max(1, len(book_of_land_ids))

        self._build_buttons()

    def _build_buttons(self) -> None:
        if not self.book_of_land_ids:
            return  # Empty book: no land buttons, pagers render disabled
        curr_page_content = self.book_of_land_ids[self.current_page - 1]
        row = 0

        for token_id in curr_page_content:
            button = self._create_land_button_sync(token_id, row)
            self.add_item(button)

            if len(self.children) % 3 == 0 or token_id == self.book_of_land_ids[-1][-1]:
                row += 1

        # Add pagination buttons in their own row (capped to avoid exceeding Discord's 5-row limit)
        pagination_row = min(row + 1, 4)
        total_pages = max(1, len(self.book_of_land_ids))
        self.add_item(FirstPageLandButton(row=pagination_row, total_pages=total_pages))
        self.add_item(
            PreviousPageLandButton(row=pagination_row, current_page=self.current_page)
        )
        self.add_item(SearchSortLandButton(row=pagination_row))
        self.add_item(
            NextPageLandButton(
                row=pagination_row,
                current_page=self.current_page,
                total_pages=total_pages,
            )
        )
        self.add_item(LastPageLandButton(row=pagination_row, total_pages=total_pages))

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
    """View for Revomon intro with restart-safe action buttons.

    Buttons encode the mon name in their custom_id; the Buttons cog's
    on_interaction router rebuilds attributes from SQLite at click time,
    so the buttons keep working after bot restarts.
    """

    def __init__(self, attributes: dict[str, Any]) -> None:
        super().__init__(timeout=None)
        self.attributes = attributes
        name_raw = attributes.get("name") if isinstance(attributes, dict) else None
        self.mon_name = str(name_raw or "unknown").lower()

        self.add_item(StatsButton(self.mon_name))
        self.add_item(SpawnsButton(self.mon_name))
        self.add_item(MovesButton(self.mon_name))
        self.add_item(TypesButton(self.mon_name))
        self.add_item(CounterdexButton(self.mon_name))


class CompareIntroView(View):
    """Compare variant of IntroView; both mon names ride in the custom_id."""

    def __init__(self, attributes: dict[str, Any], attributes2: dict[str, Any]) -> None:
        super().__init__(timeout=None)
        self.attributes = attributes
        self.attributes2 = attributes2

        def _name(attrs: Any) -> str:
            raw = attrs.get("name") if isinstance(attrs, dict) else None
            return str(raw or "unknown").lower()

        name1 = _name(attributes)
        name2 = _name(attributes2)

        self.add_item(CompareStatsButton(name1, name2))
        self.add_item(CompareSpawnsButton(name1, name2))
        self.add_item(CompareMovesButton(name1, name2))
        self.add_item(CompareTypesButton(name1, name2))
        self.add_item(CompareCounterdexsButton(name1, name2))


# Action Buttons - stateless: payload rides in the custom_id and the
# Buttons cog's on_interaction router serves every click, restart-proof.
def _action_custom_id(verb: str, *names: str) -> str:
    return f"action:{verb}:" + "&".join(names)


class StatsButton(Button[View]):
    def __init__(self, mon_name: str) -> None:
        super().__init__(
            label="Stats",
            style=ButtonStyle.green,
            custom_id=_action_custom_id("stats", mon_name.lower()),
        )

    async def callback(self, interaction: Interaction) -> None:
        return None  # Handled by the Buttons cog's on_interaction router


class CompareStatsButton(Button[View]):
    def __init__(self, mon_name: str, other_mon_name: str) -> None:
        super().__init__(
            label="Compare Stats",
            style=ButtonStyle.green,
            custom_id=_action_custom_id(
                "compare_stats", mon_name.lower(), other_mon_name.lower()
            ),
        )

    async def callback(self, interaction: Interaction) -> None:
        return None  # Handled by the Buttons cog's on_interaction router


class SpawnsButton(Button[View]):
    def __init__(self, mon_name: str) -> None:
        super().__init__(
            label="Spawns",
            style=ButtonStyle.green,
            custom_id=_action_custom_id("spawns", mon_name.lower()),
        )

    async def callback(self, interaction: Interaction) -> None:
        return None  # Handled by the Buttons cog's on_interaction router


class CompareSpawnsButton(Button[View]):
    def __init__(self, mon_name: str, other_mon_name: str) -> None:
        super().__init__(
            label="Compare Spawns",
            style=ButtonStyle.green,
            custom_id=_action_custom_id(
                "compare_spawns", mon_name.lower(), other_mon_name.lower()
            ),
        )

    async def callback(self, interaction: Interaction) -> None:
        return None  # Handled by the Buttons cog's on_interaction router


class MovesButton(Button[View]):
    def __init__(self, mon_name: str) -> None:
        super().__init__(
            label="Moves",
            style=ButtonStyle.green,
            custom_id=_action_custom_id("moves", mon_name.lower()),
        )

    async def callback(self, interaction: Interaction) -> None:
        return None  # Handled by the Buttons cog's on_interaction router


class CompareMovesButton(Button[View]):
    def __init__(self, mon_name: str, other_mon_name: str) -> None:
        super().__init__(
            label="Compare Moves",
            style=ButtonStyle.green,
            custom_id=_action_custom_id(
                "compare_moves", mon_name.lower(), other_mon_name.lower()
            ),
        )

    async def callback(self, interaction: Interaction) -> None:
        return None  # Handled by the Buttons cog's on_interaction router


class TypesButton(Button[View]):
    def __init__(self, mon_name: str) -> None:
        super().__init__(
            label="Types",
            style=ButtonStyle.green,
            custom_id=_action_custom_id("types", mon_name.lower()),
        )

    async def callback(self, interaction: Interaction) -> None:
        return None  # Handled by the Buttons cog's on_interaction router


class CompareTypesButton(Button[View]):
    def __init__(self, mon_name: str, other_mon_name: str) -> None:
        super().__init__(
            label="Compare Types",
            style=ButtonStyle.green,
            custom_id=_action_custom_id(
                "compare_types", mon_name.lower(), other_mon_name.lower()
            ),
        )

    async def callback(self, interaction: Interaction) -> None:
        return None  # Handled by the Buttons cog's on_interaction router


class CounterdexButton(Button[View]):
    def __init__(self, mon_name: str) -> None:
        super().__init__(
            label="Counterdex",
            style=ButtonStyle.green,
            custom_id=_action_custom_id("counterdex", mon_name.lower()),
        )

    async def callback(self, interaction: Interaction) -> None:
        return None  # Handled by the Buttons cog's on_interaction router


class CompareCounterdexsButton(Button[View]):
    def __init__(self, mon_name: str, other_mon_name: str) -> None:
        super().__init__(
            label="Compare Counterdexs",
            style=ButtonStyle.green,
            custom_id=_action_custom_id(
                "compare_counterdexs", mon_name.lower(), other_mon_name.lower()
            ),
        )

    async def callback(self, interaction: Interaction) -> None:
        return None  # Handled by the Buttons cog's on_interaction router


# Pagination Buttons for Mon — target page encoded in custom_id so the
# Buttons-cog router can serve clicks statelessly, even after restarts.
class FirstPageButton(Button[View]):
    def __init__(self, row: int, total_pages: int = 1) -> None:
        super().__init__(
            emoji="\u23ee\ufe0f",
            style=ButtonStyle.green,
            row=row,
            custom_id="mon_page:goto:1",
            disabled=total_pages <= 1,
        )

    async def callback(self, interaction: Interaction) -> None:
        return None  # Handled by the Buttons cog's on_interaction router


class PreviousPageButton(Button[View]):
    def __init__(self, row: int, current_page: int = 1) -> None:
        super().__init__(
            emoji="\u23ea",
            style=ButtonStyle.green,
            row=row,
            custom_id=f"mon_page:goto:{max(1, current_page - 1)}",
            disabled=current_page <= 1,
        )

    async def callback(self, interaction: Interaction) -> None:
        return None  # Handled by the Buttons cog's on_interaction router


class NextPageButton(Button[View]):
    def __init__(self, row: int, current_page: int = 1, total_pages: int = 1) -> None:
        super().__init__(
            emoji="\u23e9",
            style=ButtonStyle.green,
            row=row,
            custom_id=f"mon_page:goto:{min(total_pages, current_page + 1)}",
            disabled=current_page >= total_pages,
        )

    async def callback(self, interaction: Interaction) -> None:
        return None  # Handled by the Buttons cog's on_interaction router


class LastPageButton(Button[View]):
    def __init__(self, row: int, total_pages: int = 1) -> None:
        super().__init__(
            emoji="\u23ef\ufe0f",
            style=ButtonStyle.green,
            row=row,
            custom_id=f"mon_page:goto:{max(1, total_pages)}",
            disabled=total_pages <= 1,
        )

    async def callback(self, interaction: Interaction) -> None:
        return None  # Handled by the Buttons cog's on_interaction router


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
            try:
                await interaction.response.defer()
                await interaction.followup.send(view=new_view, ephemeral=False)
            except (discord.HTTPException, discord.Forbidden) as e:
                print(f"ShareButton callback error: {e}")


# Pagination Buttons for Land — target page encoded in custom_id.
class FirstPageLandButton(Button[View]):
    def __init__(self, row: int, total_pages: int = 1) -> None:
        super().__init__(
            emoji="\u23ee\ufe0f",
            style=ButtonStyle.green,
            row=row,
            custom_id="land_page:goto:1",
            disabled=total_pages <= 1,
        )

    async def callback(self, interaction: Interaction) -> None:
        return None  # Handled by the Buttons cog's on_interaction router


class PreviousPageLandButton(Button[View]):
    def __init__(self, row: int, current_page: int = 1) -> None:
        super().__init__(
            emoji="\u23ea",
            style=ButtonStyle.green,
            row=row,
            custom_id=f"land_page:goto:{max(1, current_page - 1)}",
            disabled=current_page <= 1,
        )

    async def callback(self, interaction: Interaction) -> None:
        return None  # Handled by the Buttons cog's on_interaction router


class NextPageLandButton(Button[View]):
    def __init__(self, row: int, current_page: int = 1, total_pages: int = 1) -> None:
        super().__init__(
            emoji="\u23e9",
            style=ButtonStyle.green,
            row=row,
            custom_id=f"land_page:goto:{min(total_pages, current_page + 1)}",
            disabled=current_page >= total_pages,
        )

    async def callback(self, interaction: Interaction) -> None:
        return None  # Handled by the Buttons cog's on_interaction router


class LastPageLandButton(Button[View]):
    def __init__(self, row: int, total_pages: int = 1) -> None:
        super().__init__(
            emoji="\u23ef\ufe0f",
            style=ButtonStyle.green,
            row=row,
            custom_id=f"land_page:goto:{max(1, total_pages)}",
            disabled=total_pages <= 1,
        )

    async def callback(self, interaction: Interaction) -> None:
        return None  # Handled by the Buttons cog's on_interaction router


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
    """Router for stateless mon/land browse buttons.

    All pagination state is encoded in custom_ids (``mon_page:goto:<n>`` /
    ``land_page:goto:<n>``), so clicks keep working after bot restarts.
    """

    # Legacy page-less pager ids emitted by pre-router views; their page state
    # is unrecoverable, so clicks get an expiry notice instead of silence.
    _LEGACY_PAGERS = frozenset(
        {
            "first_page",
            "previous_page",
            "next_page",
            "last_page",
            "first_page_land",
            "previous_page_land",
            "next_page_land",
            "last_page_land",
            "page:first",
            "page:prev",
            "page:next",
            "page:last",
            "land_page:first",
            "land_page:prev",
            "land_page:next",
            "land_page:last",
        }
    )
    _MON_ALIASES = frozenset({"mon1", "mon2", "mon3"})
    _ACTION_VERBS = frozenset(
        {
            "stats",
            "spawns",
            "moves",
            "types",
            "counterdex",
            "compare_stats",
            "compare_spawns",
            "compare_moves",
            "compare_types",
            "compare_counterdexs",
        }
    )

    def __init__(self, gradex: commands.Bot) -> None:
        self.gradex = gradex
        self.app_emojis: dict[str, Any] | None = None
        self.book_of_names: list[list[str]] | None = None
        self.book_of_land_ids: list[list[int]] | None = None

    async def _load_app_emojis(self) -> dict[str, Any]:
        if self.app_emojis is None:
            try:
                emojis = await list_application_emojis()
                self.app_emojis = {e["name"]: e["id"] for e in emojis}
            except Exception as e:
                logger.debug(f"Failed to fetch application emojis: {e}")
                self.app_emojis = {}
        return self.app_emojis

    async def mon_view(self, user_id: int, page: int = 1) -> View:
        if self.book_of_names is None:
            self.book_of_names = await get_book_of_mon_names()
        book = self.book_of_names or []
        total_pages = max(1, len(book))
        page = max(1, min(page, total_pages))
        return MonPaginationView(
            bot=self.gradex,
            user_id=user_id,
            book_of_names=book,
            current_page=page,
            group_by_evo=True,
            app_emojis=await self._load_app_emojis(),
        )

    async def land_view(
        self, user_id: int, token_ids: list[int] | None = None, page: int = 1
    ) -> View:
        if token_ids is not None:
            self.book_of_land_ids = await get_book_of_land_ids(token_ids=token_ids)
        elif self.book_of_land_ids is None:
            self.book_of_land_ids = await get_book_of_land_ids()
        book = self.book_of_land_ids or []
        total_pages = max(1, len(book))
        page = max(1, min(page, total_pages))
        return LandPaginationView(
            user_id=user_id,
            book_of_land_ids=book,
            current_page=page,
        )

    async def intro_view(self, attributes: dict[str, Any]) -> View:
        return IntroView(attributes)

    async def compare_intros_view(
        self, attributes: dict[str, Any], attributes2: dict[str, Any]
    ) -> View:
        return CompareIntroView(attributes, attributes2)

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        print("utils(Button Utils) is ready!")
        print("---------------------------")

    # -- component-interaction router ----------------------------------

    @staticmethod
    def _extract_custom_id(interaction: Interaction) -> str | None:
        if interaction.type is not discord.InteractionType.component:
            return None
        data = interaction.data
        if not isinstance(data, dict):
            return None
        custom_id = data.get("custom_id")
        return custom_id if isinstance(custom_id, str) else None

    @staticmethod
    async def _send_expiry_notice(interaction: Interaction) -> None:
        await interaction.response.send_message(
            "This pager has expired - run /search again.", ephemeral=True
        )

    async def _handle_action(self, interaction: Interaction, custom_id: str) -> None:
        """Serve IntroView action buttons by rebuilding attributes from SQLite.

        custom_id format: ``action:<verb>:<mon>`` or
        ``action:compare_<verb>:<mon_a>&<mon_b>``. Bare pre-router ids
        (no payload) carried per-instance state and get the expiry notice.
        """
        rest = custom_id[len("action:") :]
        verb, _, payload = rest.partition(":")
        verb = verb.strip()

        if not payload:
            await self._send_expiry_notice(interaction)
            return

        names = [n for n in payload.split("&") if n]
        is_compare = verb.startswith("compare_")
        expected_names = 2 if is_compare else 1

        if verb not in self._ACTION_VERBS or len(names) != expected_names:
            logger.debug(f"[Buttons] bad action id {custom_id!r}")
            return

        await interaction.response.defer()

        attributes = await get_attributes(revomon_name=names[0].lower())
        if not attributes:
            await interaction.followup.send(
                f"No Revomon found for '{names[0]}'.", ephemeral=True
            )
            return

        if is_compare:
            attributes2 = await get_attributes(revomon_name=names[1].lower())
            if not attributes2:
                await interaction.followup.send(
                    f"No Revomon found for '{names[1]}'.", ephemeral=True
                )
                return
            if verb == "compare_types":
                embed, embed2 = compare_types(attributes, attributes2)
                await interaction.followup.send(embed=embed, ephemeral=True)
                await interaction.followup.send(embed=embed2, ephemeral=True)
            else:
                cmp_builder: Callable[
                    [dict[str, Any], dict[str, Any]], discord.Embed
                ] = {
                    "compare_stats": compare_stats,
                    "compare_spawns": compare_spawns,
                    "compare_moves": compare_moves,
                    "compare_counterdexs": compare_counterdexs,
                }[verb]
                await interaction.followup.send(
                    embed=cmp_builder(attributes, attributes2), ephemeral=True
                )
            return

        single_builders: dict[str, Callable[[dict[str, Any]], discord.Embed]] = {
            "stats": stats,
            "spawns": spawns,
            "moves": moves,
            "types": types,
            "counterdex": counterdex,
        }
        await interaction.followup.send(
            embed=single_builders[verb](attributes), ephemeral=True
        )

    async def _handle_mon_lookup(self, interaction: Interaction, name: str) -> None:
        await interaction.response.defer()
        attributes = await get_attributes(revomon_name=name.lower())
        if not attributes:
            await interaction.followup.send(
                f"No Revomon found for '{name}'.", ephemeral=True
            )
            return
        embed = intro(attributes)
        intro_view = IntroView(attributes)
        await interaction.followup.send(embed=embed, view=intro_view, ephemeral=True)

    async def _handle_mon_goto(self, interaction: Interaction, page: int) -> None:
        await interaction.response.defer()
        view = await self.mon_view(user_id=interaction.user.id, page=page)
        if interaction.message is not None:
            await interaction.followup.edit_message(interaction.message.id, view=view)

    async def _handle_land_goto(self, interaction: Interaction, page: int) -> None:
        await interaction.response.defer()
        view = await self.land_view(user_id=interaction.user.id, page=page)
        if interaction.message is not None:
            await interaction.followup.edit_message(interaction.message.id, view=view)

    async def _handle_land_lookup(
        self, interaction: Interaction, token_id: int
    ) -> None:
        await interaction.response.defer()
        land_obj = OwnedLandsTable()
        land_info_list = await land_obj.get_info(token_id=token_id)
        if not land_info_list:
            await interaction.followup.send(
                f"Land {token_id} not found", ephemeral=True
            )
            return
        land_info = land_info_list[0]
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

    @commands.Cog.listener()
    async def on_interaction(self, interaction: Interaction) -> None:
        """Route stateless browse-button clicks by custom_id prefix.

        Malformed or unrecognized ids are logged at debug level and ignored;
        only recognizable-but-stale pager ids produce a user-facing notice.
        """
        try:
            user = getattr(interaction, "user", None)
            if getattr(user, "bot", False):
                return

            custom_id = self._extract_custom_id(interaction)
            if custom_id is None:
                return
            logger.debug(f"[Buttons] component custom_id={custom_id}")

            # Live-view features own these while their views are alive.
            if custom_id.startswith(
                ("mon:share", "mon:search_sort", "land:search_sort")
            ):
                return

            if custom_id in self._LEGACY_PAGERS:
                await self._send_expiry_notice(interaction)
                return

            if custom_id.startswith("action:"):
                await self._handle_action(interaction, custom_id)
                return

            if ":goto:" in custom_id and custom_id.startswith(
                ("mon_page:", "land_page:")
            ):
                prefix, _, rest = custom_id.partition(":goto:")
                try:
                    page = int(rest)
                except ValueError:
                    logger.debug(f"[Buttons] bad goto page in {custom_id!r}")
                    return
                if prefix == "mon_page":
                    await self._handle_mon_goto(interaction, page)
                else:
                    await self._handle_land_goto(interaction, page)
                return

            if custom_id.startswith("land:"):
                suffix = custom_id[len("land:") :]
                try:
                    token_id = int(suffix)
                except ValueError:
                    logger.debug(f"[Buttons] bad land id in {custom_id!r}")
                    return
                await self._handle_land_lookup(interaction, token_id)
                return

            if custom_id.startswith("land ") and len(custom_id.split()) == 2:
                raw = custom_id.split()[1]
                try:
                    token_id = int(raw)
                except ValueError:
                    logger.debug(f"[Buttons] bad legacy land id in {custom_id!r}")
                    return
                await self._handle_land_lookup(interaction, token_id)
                return

            if custom_id.startswith("mon:"):
                name = custom_id[len("mon:") :]
                if name:
                    await self._handle_mon_lookup(interaction, name)
                return

            if custom_id in self._MON_ALIASES:
                await self._handle_mon_lookup(interaction, custom_id)
                return

            logger.debug(f"[Buttons] ignoring unrecognized custom_id={custom_id!r}")
        except Exception as e:
            logger.error(f"[Buttons] router error: {e}", exc_info=True)


async def setup(gradex: commands.Bot) -> None:
    await gradex.add_cog(Buttons(gradex))
