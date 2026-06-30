from typing import Any

"""Comprehensive tests for helpers module."""

from unittest.mock import AsyncMock, MagicMock, patch  # noqa: E402

import discord  # noqa: E402
import pytest  # noqa: E402

from utils.helpers import (  # noqa: E402
    is_pro_tamer,
    respond,
    user_check,
)


class TestIsProTamer:
    """Test cases for the is_pro_tamer function."""

    def test_is_pro_tamer_with_pro_role(self, mock_bot: Any) -> None:
        """Test that is_pro_tamer returns True when user has pro role."""
        # Create mock guild
        mock_guild = MagicMock(spec=discord.Guild)
        mock_guild.id = 123456789

        # Create mock member with pro role
        mock_member = MagicMock(spec=discord.Member)
        mock_member.id = 987654321
        mock_member.roles = [MagicMock(id=111222333)]  # Pro role ID

        mock_guild.get_member.return_value = mock_member
        mock_bot.get_guild.return_value = mock_guild

        # Mock the config to include the role ID
        with patch("utils.helpers.GRA_PRO_TAMER_ROLE_IDS", [111222333]):
            with patch("utils.helpers.GRA_GUILD_ID", 123456789):
                result = is_pro_tamer(mock_bot, mock_member)
                assert result is True

    def test_is_pro_tamer_without_pro_role(self, mock_bot: Any) -> None:
        """Test that is_pro_tamer returns False when user lacks pro role."""
        # Create mock guild
        mock_guild = MagicMock(spec=discord.Guild)
        mock_guild.id = 123456789

        # Create mock member without pro role
        mock_member = MagicMock(spec=discord.Member)
        mock_member.id = 987654321
        mock_member.roles = [MagicMock(id=999888777)]  # Non-pro role ID

        mock_guild.get_member.return_value = mock_member
        mock_bot.get_guild.return_value = mock_guild

        # Mock the config to not include the role ID
        with patch("utils.helpers.GRA_PRO_TAMER_ROLE_IDS", [111222333]):
            with patch("utils.helpers.GRA_GUILD_ID", 123456789):
                result = is_pro_tamer(mock_bot, mock_member)
                assert result is False

    def test_is_pro_tamer_guild_not_found(self, mock_bot: Any) -> None:
        """Test that is_pro_tamer returns False when guild is not found."""
        mock_member = MagicMock(spec=discord.Member)
        mock_member.id = 987654321

        mock_bot.get_guild.return_value = None

        with patch("utils.helpers.GRA_GUILD_ID", 123456789):
            result = is_pro_tamer(mock_bot, mock_member)
            assert result is False

    def test_is_pro_tamer_member_not_in_guild(self, mock_bot: Any) -> None:
        """Test that is_pro_tamer returns False when member is not in guild."""
        # Create mock guild
        mock_guild = MagicMock(spec=discord.Guild)
        mock_guild.id = 123456789

        # Create mock member
        mock_member = MagicMock(spec=discord.Member)
        mock_member.id = 987654321

        mock_guild.get_member.return_value = None
        mock_bot.get_guild.return_value = mock_guild

        with patch("utils.helpers.GRA_GUILD_ID", 123456789):
            result = is_pro_tamer(mock_bot, mock_member)
            assert result is False

    def test_is_pro_tamer_with_multiple_pro_roles(self, mock_bot: Any) -> None:
        """Test that is_pro_tamer returns True with multiple pro role IDs."""
        # Create mock guild
        mock_guild = MagicMock(spec=discord.Guild)
        mock_guild.id = 123456789

        # Create mock member with second pro role
        mock_member = MagicMock(spec=discord.Member)
        mock_member.id = 987654321
        mock_member.roles = [MagicMock(id=222333444)]  # Second pro role ID

        mock_guild.get_member.return_value = mock_member
        mock_bot.get_guild.return_value = mock_guild

        # Mock the config to include multiple pro role IDs
        with patch("utils.helpers.GRA_PRO_TAMER_ROLE_IDS", [111222333, 222333444]):
            with patch("utils.helpers.GRA_GUILD_ID", 123456789):
                result = is_pro_tamer(mock_bot, mock_member)
                assert result is True

    def test_is_pro_tamer_with_no_roles(self, mock_bot: Any) -> None:
        """Test that is_pro_tamer returns False when user has no roles."""
        # Create mock guild
        mock_guild = MagicMock(spec=discord.Guild)
        mock_guild.id = 123456789

        # Create mock member with no roles
        mock_member = MagicMock(spec=discord.Member)
        mock_member.id = 987654321
        mock_member.roles = []

        mock_guild.get_member.return_value = mock_member
        mock_bot.get_guild.return_value = mock_guild

        with patch("utils.helpers.GRA_PRO_TAMER_ROLE_IDS", [111222333]):
            with patch("utils.helpers.GRA_GUILD_ID", 123456789):
                result = is_pro_tamer(mock_bot, mock_member)
                assert result is False


