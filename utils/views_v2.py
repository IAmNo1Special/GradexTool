"""Components V2 (LayoutView) utilities for modern Discord UI."""

from collections.abc import Callable
from typing import Any

from discord import ButtonStyle, SelectOption, ui
from discord.ui import ActionRow, Button, Select


def build_text_view(content: str, *, accent_color: int | None = None) -> ui.LayoutView:
    """Build a V2 LayoutView containing a single Container with TextDisplay."""
    view = ui.LayoutView()
    text_display: Any = ui.TextDisplay(content)
    container = ui.Container(text_display, accent_color=accent_color)
    view.add_item(container)
    return view


def build_embed_view(embed: Any, *, accent_color: int | None = None) -> ui.LayoutView:
    """Build a V2 LayoutView with a single Container containing an Embed."""
    view = ui.LayoutView()
    container = ui.Container(embed, accent_color=accent_color)
    view.add_item(container)
    return view


def build_section_view(
    title: str,
    description: str,
    *,
    accent_color: int | None = None,
    thumbnail: str | None = None,
) -> ui.LayoutView:
    """Build a V2 LayoutView with a titled section."""
    view = ui.LayoutView()
    content = f"## {title}\n{description}"
    text_display: Any = ui.TextDisplay(content)
    container = ui.Container(text_display, accent_color=accent_color)
    if thumbnail:
        container.add_item(ui.Thumbnail(media=thumbnail))
    view.add_item(container)
    return view


def build_list_view(
    title: str,
    items: list[str],
    *,
    accent_color: int | None = None,
    numbered: bool = False,
) -> ui.LayoutView:
    """Build a V2 LayoutView with a list of items."""
    view = ui.LayoutView()
    if numbered:
        content = f"## {title}\n" + "\n".join(
            f"{i + 1}. {item}" for i, item in enumerate(items)
        )
    else:
        content = f"## {title}\n" + "\n".join(f"- {item}" for item in items)
    text_display: Any = ui.TextDisplay(content)
    container = ui.Container(text_display, accent_color=accent_color)
    view.add_item(container)
    return view


class PaginationView(ui.LayoutView):
    """A V2 LayoutView with pagination controls."""

    def __init__(
        self,
        items: list[Any],
        items_per_page: int = 10,
        title: str = "",
        formatter: Callable[[Any], str] | None = None,
    ):
        super().__init__(timeout=None)
        self.items = items
        self.items_per_page = items_per_page
        self.title = title
        self.formatter = formatter or (lambda x: str(x))
        self.current_page = 0
        self._build_page()

    def _build_page(self) -> None:
        self.clear_items()
        start = self.current_page * self.items_per_page
        end = start + self.items_per_page
        page_items = self.items[start:end]

        content = ""
        if self.title:
            content = f"## {self.title}\n\n"

        for i, item in enumerate(page_items, start=start + 1):
            content += f"{i}. {self.formatter(item)}\n"

        text_display: Any = ui.TextDisplay(content)
        container = ui.Container(text_display, accent_color=0x2ECC71)
        self.add_item(container)

        # Pagination controls
        total_pages = (len(self.items) + self.items_per_page - 1) // self.items_per_page
        if total_pages > 1:
            action_row: Any = ActionRow()
            action_row.add_item(
                Button(
                    label="\u23ee",
                    style=ButtonStyle.gray,
                    custom_id="page:first",
                    disabled=self.current_page == 0,
                )
            )
            action_row.add_item(
                Button(
                    label="\u23ea",
                    style=ButtonStyle.gray,
                    custom_id="page:prev",
                    disabled=self.current_page == 0,
                )
            )
            action_row.add_item(
                Button(
                    label=f"Page {self.current_page + 1}/{total_pages}",
                    style=ButtonStyle.secondary,
                    disabled=True,
                )
            )
            action_row.add_item(
                Button(
                    label="\u23e9",
                    style=ButtonStyle.gray,
                    custom_id="page:next",
                    disabled=self.current_page >= total_pages - 1,
                )
            )
            action_row.add_item(
                Button(
                    label="\u23ef",
                    style=ButtonStyle.gray,
                    custom_id="page:last",
                    disabled=self.current_page >= total_pages - 1,
                )
            )
            self.add_item(action_row)


