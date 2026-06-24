from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import discord
import pytest
from discord.ext import commands

from mods.revocord.portal import (
    GameConsoleView,
    PortalCog,
    PortalLoginView,
    build_console_embed,
    setup,
)


class TestPortalLoginViewInitialization:
    def test_portal_login_view_init(self) -> None:
        view = PortalLoginView()
        assert isinstance(view, discord.ui.View)
        assert view.timeout is None


class TestPortalLoginViewButtons:
    @pytest.mark.asyncio
    async def test_portal_login_not_member(self) -> None:
        view = PortalLoginView()
        mock_interaction = MagicMock(spec=discord.Interaction)
        mock_interaction.response.defer = AsyncMock()
        mock_interaction.user = "not a member"

        button = view.children[0]
        await button.callback(mock_interaction)

        mock_interaction.response.defer.assert_called_once()
        mock_interaction.followup.send.assert_not_called()

    def test_login_button_exists(self) -> None:
        view = PortalLoginView()
        login_button = next(
            (
                child
                for child in view.children
                if getattr(child, "custom_id", "") == "persistent_portal_login"
            ),
            None,
        )
        assert login_button is not None
        assert hasattr(login_button, "callback")


class TestPortalCog:
    def test_portal_cog_init(self, mock_bot: Any) -> None:
        cog = PortalCog(mock_bot)
        assert cog.bot == mock_bot
        assert isinstance(cog, PortalCog)

    def test_portal_cog_is_cog(self, mock_bot: Any) -> None:
        cog = PortalCog(mock_bot)
        assert isinstance(cog, commands.Cog)

    @pytest.mark.asyncio
    async def test_cog_load_registers_views(self, mock_bot: Any) -> None:
        cog = PortalCog(mock_bot)
        await cog.cog_load()
        assert mock_bot.add_view.call_count == 1


class TestPortalSetup:
    @pytest.mark.asyncio
    async def test_setup_adds_cog(self, mock_bot: Any) -> None:
        await setup(mock_bot)
        mock_bot.add_cog.assert_called_once()
        call_args = mock_bot.add_cog.call_args
        cog = call_args[0][0]
        assert isinstance(cog, PortalCog)

    @pytest.mark.asyncio
    async def test_setup_handles_exception(self, mock_bot: Any) -> None:
        mock_bot.add_cog = AsyncMock(side_effect=Exception("Setup error"))
        await setup(mock_bot)
        mock_bot.add_cog.assert_called_once()


class TestPortalIntegration:
    @pytest.mark.asyncio
    async def test_full_portal_lifecycle(self, mock_bot: Any) -> None:
        await setup(mock_bot)
        cog = PortalCog(mock_bot)
        await cog.cog_load()
        mock_bot.add_cog.assert_called_once()
        assert mock_bot.add_view.call_count == 1


class TestPortalViewCallbacks:
    @pytest.mark.asyncio
    @patch("mods.revocord.portal.get_or_create_account")
    @patch("mods.revocord.portal.update_account")
    @patch("mods.revocord.portal.build_console_embed")
    async def test_login_callback(
        self,
        mock_build_embed: Any,
        mock_update: Any,
        mock_get_account: Any,
        mock_interaction: Any,
    ) -> None:
        view = PortalLoginView()
        login_button = next(
            child
            for child in view.children
            if getattr(child, "custom_id", "") == "persistent_portal_login"
        )

        mock_get_account.return_value = {"trainer_level": 5}
        mock_update.return_value = {"trainer_level": 5, "is_logged_in": True}
        mock_embed = MagicMock(spec=discord.Embed)
        mock_build_embed.return_value = mock_embed

        await login_button.callback(mock_interaction)

        mock_interaction.response.defer.assert_called_once_with(ephemeral=True)
        mock_update.assert_called_once_with(mock_interaction.user.id, is_logged_in=True)
        mock_interaction.followup.send.assert_called_once()

        kwargs = mock_interaction.followup.send.call_args[1]
        assert kwargs["embed"] == mock_embed
        assert isinstance(kwargs["view"], GameConsoleView)
        assert kwargs["ephemeral"] is True

    @pytest.mark.asyncio
    @patch("mods.revocord.portal.get_or_create_account")
    async def test_login_callback_exception(
        self, mock_get_account: Any, mock_interaction: Any
    ) -> None:
        view = PortalLoginView()
        login_button = next(
            child
            for child in view.children
            if getattr(child, "custom_id", "") == "persistent_portal_login"
        )

        mock_get_account.side_effect = Exception("Database error")

        await login_button.callback(mock_interaction)

        mock_interaction.followup.send.assert_called_once()
        assert "Database error" in mock_interaction.followup.send.call_args[0][0]


