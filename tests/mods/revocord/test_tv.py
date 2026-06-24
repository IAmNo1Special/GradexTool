from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import discord
import pytest

from mods.revocord.tv import (
    RevomonTVButton,
    TVNavButton,
    TVStatView,
    TVView,
    build_stat_embed,
    build_tv_embed,
)


class TestBuildTVEmbed:
    def test_build_tv_embed(self) -> None:
        member = MagicMock(spec=discord.Member)
        member.display_name = "Ash"

        embed = build_tv_embed(member, 100, 2, 5)

        assert isinstance(embed, discord.Embed)
        assert embed.title is not None and "ASH" in embed.title
        assert embed.description is not None and "100" in embed.description
        assert embed.footer.text is not None and "Page 3 of 5" in embed.footer.text

    def test_build_tv_embed_no_pages(self) -> None:
        member = MagicMock(spec=discord.Member)
        member.display_name = "Ash"

        embed = build_tv_embed(member, 0, 0, 0)
        assert embed.footer.text is not None and "Page 1 of 1" in embed.footer.text


class TestBuildStatEmbed:
    @pytest.mark.asyncio
    async def test_build_stat_embed_basic(self) -> None:
        mon = {
            "name": "Pikachu",
            "is_shiny": False,
            "level": 10,
            "xp": 500,
            "nature": "bold",
            "ability": "static",
            "ivs": {"hp": 31, "atk": 31, "def": 31, "spa": 31, "spd": 31, "spe": 31},
            "iv_percent": 100.0,
            "rc_id": "12345",
        }

        embed = await build_stat_embed(mon, {"num": 25})

        assert embed.title is not None and "Pikachu (Lv. 10)" in embed.title
        assert embed.fields[0].value is not None and "500 XP" in embed.fields[0].value
        assert embed.fields[1].value is not None and "Bold" in embed.fields[1].value
        assert embed.fields[2].value is not None and "Static" in embed.fields[2].value
        assert (
            embed.fields[3].value is not None
            and "186/186 (100.0%)" in embed.fields[3].value
        )
        assert embed.footer.text is not None and "RC-ID: #12345" in embed.footer.text
        assert embed.thumbnail.url is not None and "25.png" in embed.thumbnail.url

    @pytest.mark.asyncio
    async def test_build_stat_embed_shiny(self) -> None:
        mon = {
            "name": "Pikachu",
            "is_shiny": True,
            "level": 10,
        }

        embed = await build_stat_embed(mon, {"num": 25})

        assert embed.title is not None and "✨ SHINY Pikachu" in embed.title
        assert embed.thumbnail.url is not None and "25_shiny.png" in embed.thumbnail.url

    @pytest.mark.asyncio
    async def test_build_stat_embed_no_attrs(self) -> None:
        mon = {"name": "MissingNo"}
        embed = await build_stat_embed(mon, None)
        assert not getattr(embed.thumbnail, "url", None)


class TestTVStatView:
    @pytest.mark.asyncio
    async def test_back_button_wrong_user(self, mock_interaction: Any) -> None:
        view = TVStatView(123, [], 0)
        button = next(
            child
            for child in view.children
            if getattr(child, "custom_id", "") == "tv_back"
        )

        mock_interaction.user.id = 999
        await button.callback(mock_interaction)

        mock_interaction.response.send_message.assert_called_once()
        assert "not your TV" in mock_interaction.response.send_message.call_args[0][0]

    @pytest.mark.asyncio
    async def test_back_button_success(self, mock_interaction: Any) -> None:
        view = TVStatView(123, [{"name": "A"}], 0)
        button = next(
            child
            for child in view.children
            if getattr(child, "custom_id", "") == "tv_back"
        )

        mock_interaction.user.id = 123
        mock_interaction.client._app_emojis_cache = []
        mock_interaction.client.emojis = []

        await button.callback(mock_interaction)

        mock_interaction.response.defer.assert_called_once()
        mock_interaction.edit_original_response.assert_called_once()


