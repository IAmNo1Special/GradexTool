from typing import Any
"""Comprehensive tests for activity.py cog."""

import sys
import time
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch, PropertyMock

import pytest
import discord



from mods.revocord.activity import (
    TravelButtonView,
    ShopSelect,
    ShopSelectView,
    RestButtonView,
    RouteAITrainerView,
)


class TestTravelButtonViewInitialization:
    """Test suite for TravelButtonView initialization."""

    def test_travel_button_view_init(self) -> None:
        """Test TravelButtonView initialization."""
        view = TravelButtonView()
        
        assert isinstance(view, discord.ui.View)
        assert view.timeout is None  # Persistent view


class TestTravelButtonViewButtons:
    """Test suite for TravelButtonView buttons."""

    def test_hunt_button_exists(self) -> None:
        """Test that hunt button exists in the view."""
        view = TravelButtonView()
        
        hunt_button = None
        for child in view.children:
            if hasattr(child, 'custom_id') and 'hunt' in child.custom_id:
                hunt_button = child
                break
        
        assert hunt_button is not None
        assert hasattr(hunt_button, 'callback')


class TestShopSelectInitialization:
    """Test suite for ShopSelect initialization."""

    def test_shop_select_init(self) -> None:
        """Test ShopSelect initialization."""
        select = ShopSelect()
        
        assert len(select.options) == 3  # Red, Blue, Green orbs
        assert select.min_values == 1
        assert select.max_values == 1
        assert select.placeholder == "Select an Orb to buy..."


class TestShopSelectOptions:
    """Test suite for ShopSelect options."""

    def test_shop_select_red_orb_option(self) -> None:
        """Test that Red Orb option is configured correctly."""
        select = ShopSelect()
        red_option = select.options[0]
        
        assert red_option.label == "Red Orb"
        assert red_option.value == "159"
        assert red_option.description and "1.0x" in red_option.description
        assert red_option.emoji and red_option.emoji.name == "🔴"

    def test_shop_select_blue_orb_option(self) -> None:
        """Test that Blue Orb option is configured correctly."""
        select = ShopSelect()
        blue_option = select.options[1]
        
        assert blue_option.label == "Blue Orb"
        assert blue_option.value == "4"
        assert blue_option.description and "1.5x" in blue_option.description
        assert blue_option.emoji and blue_option.emoji.name == "🔵"

    def test_shop_select_green_orb_option(self) -> None:
        """Test that Green Orb option is configured correctly."""
        select = ShopSelect()
        green_option = select.options[2]
        
        assert green_option.label == "Green Orb"
        assert green_option.value == "31"
        assert green_option.description and "2.0x" in green_option.description
        assert green_option.emoji and green_option.emoji.name == "🟢"


class TestShopSelectCallback:
    """Test suite for ShopSelect callback."""

    def test_shop_select_callback_exists(self) -> None:
        """Test that shop select callback exists."""
        select = ShopSelect()
        assert hasattr(select, 'callback')
        assert callable(select.callback)


class TestShopSelectView:
    """Test suite for ShopSelectView."""

    def test_shop_select_view_init(self) -> None:
        """Test ShopSelectView initialization."""
        view = ShopSelectView()
        
        assert isinstance(view, discord.ui.View)
        assert view.timeout == 180  # 3 minutes

    def test_shop_select_view_contains_select(self) -> None:
        """Test that ShopSelectView contains the select menu."""
        view = ShopSelectView()
        
        assert len(view.children) == 1
        assert isinstance(view.children[0], ShopSelect)


class TestRestButtonViewInitialization:
    """Test suite for RestButtonView initialization."""

    def test_rest_button_view_init(self) -> None:
        """Test RestButtonView initialization."""
        view = RestButtonView()
        
        assert isinstance(view, discord.ui.View)
        assert view.timeout is None  # Persistent view


class TestRestButtonViewButtons:
    """Test suite for RestButtonView buttons."""

    def test_rest_button_exists(self) -> None:
        """Test that rest button exists in the view."""
        view = RestButtonView()
        
        rest_button = None
        for child in view.children:
            if hasattr(child, 'custom_id') and 'rest' in child.custom_id:
                rest_button = child
                break
        
        assert rest_button is not None
        assert hasattr(rest_button, 'callback')

    def test_shop_button_exists(self) -> None:
        """Test that shop button exists in the view."""
        view = RestButtonView()
        
        shop_button = None
        for child in view.children:
            if hasattr(child, 'custom_id') and 'shop' in child.custom_id:
                shop_button = child
                break
        
        assert shop_button is not None
        assert hasattr(shop_button, 'callback')


