import logging
from collections.abc import Callable
from typing import Any

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

# Sortable fields for the stateless sort panels (value, label).
MON_SORT_FIELDS: tuple[tuple[str, str], ...] = (
    ("dex_id", "Dex #"),
    ("name", "Name"),
    ("type1", "Type"),
    ("hp", "HP"),
    ("atk", "ATK"),
    ("def", "DEF"),
    ("spa", "SPA"),
    ("spd", "SPD"),
    ("spe", "SPE"),
    ("rarity", "Rarity"),
)
LAND_SORT_FIELDS: tuple[tuple[str, str], ...] = (
    ("token_id", "Token ID"),
    ("biome", "Biome"),
    ("land_type", "Land Type"),
    ("rarity", "Rarity"),
    ("for_sale_usd", "Price"),
    ("size", "Size"),
    ("owners_address", "Owner's Address"),
)
SORT_ORDERS: tuple[tuple[str, str], ...] = (
    ("asc", "Ascending"),
    ("desc", "Descending"),
)
_VALID_MON_SORT_FIELDS = frozenset(v for v, _ in MON_SORT_FIELDS)
_VALID_LAND_SORT_FIELDS = frozenset(v for v, _ in LAND_SORT_FIELDS)

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
        self.add_item(SearchSortButton(row=pagination_row, page=self.current_page))
        self.add_item(
            NextPageButton(
                row=pagination_row,
                current_page=self.current_page,
                total_pages=self.total_pages,
            )
        )
        self.add_item(LastPageButton(row=pagination_row, total_pages=self.total_pages))
        self.add_item(
            ShareButton(
                row=min(pagination_row + 1, 4),
                user_id=self.user_id,
                page=self.current_page,
            )
        )

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
        self.add_item(SearchSortLandButton(row=pagination_row, page=self.current_page))
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
    """Re-post the current browse view publicly; payload rides in custom_id."""

    def __init__(self, row: int, user_id: int, page: int) -> None:
        super().__init__(
            emoji="\U0001f4e4",
            style=ButtonStyle.green,
            row=row,
            custom_id=f"mon:share:{user_id}:{page}",
        )

    async def callback(self, interaction: Interaction) -> None:
        return None  # Handled by the Buttons cog's on_interaction router


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


# Sort-entry buttons — page encoded; the router renders a restart-safe
# sort panel (selects + cancel are themselves router-owned components).
class SearchSortButton(Button[View]):
    def __init__(self, row: int, page: int = 1) -> None:
        super().__init__(
            label="",
            emoji="\U0001f50d",
            style=ButtonStyle.secondary,
            custom_id=f"mon:search_sort:{page}",
            row=row,
        )

    async def callback(self, interaction: Interaction) -> None:
        return None  # Handled by the Buttons cog's on_interaction router