class TestTVView:
    @pytest.mark.asyncio
    async def test_build_buttons_empty(self) -> None:
        bot = MagicMock()
        bot.emojis = []
        bot._app_emojis_cache = []
        bot.fetch_application_emojis = AsyncMock(return_value=[])

        view = TVView(bot, 123, [], 0)
        await view.build_buttons()

        # Should have 5 nav buttons
        assert len(view.children) == 5
        assert getattr(view.children[2], "custom_id", "") == "tv_nav_close"

    @pytest.mark.asyncio
    async def test_build_buttons_with_items(self) -> None:
        bot = MagicMock()
        bot.emojis = []
        bot.fetch_application_emojis = AsyncMock(return_value=[])
        delattr(bot, "_app_emojis_cache")

        caught: list[dict[str, Any]] = [
            {"name": "Pikachu", "rc_id": "1", "captured_at": 10},
            {"name": "Charmander", "rc_id": "2", "captured_at": 20},
            {"name": "Squirtle", "rc_id": "3", "captured_at": 5},
        ]

        view = TVView(bot, 123, caught, 0)
        await view.build_buttons()

        bot.fetch_application_emojis.assert_called_once()

        assert len(view.children) == 8  # 3 mons + 5 nav

        labels = [getattr(c, "label", "") for c in view.children if hasattr(c, "label")]
        assert "#2" in labels[0]  # Charmander
        assert "#1" in labels[1]  # Pikachu
        assert "#3" in labels[2]  # Squirtle


class TestTVNavButton:
    @pytest.mark.asyncio
    async def test_nav_wrong_user(self, mock_interaction: Any) -> None:
        bot = MagicMock()
        bot.emojis = []
        bot._app_emojis_cache = []
        caught: list[dict[str, Any]] = []

        btn = TVNavButton("next", "⏩", "Next", bot, 123, caught, 0)
        mock_interaction.user.id = 999
        await btn.callback(mock_interaction)
        mock_interaction.response.send_message.assert_called_once()

    @pytest.mark.asyncio
    @patch("mods.revocord.shared.get_or_create_account")
    @patch("mods.revocord.portal.build_console_embed")
    async def test_nav_close(
        self, mock_build: MagicMock, mock_get: MagicMock, mock_interaction: Any
    ) -> None:
        bot = MagicMock()
        bot.emojis = []
        bot._app_emojis_cache = []
        caught: list[dict[str, Any]] = []

        mock_get.return_value = {}
        mock_build.return_value = MagicMock()

        btn = TVNavButton("close", "❌", "Close", bot, 123, caught, 0)
        mock_interaction.user.id = 123
        await btn.callback(mock_interaction)
        mock_interaction.response.defer.assert_called_once()
        mock_interaction.edit_original_response.assert_called_once()

    @pytest.mark.asyncio
    async def test_nav_first(self, mock_interaction: Any) -> None:
        bot = MagicMock()
        bot.emojis = []
        bot._app_emojis_cache = []
        caught = [{"name": "A"} for _ in range(50)]

        btn = TVNavButton("first", "⏮️", "First", bot, 123, caught, 2)
        mock_interaction.user.id = 123
        await btn.callback(mock_interaction)
        mock_interaction.response.defer.assert_called_once()
        mock_interaction.edit_original_response.assert_called_once()

    @pytest.mark.asyncio
    async def test_nav_prev(self, mock_interaction: Any) -> None:
        bot = MagicMock()
        bot.emojis = []
        bot._app_emojis_cache = []
        caught = [{"name": "A"} for _ in range(50)]

        btn = TVNavButton("prev", "⏪", "Prev", bot, 123, caught, 1)
        mock_interaction.user.id = 123
        await btn.callback(mock_interaction)
        mock_interaction.response.defer.assert_called_once()
        mock_interaction.edit_original_response.assert_called_once()

    @pytest.mark.asyncio
    async def test_nav_prev_bound(self, mock_interaction: Any) -> None:
        bot = MagicMock()
        bot.emojis = []
        bot._app_emojis_cache = []
        caught = [{"name": "A"} for _ in range(50)]

        btn = TVNavButton("prev", "⏪", "Prev", bot, 123, caught, 0)
        mock_interaction.user.id = 123
        await btn.callback(mock_interaction)
        mock_interaction.response.defer.assert_called_once()
        mock_interaction.edit_original_response.assert_not_called()

    @pytest.mark.asyncio
    async def test_nav_next(self, mock_interaction: Any) -> None:
        bot = MagicMock()
        bot.emojis = []
        bot._app_emojis_cache = []
        caught = [{"name": "A"} for _ in range(50)]

        btn = TVNavButton("next", "⏩", "Next", bot, 123, caught, 0)
        mock_interaction.user.id = 123
        await btn.callback(mock_interaction)
        mock_interaction.response.defer.assert_called_once()
        mock_interaction.edit_original_response.assert_called_once()

    @pytest.mark.asyncio
    async def test_nav_next_bound(self, mock_interaction: Any) -> None:
        bot = MagicMock()
        bot.emojis = []
        bot._app_emojis_cache = []
        caught = [{"name": "A"} for _ in range(50)]

        btn = TVNavButton("next", "⏩", "Next", bot, 123, caught, 2)
        mock_interaction.user.id = 123
        await btn.callback(mock_interaction)
        mock_interaction.response.defer.assert_called_once()
        mock_interaction.edit_original_response.assert_not_called()

    @pytest.mark.asyncio
    async def test_nav_last(self, mock_interaction: Any) -> None:
        bot = MagicMock()
        bot.emojis = []
        bot._app_emojis_cache = []
        caught = [{"name": "A"} for _ in range(50)]

        btn = TVNavButton("last", "⏭️", "Last", bot, 123, caught, 0)
        mock_interaction.user.id = 123
        await btn.callback(mock_interaction)
        mock_interaction.response.defer.assert_called_once()
        mock_interaction.edit_original_response.assert_called_once()
        kwargs = mock_interaction.edit_original_response.call_args[1]
        assert kwargs["view"].current_page == 2