class SelectView(ui.LayoutView):
    """A V2 LayoutView with a dropdown select menu."""

    def __init__(
        self,
        placeholder: str,
        options: list[tuple[str, str, str | None]],  # (label, value, description)
        callback: Callable[..., Any],
        *,
        accent_color: int | None = None,
    ):
        super().__init__(timeout=None)
        self.callback = callback

        select: Select[Any] = Select(
            placeholder=placeholder,
            custom_id="select:menu",
            options=[
                SelectOption(label=label, value=value, description=desc)
                for label, value, desc in options
            ],
        )
        select.callback = self._on_select  # type: ignore[method-assign]

        container = ui.Container(select, accent_color=accent_color)
        self.add_item(container)

    async def _on_select(self, interaction: Any) -> None:
        await self.callback(interaction, interaction.data["values"][0])


class ConfirmView(ui.LayoutView):
    """A V2 LayoutView with confirm/cancel buttons."""

    def __init__(
        self,
        message: str,
        on_confirm: Callable[..., Any],
        on_cancel: Callable[..., Any] | None = None,
        *,
        accent_color: int | None = None,
    ):
        super().__init__(timeout=60)
        self.on_confirm = on_confirm
        self.on_cancel = on_cancel

        text_display: Any = ui.TextDisplay(message)
        container = ui.Container(text_display, accent_color=accent_color)

        action_row: Any = ActionRow()
        action_row.add_item(
            Button(label="Confirm", style=ButtonStyle.green, custom_id="confirm:yes")
        )
        action_row.add_item(
            Button(label="Cancel", style=ButtonStyle.red, custom_id="confirm:no")
        )

        self.add_item(container)
        self.add_item(action_row)


class InteractiveView(ui.LayoutView):
    """A V2 LayoutView with multiple interactive components."""

    def __init__(
        self,
        content: str,
        buttons: list[tuple[str, str, Callable[..., Any]]] | None = None,
        selects: list[tuple[str, list[tuple[str, str, str | None]], Callable[..., Any]]]
        | None = None,
        *,
        accent_color: int | None = None,
    ):
        super().__init__(timeout=None)

        text_display: Any = ui.TextDisplay(content)
        container = ui.Container(text_display, accent_color=accent_color)
        self.add_item(container)

        if buttons:
            action_row: Any = ActionRow()
            for label, custom_id, callback in buttons:
                btn: Button[Any] = Button(
                    label=label, style=ButtonStyle.primary, custom_id=custom_id
                )
                btn.callback = callback  # type: ignore[method-assign]
                action_row.add_item(btn)
            self.add_item(action_row)

        if selects:
            for placeholder, options, callback in selects:
                select: Select[Any] = Select(
                    placeholder=placeholder,
                    custom_id=f"select:{placeholder}",
                    options=[
                        SelectOption(label=label, value=value, description=desc)
                        for label, value, desc in options
                    ],
                )
                select.callback = callback  # type: ignore[method-assign]
                self.add_item(ui.Container(select, accent_color=accent_color))


async def send_v2(
    interaction: Any,
    content: str | None = None,
    embed: Any | None = None,
    view: ui.LayoutView | None = None,
    ephemeral: bool = False,
) -> None:
    """Send a V2 message (LayoutView) or fallback to legacy."""
    try:
        if view is not None:
            await interaction.response.send_message(view=view, ephemeral=ephemeral)
        elif embed is not None:
            await interaction.response.send_message(embed=embed, ephemeral=ephemeral)
        else:
            await interaction.response.send_message(
                content=content, ephemeral=ephemeral
            )
    except Exception:
        # Fallback to followup if response already sent
        if view is not None:
            await interaction.followup.send(view=view, ephemeral=ephemeral)
        elif embed is not None:
            await interaction.followup.send(embed=embed, ephemeral=ephemeral)
        else:
            await interaction.followup.send(content=content, ephemeral=ephemeral)
