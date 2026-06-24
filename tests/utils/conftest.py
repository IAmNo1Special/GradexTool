from typing import Any

"""Pytest configuration and common fixtures for testing utils modules."""

from unittest.mock import MagicMock, patch  # noqa: E402

import discord  # noqa: E402
import pytest  # noqa: E402


@pytest.fixture
def mock_discord_color() -> Any:
    """Mock Discord Color."""
    color = MagicMock(spec=discord.Color)
    color.red = MagicMock(return_value=color)
    return color


@pytest.fixture
def mock_discord_embed() -> Any:
    """Mock Discord Embed."""
    embed = MagicMock(spec=discord.Embed)
    embed.title = "Test Embed"
    embed.description = "Test Description"
    embed.color = discord.Color.red()
    embed.url = "https://example.com"
    embed.add_field = MagicMock()
    embed.set_thumbnail = MagicMock()
    embed.set_footer = MagicMock()
    embed.set_image = MagicMock()
    embed.set_author = MagicMock()
    return embed


@pytest.fixture
def sample_revomon_attributes() -> Any:
    """Sample Revomon attributes for testing."""
    return {
        "name": "testmon",
        "num": 1,
        "profile_img": "https://example.com/testmon.png",
        "shiny_profile_img": "https://example.com/shiny-testmon.png",
        "nft_img": "https://example.com/testmon-nft.png",
        "shiny_nft_img": "https://example.com/shiny-testmon-nft.png",
        "emoji": "testmon_emoji",
        "shiny_emoji": "shiny_testmon_emoji",
        "main_description": "A test description for testmon.",
        "type1": "fire",
        "type1_img": "https://example.com/fire.png",
        "type2": None,
        "type2_img": None,
        "type_chart_img": "https://example.com/type-chart.png",
        "rarity": "rare",
        "ability1": "overgrow",
        "ability2": None,
        "abilityh": "chlorophyll",
        "evolution": None,
        "evolution_lvl": None,
        "evolution_tree": "testmon -> evomons",
        "ev_gains1": "+ 1 Hit Points",
        "ev_gains2": None,
        "base_hp": 45,
        "base_atk": 49,
        "base_def": 49,
        "base_spa": 65,
        "base_spd": 65,
        "base_spe": 45,
        "total_stats": 273,
        "spawn_loc1": "Forest",
        "spawn_time1": "Morning",
        "spawn_loc2": None,
        "spawn_time2": None,
        "spawn_loc3": None,
        "spawn_time3": None,
        "spawn_rate": "10%",
        "spawn_table": "forest_morning",
        "move_list": ["tackle", "ember"],
        "cdex_tier": "b",
        "cdex_description": "A decent fire type.",
        "weakness": ["water", "rock"],
        "meta_build": "Physical Attacker",
        "meta_moves": ["tackle", "ember"],
        "tips": "Use in sunny weather.",
        "counters": ["water types"],
    }


@pytest.fixture
def sample_revomon_attributes_dual_type() -> Any:
    """Sample Revomon attributes with dual types for testing."""
    return {
        "name": "dualmon",
        "num": 2,
        "profile_img": "https://example.com/dualmon.png",
        "shiny_profile_img": "https://example.com/shiny-dualmon.png",
        "nft_img": "https://example.com/dualmon-nft.png",
        "shiny_nft_img": "https://example.com/shiny-dualmon-nft.png",
        "emoji": "dualmon_emoji",
        "shiny_emoji": "shiny_dualmon_emoji",
        "main_description": "A dual type testmon.",
        "type1": "fire",
        "type1_img": "https://example.com/fire.png",
        "type2": "water",
        "type2_img": "https://example.com/water.png",
        "type_chart_img": "https://example.com/type-chart.png",
        "rarity": "epic",
        "ability1": "overgrow",
        "ability2": "blaze",
        "abilityh": "chlorophyll",
        "evolution": "evomons",
        "evolution_lvl": 16,
        "evolution_tree": "dualmon -> evomons -> finalmon",
        "ev_gains1": "+ 1 Hit Points",
        "ev_gains2": "+ 1 Attack",
        "base_hp": 60,
        "base_atk": 62,
        "base_def": 63,
        "base_spa": 80,
        "base_spd": 80,
        "base_spe": 60,
        "total_stats": 405,
        "spawn_loc1": "Forest",
        "spawn_time1": "Morning",
        "spawn_loc2": "Lake",
        "spawn_time2": "Evening",
        "spawn_loc3": None,
        "spawn_time3": None,
        "spawn_rate": "5%",
        "spawn_table": "forest_morning",
        "move_list": ["tackle", "ember", "water gun"],
        "cdex_tier": "a",
        "cdex_description": "A strong dual type.",
        "weakness": ["electric", "grass"],
        "meta_build": "Special Attacker",
        "meta_moves": ["ember", "water gun"],
        "tips": "Use balanced teams.",
        "counters": ["electric types"],
    }


@pytest.fixture
def sample_land_attributes() -> Any:
    """Sample land attributes for testing."""
    return {
        "land_type": "forest",
        "biome": "woodland",
        "token_id": 12345,
        "for_sale": True,
        "for_sale_token": 100.0,
        "token_symbol": "IMX",
        "for_sale_usd": 150.0,
        "owners_address": "0x1234567890abcdef1234567890abcdef12345678",
        "rarity": "rare",
        "size": "medium",
        "img_url": "https://example.com/land.png",
    }