class TestRevomonTVButton:
    @pytest.mark.asyncio
    async def test_wrong_user(self, mock_interaction: Any) -> None:
        bot = MagicMock()
        btn = RevomonTVButton(bot, 123, [], 0, {"rc_id": "1"}, 0, None)

        mock_interaction.user.id = 999
        await btn.callback(mock_interaction)
        mock_interaction.response.send_message.assert_called_once()

    @pytest.mark.asyncio
    @patch("mods.revocord.tv.get_attributes")
    async def test_success(self, mock_get_attrs: Any, mock_interaction: Any) -> None:
        bot = MagicMock()
        mon = {"name": "Pikachu", "rc_id": "1"}
        btn = RevomonTVButton(bot, 123, [mon], 0, mon, 0, None)

        mock_interaction.user.id = 123
        mock_get_attrs.return_value = {"num": 25}

        await btn.callback(mock_interaction)

        mock_interaction.response.defer.assert_called_once()
        mock_interaction.edit_original_response.assert_called_once()

    @pytest.mark.asyncio
    @patch("mods.revocord.tv.get_attributes")
    async def test_get_attrs_exception(
        self, mock_get_attrs: Any, mock_interaction: Any
    ) -> None:
        bot = MagicMock()
        mon = {"name": "MissingNo", "rc_id": "1"}
        btn = RevomonTVButton(bot, 123, [mon], 0, mon, 0, None)

        mock_interaction.user.id = 123
        mock_get_attrs.side_effect = Exception("API down")

        await btn.callback(mock_interaction)

        mock_interaction.response.defer.assert_called_once()
        mock_interaction.edit_original_response.assert_called_once()
