from typing import Any

"""Pytest configuration and common fixtures for testing mods."""

from unittest.mock import AsyncMock, MagicMock, patch  # noqa: E402

import discord  # noqa: E402
import pytest  # noqa: E402
from discord import app_commands  # noqa: E402
from discord.ext import commands  # noqa: E402


@pytest.fixture
def mock_bot() -> Any:
    """Create a mock Discord bot."""
    bot = MagicMock(spec=commands.Bot)
    bot.wait_until_ready = AsyncMock()
    bot.get_guild = MagicMock(return_value=None)
    bot.get_channel = MagicMock(return_value=None)
    bot.add_cog = AsyncMock()
    bot.load_extension = AsyncMock()
    bot.add_view = MagicMock()
    return bot


@pytest.fixture
def mock_guild() -> Any:
    """Create a mock Discord guild."""
    guild = MagicMock(spec=discord.Guild)
    guild.id = 123456789
    guild.name = "Test Server"
    guild.categories = []
    guild.roles = []
    guild.forums = []
    guild.threads = []
    return guild


@pytest.fixture
def mock_member() -> Any:
    """Create a mock Discord member."""
    member = MagicMock(spec=discord.Member)
    member.id = 987654321
    member.name = "TestUser"
    member.bot = False
    member.roles = []
    return member


@pytest.fixture
def mock_message() -> Any:
    """Create a mock Discord message."""
    message = MagicMock(spec=discord.Message)
    message.id = 111222333
    message.author = MagicMock(spec=discord.Member)
    message.author.id = 987654321
    message.author.name = "TestUser"
    message.author.bot = False
    message.guild = MagicMock(spec=discord.Guild)
    message.guild.id = 123456789
    message.delete = AsyncMock()
    return message


@pytest.fixture
def mock_interaction() -> Any:
    """Create a mock Discord interaction."""
    interaction = MagicMock(spec=discord.Interaction)
    interaction.user = MagicMock(spec=discord.Member)
    interaction.user.id = 987654321
    interaction.user.name = "TestUser"
    interaction.guild = MagicMock(spec=discord.Guild)
    interaction.guild.id = 123456789
    interaction.guild_id = 123456789
    interaction.response = AsyncMock()
    interaction.followup = AsyncMock()
    interaction.message = MagicMock()
    interaction.message.id = 111222333
    interaction.message.delete = AsyncMock()
    mock_category = MagicMock(spec=discord.CategoryChannel)
    mock_channel = MagicMock(spec=discord.TextChannel)
    mock_channel.category = mock_category
    mock_channel.category_id = 999
    interaction.channel = mock_channel
    interaction.guild.get_channel.return_value = mock_category
    return interaction


@pytest.fixture
def mock_channel() -> Any:
    """Create a mock Discord channel."""
    channel = MagicMock(spec=discord.TextChannel)
    channel.id = 444555666
    channel.name = "test-channel"
    channel.edit = AsyncMock()
    channel.send = AsyncMock()
    return channel


@pytest.fixture
def mock_role() -> Any:
    """Create a mock Discord role."""
    role = MagicMock(spec=discord.Role)
    role.id = 777888999
    role.name = "Test Role"
    return role


@pytest.fixture
def mock_poll() -> Any:
    """Create a mock Discord poll."""
    poll = MagicMock(spec=discord.Poll)
    poll.question = "Test Poll Question"
    poll.answers = []
    poll.message = MagicMock()
    poll.message.id = 111222333
    poll.message.author = MagicMock()
    poll.end = AsyncMock()
    return poll


@pytest.fixture
def mock_forum() -> Any:
    """Create a mock Discord forum."""
    forum = MagicMock(spec=discord.ForumChannel)
    forum.id = 555666777
    forum.name = "test-forum"
    forum.threads = []
    forum.create_thread = AsyncMock()
    return forum


@pytest.fixture
def mock_thread() -> Any:
    """Create a mock Discord thread."""
    thread = MagicMock(spec=discord.Thread)
    thread.id = 666777888
    thread.name = "test-thread"
    thread.send = AsyncMock()
    return thread


