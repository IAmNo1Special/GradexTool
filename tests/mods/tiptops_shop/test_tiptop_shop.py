from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import discord
import pytest
from discord.ext import commands

from mods.tiptops_shop.tiptop_shop import setup, tiptop_shop


@pytest.fixture
def mock_bot() -> Any:
    bot = AsyncMock(spec=commands.Bot)
    return bot


@pytest.fixture
def cog(mock_bot: Any) -> Any:
    return tiptop_shop(mock_bot)


@pytest.fixture
def mock_interaction() -> Any:
    interaction = AsyncMock(spec=discord.Interaction)
    interaction.response = AsyncMock()
    interaction.response.defer = AsyncMock()
    interaction.followup = AsyncMock()
    interaction.followup.send = AsyncMock()
    interaction.message = AsyncMock()
    interaction.message.delete = AsyncMock()
    return interaction


@pytest.fixture
def mock_button() -> Any:
    return MagicMock(spec=discord.ui.Button)


@pytest.mark.asyncio
async def test_setup(mock_bot: Any) -> None:
    await setup(mock_bot)
    mock_bot.add_cog.assert_called_once()
    assert isinstance(mock_bot.add_cog.call_args[0][0], tiptop_shop)


def test_tiptop_shop_intro_embed(cog: Any) -> None:
    embed = cog.tiptop_shop_intro_embed()
    assert isinstance(embed, discord.Embed)
    assert embed.title == "Tip: Welcome to Tiptop's Top-up Shop."
    assert embed.color == discord.Color.red()


@pytest.mark.asyncio
async def test_on_ready(cog: Any, capsys: Any) -> None:
    await cog.on_ready()
    captured = capsys.readouterr()
    assert "The Elder's Library(Revomon Search) is ready!" in captured.out
    assert "---------------------------" in captured.out


@pytest.mark.asyncio
@patch("mods.tiptops_shop.tiptop_shop.respond", new_callable=AsyncMock)
async def test_on_message(mock_respond: Any, cog: Any) -> None:
    # Test bot message ignored
    bot_msg = MagicMock(spec=discord.Message)
    bot_msg.author.bot = True
    await cog.on_message(bot_msg)
    mock_respond.assert_not_called()

    # Test "tiptop" prompt
    user_msg_tiptop = MagicMock(spec=discord.Message)
    user_msg_tiptop.author.bot = False
    user_msg_tiptop.content = " tiptop "
    await cog.on_message(user_msg_tiptop)
    mock_respond.assert_called_once()
    mock_respond.reset_mock()

    # Test "tip top" prompt
    user_msg_tip_top = MagicMock(spec=discord.Message)
    user_msg_tip_top.author.bot = False
    user_msg_tip_top.content = "tip top"
    await cog.on_message(user_msg_tip_top)
    mock_respond.assert_called_once()
    mock_respond.reset_mock()

    # Test unrelated prompt
    user_msg_other = MagicMock(spec=discord.Message)
    user_msg_other.author.bot = False
    user_msg_other.content = "hello"
    await cog.on_message(user_msg_other)
    mock_respond.assert_not_called()

    # Test exception handling in on_message
    with patch(
        "mods.tiptops_shop.tiptop_shop.tiptop_shop.tiptop_shop_intro_embed",
        side_effect=Exception("Test Exception"),
    ):
        user_msg_error = MagicMock(spec=discord.Message)
        user_msg_error.author.bot = False
        user_msg_error.content = "tiptop"
        # Should not raise exception
        await cog.on_message(user_msg_error)


# --- Test Button Classes ---


@pytest.mark.asyncio
async def test_intro_buttons_tiptop_nft_items(
    mock_interaction: Any, mock_button: Any
) -> None:
    view = tiptop_shop.tiptop_shop_intro_buttons()
    await view.tiptop_nft_items.callback(mock_interaction)
    mock_interaction.response.defer.assert_called_once()
    mock_interaction.followup.send.assert_called_once()
    kwargs = mock_interaction.followup.send.call_args[1]
    assert kwargs["ephemeral"] is True
    assert isinstance(kwargs["embed"], discord.Embed)
    assert isinstance(kwargs["view"], tiptop_shop.tiptop_shop_nft_items_buttons)


@pytest.mark.asyncio
async def test_intro_buttons_exit_embed(
    mock_interaction: Any, mock_button: Any
) -> None:
    view = tiptop_shop.tiptop_shop_intro_buttons()
    await view.exit_embed.callback(mock_interaction)
    mock_interaction.message.delete.assert_called_once()


@pytest.mark.asyncio
async def test_nft_items_buttons_tiptop_gradex_tool(
    mock_interaction: Any, mock_button: Any
) -> None:
    view = tiptop_shop.tiptop_shop_nft_items_buttons()
    await view.tiptop_gradex_tool.callback(mock_interaction)
    mock_interaction.response.defer.assert_called_once()
    mock_interaction.followup.send.assert_called_once()
    kwargs = mock_interaction.followup.send.call_args[1]
    assert kwargs["ephemeral"] is True
    assert isinstance(kwargs["embed"], discord.Embed)
    assert "view" not in kwargs