class TestUserCheck:
    """Test cases for the user_check function."""

    @pytest.mark.asyncio
    async def test_user_check_new_user_pro_status(self, mock_bot: Any) -> None:
        """Test user_check adds new user with pro status."""
        # Create mock member
        mock_member = MagicMock(spec=discord.Member)
        mock_member.id = 987654321
        mock_member.name = "TestUser"

        # Mock database
        mock_users_table = AsyncMock()
        mock_users_table.get_user.return_value = None
        mock_users_table.add_user = AsyncMock()

        # Mock is_pro_tamer to return True
        with patch("utils.helpers.is_pro_tamer", return_value=True):
            with patch("utils.helpers.get_users_table", return_value=mock_users_table):
                await user_check(mock_bot, mock_member)

                # Verify user was added with pro status
                mock_users_table.add_user.assert_called_once()
                call_args = mock_users_table.add_user.call_args
                assert call_args[1]["is_pro"] == 1

    @pytest.mark.asyncio
    async def test_user_check_new_user_non_pro_status(self, mock_bot: Any) -> None:
        """Test user_check adds new user without pro status."""
        # Create mock member
        mock_member = MagicMock(spec=discord.Member)
        mock_member.id = 987654321
        mock_member.name = "TestUser"

        # Mock database
        mock_users_table = AsyncMock()
        mock_users_table.get_user.return_value = None
        mock_users_table.add_user = AsyncMock()

        # Mock is_pro_tamer to return False
        with patch("utils.helpers.is_pro_tamer", return_value=False):
            with patch("utils.helpers.get_users_table", return_value=mock_users_table):
                await user_check(mock_bot, mock_member)

                # Verify user was added without pro status
                mock_users_table.add_user.assert_called_once()
                call_args = mock_users_table.add_user.call_args
                assert call_args[1]["is_pro"] == 0

    @pytest.mark.asyncio
    async def test_user_check_existing_user_pro_status_change(
        self, mock_bot: Any
    ) -> None:
        """Test user_check updates existing user when pro status changes."""
        # Create mock member
        mock_member = MagicMock(spec=discord.Member)
        mock_member.id = 987654321
        mock_member.name = "TestUser"

        # Mock database with existing user (non-pro)
        mock_users_table = AsyncMock()
        mock_users_table.get_user.return_value = {"user_id": 987654321, "is_pro": 0}
        mock_users_table.update_user = AsyncMock()

        # Mock is_pro_tamer to return True (status changed)
        with patch("utils.helpers.is_pro_tamer", return_value=True):
            with patch("utils.helpers.get_users_table", return_value=mock_users_table):
                await user_check(mock_bot, mock_member)

                # Verify user was updated with new pro status
                mock_users_table.update_user.assert_called_once()
                call_args = mock_users_table.update_user.call_args
                assert call_args[1]["is_pro"] == 1

    @pytest.mark.asyncio
    async def test_user_check_existing_user_no_status_change(
        self, mock_bot: Any
    ) -> None:
        """Test user_check doesn't update when pro status unchanged."""
        # Create mock member
        mock_member = MagicMock(spec=discord.Member)
        mock_member.id = 987654321
        mock_member.name = "TestUser"

        # Mock database with existing user (non-pro)
        mock_users_table = AsyncMock()
        mock_users_table.get_user.return_value = {"user_id": 987654321, "is_pro": 0}
        mock_users_table.update_user = AsyncMock()

        # Mock is_pro_tamer to return False (status unchanged)
        with patch("utils.helpers.is_pro_tamer", return_value=False):
            with patch("utils.helpers.get_users_table", return_value=mock_users_table):
                await user_check(mock_bot, mock_member)

                # Verify user was not updated
                mock_users_table.update_user.assert_not_called()

    @pytest.mark.asyncio
    async def test_user_check_new_user_default_values(self, mock_bot: Any) -> None:
        """Test user_check sets default values for new user."""
        # Create mock member
        mock_member = MagicMock(spec=discord.Member)
        mock_member.id = 987654321
        mock_member.name = "TestUser"

        # Mock database
        mock_users_table = AsyncMock()
        mock_users_table.get_user.return_value = None
        mock_users_table.add_user = AsyncMock()

        with patch("utils.helpers.is_pro_tamer", return_value=False):
            with patch("utils.helpers.get_users_table", return_value=mock_users_table):
                await user_check(mock_bot, mock_member)

                # Verify all default values were set
                call_args = mock_users_table.add_user.call_args
<<<<<<< HEAD
=======
                assert call_args[1]["wallet_connected"] == 0
                assert call_args[1]["wallet_address"] == ""
