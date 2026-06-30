from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from discord import ButtonStyle

from utils.button_utils import Buttons, setup


@pytest.fixture
def mock_bot() -> Any:
    bot = MagicMock()
    bot.add_cog = AsyncMock()
    return bot


@pytest.fixture
def buttons_cog(mock_bot: Any) -> Any:
    with patch(
        "utils.button_utils.get_book_of_mon_names", new_callable=AsyncMock
    ) as mock_get:
        mock_get.return_value = [["mon1", "mon2"], ["mon3"]]
        cog = Buttons(mock_bot)
        return cog


def test_init(buttons_cog: Any, mock_bot: Any) -> None:
    assert buttons_cog.gradex == mock_bot
    assert buttons_cog.book_of_names is None
    assert buttons_cog.current_page == {}
    assert buttons_cog.attributes == {}
    assert buttons_cog.attributes2 == {}
    assert buttons_cog.book_of_land_ids is None
    assert buttons_cog.book_of_land_current_page == {}
    assert buttons_cog.land_attributes == {}


@pytest.mark.asyncio
@patch("utils.button_utils.RevomonTable")
async def test_mon_button(mock_revo_table: Any, buttons_cog: Any) -> None:
    mock_instance = mock_revo_table.return_value
    mock_instance.get_info = AsyncMock(
        return_value=[
            [
                1,
                "dex1",
                "a",
                "b",
                "c",
                "d",
                "e",
                "f",
                "g",
                "h",
                "i",
                "emoji_id",
                "k",
                "l",
                "m",
            ]
        ]
    )

    button = await buttons_cog.mon_button("mon1", 1)

    assert button.label == "1. Mon1"
    assert button.custom_id == "mon1"
    assert button.row == 1
    assert button.style == ButtonStyle.gray
    assert button.callback == buttons_cog.on_button_click
    mock_instance.get_info.assert_called_with("mon1")


@pytest.mark.asyncio
@patch("utils.button_utils.OwnedLandsTable")
async def test_land_button(mock_owned_lands_table: Any, buttons_cog: Any) -> None:
    mock_instance = mock_owned_lands_table.return_value
    # [-2] is for_sale_usd
    mock_instance.get_info = AsyncMock(
        return_value=[
            [
                1,
                2,
                "address",
                "forest",
                "plot",
                "rare",
                "small",
                "url",
                "tree_emoji",
                True,
                "sym",
                "100",
                "1000",
            ]
        ]
    )

    button = await buttons_cog.land_button(2, 2)

    assert button.label == "2. Plot · Forest ($100)"
    assert button.custom_id == "land 2"
    assert button.row == 2
    assert button.style == ButtonStyle.gray
    assert button.callback == buttons_cog.on_button_click
    mock_instance.get_info.assert_called_with(token_id=2)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "method_name,label,custom_id",
    [
        ("stats_button", "Stats", "stats"),
        ("compare_stats_button", "Compare Stats", "compare_stats"),
        ("spawns_button", "Spawns", "spawns"),
        ("compare_spawns_button", "Compare Spawns", "compare_Spawns"),
        ("moves_button", "Moves", "moves"),
        ("compare_moves_button", "Compare Moves", "compare_move_list"),
        ("types_button", "Types", "types"),
        ("compare_types_button", "Compare Types", "compare_types"),
        ("counterdex_button", "Counterdex", "counterdex"),
        ("compare_counterdexs_button", "Compare Counterdexs", "compare_counterdexs"),
    ],
)
async def test_info_buttons(
    buttons_cog: Any, method_name: Any, label: Any, custom_id: Any
) -> None:
    method = getattr(buttons_cog, method_name)
    button = await method()
    assert button.label == label
    assert button.custom_id == custom_id
    assert button.style == ButtonStyle.green
    assert button.callback == buttons_cog.on_button_click