@pytest.fixture
def sample_land_attributes_not_for_sale() -> Any:
    """Sample land attributes not for sale for testing."""
    return {
        "land_type": "forest",
        "biome": "woodland",
        "token_id": 12346,
        "for_sale": False,
        "for_sale_token": 0.0,
        "token_symbol": "IMX",
        "for_sale_usd": 0.0,
        "owners_address": "0x1234567890abcdef1234567890abcdef12345678",
        "rarity": "epic",
        "size": "large",
        "img_url": "https://example.com/land2.png",
    }


@pytest.fixture
def mock_revomon_table() -> Any:
    """Mock RevomonTable."""
    table = MagicMock()
    table.get_info = MagicMock(
        return_value=[
            (
                1,  # dex_id
                1,  # mon_id
                "testmon",  # name
                "A test description.",  # description
                "rare",  # rarity
                "overgrow",  # ability1
                None,  # ability2
                "chlorophyll",  # abilityh
                None,  # evolution
                None,  # evolution_lvl
                "testmon tree",  # evolution_tree
                "fire",  # type1
                "https://example.com/fire.png",  # type1_img
                None,  # type2
                None,  # type2_img
                45,  # hp
                49,  # atk
                49,  # def
                65,  # spa
                65,  # spd
                45,  # spe
                273,  # total_stats
                1,  # ev_hp
                0,  # ev_atk
                0,  # ev_def
                0,  # ev_spa
                0,  # ev_spd
                0,  # ev_spe
                "Forest",  # spawn_loc1
                "Morning",  # spawn_time1
                None,  # spawn_loc2
                None,  # spawn_time2
                None,  # spawn_loc3
                None,  # spawn_time3
                "10%",  # spawn_rate
                "forest_morning",  # spawn_table
                "https://example.com/testmon.png",  # profile_img
                "https://example.com/shiny-testmon.png",  # shiny_profile_img
                "https://example.com/testmon-nft.png",  # nft_img
                "https://example.com/shiny-testmon-nft.png",  # shiny_nft_img
                "testmon_emoji_id",  # emoji_id
                "shiny_testmon_emoji_id",  # shiny_emoji_id
            )
        ]
    )
    table.get_names = MagicMock(return_value=["testmon", "dualmon"])
    return table


@pytest.fixture
def mock_types_table() -> Any:
    """Mock TypesTable."""
    table = MagicMock()
    table.get_info = MagicMock(
        return_value=[
            (
                "fire",
                "water",
                "https://example.com/type-chart.png",
            )
        ]
    )
    table.get_mono_types = MagicMock(return_value=["fire", "water", "grass"])
    return table


@pytest.fixture
def mock_counterdex_table() -> Any:
    """Mock CounterdexTable."""
    table = MagicMock()
    table.get_info = MagicMock(
        return_value=[
            (
                1,  # id
                "testmon",  # name
                "b",  # tier
                "A decent fire type.",  # description
                "tackle,ember",  # meta_moves
                "Physical Attacker",  # meta_build
                "Use in sunny weather.",  # tips
                "water types",  # counters
                ["water", "rock"],  # weakness
            )
        ]
    )
    return table


@pytest.fixture
def mock_revomon_moves_table() -> Any:
    """Mock RevomonMovesTable."""
    table = MagicMock()
    table.get_moves_for_revomon = MagicMock(
        return_value=[
            ("tackle",),
            ("ember",),
        ]
    )
    return table


@pytest.fixture
def mock_natures_table() -> Any:
    """Mock NaturesTable."""
    table = MagicMock()
    table.get_all = MagicMock(
        return_value=[
            (1, "adamant", "atk", "spa"),
            (2, "modest", "spa", "atk"),
        ]
    )
    return table


@pytest.fixture
def mock_owned_lands_table() -> Any:
    """Mock OwnedLandsTable."""
    table = MagicMock()
    table.get_info = MagicMock(
        return_value=[
            (
                12345,  # token_id
                "forest",  # land_type
                "woodland",  # biome
                "rare",  # rarity
                "medium",  # size
                "https://example.com/land.png",  # img_url
                "0x1234567890abcdef1234567890abcdef12345678",  # owner_address
                "land_emoji_id",  # emoji_id
                100.0,  # price
                "IMX",  # token_symbol
                150.0,  # usd_price
            )
        ]
    )
    table.get_ids = MagicMock(return_value=[12345, 12346])
    return table


@pytest.fixture
def mock_users_table() -> Any:
    """Mock UsersTable."""
    table = MagicMock()
    table.get_user = MagicMock(return_value=None)
    table.add_user = MagicMock()
    table.update_user = MagicMock()
    return table


@pytest.fixture
def mock_pil_image() -> None:  # type: ignore[misc]
    """Mock PIL Image."""
    with patch("PIL.Image.new") as mock_new:
        mock_image = MagicMock()
        mock_image.size = (100, 100)
        mock_new.return_value = mock_image
        yield mock_image


@pytest.fixture
def mock_pil_image_draw() -> None:  # type: ignore[misc]
    """Mock PIL ImageDraw."""
    with patch("PIL.ImageDraw.Draw") as mock_draw:
        draw_instance = MagicMock()
        mock_draw.return_value = draw_instance
        yield draw_instance


@pytest.fixture
def mock_pil_image_font() -> None:  # type: ignore[misc]
    """Mock PIL ImageFont."""
    with patch("PIL.ImageFont.truetype") as mock_font:
        font_instance = MagicMock()
        mock_font.return_value = font_instance
        yield font_instance
