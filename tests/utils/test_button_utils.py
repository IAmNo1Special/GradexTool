from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import discord
import pytest
from discord import ButtonStyle

from utils.button_utils import (
    Buttons,
    CompareIntroView,
    FirstPageButton,
    IntroView,
    LastPageButton,
    MonPaginationView,
    NextPageButton,
    PreviousPageButton,
    ShareButton,
    setup,
)


@pytest.fixture
def mock_bot() -> Any:
    bot = MagicMock()
    bot.add_cog = AsyncMock()
    return bot


@pytest.fixture
def buttons_cog(mock_bot: Any) -> Any:
    cog = Buttons(mock_bot)
    return cog


def _interaction(custom_id: str | None = None) -> Any:
    interaction = MagicMock()
    interaction.user.bot = False
    interaction.user.id = 123
    interaction.type = discord.InteractionType.component
    interaction.data = {"custom_id": custom_id} if custom_id is not None else {}
    interaction.message = MagicMock()
    interaction.message.id = 555
    interaction.response.defer = AsyncMock()
    interaction.response.send_message = AsyncMock()
    interaction.followup.send = AsyncMock()
    interaction.followup.edit_message = AsyncMock()
    return interaction


# ---------------------------------------------------------------- init/views


def test_init(buttons_cog: Any, mock_bot: Any) -> None:
    assert buttons_cog.gradex == mock_bot
    assert buttons_cog.book_of_names is None
    assert buttons_cog.book_of_land_ids is None
    assert buttons_cog.app_emojis is None


@pytest.mark.asyncio
async def test_on_ready(buttons_cog: Any, capsys: Any) -> None:
    await buttons_cog.on_ready()
    captured = capsys.readouterr()
    assert "utils(Button Utils) is ready!" in captured.out


@pytest.mark.asyncio
async def test_setup(mock_bot: Any) -> None:
    await setup(mock_bot)
    mock_bot.add_cog.assert_called_once()


def test_mon_pagination_pager_ids_encode_target_page() -> None:
    view = MonPaginationView(
        bot=MagicMock(),
        user_id=123,
        book_of_names=[["mon1"], ["mon2"]],
        current_page=1,
        group_by_evo=True,
        app_emojis={},
    )
    ids = [getattr(child, "custom_id", None) for child in view.children]
    assert "mon_page:goto:1" in ids  # first
    assert "mon_page:goto:2" in ids  # next from page 1
    # Previous/first are disabled on page 1 but still encode their target
    prev_btn = next(c for c in view.children if isinstance(c, PreviousPageButton))
    first_btn = next(c for c in view.children if isinstance(c, FirstPageButton))
    last_btn = next(c for c in view.children if isinstance(c, LastPageButton))
    next_btn = next(c for c in view.children if isinstance(c, NextPageButton))
    assert prev_btn.custom_id == "mon_page:goto:1" and prev_btn.disabled
    assert first_btn.custom_id == "mon_page:goto:1"
    assert next_btn.custom_id == "mon_page:goto:2" and not next_btn.disabled
    assert last_btn.custom_id == "mon_page:goto:2"


@pytest.mark.asyncio
async def test_share_button_in_view() -> None:
    view = MonPaginationView(
        bot=MagicMock(),
        user_id=123,
        book_of_names=[["mon1", "mon2"]],
        current_page=1,
        group_by_evo=True,
        app_emojis={},
    )
    share_buttons = [child for child in view.children if isinstance(child, ShareButton)]
    assert len(share_buttons) == 1
    assert share_buttons[0].custom_id == "mon:share"
    assert share_buttons[0].style == ButtonStyle.green


@pytest.mark.asyncio
async def test_share_button_callback() -> None:
    original_view = MonPaginationView(
        bot=MagicMock(),
        user_id=123,
        book_of_names=[["mon1", "mon2"]],
        current_page=1,
        group_by_evo=True,
        app_emojis={},
    )
    share_button = next(
        child for child in original_view.children if isinstance(child, ShareButton)
    )

    interaction = MagicMock()
    interaction.response.defer = AsyncMock()
    interaction.followup.send = AsyncMock()

    await share_button.callback(interaction)

    interaction.response.defer.assert_awaited_once()
    interaction.followup.send.assert_awaited_once()
    assert interaction.followup.send.call_args[1]["ephemeral"] is False
    new_view = interaction.followup.send.call_args[1]["view"]
    assert isinstance(new_view, MonPaginationView)
    assert new_view.current_page == original_view.current_page
    assert new_view is not original_view