@pytest.mark.parametrize(
    "method_name,custom_id,emoji",
    [
        ("first_page_button", "first_page", "⏮️"),
        ("previous_button", "previous_page", "⏪"),
        ("next_button", "next_page", "⏩"),
        ("last_page_button", "last_page", "⏭️"),
        ("first_page_button_land", "first_page_land", "⏮️"),
        ("previous_button_land", "previous_page_land", "⏪"),
        ("next_button_land", "next_page_land", "⏩"),
        ("last_page_button_land", "last_page_land", "⏭️"),
    ],
)
def test_sync_navigation_buttons(
    buttons_cog: Any, method_name: Any, custom_id: Any, emoji: Any
) -> None:
    method = getattr(buttons_cog, method_name)
    button = method(1)
    assert button.custom_id == custom_id
    assert button.row == 1
    assert button.style == ButtonStyle.green
    assert button.emoji.name == emoji
    assert button.callback == buttons_cog.on_button_click


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "method_name,custom_id,style,emoji",
    [
        ("exit_button", "exit", ButtonStyle.red, "❌"),
        ("search_button_land", "search_land", ButtonStyle.green, "🔎"),
        ("filter_button_land", "filter_land", ButtonStyle.green, "filter"),
        ("sort_by_button_land", "sort_by_land", ButtonStyle.green, "sortby"),
        ("search_settings_button_land", "search_settings_land", ButtonStyle.green, "⚙️"),
    ],
)
async def test_async_land_buttons(
    buttons_cog: Any, method_name: Any, custom_id: Any, style: Any, emoji: Any
) -> None:
    method = getattr(buttons_cog, method_name)
    button = await method(2)
    assert button.custom_id == custom_id
    assert button.row == 2
    assert button.style == style
    assert button.emoji.name == emoji
    assert button.callback == buttons_cog.on_button_click


@pytest.mark.asyncio
@patch("utils.button_utils.RevomonTable")
async def test_mon_view(mock_revo_table: Any, buttons_cog: Any) -> None:
    buttons_cog.book_of_names = [["mon1"]]
    mock_instance = mock_revo_table.return_value
    # mock get_info, indices: 0: dex_num, 8: ability_hidden?, -10: emoji
    mock_info = [
        [
            1,
            "dex1",
            "a",
            "b",
            "c",
            "d",
            "e",
            "f",
            None,
            "h",
            "i",
            "emoji_id",
            "k",
            "l",
            "m",
        ]
    ]
    mock_instance.get_info = AsyncMock(return_value=mock_info)

    view = await buttons_cog.mon_view(user_id=123)
    assert buttons_cog.current_page[123] == 1
    assert len(view.children) > 0

    # Test with existing page
    buttons_cog.current_page[123] = 1  # Keep it at 1 since we only have 1 page now
    view = await buttons_cog.mon_view(user_id=123)
    assert buttons_cog.current_page[123] == 1
    assert len(view.children) > 0


@pytest.mark.asyncio
@patch("utils.button_utils.OwnedLandsTable")
@patch("utils.button_utils.get_book_of_land_ids", new_callable=AsyncMock)
async def test_land_view(mock_get_book: Any, mock_owned: Any, buttons_cog: Any) -> None:
    mock_get_book.return_value = [[1, 2, 3]]
    mock_instance = mock_owned.return_value
    mock_instance.get_info = AsyncMock(
        return_value=[
            [
                1,
                2,
                "address",
                "forest",
                "plot",
                "rare",
                "small",
                "url",
                "tree",
                True,
                "sym",
                "100",
                "1000",
            ]
        ]
    )

    # User ID not in dict, tokens provided
    view = await buttons_cog.land_view(user_id=123, token_ids=[1, 2, 3])
    assert buttons_cog.book_of_land_current_page[123] == 1
    assert len(view.children) > 0

    # User ID in dict, tokens not provided, book_of_land_ids is populated
    buttons_cog.book_of_land_current_page[123] = (
        1  # Keep it at 1 since we only have 1 page now
    )
    view = await buttons_cog.land_view(user_id=123)
    assert buttons_cog.book_of_land_current_page[123] == 1
    assert len(view.children) > 0

    # tokens not provided and book_of_land_ids is None
    buttons_cog.book_of_land_ids = None
    view = await buttons_cog.land_view(user_id=124)
    assert buttons_cog.book_of_land_current_page[124] == 1
    assert len(view.children) > 0


@pytest.mark.asyncio
async def test_intro_view(buttons_cog: Any) -> None:
    view = await buttons_cog.intro_view(attributes={"attr": 1})
    assert buttons_cog.attributes == {"attr": 1}
    assert len(view.children) == 5


@pytest.mark.asyncio
async def test_compare_intros_view(buttons_cog: Any) -> None:
    view = await buttons_cog.compare_intros_view(
        attributes={"a": 1}, attributes2={"b": 2}
    )
    assert buttons_cog.attributes == {"a": 1}
    assert buttons_cog.attributes2 == {"b": 2}
    assert len(view.children) == 5


@pytest.mark.asyncio
async def test_on_ready(buttons_cog: Any, capsys: Any) -> None:
    await buttons_cog.on_ready()
    captured = capsys.readouterr()
    assert "utils(Button Utils) is ready!" in captured.out


