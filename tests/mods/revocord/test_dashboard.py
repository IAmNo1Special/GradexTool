from typing import Any

"""Comprehensive tests for dashboard.py cog."""

from unittest.mock import AsyncMock, MagicMock  # noqa: E402

import discord  # noqa: E402
import pytest  # noqa: E402

from mods.revocord.dashboard import DashboardCog, DashboardView, setup  # noqa: E402


class TestDashboardViewInitialization:
    """Test suite for DashboardView initialization."""

    def test_dashboard_view_init(self) -> None:
        """Test DashboardView initialization."""
        view = DashboardView()

        assert isinstance(view, discord.ui.View)
        assert view.timeout is None  # Persistent view


class TestDashboardViewButtons:
    """Test suite for DashboardView buttons."""

    def test_profile_button_exists(self) -> None:
        """Test that profile button exists in the view."""
        view = DashboardView()

        profile_button = None
        for child in view.children:
            if hasattr(child, "custom_id") and "profile" in child.custom_id:
                profile_button = child
                break

        assert profile_button is not None
        assert hasattr(profile_button, "callback")

    def test_logout_button_exists(self) -> None:
        """Test that logout button exists in the view."""
        view = DashboardView()

        logout_button = None
        for child in view.children:
            if hasattr(child, "custom_id") and "logout" in child.custom_id:
                logout_button = child
                break

        assert logout_button is not None
        assert hasattr(logout_button, "callback")


class TestDashboardCog:
    """Test suite for DashboardCog."""

    def test_dashboard_cog_init(self, mock_bot: Any) -> None:
        """Test DashboardCog initialization."""
        cog = DashboardCog(mock_bot)

        assert cog.bot == mock_bot
        assert isinstance(cog, DashboardCog)

    def test_dashboard_cog_is_cog(self, mock_bot: Any) -> None:
        """Test that DashboardCog is a proper Discord Cog."""
        from discord.ext import commands

        cog = DashboardCog(mock_bot)
        assert isinstance(cog, commands.Cog)

    @pytest.mark.asyncio
    async def test_cog_load_registers_view(self, mock_bot: Any) -> None:
        """Test that cog_load registers the persistent view."""
        cog = DashboardCog(mock_bot)

        await cog.cog_load()

        mock_bot.add_view.assert_called_once()
        call_args = mock_bot.add_view.call_args
        view = call_args[0][0]
        assert isinstance(view, DashboardView)


class TestDashboardSetup:
    """Test suite for dashboard setup function."""

    @pytest.mark.asyncio
    async def test_setup_adds_cog(self, mock_bot: Any) -> None:
        """Test that setup function adds the cog to bot."""
        await setup(mock_bot)

        mock_bot.add_cog.assert_called_once()

        call_args = mock_bot.add_cog.call_args
        cog = call_args[0][0]
        assert isinstance(cog, DashboardCog)

    @pytest.mark.asyncio
    async def test_setup_handles_exception(self, mock_bot: Any) -> None:
        """Test that setup handles exceptions gracefully."""
        mock_bot.add_cog = AsyncMock(side_effect=Exception("Setup error"))

        await setup(mock_bot)

        mock_bot.add_cog.assert_called_once()


class TestDashboardIntegration:
    """Integration tests for dashboard system."""

    @pytest.mark.asyncio
    async def test_full_dashboard_lifecycle(self, mock_bot: Any) -> None:
        """Test full dashboard lifecycle: setup -> cog_load."""
        await setup(mock_bot)

        cog = DashboardCog(mock_bot)
        await cog.cog_load()

        # Verify setup was called
        mock_bot.add_cog.assert_called_once()

        # Verify view was registered
        mock_bot.add_view.assert_called_once()


# Note: Complex button callback tests have been simplified to avoid
# Discord library dependencies and account file mocking issues.
# The structural tests provide good coverage of the dashboard functionality.

from unittest.mock import patch  # noqa: E402