>>>>>>> de733c415448a6db7eb45eb4a06a6462f48833b2
                assert call_args[1]["is_certified"] == 0
                assert call_args[1]["experience_points"] == 0
                assert call_args[1]["battle_points"] == 0
                assert call_args[1]["victory_points"] == 0
                assert call_args[1]["wins"] == 0
                assert call_args[1]["losses"] == 0
                assert call_args[1]["draws"] == 0


class TestRespond:
    """Test cases for the respond function."""

    @pytest.mark.asyncio
    async def test_respond_in_dm_with_pro_user(self, mock_bot: Any) -> None:
        """Test respond sends embed in DM to pro user."""
        # Create mock message (DM - no guild)
        mock_message = MagicMock(spec=discord.Message)
        mock_message.guild = None
        mock_message.author = MagicMock(spec=discord.Member)
        mock_message.author.id = 987654321
        mock_message.author.send = AsyncMock()

        # Create mock embed
        mock_embed = MagicMock(spec=discord.Embed)

        # Mock is_pro_tamer to return True
        with patch("utils.helpers.is_pro_tamer", return_value=True):
            await respond(mock_bot, mock_message, embed=mock_embed)

            # Verify embed was sent
            mock_message.author.send.assert_called_once()
            call_args = mock_message.author.send.call_args
            assert call_args[1]["embed"] == mock_embed

    @pytest.mark.asyncio
    async def test_respond_in_dm_with_non_pro_user(self, mock_bot: Any) -> None:
        """Test respond sends error message in DM to non-pro user."""
        # Create mock message (DM - no guild)
        mock_message = MagicMock(spec=discord.Message)
        mock_message.guild = None
        mock_message.author = MagicMock(spec=discord.Member)
        mock_message.author.id = 987654321
        mock_message.author.send = AsyncMock()

        # Create mock embed
        mock_embed = MagicMock(spec=discord.Embed)

        # Mock is_pro_tamer to return False
        with patch("utils.helpers.is_pro_tamer", return_value=False):
            await respond(mock_bot, mock_message, embed=mock_embed)

            # Verify error message was sent
            mock_message.author.send.assert_called_once()
            call_args = mock_message.author.send.call_args
            assert "Pro or Pro+ Tamer" in call_args[1]["content"]
            # Verify the reply message deletion was set up
            assert mock_message.author.send.return_value.delete.called

    @pytest.mark.asyncio
    async def test_respond_in_guild(self, mock_bot: Any) -> None:
        """Test respond sends DM when message is from guild."""
        # Create mock message (from guild)
        mock_message = MagicMock(spec=discord.Message)
        mock_message.guild = MagicMock(spec=discord.Guild)
        mock_message.delete = AsyncMock()
        mock_message.author = MagicMock(spec=discord.Member)
        mock_message.author.send = AsyncMock()

        # Create mock embed
        mock_embed = MagicMock(spec=discord.Embed)

        with patch("utils.helpers.is_pro_tamer", return_value=True):
            await respond(mock_bot, mock_message, embed=mock_embed)

            # Verify message was deleted
            mock_message.delete.assert_called_once()
            # Verify embed was sent via DM
            mock_message.author.send.assert_called_once()
            call_args = mock_message.author.send.call_args
            assert call_args[1]["embed"] == mock_embed

    @pytest.mark.asyncio
    async def test_respond_with_view(self, mock_bot: Any) -> None:
        """Test respond includes view when provided."""
        # Create mock message (DM - no guild)
        mock_message = MagicMock(spec=discord.Message)
        mock_message.guild = None
        mock_message.author = MagicMock(spec=discord.Member)
        mock_message.author.id = 987654321
        mock_message.author.send = AsyncMock()

        # Create mock embed and view
        mock_embed = MagicMock(spec=discord.Embed)
        mock_view = MagicMock(spec=discord.ui.View)

        with patch("utils.helpers.is_pro_tamer", return_value=True):
            await respond(mock_bot, mock_message, embed=mock_embed, buttons=mock_view)

            # Verify both embed and view were sent
            mock_message.author.send.assert_called_once()
            call_args = mock_message.author.send.call_args
            assert call_args[1]["embed"] == mock_embed
            assert call_args[1]["view"] == mock_view

    @pytest.mark.asyncio
    async def test_respond_with_file(self, mock_bot: Any) -> None:
        """Test respond includes file when provided."""
        # Create mock message (DM - no guild)
        mock_message = MagicMock(spec=discord.Message)
        mock_message.guild = None
        mock_message.author = MagicMock(spec=discord.Member)
        mock_message.author.id = 987654321
        mock_message.author.send = AsyncMock()

        # Create mock embed and file
        mock_embed = MagicMock(spec=discord.Embed)
        mock_file = MagicMock(spec=discord.File)

        with patch("utils.helpers.is_pro_tamer", return_value=True):
            await respond(mock_bot, mock_message, embed=mock_embed, file=mock_file)

            # Verify embed and file were sent
            mock_message.author.send.assert_called_once()
            call_args = mock_message.author.send.call_args
            assert call_args[1]["embed"] == mock_embed
            assert call_args[1]["file"] == mock_file

    @pytest.mark.asyncio
    async def test_respond_with_all_parameters(self, mock_bot: Any) -> None:
        """Test respond with all parameters."""
        # Create mock message (DM - no guild)
        mock_message = MagicMock(spec=discord.Message)
        mock_message.guild = None
        mock_message.author = MagicMock(spec=discord.Member)
        mock_message.author.id = 987654321
        mock_message.author.send = AsyncMock()

        # Create mock embed, view, and file
        mock_embed = MagicMock(spec=discord.Embed)
        mock_view = MagicMock(spec=discord.ui.View)
        mock_file = MagicMock(spec=discord.File)

        with patch("utils.helpers.is_pro_tamer", return_value=True):
            await respond(
                mock_bot,
                mock_message,
                embed=mock_embed,
                buttons=mock_view,
                file=mock_file,
            )

            # Verify all parameters were sent
            mock_message.author.send.assert_called_once()
            call_args = mock_message.author.send.call_args
            assert call_args[1]["embed"] == mock_embed
            assert call_args[1]["view"] == mock_view
            assert call_args[1]["file"] == mock_file

    @pytest.mark.asyncio
    async def test_respond_guild_with_pro_check(self, mock_bot: Any) -> None:
        """Test respond in guild checks pro status and sends DM accordingly."""
        # Create mock message (from guild)
        mock_message = MagicMock(spec=discord.Message)
        mock_message.guild = MagicMock(spec=discord.Guild)
        mock_message.delete = AsyncMock()
        mock_message.author = MagicMock(spec=discord.Member)
        mock_message.author.send = AsyncMock()

        # Create mock embed
        mock_embed = MagicMock(spec=discord.Embed)

        # Mock is_pro_tamer - it should be called but result shouldn't matter in guild
        with patch("utils.helpers.is_pro_tamer", return_value=True):
            await respond(mock_bot, mock_message, embed=mock_embed)

            # Verify message was deleted and DM sent
            mock_message.delete.assert_called_once()
            mock_message.author.send.assert_called_once()