class TestGameConsoleView:
    @pytest.mark.asyncio
    async def test_bag_button(self, mock_interaction: Any) -> None:
        view = GameConsoleView(123)
        bag_button = next(
            child
            for child in view.children
            if getattr(child, "custom_id", "") == "console_bag"
        )

        await bag_button.callback(mock_interaction)
        mock_interaction.response.defer.assert_called_once()

    @pytest.mark.asyncio
    async def test_heal_button(self, mock_interaction: Any) -> None:
        view = GameConsoleView(123)
        heal_button = next(
            child
            for child in view.children
            if getattr(child, "custom_id", "") == "console_heal"
        )

        await heal_button.callback(mock_interaction)
        mock_interaction.response.defer.assert_called_once()

    @pytest.mark.asyncio
    async def test_tv_button_wrong_user(self, mock_interaction: Any) -> None:
        view = GameConsoleView(123)
        tv_button = next(
            child
            for child in view.children
            if getattr(child, "custom_id", "") == "console_tv"
        )

        mock_interaction.user.id = 999
        await tv_button.callback(mock_interaction)
        mock_interaction.response.send_message.assert_called_once()
        assert (
            "❌ You cannot access someone else's Console!"
            in mock_interaction.response.send_message.call_args[0][0]
        )

    @pytest.mark.asyncio
    @patch("mods.revocord.shared.get_or_create_account")
    @patch("mods.revocord.tv.build_tv_embed")
    @patch("mods.revocord.tv.TVView")
    async def test_tv_button_success(
        self,
        mock_tv_view_cls: Any,
        mock_build_embed: Any,
        mock_get_account: Any,
        mock_interaction: Any,
    ) -> None:
        view = GameConsoleView(123)
        tv_button = next(
            child
            for child in view.children
            if getattr(child, "custom_id", "") == "console_tv"
        )

        mock_interaction.user.id = 123
        mock_get_account.return_value = {"caught_revomon": []}

        mock_tv_view = MagicMock()
        mock_tv_view.build_buttons = AsyncMock()
        mock_tv_view_cls.return_value = mock_tv_view

        mock_embed = MagicMock()
        mock_build_embed.return_value = mock_embed

        await tv_button.callback(mock_interaction)

        mock_interaction.response.defer.assert_called_once()
        mock_get_account.assert_called_once_with(123)
        mock_tv_view.build_buttons.assert_called_once()
        mock_interaction.edit_original_response.assert_called_once_with(
            embed=mock_embed, view=mock_tv_view, attachments=[]
        )


class TestBuildConsoleEmbed:
    @pytest.mark.asyncio
    async def test_build_console_embed(self) -> None:
        mock_member = MagicMock(spec=discord.Member)
        mock_member.display_name = "TestUser"

        account = {
            "trainer_level": 5,
            "trainer_xp": 50,
            "coins": 100,
            "rank": "Veteran",
            "energy": 80,
            "max_energy": 120,
            "current_city": "drassius city",
            "inventory": {"159": 5, "4": 2, "31": 0},
        }

        embed = await build_console_embed(account, mock_member)

        assert isinstance(embed, discord.Embed)
        assert embed.title is not None and "TESTUSER" in embed.title
        assert embed.description is not None and "Drassius City" in embed.description

        fields = {f.name: f.value for f in embed.fields if f.name is not None}
        assert "Level & Rank" in fields
        assert (
            fields["Level & Rank"] is not None and "Veteran" in fields["Level & Rank"]
        )

        assert "Wealth" in fields
        assert fields["Wealth"] is not None and "100" in fields["Wealth"]

        assert "Stats" in fields
        assert fields["Stats"] is not None and "50%" in fields["Stats"]
        assert fields["Stats"] is not None and "80/120" in fields["Stats"]

        assert "Bag (Quick Look)" in fields
        assert (
            fields["Bag (Quick Look)"] is not None
            and "Red x5" in fields["Bag (Quick Look)"]
        )
        assert (
            fields["Bag (Quick Look)"] is not None
            and "Blue x2" in fields["Bag (Quick Look)"]
        )
        assert (
            fields["Bag (Quick Look)"] is not None
            and "Green" not in fields["Bag (Quick Look)"]
        )