@pytest.mark.asyncio
@patch("utils.button_utils.intro")
@patch("utils.button_utils.get_attributes", new_callable=AsyncMock)
@patch("utils.button_utils.RevomonTable")
async def test_on_button_click_mon(
    mock_revo_table: Any, mock_get_attrs: Any, mock_intro: Any, buttons_cog: Any
) -> None:
    mock_revo_table.return_value.get_names = AsyncMock(return_value=["mon1"])
    mock_get_attrs.return_value = {"a": 1}
    mock_intro.return_value = "embed"

    interaction = MagicMock()
    interaction.user.bot = False
    interaction.data = {"custom_id": "mon1"}
    interaction.response.defer = AsyncMock()
    interaction.followup.send = AsyncMock()

    await buttons_cog.on_button_click(interaction)

    interaction.response.defer.assert_called_once()
    interaction.followup.send.assert_called_once()
    assert interaction.followup.send.call_args[1]["embed"] == "embed"


@pytest.mark.asyncio
@patch("utils.button_utils.RevomonTable")
@patch("utils.button_utils.land_intro")
@patch("utils.button_utils.OwnedLandsTable")
async def test_on_button_click_land(
    mock_owned: Any, mock_land_intro: Any, mock_revo_table: Any, buttons_cog: Any
) -> None:
    mock_revo_table.return_value.get_names = AsyncMock(return_value=[])
    mock_instance = mock_owned.return_value
    mock_instance.get_info = AsyncMock(
        return_value=[
            [
                1,
                2,
                "address",
                "forest",
                "plot",
                "rare",
                "small",
                "url",
                "tree",
                True,
                "sym",
                "100",
                "1000",
            ]
        ]
    )
    mock_land_intro.return_value = "embed"

    interaction = MagicMock()
    interaction.user.bot = False
    interaction.data = {"custom_id": "land 2"}
    interaction.response.defer = AsyncMock()
    interaction.followup.send = AsyncMock()

    await buttons_cog.on_button_click(interaction)

    interaction.response.defer.assert_called_once()
    interaction.followup.send.assert_called_once()
    assert interaction.followup.send.call_args[1]["embed"] == "embed"


@pytest.mark.asyncio
@patch("utils.button_utils.RevomonTable")
@patch("utils.button_utils.Buttons.mon_view")
async def test_on_button_click_pagination(
    mock_mon_view: Any, mock_revo_table: Any, buttons_cog: Any
) -> None:
    mock_revo_table.return_value.get_names = AsyncMock(return_value=[])
    mock_mon_view.return_value = "view"

    for custom_id in ["last_page", "previous_page", "next_page", "first_page"]:
        interaction = MagicMock()
        interaction.user.bot = False
        interaction.user.id = 123
        interaction.data = {"custom_id": custom_id}
        interaction.response.defer = AsyncMock()
        interaction.followup.edit_message = AsyncMock()

        if custom_id in ("next_page", "first_page"):
            buttons_cog.current_page[123] = -1  # next_page adds 1 -> 0, which is < 1
        else:
            buttons_cog.current_page[123] = 0  # last_page, previous_page will be < 1

        # for last_page, len(book_of_names) needs to be 0 to trigger the < 1 condition
        if custom_id == "last_page":
            buttons_cog.book_of_names = []
            mock_mon_view.return_value = "view"
        else:
            buttons_cog.book_of_names = [["mon1"]]

        await buttons_cog.on_button_click(interaction)

        interaction.response.defer.assert_called_once()
        interaction.followup.edit_message.assert_called_once_with(
            message_id=interaction.message.id, view="view"
        )


@pytest.mark.asyncio
@patch("utils.button_utils.RevomonTable")
@patch("utils.button_utils.Buttons.land_view")
async def test_on_button_click_land_pagination(
    mock_land_view: Any, mock_revo_table: Any, buttons_cog: Any
) -> None:
    mock_revo_table.return_value.get_names = AsyncMock(return_value=[])
    mock_land_view.return_value = "view"
    buttons_cog.book_of_land_ids = [[1, 2], [3]]

    for custom_id in [
        "last_page_land",
        "previous_page_land",
        "next_page_land",
        "first_page_land",
    ]:
        interaction = MagicMock()
        interaction.user.bot = False
        interaction.user.id = 123
        interaction.data = {"custom_id": custom_id}
        interaction.response.defer = AsyncMock()
        interaction.followup.edit_message = AsyncMock()

        if custom_id in ("next_page_land", "first_page_land"):
            buttons_cog.book_of_land_current_page[123] = -1
        else:
            buttons_cog.book_of_land_current_page[123] = 0

        if custom_id == "last_page_land":
            buttons_cog.book_of_land_ids = []
            mock_land_view.return_value = "view"
        else:
            buttons_cog.book_of_land_ids = [[1, 2], [3]]

        await buttons_cog.on_button_click(interaction)

        interaction.response.defer.assert_called_once()
        interaction.followup.edit_message.assert_called_once_with(
            message_id=interaction.message.id, view="view"
        )