class TestHelpersEdgeCases:
    """Test edge cases for helpers functions."""

    @pytest.mark.asyncio
    async def test_user_check_with_long_username(self, mock_bot: Any) -> None:
        """Test user_check handles long usernames."""
        # Create mock member with long username
        mock_member = MagicMock(spec=discord.Member)
        mock_member.id = 987654321
        mock_member.name = "A" * 100  # Very long username

        # Mock database
        mock_users_table = AsyncMock()
        mock_users_table.get_user.return_value = None
        mock_users_table.add_user = AsyncMock()

        with patch("utils.helpers.is_pro_tamer", return_value=False):
            with patch("utils.helpers.get_users_table", return_value=mock_users_table):
                await user_check(mock_bot, mock_member)

                # Should handle long username
                mock_users_table.add_user.assert_called_once()
                call_args = mock_users_table.add_user.call_args
                assert call_args[1]["username"] == "A" * 100

    @pytest.mark.asyncio
    async def test_respond_with_none_embed(self, mock_bot: Any) -> None:
        """Test respond handles None embed gracefully."""
        # Create mock message (DM - no guild)
        mock_message = MagicMock(spec=discord.Message)
        mock_message.guild = None
        mock_message.author = MagicMock(spec=discord.Member)
        mock_message.author.id = 987654321
        mock_message.author.send = AsyncMock()

        with patch("utils.helpers.is_pro_tamer", return_value=True):
            await respond(mock_bot, mock_message, embed=None)

            # Should handle None embed
            mock_message.author.send.assert_called_once()

    @pytest.mark.asyncio
    async def test_respond_in_guild_without_pro_check_bypass(
        self, mock_bot: Any
    ) -> None:
        """Test respond in guild still sends DM even to non-pro users."""
        # Create mock message (from guild)
        mock_message = MagicMock(spec=discord.Message)
        mock_message.guild = MagicMock(spec=discord.Guild)
        mock_message.delete = AsyncMock()
        mock_message.author = MagicMock(spec=discord.Member)
        mock_message.author.send = AsyncMock()

        # Create mock embed
        mock_embed = MagicMock(spec=discord.Embed)

        with patch("utils.helpers.is_pro_tamer", return_value=False):
            await respond(mock_bot, mock_message, embed=mock_embed)

            # Even non-pro users in guild should get DM
            mock_message.delete.assert_called_once()
            mock_message.author.send.assert_called_once()