@pytest.mark.asyncio
async def test_share_button_callback_no_view() -> None:
    button = ShareButton(row=0)

    interaction = MagicMock()
    interaction.response.defer = AsyncMock()
    interaction.followup.send = AsyncMock()

    await button.callback(interaction)

    interaction.response.defer.assert_not_awaited()
    interaction.followup.send.assert_not_awaited()


# ------------------------------------------------------------------ router


@pytest.mark.asyncio
@patch("utils.button_utils.intro")
@patch("utils.button_utils.get_attributes", new_callable=AsyncMock)
async def test_router_mon_lookup(
    mock_get_attrs: Any, mock_intro: Any, buttons_cog: Any
) -> None:
    mock_get_attrs.return_value = {"name": "mon1"}
    mock_intro.return_value = "embed"

    interaction = _interaction("mon:mon1")
    await buttons_cog.on_interaction(interaction)

    interaction.response.defer.assert_called_once()
    kwargs = interaction.followup.send.call_args[1]
    assert kwargs["embed"] == "embed"
    assert kwargs["ephemeral"] is True


@pytest.mark.asyncio
@patch("utils.button_utils.get_attributes", new_callable=AsyncMock)
async def test_router_mon_lookup_unknown(mock_get_attrs: Any, buttons_cog: Any) -> None:
    mock_get_attrs.return_value = {}

    interaction = _interaction("mon:nosuchmon")
    await buttons_cog.on_interaction(interaction)

    interaction.response.defer.assert_called_once()
    message = str(interaction.followup.send.call_args)
    assert "No Revomon found" in message


@pytest.mark.asyncio
@patch("utils.button_utils.land_intro")
@patch("utils.button_utils.OwnedLandsTable")
async def test_router_land_lookup(
    mock_owned: Any, mock_land_intro: Any, buttons_cog: Any
) -> None:
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

    interaction = _interaction("land:2")
    await buttons_cog.on_interaction(interaction)

    interaction.response.defer.assert_called_once()
    assert interaction.followup.send.call_args[1]["embed"] == "embed"


@pytest.mark.asyncio
@patch("utils.button_utils.OwnedLandsTable")
async def test_router_land_lookup_unknown(mock_owned: Any, buttons_cog: Any) -> None:
    mock_owned.return_value.get_info = AsyncMock(return_value=[])

    interaction = _interaction("land:99999")
    await buttons_cog.on_interaction(interaction)

    message = str(interaction.followup.send.call_args)
    assert "not found" in message


@pytest.mark.asyncio
@patch("utils.button_utils.OwnedLandsTable")
@patch("utils.button_utils.land_intro")
async def test_router_legacy_space_land_alias(
    mock_land_intro: Any, mock_owned: Any, buttons_cog: Any
) -> None:
    mock_owned.return_value.get_info = AsyncMock(
        return_value=[
            [
                1,
                2,
                "a",
                "forest",
                "plot",
                "rare",
                "small",
                "url",
                "e",
                True,
                "sym",
                "100",
                "1000",
            ]
        ]
    )
    mock_land_intro.return_value = "embed"

    interaction = _interaction("land 2")
    await buttons_cog.on_interaction(interaction)

    interaction.response.defer.assert_called_once()
    interaction.followup.send.assert_called_once()


@pytest.mark.asyncio
@patch("utils.button_utils.Buttons.mon_view")
async def test_router_mon_goto(mock_mon_view: Any, buttons_cog: Any) -> None:
    mock_mon_view.return_value = "view"

    interaction = _interaction("mon_page:goto:2")
    await buttons_cog.on_interaction(interaction)

    mock_mon_view.assert_awaited_once_with(user_id=123, page=2)
    interaction.response.defer.assert_called_once()
    interaction.followup.edit_message.assert_called_once_with(555, view="view")


@pytest.mark.asyncio
@patch("utils.button_utils.Buttons.land_view")
async def test_router_land_goto(mock_land_view: Any, buttons_cog: Any) -> None:
    mock_land_view.return_value = "view"

    interaction = _interaction("land_page:goto:3")
    await buttons_cog.on_interaction(interaction)

    mock_land_view.assert_awaited_once_with(user_id=123, page=3)
    interaction.followup.edit_message.assert_called_once_with(555, view="view")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "custom_id",
    [
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
    ],
)
async def test_router_legacy_pagers_expire(buttons_cog: Any, custom_id: str) -> None:
    interaction = _interaction(custom_id)
    await buttons_cog.on_interaction(interaction)

    interaction.response.send_message.assert_called_once()
    assert "expired" in str(interaction.response.send_message.call_args)
    assert interaction.response.send_message.call_args[1]["ephemeral"] is True
    interaction.followup.send.assert_not_called()