<<<<<<< HEAD

=======
@pytest.mark.asyncio
@patch("utils.button_utils.RevomonTable")
async def test_on_button_click_search_settings_land(
    mock_revo_table: Any, buttons_cog: Any
) -> None:
    mock_revo_table.return_value.get_names = AsyncMock(return_value=[])
    interaction = MagicMock()
    interaction.user.bot = False
    interaction.data = {"custom_id": "search_settings_land"}
    interaction.response.defer = AsyncMock()
    interaction.followup.send = AsyncMock()

    await buttons_cog.on_button_click(interaction)

    interaction.response.defer.assert_called_once()
    interaction.followup.send.assert_called_once()
>>>>>>> de733c415448a6db7eb45eb4a06a6462f48833b2


@pytest.mark.asyncio
@patch("utils.button_utils.RevomonTable")
@pytest.mark.parametrize(
    "custom_id,func_mock",
    [
        ("stats", "utils.button_utils.stats"),
        ("compare_stats", "utils.button_utils.compare_stats"),
        ("spawns", "utils.button_utils.spawns"),
        ("compare_spawns", "utils.button_utils.compare_spawns"),
        ("moves", "utils.button_utils.moves"),
        ("compare_moves", "utils.button_utils.compare_moves"),
        ("types", "utils.button_utils.types"),
        ("counterdex", "utils.button_utils.counterdex"),
        ("compare_counterdexs", "utils.button_utils.compare_counterdexs"),
    ],
)
async def test_on_button_click_info(
    mock_revo_table: Any, buttons_cog: Any, custom_id: Any, func_mock: Any
) -> None:
    mock_revo_table.return_value.get_names = AsyncMock(return_value=[])
    with patch(func_mock) as mock_func:
        mock_func.return_value = "embed"

        interaction = MagicMock()
        interaction.user.bot = False
        interaction.data = {"custom_id": custom_id}
        interaction.response.defer = AsyncMock()
        interaction.followup.send = AsyncMock()

        await buttons_cog.on_button_click(interaction)

        interaction.response.defer.assert_called_once()
        interaction.followup.send.assert_called_once_with(embed="embed", ephemeral=True)


@pytest.mark.asyncio
@patch("utils.button_utils.RevomonTable")
@patch("utils.button_utils.compare_types")
async def test_on_button_click_compare_types(
    mock_compare_types: Any, mock_revo_table: Any, buttons_cog: Any
) -> None:
    mock_revo_table.return_value.get_names = AsyncMock(return_value=[])
    mock_compare_types.return_value = ("embed1", "embed2")

    interaction = MagicMock()
    interaction.user.bot = False
    interaction.data = {"custom_id": "compare_types"}
    interaction.response.defer = AsyncMock()
    interaction.followup.send = AsyncMock()

    await buttons_cog.on_button_click(interaction)

    interaction.response.defer.assert_called_once()
    assert interaction.followup.send.call_count == 2


@pytest.mark.asyncio
async def test_on_button_click_bot_user(buttons_cog: Any) -> None:
    interaction = MagicMock()
    interaction.user.bot = True

    await buttons_cog.on_button_click(interaction)
    # Should return early
    interaction.response.defer.assert_not_called()


@pytest.mark.asyncio
async def test_on_button_click_exception(buttons_cog: Any) -> None:
    interaction = MagicMock()
    interaction.user.bot = False
    interaction.data = {"custom_id": "mon1"}

    # Make RevomonTable raise an exception to hit the outer except block
    with patch("utils.button_utils.RevomonTable") as mock_revo_table:
        mock_revo_table.return_value.get_names.side_effect = Exception("Test Error")

        # Exception should be caught and printed
        await buttons_cog.on_button_click(interaction)


@pytest.mark.asyncio
@patch("utils.button_utils.RevomonTable")
async def test_on_button_click_stats_exception(
    mock_revo_table: Any, buttons_cog: Any
) -> None:
    mock_revo_table.return_value.get_names = AsyncMock(return_value=[])
    interaction = MagicMock()
    interaction.user.bot = False
    interaction.data = {"custom_id": "stats"}

    with patch("utils.button_utils.stats") as mock_stats:
        mock_stats.side_effect = Exception("Test Error")

        # Exception should be caught and printed, continuing to the end
        await buttons_cog.on_button_click(interaction)


@pytest.mark.asyncio
@patch("utils.button_utils.get_book_of_mon_names")
async def test_setup(mock_get_book: Any, mock_bot: Any) -> None:
    mock_get_book.return_value = []
    await setup(mock_bot)
    mock_bot.add_cog.assert_called_once()