class TestDashboardViewCallbacks:
    """Test suite for DashboardView callbacks."""

    @pytest.mark.asyncio
    @patch("mods.revocord.dashboard.get_or_create_account")
    @patch("mods.revocord.dashboard.build_text_view")
    async def test_profile_callback(
        self, mock_build: Any, mock_get_account: Any, mock_interaction: Any
    ) -> None:
        view = DashboardView()

        profile_button = [
            x
            for x in view.children
            if getattr(x, "custom_id", "") == "persistent_dashboard_profile"
        ][0]

        mock_get_account.return_value = {
            "trainer_level": 5,
            "trainer_xp": 50,
            "coins": 1000,
            "rank": "Veteran",
            "energy": 80,
            "max_energy": 100,
            "current_city": "drassius city",
            "current_location": "wilds",
            "battles_won": 10,
            "battles_lost": 2,
            "inventory": {"159": 1, "4": 2, "31": 3},
            "caught_revomon": [{"name": "testmon", "level": 5, "is_shiny": True}] * 7,
        }
        mock_build.return_value = "mocked_view"

        await profile_button.callback(mock_interaction)

        mock_interaction.response.defer.assert_called_once_with(ephemeral=True)
        mock_get_account.assert_called_once_with(mock_interaction.user.id)
        mock_build.assert_called_once()
        mock_interaction.followup.send.assert_called_once_with(
            view="mocked_view", ephemeral=True
        )

    @pytest.mark.asyncio
    @patch("mods.revocord.dashboard.get_or_create_account")
    async def test_profile_callback_no_orbs_no_caught(
        self, mock_get_account: Any, mock_interaction: Any
    ) -> None:
        view = DashboardView()
        profile_button = [
            x
            for x in view.children
            if getattr(x, "custom_id", "") == "persistent_dashboard_profile"
        ][0]

        mock_get_account.return_value = {}

        await profile_button.callback(mock_interaction)

        mock_interaction.followup.send.assert_called_once()

    @pytest.mark.asyncio
    @patch("mods.revocord.dashboard.get_or_create_account")
    @patch("mods.revocord.dashboard.logger")
    async def test_profile_callback_exception(
        self, mock_logger: Any, mock_get_account: Any, mock_interaction: Any
    ) -> None:
        view = DashboardView()
        profile_button = [
            x
            for x in view.children
            if getattr(x, "custom_id", "") == "persistent_dashboard_profile"
        ][0]

        mock_get_account.side_effect = Exception("Test Error")

        await profile_button.callback(mock_interaction)

        mock_interaction.followup.send.assert_called_with(
            "❌ An error occurred loading your profile: Test Error", ephemeral=True
        )
        mock_logger.error.assert_called_once()

    @pytest.mark.asyncio
    @patch("mods.revocord.dashboard.update_account")
    async def test_logout_callback(
        self, mock_update: Any, mock_interaction: Any
    ) -> None:
        view = DashboardView()
        logout_button = [
            x
            for x in view.children
            if getattr(x, "custom_id", "") == "persistent_dashboard_logout"
        ][0]

        mock_category = MagicMock()
        mock_portal = MagicMock(name="portal")
        mock_portal.name = "portal"
        mock_portal.set_permissions = AsyncMock()
        mock_other = MagicMock(name="other")
        mock_other.name = "other"
        mock_other.set_permissions = AsyncMock()
        mock_category.channels = [mock_portal, mock_other]

        mock_channel = MagicMock(spec=discord.TextChannel)
        mock_channel.category = mock_category
        mock_interaction.channel = mock_channel

        await logout_button.callback(mock_interaction)

        mock_update.assert_called_once_with(
            mock_interaction.user.id, is_logged_in=False
        )
        mock_portal.set_permissions.assert_called_once_with(
            mock_interaction.user, overwrite=None
        )
        mock_other.set_permissions.assert_called_once_with(
            mock_interaction.user, overwrite=None
        )
        mock_interaction.followup.send.assert_called_with(
            "✅ You have successfully logged out. You can return via the portal.",
            ephemeral=True,
        )

    @pytest.mark.asyncio
    @patch("mods.revocord.dashboard.update_account")
    async def test_logout_callback_no_category(
        self, mock_update: Any, mock_interaction: Any
    ) -> None:
        view = DashboardView()
        logout_button = [
            x
            for x in view.children
            if getattr(x, "custom_id", "") == "persistent_dashboard_logout"
        ][0]

        mock_interaction.channel = None

        await logout_button.callback(mock_interaction)

        mock_interaction.followup.send.assert_called_with(
            "❌ Error: Workspace structure not found.", ephemeral=True
        )

    @pytest.mark.asyncio
    @patch("mods.revocord.dashboard.update_account")
    async def test_logout_callback_forbidden(
        self, mock_update: Any, mock_interaction: Any
    ) -> None:
        view = DashboardView()
        logout_button = [
            x
            for x in view.children
            if getattr(x, "custom_id", "") == "persistent_dashboard_logout"
        ][0]

        mock_category = MagicMock()
        mock_portal = MagicMock(name="portal")
        mock_portal.name = "portal"
        mock_portal.set_permissions = AsyncMock(
            side_effect=discord.Forbidden(MagicMock(), "")
        )
        mock_category.channels = [mock_portal]

        mock_channel = MagicMock(spec=discord.TextChannel)
        mock_channel.category = mock_category
        mock_interaction.channel = mock_channel

        await logout_button.callback(mock_interaction)

        mock_interaction.followup.send.assert_called_with(
            "❌ Error: I don't have permissions to update your access.", ephemeral=True
        )

    @pytest.mark.asyncio
    @patch("mods.revocord.dashboard.update_account")
    @patch("mods.revocord.dashboard.logger")
    async def test_logout_callback_exception(
        self, mock_logger: Any, mock_update: Any, mock_interaction: Any
    ) -> None:
        view = DashboardView()
        logout_button = [
            x
            for x in view.children
            if getattr(x, "custom_id", "") == "persistent_dashboard_logout"
        ][0]

        mock_update.side_effect = Exception("Test Error")

        mock_category = MagicMock()
        mock_channel = MagicMock(spec=discord.TextChannel)
        mock_channel.category = mock_category
        mock_interaction.channel = mock_channel

        await logout_button.callback(mock_interaction)

        mock_interaction.followup.send.assert_called_with(
            "❌ An unexpected error occurred: Test Error", ephemeral=True
        )
        mock_logger.error.assert_called_once()