class SearchSortLandButton(Button[View]):
    def __init__(self, row: int, page: int = 1) -> None:
        super().__init__(
            label="",
            emoji="\U0001f50d",
            style=ButtonStyle.secondary,
            custom_id=f"land:search_sort:{page}",
            row=row,
        )

    async def callback(self, interaction: Interaction) -> None:
        return None  # Handled by the Buttons cog's on_interaction router


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
            # Pre-router sort/share ids whose live closures are gone.
            "mon:share",
            "mon:search_sort",
            "land:search_sort",
            "mon_sort_by_select",
            "mon_sort_order_select",
            "apply_mon_sort",
            "cancel_mon_sort",
            "land_sort_by_select",
            "land_sort_order_select",
            "apply_land_sort",
            "cancel_land_sort",
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

    @staticmethod
    def _parse_page(raw: str) -> int | None:
        try:
            return max(1, int(raw))
        except ValueError:
            logger.debug(f"[Buttons] bad page value {raw!r}")
            return None

    @staticmethod
    def _extract_values(interaction: Interaction) -> list[str]:
        data = interaction.data
        if not isinstance(data, dict):
            return []
        values = data.get("values")
        if isinstance(values, list):
            return [v for v in values if isinstance(v, str)]
        return []

    def _build_sort_panel(self, kind: str, field: str, page: int) -> View:
        """Restart-safe sort panel: every component is router-owned."""
        fields = MON_SORT_FIELDS if kind == "mon" else LAND_SORT_FIELDS
        default_label = "Dex #" if kind == "mon" else "Token ID"
        by_select: Select[View] = Select(
            placeholder="Sort by...",
            custom_id=f"{kind}_sort_by:{page}",
            row=0,
            options=[SelectOption(label=lbl, value=val) for val, lbl in fields],
        )
        order_select: Select[View] = Select(
            placeholder=(
                f"Sort order... (picking applies; default {default_label})"
                if field == "_"
                else f"Sort by '{field}' - pick order to apply"
            ),
            custom_id=f"{kind}_sort_order:{field}:{page}",
            row=1,
            options=[SelectOption(label=lbl, value=val) for val, lbl in SORT_ORDERS],
        )
        cancel_button: Button[View] = Button(
            label="Cancel",
            style=ButtonStyle.secondary,
            custom_id=f"{kind}_sort_cancel:{page}",
            row=2,
        )
        view = View(timeout=None)
        view.add_item(by_select)
        view.add_item(order_select)
        view.add_item(cancel_button)
        return view

    async def _handle_share(
        self, interaction: Interaction, user_id: int, page: int
    ) -> None:
        await interaction.response.defer()
        view = await self.mon_view(user_id=user_id, page=page)
        if interaction.message is not None:
            # Public re-post of a browsable, restart-proof copy.
            await interaction.followup.send(view=view, ephemeral=False)

    async def _handle_sort_panel(
        self, interaction: Interaction, kind: str, field: str, page: int
    ) -> None:
        await interaction.response.defer()
        panel = self._build_sort_panel(kind, field, page)
        if interaction.message is not None:
            await interaction.followup.edit_message(interaction.message.id, view=panel)

    async def _handle_sort_cancel(
        self, interaction: Interaction, kind: str, page: int
    ) -> None:
        await interaction.response.defer()
        view: View
        if kind == "mon":
            view = await self.mon_view(user_id=interaction.user.id, page=page)
        else:
            view = await self.land_view(user_id=interaction.user.id, page=page)
        if interaction.message is not None:
            await interaction.followup.edit_message(interaction.message.id, view=view)

    async def _handle_sort_apply(
        self,
        interaction: Interaction,
        kind: str,
        effective_field: str,
        asc: bool,
        page: int,
    ) -> None:
        await interaction.response.defer()
        clicker_id = interaction.user.id

        if kind == "mon":
            group_by_evo = effective_field == "dex_id"
            sorted_names = await RevomonTable().get_sorted_names(
                sort_by=effective_field, asc=asc
            )
            book_of_names = await get_book_of_mon_names(
                names=sorted_names, group_by_evo=group_by_evo
            )
            new_view: View = MonPaginationView(
                bot=self.gradex,
                user_id=clicker_id,
                book_of_names=book_of_names,
                current_page=1,
                group_by_evo=group_by_evo,
                app_emojis=await self._load_app_emojis(),
            )
        else:
            sorted_lands = await OwnedLandsTable().get_info(
                sort_by=effective_field, asc=asc
            )
            sorted_token_ids = (
                [land[0] for land in sorted_lands] if sorted_lands else []
            )
            book_of_land_ids = await get_book_of_land_ids(token_ids=sorted_token_ids)
            new_view = LandPaginationView(
                user_id=clicker_id,
                book_of_land_ids=book_of_land_ids or [],
                current_page=1,
            )

        if interaction.message is not None:
            await interaction.followup.edit_message(
                interaction.message.id, view=new_view
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

            if custom_id in self._LEGACY_PAGERS:
                await self._send_expiry_notice(interaction)
                return

            if custom_id.startswith("mon:share:"):
                rest = custom_id[len("mon:share:") :]
                uid_s, sep, page_s = rest.partition(":")
                try:
                    share_uid = int(uid_s)
                    share_page = max(1, int(page_s))
                except ValueError:
                    logger.debug(f"[Buttons] bad share id {custom_id!r}")
                    return
                await self._handle_share(interaction, share_uid, share_page)
                return

            if custom_id.startswith("mon:search_sort:"):
                page = self._parse_page(custom_id.rpartition(":")[2])
                if page is not None:
                    await self._handle_sort_panel(interaction, "mon", "_", page)
                return

            if custom_id.startswith("land:search_sort:"):
                page = self._parse_page(custom_id.rpartition(":")[2])
                if page is not None:
                    await self._handle_sort_panel(interaction, "land", "_", page)
                return

            if custom_id.startswith(("mon_sort_by:", "land_sort_by:")):
                kind = "mon" if custom_id.startswith("mon_") else "land"
                page = self._parse_page(custom_id.rpartition(":")[2])
                values = self._extract_values(interaction)
                field = values[0] if values else "_"
                valid_fields = (
                    _VALID_MON_SORT_FIELDS if kind == "mon" else _VALID_LAND_SORT_FIELDS
                )
                if page is None or field not in valid_fields:
                    logger.debug(f"[Buttons] bad sort-by id {custom_id!r}")
                    return
                await self._handle_sort_panel(interaction, kind, field, page)
                return

            if custom_id.startswith(("mon_sort_order:", "land_sort_order:")):
                kind = "mon" if custom_id.startswith("mon_") else "land"
                field, _, rest = custom_id.partition(":")[2].rpartition(":")
                page = self._parse_page(rest)
                values = self._extract_values(interaction)
                order = values[0] if values else ""
                valid_fields = (
                    _VALID_MON_SORT_FIELDS if kind == "mon" else _VALID_LAND_SORT_FIELDS
                )
                effective_field: str | None
                if field == "_":
                    effective_field = "dex_id" if kind == "mon" else "token_id"
                elif field in valid_fields:
                    effective_field = field
                else:
                    effective_field = None
                if (
                    page is None
                    or order not in {"asc", "desc"}
                    or effective_field is None
                ):
                    logger.debug(f"[Buttons] bad sort-order id {custom_id!r}")
                    return
                await self._handle_sort_apply(
                    interaction, kind, effective_field, order == "asc", page
                )
                return

            if custom_id.startswith(("mon_sort_cancel:", "land_sort_cancel:")):
                kind = "mon" if custom_id.startswith("mon_") else "land"
                page = self._parse_page(custom_id.rpartition(":")[2])
                if page is not None:
                    await self._handle_sort_cancel(interaction, kind, page)
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