@pytest.mark.asyncio
async def test_nft_items_buttons_tiptop_6000_igc(
    mock_interaction: Any, mock_button: Any
) -> None:
    view = tiptop_shop.tiptop_shop_nft_items_buttons()
    await view.tiptop_6000_igc.callback(mock_interaction)
    mock_interaction.response.defer.assert_called_once()
    mock_interaction.followup.send.assert_called_once()
    kwargs = mock_interaction.followup.send.call_args[1]
    assert kwargs["ephemeral"] is True
    assert isinstance(kwargs["embed"], discord.Embed)
    assert isinstance(kwargs["view"], tiptop_shop.igc_6000_nft_buttons)


@pytest.mark.asyncio
async def test_nft_items_buttons_tiptop_60000_igc(
    mock_interaction: Any, mock_button: Any
) -> None:
    view = tiptop_shop.tiptop_shop_nft_items_buttons()
    await view.tiptop_60000_igc.callback(mock_interaction)
    mock_interaction.response.defer.assert_called_once()
    mock_interaction.followup.send.assert_called_once()
    kwargs = mock_interaction.followup.send.call_args[1]
    assert kwargs["ephemeral"] is True
    assert isinstance(kwargs["embed"], discord.Embed)
    assert isinstance(kwargs["view"], tiptop_shop.igc_60000_nft_buttons)


@pytest.mark.asyncio
async def test_nft_items_buttons_tiptop_120000_igc(
    mock_interaction: Any, mock_button: Any
) -> None:
    view = tiptop_shop.tiptop_shop_nft_items_buttons()
    await view.tiptop_120000_igc.callback(mock_interaction)
    mock_interaction.response.defer.assert_called_once()
    mock_interaction.followup.send.assert_called_once()
    kwargs = mock_interaction.followup.send.call_args[1]
    assert kwargs["ephemeral"] is True
    assert isinstance(kwargs["embed"], discord.Embed)
    assert isinstance(kwargs["view"], tiptop_shop.igc_120000_nft_buttons)


# --- 6000 IGC Buttons ---
@pytest.mark.asyncio
async def test_igc_6000_nft_buttons_redeem(
    mock_interaction: Any, mock_button: Any
) -> None:
    view = tiptop_shop.igc_6000_nft_buttons()
    await view.redeem_6000_igc.callback(mock_interaction)
    mock_interaction.response.defer.assert_called_once()
    mock_interaction.followup.send.assert_called_once()
    kwargs = mock_interaction.followup.send.call_args[1]
    assert kwargs["ephemeral"] is True
    assert isinstance(kwargs["embed"], discord.Embed)


@pytest.mark.asyncio
async def test_igc_6000_nft_buttons_buy_revo(
    mock_interaction: Any, mock_button: Any
) -> None:
    view = tiptop_shop.igc_6000_nft_buttons()
    await view.buy_6000_igc_revo.callback(mock_interaction)
    mock_interaction.response.defer.assert_called_once()
    mock_interaction.followup.send.assert_called_once()


@pytest.mark.asyncio
async def test_igc_6000_nft_buttons_buy_igc(
    mock_interaction: Any, mock_button: Any
) -> None:
    view = tiptop_shop.igc_6000_nft_buttons()
    await view.buy_6000_igc_igc.callback(mock_interaction)
    mock_interaction.response.defer.assert_called_once()
    mock_interaction.followup.send.assert_called_once()


# --- 60000 IGC Buttons ---
@pytest.mark.asyncio
async def test_igc_60000_nft_buttons_redeem(
    mock_interaction: Any, mock_button: Any
) -> None:
    view = tiptop_shop.igc_60000_nft_buttons()
    await view.redeem_60000_igc.callback(mock_interaction)
    mock_interaction.response.defer.assert_called_once()
    mock_interaction.followup.send.assert_called_once()


@pytest.mark.asyncio
async def test_igc_60000_nft_buttons_buy_revo(
    mock_interaction: Any, mock_button: Any
) -> None:
    view = tiptop_shop.igc_60000_nft_buttons()
    await view.buy_60000_igc_revo.callback(mock_interaction)
    mock_interaction.response.defer.assert_called_once()
    mock_interaction.followup.send.assert_called_once()


@pytest.mark.asyncio
async def test_igc_60000_nft_buttons_buy_igc(
    mock_interaction: Any, mock_button: Any
) -> None:
    view = tiptop_shop.igc_60000_nft_buttons()
    await view.buy_60000_igc_igc.callback(mock_interaction)
    mock_interaction.response.defer.assert_called_once()
    mock_interaction.followup.send.assert_called_once()


# --- 120000 IGC Buttons ---
@pytest.mark.asyncio
async def test_igc_120000_nft_buttons_redeem(
    mock_interaction: Any, mock_button: Any
) -> None:
    view = tiptop_shop.igc_120000_nft_buttons()
    await view.redeem_120000_igc.callback(mock_interaction)
    mock_interaction.response.defer.assert_called_once()
    mock_interaction.followup.send.assert_called_once()


@pytest.mark.asyncio
async def test_igc_120000_nft_buttons_buy_revo(
    mock_interaction: Any, mock_button: Any
) -> None:
    view = tiptop_shop.igc_120000_nft_buttons()
    await view.buy_120000_igc_revo.callback(mock_interaction)
    mock_interaction.response.defer.assert_called_once()
    mock_interaction.followup.send.assert_called_once()


@pytest.mark.asyncio
async def test_igc_120000_nft_buttons_buy_igc(
    mock_interaction: Any, mock_button: Any
) -> None:
    view = tiptop_shop.igc_120000_nft_buttons()
    await view.buy_120000_igc_igc.callback(mock_interaction)
    mock_interaction.response.defer.assert_called_once()
    mock_interaction.followup.send.assert_called_once()