class TestRouteAITrainerViewInitialization:
    """Test suite for RouteAITrainerView initialization."""

    def test_route_ai_trainer_view_init(self) -> None:
        """Test RouteAITrainerView initialization."""
        view = RouteAITrainerView()
        
        assert isinstance(view, discord.ui.View)
        assert view.timeout is None  # Persistent view


class TestRouteAITrainerViewButtons:
    """Test suite for RouteAITrainerView buttons."""

    def test_battle_button_exists(self) -> None:
        """Test that battle button exists in the view."""
        view = RouteAITrainerView()
        
        battle_button = None
        for child in view.children:
            if hasattr(child, 'custom_id') and 'battle' in child.custom_id:
                battle_button = child
                break
        
        assert battle_button is not None
        assert hasattr(battle_button, 'callback')


class TestActivityViewIntegration:
    """Integration tests for activity views."""

    def test_view_compatibility(self) -> None:
        """Test that all views are compatible with Discord UI framework."""
        views_to_test = [
            TravelButtonView(),
            ShopSelectView(),
            RestButtonView(),
            RouteAITrainerView(),
        ]
        
        for view in views_to_test:
            assert hasattr(view, 'children')
            assert isinstance(view, discord.ui.View)

    def test_all_views_have_required_components(self) -> None:
        """Test that all views have the required UI components."""
        views_to_test = [
            (TravelButtonView(), 1),  # Should have 2 buttons
            (ShopSelectView(), 1),    # Should have 1 select
            (RestButtonView(), 2),    # Should have 2 buttons
            (RouteAITrainerView(), 1), # Should have 2 buttons
        ]
        
        for view, expected_children in views_to_test:
            assert len(view.children) == expected_children


class TestTravelButtonViewCallbacks:
    """Test suite for TravelButtonView callbacks."""

    @pytest.mark.asyncio
    async def test_hunt_button_no_cog(self, mock_interaction: Any) -> None:
        view = TravelButtonView()
        mock_interaction.client.get_cog = MagicMock(return_value=None)
        
        button = [x for x in view.children if getattr(x, "custom_id", "") == "persistent_hunt_button"][0]
        await button.callback(mock_interaction)
        
        mock_interaction.response.defer.assert_called_once()
        mock_interaction.followup.send.assert_called_once_with(
            "❌ Hunting system is currently unavailable. Try again later.",
            ephemeral=True,
        )

    @pytest.mark.asyncio
    async def test_hunt_button_with_cog(self, mock_interaction: Any) -> None:
        view = TravelButtonView()
        mock_cog = MagicMock()
        mock_cog.spawn_wild_revomon = AsyncMock()
        mock_interaction.client.get_cog = MagicMock(return_value=mock_cog)
        
        button = [x for x in view.children if getattr(x, "custom_id", "") == "persistent_hunt_button"][0]
        await button.callback(mock_interaction)
        
        mock_interaction.response.defer.assert_called_once()
        mock_cog.spawn_wild_revomon.assert_called_once_with(mock_interaction)