@pytest.mark.asyncio
async def test_router_unrecognized_custom_id_ignored(buttons_cog: Any) -> None:
    interaction = _interaction("some_foreign_button:id")
    await buttons_cog.on_interaction(interaction)

    interaction.response.defer.assert_not_called()
    interaction.response.send_message.assert_not_called()
    interaction.followup.send.assert_not_called()


@pytest.mark.asyncio
async def test_router_malformed_goto_page_ignored(buttons_cog: Any) -> None:
    interaction = _interaction("mon_page:goto:notanumber")
    await buttons_cog.on_interaction(interaction)

    interaction.response.defer.assert_not_called()
    interaction.response.send_message.assert_not_called()


@pytest.mark.asyncio
async def test_router_live_view_feature_ids_ignored(buttons_cog: Any) -> None:
    for custom_id in ("mon:share", "mon:search_sort", "land:search_sort"):
        interaction = _interaction(custom_id)
        await buttons_cog.on_interaction(interaction)

        interaction.response.defer.assert_not_called()
        interaction.response.send_message.assert_not_called()


@pytest.mark.asyncio
async def test_router_non_component_interaction_ignored(buttons_cog: Any) -> None:
    interaction = _interaction("mon:mon1")
    interaction.type = 1  # APPLICATION_COMMAND
    await buttons_cog.on_interaction(interaction)

    interaction.response.defer.assert_not_called()


@pytest.mark.asyncio
async def test_router_missing_custom_id_ignored(buttons_cog: Any) -> None:
    interaction = _interaction(None)
    interaction.data = {"id": "whatever"}
    await buttons_cog.on_interaction(interaction)

    interaction.response.defer.assert_not_called()


@pytest.mark.asyncio
async def test_router_custom_id_not_str_ignored(buttons_cog: Any) -> None:
    interaction = _interaction(None)
    interaction.data = {"custom_id": 12345}
    await buttons_cog.on_interaction(interaction)

    interaction.response.defer.assert_not_called()


@pytest.mark.asyncio
async def test_router_bot_user_ignored(buttons_cog: Any) -> None:
    interaction = _interaction("mon:mon1")
    interaction.user.bot = True
    await buttons_cog.on_interaction(interaction)

    interaction.response.defer.assert_not_called()


@pytest.mark.asyncio
@patch("utils.button_utils.get_attributes", new_callable=AsyncMock)
async def test_router_exception_swallowed(
    mock_get_attrs: Any, buttons_cog: Any
) -> None:
    mock_get_attrs.side_effect = Exception("boom")

    interaction = _interaction("mon:mon1")
    await buttons_cog.on_interaction(interaction)

    interaction.followup.send.assert_not_called()


# ------------------------------------------------- action-button router


@pytest.mark.asyncio
@patch("utils.button_utils.stats")
@patch("utils.button_utils.get_attributes", new_callable=AsyncMock)
async def test_router_action_stats(
    mock_get_attrs: Any, mock_stats: Any, buttons_cog: Any
) -> None:
    mock_get_attrs.return_value = {"name": "pikachu"}
    mock_stats.return_value = "embed"

    interaction = _interaction("action:stats:pikachu")
    await buttons_cog.on_interaction(interaction)

    interaction.response.defer.assert_called_once()
    kwargs = interaction.followup.send.call_args[1]
    assert kwargs["embed"] == "embed"
    assert kwargs["ephemeral"] is True


@pytest.mark.asyncio
@patch("utils.button_utils.get_attributes", new_callable=AsyncMock)
async def test_router_action_unknown_mon(mock_get_attrs: Any, buttons_cog: Any) -> None:
    mock_get_attrs.return_value = {}

    interaction = _interaction("action:moves:nosuchmon")
    await buttons_cog.on_interaction(interaction)

    message = str(interaction.followup.send.call_args)
    assert "No Revomon found" in message


