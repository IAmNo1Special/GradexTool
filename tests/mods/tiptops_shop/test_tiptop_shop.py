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
async def test_tiptop_command(cog: Any, mock_interaction: Any) -> None:
    await cog.tiptop.callback(cog, mock_interaction)
    mock_interaction.response.send_message.assert_called_once()
    kwargs = mock_interaction.response.send_message.call_args[1]
    assert kwargs["ephemeral"] is True
    assert isinstance(kwargs["embed"], discord.Embed)
    assert isinstance(kwargs["view"], tiptop_shop.tiptop_shop_intro_buttons)


@pytest.mark.asyncio
async def test_tiptop_command_exception(cog: Any, mock_interaction: Any) -> None:
    with patch.object(
        cog, "tiptop_shop_intro_embed", side_effect=Exception("Test Exception")
    ):
        # Should not raise exception
        await cog.tiptop.callback(cog, mock_interaction)
        mock_interaction.response.send_message.assert_not_called()


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