@pytest.fixture
def mock_embed() -> Any:
    """Create a mock Discord embed."""
    embed = MagicMock(spec=discord.Embed)
    embed.title = "Test Embed"
    embed.description = "Test Description"
    embed.color = discord.Color.blue()
    embed.set_image = MagicMock()
    embed.set_thumbnail = MagicMock()
    embed.set_footer = MagicMock()
    embed.add_field = MagicMock()
    embed.set_author = MagicMock()
    return embed


@pytest.fixture
def mock_file() -> Any:
    """Create a mock Discord file."""
    file = MagicMock(spec=discord.File)
    file.filename = "test.png"
    return file


@pytest.fixture
def mock_view() -> Any:
    """Create a mock Discord view."""
    view = MagicMock(spec=discord.ui.View)
    return view


@pytest.fixture
def mock_button() -> Any:
    """Create a mock Discord button."""
    button = MagicMock(spec=discord.ui.Button)
    button.custom_id = "test_button"
    button.label = "Test Button"
    return button


@pytest.fixture
def mock_app_command() -> Any:
    """Create a mock app command."""
    command = MagicMock(spec=app_commands.Command)
    command.name = "test_command"
    return command


@pytest.fixture
def mock_requests_get() -> None:  # type: ignore[misc]
    """Mock requests.get for API calls."""
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json = MagicMock(return_value={})
        mock_get.return_value = mock_response
        yield mock_get


@pytest.fixture
def mock_requests_post() -> None:  # type: ignore[misc]
    """Mock requests.post for API calls."""
    with patch('requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json = MagicMock(return_value={})
        mock_post.return_value = mock_response
        yield mock_post


@pytest.fixture
def mock_aiohttp_session() -> None:  # type: ignore[misc]
    """Mock aiohttp client session."""
    with patch('aiohttp.ClientSession') as mock_session:
        session = AsyncMock()
        mock_session.return_value = session
        yield session


@pytest.fixture
def sample_revomon_data() -> Any:
    """Sample Revomon data for testing."""
    return {
        "mon_name": "Testmon",
        "mon_nature": "Adamant",
        "mon_ability": "Overgrow",
        "hp_iv": 31,
        "atk_iv": 31,
        "def_iv": 31,
        "spa_iv": 31,
        "spd_iv": 31,
        "spe_iv": 31,
        "hp_ev": 0,
        "atk_ev": 0,
        "def_ev": 0,
        "spa_ev": 0,
        "spd_ev": 0,
        "spe_ev": 0,
    }


@pytest.fixture
def sample_grade_data() -> Any:
    """Sample grade data for testing."""
    return {
        "grade_percent": 85.5,
        "grade_letter": "A",
        "role": "Physical Attacker",
        "nature_quality": "Perfect",
        "stat_weights": {
            "hp": 1.0,
            "atk": 2.0,
            "def": 1.0,
            "spa": 0.5,
            "spd": 1.0,
            "spe": 1.5,
        },
    }


@pytest.fixture
def sample_podium_data() -> Any:
    """Sample podium data for testing."""
    return {
        "first": {
            "user": "User1",
            "img": "https://example.com/user1.png",
            "time": "01:23:45",
        },
        "second": {
            "user": "User2",
            "img": "https://example.com/user2.png",
            "time": "02:34:56",
        },
        "third": {
            "user": "User3",
            "img": "https://example.com/user3.png",
            "time": "03:45:67",
        },
    }


@pytest.fixture
def sample_pvp_data() -> Any:
    """Sample PvP data for testing."""
    return [
        {
            "Rank": 1,
            "Name": "Player1",
            "Elo": 2000,
            "Wins": 50,
            "Losses": 10,
            "Winning": "83.33%",
            "Reward": "1000 REVO",
        },
        {
            "Rank": 2,
            "Name": "Player2",
            "Elo": 1900,
            "Wins": 45,
            "Losses": 15,
            "Winning": "75.00%",
            "Reward": "900 REVO",
        },
    ]


@pytest.fixture
def mock_podium() -> Any:
    """Create a mock Podium2 instance for testing."""
    from mods.revomon.podium_command import Podium2
    mock_bot = MagicMock(spec=commands.Bot)
    return Podium2(mock_bot)


@pytest.fixture
def mock_pvp_leaderboard() -> Any:
    """Create a mock PvpLeaderboard2 instance for testing."""
    from mods.revomon.pvp_command import PvpLeaderboard2
    mock_bot = MagicMock(spec=commands.Bot)
    return PvpLeaderboard2(mock_bot)