@pytest.mark.asyncio
@patch("utils.button_utils.compare_types")
@patch("utils.button_utils.get_attributes", new_callable=AsyncMock)
async def test_router_action_compare_types_two_embeds(
    mock_get_attrs: Any, mock_compare: Any, buttons_cog: Any
) -> None:
    mock_get_attrs.side_effect = [{"name": "a"}, {"name": "b"}]
    mock_compare.return_value = ("embed1", "embed2")

    interaction = _interaction("action:compare_types:mona&monb")
    await buttons_cog.on_interaction(interaction)

    assert interaction.followup.send.call_count == 2
    assert interaction.followup.send.call_args_list[0][1]["embed"] == "embed1"


@pytest.mark.asyncio
@patch("utils.button_utils.get_attributes", new_callable=AsyncMock)
async def test_router_action_compare_unknown_second_mon(
    mock_get_attrs: Any, buttons_cog: Any
) -> None:
    mock_get_attrs.side_effect = [{"name": "a"}, {}]

    interaction = _interaction("action:compare_stats:good&bad")
    await buttons_cog.on_interaction(interaction)

    message = str(interaction.followup.send.call_args)
    assert "No Revomon found for 'bad'" in message


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "custom_id",
    [
        "action:stats",  # pre-router bare id: unrecoverable state
        "action:moves",
        "action:compare_spawns",
        "action:stats:",  # empty payload == truncated legacy id
    ],
)
async def test_router_bare_legacy_action_expires(
    buttons_cog: Any, custom_id: str
) -> None:
    interaction = _interaction(custom_id)
    await buttons_cog.on_interaction(interaction)

    assert "expired" in str(interaction.response.send_message.call_args)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "custom_id",
    [
        "action:warp:pikachu",  # unknown verb
        "action:stats:a&b",  # wrong arity for single-mon verb
        "action:compare_moves:onlyone",  # wrong arity for compare verb
    ],
)
async def test_router_malformed_action_ignored(
    buttons_cog: Any, custom_id: str
) -> None:
    interaction = _interaction(custom_id)
    await buttons_cog.on_interaction(interaction)

    interaction.response.defer.assert_not_called()
    interaction.response.send_message.assert_not_called()
    interaction.followup.send.assert_not_called()


@pytest.mark.asyncio
async def test_intro_view_encodes_names_in_custom_ids() -> None:
    view = IntroView(attributes={"name": "Pikachu"})
    ids = [getattr(child, "custom_id", None) for child in view.children]
    assert ids == [
        "action:stats:pikachu",
        "action:spawns:pikachu",
        "action:moves:pikachu",
        "action:types:pikachu",
        "action:counterdex:pikachu",
    ]


@pytest.mark.asyncio
async def test_compare_intro_view_encodes_both_names() -> None:
    view = CompareIntroView({"name": "MonA"}, {"name": "MonB"})
    ids = [getattr(child, "custom_id", None) for child in view.children]
    assert ids[0] == "action:compare_stats:mona&monb"
    assert all(isinstance(i, str) and i.endswith(":mona&monb") for i in ids)


@pytest.mark.asyncio
@patch("utils.button_utils.list_application_emojis", new_callable=AsyncMock)
async def test_mon_view_loads_book_and_clamps_page(
    mock_list_emojis: Any, buttons_cog: Any
) -> None:
    mock_list_emojis.return_value = []
    buttons_cog.book_of_names = [["mon1"], ["mon2"]]

    view = await buttons_cog.mon_view(user_id=123, page=99)
    assert view.current_page == 2

    view = await buttons_cog.mon_view(user_id=123, page=0)
    assert view.current_page == 1


@pytest.mark.asyncio
@patch("utils.button_utils.get_book_of_land_ids", new_callable=AsyncMock)
async def test_land_view_fetches_book_when_none(
    mock_get_book: Any, buttons_cog: Any
) -> None:
    mock_get_book.return_value = [[1, 2, 3]]

    view = await buttons_cog.land_view(user_id=123)
    assert len(view.children) > 0

    # token_ids provided -> book rebuilt through the fetcher
    view = await buttons_cog.land_view(user_id=124, token_ids=[7])
    assert len(view.children) > 0
    mock_get_book.assert_awaited_with(token_ids=[7])


@pytest.mark.asyncio
async def test_intro_view_returns_live_action_buttons(buttons_cog: Any) -> None:
    view = await buttons_cog.intro_view(attributes={"attr": 1})
    assert len(view.children) == 5


@pytest.mark.asyncio
async def test_compare_intros_view(buttons_cog: Any) -> None:
    view = await buttons_cog.compare_intros_view(
        attributes={"a": 1}, attributes2={"b": 2}
    )
    assert len(view.children) == 5