class TestShopSelectCallbackLogic:
    """Test suite for ShopSelect callback logic."""

    @pytest.mark.asyncio
    async def test_shop_select_invalid_orb(self, mock_interaction: Any) -> None:
        select = ShopSelect()
        with patch.object(ShopSelect, "values", new_callable=PropertyMock, return_value=["999"]):
            await select.callback(mock_interaction)
            
            mock_interaction.response.defer.assert_called_once_with(ephemeral=True)
            mock_interaction.followup.send.assert_called_once_with("❌ Invalid selection.", ephemeral=True)

    @pytest.mark.asyncio
    @patch("mods.revocord.activity.get_or_create_account")
    async def test_shop_select_insufficient_funds(self, mock_get_account: Any, mock_interaction: Any) -> None:
        select = ShopSelect()
        mock_get_account.return_value = {"coins": 50}
        
        with patch.object(ShopSelect, "values", new_callable=PropertyMock, return_value=["159"]):
            await select.callback(mock_interaction)
            
            mock_interaction.followup.send.assert_called_once()
            args, kwargs = mock_interaction.followup.send.call_args
            assert "not have enough RevoCoins" in args[0]

    @pytest.mark.asyncio
    @patch("mods.revocord.activity.get_or_create_account")
    @patch("mods.revocord.activity.update_account")
    async def test_shop_select_success(self, mock_update: Any, mock_get_account: Any, mock_interaction: Any) -> None:
        select = ShopSelect()
        mock_get_account.return_value = {"coins": 500, "inventory": {"159": 1}}
        
        with patch.object(ShopSelect, "values", new_callable=PropertyMock, return_value=["159"]):
            await select.callback(mock_interaction)
            
            mock_update.assert_called_once_with(
                mock_interaction.user.id,
                coins=300,
                inventory={"159": 2}
            )
            mock_interaction.followup.send.assert_called_once()
            args, kwargs = mock_interaction.followup.send.call_args
            assert "Success!" in args[0]


class TestRestButtonViewCallbacks:
    """Test suite for RestButtonView callbacks."""

    @pytest.mark.asyncio
    @patch("mods.revocord.activity.get_or_create_account")
    async def test_rest_button_already_full(self, mock_get_account: Any, mock_interaction: Any) -> None:
        view = RestButtonView()
        mock_get_account.return_value = {"energy": 100, "max_energy": 100}
        
        button = [x for x in view.children if getattr(x, "custom_id", "") == "persistent_rest_button"][0]
        await button.callback(mock_interaction)
        
        mock_interaction.followup.send.assert_called_once_with("You are already fully rested!", ephemeral=True)

    @pytest.mark.asyncio
    @patch("mods.revocord.activity.get_or_create_account")
    @patch("mods.revocord.activity.update_account")
    async def test_rest_button_success(self, mock_update: Any, mock_get_account: Any, mock_interaction: Any) -> None:
        view = RestButtonView()
        mock_get_account.return_value = {"energy": 50, "max_energy": 100}
        
        button = [x for x in view.children if getattr(x, "custom_id", "") == "persistent_rest_button"][0]
        await button.callback(mock_interaction)
        
        mock_update.assert_called_once_with(mock_interaction.user.id, energy=100)
        mock_interaction.followup.send.assert_called_once()
        args, kwargs = mock_interaction.followup.send.call_args
        assert "restored your energy" in args[0]

    @pytest.mark.asyncio
    @patch("mods.revocord.activity.get_or_create_account")
    async def test_shop_button(self, mock_get_account: Any, mock_interaction: Any) -> None:
        view = RestButtonView()
        mock_get_account.return_value = {"coins": 1000}
        
        button = [x for x in view.children if getattr(x, "custom_id", "") == "persistent_shop_button"][0]
        await button.callback(mock_interaction)
        
        mock_interaction.response.send_message.assert_called_once()
        args, kwargs = mock_interaction.response.send_message.call_args
        assert isinstance(kwargs["embed"], discord.Embed)
        assert isinstance(kwargs["view"], ShopSelectView)
        assert kwargs["ephemeral"] is True


class TestRouteAITrainerViewCallbacks:
    """Test suite for RouteAITrainerView callbacks."""

    @pytest.mark.asyncio
    async def test_battle_button(self, mock_interaction: Any) -> None:
        view = RouteAITrainerView()
        button = [x for x in view.children if getattr(x, "custom_id", "") == "persistent_battle_button"][0]
        
        await button.callback(mock_interaction)
        mock_interaction.response.send_message.assert_called_once_with(
            "The Battle system is not yet implemented! 🚧", ephemeral=True
        )




class TestActivityCog:
    """Test suite for ActivityCog."""

    @pytest.mark.asyncio
    async def test_cog_load(self, mock_bot: Any) -> None:
        from mods.revocord.activity import ActivityCog
        cog = ActivityCog(mock_bot)
        
        await cog.cog_load()
        assert mock_bot.add_view.call_count == 3

    @pytest.mark.asyncio
    async def test_setup(self, mock_bot: Any) -> None:
        from mods.revocord.activity import setup
        await setup(mock_bot)
        mock_bot.add_cog.assert_called_once()
